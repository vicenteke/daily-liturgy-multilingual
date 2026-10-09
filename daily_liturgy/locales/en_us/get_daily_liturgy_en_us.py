import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.locales.en_us.fetch_usccb_items import fetch_usccb_items
from daily_liturgy.locales.en_us.parse_usccb_celebrations import parse_usccb_celebrations
from daily_liturgy.locales.en_us.parse_usccb_readings import parse_usccb_readings
from daily_liturgy.locales.en_us.select_usccb_item import select_usccb_item
from daily_liturgy.models import DailyLiturgy


def get_daily_liturgy_en_us(date: datetime.date) -> DailyLiturgy:
    """USCCB publishes no color, so it's always None (never guessed from the season)."""
    item = select_usccb_item(fetch_usccb_items(), date)
    season, week = get_season_and_week(date)
    celebrations = parse_usccb_celebrations(item["title"])
    return DailyLiturgy(
        date=date,
        locale="en-us",
        source_url=item["link"],
        season=season,
        week=week,
        color=None,  # USCCB publishes no color
        celebrations=celebrations,
        readings=parse_usccb_readings(item["description"]),
    )
