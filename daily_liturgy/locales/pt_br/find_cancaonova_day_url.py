"""Canção Nova daily liturgy (liturgia.cancaonova.com), which publishes the CNBB
lectionary text. CNBB's own API (Edições CNBB) is restricted to licensed domains.

Each day is a WordPress post with an unpredictable slug, so the URL is looked up
in the site's month calendar widget (the same AJAX call its date picker makes).
"""

import datetime

import httpx
from bs4 import BeautifulSoup

from daily_liturgy.exceptions import LiturgyNotAvailableError

_CALENDAR_URL = "https://liturgia.cancaonova.com/wp-admin/admin-ajax.php"


def find_cancaonova_day_url(date: datetime.date) -> str:
    calendar_html = _download_calendar(date.month, date.year)
    wanted = f"sDia={date.day}&sMes={date.month}&sAno={date.year}"
    for link in BeautifulSoup(calendar_html, "html.parser").find_all("a", href=True):
        if link["href"].endswith(wanted):
            return link["href"]
    raise LiturgyNotAvailableError(f"Canção Nova has no liturgy published for {date.isoformat()}.")


def _download_calendar(month: int, year: int) -> str:
    data = {"action": "widget-ajax", "sMes": month, "sAno": year, "title": "", "type": "liturgia", "ajax": "true"}
    response = httpx.post(_CALENDAR_URL, data=data, timeout=20)
    response.raise_for_status()
    return response.text
