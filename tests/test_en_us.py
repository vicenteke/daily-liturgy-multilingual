import datetime

import pytest

from daily_liturgy import Celebration, LiturgyNotAvailableError, Rank, Season
from daily_liturgy.locales.en_us import get_daily_liturgy_en_us
from daily_liturgy.locales.en_us.fetch_usccb_items import fetch_usccb_items
from daily_liturgy.locales.en_us.parse_usccb_readings import parse_usccb_readings
from daily_liturgy.locales.en_us.select_usccb_item import select_usccb_item


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def test_weekday_has_four_readings(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 10, 8))
    assert liturgy.date == datetime.date(2026, 10, 8)
    assert liturgy.locale == "en-us"
    assert liturgy.source_url == "https://bible.usccb.org/bible/readings/100826.cfm"
    assert types(liturgy) == ["Reading 1", "Responsorial Psalm", "Alleluia", "Gospel"]

    first, psalm, _, gospel = liturgy.readings
    assert first.citation == "Galatians 3:1-5"
    assert first.content.startswith("O stupid Galatians!\nWho has bewitched you,")
    assert psalm.content.startswith("R. (68) Blessed be the Lord")
    assert gospel.citation == "Luke 11:5-13"


def test_weekday_metadata(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 10, 8))
    assert (liturgy.season, liturgy.week) == (Season.ORDINARY_TIME, 27)
    assert liturgy.color is None  # USCCB publishes no color
    assert liturgy.celebrations == []


def test_feast_metadata(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 9, 29))
    assert liturgy.celebrations == [Celebration(name="Saints Michael, Gabriel, and Raphael, Archangels", rank=Rank.FEAST)]
    assert liturgy.color is None


def test_memorial_strips_article(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 10, 2))
    assert liturgy.celebrations == [Celebration(name="Holy Guardian Angels", rank=Rank.MEMORIAL)]


def test_sunday_has_second_reading(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 10, 4))
    assert types(liturgy) == ["Reading 1", "Responsorial Psalm", "Reading 2", "Alleluia", "Gospel"]
    assert liturgy.readings[2].citation == "Philippians 4:6-9"


def test_or_section_becomes_alternative(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 9, 29))
    assert types(liturgy) == ["Reading 1", "Responsorial Psalm", "Alleluia", "Gospel"]
    first = liturgy.readings[0]
    assert first.citation == "Daniel 7:9-10, 13-14"
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Reading 1", "Revelation 12:7-12ab")]
    assert first.alternatives[0].content
    assert all(not r.alternatives for r in liturgy.readings[1:])


def test_citation_whitespace_is_normalized(usccb_feed):
    liturgy = get_daily_liturgy_en_us(datetime.date(2026, 10, 5))
    assert liturgy.readings[1].citation == "Psalm 111:1b-2, 7-8, 9, 10c"


def test_date_outside_feed_raises(usccb_feed):
    with pytest.raises(LiturgyNotAvailableError, match="2026-09-29 to 2026-10-08"):
        get_daily_liturgy_en_us(datetime.date(2026, 12, 25))


def test_multiple_masses_prefers_mass_during_the_day():
    items = [
        {"link": "https://bible.usccb.org/bible/readings/122526-Vigil.cfm", "description": ""},
        {"link": "https://bible.usccb.org/bible/readings/122526.cfm", "description": ""},
        {"link": "https://bible.usccb.org/bible/readings/122626.cfm", "description": ""},
    ]
    selected = select_usccb_item(items, datetime.date(2026, 12, 25))
    assert selected["link"].endswith("/122526.cfm")


@pytest.mark.network
def test_live_feed_today():
    items = fetch_usccb_items()
    assert items
    readings = parse_usccb_readings(items[0]["description"])
    assert readings[0].type == "Reading 1"
    assert readings[-1].type == "Gospel"
