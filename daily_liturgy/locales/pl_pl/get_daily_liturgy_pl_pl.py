import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.exceptions import LiturgyNotAvailableError
from daily_liturgy.locales.pl_pl.fetch_episkopat_page import fetch_episkopat_page
from daily_liturgy.locales.pl_pl.parse_episkopat_celebrations import parse_episkopat_celebrations
from daily_liturgy.locales.pl_pl.parse_episkopat_readings import parse_episkopat_readings
from daily_liturgy.models import DailyLiturgy


def get_daily_liturgy_pl_pl(date: datetime.date) -> DailyLiturgy:
    """The Polish bishops' conference publishes no liturgical color, so `color` is None."""
    url = f"https://episkopat.pl/liturgia/{date.isoformat()}"
    page = fetch_episkopat_page(url)
    readings = parse_episkopat_readings(page)
    if not readings:
        raise LiturgyNotAvailableError(f"episkopat.pl has no readings for {date.isoformat()}.")
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale="pl-pl",
        source_url=url,
        season=season,
        week=week,
        color=None,
        celebrations=parse_episkopat_celebrations(page),
        readings=readings,
    )
