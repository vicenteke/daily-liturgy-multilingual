"""Season and week of the General Roman Calendar (General Norms for the Liturgical
Year), with Epiphany kept on the Sunday between January 2 and 8, as in the United
States and Brazil."""

import datetime

from daily_liturgy.models import Season

_DAY = datetime.timedelta(days=1)
_WEEK = datetime.timedelta(days=7)


def get_season_and_week(date: datetime.date) -> tuple[Season, int | None]:
    easter = _easter(date.year)
    ash_wednesday = easter - 46 * _DAY
    advent = _first_advent_sunday(date.year)
    baptism = _baptism_of_the_lord(date.year)

    if date <= baptism:
        return Season.CHRISTMAS, None
    if date < ash_wednesday:
        return Season.ORDINARY_TIME, 1 + _sundays_between(baptism, date)
    if date < easter - 3 * _DAY:
        return Season.LENT, _sundays_between(ash_wednesday, date)
    if date < easter:
        return Season.EASTER_TRIDUUM, None
    if date <= easter + 49 * _DAY:
        return Season.EASTER, 1 + (date - easter).days // 7
    if date < advent:
        christ_the_king = advent - _WEEK
        return Season.ORDINARY_TIME, 34 - (christ_the_king - _sunday_on_or_before(date)).days // 7
    if date.month == 12 and date.day >= 25:
        return Season.CHRISTMAS, None
    return Season.ADVENT, 1 + (date - advent).days // 7


def _easter(year: int) -> datetime.date:
    """Anonymous Gregorian algorithm (Meeus/Jones/Butcher)."""
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    g = (8 * b + 13) // 25
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 19 * l) // 433
    month = (h + l - 7 * m + 90) // 25
    return datetime.date(year, month, (h + l - 7 * m + 33 * month + 19) % 32)


def _first_advent_sunday(year: int) -> datetime.date:
    return _sunday_on_or_before(datetime.date(year, 12, 24)) - 3 * _WEEK


def _baptism_of_the_lord(year: int) -> datetime.date:
    """Sunday after Epiphany, or the Monday after when Epiphany falls on January 7 or 8."""
    epiphany = _sunday_on_or_before(datetime.date(year, 1, 8))
    return epiphany + (_DAY if epiphany.day >= 7 else _WEEK)


def _sunday_on_or_before(date: datetime.date) -> datetime.date:
    return date - ((date.weekday() + 1) % 7) * _DAY


def _sundays_between(start: datetime.date, end: datetime.date) -> int:
    """Number of Sundays in (start, end]."""
    return (_sunday_on_or_before(end) - _sunday_on_or_before(start)).days // 7
