import re

_KINDS = [
    "Aclamación antes del Evangelio",
    "Salmo Responsorial",
    "Primera lectura",
    "Segunda lectura",
    "Tercera lectura",
    "Cuarta lectura",
    "Quinta lectura",
    "Sexta lectura",
    "Séptima lectura",
    "Secuencia",
    "Epístola",
    "Evangelio",
    "O bien",
]
_KIND = re.compile(rf"^({'|'.join(map(re.escape, _KINDS))})\b:?\s*(.*)$", re.IGNORECASE)
# What follows a known kind is a citation if it's capitalized and has a verse number, so
# "Evangelio de la procesión …" isn't taken as "Evangelio" + citation.
_KIND_CITATION = re.compile(r"(?:[1-3]\s+)?[A-ZÁÉÍÓÚÑ]\D*\d.*")
# Fallback: the citation starts at the book name before the first verse number, with an
# optional "Cfr"/"Del" prefix and book number, e.g. "Cfr 1 Corintios 5, 7".
_CITATION = re.compile(r"\s((?:(?:Cfr?\.?|Del)\s+)?(?:[1-3]\s+)?[A-ZÁÉÍÓÚÑ][^\s\d]*\s+\d.*)$")


def split_usccb_heading(heading: str) -> tuple[str, str]:
    """Split a Spanish feed heading, which has no link around the citation, into
    (kind, citation): "Primera lectura Gálatas 3, 1-5" → ("Primera lectura", "Gálatas 3, 1-5"),
    "O bien: Apocalipsis 12, 7-12" → ("O bien", "Apocalipsis 12, 7-12")."""
    heading = " ".join(heading.split())
    known = _KIND.match(heading)
    if known and (not known.group(2) or _KIND_CITATION.fullmatch(known.group(2))):
        return known.group(1), known.group(2)
    fallback = _CITATION.search(heading)
    if fallback:
        return heading[: fallback.start()].strip(), fallback.group(1)
    return heading, ""
