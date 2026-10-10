"""
IndexNow (https://www.indexnow.org/): meldet Bing, Yandex, Seznam, Naver und Yep neue, geänderte und entfernte
Adressen sofort, statt auf den nächsten Besuch des Crawlers zu warten. Google nimmt nicht teil; dort bleibt es bei
der Sitemap.

Der Schlüssel ``INDEXNOW_KEY`` (8–128 Zeichen aus Buchstaben, Ziffern und Bindestrich) zeigt, dass die Meldung von
uns kommt: Die Suchmaschine liest ihn unter ``/<schlüssel>.txt`` nach (``schluesseldatei``). Dieselbe Datei gilt für
die Meldungen der mandari-Anwendung (Insight) unter derselben Domain – beide brauchen denselben Wert.

Ohne Schlüssel ist alles aus: keine Datei, keine Meldung (Entwicklung, Tests, Vorschau-Instanzen).
"""

from __future__ import annotations

import json
import logging
import re
import urllib.error
import urllib.request
from collections.abc import Iterable
from urllib.parse import urlsplit

from django.conf import settings
from django.http import Http404, HttpResponse
from django.views.decorators.http import require_http_methods

from marketing import seo

logger = logging.getLogger(__name__)

#: Erlaubte Schlüssel laut Protokoll
SCHLUESSEL_MUSTER = re.compile(r"[A-Za-z0-9-]{8,128}")
#: Höchstens so viele Adressen je Meldung (Grenze des Protokolls)
ADRESSEN_JE_MELDUNG = 10_000
#: Wartezeit auf die Suchmaschine; die Meldung läuft beim Veröffentlichen mit
WARTEZEIT_SEKUNDEN = 5


def schluessel() -> str:
    """Der Schlüssel aus ``INDEXNOW_KEY``, wenn er dem Protokoll genügt, sonst ``""`` (IndexNow aus)."""
    wert = (getattr(settings, "INDEXNOW_KEY", "") or "").strip()
    return wert if SCHLUESSEL_MUSTER.fullmatch(wert) else ""


@require_http_methods(["GET", "HEAD"])
def schluesseldatei(request, name: str) -> HttpResponse:
    """``/<schlüssel>.txt``: Die Suchmaschine prüft hier, ob der Schlüssel einer Meldung zu mandari.de gehört."""
    aktuell = schluessel()
    if not aktuell or name != aktuell:
        raise Http404
    antwort = HttpResponse(aktuell, content_type="text/plain; charset=utf-8")
    antwort["Cache-Control"] = "public, max-age=86400"
    return antwort


def eigene(adressen: Iterable[str]) -> list[str]:
    """Nur absolute Adressen auf dem eigenen Host, jede einmal, in der Reihenfolge der Eingabe."""
    host = urlsplit(seo.site_url()).netloc
    gesehen: dict[str, None] = {}
    for adresse in adressen:
        teile = urlsplit(adresse or "")
        if teile.scheme in ("http", "https") and teile.netloc == host:
            gesehen.setdefault(adresse, None)
    return list(gesehen)


def melden(adressen: Iterable[str]) -> int:
    """
    Meldet ``adressen`` (absolute Adressen auf ``SITE_URL``) an ``INDEXNOW_ENDPOINT``; gibt zurück, wie viele die
    Suchmaschine angenommen hat (Antwort 200 oder 202).

    Wirft nie: Ein Fehler der Suchmaschine darf das Veröffentlichen nicht stören, die Sitemap bleibt der Weg dorthin.
    """
    aktuell = schluessel()
    liste = eigene(adressen)
    if not aktuell or not liste:
        return 0
    angenommen = 0
    for start in range(0, len(liste), ADRESSEN_JE_MELDUNG):
        teil = liste[start : start + ADRESSEN_JE_MELDUNG]
        daten = {
            "host": urlsplit(seo.site_url()).netloc,
            "key": aktuell,
            "keyLocation": seo.absolute_url(f"/{aktuell}.txt"),
            "urlList": teil,
        }
        anfrage = urllib.request.Request(
            settings.INDEXNOW_ENDPOINT,
            data=json.dumps(daten).encode(),
            headers={"Content-Type": "application/json; charset=utf-8"},
            method="POST",
        )
        try:
            # Feste Adresse aus den Einstellungen (https), keine Eingabe von außen
            with urllib.request.urlopen(anfrage, timeout=WARTEZEIT_SEKUNDEN) as antwort:  # noqa: S310
                status = antwort.status
        except urllib.error.HTTPError as fehler:
            status = fehler.code
        except (OSError, ValueError) as fehler:
            logger.warning("IndexNow: %d Adressen nicht gemeldet (%s)", len(teil), fehler)
            continue
        if status in (200, 202):
            angenommen += len(teil)
            logger.info("IndexNow: %d Adressen gemeldet (Antwort %d)", len(teil), status)
        else:
            # 400 Format, 403 Schlüssel nicht gefunden, 422 fremde Adressen, 429 zu viele Meldungen
            logger.warning("IndexNow: %d Adressen abgelehnt (Antwort %d)", len(teil), status)
    return angenommen


def seitenadressen(page) -> list[str]:
    """Adresse einer Seite und ihrer Elternseite (Übersichten wie /releases/ zeigen ihre Unterseiten)."""
    adressen = []
    for seite in (page, page.get_parent()):
        # Wurzel des Seitenbaums hat keine Adresse; die Elternseite nur, solange sie veröffentlicht ist
        if seite is None or seite.depth < 2 or (seite is not page and not seite.live):
            continue
        pfad = seite.specific.get_url()
        if pfad:
            adressen.append(seo.absolute_url(urlsplit(pfad).path))
    return adressen
