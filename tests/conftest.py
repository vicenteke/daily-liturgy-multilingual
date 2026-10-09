import importlib
from pathlib import Path

import pytest

FIXTURES = Path(__file__).parent / "fixtures"
USCCB_FEEDS = {"readings.rss": "usccb_readings.rss", "lecturas.rss": "usccb_lecturas.rss"}


@pytest.fixture
def usccb_feed(monkeypatch):
    """Serve the saved USCCB feeds, English and Spanish (both 2026-09-29 .. 2026-10-08),
    instead of the network."""

    def download_feed(feed_url):
        return (FIXTURES / USCCB_FEEDS[feed_url.rsplit("/", 1)[-1]]).read_text(encoding="utf-8")

    module = importlib.import_module("daily_liturgy.locales.en_us.fetch_usccb_items")
    monkeypatch.setattr(module, "_download_feed", download_feed)


CANCAONOVA = Path(__file__).parent / "fixtures" / "cancaonova"


@pytest.fixture
def cancaonova_site(monkeypatch):
    """Serve saved Canção Nova calendars (Apr 2025; Sep, Oct, Dec 2026) and day pages
    (2025-04-20, 2026-09-29, 10-04, 10-08, 12-25) instead of the network."""

    def download_calendar(month, year):
        return (CANCAONOVA / f"calendar_{year}_{month:02d}.html").read_text(encoding="utf-8")

    def fetch_page(url):
        query = dict(part.split("=") for part in url.split("?", 1)[1].split("&"))
        name = f"{query['sAno']}_{int(query['sMes']):02d}_{int(query['sDia']):02d}.html"
        return (CANCAONOVA / name).read_text(encoding="utf-8")

    find_module = importlib.import_module("daily_liturgy.locales.pt_br.find_cancaonova_day_url")
    main_module = importlib.import_module("daily_liturgy.locales.pt_br.get_daily_liturgy_pt_br")
    monkeypatch.setattr(find_module, "_download_calendar", download_calendar)
    monkeypatch.setattr(main_module, "fetch_cancaonova_page", fetch_page)


IBREVIARY = Path(__file__).parent / "fixtures" / "ibreviary"


@pytest.fixture
def ibreviary_site(monkeypatch):
    """Serve saved iBreviary readings pages, `fixtures/ibreviary/<language>/YYYY_MM_DD.html`,
    instead of the network, with an options page echoing the requested date."""

    def download(date, language):
        options = f"<p>Dies: Feria, {date.day} Mensis {date.year}</p>"
        return options, (IBREVIARY / language / f"{date:%Y_%m_%d}.html").read_text(encoding="utf-8")

    module = importlib.import_module("daily_liturgy.ibreviary.fetch_ibreviary_page")
    monkeypatch.setattr(module, "_download", download)


CEI = FIXTURES / "cei"


@pytest.fixture
def cei_site(monkeypatch):
    """Serve trimmed CEI day pages (2025-04-20; 2026-04-02, 09-29, 10-04, 10-06, 10-08,
    12-25) instead of the network."""
    module = importlib.import_module("daily_liturgy.locales.it_it.get_daily_liturgy_it_it")
    monkeypatch.setattr(module, "fetch_cei_page", lambda date: (CEI / f"{date:%Y_%m_%d}.html").read_text(encoding="utf-8"))


CBCP = Path(__file__).parent / "fixtures" / "cbcp"


@pytest.fixture
def cbcp_site(monkeypatch):
    """Serve saved CBCP pages (2026-09-29, 10-04, 10-07, 10-08, 11-01) by their URL slug
    instead of the network. Other dates raise like CBCP's 404."""
    from daily_liturgy.exceptions import LiturgyNotAvailableError

    def fetch_page(url, date):
        path = CBCP / f"{url.rstrip('/').rsplit('/', 1)[-1]}.html"
        if not path.exists():
            raise LiturgyNotAvailableError(f"CBCP has not published the readings for {date.isoformat()}.")
        return path.read_text(encoding="utf-8")

    module = importlib.import_module("daily_liturgy.locales.en_ph.get_daily_liturgy_en_ph")
    monkeypatch.setattr(module, "fetch_cbcp_page", fetch_page)


AELF = FIXTURES / "aelf"


@pytest.fixture
def aelf_api(monkeypatch):
    """Serve saved AELF responses (tests/fixtures/aelf/YYYY-MM-DD_zone.json); other
    date/zone pairs are a 404, like the real API."""
    import httpx

    def download(url):
        date, zone = url.rstrip("/").split("/")[-2:]
        path = AELF / f"{date}_{zone}.json"
        request = httpx.Request("GET", url)
        if not path.exists():
            return httpx.Response(404, request=request)
        return httpx.Response(200, content=path.read_bytes(), request=request)

    module = importlib.import_module("daily_liturgy.aelf.fetch_aelf_masses")
    monkeypatch.setattr(module, "_download", download)


EPISKOPAT = Path(__file__).parent / "fixtures" / "episkopat"


@pytest.fixture
def episkopat_site(monkeypatch):
    """Serve saved episkopat.pl pages (2025-04-20, 2026-09-29, 10-04, 10-07, 10-08, 10-12,
    11-01, 12-25), named by date, instead of the network."""

    def fetch_page(url):
        return (EPISKOPAT / f"{url.rsplit('/', 1)[-1]}.html").read_text(encoding="utf-8")

    module = importlib.import_module("daily_liturgy.locales.pl_pl.get_daily_liturgy_pl_pl")
    monkeypatch.setattr(module, "fetch_episkopat_page", fetch_page)


SCHOTT = FIXTURES / "schott"


@pytest.fixture
def schott_site(monkeypatch):
    """Serve saved Schott data instead of the network: calendar index scripts
    (`index/YYYY-MM-DD.js`), the `/?datum=` redirects (`redirects.json`) and trimmed pages
    (`pages/<path with / as __>`), for 2025-04-20 and 2026-08-15, 09-29, 10-06, 10-08, 12-25."""
    import json

    redirects = json.loads((SCHOTT / "redirects.json").read_text(encoding="utf-8"))
    index = importlib.import_module("daily_liturgy.locales.de_de.fetch_schott_index")
    path = importlib.import_module("daily_liturgy.locales.de_de.find_schott_path")
    main = importlib.import_module("daily_liturgy.locales.de_de.get_daily_liturgy_de_de")
    monkeypatch.setattr(index, "_download", lambda date: (SCHOTT / "index" / f"{date.isoformat()}.js").read_text(encoding="utf-8"))
    monkeypatch.setattr(path, "_redirect_location", lambda date: redirects.get(date.isoformat()))
    monkeypatch.setattr(main, "fetch_schott_page", lambda page: (SCHOTT / "pages" / page.replace("/", "__")).read_text(encoding="utf-8"))
