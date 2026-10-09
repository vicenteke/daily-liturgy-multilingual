import re

from bs4 import BeautifulSoup, Tag

from daily_liturgy.models import Reading


def parse_usccb_readings(description_html: str) -> list[Reading]:
    """Parse a feed item's HTML: each `<h4>Type <a>Citation</a></h4>` is followed by
    a `<div class="poetry">` with the text. An "or" heading is an alternative to the
    previous reading."""
    soup = BeautifulSoup(description_html, "html.parser")
    readings: list[Reading] = []
    for heading in soup.find_all("h4"):
        link = heading.find("a")
        citation = _clean(link.get_text()) if link else ""
        if link:
            link.extract()
        reading_type = _clean(heading.get_text())
        body = heading.find_next_sibling(["div", "h4"])
        content = _block_text(body) if body is not None and body.name == "div" else ""

        if reading_type.lower() == "or" and readings:
            previous = readings[-1]
            previous.alternatives.append(Reading(type=previous.type, citation=citation, content=content))
        else:
            readings.append(Reading(type=reading_type, citation=citation, content=content))
    return readings


def _block_text(block: Tag) -> str:
    for br in block.find_all("br"):
        br.replace_with("\n")
    paragraphs = []
    for p in block.find_all("p") or [block]:
        lines = [_clean(line) for line in p.get_text().split("\n")]
        paragraph = "\n".join(line for line in lines if line)
        if paragraph:
            paragraphs.append(paragraph)
    return "\n\n".join(paragraphs)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
