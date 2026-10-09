from bs4 import Tag

from daily_liturgy.models import Color

_COLORS = {
    "verde": Color.GREEN,
    "viola": Color.VIOLET,
    "bianco": Color.WHITE,
    "rosso": Color.RED,
    "rosa": Color.ROSE,
    "rosaceo": Color.ROSE,
    "nero": Color.BLACK,
}


def parse_cei_color(mass: Tag) -> Color | None:
    """Parse `<div class="cci-colore-liturgico">Colore Liturgico <span>verde</span></div>`;
    None if missing or unknown."""
    label = mass.select_one(".cci-colore-liturgico span")
    return _COLORS.get(label.get_text().strip().lower()) if label is not None else None
