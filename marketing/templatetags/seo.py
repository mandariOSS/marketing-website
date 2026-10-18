"""
Template-Tags für Seitentitel, Meta-Description und kanonische Adressen.

Verwendung in ``base.html``::

    {% load seo %}
    {% seo_meta as seo %}
    {% capture as head_title %}{% block title %}{{ seo.title }}{% endblock %}{% endcapture %}
    <title>{{ head_title|full_title:seo.is_home }}</title>

``capture`` rendert seinen Inhalt einmal und legt ihn als Variable ab. So kann
ein Block, den Unterseiten überschreiben (``title``, ``meta_description``,
``canonical``), mehrfach ausgegeben werden – im ``<title>``, in Open Graph und
in der Twitter-Card – ohne dass Django den Block doppelt rendern muss.
"""

from html import unescape

from django import template
from django.templatetags.static import static
from django.utils.html import escape, format_html, strip_tags
from django.utils.safestring import mark_safe

from marketing import seo

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_meta(context):
    """Liefert Titel, Beschreibung und absolute Adressen für die aktuelle Seite."""
    page = context.get("page")
    request = context.get("request")
    path = request.path if request is not None else "/"
    return {
        "title": seo.page_title(page),
        "description": seo.page_description(page),
        "canonical": seo.absolute_url(path),
        "is_home": seo.is_home(page) or path == "/",
        "og_image": seo.absolute_url(static("images/og-default.png")),
        "site_name": seo.BRAND,
    }


@register.simple_tag(takes_context=True)
def strukturdaten(context):
    """Strukturierte Daten der Seite (schema.org, JSON-LD) als ``<script type="application/ld+json">``.

    Inhalt und Begründung (CSP, Maskierung) in ``marketing/strukturdaten.py``.
    """
    from marketing.strukturdaten import json_ld

    return format_html('<script type="application/ld+json">{}</script>', mark_safe(json_ld(context.get("page"))))


@register.filter(is_safe=True)
def full_title(value, is_home=False):
    """„<Titel> | mandari“ bzw. „mandari – <Claim>“ auf der Startseite."""
    return seo.full_title(value, is_home=bool(is_home))


@register.filter
def meta_text(value):
    """Beschreibungstext einzeilig, ohne Tags, Marke klein, höchstens 160 Zeichen.

    Gekürzt wird der entschlüsselte Text (keine halben HTML-Entitäten), danach wird
    er wieder maskiert.
    """
    text = unescape(strip_tags(str(value or "")))
    return mark_safe(escape(seo.truncate(seo.normalize_brand(text))))


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname):
        self.nodelist = nodelist
        self.varname = varname

    def render(self, context):
        output = self.nodelist.render(context)
        context[self.varname] = mark_safe(" ".join(output.split()))
        return ""


@register.tag(name="capture")
def do_capture(parser, token):
    """``{% capture as name %}…{% endcapture %}`` – rendert den Inhalt in eine Variable."""
    bits = token.split_contents()
    if len(bits) != 3 or bits[1] != "as":
        raise template.TemplateSyntaxError("Verwendung: {% capture as name %}…{% endcapture %}")
    nodelist = parser.parse(("endcapture",))
    parser.delete_first_token()
    return CaptureNode(nodelist, bits[2])
