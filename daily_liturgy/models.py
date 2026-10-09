import datetime
from enum import Enum

from pydantic import BaseModel


class Color(str, Enum):
    GREEN = "green"
    VIOLET = "violet"
    WHITE = "white"
    RED = "red"
    ROSE = "rose"
    BLACK = "black"


class Season(str, Enum):
    ADVENT = "advent"
    CHRISTMAS = "christmas"
    LENT = "lent"
    EASTER_TRIDUUM = "easter_triduum"
    EASTER = "easter"
    ORDINARY_TIME = "ordinary_time"


class Rank(str, Enum):
    SOLEMNITY = "solemnity"
    FEAST = "feast"
    MEMORIAL = "memorial"
    OPTIONAL_MEMORIAL = "optional_memorial"


class Celebration(BaseModel):
    name: str  # as published, without the rank, e.g. "Saint Jerome, Priest and Doctor of the Church"
    rank: Rank | None  # None when the source names the day without a rank, e.g. "Páscoa do Senhor"


class Reading(BaseModel):
    type: str  # as published by the source, e.g. "Reading 1", "Responsorial Psalm", "Alleluia", "Gospel"
    citation: str
    content: str
    alternatives: list["Reading"] = []  # texts that may be read instead of this one


class DailyLiturgy(BaseModel):
    date: datetime.date
    locale: str
    source_url: str
    season: Season
    week: int | None  # week of the season; see CLAUDE.md for the conventions
    color: Color | None  # None when it couldn't be determined
    celebrations: list[Celebration]  # empty on plain weekdays and Sundays
    readings: list[Reading]
