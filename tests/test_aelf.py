import datetime

import pytest

from daily_liturgy import Celebration, Color, LiturgyNotAvailableError, Rank, Season, get_daily_liturgy
from daily_liturgy.aelf import get_aelf_liturgy
from daily_liturgy.aelf.fetch_aelf_masses import fetch_aelf_masses
from daily_liturgy.aelf.parse_aelf_readings import parse_aelf_readings


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def citations(readings):
    return [reading.citation for reading in readings]


def test_weekday(aelf_api):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), "fr-fr")
    assert liturgy.locale == "fr-fr"
    assert liturgy.source_url == "https://api.aelf.org/v1/messes/2026-10-08/france"
    assert types(liturgy) == ["Première lecture", "Cantique", "Acclamation", "Évangile"]
    assert citations(liturgy.readings) == ["Ga 3, 1-5", "Lc 1, 69-70, 71-72, 73-75", "cf. Ac 16, 14b", "Lc 11, 5-13"]
    first, canticle, acclamation, gospel = liturgy.readings
    assert first.content.startswith("Lecture de la lettre de saint Paul apôtre aux Galates\n\nGalates stupides,\nqui donc")
    assert canticle.content.startswith("Béni soit le Seigneur, le Dieu d’Israël,\ncar il a visité son peuple.\n\nIl a fait surgir")
    assert acclamation.content.startswith("Alléluia. Alléluia.\nSeigneur, ouvre notre cœur")
    assert gospel.content.startswith("Évangile de Jésus Christ selon saint Luc\n\nEn ce temps-là,")
    assert (liturgy.season, liturgy.week, liturgy.color, liturgy.celebrations) == (Season.ORDINARY_TIME, 27, Color.GREEN, [])


def test_feast_with_alternative(aelf_api):
    liturgy = get_daily_liturgy(datetime.date(2026, 9, 29), "fr-fr")
    assert (liturgy.color, liturgy.celebrations) == (Color.WHITE, [Celebration(name="Saint Michel, Saint Gabriel et Saint Raphaël, Archanges", rank=Rank.FEAST)])
    first = liturgy.readings[0]
    assert first.citation == "Dn 7, 9-10.13-14"
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Première lecture", "Ap 12, 7-12a")]


def test_easter_day_mass_sequence_and_alternatives(aelf_api):
    liturgy = get_daily_liturgy(datetime.date(2025, 4, 20), "fr-fr")
    assert types(liturgy) == ["Première lecture", "Psaume", "Deuxième lecture", "Séquence", "Acclamation", "Évangile"]
    assert citations(liturgy.readings[2].alternatives) == ["1 Co 5, 6b-8"]
    assert citations(liturgy.readings[5].alternatives) == ["Lc 24, 13-35"]
    assert liturgy.celebrations == [Celebration(name="Résurrection du Seigneur", rank=Rank.SOLEMNITY)]


def test_christmas_keeps_mass_during_the_day(aelf_api):
    liturgy = get_daily_liturgy(datetime.date(2026, 12, 25), "fr-fr")
    assert citations(liturgy.readings) == ["Is 52, 7-10", "97 (98), 1, 2-3ab, 3cd-4, 5-6", "He 1, 1-6", "", "Jn 1, 1-18"]
    assert liturgy.celebrations == [Celebration(name="Nativité du Seigneur", rank=Rank.SOLEMNITY)]


def test_optional_memorial(aelf_api):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 6), "fr-fr")
    assert liturgy.color == Color.GREEN
    assert liturgy.celebrations == [Celebration(name="S. Bruno, prêtre", rank=Rank.OPTIONAL_MEMORIAL)]


def test_national_calendars_differ(aelf_api):
    canada = get_daily_liturgy(datetime.date(2026, 1, 12), "fr-ca")
    roman = get_daily_liturgy(datetime.date(2026, 1, 12), "fr")
    assert canada.source_url.endswith("/canada") and roman.source_url.endswith("/romain")
    assert (canada.color, canada.celebrations) == (Color.WHITE, [Celebration(name="Ste Marguerite Bourgeoys", rank=Rank.MEMORIAL)])
    assert (roman.color, roman.celebrations) == (Color.GREEN, [])
    swiss = get_daily_liturgy(datetime.date(2026, 9, 25), "fr-ch")
    assert swiss.celebrations == [Celebration(name="S. Nicolas de Flüe, ermite", rank=Rank.SOLEMNITY)]
    assert citations(swiss.readings)[0] == "Sg 7, 27c–8, 2a.3-7.9"


def test_unpublished_date_raises(aelf_api):
    with pytest.raises(LiturgyNotAvailableError, match="2030-06-01"):
        get_aelf_liturgy(datetime.date(2030, 6, 1), zone="france", locale="fr-fr")


@pytest.mark.network
@pytest.mark.parametrize("zone", ["romain", "france", "belgique", "luxembourg", "suisse", "monaco", "canada"])
def test_live_api(zone):
    data = fetch_aelf_masses(datetime.date.today(), zone)
    readings = parse_aelf_readings(data["messes"][0])
    assert readings[0].type == "Première lecture" and readings[0].citation
    assert readings[-1].type == "Évangile"
