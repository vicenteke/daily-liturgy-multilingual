import datetime
import re

from daily_liturgy.exceptions import LiturgyNotAvailableError


def select_usccb_item(items: list[dict], date: datetime.date) -> dict:
    """Pick the feed item for `date`, matched on the MMDDYY code in its link
    (`/bible/readings/100826.cfm`, or `/es/bible/lecturas/100826.cfm` in Spanish)."""
    code = date.strftime("%m%d%y")
    matches = [item for item in items if _link_date_code(item["link"]) == code]
    if not matches:
        raise LiturgyNotAvailableError(
            f"USCCB feed has no readings for {date.isoformat()}; it covers {_feed_range(items)}."
        )
    return _prefer_main_mass(matches)


def _link_date_code(link: str) -> str | None:
    match = re.search(r"/(?:readings|lecturas)/(\d{6})", link)
    return match.group(1) if match else None


def _prefer_main_mass(items: list[dict]) -> dict:
    """On days with several Masses (e.g. Christmas Vigil/Night/Dawn/Day), prefer the
    unsuffixed link (MMDDYY.cfm), assumed to be the Mass during the Day."""
    for item in items:
        if re.search(r"/(?:readings|lecturas)/\d{6}\.cfm$", item["link"]):
            return item
    return items[0]


def _feed_range(items: list[dict]) -> str:
    dates = sorted(
        datetime.datetime.strptime(code, "%m%d%y").date()
        for code in (_link_date_code(item["link"]) for item in items)
        if code
    )
    if not dates:
        return "no dates"
    return f"{dates[0].isoformat()} to {dates[-1].isoformat()}"
