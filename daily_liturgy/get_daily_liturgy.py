import datetime
from collections.abc import Callable
from functools import partial

from daily_liturgy.aelf import get_aelf_liturgy
from daily_liturgy.exceptions import UnsupportedLocaleError
from daily_liturgy.ibreviary.arabic import get_daily_liturgy_arabic
from daily_liturgy.ibreviary.english import get_daily_liturgy_english
from daily_liturgy.ibreviary.galician import get_daily_liturgy_galician
from daily_liturgy.ibreviary.latin import get_daily_liturgy_latin
from daily_liturgy.ibreviary.portuguese import get_daily_liturgy_portuguese
from daily_liturgy.ibreviary.romanian import get_daily_liturgy_romanian
from daily_liturgy.ibreviary.spanish import get_daily_liturgy_spanish
from daily_liturgy.locales.de_de import get_daily_liturgy_de_de
from daily_liturgy.locales.en_ph import get_daily_liturgy_en_ph
from daily_liturgy.locales.en_us import get_daily_liturgy_en_us
from daily_liturgy.locales.es_mx import get_daily_liturgy_es_mx
from daily_liturgy.locales.it_it import get_daily_liturgy_it_it
from daily_liturgy.locales.pl_pl import get_daily_liturgy_pl_pl
from daily_liturgy.locales.pt_br import get_daily_liturgy_pt_br
from daily_liturgy.models import DailyLiturgy

SUPPORTED_LOCALES: dict[str, Callable[[datetime.date], DailyLiturgy]] = {
    "en-us": get_daily_liturgy_en_us,
    "en-ph": get_daily_liturgy_en_ph,
    "pl-pl": get_daily_liturgy_pl_pl,
    "es-mx": get_daily_liturgy_es_mx,
    "pt-br": get_daily_liturgy_pt_br,
    "it-it": get_daily_liturgy_it_it,
    "de-de": get_daily_liturgy_de_de,
    "fr": partial(get_aelf_liturgy, zone="romain", locale="fr"),
    "fr-fr": partial(get_aelf_liturgy, zone="france", locale="fr-fr"),
    "fr-be": partial(get_aelf_liturgy, zone="belgique", locale="fr-be"),
    "fr-lu": partial(get_aelf_liturgy, zone="luxembourg", locale="fr-lu"),
    "fr-ch": partial(get_aelf_liturgy, zone="suisse", locale="fr-ch"),
    "fr-mc": partial(get_aelf_liturgy, zone="monaco", locale="fr-mc"),
    "fr-ca": partial(get_aelf_liturgy, zone="canada", locale="fr-ca"),
    "en": get_daily_liturgy_english,
    "es-es": get_daily_liturgy_spanish,
    "pt-pt": get_daily_liturgy_portuguese,
    "ro-ro": get_daily_liturgy_romanian,
    "gl-es": get_daily_liturgy_galician,
    "ar": get_daily_liturgy_arabic,
    "la": get_daily_liturgy_latin,
}


def get_daily_liturgy(date: datetime.date | None = None, locale: str = "en-us") -> DailyLiturgy:
    normalized = locale.strip().lower()
    if normalized not in SUPPORTED_LOCALES:
        supported = ", ".join(sorted(SUPPORTED_LOCALES))
        raise UnsupportedLocaleError(f"Unsupported locale {locale!r}. Supported locales: {supported}")
    liturgy = SUPPORTED_LOCALES[normalized](date or datetime.date.today())
    return liturgy.model_copy(update={"locale": normalized})
