"""
Hilfen für Kopf- und Fußzeile.

``{% current_page request "/preise/" %}`` gibt ``aria-current="page"`` aus, wenn
die Anfrage auf diese Seite (oder eine ihrer Unterseiten) zeigt. Screenreader
sagen so an, wo man sich befindet; die Kopfzeile hebt den Eintrag hervor.
"""

from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def current_page(request, href):
    if request is None or not href.startswith("/") or "#" in href:
        return ""
    path = request.path
    if path == href or (href != "/" and path.startswith(href)):
        return mark_safe(' aria-current="page"')
    return ""
