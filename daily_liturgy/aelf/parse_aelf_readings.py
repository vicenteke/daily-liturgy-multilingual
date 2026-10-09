import re

from bs4 import BeautifulSoup

from daily_liturgy.models import Reading

# AELF gives each reading a key; these are the headings its site shows for them.
_TYPES = {
    "psaume": "Psaume",
    "cantique": "Cantique",
    "epitre": "Épître",
    "sequence": "Séquence",
    "evangile": "Évangile",
}
_ORDINALS = ["Première", "Deuxième", "Troisième", "Quatrième", "Cinquième", "Sixième", "Septième"]
_ACCLAMATION = "Acclamation"


def parse_aelf_readings(mass: dict) -> list[Reading]:
    """A Mass's `lectures`, in order. A reading with the same key as the one before
    (two `lecture_1`, two `evangile`) is an alternative to it. The Gospel acclamation
    (`verset_evangile`) comes with the Gospel and is returned as its own reading."""
    readings: list[Reading] = []
    previous_key = None
    for lecture in mass.get("lectures", []):
        key = lecture.get("type", "")
        reading = _to_reading(key, lecture)
        if key == previous_key and readings:
            main = readings[-1]
            readings[-1] = main.model_copy(update={"alternatives": [*main.alternatives, reading]})
            continue
        acclamation = _html_text(lecture.get("verset_evangile") or "")
        if acclamation:
            readings.append(Reading(type=_ACCLAMATION, citation=_clean(lecture.get("ref_verset") or ""), content=acclamation))
        readings.append(reading)
        previous_key = key
    return readings


def _to_reading(key: str, lecture: dict) -> Reading:
    """Content: the reading's announcement ("Lecture de la lettre de saint Paul…") or the
    psalm's refrain, then the text."""
    parts = [_clean(lecture.get("intro_lue") or ""), _html_text(lecture.get("refrain_psalmique") or ""), _html_text(lecture.get("contenu") or "")]
    return Reading(type=_type_name(key), citation=_clean(lecture.get("ref") or ""), content="\n\n".join(part for part in parts if part))


def _type_name(key: str) -> str:
    match = re.fullmatch(r"lecture_(\d+)", key)
    if match and 1 <= int(match.group(1)) <= len(_ORDINALS):
        return f"{_ORDINALS[int(match.group(1)) - 1]} lecture"
    return _TYPES.get(key, key)


def _html_text(html: str) -> str:
    soup = BeautifulSoup(html, "html.parser")
    for br in soup.find_all("br"):
        br.replace_with("\n")
    paragraphs = [p.get_text() for p in soup.find_all("p")] or [soup.get_text()]
    cleaned = ["\n".join(line for line in map(_clean, p.split("\n")) if line) for p in paragraphs]
    return "\n\n".join(p for p in cleaned if p)


def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.replace("\xa0", " ")).strip()
