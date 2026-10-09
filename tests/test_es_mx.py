import datetime

import pytest

from daily_liturgy import Celebration, LiturgyNotAvailableError, Rank, Season, get_daily_liturgy
from daily_liturgy.locales.en_us.fetch_usccb_items import USCCB_SPANISH_FEED_URL, fetch_usccb_items
from daily_liturgy.locales.es_mx import get_daily_liturgy_es_mx
from daily_liturgy.locales.es_mx.parse_usccb_celebraciones import parse_usccb_celebraciones
from daily_liturgy.locales.es_mx.parse_usccb_lecturas import parse_usccb_lecturas
from daily_liturgy.locales.es_mx.split_usccb_heading import split_usccb_heading


def types(liturgy):
    return [reading.type for reading in liturgy.readings]


def test_weekday(usccb_feed):
    liturgy = get_daily_liturgy_es_mx(datetime.date(2026, 10, 8))
    assert liturgy.locale == "es-mx"
    assert liturgy.source_url == "https://bible.usccb.org/es/bible/lecturas/100826.cfm"
    assert types(liturgy) == ["Primera lectura", "Salmo Responsorial", "Aclamación antes del Evangelio", "Evangelio"]
    assert [r.citation for r in liturgy.readings] == ["Gálatas 3, 1-5", "Lucas 1, 69-70. 71-71. 73-75", "Cfr Hechos 16, 14", "Lucas 11, 5-13"]

    first, psalm, _, gospel = liturgy.readings
    assert first.content.startswith("¡Insensatos gálatas!")
    assert psalm.content.startswith("R. (cf. 68) Bendito sea el Señor, Dios de Israel.\nEl Señor ha hecho surgir")
    assert gospel.content.startswith("En aquel tiempo, Jesús dijo a sus discípulos:")


def test_weekday_metadata(usccb_feed):
    liturgy = get_daily_liturgy(datetime.date(2026, 10, 8), "ES-MX")
    assert (liturgy.season, liturgy.week, liturgy.color) == (Season.ORDINARY_TIME, 27, None)
    assert liturgy.celebrations == []


def test_sunday_has_second_reading(usccb_feed):
    liturgy = get_daily_liturgy_es_mx(datetime.date(2026, 10, 4))
    assert types(liturgy)[2] == "Segunda lectura"
    assert liturgy.readings[2].citation == "Filipenses 4, 6-9"
    assert liturgy.celebrations == []


def test_o_bien_becomes_alternative(usccb_feed):
    liturgy = get_daily_liturgy_es_mx(datetime.date(2026, 9, 29))
    first = liturgy.readings[0]
    assert first.citation == "Daniel 7, 9-10. 13-14"
    assert [(alt.type, alt.citation) for alt in first.alternatives] == [("Primera lectura", "Apocalipsis 12, 7-12")]
    assert first.alternatives[0].content.startswith("En el cielo se trabó una gran batalla")
    assert len(liturgy.readings) == 4


def test_feast_and_memorial_metadata(usccb_feed):
    feast = get_daily_liturgy_es_mx(datetime.date(2026, 9, 29))
    assert feast.celebrations == [Celebration(name="Santos Arcángeles Miguel, Gabriel y Rafael", rank=Rank.FEAST)]
    assert feast.color is None
    memorial = get_daily_liturgy_es_mx(datetime.date(2026, 10, 7))
    assert memorial.celebrations == [Celebration(name="Bienaventurada Virgen María del Rosario", rank=Rank.MEMORIAL)]


def test_date_outside_feed_raises(usccb_feed):
    with pytest.raises(LiturgyNotAvailableError, match="2026-09-29 to 2026-10-08"):
        get_daily_liturgy_es_mx(datetime.date(2026, 10, 9))


@pytest.mark.parametrize(
    "heading, expected",
    [
        ("Primera lectura  Gálatas 2, 1-2. 7-14", ("Primera lectura", "Gálatas 2, 1-2. 7-14")),
        ("Salmo Responsorial Del Salmo 26", ("Salmo Responsorial", "Del Salmo 26")),
        ("Primera lectura Cantar de los Cantares 2, 8-14", ("Primera lectura", "Cantar de los Cantares 2, 8-14")),
        ("O bien: Apocalipsis 12, 7-12", ("O bien", "Apocalipsis 12, 7-12")),
        ("Evangelio de la procesión Cfr 1 Corintios 5, 7", ("Evangelio de la procesión", "Cfr 1 Corintios 5, 7")),
        ("Lectura del santo Evangelio Mateo 26, 14", ("Lectura del santo Evangelio", "Mateo 26, 14")),
        ("Secuencia", ("Secuencia", "")),
    ],
)
def test_split_heading(heading, expected):
    assert split_usccb_heading(heading) == expected


@pytest.mark.parametrize(
    "title, expected",
    [
        ("Jueves de la XXVII semana del Tiempo ordinario", []),
        ("XXVII Domingo ordinario", []),
        ("Domingo de Ramos de la Pasión del Señor", []),
        ("Miércoles de Ceniza", []),
        ("17 de diciembre", []),
        ("Memoria libre de San Bruno, presbítero", [Celebration(name="San Bruno, presbítero", rank=Rank.OPTIONAL_MEMORIAL)]),
        ("Solemnidad de la Natividad del Señor", [Celebration(name="Natividad del Señor", rank=Rank.SOLEMNITY)]),
        ("Domingo de Pascua de la Resurrección del Señor", [Celebration(name="Domingo de Pascua de la Resurrección del Señor", rank=None)]),
    ],
)
def test_celebrations_from_title(title, expected):
    assert parse_usccb_celebraciones(title) == expected


@pytest.mark.network
def test_live_feed():
    items = fetch_usccb_items(USCCB_SPANISH_FEED_URL)
    assert items and "/es/bible/lecturas/" in items[0]["link"]
    readings = parse_usccb_lecturas(items[0]["description"])
    assert readings[0].type == "Primera lectura" and readings[0].citation
    assert readings[-1].type == "Evangelio"
