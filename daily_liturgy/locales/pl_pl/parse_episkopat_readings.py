import re

from bs4 import BeautifulSoup

from daily_liturgy.models import Reading

# "[lub do wyboru: Ap 12, 7-12a]", "[Lub: (podczas Mszy wieczornej w niedzielę): Łk 24, 13-35]"
_ALTERNATIVE = re.compile(r"\[\s*(?:lub|albo)\b[^\]]*?:\s*([^\]:]+?)\s*\]", re.IGNORECASE)


def parse_episkopat_readings(page_html: str) -> list[Reading]:
    """Each `.lit-right .subsec` is a reading: `<h2>` type ("Pierwsze czytanie", "Psalm
    responsoryjny", "Werset przed Ewangelią (Alleluja)", "Ewangelia"…), `.siglum` citation,
    then the text, where a bracketed "lub"/"albo" rubric starts an alternative."""
    soup = BeautifulSoup(page_html.replace("</br>", "\n"), "html.parser")
    readings = []
    for section in soup.select(".lit-right .subsec"):
        heading, siglum = section.find("h2"), section.select_one(".siglum")
        if heading is None or siglum is None:  # e.g. the "Homilie" links
            continue
        body = siglum.find_next_sibling("div")
        parts = _ALTERNATIVE.split(_text(body) if body is not None else "")
        reading_type = _clean(heading.get_text())
        alternatives = [
            Reading(type=reading_type, citation=_clean(citation), content=_tidy(content))
            for citation, content in zip(parts[1::2], parts[2::2])
        ]
        readings.append(Reading(type=reading_type, citation=_clean(siglum.get_text()), content=_tidy(parts[0]), alternatives=alternatives))
    return readings


def _text(element) -> str:
    for paragraph in element.find_all("p"):
        paragraph.insert_before("\n")
        paragraph.insert_after("\n")
    return element.get_text()


def _tidy(text: str) -> str:
    lines = [_clean(line) for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
