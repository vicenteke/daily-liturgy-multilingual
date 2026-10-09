from bs4 import BeautifulSoup

from daily_liturgy.models import Color

_COLORS = {
    "verde": Color.GREEN,
    "roxo": Color.VIOLET,
    "branco": Color.WHITE,
    "vermelho": Color.RED,
    "rosa": Color.ROSE,
    "róseo": Color.ROSE,
    "preto": Color.BLACK,
}


def parse_cancaonova_color(page_html: str) -> Color | None:
    """Parse `<span class="cor-liturgica">Cor Litúrgica: Verde</span>`; None if missing or unknown."""
    label = BeautifulSoup(page_html, "html.parser").select_one(".cor-liturgica")
    if label is None:
        return None
    value = label.get_text().split(":")[-1].strip().lower()
    return _COLORS.get(value)
