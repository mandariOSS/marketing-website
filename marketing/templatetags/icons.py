"""
Symbole als Inline-SVG: ``{% icon "check" "w-4 h-4 flex-none" %}``.

Die Pfade stammen unverändert aus Lucide v0.469.0 (ISC, https://lucide.dev), dieselbe Optik wie zuvor. Sie
werden auf dem Server in die Seite geschrieben – kein Lucide-JavaScript mehr, das im Kopf blockiert und die
Symbole erst nach dem Laden erzeugt. Symbole stehen neben einem Text und sind deshalb immer ``aria-hidden``.

Ein neues Symbol: Pfade von https://lucide.dev (Version wie oben) in ``ICONS`` übernehmen. Symbole mit
Alpine-Attributen (``x-show``, ``:class``) stehen als ``<svg>`` direkt im Template, z. B. in der Kopfzeile.
"""

from django import template
from django.utils.html import format_html
from django.utils.safestring import mark_safe

register = template.Library()

ICONS = {
    "arrow-left": '<path d="m12 19-7-7 7-7"/><path d="M19 12H5"/>',
    "check": '<path d="M20 6 9 17l-5-5"/>',
    "check-circle": '<path d="M21.801 10A10 10 0 1 1 17 3.335"/><path d="m9 11 3 3L22 4"/>',
    "chevron-down": '<path d="m6 9 6 6 6-6"/>',
    "chevron-left": '<path d="m15 18-6-6 6-6"/>',
    "chevron-right": '<path d="m9 18 6-6-6-6"/>',
    "circle-dashed": '<path d="M10.1 2.182a10 10 0 0 1 3.8 0"/><path d="M13.9 21.818a10 10 0 0 1-3.8 0"/><path d="M17.609 3.721a10 10 0 0 1 2.69 2.7"/><path d="M2.182 13.9a10 10 0 0 1 0-3.8"/><path d="M20.279 17.609a10 10 0 0 1-2.7 2.69"/><path d="M21.818 10.1a10 10 0 0 1 0 3.8"/><path d="M3.721 6.391a10 10 0 0 1 2.7-2.69"/><path d="M6.391 20.279a10 10 0 0 1-2.69-2.7"/>',
    "circle-dot": '<circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="1"/>',
    "circle-help": '<circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><path d="M12 17h.01"/>',
    "clock": '<circle cx="12" cy="12" r="10"/><polyline points="12 6 12 12 16 14"/>',
    "link": '<path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/>',
    "minus": '<path d="M5 12h14"/>',
    "moon": '<path d="M12 3a6 6 0 0 0 9 9 9 9 0 1 1-9-9Z"/>',
    "newspaper": '<path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"/><path d="M18 14h-8"/><path d="M15 18h-5"/><path d="M10 6h8v4h-8V6Z"/>',
    "rss": '<path d="M4 11a9 9 0 0 1 9 9"/><path d="M4 4a16 16 0 0 1 16 16"/><circle cx="5" cy="19" r="1"/>',
    "search": '<circle cx="11" cy="11" r="8"/><path d="m21 21-4.3-4.3"/>',
    "sun": '<circle cx="12" cy="12" r="4"/><path d="M12 2v2"/><path d="M12 20v2"/><path d="m4.93 4.93 1.41 1.41"/><path d="m17.66 17.66 1.41 1.41"/><path d="M2 12h2"/><path d="M20 12h2"/><path d="m6.34 17.66-1.41 1.41"/><path d="m19.07 4.93-1.41 1.41"/>',
}

_SVG = (
    '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" '
    'stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="{}" '
    'aria-hidden="true" focusable="false">{}</svg>'
)


@register.simple_tag
def icon(name, css=""):
    """Inline-SVG eines Symbols aus ``ICONS``; ein unbekannter Name ist ein Fehler im Template."""
    try:
        pfade = ICONS[name]
    except KeyError as fehler:
        raise template.TemplateSyntaxError(f"Unbekanntes Symbol: {name!r}") from fehler
    return format_html(_SVG, css, mark_safe(pfade))
