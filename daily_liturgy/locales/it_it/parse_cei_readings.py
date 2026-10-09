import re

from bs4 import Tag

from daily_liturgy.locales.it_it.split_cei_section import split_cei_section
from daily_liturgy.models import Reading

# Sections are also the Mass prayers ("Antifona", "Colletta", "Sulle offerte"…) and rites
# ("Benedizione e imposizione delle ceneri"); only the readings are kept.
_READING = re.compile(r"lettura|salmo|acclamazione|vangelo|sequenza|epistola", re.IGNORECASE)


def parse_cei_readings(mass: Tag) -> list[Reading]:
    """Each `div.cci-liturgia-giorno-dettagli-content` is a section titled by its
    `h2` ("Prima Lettura", "Salmo Responsoriale", "Seconda Lettura", "SEQUENZA",
    "Acclamazione al Vangelo", "Vangelo"). The psalm's citation is its
    `p.cci-liturgia-giorno-section-versetto` ("Dal Sal 137 (138)")."""
    readings = []
    for section in mass.select("div.cci-liturgia-giorno-dettagli-content"):
        heading = section.select_one("h2.cci-liturgia-giorno-section-title")
        reading_type = " ".join(heading.get_text().split()) if heading is not None else ""
        if not _READING.search(reading_type):
            continue
        options = split_cei_section(section)
        if not options:
            continue
        versetto = section.select_one("p.cci-liturgia-giorno-section-versetto")
        if versetto is not None:
            options[0] = (" ".join(versetto.get_text().split()), options[0][1])
        main, *alternatives = [Reading(type=reading_type, citation=c, content=text) for c, text in options]
        readings.append(main.model_copy(update={"alternatives": alternatives}))
    return readings
