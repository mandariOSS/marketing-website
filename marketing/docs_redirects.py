"""
Weiterleitungen der alten Dokumentation unter mandari.de/docs/ auf docs.mandari.de.

Die Dokumentation ist ein eigenes Projekt (github.com/mandariOSS/docs, MkDocs
Material). Bekannte alte Slugs werden auf ihre neuen Seiten abgebildet, alles
andere landet auf der Startseite der Dokumentation.
"""

from django.http import HttpResponsePermanentRedirect

DOCS_BASE = "https://docs.mandari.de/"

# alter Slug -> neuer Pfad (relativ zu DOCS_BASE)
SLUG_MAP = {
    "tutorial-termine-einbinden": "work/termine-einbinden/",
    "oparl": "insight/oparl-api/",
    "fraktions-api": "work/fraktions-api/",
    "session-api": "session/oparl-api/",
    "self-hosting": "betrieb/",
}


def docs_redirect(request, rest: str = ""):
    slug = rest.strip("/").split("/")[0] if rest else ""
    target = DOCS_BASE + SLUG_MAP.get(slug, "")
    return HttpResponsePermanentRedirect(target)
