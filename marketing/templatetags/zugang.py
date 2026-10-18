"""
Barrierefreiheit in Vorlagen.

``{{ html|neuer_tab }}``: Links mit ``target="_blank"`` (Rechtstexte aus ``.legal-content/``, Quellennachweise)
bekommen den vorgelesenen Hinweis „(öffnet in neuem Tab)“ (WCAG 3.2.5, Technik G201). Der Hinweis entsteht beim
Ausgeben; Inhalte in der Datenbank bleiben unverändert.

``{% aufruf_name label url %}``: ``aria-label`` mit dem Anlass, wenn ein Aufruf mit gleichem Text auf derselben Seite
zu verschiedenen Anlässen führt (``ANLASS_NAMEN`` in ``marketing/contact.py``), z. B. „Erstgespräch vereinbaren:
Pilotkommune werden“. Der sichtbare Text steht am Anfang (WCAG 2.5.3); nennt er den Anlass schon, bleibt es beim Text.
"""

import re

from django import template
from django.utils.html import conditional_escape, format_html
from django.utils.safestring import mark_safe

from marketing.contact import anlass_for_url

register = template.Library()

HINWEIS_NEUER_TAB = "(öffnet in neuem Tab)"
_LINK_NEUER_TAB = re.compile(
    r"""(<a\b[^>]*\btarget\s*=\s*(["']?)_blank\2[^>]*>)(.*?)(</a\s*>)""", re.IGNORECASE | re.DOTALL
)


def neuer_tab_hinweis(html: str) -> str:
    """Fügt in jeden Link mit ``target="_blank"`` den vorgelesenen Hinweis ein (einmal, auch bei Wiederholung)."""

    def einfuegen(link):
        if HINWEIS_NEUER_TAB in link.group(3):
            return link.group(0)
        return f'{link.group(1)}{link.group(3)}<span class="sr-only"> {HINWEIS_NEUER_TAB}</span>{link.group(4)}'

    return _LINK_NEUER_TAB.sub(einfuegen, html)


@register.filter(is_safe=True)
def neuer_tab(value):
    """Hinweis „(öffnet in neuem Tab)“ für Links mit ``target="_blank"``; nicht sicheres HTML wird maskiert."""
    return mark_safe(neuer_tab_hinweis(str(conditional_escape(value))))


def _ohne_bindestrich(text: str) -> str:
    return " ".join(str(text).replace("-", "").lower().split())


@register.simple_tag
def aufruf_name(label, url):
    """`` aria-label="<Text>: <Anlass>"`` für Aufrufe mit eingetragenem Anlass, sonst nichts."""
    anlass = anlass_for_url(url)
    if not anlass or _ohne_bindestrich(anlass) in _ohne_bindestrich(label):
        return ""
    return format_html(' aria-label="{}: {}"', label, anlass)
