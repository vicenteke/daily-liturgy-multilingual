import re

from bs4 import BeautifulSoup

from daily_liturgy.models import Celebration, Rank

_RANKS = {
    "memória facultativa": Rank.OPTIONAL_MEMORIAL,
    "memória": Rank.MEMORIAL,
    "festa": Rank.FEAST,
    "solenidade": Rank.SOLEMNITY,
}
_WEEKDAYS = {"domingo", "segunda-feira", "terça-feira", "quarta-feira", "quinta-feira", "sexta-feira", "sábado"}
_TEMPORAL = re.compile(
    r"^\d+[ºª°o]\s+(semana|domingo|dia)\b"  # "27ª Semana do Tempo Comum", "3º Domingo do Advento", "5º Dia na Oitava de Natal"
    r"|^(depois das cinzas|quarta-feira de cinzas|semana santa|sábado santo|paixão do senhor"
    r"|domingo de ramos|domingo na oitava|oitava d[ae] |tempo do natal)",
    re.IGNORECASE,
)
_RANK_SUFFIX = re.compile(r"^(.*?)\s*(?:,|\s-)\s*(" + "|".join(_RANKS) + r")$", re.IGNORECASE)


def parse_cancaonova_celebrations(page_html: str) -> list[Celebration]:
    """Parse the `h1.entry-title`, e.g. "Santos Miguel, Gabriel e Rafael, Arcanjos - Festa | Terça-feira",
    "São Barnabé, Apóstolo | Memória | Quinta-feira", "Santa Maria, Mãe de Deus, Solenidade | Quinta-feira"."""
    heading = BeautifulSoup(page_html, "html.parser").select_one("h1.entry-title")
    if heading is None:
        return []
    name, rank = None, None
    for part in (p.strip() for p in heading.get_text().split("|")):
        if not part or part.lower() in _WEEKDAYS:
            continue
        suffix = _RANK_SUFFIX.match(part)
        if suffix:
            part, rank = suffix.group(1), _RANKS[suffix.group(2).lower()]
        elif part.lower() in _RANKS:
            rank = _RANKS[part.lower()]
            continue
        name = name or part
    if name is None or (rank is None and _TEMPORAL.match(name)):
        return []
    return [Celebration(name=name, rank=rank)]
