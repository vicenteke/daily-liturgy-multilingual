import datetime

from bs4 import Tag

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.exceptions import LiturgyNotAvailableError
from daily_liturgy.locales.it_it.fetch_cei_page import CEI_DAY_URL, fetch_cei_page
from daily_liturgy.locales.it_it.parse_cei_celebrations import parse_cei_celebrations
from daily_liturgy.locales.it_it.parse_cei_color import parse_cei_color
from daily_liturgy.locales.it_it.parse_cei_readings import parse_cei_readings
from daily_liturgy.locales.it_it.split_cei_masses import split_cei_masses
from daily_liturgy.models import DailyLiturgy

_MAIN_MASS = "messa del giorno"


def get_daily_liturgy_it_it(date: datetime.date) -> DailyLiturgy:
    masses = split_cei_masses(fetch_cei_page(date))
    if not masses:
        raise LiturgyNotAvailableError(f"CEI's page for {date.isoformat()} has no Mass.")
    mass = _choose_mass(masses)
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale="it-it",
        source_url=CEI_DAY_URL.format(date),
        season=season,
        week=week,
        color=parse_cei_color(mass),
        celebrations=parse_cei_celebrations([title for title, _ in masses]),
        readings=parse_cei_readings(mass),
    )


def _choose_mass(masses: list[tuple[str, Tag]]) -> Tag:
    """The Mass during the Day on Christmas (matching en-us), otherwise the first Mass:
    the weekday's on a day with an optional memorial, "Messa 1" on All Souls."""
    for title, mass in masses:
        if _MAIN_MASS in title.lower():
            return mass
    return masses[0][1]
