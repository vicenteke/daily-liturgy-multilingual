import re

from daily_liturgy.models import Celebration, Rank

_FERIA = "de la férie"


def parse_aelf_celebrations(informations: dict) -> list[Celebration]:
    """Celebration from AELF's `informations`:
    - feasts and solemnities: `jour_liturgique_nom` is the name, `degre` the rank
      ("Fête", "Solennité", "Solennité du Seigneur", "Solennité de la Vierge Marie");
    - memorials: `jour_liturgique_nom` is "de la férie", `fete` the saint, `ligne3` the
      rank ("Mémoire", "Mémoire facultative");
    - weekdays and Sundays: `degre` empty and `fete` empty or "de la férie"."""
    day_name = _clean(informations.get("jour_liturgique_nom"))
    degree = _clean(informations.get("degre"))
    if degree and day_name and day_name.lower() != _FERIA:
        return [Celebration(name=_strip_note(day_name), rank=_rank(degree))]
    saint = _clean(informations.get("fete"))
    if saint and saint.lower() != _FERIA and _rank(saint) is None:
        return [Celebration(name=saint, rank=_rank(_clean(informations.get("ligne3"))))]
    return []


def _rank(text: str) -> Rank | None:
    lowered = text.lower()
    if lowered.startswith("solennité"):
        return Rank.SOLEMNITY
    if lowered.startswith("fête"):
        return Rank.FEAST
    if lowered.startswith("mémoire facultative"):
        return Rank.OPTIONAL_MEMORIAL
    if lowered.startswith("mémoire"):
        return Rank.MEMORIAL
    return None


def _strip_note(name: str) -> str:
    """Drop bracketed notes: "Résurrection du Seigneur [Psautier semaine propre]"."""
    return re.sub(r"\s*\[[^\]]*\]", "", name).strip()


def _clean(value) -> str:
    return re.sub(r"\s+", " ", str(value or "").replace("\xa0", " ")).strip()
