import re

from bs4 import Tag

_YEAR = re.compile(r"^Jahr (I{1,2})( und II)?$")
_DATE = re.compile(r"^\d+\.\s")
_DAY_MASS = "am tag"
_ACCLAMATION = re.compile(r"^(Ruf vor dem Evangelium|Halleluja)", re.IGNORECASE)


def select_schott_headings(page: Tag, weekday_year: int) -> list[Tag]:
    """The reading headings of one Mass and one weekday cycle, in order.

    Readings are `h2.lb_u1`, and on weekday pages the acclamation is an `h2.s_u1`
    ("RUF VOR DEM EVANGELIUM"). `h4.lb_u_datum` lines mark:
    - weekday cycles, "Jahr I" / "Jahr II" / "Jahr I und II"; some pages omit "Jahr II",
      so a new "Erste Lesung" after a psalm in "Jahr I" starts Year II;
    - several Masses on one page ("Am Vorabend" / "Am Tag", All Souls' "I" / "II" / "III"):
      "Am Tag" is kept, else the first;
    - the date ("15. August"), ignored."""
    masses: list[tuple[str, list[Tag]]] = [("", [])]
    year, seen_psalm = None, False
    for heading in page.find_all(["h2", "h4"]):
        text = " ".join(heading.get_text().split())
        classes = heading.get("class", [])
        if heading.name == "h4" and "lb_u_datum" in classes:
            cycle = _YEAR.match(text)
            if cycle:
                year, seen_psalm = (None if cycle.group(2) else len(cycle.group(1))), False
            elif not _DATE.match(text):
                masses.append((text.lower(), []))
                year = None
            continue
        if heading.name != "h2" or not ("lb_u1" in classes or ("s_u1" in classes and _ACCLAMATION.match(text))):
            continue
        lowered = text.lower()
        if year == 1 and seen_psalm and lowered.startswith("erste lesung"):
            year = 2
        seen_psalm = seen_psalm or "psalm" in lowered
        if year is None or not weekday_year or year == weekday_year:
            masses[-1][1].append(heading)
    filled = [(label, headings) for label, headings in masses if headings]
    chosen = next((headings for label, headings in filled if label == _DAY_MASS), None)
    return chosen if chosen is not None else (filled[0][1] if filled else [])
