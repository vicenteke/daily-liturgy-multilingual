"""Schott (Erzabtei Beuron) Mass pages, approved by the user as the de-de source."""

import httpx

SCHOTT_URL = "https://schott.erzabtei-beuron.de"


def fetch_schott_page(path: str) -> str:
    """The page at `path` (e.g. "jk27/Donnerstag.htm"), relative to the site root."""
    response = httpx.get(f"{SCHOTT_URL}/{path.lstrip('/')}", timeout=45, follow_redirects=True)
    response.raise_for_status()
    return response.text
