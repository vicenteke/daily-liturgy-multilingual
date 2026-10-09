import copy
import re

from bs4 import Tag

# Markers put around citation links and red rubrics, so they survive get_text().
_CIT, _END_CIT, _RUB, _END_RUB = "\x01", "\x02", "\x03", "\x04"
_LEFTOVER = re.compile(r"^[\s().,;:]*(cf\.)?[\s().,;:]*$", re.IGNORECASE)
# An unlinked citation closing a line, e.g. "… sue schiere, (Sal 102 (103),21)".
_TRAILING_CITATION = re.compile(r"\(((?:Cf\.\s*)?(?:[1-3]\s?)?[A-Z][a-z]+\s\d.*)\)$")


def split_cei_section(section: Tag) -> list[tuple[str, str]]:
    """Return (citation, content) for a reading section's text, then for each alternative.

    The citation is a BibbiaEdu link line under the "Dal libro…" line, and may be split
    over several links ("Dn 7,9-10" "." "13-14"). Without a link, it's an unlinked
    "(…)" closing a line (acclamations), or empty. An alternative starts at a red rubric
    line ("Oppure:", "Forma breve:", "Dove si celebra la Messa vespertina…") followed by
    its own citation; red lines not followed by a citation (a psalm's "Oppure:" between
    two refrains) stay in the text."""
    section = copy.copy(section)
    for tag in section.select("h2, h3, p.cci-liturgia-giorno-section-versetto, span.verses"):
        tag.decompose()
    for link in section.select('a[href*="bibbiaedu.it"]'):
        link.replace_with(_CIT + link.get_text() + _END_CIT)
    for span in section.select("span.bibbiaedu-linked"):
        span.unwrap()  # it sometimes wraps the text after the link too
    for span in section.select("span.cci-liturgia-giorno-testo-rosso"):
        span.replace_with(_RUB + span.get_text() + _END_RUB)
    for br in section.find_all("br"):
        br.replace_with("\n")
    for block in section.find_all(["p", "div"]):
        block.insert_before("\n")
        block.insert_after("\n")
    lines = [" ".join(line.replace("\xa0", " ").split()) for line in section.get_text().split("\n")]

    options: list[list[str]] = [[]]
    for i, line in enumerate(lines):
        if _is_rubric(line) and _citation_follows(lines[i + 1:]):
            options.append([])
        else:
            options[-1].append(line)
    return [_to_option(option) for option in options if any(option)]


def _is_rubric(line: str) -> bool:
    return line.startswith(_RUB) and line.endswith(_END_RUB) and line.count(_RUB) == 1


def _citation_follows(lines: list[str]) -> bool:
    for line in lines:
        if _is_rubric(line):
            return False
        if _CIT in line:
            return True
    return False


def _to_option(lines: list[str]) -> tuple[str, str]:
    citation = ""
    for i, line in enumerate(lines):
        if _CIT in line:
            start, end = line.index(_CIT), line.rindex(_END_CIT) + 1
            citation = re.sub(f"[{_CIT}{_END_CIT}]", "", line[start:end])
            before, after = line[:start], line[end:]
            if before.rstrip().lower().endswith("cf."):
                citation = f"Cf. {citation}"
            if _LEFTOVER.match(before + after):
                lines = lines[:i] + lines[i + 1:]
            break
    else:
        trailing = next((m for m in map(_TRAILING_CITATION.search, lines) if m), None)
        citation = trailing.group(1) if trailing else ""
    text = re.sub(f"[{_CIT}{_END_CIT}{_RUB}{_END_RUB}]", "", "\n".join(lines))
    return citation, re.sub(r"\n{3,}", "\n\n", text).strip()
