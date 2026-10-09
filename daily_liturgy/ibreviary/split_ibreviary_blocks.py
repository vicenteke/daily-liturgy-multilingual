from bs4 import BeautifulSoup, Tag


def split_ibreviary_blocks(page_html: str) -> list[list[Tag]]:
    """Return the readings as element lists, one per `<hr>`-separated block.

    The page is divided by `span.sezione` headings whose labels are translated: a page
    heading ("Letture", "Readings"…), and on saints' days a proper section ("Letture
    proprie", "Proper readings"…), a weekday section ("Letture feriali"…), and sometimes
    the prayer of the faithful. The first section holding readings wins, so the proper
    readings are kept: they're required on feasts and allowed on memorials."""
    inner = BeautifulSoup(page_html, "html.parser").select_one("#contenuto .inner")
    if inner is None:
        return []
    sections: list[list[list[Tag]]] = [[[]]]
    for element in inner.find_all(["p", "div", "hr"], recursive=False):
        if element.select_one("span.sezione") is not None:
            sections.append([[]])
        elif element.name == "hr":
            sections[-1].append([])
        elif element.select_one('a[href="#menu"]') is None:
            sections[-1][-1].append(element)
    for blocks in sections:
        if any(element.select_one("span.titolo") for block in blocks for element in block):
            return [block for block in blocks if block]
    return []
