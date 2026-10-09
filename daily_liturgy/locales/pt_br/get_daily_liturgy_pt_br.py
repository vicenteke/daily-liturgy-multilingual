import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.models import DailyLiturgy
from daily_liturgy.locales.pt_br.fetch_cancaonova_page import fetch_cancaonova_page
from daily_liturgy.locales.pt_br.find_cancaonova_day_url import find_cancaonova_day_url
from daily_liturgy.locales.pt_br.parse_cancaonova_celebrations import parse_cancaonova_celebrations
from daily_liturgy.locales.pt_br.parse_cancaonova_color import parse_cancaonova_color
from daily_liturgy.locales.pt_br.parse_cancaonova_readings import parse_cancaonova_readings


def get_daily_liturgy_pt_br(date: datetime.date) -> DailyLiturgy:
    url = find_cancaonova_day_url(date)
    page = fetch_cancaonova_page(url)
    season, week = get_season_and_week(date)
    return DailyLiturgy(
        date=date,
        locale="pt-br",
        source_url=url,
        season=season,
        week=week,
        color=parse_cancaonova_color(page),
        celebrations=parse_cancaonova_celebrations(page),
        readings=parse_cancaonova_readings(page),
    )
