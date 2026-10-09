# daily-liturgy

Daily Catholic Mass readings, in several languages, as typed Python objects. For a date and a locale, it returns that day's readings, along with the liturgical season, week, color and celebrations.

## Supported locales

| Locale  | Source | Dates available |
|---------|--------|-----------------|
| `en-us` | [USCCB](https://bible.usccb.org/bible/readings) (official RSS feed) | About the last 10 days |
| `en-ph` | [CBCP](https://cbcp.ph/) (Catholic Bishops' Conference of the Philippines; US lectionary text) | Published in batches (June 8 to November 30, 2026 as of October 2026) |
| `es-mx` | [USCCB en español](https://bible.usccb.org/es/bible/lecturas) (official RSS feed, Mexican lectionary text) | About the last 10 days |
| `pt-br` | [Canção Nova](https://liturgia.cancaonova.com/pb/) (CNBB text) | Past dates and a few months ahead |
| `fr`, `fr-fr`, `fr-be`, `fr-lu`, `fr-ch`, `fr-mc`, `fr-ca` | [AELF](https://www.aelf.org/) (official API of the French-speaking bishops' liturgical association; `fr` = General Roman Calendar, the others = national calendars) | About 2019 to the end of next year |
| `it-it` | [CEI](https://www.chiesacattolica.it/liturgia-del-giorno/) (Italian bishops' conference) | About the last and current liturgical years (2024 to end of 2026 as of Oct 2026). Celebration names are upper case, as published |
| `pl-pl` | [Konferencja Episkopatu Polski](https://episkopat.pl/liturgia/) (Polish bishops' conference) | Years back and ahead (2024 to 2027 checked) |
| `de-de` | [Schott](https://schott.erzabtei-beuron.de/) (Erzabtei Beuron; the German lectionary on the calendar of the German-speaking dioceses) | Past and future dates (2030 checked) |
| `la` | [iBreviary](https://www.ibreviary.com/m2/letture.php) (Latin lectionary, Nova Vulgata) | Past and future dates |
| `en` | iBreviary (US lectionary translation, general Roman calendar) | Past and future dates |
| `es-es` | iBreviary (Spain's lectionary and calendar) | Past and future dates |
| `pt-pt` | iBreviary (Portugal's lectionary and calendar) | Past and future dates |
| `ro-ro` | iBreviary (Romanian) | Past and future dates, with gaps |
| `gl-es` | iBreviary (Galician) | Past and future dates, with gaps |
| `ar` | iBreviary (Arabic) | Past and future dates |

`en-ph`: `celebrations` is always `[]` and `color` always `None`. CBCP publishes no color, and its pages follow the general calendar, so Philippine celebrations such as San Lorenzo Ruiz (Sep 28) or Santo Niño may be missing from them.

`pl-pl`: `color` is always `None`, because episkopat.pl publishes no color. Celebrations are given only when the day's title names a rank ("Uroczystość", "Święto", "Wspomnienie"). Pentecost or Christ the King, published without a rank, give `[]`. Celebration names are in the genitive form the title uses ("Najśw. Maryi Panny Różańcowej").

`de-de`: `color` is always `None`, because Schott publishes no color. On memorials the weekday's readings are returned, with the saint in `celebrations`. Temporal days are a celebration only when Schott's name for them says "Hochfest" or "Fest" (so Easter Sunday has none).

iBreviary isn't an official Church site. It's used where no official source is usable. Its locales have no celebrations or color (always `[]` and `None`), and some days are missing or incomplete. For example, no language has All Saints in 2026, which falls on a Sunday. Galician reading types come out in Italian ("Prima Lettura"), as iBreviary labels them.

## Install

```bash
pip install -e .
```

## Usage

```python
get_daily_liturgy(date: datetime.date | None = None, locale: str = "en-us") -> DailyLiturgy
```

- `date`: defaults to today.
- `locale`: one of the supported locales, case-insensitive. Any other value raises `UnsupportedLocaleError`.
- If the source has nothing for that date, it raises `LiturgyNotAvailableError`.

```python
import datetime
from daily_liturgy import get_daily_liturgy

liturgy = get_daily_liturgy(datetime.date(2026, 9, 29), "pt-br")

liturgy.season        # Season.ORDINARY_TIME
liturgy.week          # 26
liturgy.color         # Color.WHITE
liturgy.celebrations  # [Celebration(name="Santos Miguel, Gabriel e Rafael, Arcanjos", rank=Rank.FEAST)]

for reading in liturgy.readings:
    print(reading.type, reading.citation)
# 1ª Leitura Dn 7,9-10.13-14
# Salmo Sl 137(138),1-2a.2bc-3.4-5 (R. 1c)
# Evangelho Jo 1,47-51

liturgy.readings[0].alternatives[0].citation  # "Ap 12,7-12a" (may be read instead)
```

### `DailyLiturgy`

| Field | Type | Notes |
|-------|------|-------|
| `date` | `datetime.date` | |
| `locale` | `str` | e.g. `"en-us"` |
| `source_url` | `str` | Page the readings came from |
| `season` | `Season` | `advent`, `christmas`, `lent`, `easter_triduum`, `easter`, `ordinary_time` |
| `week` | `int \| None` | Week of the season. `None` in Christmas and the Triduum |
| `color` | `Color \| None` | `green`, `violet`, `white`, `red`, `rose`, `black`. `None` when the source doesn't publish it (never guessed), e.g. always for `en-us`, `es-mx`, `en-ph`, `pl-pl` and the iBreviary locales |
| `celebrations` | `list[Celebration]` | `name` and `rank` (`solemnity`, `feast`, `memorial`, `optional_memorial` or `None`). Empty on plain weekdays and Sundays, and always empty when the source doesn't name them (`en-ph`, iBreviary) |
| `readings` | `list[Reading]` | `type`, `citation`, `content` and `alternatives` (a list of `Reading`) |

Reading types and celebration names are given as each source publishes them, in its language.
