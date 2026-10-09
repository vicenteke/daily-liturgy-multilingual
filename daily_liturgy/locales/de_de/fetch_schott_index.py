"""The calendar index behind Schott's own date widget: for a date, a JavaScript object
(not JSON) of about two weeks of days, each with `LESEJAHR_S` (Sunday cycle 1-3 = A-C),
`LESEJAHR_W` (weekday cycle 1-2), `NON_PROPRIUM` (the temporal day, with its page `url`)
and `PROPRIUM` (saints, with `TYPE_D` H/F/G/g = Hochfest/Fest/Gedenktag/nicht gebotener
Gedenktag, and their page `url`).
"""

import ast
import datetime
import re

import httpx

from daily_liturgy.exceptions import LiturgyNotAvailableError

_INDEX_URL = "https://liturgie-server.de/dyn/schott.json"


def fetch_schott_index(date: datetime.date) -> dict:
    days = _parse_index(_download(date))
    day = days.get(date.isoformat())
    if not isinstance(day, dict):
        raise LiturgyNotAvailableError(f"Schott's calendar has no entry for {date.isoformat()}.")
    return day


def _download(date: datetime.date) -> str:
    response = httpx.get(_INDEX_URL, params={"date": date.isoformat()}, timeout=45)
    response.raise_for_status()
    return response.text


def _parse_index(script: str) -> dict:
    """`window.Schott.loadedData( { '2026-10-01' : { LESEJAHR_S : 1, … url : '…' } } );`
    → a dict, by quoting the bare keys and reading it as a Python literal."""
    start = script.find("{", script.find("loadedData("))
    end = script.rfind("}", 0, script.rfind(")"))  # the object ends before "} );"
    if start < 0 or end < start:
        return {}
    literal = re.sub(r"(?m)^(\s*)([A-Za-z_]\w*)\s*:", r"\1'\2':", script[start:end + 1])
    literal = re.sub(r"\bnull\b", "None", literal)
    try:
        return ast.literal_eval(literal)
    except (ValueError, SyntaxError):
        return {}
