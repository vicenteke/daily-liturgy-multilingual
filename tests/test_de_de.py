import datetime
import importlib

import pytest

from daily_liturgy import Celebration, LiturgyNotAvailableError, Rank, Season, get_daily_liturgy
from daily_liturgy.locales.de_de import get_daily_liturgy_de_de
from daily_liturgy.locales.de_de.fetch_schott_index import _parse_index
from daily_liturgy.locales.de_de.parse_schott_celebrations import parse_schott_celebrations


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def citations(readings):
    return [reading.citation for reading in readings]


def test_weekday_keeps_the_years_readings(schott_site):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), "de-de")
    assert liturgy.locale == "de-de"
    assert liturgy.source_url == "https://schott.erzabtei-beuron.de/jk27/Donnerstag.htm"
    assert types(liturgy) == ["Erste Lesung", "Antwortpsalm", "Ruf vor dem Evangelium", "Evangelium"]
    assert citations(liturgy.readings) == ["Gal 3, 1–5", "Lk 1, 68–69.70–71.72–75 (Kv: 68a)", "vgl. Apg 16, 14b", "Lk 11, 5–13"]  # Jahr II
    first, psalm, acclamation, gospel = liturgy.readings
    assert first.content.startswith("Lesung\naus dem Brief des Apostels Paulus an die Gemeinden in Galátien.\n\nIhr unvernünftigen Gálater")
    assert psalm.content.startswith("Kv Gepriesen sei der Herr, der Gott Israels! – Kv\n\n")  # hymnal number dropped
    assert acclamation.content.startswith("Halleluja. Halleluja.")
    assert gospel.content.startswith("Aus dem heiligen Evangelium nach Lukas.")
    assert (liturgy.season, liturgy.week, liturgy.color, liturgy.celebrations) == (Season.ORDINARY_TIME, 27, None, [])


def test_optional_memorial_keeps_weekday_readings_despite_missing_year_marker(schott_site):
    liturgy = get_daily_liturgy_de_de(datetime.date(2026, 10, 6))
    assert liturgy.source_url.endswith("/jk27/Dienstag.htm")
    assert citations(liturgy.readings)[:2] == ["Gal 1, 13–24", "Ps 139 (138), 1–3.13–14.15–16 (Kv: vgl. 24b)"]
    assert liturgy.celebrations == [Celebration(name="Hl. Bruno", rank=Rank.OPTIONAL_MEMORIAL)]


def test_feast_with_alternative(schott_site):
    liturgy = get_daily_liturgy_de_de(datetime.date(2026, 9, 29))
    assert liturgy.celebrations == [Celebration(name="Hl. Michael, Hl. Gabriel und Hl. Rafael", rank=Rank.FEAST)]
    first = liturgy.readings[0]
    assert first.citation == "Dan 7, 9–10.13–14"
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Erste Lesung", "Offb 12, 7–12a")]
    assert "Oder" not in first.content


def test_page_with_vigil_and_day_masses_keeps_day(schott_site):
    liturgy = get_daily_liturgy_de_de(datetime.date(2026, 8, 15))
    assert citations(liturgy.readings) == ["Offb 11, 19a; 12, 1–6a.10ab", "Ps 45 (44), 11–12.16 u. 18", "1 Kor 15, 20–27a", "", "Lk 1, 39–56"]
    assert liturgy.celebrations == [Celebration(name="Mariä Aufnahme in den Himmel", rank=Rank.SOLEMNITY)]


def test_christmas_index_page_leads_to_mass_during_the_day(schott_site):
    liturgy = get_daily_liturgy_de_de(datetime.date(2026, 12, 25))
    assert liturgy.source_url.endswith("/weihnachtszeit/weihnachten_tag.htm")
    assert citations(liturgy.readings) == ["Jes 52, 7–10", "Ps 98 (97), 1.2–3b.3c–4.5–6 (Kv: vgl. 3cd)", "Hebr 1, 1–6", "", "Joh 1, 1–18"]
    assert citations(liturgy.readings[4].alternatives) == ["Joh 1, 1–5.9–14"]  # "Oder Kurzfassung"
    assert liturgy.celebrations == [Celebration(name="Weihnachten - Hochfest der Geburt des Herrn", rank=Rank.SOLEMNITY)]


def test_easter_index_page_leads_to_sunday_mass_of_the_cycle(schott_site):
    liturgy = get_daily_liturgy_de_de(datetime.date(2025, 4, 20))
    assert liturgy.source_url.endswith("/osterzeit/ostersonntag/TagC.htm")
    assert types(liturgy) == ["Erste Lesung", "Antwortpsalm", "Zweite Lesung", "Sequenz", "Ruf vor dem Evangelium", "Evangelium"]
    assert citations(liturgy.readings[2].alternatives) == ["1 Kor 5, 6b–8"]
    assert citations(liturgy.readings[5].alternatives) == ["Joh 20, 1–18", "Lk 24, 1–12", "Lk 24, 13–35"]
    assert liturgy.celebrations == []  # "Ostersonntag": the index gives no rank


def test_index_script_is_parsed():
    script = "\nif ( null != window.Schott ) {\n  window.Schott.loadedData( {\n\t'2026-10-01' : {\n\t\tLESEJAHR_W   : 2,\n\t\tPROPRIUM     : null,\n\t\tNAME_DE      : 'Gr\\xfc\\xdfe'\n\t}\n} );\n}"
    assert _parse_index(script) == {"2026-10-01": {"LESEJAHR_W": 2, "PROPRIUM": None, "NAME_DE": "Grüße"}}


def test_sunday_without_feast_name_has_no_celebration():
    day = {"NON_PROPRIUM": [{"NAME_DE": "27. Sonntag im Jahreskreis", "url": "jk27/SonntagA.htm"}], "PROPRIUM": [{"NAME_DE": "Hl. Franz", "TYPE_D": "G", "url": "proprium/Oktober04.htm"}]}
    assert parse_schott_celebrations(day, "jk27/SonntagA.htm") == []


def test_date_without_redirect_raises(schott_site, monkeypatch):
    module = importlib.import_module("daily_liturgy.locales.de_de.find_schott_path")
    monkeypatch.setattr(module, "_redirect_location", lambda date: None)
    with pytest.raises(LiturgyNotAvailableError, match="2010-01-01"):
        module.find_schott_path(datetime.date(2010, 1, 1))


@pytest.mark.network
def test_live_site():
    liturgy = get_daily_liturgy_de_de(datetime.date.today())
    assert liturgy.readings[0].type == "Erste Lesung" and liturgy.readings[0].citation
    assert liturgy.readings[-1].type == "Evangelium"
