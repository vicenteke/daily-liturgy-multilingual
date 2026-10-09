import datetime
import importlib

import httpx
import pytest

from daily_liturgy import Celebration, Color, LiturgyNotAvailableError, Rank, Season, get_daily_liturgy
from daily_liturgy.locales.it_it import get_daily_liturgy_it_it
from daily_liturgy.locales.it_it.fetch_cei_page import fetch_cei_page
from daily_liturgy.locales.it_it.parse_cei_celebrations import parse_cei_celebrations
from daily_liturgy.locales.it_it.parse_cei_readings import parse_cei_readings
from daily_liturgy.locales.it_it.split_cei_masses import split_cei_masses


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def citations(liturgy):
    return [reading.citation for reading in liturgy.readings]


def test_weekday(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2026, 10, 8))
    assert liturgy.locale == "it-it"
    assert liturgy.source_url == "https://www.chiesacattolica.it/liturgia-del-giorno/liturgie-del-20261008/"
    assert types(liturgy) == ["Prima Lettura", "Salmo Responsoriale", "Acclamazione al Vangelo", "Vangelo"]
    assert citations(liturgy) == ["Gal 3,1-5", "Lc 1,68-75", "Cf. At 16,14b", "Lc 11,5-13"]

    first, psalm, acclamation, gospel = liturgy.readings
    assert first.content.startswith("Dalla lettera di san Paolo apostolo ai Gàlati\n\nO stolti Gàlati")
    assert first.content.endswith("Parola di Dio.")
    assert "Gal 3,1-5" not in first.content
    assert psalm.content.startswith("R. Benedetto il Signore, Dio d’Israele,")
    assert acclamation.content.endswith("(Cf. At 16,14b)\n\nAlleluia.")
    assert gospel.content.endswith("Parola del Signore.")


def test_weekday_metadata(cei_site):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), "IT-IT")
    assert (liturgy.season, liturgy.week, liturgy.color) == (Season.ORDINARY_TIME, 27, Color.GREEN)
    assert liturgy.celebrations == []


def test_sunday(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2026, 10, 4))
    assert citations(liturgy) == ["Is 5,1-7", "Dal Sal 79 (80)", "Fil 4,6-9", "Cf. Gv 15,16", "Mt 21,33-43"]
    assert liturgy.celebrations == []


def test_feast_with_alternative_and_split_citation(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2026, 9, 29))
    assert liturgy.color == Color.WHITE
    assert liturgy.celebrations == [Celebration(name="SANTI MICHELE, GABRIELE E RAFFAELE, ARCANGELI", rank=Rank.FEAST)]
    first = liturgy.readings[0]
    assert first.citation == "Dn 7,9-10.13-14"
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Prima Lettura", "Ap 12,7-12a")]
    assert first.alternatives[0].content.startswith("Michele e i suoi angeli combattevano contro il drago.")
    assert "Oppure" not in first.content
    assert liturgy.readings[2].citation == "Sal 102 (103),21"  # unlinked, in the text


def test_easter_alternatives_and_sequence(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2025, 4, 20))
    assert types(liturgy) == ["Prima Lettura", "Salmo Responsoriale", "Seconda Lettura", "SEQUENZA", "Acclamazione al Vangelo", "Vangelo"]
    psalm, second, gospel = liturgy.readings[1], liturgy.readings[2], liturgy.readings[5]
    assert psalm.alternatives == [] and "Oppure:\nR. Alleluia, alleluia, alleluia." in psalm.content
    assert [alt.citation for alt in second.alternatives] == ["1Cor 5,6b-8"]
    assert [alt.citation for alt in gospel.alternatives] == ["Lc 24,13-35"]
    assert liturgy.celebrations == [Celebration(name="DOMENICA DI PASQUA «RISURREZIONE DEL SIGNORE»", rank=None)]


def test_christmas_keeps_mass_during_the_day(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2026, 12, 25))
    assert citations(liturgy) == ["Is 52,7-10", "Dal Sal 97 (98)", "Eb 1,1-6", "", "Gv 1,1-18"]
    assert [alt.citation for alt in liturgy.readings[4].alternatives] == ["Gv 1,1-5.9-14"]  # "Forma breve"
    assert liturgy.celebrations == [Celebration(name="NATALE DEL SIGNORE", rank=Rank.SOLEMNITY)]


def test_optional_memorial_keeps_weekday_mass(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2026, 10, 6))
    assert (liturgy.color, liturgy.readings[0].citation) == (Color.GREEN, "Gal 1,13-24")
    assert liturgy.celebrations == [Celebration(name="SAN BRUNO, PRESBITERO", rank=Rank.OPTIONAL_MEMORIAL)]


def test_plain_link_citation_and_rites_skipped(cei_site):
    liturgy = get_daily_liturgy_it_it(datetime.date(2026, 4, 2))
    assert (liturgy.season, liturgy.celebrations) == (Season.EASTER_TRIDUUM, [])
    assert liturgy.readings[-1].citation == "Gv 13,1-15"
    assert "Gv 13,1-15" not in liturgy.readings[-1].content


@pytest.mark.parametrize(
    "title, expected",
    [
        ("GIOVEDÌ DELLA XXVII SETTIMANA DEL TEMPO ORDINARIO (ANNO PARI)", []),
        ("XXVII DOMENICA DEL TEMPO ORDINARIO - ANNO A", []),
        ("MERCOLEDÌ DELLE CENERI", []),
        ("GIOVEDÌ SANTO «CENA DEL SIGNORE»", []),
        ("SANTA TERESA DI GESÙ BAMBINO, VERGINE E DOTTORE DELLA CHIESA – MEMORIA",
         [Celebration(name="SANTA TERESA DI GESÙ BAMBINO, VERGINE E DOTTORE DELLA CHIESA", rank=Rank.MEMORIAL)]),
        ("COMMEMORAZIONE DI TUTTI I FEDELI DEFUNTI (MESSA 1)", [Celebration(name="COMMEMORAZIONE DI TUTTI I FEDELI DEFUNTI", rank=None)]),
    ],
)
def test_celebrations_from_title(title, expected):
    assert parse_cei_celebrations([title]) == expected


def test_missing_page_raises(monkeypatch):
    module = importlib.import_module("daily_liturgy.locales.it_it.fetch_cei_page")
    monkeypatch.setattr(module.httpx, "get", lambda url, **kwargs: httpx.Response(404, request=httpx.Request("GET", url)))
    with pytest.raises(LiturgyNotAvailableError, match="2030-01-01"):
        fetch_cei_page(datetime.date(2030, 1, 1))


@pytest.mark.network
def test_live_site():
    masses = split_cei_masses(fetch_cei_page(datetime.date.today()))
    readings = parse_cei_readings(masses[0][1])
    assert readings[0].type == "Prima Lettura" and readings[0].citation
    assert readings[-1].type == "Vangelo"
