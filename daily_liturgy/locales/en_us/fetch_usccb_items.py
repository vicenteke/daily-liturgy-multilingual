"""USCCB (United States Conference of Catholic Bishops) daily readings feeds,
in English and in Spanish (also used by es-mx).

Only the official RSS feeds are used: the per-day HTML pages are behind a bot
challenge. A feed covers roughly the last 10 days and no future dates.
"""

import xml.etree.ElementTree as ET

import httpx

USCCB_FEED_URL = "https://bible.usccb.org/readings.rss"
USCCB_SPANISH_FEED_URL = "https://bible.usccb.org/lecturas.rss"


def fetch_usccb_items(feed_url: str = USCCB_FEED_URL) -> list[dict]:
    """Return one {"title", "link", "description"} dict per feed item, newest first."""
    return _parse_feed(_download_feed(feed_url))


def _download_feed(feed_url: str) -> str:
    response = httpx.get(feed_url, timeout=20, follow_redirects=True)
    response.raise_for_status()
    return response.text


def _parse_feed(xml: str) -> list[dict]:
    channel = ET.fromstring(xml).find("channel")
    if channel is None:
        return []
    return [
        {
            "title": " ".join(item.findtext("title", "").split()),
            "link": item.findtext("link", "").strip(),
            "description": item.findtext("description", ""),
        }
        for item in channel.findall("item")
    ]
