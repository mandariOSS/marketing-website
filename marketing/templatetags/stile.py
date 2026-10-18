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
mit dem Build; bei einer Content-Security-Policy genügt sein Hash (``LADER``, siehe README). Den Hash des Skripts
und des kritischen CSS meldet der Tag für die Policy der Antwort an (``marketing/sicherheit.py``).

Fehlt das kritische CSS (Entwicklung ohne ``npm run build:css``) oder läuft die Seite mit ``DEBUG``, bleibt es beim
blockierenden ``<link rel="stylesheet">`` – dann passt das Ergebnis immer zum gerade gebauten ``styles.css``. Im
Betrieb schaltet ``KRITISCHES_CSS=aus`` (Umgebungsvariable, nach Neustart des Containers) ebenfalls dorthin zurück.
"""

import os

from django import template
from django.conf import settings
from django.contrib.staticfiles import finders
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail.blocks import StreamValue

from marketing.sicherheit import inline_erlauben

register = template.Library()

KRITISCH = "css/kritisch.css"
VOLL = "css/styles.css"

# Blöcke mit Bildern (loading="lazy"), die der Browser schon beim ersten Laden holt, weil sie am Handy kurz unter dem
# Seitenkopf stehen. Auf Seiten mit einem solchen Block lädt styles.css mit fetchpriority="high" (Chrome: High statt
# VeryLow). Lighthouse simuliert HTTP/2 als eine Verbindung und reiht Anfragen nach beobachtetem Start plus Aufschlag
# je Priorität (Low 1 s, VeryLow 2 s). Ohne die Angabe kam styles.css auf /produkte/ hinter die drei Produktbilder
# (150 KB) und schob das errechnete LCP am Handy von 1,7 auf 2,0 s. Im Browser laden diese Bilder ohnehin erst nach
# styles.css (``vorab``). Auf Seiten ohne solche Bilder bleibt es bei VeryLow: Dort kostete High 20 bis 50 ms LCP.
BLOECKE_MIT_BILDERN = {"produktbilder"}

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


def bilder_unter_dem_kopf(page):
    """Ob die Seite einen Block aus ``BLOECKE_MIT_BILDERN`` enthält (z. B. /produkte/; bei Rechtstexten ist ``body``
    noch das alte Textfeld)."""
    body = getattr(page, "body", None)
    return isinstance(body, StreamValue) and any(block.block_type in BLOECKE_MIT_BILDERN for block in body)


@register.simple_tag(takes_context=True)
def stile(context):
    url = static(VOLL)
    css = "" if settings.DEBUG or os.environ.get("KRITISCHES_CSS", "an") == "aus" else kritisches_css()
    if not css:
        return format_html('<link rel="stylesheet" href="{}">', url)
    prioritaet = mark_safe(' fetchpriority="high"' if bilder_unter_dem_kopf(context.get("page")) else "")
    inline_erlauben(context.get("request"), "style", css)
    inline_erlauben(context.get("request"), "script", LADER)
    return format_html(
        '<style>{}</style>\n'
        '    <link rel="stylesheet" href="{}" media="print"{} id="stile">\n'
        "    <script>{}</script>\n"
        '    <noscript><link rel="stylesheet" href="{}"></noscript>',
        mark_safe(css),  # eigene Build-Ausgabe, ohne "</" (sonst Rückfall auf das blockierende Stylesheet)
        url,
        prioritaet,
        mark_safe(LADER),
        url,
    )
