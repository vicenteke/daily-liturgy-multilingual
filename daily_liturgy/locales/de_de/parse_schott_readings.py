import re

from bs4 import BeautifulSoup, Tag

from daily_liturgy.locales.de_de.select_schott_headings import select_schott_headings
from daily_liturgy.models import Reading

# Headings are cased inconsistently ("ERSTE Lesung", "Erste Lesung"); these are the forms used.
_TYPES = {
    "erste lesung": "Erste Lesung",
    "zweite lesung": "Zweite Lesung",
    "antwortpsalm": "Antwortpsalm",
    "sequenz": "Sequenz",
    "ruf vor dem evangelium": "Ruf vor dem Evangelium",
    "evangelium": "Evangelium",
}
_READING = re.compile(r"lesung|psalm|sequenz|evangelium|halleluja", re.IGNORECASE)
_OR_LINE = re.compile(r"^Oder\b[^.]*:$")


def parse_schott_readings(page_html: str, weekday_year: int) -> list[Reading]:
    """Readings of the page's Mass (see `select_schott_headings` for which headings),
    with the citation in the heading's `span.lb_right` and the text in the following
    `p.lb_tx` paragraphs. A reading of the same type as the one before (announced by an
    "Oder:" line) is an alternative to it."""
    page = BeautifulSoup(page_html, "html.parser").select_one("#schott")
    if page is None:
        return []
    readings: list[Reading] = []
    for heading in select_schott_headings(page, weekday_year):
        reading = _to_reading(heading)
        if reading is None:
            continue
        if readings and readings[-1].type == reading.type:
            main = readings[-1]
            readings[-1] = main.model_copy(update={"alternatives": [*main.alternatives, reading]})
        else:
            readings.append(reading)
    return readings


def _to_reading(heading: Tag) -> Reading | None:
    label = BeautifulSoup(str(heading), "html.parser").h2  # a copy, to strip spans from
    citation_span = label.select_one("span.lb_right")
    citation = _clean(citation_span.get_text()) if citation_span else ""
    for span in label.select("span.lb_right, span.marg"):
        span.decompose()
    title = _clean(label.get_text())
    content = _content_after(heading)
    if not _READING.search(title) or not content:
        return None  # e.g. "Präfation von den Engeln", or a heading with no text of its own
    return Reading(type=_TYPES.get(title.lower(), title), citation=re.sub(r"^Vers:\s*", "", citation), content=content)


def _content_after(heading: Tag) -> str:
    """The `p.lb_tx` paragraphs up to the next heading, without "Oder:" lines
    (the introductions and rubrics are `p.s_rub`)."""
    paragraphs = []
    for sibling in heading.find_next_siblings():
        if sibling.name in ("h1", "h2", "h3", "h4"):
            break
        if sibling.name != "p" or "lb_tx" not in sibling.get("class", []):
            continue
        text = _paragraph_text(sibling)
        if text and not _OR_LINE.match(text):
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _paragraph_text(paragraph: Tag) -> str:
    paragraph = BeautifulSoup(str(paragraph), "html.parser").p
    for br in paragraph.find_all("br"):
        br.replace_with("\n")
    for span in paragraph.select("span.vers, span.lb_right"):
        span.decompose()  # verse numbers, and hymnal references ("GL 616") set to the right
    lines = [_clean(line) for line in paragraph.get_text().split("\n")]
    return "\n".join(line for line in lines if line)


def _clean(text: str) -> str:
    text = re.sub(r"[\x00-\x08\x0b-\x1f]", " ", text)  # stray control characters ("Paulus\x06an")
    return re.sub(r"\s+", " ", text.replace("\xa0", " ").replace("\u2217", "*")).strip()
