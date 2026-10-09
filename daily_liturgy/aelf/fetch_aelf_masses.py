"""AELF (Association Épiscopale Liturgique pour les pays Francophones) official API.

`https://api.aelf.org/v1/messes/{YYYY-MM-DD}/{zone}` returns JSON with the day's
`informations` (color, celebration, rank) and `messes` (one per Mass, with its readings).
Zones: france, belgique, luxembourg, suisse, canada, monaco, afrique, and romain (the
General Roman Calendar). Dates from about 2019 to the end of next year; others are 404.
"""

import datetime

import httpx

from daily_liturgy.exceptions import LiturgyNotAvailableError

AELF_MASSES_URL = "https://api.aelf.org/v1/messes/{date:%Y-%m-%d}/{zone}"


def fetch_aelf_masses(date: datetime.date, zone: str) -> dict:
    response = _download(AELF_MASSES_URL.format(date=date, zone=zone))
    if response.status_code == 404:
        raise LiturgyNotAvailableError(f"AELF has no Mass for {date.isoformat()} in zone {zone!r}.")
    response.raise_for_status()
    return response.json()


def _download(url: str) -> httpx.Response:
    return httpx.get(url, timeout=20, follow_redirects=True)
