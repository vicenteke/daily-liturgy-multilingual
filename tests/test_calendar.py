import datetime

import pytest

from daily_liturgy import Season
from daily_liturgy.calendar.get_season_and_week import get_season_and_week

SEASONS = [
    ("2026-11-29", Season.ADVENT, 1),
    ("2026-12-24", Season.ADVENT, 4),
    ("2026-12-25", Season.CHRISTMAS, None),
    ("2027-01-10", Season.CHRISTMAS, None),  # Baptism of the Lord (Epiphany on Jan 3)
    ("2027-01-11", Season.ORDINARY_TIME, 1),
    ("2024-01-08", Season.CHRISTMAS, None),  # Baptism on Monday (Epiphany on Jan 7)
    ("2024-01-09", Season.ORDINARY_TIME, 1),
    ("2024-01-14", Season.ORDINARY_TIME, 2),
    ("2026-02-17", Season.ORDINARY_TIME, 6),
    ("2026-02-18", Season.LENT, 0),  # Ash Wednesday
    ("2026-02-22", Season.LENT, 1),
    ("2026-03-29", Season.LENT, 6),  # Palm Sunday
    ("2026-04-02", Season.EASTER_TRIDUUM, None),
    ("2026-04-04", Season.EASTER_TRIDUUM, None),
    ("2026-04-05", Season.EASTER, 1),
    ("2026-05-24", Season.EASTER, 8),  # Pentecost
    ("2026-05-25", Season.ORDINARY_TIME, 8),
    ("2026-10-08", Season.ORDINARY_TIME, 27),
    ("2026-11-22", Season.ORDINARY_TIME, 34),  # Christ the King
]


@pytest.mark.parametrize("day, season, week", SEASONS)
def test_season_and_week(day, season, week):
    assert get_season_and_week(datetime.date.fromisoformat(day)) == (season, week)

