"""
Stylesheets im Kopf: ``{% load stile %}{% stile %}`` in base.html.

Das vollständige ``styles.css`` hielt auf jeder Seite das erste Zeichnen auf (PageSpeed: render-blockierend). Jetzt
steht ein kleines kritisches CSS inline im Kopf (``static/css/kritisch.css``, gebaut mit ``npm run build:css`` aus
``tailwind.kritisch.config.js``): Grundgerüst, Kopfzeile und Seitenkopf. ``styles.css`` lädt parallel mit
``media="print"`` – das blockiert nicht und hat niedrige Priorität – und gilt, sobald es geladen ist. Bis dahin (und
bis Alpine gestartet ist) setzt das Ladeskript die Klasse ``vorab`` am ``<html>``; ``static/css/erste-ansicht.css``
blendet damit alles unterhalb des Seitenkopfs aus, statt es kurz ohne Gestaltung zu zeigen. Ohne JavaScript
lädt ``<noscript>`` das Stylesheet wie bisher blockierend, ``vorab`` gibt es dann nicht.

Bewusst kein ``<link rel="preload" as="style">``: Chrome lädt das mit höchster Priorität, Lighthouse rechnet es
dann weiter als render-blockierend. Das Ladeskript kommt ohne Inline-Handler (``onload``) aus und ändert sich nicht
mit dem Build; bei einer Content-Security-Policy genügt sein Hash (``LADER``, siehe README).

Fehlt das kritische CSS (Entwicklung ohne ``npm run build:css``) oder läuft die Seite mit ``DEBUG``, bleibt es beim
blockierenden ``<link rel="stylesheet">`` – dann passt das Ergebnis immer zum gerade gebauten ``styles.css``.
"""

import os

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

KRITISCH = "css/kritisch.css"
VOLL = "css/styles.css"

# styles.css gilt, sobald es geladen ist (aus dem Cache ist ``sheet`` schon gesetzt; bei einem Fehler zählt es als
# geladen). Sichtbar wird der Rest der Seite erst, wenn auch Alpine gestartet ist: Sonst erschienen Elemente mit
# x-cloak (Umschalter auf /kontakt/) erst danach und verschöben, was unter ihnen steht. Spätestens mit ``load``
# (auch ohne Alpine) ist alles sichtbar. Danach meldet ``stile:fertig``, dass die Seite vollständig steht (z. B. für
# das Scrollen zum Umschalter auf /kontakt/#termin).
LADER = (
    '(function(){var h=document.documentElement,l=document.getElementById("stile"),c=0,a=0;'
    'function z(){if(c&&a&&h.classList.contains("vorab")){h.classList.remove("vorab");'
    'document.dispatchEvent(new Event("stile:fertig"))}}'
    'function g(){l.media="all";c=1;z()}'
    'h.classList.add("vorab");'
    'document.addEventListener("alpine:initialized",function(){a=1;z()});'
    'addEventListener("load",function(){a=1;g()});'
    'if(l.sheet)g();else{l.addEventListener("load",g);l.addEventListener("error",g)}})();'
)

_gelesen = {}


def kritisches_css():
    """Inhalt von ``static/css/kritisch.css`` (je Prozess einmal gelesen, neu bei geänderter Datei) oder ``""``."""
    pfad = finders.find(KRITISCH)
    if not pfad:
        return ""
    stand = os.path.getmtime(pfad)
    if pfad not in _gelesen or _gelesen[pfad][0] != stand:
        with open(pfad, encoding="utf-8") as datei:
            css = datei.read().strip()
        _gelesen[pfad] = (stand, "" if "</" in css else css)
    return _gelesen[pfad][1]


@register.simple_tag
def stile():
    url = static(VOLL)
    css = "" if settings.DEBUG else kritisches_css()
    if not css:
        return format_html('<link rel="stylesheet" href="{}">', url)
    return format_html(
        '<style>{}</style>\n'
        '    <link rel="stylesheet" href="{}" media="print" id="stile">\n'
        "    <script>{}</script>\n"
        '    <noscript><link rel="stylesheet" href="{}"></noscript>',
        mark_safe(css),  # eigene Build-Ausgabe, ohne "</" (sonst Rückfall auf das blockierende Stylesheet)
        url,
        mark_safe(LADER),
        url,
    )
