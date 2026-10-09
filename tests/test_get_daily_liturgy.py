import datetime

import pytest

from daily_liturgy import SUPPORTED_LOCALES, UnsupportedLocaleError, get_daily_liturgy


def test_unsupported_locale_raises():
    with pytest.raises(UnsupportedLocaleError, match="en-us"):
        get_daily_liturgy(datetime.date(2026, 10, 8), "xx-yy")


def test_supported_locales_are_plain_strings():
    assert all(isinstance(locale, str) for locale in SUPPORTED_LOCALES)
    assert {"de-de", "pl-pl", "en-ph", "en-us", "es-mx", "pt-br", "it-it", "la", "en", "es-es", "pt-pt", "fr-fr", "fr", "fr-be", "fr-lu", "fr-ch", "fr-mc", "fr-ca", "ro-ro", "gl-es", "ar"} <= set(SUPPORTED_LOCALES)


@pytest.mark.parametrize("locale", ["en-us", "EN-US", " en-US "])
def test_locale_is_case_insensitive(usccb_feed, locale):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), locale)
    assert liturgy.locale == "en-us"
    assert liturgy.source_url.endswith("/100826.cfm")


def test_locale_is_the_one_asked_for(ibreviary_site):
    assert get_daily_liturgy(datetime.date(2026, 10, 8), "ES-ES").locale == "es-es"
