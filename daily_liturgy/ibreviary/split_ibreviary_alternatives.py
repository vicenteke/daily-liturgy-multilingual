import re

from bs4 import NavigableString, Tag

# Rubrics that introduce a text read instead of the previous one. Latin puts each
# alternative in its own block instead, so it has no inline marker.
_MARKERS = {
    "en": re.compile(r"^Or\b[^:]*:$"),  # "Or:", "Or, at an afternoon or evening Mass:"; not the psalm's "or:℟."
    "it": re.compile(r"^Oppure:?$", re.IGNORECASE),
    "es": re.compile(r"\(opción \d+\)|^O bien:?$", re.IGNORECASE),
    "pt": re.compile(r"^(Ou\b|Em vez da leitura precedente|Em vez deste Evangelho|Nas Missas Vespertinas)"),
    "gl": re.compile(r"^Ou\b"),
    "fr": re.compile(r"^Ou bien\b"),
    "ro": re.compile(r"^Sau\b"),
    "ar": re.compile(r"^أو\b"),
}
_MARK, _MARK_END, _CITE, _CITE_END = "\x00", "\x01", "\x02", "\x03"


def split_ibreviary_alternatives(block: list[Tag], language: str, split: bool) -> list[tuple[str, str, str]]:
    """Return `(label, citation, text)` for the block's main text, then for each
    alternative. `citation` is the first `span.citazione` inside that text (whatever
    precedes it, such as a "Vel" label, is dropped), or "" when there's none."""
    marker = _MARKERS.get(language) if split else None
    for element in block:
        if marker is not None:
            for rubric in [element, *element.select(".rubrica")]:
                label = _clean(rubric.get_text())
                if "rubrica" in (rubric.get("class") or []) and marker.search(label):
                    rubric.clear()
                    rubric.append(NavigableString(f"{_MARK}{label}{_MARK_END}"))
        for span in element.select("span.citazione"):
            span.replace_with(NavigableString(f"{_CITE}{_clean(span.get_text())}{_CITE_END}"))
    text = "\n\n".join(filter(None, map(_element_text, block)))
    head, *rest = text.split(_MARK)
    segments = [("", head)] + [tuple(part.split(_MARK_END, 1)) for part in rest]
    if not _without_citations(segments[0][1]).strip() and len(segments) > 1:
        segments = [("", head + segments[1][1]), *segments[2:]]
    return [(label, *_take_citation(body)) for label, body in segments]


def _take_citation(body: str) -> tuple[str, str]:
    """Back-to-back citations (a heading listing every option, then this text's own) count
    as one header: the last one is kept. A `citazione` without digits isn't a reference
    (the source sometimes marks an antiphon that way) and stays in the text."""
    match = re.search(f"(?:{_CITE}(.*?){_CITE_END}\\s*)+", body)
    citations = re.findall(f"{_CITE}(.*?){_CITE_END}", match.group(0)) if match else []
    references = [c for c in citations if re.search(r"[0-9\u0660-\u0669]", c)]
    if not references:
        return "", _tidy(_unwrap(body))
    return references[-1], _tidy(_unwrap(body[match.end():]))


def _unwrap(text: str) -> str:
    return re.sub(f"{_CITE}(.*?){_CITE_END}", r"\1", text)


def _without_citations(text: str) -> str:
    return re.sub(f"{_CITE}.*?{_CITE_END}", "", text)


def _element_text(element: Tag) -> str:
    for br in element.find_all("br"):
        br.replace_with("\n")
    for nested in element.find_all(["div", "p"]):
        nested.insert_before("\n")
        nested.insert_after("\n")
    return _tidy(element.get_text())


def _tidy(text: str) -> str:
    lines = [_clean(line) for line in text.split("\n")]
    return re.sub(r"\n{3,}", "\n\n", "\n".join(lines)).strip()


def _clean(text: str) -> str:
    return re.sub(r"[ \t\r\f\v\xa0]+", " ", text).strip()
