"""
Inline-Code für die Content-Security-Policy anmelden (``marketing/sicherheit.py``).

``{% load sicherheit %}{% csp_inline %}<script>…</script>{% endcsp_inline %}`` gibt seinen Inhalt unverändert aus
und meldet den Text jedes Inline-Skripts und jedes ``<style>``-Elements darin mit seinem Hash an; die Middleware
erlaubt genau diese Hashes. Ausgenommen sind Skripte mit ``src`` und Datenblöcke (``type="application/ld+json"``),
die der Browser nicht ausführt. Nur für festen Code aus der Vorlage, nie für Eingaben.

``{% csp_altcha %}`` erlaubt auf Seiten mit Kontaktformular den Stil, den Altcha beim Laden in den Kopf schreibt.
"""

import re

from django import template

from marketing.sicherheit import altcha_erlauben, inline_erlauben

register = template.Library()

_ELEMENT = re.compile(r"<(script|style)\b([^>]*)>(.*?)</\1\s*>", re.IGNORECASE | re.DOTALL)
_TYP = re.compile(r"""\btype\s*=\s*["']?([^"'\s>]+)""", re.IGNORECASE)
# Skript-Typen, die der Browser ausführt (leer = klassisches Skript)
_AUSFUEHRBAR = {"", "text/javascript", "application/javascript", "module"}


def anmelden(html: str, request) -> None:
    """Meldet die Inline-Skripte und -Stile in ``html`` für die Antwort auf ``request`` an."""
    for element in _ELEMENT.finditer(html):
        art, attribute, inhalt = element.group(1).lower(), element.group(2), element.group(3)
        if art == "script":
            typ = _TYP.search(attribute)
            if re.search(r"\bsrc\s*=", attribute, re.IGNORECASE) or (typ and typ.group(1).lower() not in _AUSFUEHRBAR):
                continue
        inline_erlauben(request, art, inhalt)


class CspInlineNode(template.Node):
    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        html = self.nodelist.render(context)
        anmelden(html, context.get("request"))
        return html


@register.tag(name="csp_inline")
def csp_inline(parser, token):
    """``{% csp_inline %}…{% endcsp_inline %}`` – Inline-Skripte und -Stile darin für die CSP anmelden."""
    if len(token.split_contents()) != 1:
        raise template.TemplateSyntaxError("Verwendung: {% csp_inline %}…{% endcsp_inline %}")
    nodelist = parser.parse(("endcsp_inline",))
    parser.delete_first_token()
    return CspInlineNode(nodelist)


@register.simple_tag(takes_context=True)
def csp_altcha(context):
    """Stil von Altcha für die Content-Security-Policy dieser Seite anmelden (gibt nichts aus)."""
    altcha_erlauben(context.get("request"))
    return ""
