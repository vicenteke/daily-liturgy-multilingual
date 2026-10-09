import re

from bs4 import BeautifulSoup, Tag

from daily_liturgy.models import Reading


def parse_cbcp_readings(page_html: str) -> list[Reading]:
    """Each reading is an `<h3>Type<br><span>Citation</span></h3>` followed by `<p>`s. An
    `<h3>` with only a citation (after a `<p>or</p>`) is an alternative to the previous one."""
    soup = BeautifulSoup(page_html, "html.parser")
    heading = next((h for h in soup.select(".et_pb_text_inner h3") if h.find("span")), None)
    if heading is None:
        return []
    readings: list[Reading] = []
    for heading in heading.parent.find_all("h3", recursive=False):
        citation = _clean("".join(span.get_text() for span in heading.find_all("span")))
        for span in heading.find_all("span"):
            span.decompose()
        reading_type = _clean(heading.get_text())
        content = _content_after(heading)
        if reading_type or not readings:
            readings.append(Reading(type=reading_type, citation=citation, content=content))
        else:
            main = readings[-1]
            alternative = Reading(type=main.type, citation=citation, content=content)
            readings[-1] = main.model_copy(update={"alternatives": [*main.alternatives, alternative]})
    return readings


def _content_after(heading: Tag) -> str:
    paragraphs = []
    for sibling in heading.find_next_siblings():
        if sibling.name == "h3":
            break
        if sibling.name != "p":
            continue
        for br in sibling.find_all("br"):
            br.replace_with("\n")
        text = "\n".join(line for line in map(_clean, sibling.get_text().split("\n")) if line)
        if text and text.lower() != "or":
            paragraphs.append(text)
    return "\n\n".join(paragraphs)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
