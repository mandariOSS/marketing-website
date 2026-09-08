"""
Typografie-Filter für Templates.

``shy``: fügt in lange Wörter weiche Trennstellen (U+00AD) nach deutscher
Silbentrennung ein. Browser brechen damit an sinnvollen Stellen mit Trennstrich
um — unabhängig davon, ob ``hyphens: auto`` ein Wörterbuch zur Verfügung hat.
Kurze Wörter bleiben unverändert, Autoescaping bleibt aktiv.
"""

import re

from django import template
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

register = template.Library()

SOFT_HYPHEN = "­"
MIN_LENGTH = 10
_WORD = re.compile(r"[A-Za-zÄÖÜäöüß]{%d,}" % MIN_LENGTH)
_dictionary = None


def _dic():
    global _dictionary
    if _dictionary is None:
        try:
            import pyphen

            _dictionary = pyphen.Pyphen(lang="de_DE")
        except Exception:  # Bibliothek fehlt → Filter wird zum No-op
            _dictionary = False
    return _dictionary


def soft_hyphenate(text: str) -> str:
    """Weiche Trennstellen in alle Wörter ab MIN_LENGTH Zeichen einfügen."""
    dic = _dic()
    if not dic or not text:
        return text or ""
    return _WORD.sub(lambda m: dic.inserted(m.group(0), hyphen=SOFT_HYPHEN), text)


@register.filter(name="shy", is_safe=True)
def shy(value):
    return mark_safe(soft_hyphenate(conditional_escape(value)))
