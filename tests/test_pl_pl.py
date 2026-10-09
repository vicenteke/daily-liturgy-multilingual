import datetime

import pytest

from daily_liturgy import Celebration, LiturgyNotAvailableError, Rank, Season, get_daily_liturgy
from daily_liturgy.locales.pl_pl import get_daily_liturgy_pl_pl
from daily_liturgy.locales.pl_pl.parse_episkopat_celebrations import parse_episkopat_celebrations


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def celebrations_for(title):
    return parse_episkopat_celebrations(f'<div class="period_name">{title}</div>')


def test_weekday(episkopat_site):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), "PL-PL")
    assert liturgy.locale == "pl-pl"
    assert liturgy.source_url == "https://episkopat.pl/liturgia/2026-10-08"
    assert types(liturgy) == ["Pierwsze czytanie", "Psalm responsoryjny", "Werset przed Ewangelią (Alleluja)", "Ewangelia"]
    assert [r.citation for r in liturgy.readings] == ["Ga 3, 1-5", "Łk 1, 69-70. 71-73. 74-75 (R.: por. 68)", "Dz 16, 14b", "Łk 11, 5-13"]
    assert liturgy.readings[0].content.startswith("Czytanie z Listu Świętego Pawła Apostoła do Galatów\n\nO, nierozumni Galaci!")
    assert (liturgy.season, liturgy.week, liturgy.color, liturgy.celebrations) == (Season.ORDINARY_TIME, 27, None, [])


def test_sunday_has_second_reading_and_skips_homilies(episkopat_site):
    liturgy = get_daily_liturgy_pl_pl(datetime.date(2026, 10, 4))
    assert types(liturgy) == ["Pierwsze czytanie", "Psalm responsoryjny", "Drugie czytanie", "Werset przed Ewangelią (Alleluja)", "Ewangelia"]


def test_feast_with_alternative(episkopat_site):
    liturgy = get_daily_liturgy_pl_pl(datetime.date(2026, 9, 29))
    assert liturgy.celebrations == [Celebration(name="Świętych Archaniołów Michała, Gabriela i Rafała", rank=Rank.FEAST)]
    assert liturgy.color is None
    first = liturgy.readings[0]
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Pierwsze czytanie", "Ap 12, 7-12a")]
    assert first.alternatives[0].content.startswith("Czytanie z Apokalipsy Świętego Jana Apostoła")
    assert "lub do wyboru" not in first.content


def test_easter_alternatives(episkopat_site):
    readings = get_daily_liturgy_pl_pl(datetime.date(2025, 4, 20)).readings
    assert [alt.citation for alt in readings[2].alternatives] == ["1 Kor 5, 6b-8"]
    assert [alt.citation for alt in readings[4].alternatives] == ["Łk 24, 13-35"]


@pytest.mark.parametrize(
    "day, expected",
    [
        (datetime.date(2026, 10, 7), [Celebration(name="Najśw. Maryi Panny Różańcowej", rank=Rank.MEMORIAL)]),
        (datetime.date(2026, 10, 12), [Celebration(name="bł. Jana Beyzyma, prezbitera", rank=Rank.OPTIONAL_MEMORIAL)]),
        (datetime.date(2026, 11, 1), [Celebration(name="Wszystkich Świętych", rank=Rank.SOLEMNITY)]),
        (datetime.date(2026, 12, 25), [Celebration(name="Narodzenia Pańskiego", rank=Rank.SOLEMNITY)]),
        (datetime.date(2025, 4, 20), []),  # "Niedziela Wielkanocna": no rank published
    ],
)
def test_celebrations(episkopat_site, day, expected):
    assert get_daily_liturgy_pl_pl(day).celebrations == expected


def test_several_optional_memorials():
    title = "Dzień powszedni albo wspomnienie św. Jana Kapistrana, prezbitera albo wspomnienie św. Józefa Bilczewskiego, biskupa"
    assert celebrations_for(title) == [
        Celebration(name="św. Jana Kapistrana, prezbitera", rank=Rank.OPTIONAL_MEMORIAL),
        Celebration(name="św. Józefa Bilczewskiego, biskupa", rank=Rank.OPTIONAL_MEMORIAL),
    ]


@pytest.mark.parametrize("title", ["Zesłanie Ducha Świętego", "Chrystusa Króla", "Wielki Post - Środa Popielcowa", "Dzień Powszedni"])
def test_titles_without_rank_are_not_guessed(title):
    assert celebrations_for(title) == []


def test_all_souls_is_not_a_memorial():
    assert celebrations_for("Wspomnienie wszystkich wiernych zmarłych") == [Celebration(name="wszystkich wiernych zmarłych", rank=None)]


def test_page_without_readings_raises(monkeypatch):
    import importlib

    module = importlib.import_module("daily_liturgy.locales.pl_pl.get_daily_liturgy_pl_pl")
    monkeypatch.setattr(module, "fetch_episkopat_page", lambda url: "<div class='lit-right'></div>")
    with pytest.raises(LiturgyNotAvailableError, match="2030-01-01"):
        get_daily_liturgy_pl_pl(datetime.date(2030, 1, 1))


@pytest.mark.network
def test_live_site():
    readings = get_daily_liturgy_pl_pl(datetime.date(2026, 10, 8)).readings
    assert readings[0].citation == "Ga 3, 1-5"
    assert readings[-1].type == "Ewangelia"
