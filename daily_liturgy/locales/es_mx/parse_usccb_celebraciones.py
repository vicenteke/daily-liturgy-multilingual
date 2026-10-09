import re

from daily_liturgy.models import Celebration, Rank

_RANK_PREFIXES = [
    ("memoria libre de ", Rank.OPTIONAL_MEMORIAL),
    ("memoria opcional de ", Rank.OPTIONAL_MEMORIAL),
    ("memoria de ", Rank.MEMORIAL),
    ("fiesta de ", Rank.FEAST),
    ("solemnidad de ", Rank.SOLEMNITY),
]
_ARTICLE = re.compile(r"^(el|la|los|las)\s+", re.IGNORECASE)
_TEMPORAL = re.compile(
    r"^(lunes|martes|miércoles|jueves|viernes|sábado)\b"  # "Jueves de la XXVII semana…", "Viernes Santo"
    r"|^domingo\b(?! de pascua)"  # "Domingo de Ramos…", but not Easter Sunday
    r"|^[IVXL]+\s+(domingo|semana)\b"  # "XXVII Domingo ordinario", "I Domingo de Adviento"
    r"|^\d+ de (diciembre|enero)\b"  # late Advent and Christmas weekdays
    r"|^(vigilia pascual|feria|octava)\b",
    re.IGNORECASE,
)


def parse_usccb_celebraciones(title: str) -> list[Celebration]:
    """Celebration named by a Spanish USCCB item title, e.g. "Fiesta de los santos
    Arcángeles Miguel, Gabriel y Rafael". Weekday and Sunday titles have none; titles
    without a rank prefix get no rank."""
    lowered = title.lower()
    for prefix, rank in _RANK_PREFIXES:
        if lowered.startswith(prefix):
            name = _ARTICLE.sub("", title[len(prefix):])
            return [Celebration(name=name[:1].upper() + name[1:], rank=rank)]
    if _TEMPORAL.match(title):
        return []
    return [Celebration(name=title, rank=None)]
