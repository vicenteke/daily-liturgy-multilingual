import datetime

from daily_liturgy.aelf.fetch_aelf_masses import AELF_MASSES_URL, fetch_aelf_masses
from daily_liturgy.aelf.parse_aelf_celebrations import parse_aelf_celebrations
from daily_liturgy.aelf.parse_aelf_readings import parse_aelf_readings
from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.exceptions import LiturgyNotAvailableError
from daily_liturgy.models import Color, DailyLiturgy

_COLORS = {"vert": Color.GREEN, "violet": Color.VIOLET, "blanc": Color.WHITE, "rouge": Color.RED, "rose": Color.ROSE, "noir": Color.BLACK}
_MAIN_MASS = "messe du jour"


def get_aelf_liturgy(date: datetime.date, zone: str, locale: str) -> DailyLiturgy:
    """The French locales, one AELF zone each (registered with functools.partial)."""
    data = fetch_aelf_masses(date, zone)
    masses = data.get("messes") or []
    if not masses:
        raise LiturgyNotAvailableError(f"AELF has no Mass for {date.isoformat()} in zone {zone!r}.")
    informations = data.get("informations") or {}
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale=locale,
        source_url=AELF_MASSES_URL.format(date=date, zone=zone),
        season=season,
        week=week,
        color=_COLORS.get(str(informations.get("couleur") or "").strip().lower()),
        celebrations=parse_aelf_celebrations(informations),
        readings=parse_aelf_readings(_choose_mass(masses)),
    )


def _choose_mass(masses: list[dict]) -> dict:
    """The Mass during the Day ("Messe du jour", "MESSE DU JOUR DE PÂQUES") when there
    are several (vigil, night, dawn), otherwise the first."""
    for mass in masses:
        if _MAIN_MASS in str(mass.get("nom") or "").lower():
            return mass
    return masses[0]
