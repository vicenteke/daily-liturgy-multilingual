"""CEI (Conferenza Episcopale Italiana) "Messa del Giorno" pages on chiesacattolica.it.

One page per day at a predictable URL. It covers roughly the current and previous
liturgical years (2024 to end of 2026 as of October 2026); other dates are 404.
"""

import datetime

import httpx

from daily_liturgy.exceptions import LiturgyNotAvailableError

CEI_DAY_URL = "https://www.chiesacattolica.it/liturgia-del-giorno/liturgie-del-{:%Y%m%d}/"


def fetch_cei_page(date: datetime.date) -> str:
    response = httpx.get(CEI_DAY_URL.format(date), timeout=30, follow_redirects=True)
    if response.status_code == 404:
        raise LiturgyNotAvailableError(f"CEI has no liturgy published for {date.isoformat()}.")
    response.raise_for_status()
    return response.text
