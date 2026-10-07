"""
Fehlerseite 500 (``handler500`` in ``website/urls.py``).

Bei einem Serverfehler darf die Fehlerseite selbst nicht scheitern: Sie rendert ``templates/500.html`` ohne
Anfragekontext (keine Kontextprozessoren, keine Datenbank, keine Seitenobjekte) und fällt auf einen festen Text
zurück, wenn auch das nicht gelingt (z. B. ohne Manifest der statischen Dateien). Die 404-Seite braucht keinen eigenen
Handler: Django rendert ``templates/404.html`` mit Kopf- und Fußzeile (``django.views.defaults.page_not_found``).
"""

import logging

from django.conf import settings
from django.http import HttpResponseServerError
from django.template.loader import render_to_string

logger = logging.getLogger(__name__)

NOTFALL = (
    '<!DOCTYPE html><html lang="de"><head><meta charset="UTF-8"><meta name="robots" content="noindex">'
    "<title>Serverfehler | mandari</title></head><body><h1>Da ist etwas schiefgegangen.</h1>"
    "<p>Der Fehler liegt bei uns. Bitte versuchen Sie es in ein paar Minuten noch einmal.</p>"
    '<p><a href="/">Zur Startseite</a></p></body></html>'
)


def server_error(request, template_name="500.html"):
    """Antwort mit Status 500 aus der statischen Vorlage, sonst aus ``NOTFALL``."""
    try:
        html = render_to_string(template_name, {"status_url": settings.STATUS_PAGE_URL})
    except Exception:
        logger.exception("Fehlerseite 500 ließ sich nicht rendern, Notfalltext ausgeliefert")
        html = NOTFALL
    return HttpResponseServerError(html)
