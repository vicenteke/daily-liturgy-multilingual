import re
from urllib.parse import parse_qs, urlsplit

from bs4 import BeautifulSoup

_DAY_MASS = re.compile(r"^(Am Tag|Sonntag)\b")
_CYCLES = "ABC"


def select_schott_mass(page_html: str, sunday_year: int) -> str | None:
    """On days with several Masses, Schott's day page is an index of links
    (`…/schott_anz/index.html?file=weihnachtszeit%2Fweihnachten_tag.htm`): Christmas lists
    "Am Heiligen Abend", "In der Heiligen Nacht", "Am Morgen", "Am Tag"; Easter Sunday
    lists "Osternacht" and "Sonntag", each with A/B/C buttons. Return the path of the
    Mass during the Day (for `sunday_year` 1-3 = A-C), or None if the page is a Mass."""
    soup = BeautifulSoup(page_html, "html.parser")
    if soup.select_one("#schott h2.lb_u1") is not None:
        return None
    links = []
    for link in soup.select('a[href*="file="]'):
        group = link.find_parent("dl")
        label = group.find("dt") if group is not None else None
        group_label = " ".join(label.get_text().split()) if label is not None else ""
        files = parse_qs(urlsplit(link["href"]).query).get("file")
        if files:
            links.append((group_label, " ".join(link.get_text().split()), files[0]))
    day = [(text, path) for group, text, path in links if _DAY_MASS.match(text) or _DAY_MASS.match(group)]
    cycle = _CYCLES[sunday_year - 1] if 1 <= sunday_year <= 3 else None
    for text, path in day:
        if text == cycle:
            return path
    if day:
        return day[0][1]
    return links[-1][2] if links else None
