"""CBCP (Catholic Bishops' Conference of the Philippines) daily readings, one WordPress
post per day at `cbcp.ph/readings/<month>-<day>-<year>/`. Days are published in batches
(in October 2026: June 8 to November 30, 2026); other dates are 404."""

import datetime

import httpx

from daily_liturgy.exceptions import LiturgyNotAvailableError


def fetch_cbcp_page(url: str, date: datetime.date) -> str:
    response = httpx.get(url, timeout=30, follow_redirects=True)
    if response.status_code == 404:
        raise LiturgyNotAvailableError(f"CBCP has not published the readings for {date.isoformat()}.")
    response.raise_for_status()
    return response.text
