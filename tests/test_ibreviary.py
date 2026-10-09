import datetime
import importlib

import pytest

from daily_liturgy import LiturgyNotAvailableError, Season, get_daily_liturgy
from daily_liturgy.ibreviary.fetch_ibreviary_page import fetch_ibreviary_page
from daily_liturgy.ibreviary.italian import get_daily_liturgy_italian
from daily_liturgy.ibreviary.find_ibreviary_citation import find_ibreviary_citation
from daily_liturgy.ibreviary.latin import get_daily_liturgy_latin
from daily_liturgy.ibreviary.parse_ibreviary_readings import parse_ibreviary_readings

OCT_8, SEP_29, EASTER_2025 = datetime.date(2026, 10, 8), datetime.date(2026, 9, 29), datetime.date(2025, 4, 20)


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def citations(readings):
    return [reading.citation for reading in readings]


# Latin


def test_latin_weekday(ibreviary_site):
    liturgy = get_daily_liturgy_latin(OCT_8)
    assert liturgy.source_url == "https://www.ibreviary.com/m2/letture.php?s=letture"
    assert types(liturgy) == ["Lectio Prima", "Psalmus Responsorialis", "Alleluia", "Evangélium"]
    assert citations(liturgy.readings) == ["Gal 3, 1-5", "Lc 1, 69-70. 71-72. 73-75", "Cf. Act 16, 14b", "Lc 11, 5-13"]

    first, psalm, _, gospel = liturgy.readings
    assert first.content.startswith("Ex operibus Legis Spiritum accepistis, an ex auditu fidei.\n\nLéctio Epístolæ")
    assert first.content.endswith("Verbum Dómini.")
    assert psalm.content.startswith("Rit:\n\n℟. (68) Benedíctus Deus Israel")
    assert "Léctio sancti Evangélii secúndum Lucam" in gospel.content


def test_metadata_without_color_or_celebrations(ibreviary_site):
    liturgy = get_daily_liturgy(OCT_8, "LA")
    assert liturgy.locale == "la"
    assert (liturgy.season, liturgy.week) == (Season.ORDINARY_TIME, 27)
    assert (liturgy.color, liturgy.celebrations) == (None, [])


def test_latin_sunday_has_second_reading(ibreviary_site):
    liturgy = get_daily_liturgy_latin(datetime.date(2026, 10, 4))
    assert types(liturgy) == ["Lectio Prima", "Psalmus Responsorialis", "Lectio secunda", "Alleluia", "Evangélium"]
    assert liturgy.readings[2].citation == "Phil 4, 6-9"


def test_latin_proper_readings_win_over_ferial(ibreviary_site):
    liturgy = get_daily_liturgy_latin(SEP_29)
    assert citations(liturgy.readings) == ["Dan 7, 9-10. 13-14", "Ps 137, 1-2a. 2b-3. 4-5", "Ps 102, 21", "Io 1, 47-51"]
    first = liturgy.readings[0]
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Lectio Prima", "Apoc 12, 7-12a")]
    assert first.alternatives[0].content.startswith("Míchael et angeli eius")


def test_latin_alternatives_in_their_own_blocks(ibreviary_site):
    liturgy = get_daily_liturgy_latin(EASTER_2025)
    second, gospel = liturgy.readings[2], liturgy.readings[4]
    assert citations(second.alternatives) == ["1 Cor 5, 6b-8"]
    assert citations(gospel.alternatives) == ["Lc 24, 1-12", "Lc 24, 13-35"]
    assert gospel.alternatives[0].content.startswith("Quid quæritis viventem cum mortuis?")


def test_latin_shorter_form_and_missing_citation(ibreviary_site):
    readings = get_daily_liturgy_latin(datetime.date(2026, 12, 25)).readings
    assert readings[3].type == "Alleluia" and readings[3].citation == ""
    assert citations(readings[4].alternatives) == ["Mt 1,18-25"]
    assert readings[4].alternatives[0].content.startswith("✠ Léctio sancti Evangélii")


# Other languages


@pytest.mark.parametrize(
    "locale, expected",
    [
        ("en", ["First Reading", "Responsorial Psalm", "Acclamation before the Gospel", "Gospel"]),
        ("es-es", ["Primera Lectura", "Salmo Responsorial", "Aclamación antes del Evangelio", "Evangelio"]),
        ("pt-pt", ["Primeira Leitura", "Salmo Responsorial", "Aclamação ao Evangelho", "Evangelho"]),
        ("ro-ro", ["Lectura întâi", "Psalmul responsorial", "Versetul la Evanghelie", "Evanghelia"]),
        ("gl-es", ["Prima Lettura", "Salmo Responsoriale", "Canto al Vangelo", "Vangelo"]),  # Italian labels, Galician text
        ("ar", ["القراءة الأولى", "المزمور", "نشيد الإنجيل", "الإنجيل"]),
    ],
)
def test_weekday_in_every_language(ibreviary_site, locale, expected):
    liturgy = get_daily_liturgy(OCT_8, locale)
    assert liturgy.locale == locale
    assert types(liturgy) == expected
    assert all(reading.content for reading in liturgy.readings)


def test_citations_as_published(ibreviary_site):
    assert citations(get_daily_liturgy(OCT_8, "en").readings) == ["Gal 3:1-5", "Luke 1:69-70, 71-72, 73-75", "See Acts 16:14b", "Lk 11:5-13"]
    assert citations(get_daily_liturgy(OCT_8, "es-es").readings) == ["Gál 3, 1-5.", "Lc 1, 69-70.71-72.73-75", "", "Lc 11, 5-13."]
    assert citations(get_daily_liturgy(OCT_8, "ar").readings)[0] == "(غل ٣: ١-٥)"


def test_italian_citation_found_in_text(ibreviary_site):
    """Italian isn't registered ("it-it" comes from CEI), but the function is kept."""
    first, _, _, gospel = get_daily_liturgy_italian(OCT_8).readings
    assert (first.citation, gospel.citation) == ("Gal 3,1-5", "Lc 11,5-13")


@pytest.mark.parametrize(
    "locale, main, alternative, alternative_start",
    [
        ("en", "Dn 7:9-10, 13-14", "Rev 12:7-12ab", "Michael and his angels battled against the dragon."),
        ("es-es", "Dn 7, 9-10.13-14.", "Ap 12, 7-12a", "Miguel y sus ángeles combatieron contra el dragón"),
        ("pt-pt", "Dan 7, 9-10.13-14", "Ap 12, 7-12a", "«Miguel e os seus Anjos lutaram contra o Dragão»"),
        ("gl-es", "Dn 7, 9-10. 13-14.", "Ap 12, 7-12a", "Miguel e os seus anxos loitaban contra o dragón"),
    ],
)
def test_inline_alternative(ibreviary_site, locale, main, alternative, alternative_start):
    first = get_daily_liturgy(SEP_29, locale).readings[0]
    assert first.citation == main
    assert citations(first.alternatives) == [alternative]
    assert first.alternatives[0].content.startswith(alternative_start)


def test_alternative_citation_from_heading(ibreviary_site):
    """The source marks the antiphon as the alternative's citation; the heading lists the real one."""
    readings = get_daily_liturgy(EASTER_2025, "en").readings
    second, gospel = readings[2], readings[4]
    assert (second.citation, citations(second.alternatives)) == ("Col 3:1-4", ["I Cor 5:6b-8"])
    assert second.alternatives[0].content.startswith("Clear out the old yeast")
    assert (gospel.citation, citations(gospel.alternatives)) == ("Jn 20:1-9", ["Lk 24:1-12", "Luke 24:13-35"])


@pytest.mark.parametrize("locale, alternative", [("es-es", "1 Cor 5, 6b-8"), ("pt-pt", "1 Cor 5, 6b-8")])
def test_easter_second_reading_alternative(ibreviary_site, locale, alternative):
    second = get_daily_liturgy(EASTER_2025, locale).readings[2]
    assert citations(second.alternatives) == [alternative]
    assert not second.alternatives[0].content.upper().startswith("OU")


def test_italian_inline_alternatives(ibreviary_site):
    first = get_daily_liturgy_italian(SEP_29).readings[0]
    assert (first.citation, citations(first.alternatives)) == ("Dn 7,9-10.13-14", ["Ap 12, 7-12"])
    second = get_daily_liturgy_italian(EASTER_2025).readings[2]
    assert citations(second.alternatives) == ["1Cor 5,6b-8"]


def test_psalm_refrain_options_are_not_alternatives(ibreviary_site):
    psalm = get_daily_liturgy(EASTER_2025, "pt-pt").readings[1]
    assert psalm.alternatives == []
    assert "Ou: Aleluia" in psalm.content


@pytest.mark.parametrize("locale, day, gospel", [("es-es", datetime.date(2026, 10, 12), "Lc 11, 27-28."), ("pt-pt", datetime.date(2026, 5, 13), "Lc 11, 27-28")])
def test_national_proper_days(ibreviary_site, locale, day, gospel):
    """Our Lady of the Pillar (Spain) and Our Lady of Fátima (Portugal) have their own readings."""
    assert get_daily_liturgy(day, locale).readings[-1].citation == gospel


def test_page_with_empty_readings_raises(ibreviary_site):
    with pytest.raises(LiturgyNotAvailableError, match="ro Mass readings for 2025-04-20"):
        get_daily_liturgy(EASTER_2025, "ro-ro")


@pytest.mark.parametrize(
    "text, citation",
    [("Dal libro del profeta Daniele\nDn 7,9-10.13-14\n\nIo", "Dn 7,9-10.13-14"), ("Ou 1 Cor 5, 6b-8", "1 Cor 5, 6b-8"), ("1Cor 5,6b-8", "1Cor 5,6b-8"), ("Aleluya, aleluya.", "")],
)
def test_find_citation(text, citation):
    assert find_ibreviary_citation(text) == citation


# Fetching


def test_date_not_accepted_raises(monkeypatch):
    module = importlib.import_module("daily_liturgy.ibreviary.fetch_ibreviary_page")
    monkeypatch.setattr(module, "_download", lambda date, language: ("<p>Dies: Feria quinta, 8 October 2026</p>", ""))
    with pytest.raises(LiturgyNotAvailableError, match="2030-01-01"):
        fetch_ibreviary_page(datetime.date(2030, 1, 1), "la")


def test_date_echo_in_arabic_is_accepted(monkeypatch):
    module = importlib.import_module("daily_liturgy.ibreviary.fetch_ibreviary_page")
    echo = "<p>يوم: يوم الخميس, 8 تشرين الأول - أكتوبر 2026</p>"
    monkeypatch.setattr(module, "_download", lambda date, language: (echo, '<span class="titolo">x</span>'))
    assert fetch_ibreviary_page(OCT_8, "ar")


def test_page_without_readings_raises(monkeypatch):
    module = importlib.import_module("daily_liturgy.ibreviary.fetch_ibreviary_page")
    monkeypatch.setattr(module, "_download", lambda date, language: ("<p>Dies: Feria, 1 Ianuarius 2030</p>", "<div id='contenuto'></div>"))
    with pytest.raises(LiturgyNotAvailableError, match="no Mass readings"):
        fetch_ibreviary_page(datetime.date(2030, 1, 1), "la")


@pytest.mark.network
@pytest.mark.parametrize("language", ["la", "en", "es"])
def test_live_site(language):
    readings = parse_ibreviary_readings(fetch_ibreviary_page(datetime.date.today(), language), language)
    assert len(readings) >= 4
    assert all(reading.content for reading in readings)
