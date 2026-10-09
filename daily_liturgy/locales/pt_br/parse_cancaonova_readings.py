import re

from bs4 import BeautifulSoup, Tag

from daily_liturgy.models import Reading
from daily_liturgy.locales.pt_br.split_cancaonova_pane import split_cancaonova_pane


def parse_cancaonova_readings(page_html: str) -> list[Reading]:
    """Each reading is a tab (`a#lit-N` → `div#liturgia-N`) labelled with its type,
    e.g. "1ª Leitura", "Salmo", "2ª Leitura", "Evangelho"."""
    soup = BeautifulSoup(page_html, "html.parser")
    readings = []
    for tab in soup.select('a[id^="lit-"][href^="#liturgia-"]'):
        pane = soup.select_one(tab["href"])
        if pane is None:
            continue
        reading_type = _clean(tab.find("label").get_text())
        fallback_citation = _clean(tab.select_one(".referencia").get_text())
        options = [_to_reading(reading_type, option, fallback_citation) for option in split_cancaonova_pane(pane)]
        if options:
            readings.append(options[0].model_copy(update={"alternatives": options[1:]}))
    return readings


def _to_reading(reading_type: str, paragraphs: list[Tag], fallback_citation: str) -> Reading:
    """The first paragraph of a text is a bold header holding the citation, e.g.
    "Primeira Leitura (Dn 7,9-10.13-14)" or "Responsório Sl 79(80),9.12 (R. Is 5,7a)"."""
    first = paragraphs[0]
    if first.find(["strong", "b"]) is not None:
        citation, body = _citation_from_header(_paragraph_text(first)), paragraphs[1:]
    else:
        citation, body = fallback_citation, paragraphs
    content = "\n\n".join(text for text in map(_paragraph_text, body) if text)
    return Reading(type=reading_type, citation=citation, content=content)


def _citation_from_header(header: str) -> str:
    """A header may list every option ("Segunda Leitura (Cl 3,1-4 ou 1Cor 5,6b-8)");
    each alternative has its own header, so only the first option is kept."""
    if header.lower().startswith("responsório"):
        citation = header[len("responsório"):]
    else:
        match = re.match(r"^[^()]*\((.+)\)\s*$", header)
        citation = match.group(1) if match else header
    return _clean(re.split(r"\s+ou\s+", citation, flags=re.IGNORECASE)[0])


def _paragraph_text(paragraph: Tag) -> str:
    for br in paragraph.find_all("br"):
        br.replace_with("\n")
    return "\n".join(line for line in map(_clean, paragraph.get_text().split("\n")) if line)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
