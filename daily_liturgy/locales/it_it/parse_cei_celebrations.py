import re

from daily_liturgy.models import Celebration, Rank

_RANKS = {
    "memoria facoltativa": Rank.OPTIONAL_MEMORIAL,
    "memoria": Rank.MEMORIAL,
    "festa": Rank.FEAST,
    "solennità": Rank.SOLEMNITY,
}
_DASH_SUFFIX = re.compile(r"^(.*?)\s+[–-]\s+([^–-]+)$")
_PARENTHESIS = re.compile(r"\s*\((messa|anno)\b[^)]*\)", re.IGNORECASE)
_TEMPORAL = re.compile(
    r"^(lunedì|martedì|mercoledì|giovedì|venerdì|sabato)\b"  # "Giovedì della XXVII settimana…", "Venerdì santo"
    r"|^domenica\b(?! di pasqua)"  # "Domenica delle Palme…", but not Easter Sunday
    r"|^[ivxl]+ domenica\b"  # "XXVII Domenica del Tempo Ordinario", "I Domenica di Avvento"
    r"|^\d+ dicembre\b|^feria\b",
    re.IGNORECASE,
)


def parse_cei_celebrations(titles: list[str]) -> list[Celebration]:
    """Celebrations named by the page's Mass titles, e.g. "SANTI MICHELE, GABRIELE E
    RAFFAELE, ARCANGELI – FESTA", "NATALE DEL SIGNORE (MESSA DEL GIORNO) - SOLENNITÀ".
    Names are kept as published (upper case). Weekday and Sunday titles have none."""
    celebrations: list[Celebration] = []
    for title in titles:
        celebration = _parse_title(title)
        if celebration is not None and celebration not in celebrations:
            celebrations.append(celebration)
    return celebrations


def _parse_title(title: str) -> Celebration | None:
    name, rank = _PARENTHESIS.sub("", title).strip(), None
    while (suffix := _DASH_SUFFIX.match(name)) is not None:
        word = suffix.group(2).strip().lower()
        if word in _RANKS:
            rank = _RANKS[word]
        elif not (word.startswith("anno ") or word.startswith("messa ")):
            break  # a dash that belongs to the name
        name = suffix.group(1).strip()
    if rank is None and _TEMPORAL.match(name):
        return None
    return Celebration(name=name, rank=rank)
