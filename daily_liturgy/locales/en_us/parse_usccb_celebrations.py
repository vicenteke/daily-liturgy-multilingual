import re

from daily_liturgy.models import Celebration, Rank

_RANK_PREFIXES = [
    ("optional memorial of ", Rank.OPTIONAL_MEMORIAL),
    ("memorial of ", Rank.MEMORIAL),
    ("feast of ", Rank.FEAST),
    ("solemnity of ", Rank.SOLEMNITY),
]
_WEEKDAY = r"(monday|tuesday|wednesday|thursday|friday|saturday|sunday)"
_TEMPORAL = re.compile(
    rf"^{_WEEKDAY}\b"  # "Thursday of the Twenty-seventh Week…", "Friday of the Passion of the Lord"
    r"|^[\w-]+ sunday (of|in|after)\b"  # "Twenty-seventh Sunday in Ordinary Time", "First Sunday of Advent"
    r"|^(ash wednesday|palm sunday|holy thursday|good friday|holy saturday|easter vigil)"
    r"|^(december|january) \d+"  # late Advent and Christmas weekdays
    r"|^[\w-]+ day (in|within) the octave"
    r"|^(christmas|advent|lenten|easter) weekday",
    re.IGNORECASE,
)


def parse_usccb_celebrations(title: str) -> list[Celebration]:
    """Celebration named by a USCCB item title. Weekday and Sunday titles have none;
    titles without a rank prefix, e.g. "The Nativity of the Lord (Christmas)", get no rank."""
    lowered = title.lower()
    for prefix, rank in _RANK_PREFIXES:
        if lowered.startswith(prefix):
            return [Celebration(name=_strip_article(title[len(prefix):]), rank=rank)]
    if _TEMPORAL.match(title):
        return []
    return [Celebration(name=title, rank=None)]


def _strip_article(name: str) -> str:
    return name[4:] if name.lower().startswith("the ") else name
