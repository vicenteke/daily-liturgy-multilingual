from daily_liturgy.locales.en_us.parse_usccb_readings import parse_usccb_readings
from daily_liturgy.locales.es_mx.split_usccb_heading import split_usccb_heading
from daily_liturgy.models import Reading

_ALTERNATIVE = "o bien"


def parse_usccb_lecturas(description_html: str) -> list[Reading]:
    """Parse a Spanish feed item. It has the English feed's HTML, but the citation is
    plain text in the `<h4>` and alternatives are headed "O bien: <citation>"."""
    readings: list[Reading] = []
    for parsed in parse_usccb_readings(description_html):
        kind, citation = split_usccb_heading(parsed.type)
        reading = parsed.model_copy(update={"type": kind, "citation": parsed.citation or citation})
        if kind.lower() == _ALTERNATIVE and readings:
            main = readings[-1]
            alternative = reading.model_copy(update={"type": main.type})
            readings[-1] = main.model_copy(update={"alternatives": [*main.alternatives, alternative]})
        else:
            readings.append(reading)
    return readings
