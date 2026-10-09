from bs4 import BeautifulSoup, Tag

_PAGE_TITLE_PREFIX = "liturgie del"


def split_cei_masses(page_html: str) -> list[tuple[str, Tag]]:
    """Return (title, container) for each Mass on the page, in order.

    A single Mass has its title (`h3.cci_content_single_title`) and sections directly in
    `#cci_content_single`. Days with several Masses (Christmas, All Souls, a weekday with
    an optional memorial) give each one a toggle title followed by a `div.collapse`.
    Some pages repeat the whole set, so repeated titles are skipped."""
    content = BeautifulSoup(page_html, "html.parser").select_one("#cci_content_single")
    if content is None:
        return []
    titles = [
        heading
        for heading in content.select("h3.cci_content_single_title")
        if not heading.get_text().strip().lower().startswith(_PAGE_TITLE_PREFIX)
    ]
    masses: list[tuple[str, Tag]] = []
    for heading in titles:
        title = " ".join(heading.get_text().split())
        container = heading.find_next_sibling("div", class_="collapse") if "cci-toggle-dropdown" in heading.get("class", []) else content
        if container is not None and title not in (seen for seen, _ in masses):
            masses.append((title, container))
    return masses
