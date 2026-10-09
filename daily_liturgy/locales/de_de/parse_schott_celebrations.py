import re

from bs4 import BeautifulSoup

from daily_liturgy.models import Celebration, Rank

_RANKS = {"H": Rank.SOLEMNITY, "F": Rank.FEAST, "G": Rank.MEMORIAL, "g": Rank.OPTIONAL_MEMORIAL}
_TEMPORAL_RANK = re.compile(r"\b(Hochfest|Fest)\b")
_DATE = re.compile(r"^\d+\.\s")


def parse_schott_celebrations(day: dict, path: str, page_html: str | None = None) -> list[Celebration]:
    """The celebration of the page Schott resolved the date to (`path`), from the index:
    - a saint (`PROPRIUM`) with that `url`: the `TYPE_D` rank, and as the name the saint
      page's title when it's given as `page_html` ("Mariä Aufnahme in den Himmel", where
      the index only says "Maria"), else the entries' names joined (one page may hold
      several entries: Michael, Gabriel, Rafael);
    - otherwise the temporal day (`NON_PROPRIUM`): a celebration only when its name says
      it's a "Hochfest" or "Fest" ("Weihnachten - Hochfest der Geburt des Herrn")."""
    saints = [entry for entry in day.get("PROPRIUM") or [] if entry.get("url") == path]
    if saints:
        name = _page_title(page_html) if page_html else ""
        name = name or _join([_clean(entry.get("NAME_DE")) for entry in saints])
        return [Celebration(name=name, rank=_RANKS.get(saints[0].get("TYPE_D")))]
    for entry in day.get("NON_PROPRIUM") or []:
        name = _clean(entry.get("NAME_DE"))
        match = _TEMPORAL_RANK.search(name)
        if entry.get("url") == path and match:
            return [Celebration(name=name, rank=Rank.SOLEMNITY if match.group(1) == "Hochfest" else Rank.FEAST)]
    return []


def _page_title(page_html: str) -> str:
    """The first `h1.lb_u_tag` that isn't the date, up to its line break
    ("Hl. Michael, Hl. Gabriel und Hl. Rafael<br>Erzengel")."""
    for heading in BeautifulSoup(page_html, "html.parser").select("#schott h1.lb_u_tag"):
        for br in heading.find_all("br"):
            br.replace_with("\n")
        title = _clean(heading.get_text().split("\n")[0])
        if title and not _DATE.match(title):
            return title
    return ""


def _join(names: list[str]) -> str:
    unique = list(dict.fromkeys(name for name in names if name))
    return unique[0] if len(unique) == 1 else ", ".join(unique[:-1]) + " und " + unique[-1]


def _clean(value) -> str:
    return " ".join(str(value or "").split())
