"""`/?datum=YYYY-MM-DD` redirects to the day's page as Schott resolves it (precedence
between Sundays, saints and seasons), e.g. `/jk27/Donnerstag.htm?datum=…`. Without a
redirect (dates Schott doesn't cover), the date isn't available."""

import datetime
from urllib.parse import urlsplit

import httpx

from daily_liturgy.exceptions import LiturgyNotAvailableError
from daily_liturgy.locales.de_de.fetch_schott_page import SCHOTT_URL


def find_schott_path(date: datetime.date) -> str:
    location = _redirect_location(date)
    if not location:
        raise LiturgyNotAvailableError(f"Schott has no Mass for {date.isoformat()}.")
    return urlsplit(location).path.lstrip("/")


def _redirect_location(date: datetime.date) -> str | None:
    response = httpx.get(f"{SCHOTT_URL}/", params={"datum": date.isoformat()}, timeout=45)
    return response.headers.get("location") if response.is_redirect else None
