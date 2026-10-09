import re

from bs4 import Tag

_MASS_HEADER = re.compile(r"^missa (da|do|de|das|dos)\b", re.IGNORECASE)
_MAIN_MASS = "missa do dia"
_FOOTER = "conferência nacional dos bispos do brasil"


def split_cancaonova_pane(pane: Tag) -> list[list[Tag]]:
    """Return the pane's texts as paragraph lists: the main text first, then its
    alternatives (separated by an "ou" paragraph).

    Days with several Masses (e.g. Christmas) put each Mass in the same pane under a
    "Missa da aurora" / "Missa do dia" line; only the Mass during the Day is kept,
    matching en-us, falling back to the first Mass."""
    paragraphs = [p for p in pane.find_all("p") if _text(p) and not _text(p).lower().startswith(_FOOTER)]
    masses = _split(paragraphs, lambda p: bool(_MASS_HEADER.match(_text(p))))
    if len(masses) > 1:
        chosen = next((body for header, body in masses if header and _text(header).lower() == _MAIN_MASS), None)
        paragraphs = chosen if chosen is not None else next(body for _, body in masses if body)
    return [body for _, body in _split(paragraphs, lambda p: _text(p).lower() == "ou") if body]


def _split(paragraphs: list[Tag], is_separator) -> list[tuple[Tag | None, list[Tag]]]:
    groups: list[tuple[Tag | None, list[Tag]]] = [(None, [])]
    for paragraph in paragraphs:
        if is_separator(paragraph):
            groups.append((paragraph, []))
        else:
            groups[-1][1].append(paragraph)
    return [group for group in groups if group[1]]


def _text(paragraph: Tag) -> str:
    return paragraph.get_text().replace("\xa0", " ").strip()
