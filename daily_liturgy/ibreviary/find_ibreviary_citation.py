import re

_ARABIC = re.compile(r"\([^()\n]*[٠-٩][^()\n]*\)")  # "(لو ١١: ٥-١٣)"
_LATIN_SCRIPT = re.compile(r"\b(?:[1-3]\s?)?[A-ZÀ-Ý][a-zà-ÿ]{0,5}\.?\s?\d+\s?[,:]\s?\d+[0-9a-z\-–.,;: ]*")  # "Dn 7,9-10.13-14", "1Cor 5,6b-8"


def find_ibreviary_citation(text: str) -> str:
    """First Bible reference in free text, for texts whose citation isn't marked up,
    e.g. Italian ("Dal libro del profeta Daniele\\nDn 7,9-10.13-14") or a rubric
    introducing an alternative ("Ou 1 Cor 5, 6b-8"). "" when there's none."""
    for pattern in (_LATIN_SCRIPT, _ARABIC):
        match = pattern.search(text)
        if match:
            return match.group(0).strip().rstrip(".,;:").strip()
    return ""
