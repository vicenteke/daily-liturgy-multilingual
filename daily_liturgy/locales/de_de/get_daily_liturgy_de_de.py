import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.exceptions import LiturgyNotAvailableError
from daily_liturgy.locales.de_de.fetch_schott_index import fetch_schott_index
from daily_liturgy.locales.de_de.fetch_schott_page import SCHOTT_URL, fetch_schott_page
from daily_liturgy.locales.de_de.find_schott_path import find_schott_path
from daily_liturgy.locales.de_de.parse_schott_celebrations import parse_schott_celebrations
from daily_liturgy.locales.de_de.parse_schott_readings import parse_schott_readings
from daily_liturgy.locales.de_de.select_schott_mass import select_schott_mass
from daily_liturgy.models import DailyLiturgy

_MEMORIALS = {"G", "g"}


def get_daily_liturgy_de_de(date: datetime.date) -> DailyLiturgy:
    """Schott publishes no color, so it's always None."""
    day = fetch_schott_index(date)
    path = find_schott_path(date)
    readings_path = _readings_path(day, path)
    page = fetch_schott_page(readings_path)
    saint_page = page if readings_path == path else None
    mass_path = select_schott_mass(page, day.get("LESEJAHR_S") or 0)
    if mass_path is not None:
        readings_path, page = mass_path, fetch_schott_page(mass_path)
    readings = parse_schott_readings(page, day.get("LESEJAHR_W") or 0)
    if not readings:
        raise LiturgyNotAvailableError(f"Schott's page for {date.isoformat()} has no readings.")
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale="de-de",
        source_url=f"{SCHOTT_URL}/{readings_path}",
        season=season,
        week=week,
        color=None,
        celebrations=parse_schott_celebrations(day, path, saint_page),
        readings=readings,
    )


def _readings_path(day: dict, path: str) -> str:
    """On memorials Schott opens the saint's page, with readings chosen for the saint.
    The weekday's readings are kept instead, as in the other locales; the saint stays
    in `celebrations`."""
    saint = next((entry for entry in day.get("PROPRIUM") or [] if entry.get("url") == path), None)
    weekday = next((entry.get("url") for entry in day.get("NON_PROPRIUM") or [] if entry.get("url")), None)
    if saint is not None and saint.get("TYPE_D") in _MEMORIALS and weekday:
        return weekday
    return path
