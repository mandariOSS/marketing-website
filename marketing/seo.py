"""
SEO-Grundlagen: Seitentitel, Meta-Description und kanonische Adressen.

Alle absoluten Adressen (Canonical, og:url, og:image, Sitemap) entstehen aus
``settings.SITE_URL`` und dem Pfad der Anfrage – nie aus dem Host-Header. So
zeigt das Canonical auch hinter einem TLS-terminierenden Proxy auf ``https://``,
und ein gefälschter Host-Header kann keine fremde Adresse in die Seite schreiben.
"""

from __future__ import annotations

import re
from urllib.parse import urlsplit

from django.conf import settings
from django.utils.html import strip_tags

BRAND = "mandari"
TITLE_SEPARATOR = " | "
HOME_SEPARATOR = " – "
DESCRIPTION_MAX_LENGTH = 160

# Ältere Seeds und Templates hängen die Marke selbst an („Preise – Mandari“,
# „Kontakt | Mandari“). Der Zusatz wird entfernt und einheitlich neu gesetzt.
_BRAND_SUFFIX = re.compile(r"\s*[|–—-]\s*mandari\s*$", re.IGNORECASE)
_BRAND_WORD = re.compile(r"\bMandari\b|\bMANDARI\b")

# Reihenfolge, in der Textfelder einer Seite als Rückfall für die
# Meta-Description dienen, wenn ``search_description`` leer ist.
_TEXT_FIELDS = ("excerpt", "intro", "subtitle")
_STREAM_FIELDS = ("body_stream", "body")
_STREAM_TEXT_KEYS = ("subline", "body", "description", "intro", "text", "subline_secondary")
_MIN_FALLBACK_LENGTH = 50


def site_url() -> str:
    """Öffentliche Basisadresse ohne abschließenden Schrägstrich."""
    return (getattr(settings, "SITE_URL", "") or "https://mandari.de").rstrip("/")


def absolute_url(path: str) -> str:
    """Baut eine absolute Adresse aus SITE_URL und einem Pfad (Query/Host werden verworfen)."""
    parts = urlsplit(path or "/")
    clean_path = parts.path or "/"
    if not clean_path.startswith("/"):
        clean_path = "/" + clean_path
    return site_url() + clean_path


def normalize_brand(text: str) -> str:
    """Schreibt die Marke klein („Mandari“ → „mandari“)."""
    return _BRAND_WORD.sub(BRAND, text)


def clean_title(text: str) -> str:
    """Entfernt Leerraum-Folgen und angehängte Markenzusätze, schreibt die Marke klein."""
    text = " ".join(str(text or "").split())
    previous = None
    while previous != text:
        previous = text
        text = _BRAND_SUFFIX.sub("", text).strip()
    return normalize_brand(text)


def full_title(text: str, is_home: bool = False) -> str:
    """„<Titel> | mandari“; die Startseite trägt „mandari – <Claim>“."""
    title = clean_title(text)
    if is_home:
        if not title:
            return BRAND
        if title.lower().startswith(BRAND):
            return title
        return f"{BRAND}{HOME_SEPARATOR}{title}"
    if not title or title.lower() == BRAND:
        return BRAND
    return f"{title}{TITLE_SEPARATOR}{BRAND}"


def plain_text(value) -> str:
    """HTML/RichText → einzeiliger Klartext."""
    return " ".join(strip_tags(str(value or "")).split())


def truncate(text: str, limit: int = DESCRIPTION_MAX_LENGTH) -> str:
    """Kürzt an einer Wortgrenze und hängt eine Ellipse an."""
    text = " ".join((text or "").split())
    if len(text) <= limit:
        return text
    cut = text[: limit - 1].rsplit(" ", 1)[0].rstrip(" ,;:–-")
    return cut + "…"


def _first_text(value) -> str:
    """Erster ausreichend langer Text in einem (verschachtelten) Block-Wert."""
    if isinstance(value, str):
        text = plain_text(value)
        return text if len(text) >= _MIN_FALLBACK_LENGTH else ""
    if isinstance(value, dict):
        for key in _STREAM_TEXT_KEYS:
            if key in value:
                text = _first_text(value[key])
                if text:
                    return text
        for item in value.values():
            if isinstance(item, (dict, list)):
                text = _first_text(item)
                if text:
                    return text
        return ""
    if isinstance(value, list):
        for item in value:
            text = _first_text(item)
            if text:
                return text
    return ""


def _stream_text(stream) -> str:
    """Rückfall-Text aus einem StreamField: zuerst die Unterzeile des Heros, sonst der erste Absatz."""
    raw = getattr(stream, "raw_data", None)
    if not raw:
        return ""
    blocks = [block for block in raw if isinstance(block, dict)]
    for block in blocks:
        value = block.get("value")
        if block.get("type") == "hero" and isinstance(value, dict) and value.get("subline"):
            return plain_text(value["subline"])
    for block in blocks:
        text = _first_text(block.get("value"))
        if text:
            return text
    return ""


def page_title(page) -> str:
    """Titel einer Wagtail-Seite ohne Markenzusatz (SEO-Titel vor Seitentitel)."""
    if page is None:
        return ""
    return getattr(page, "seo_title", "") or getattr(page, "title", "") or ""


def page_description(page) -> str:
    """Meta-Description: ``search_description``, sonst ein sinnvoller Rückfall aus dem Inhalt."""
    if page is None:
        return ""
    description = plain_text(getattr(page, "search_description", ""))
    if description:
        return truncate(normalize_brand(description))

    for field in _TEXT_FIELDS:
        text = plain_text(getattr(page, field, ""))
        if len(text) >= _MIN_FALLBACK_LENGTH:
            return truncate(normalize_brand(text))

    for field in _STREAM_FIELDS:
        value = getattr(page, field, None)
        if value is None:
            continue
        text = _stream_text(value) if hasattr(value, "raw_data") else plain_text(value)
        if len(text) >= _MIN_FALLBACK_LENGTH:
            return truncate(normalize_brand(text))

    title = clean_title(page_title(page))
    return f"{title}: {BRAND} – Software für die offene Verwaltung." if title else ""


def is_home(page) -> bool:
    """Wurzelseite der Website (Startseite)?"""
    return page is not None and getattr(page, "depth", None) == 2
