import re

from bs4 import Tag

from daily_liturgy.ibreviary.find_ibreviary_citation import find_ibreviary_citation
from daily_liturgy.ibreviary.split_ibreviary_alternatives import split_ibreviary_alternatives
from daily_liturgy.ibreviary.split_ibreviary_blocks import split_ibreviary_blocks
from daily_liturgy.models import Reading

# A heading may list every option ("Col 3:1-4 or I Cor 5:6b-8"); each has its own text.
_OR = {"la": "vel", "en": "or", "it": "oppure", "es": "o", "pt": "ou", "gl": "ou", "fr": "ou", "ro": "sau", "ar": "أو"}
_PSALM = re.compile(r"salm|psalm|psaume|مزمور", re.IGNORECASE)  # its "or" rubrics offer another refrain


def parse_ibreviary_readings(page_html: str, language: str) -> list[Reading]:
    """A block opening with `span.titolo` ("Lectio Prima", "First Reading", "Prima Lettura"…)
    starts a reading. A block without one (Latin) is an alternative to the previous reading."""
    readings: list[Reading] = []
    for block in split_ibreviary_blocks(page_html):
        title = block[0].select_one("span.titolo")
        if title is None and not readings:
            continue
        reading_type = _clean(title.get_text()) if title is not None else readings[-1].type
        if title is not None:
            title.decompose()
        texts = _texts(block, reading_type, language)
        if title is not None:
            readings.append(texts[0].model_copy(update={"alternatives": texts[1:]}))
        else:
            main = readings[-1]
            readings[-1] = main.model_copy(update={"alternatives": [*main.alternatives, *texts]})
    return readings


def _texts(block: list[Tag], reading_type: str, language: str) -> list[Reading]:
    """Main text first, then its alternatives. An alternative without a citation of its
    own takes its option from the main heading ("Jn 20:1-9 or Lk 24:1-12"), or one found
    in its text; one still without a citation isn't a reading and is dropped."""
    or_word = _OR.get(language, "or")
    segments = split_ibreviary_alternatives(block, language, split=not _PSALM.search(reading_type))
    options: list[str] = []
    texts = []
    for index, (label, citation, content) in enumerate(segments):
        if index == 0:
            citation = citation or find_ibreviary_citation(content[:300])
            options = re.split(rf"\s+{or_word}\s+", citation)
            citation = options[0]
        else:
            fallback = options[index] if index < len(options) else find_ibreviary_citation(f"{label}\n{content[:300]}")
            citation = citation or fallback
            if not citation or not content:
                continue
        content = _drop_repeated_first_line(content, citation, or_word)
        texts.append(Reading(type=reading_type, citation=citation.strip(), content=content))
    return texts


def _drop_repeated_first_line(content: str, citation: str, or_word: str) -> str:
    first, _, rest = content.partition("\n")
    stripped = first.strip().rstrip(".:").strip()
    if stripped.lower() == or_word or (citation and stripped == citation.strip().rstrip(".").strip()):
        return rest.strip()
    return content


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
