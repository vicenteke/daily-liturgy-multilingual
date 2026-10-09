import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.exceptions import LiturgyNotAvailableError
from daily_liturgy.ibreviary.fetch_ibreviary_page import IBREVIARY_READINGS_URL, fetch_ibreviary_page
from daily_liturgy.ibreviary.parse_ibreviary_readings import parse_ibreviary_readings
from daily_liturgy.models import DailyLiturgy


def get_ibreviary_liturgy(date: datetime.date, language: str) -> DailyLiturgy:
    """iBreviary's readings pages name neither the day's celebration nor its color, so
    `celebrations` is always empty and `color` always None. `locale` is the iBreviary
    language code; `get_daily_liturgy` replaces it with the locale that was asked for."""
    readings = parse_ibreviary_readings(fetch_ibreviary_page(date, language), language)
    if not any(reading.citation and reading.content for reading in readings):  # an empty page still has its headings
        raise LiturgyNotAvailableError(f"iBreviary has no {language} Mass readings for {date.isoformat()}.")
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale=language,
        source_url=IBREVIARY_READINGS_URL,
        season=season,
        week=week,
        color=None,
        celebrations=[],
        readings=readings,
    )
