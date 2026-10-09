import datetime
import importlib

import pytest

from daily_liturgy import Celebration, Color, LiturgyNotAvailableError, Rank, Season, get_daily_liturgy
from daily_liturgy.locales.pt_br import get_daily_liturgy_pt_br
from daily_liturgy.locales.pt_br.fetch_cancaonova_page import fetch_cancaonova_page
from daily_liturgy.locales.pt_br.find_cancaonova_day_url import find_cancaonova_day_url
from daily_liturgy.locales.pt_br.parse_cancaonova_color import parse_cancaonova_color
from daily_liturgy.locales.pt_br.parse_cancaonova_readings import parse_cancaonova_readings


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def test_weekday(cancaonova_site):
    liturgy = get_daily_liturgy_pt_br(datetime.date(2026, 10, 8))
    assert liturgy.locale == "pt-br"
    assert liturgy.source_url.startswith("https://liturgia.cancaonova.com/liturgia/27a-semana-tempo-comum-quinta-feira")
    assert types(liturgy) == ["1ª Leitura", "Salmo", "Evangelho"]

    first, psalm, gospel = liturgy.readings
    assert first.citation == "Gl 3,1-5"
    assert first.content.startswith("Leitura da Carta de São Paulo aos Gálatas.\n\n1 Ó gálatas insensatos")
    assert psalm.citation == "Lc 1,69-70.71-72.73 e 75 (R. cf. 68)"
    assert gospel.citation == "Lc 11,5-13"
    assert gospel.content.endswith("— Glória a vós, Senhor.")
    assert "Conferência Nacional" not in gospel.content


def test_sunday_has_second_reading(cancaonova_site):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 4), "pt-br")
    assert types(liturgy) == ["1ª Leitura", "Salmo", "2ª Leitura", "Evangelho"]
    assert liturgy.readings[2].citation == "Fl 4,6-9"


def test_ou_becomes_alternative(cancaonova_site):
    first = get_daily_liturgy_pt_br(datetime.date(2026, 9, 29)).readings[0]
    assert first.citation == "Dn 7,9-10.13-14"
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("1ª Leitura", "Ap 12,7-12a")]
    assert first.alternatives[0].content.startswith("Leitura do Livro do Apocalipse de João.")


def test_christmas_keeps_mass_during_the_day(cancaonova_site):
    liturgy = get_daily_liturgy_pt_br(datetime.date(2026, 12, 25))
    assert [r.citation for r in liturgy.readings] == ["Is 52,7-10", "Sl 97(98),1.2-3ab.3cd-4.5-6 (R. 3cd)", "Hb 1,1-6", "Jo 1, 1-18"]
    assert all(not r.alternatives for r in liturgy.readings)


def test_date_missing_from_calendar_raises(monkeypatch):
    module = importlib.import_module("daily_liturgy.locales.pt_br.find_cancaonova_day_url")
    monkeypatch.setattr(module, "_download_calendar", lambda month, year: "<table id='wp-calendar'></table>")
    with pytest.raises(LiturgyNotAvailableError, match="2030-01-01"):
        find_cancaonova_day_url(datetime.date(2030, 1, 1))


@pytest.mark.network
def test_live_site():
    date = datetime.date.today()
    url = find_cancaonova_day_url(date)
    readings = parse_cancaonova_readings(fetch_cancaonova_page(url))
    assert readings[0].type == "1ª Leitura"
    assert readings[-1].type == "Evangelho"


def test_header_listing_options_keeps_first_citation(cancaonova_site):
    second = get_daily_liturgy_pt_br(datetime.date(2025, 4, 20)).readings[2]
    assert second.citation == "Cl 3,1-4"
    assert [alt.citation for alt in second.alternatives] == ["1Cor 5,6b-8"]


def test_weekday_metadata(cancaonova_site):
    liturgy = get_daily_liturgy_pt_br(datetime.date(2026, 10, 8))
    assert (liturgy.season, liturgy.week, liturgy.color) == (Season.ORDINARY_TIME, 27, Color.GREEN)
    assert liturgy.celebrations == []


def test_feast_metadata(cancaonova_site):
    liturgy = get_daily_liturgy_pt_br(datetime.date(2026, 9, 29))
    assert liturgy.color == Color.WHITE
    assert liturgy.celebrations == [Celebration(name="Santos Miguel, Gabriel e Rafael, Arcanjos", rank=Rank.FEAST)]


def test_solemnity_metadata(cancaonova_site):
    liturgy = get_daily_liturgy_pt_br(datetime.date(2026, 12, 25))
    assert (liturgy.season, liturgy.week) == (Season.CHRISTMAS, None)
    assert liturgy.celebrations == [Celebration(name="Natal de Nosso Senhor Jesus Cristo", rank=Rank.SOLEMNITY)]


def test_unranked_celebration(cancaonova_site):
    liturgy = get_daily_liturgy_pt_br(datetime.date(2025, 4, 20))
    assert (liturgy.season, liturgy.week) == (Season.EASTER, 1)
    assert liturgy.celebrations == [Celebration(name="Páscoa do Senhor", rank=None)]


def test_missing_color_is_none():
    assert parse_cancaonova_color("<html><h1 class='entry-title'>x</h1></html>") is None
    assert parse_cancaonova_color("<span class='cor-liturgica'>Cor Litúrgica: Azul</span>") is None
