"""Filter ``kennzahlen``: setzt die Kennzahlen des Bürgerportals in Seed-Texte ein (marketing/kennzahlen.py)."""

from django import template
from django.utils.safestring import SafeData, mark_safe

from marketing.kennzahlen import einsetzen

register = template.Library()


@register.filter
def kennzahlen(text):
    """``[kommunen]``, ``[vorgaenge]`` … durch Zahlen ersetzen. Eingesetzt werden nur Ziffern, Punkte und ein Datum,
    deshalb bleibt ein als sicher markierter Text sicher.

    Der Filter ``richtext`` von Wagtail liefert kein ``str``, sondern ein Objekt, das sich selbst als HTML ausgibt
    (``RichText``); es wird hier zu sicherem Text.
    """
    if not isinstance(text, str):
        if not hasattr(text, "__html__"):
            return text
        text = mark_safe(text.__html__())  # noqa: S308 - HTML, das Wagtail bereits als sicher ausgibt
    ergebnis = einsetzen(text)
    return mark_safe(ergebnis) if isinstance(text, SafeData) else ergebnis  # noqa: S308 - siehe Docstring
