from django import template
from django.template.loader import render_to_string

register = template.Library()


@register.simple_tag(takes_context=True)
def block_template(context, template_name, value):
    """Ein Block-Template (``marketing/blocks/*.html``) mit eigenen Werten rendern.

    Block-Templates lesen ``self``/``value`` – das lässt sich mit ``{% include … with self=… %}``
    nicht setzen. So tragen feste Abschnitte (Kontakt, Angaben zum Unternehmen, Logo-Paket)
    dieselbe Gestaltung wie die StreamField-Blöcke.
    """
    values = context.flatten()
    values.update({"self": value, "value": value})
    return render_to_string(template_name, values, request=context.get("request"))


@register.simple_tag(takes_context=True)
def company_settings(context):
    """Unternehmensangaben (Stufenschalter) laden: ``{% company_settings as company %}``."""
    from company.models import CompanySettings

    return CompanySettings.load(request_or_site=context.get("request"))


@register.simple_tag
def logo_rules():
    """Nutzungshinweise der Wortmarke (dieselben wie in der LIESMICH.txt des Logo-Pakets)."""
    from company.press import LOGO_RULES

    return LOGO_RULES


@register.simple_tag
def section_header(title, subline="", anchor_id="", align="left"):
    """Werte für ``marketing/blocks/section_header.html`` – damit eingefügte Abschnitte
    dieselbe Überschrift tragen wie die StreamField-Blöcke."""
    return {
        "badge_text": "",
        "badge_icon": "",
        "badge_color": "primary",
        "title": title,
        "subline": subline,
        "align": align,
        "anchor_id": anchor_id,
    }


@register.filter
def insert_position(body, anchor_id):
    """Stelle, an der ein fester Abschnitt in den StreamField-Inhalt eingefügt wird.

    Nach dem Block, dessen Überschrift (oder der Block selbst) den Anker ``anchor_id`` trägt; gibt es ihn nicht,
    vor der abschließenden Einladung (gradient_cta); sonst ans Ende. Redaktionelle
    Änderungen an der Reihenfolge verschieben den Abschnitt so sinnvoll mit.
    """
    blocks = list(body or [])
    for index, block in enumerate(blocks):
        get = getattr(block.value, "get", lambda *_: None)
        header = get("header")
        if header and header.get("anchor_id") == anchor_id or get("anchor_id") == anchor_id:
            return index + 1
    if blocks and blocks[-1].block_type == "gradient_cta":
        return len(blocks) - 1
    return len(blocks)
