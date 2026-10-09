import datetime

from daily_liturgy.ibreviary.get_ibreviary_liturgy import get_ibreviary_liturgy
from daily_liturgy.models import DailyLiturgy


def get_daily_liturgy_latin(date: datetime.date) -> DailyLiturgy:
    return get_ibreviary_liturgy(date, "la")
