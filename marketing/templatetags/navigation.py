"""
Hilfen für Kopf- und Fußzeile.

``{% current_page request "/preise/" %}`` gibt ``aria-current="page"`` aus, wenn
die Anfrage auf diese Seite (oder eine ihrer Unterseiten) zeigt. Screenreader
sagen so an, wo man sich befindet; die Kopfzeile hebt den Eintrag hervor.

``{% current_section request "/produkte/" "/kommunen/" %}`` gibt ``data-aktiv="true"``
aus, wenn die Anfrage in einem dieser Bereiche liegt. Der Knopf des Produkte-Menüs
zeigt damit, dass die aktuelle Seite in seinem Menü steht.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


def _passt(request, href):
    if request is None or not href.startswith("/") or "#" in href:
        return False
    path = request.path
    return path == href or (href != "/" and path.startswith(href))


@register.simple_tag
def current_page(request, href):
    return mark_safe(' aria-current="page"') if _passt(request, href) else ""


@register.simple_tag
def current_section(request, *hrefs):
    return mark_safe(' data-aktiv="true"') if any(_passt(request, href) for href in hrefs) else ""
