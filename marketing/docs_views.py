# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Entwickler- und Anwender-Dokumentation unter /docs/.

Die Inhalte liegen als Markdown-Dateien in docs_content/ im Repository
(versioniert, per Pull Request pflegbar) und werden serverseitig mit
Inhaltsverzeichnis gerendert. Die Navigation ist hier zentral definiert.
Erreichbar unter mandari.de/docs/ sowie über docs.mandari.de (Redirect).
"""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

import markdown
from django.http import Http404
from django.shortcuts import render
from django.views.decorators.http import require_GET

DOCS_DIR = Path(__file__).resolve().parent.parent / "docs_content"

# Navigation: (Abschnitt, [(slug, Titel)])
DOCS_NAV = [
    (
        "Erste Schritte",
        [
            ("", "Übersicht"),
            ("tutorial-termine-einbinden", "Tutorial: Termine auf der Fraktions-Webseite"),
        ],
    ),
    (
        "APIs",
        [
            ("oparl", "OParl-API (Bürgerportal)"),
            ("fraktions-api", "Öffentliche Fraktions-API v1"),
            ("session-api", "Session-API (Verwaltung)"),
        ],
    ),
    (
        "Betrieb",
        [
            ("self-hosting", "Self-Hosting mit Docker"),
        ],
    ),
]

_VALID_SLUGS = {slug for _section, entries in DOCS_NAV for slug, _title in entries}


def _title_for(slug: str) -> str:
    for _section, entries in DOCS_NAV:
        for entry_slug, title in entries:
            if entry_slug == slug:
                return title
    return "Dokumentation"


@lru_cache(maxsize=64)
def _render_markdown(slug: str, mtime: float) -> str:
    """Markdown -> HTML (Cache-Key enthält mtime für Live-Aktualisierung)."""
    path = DOCS_DIR / f"{slug or 'index'}.md"
    text = path.read_text(encoding="utf-8")
    return markdown.markdown(
        text,
        extensions=["fenced_code", "tables", "toc", "attr_list"],
        extension_configs={"toc": {"permalink": False}},
        output_format="html",
    )


@require_GET
def docs_page(request, slug: str = ""):
    """Eine Dokumentationsseite rendern (Index bei leerem Slug)."""
    if slug not in _VALID_SLUGS:
        raise Http404("Unbekannte Dokumentationsseite")

    path = DOCS_DIR / f"{slug or 'index'}.md"
    if not path.exists():
        raise Http404("Seite noch nicht verfügbar")

    content_html = _render_markdown(slug, path.stat().st_mtime)
    return render(
        request,
        "marketing/docs.html",
        {
            "docs_nav": DOCS_NAV,
            "active_slug": slug,
            "doc_title": _title_for(slug),
            "content_html": content_html,
        },
    )
