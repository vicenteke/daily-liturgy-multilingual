import datetime

from daily_liturgy.calendar.get_season_and_week import get_season_and_week
from daily_liturgy.locales.en_us.fetch_usccb_items import USCCB_SPANISH_FEED_URL, fetch_usccb_items
from daily_liturgy.locales.en_us.select_usccb_item import select_usccb_item
from daily_liturgy.locales.es_mx.parse_usccb_celebraciones import parse_usccb_celebraciones
from daily_liturgy.locales.es_mx.parse_usccb_lecturas import parse_usccb_lecturas
from daily_liturgy.models import DailyLiturgy


def get_daily_liturgy_es_mx(date: datetime.date) -> DailyLiturgy:
    """USCCB's Spanish readings (the Mexican lectionary text), from its Spanish feed.
    Like en-us, the color is always None: USCCB publishes none."""
    item = select_usccb_item(fetch_usccb_items(USCCB_SPANISH_FEED_URL), date)
    season, week = get_season_and_week(date)
    celebrations = parse_usccb_celebraciones(item["title"])
    return DailyLiturgy(
        date=date,
        locale="es-mx",
        source_url=item["link"],
        season=season,
        week=week,
        color=None,  # USCCB publishes no color
        celebrations=celebrations,
        readings=parse_usccb_lecturas(item["description"]),
    )
