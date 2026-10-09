import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.locales.en_ph.fetch_cbcp_page import fetch_cbcp_page
from daily_liturgy.locales.en_ph.parse_cbcp_readings import parse_cbcp_readings
from daily_liturgy.models import DailyLiturgy


def get_daily_liturgy_en_ph(date: datetime.date) -> DailyLiturgy:
    """CBCP's pages follow the general calendar, so Philippine celebrations may be missing
    from them, and they publish no color: `celebrations` is always empty and `color`
    always None."""
    url = f"https://cbcp.ph/readings/{date:%B}-{date.day}-{date.year}/".lower()
    page = fetch_cbcp_page(url, date)
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale="en-ph",
        source_url=url,
        season=season,
        week=week,
        color=None,
        celebrations=[],
        readings=parse_cbcp_readings(page),
    )
