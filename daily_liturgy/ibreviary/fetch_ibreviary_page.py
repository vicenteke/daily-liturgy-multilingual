"""iBreviary (ibreviary.com), approved by the user as the source for Latin and for the
languages without a usable official source.

Its mobile site keeps the chosen date and language in a PHP session, so a day's page is
read by posting the options form, then opening the readings page in the same session.
"""

import datetime
import re

import httpx

from daily_liturgy.exceptions import LiturgyNotAvailableError

IBREVIARY_READINGS_URL = "https://www.ibreviary.com/m2/letture.php?s=letture"
_OPTIONS_URL = "https://www.ibreviary.com/m2/opzioni.php"


def fetch_ibreviary_page(date: datetime.date, language: str) -> str:
    """`language` is iBreviary's code: "la", "it", "en", "es", "fr", "pt", "ro", "ar", "gl"."""
    options_html, page_html = _download(date, language)
    if not _shows_date(options_html, date):
        raise LiturgyNotAvailableError(f"iBreviary did not accept the date {date.isoformat()}.")
    if 'class="titolo"' not in page_html:
        raise LiturgyNotAvailableError(f"iBreviary has no Mass readings for {date.isoformat()}.")
    return page_html


def _download(date: datetime.date, language: str) -> tuple[str, str]:
    form = {"lang": language, "giorno": date.day, "mese": date.month, "anno": date.year, "ok": "ok"}
    with httpx.Client(timeout=60, follow_redirects=True) as client:
        options = client.post(_OPTIONS_URL, data=form)
        options.raise_for_status()
        page = client.get(IBREVIARY_READINGS_URL)
        page.raise_for_status()
    return options.text, page.text


def _shows_date(options_html: str, date: datetime.date) -> bool:
    """The options page echoes the session's date in its language, e.g. "Dies: Feria tertia,
    29 September 2026" or "يوم: يوم الخميس, 8 تشرين الأول - أكتوبر 2026"."""
    return re.search(rf"\b{date.day}\b[^<\d]*\b{date.year}\b", options_html) is not None
