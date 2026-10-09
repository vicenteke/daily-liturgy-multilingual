"""Konferencja Episkopatu Polski (episkopat.pl): one page per day at
`/liturgia/YYYY-MM-DD`, available years back and ahead."""

import httpx


def fetch_episkopat_page(url: str) -> str:
    response = httpx.get(url, timeout=30, follow_redirects=True)
    response.raise_for_status()
    return response.text
