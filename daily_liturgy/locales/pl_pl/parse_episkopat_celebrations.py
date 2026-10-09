import re

from bs4 import BeautifulSoup

from daily_liturgy.models import Celebration, Rank

_RANKS = [
    ("uroczystość ", Rank.SOLEMNITY),
    ("święto ", Rank.FEAST),
    ("wspomnienie dowolne ", Rank.OPTIONAL_MEMORIAL),
    ("wspomnienie obowiązkowe ", Rank.MEMORIAL),
    ("wspomnienie ", Rank.MEMORIAL),
]
_OPTIONAL = re.compile(r"^dzień powszedni albo wspomnienie (?:dowolne )?", re.IGNORECASE)
_ALL_SOULS = "wszystkich wiernych zmarłych"  # "Wspomnienie" here is a commemoration, not a memorial


def parse_episkopat_celebrations(page_html: str) -> list[Celebration]:
    """Parse `.period_name`. Only titles naming a rank are celebrations: "Uroczystość …",
    "Święto …", "Wspomnienie …", and "Dzień powszedni albo wspomnienie X albo wspomnienie Y"
    (optional memorials). Titles without one ("XXVII Tydzień zwykły", but also "Zesłanie
    Ducha Świętego", "Chrystusa Króla") give [], since their rank isn't published."""
    element = BeautifulSoup(page_html, "html.parser").select_one(".period_name")
    title = re.sub(r"\s+", " ", element.get_text()).strip() if element is not None else ""
    optional = _OPTIONAL.match(title)
    if optional:
        names = re.split(r"\s+albo wspomnienie (?:dowolne )?", title[optional.end():], flags=re.IGNORECASE)
        return [Celebration(name=name.strip(), rank=Rank.OPTIONAL_MEMORIAL) for name in names if name.strip()]
    for prefix, rank in _RANKS:
        if title.lower().startswith(prefix):
            name = title[len(prefix):].strip()
            return [Celebration(name=name, rank=None if name.lower() == _ALL_SOULS else rank)]
    return []
