import datetime

import httpx
import pytest

from daily_liturgy import LiturgyNotAvailableError, Season, get_daily_liturgy
from daily_liturgy.locales.en_ph import get_daily_liturgy_en_ph
from daily_liturgy.locales.en_ph.fetch_cbcp_page import fetch_cbcp_page
from daily_liturgy.locales.en_ph.parse_cbcp_readings import parse_cbcp_readings


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def test_weekday(cbcp_site):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), "EN-PH")
    assert liturgy.locale == "en-ph"
    assert liturgy.source_url == "https://cbcp.ph/readings/october-8-2026/"
    assert types(liturgy) == ["Reading 1", "Responsorial Psalm", "Alleluia", "Gospel"]
    assert [r.citation for r in liturgy.readings] == ["Galatians 3:1-5", "Luke 1:69-70, 71-72, 73-75", "Acts 16:14b", "Luke 11:5-13"]
    assert liturgy.readings[0].content.startswith("O stupid Galatians!\nWho has bewitched you,")
    assert (liturgy.season, liturgy.week, liturgy.color, liturgy.celebrations) == (Season.ORDINARY_TIME, 27, None, [])


def test_sunday_has_second_reading(cbcp_site):
    liturgy = get_daily_liturgy_en_ph(datetime.date(2026, 10, 4))
    assert types(liturgy) == ["Reading 1", "Responsorial Psalm", "Reading 2", "Alleluia", "Gospel"]
    assert liturgy.readings[2].citation == "Philippians 4:6-9"


def test_alternative(cbcp_site):
    first = get_daily_liturgy_en_ph(datetime.date(2026, 9, 29)).readings[0]
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Reading 1", "Revelation 12:7-12ab")]
    assert first.alternatives[0].content.startswith("War broke out in heaven;")
    assert not first.content.endswith("or")


@pytest.mark.parametrize("day", [datetime.date(2026, 9, 29), datetime.date(2026, 10, 7), datetime.date(2026, 11, 1)])
def test_no_celebrations_or_color_even_on_feasts(cbcp_site, day):
    liturgy = get_daily_liturgy_en_ph(day)
    assert (liturgy.celebrations, liturgy.color) == ([], None)


def test_solemnity_on_sunday_readings(cbcp_site):
    assert get_daily_liturgy_en_ph(datetime.date(2026, 11, 1)).readings[-1].citation == "Matthew 5:1-12a"


def test_unpublished_date_raises(cbcp_site):
    with pytest.raises(LiturgyNotAvailableError, match="2026-12-25"):
        get_daily_liturgy_en_ph(datetime.date(2026, 12, 25))


def test_404_raises(monkeypatch):
    monkeypatch.setattr(httpx, "get", lambda url, **kwargs: httpx.Response(404, request=httpx.Request("GET", url)))
    with pytest.raises(LiturgyNotAvailableError, match="2025-01-01"):
        fetch_cbcp_page("https://cbcp.ph/readings/january-1-2025/", datetime.date(2025, 1, 1))


def test_page_without_readings():
    assert parse_cbcp_readings("<div class='et_pb_text_inner'><h3>Saint of the Day</h3></div>") == []


@pytest.mark.network
def test_live_site():
    readings = get_daily_liturgy_en_ph(datetime.date(2026, 10, 8)).readings
    assert readings[0].citation == "Galatians 3:1-5"
    assert readings[-1].type == "Gospel"

