"""
Sicherheits-Header der Website: ``Permissions-Policy`` und ``Content-Security-Policy`` (CSP).

**Permissions-Policy** sperrt Gerätefunktionen und Schnittstellen, die die Website nicht braucht (Kamera, Mikrofon,
Standort, Zahlungen, USB …), für die Seite und alles, was sie einbettet. Die Liste nennt nur Funktionen, die Chrome
kennt: Unbekannte Namen meldet der Browser als Fehler in der Konsole (Lighthouse „Best Practices“).

**Content-Security-Policy** mit dem Schalter ``CSP_MODUS`` (Umgebungsvariable, ``website/settings.py``):

* ``report`` (Standard): ``Content-Security-Policy-Report-Only``. Der Browser blockiert nichts und meldet Verstöße an
  ``CSP_REPORT_URI`` (Standard ``/csp-report/``: der Endpunkt der mandari-Anwendung auf derselben Domain, Logger
  ``mandari.csp`` und Zähler ``mandari_csp_violations_total``).
* ``scharf``: ``Content-Security-Policy``. Der Browser blockiert Verstöße und meldet sie weiter.
* ``aus``: keine CSP.

Inline-Code ist nur mit seinem SHA-256-Hash erlaubt, nicht pauschal (kein ``'unsafe-inline'`` für Skripte und
``<style>``-Elemente). Vorlagen schreiben Inline-Skripte und -Stile deshalb in
``{% csp_inline %}…{% endcsp_inline %}`` (``marketing/templatetags/sicherheit.py``); Code, der selbst Inline-Code
ausgibt (``{% stile %}``), meldet ihn mit :func:`inline_erlauben` an. Die Middleware nimmt die Hashes, die beim
Rendern einer Antwort angefallen sind, in deren Policy auf. Hashes statt Nonce, weil die Seiten so bytegleich bleiben
(ETag, kein Zufallswert im HTML, das HTML bleibt so klein wie bisher). Anmelden darf man nur feste Texte aus
Vorlagen und eigenem Code, nie Eingaben: Was angemeldet ist, führt der Browser aus.

Bewusst noch erlaubt: ``'unsafe-eval'`` für Alpine (die Ausdrücke in ``x-data``, ``@click``, ``:class`` wertet Alpine
per ``new Function`` aus, bis zu einem Wechsel auf den CSP-Build von Alpine) und ``'unsafe-inline'`` nur für
``style``-Attribute (Geometrie der Muster wie Zeitskala und Dauerbalken, der ausgeblendete Spamschutz). Ausgenommen
von der CSP sind die Verwaltungsoberflächen (Wagtail und Django-Admin) mit eigenem Inline-Code.
"""

from __future__ import annotations

import base64
import hashlib
import logging
import re
from functools import lru_cache

from django.conf import settings
from django.contrib.staticfiles import finders
from django.utils.csp import CSP, build_policy

logger = logging.getLogger(__name__)

# Sensoren, Kamera und Mikrofon, Bildschirmaufnahme, Standort, Zahlungen und Geräteschnittstellen. Bewusst kurz: Die
# Header gehen mit jeder Seite über die Leitung (erste TCP-Pakete, siehe scripts/check_kritisches_css.py).
PERMISSIONS_POLICY = ", ".join(
    f"{funktion}=()"
    for funktion in (
        "accelerometer",
        "camera",
        "display-capture",
        "geolocation",
        "gyroscope",
        "hid",
        "magnetometer",
        "microphone",
        "midi",
        "payment",
        "serial",
        "usb",
    )
)

# Als str: WSGI-Server nehmen nur echte Zeichenketten als Header-Namen an (CSP ist ein StrEnum)
MODI = {"aus": None, "report": str(CSP.HEADER_REPORT_ONLY), "scharf": str(CSP.HEADER_ENFORCE)}
STANDARD_MODUS = "report"
# Eigener Inline-Code: Wagtail- und Django-Admin bekommen keine CSP dieser Website
OHNE_CSP = ("/cms-admin/", "/django-admin/")

_ANGEMELDET = "_csp_inline"
ALTCHA = "vendor/altcha/altcha.min.js"


def quelle(inhalt: str) -> str:
    """Hash-Quelle (``'sha256-…'``) für den Text eines Inline-Elements, wie der Browser sie bildet.

    Der HTML-Parser macht aus jedem Zeilenende vorab ein LF; auf Windows ausgecheckte Vorlagen (CRLF) ergeben
    deshalb denselben Hash wie im Betrieb.
    """
    text = inhalt.replace("\r\n", "\n").replace("\r", "\n")
    digest = hashlib.sha256(text.encode("utf-8")).digest()
    return f"'sha256-{base64.b64encode(digest).decode('ascii')}'"


def inline_erlauben(request, art: str, inhalt: str) -> None:
    """Meldet ein Inline-Skript (``art="script"``) oder einen Inline-Stil (``"style"``) dieser Antwort an.

    Nur für feste Texte aus Vorlagen und eigenem Code. Ohne Anfrage (z. B. Vorlagen im Test) passiert nichts.
    """
    if request is None or art not in ("script", "style"):
        return
    angemeldet = request.__dict__.setdefault(_ANGEMELDET, {"script": set(), "style": set()})
    angemeldet[art].add(quelle(inhalt))


def altcha_erlauben(request) -> None:
    """Meldet den Stil von Altcha für diese Antwort an (Seiten mit Kontaktformular, ``{% csp_altcha %}``)."""
    altcha = altcha_stil()
    if request is not None and altcha:
        request.__dict__.setdefault(_ANGEMELDET, {"script": set(), "style": set()})["style"].add(altcha)


@lru_cache(maxsize=1)
def altcha_stil() -> str:
    """Hash des Stils, den Altcha beim Laden als ``<style id="__altcha-css">`` in den Kopf schreibt (/kontakt/).

    Den Text liest die Funktion aus der lokal gehosteten Bibliothek, damit er nach einem Update stimmt. Findet sie ihn
    nicht (andere Fassung der Bibliothek), fehlt der Hash, die Website meldet den Verstoß im Report-Modus und
    ``marketing/tests/test_sicherheitsheader.py`` schlägt fehl.
    """
    pfad = finders.find(ALTCHA)
    if not pfad:
        return ""
    with open(pfad, encoding="utf-8") as datei:
        js = datei.read()
    einfuegen = re.search(r'function (\w+)\(e,t="__altcha-css"\)', js)
    aufruf = einfuegen and re.search(rf"\b{re.escape(einfuegen.group(1))}\((\w+)\)", js)
    text = aufruf and re.search(rf"\b{re.escape(aufruf.group(1))}='((?:[^'\\]|\\.)*)'", js)
    if not text or "\\" in text.group(1):
        logger.warning("Stil von Altcha nicht gefunden – Hash fehlt in der Content-Security-Policy")
        return ""
    return quelle(text.group(1))


def richtlinie(angemeldet: dict | None = None) -> str:
    """Die Content-Security-Policy einer Antwort, mit den Hashes ihres Inline-Codes.

    Bilder, Schriften und Abrufe (``img-src``, ``font-src``, ``connect-src``) folgen ``default-src 'self'``; die
    Policy bleibt so kurz, sie geht mit jeder Seite über die Leitung.
    """
    angemeldet = angemeldet or {}
    return build_policy(
        {
            "default-src": [CSP.SELF],
            "script-src": [CSP.SELF, CSP.UNSAFE_EVAL, *sorted(angemeldet.get("script", ()))],
            "style-src": [CSP.SELF, *sorted(angemeldet.get("style", ()))],
            "style-src-attr": [CSP.UNSAFE_INLINE],
            # Altcha rechnet den Spamschutz in einem Worker aus einer blob:-Adresse
            "worker-src": [CSP.SELF, "blob:"],
            "object-src": [CSP.NONE],
            "base-uri": [CSP.SELF],
            "form-action": [CSP.SELF],
            "frame-ancestors": [CSP.SELF],
            "report-uri": [settings.CSP_REPORT_URI] if getattr(settings, "CSP_REPORT_URI", "") else None,
        }
    )


def modus() -> str:
    """``CSP_MODUS`` aus den Settings; ein unbekannter Wert gilt als ``report`` (mit einer Warnung je Wert)."""
    return _gueltiger_modus(str(getattr(settings, "CSP_MODUS", STANDARD_MODUS) or "").strip().lower())


@lru_cache(maxsize=8)
def _gueltiger_modus(wert: str) -> str:
    if wert not in MODI:
        logger.warning("CSP_MODUS=%r ist unbekannt (aus, report, scharf) – es gilt %r", wert, STANDARD_MODUS)
        return STANDARD_MODUS
    return wert


class SicherheitsHeaderMiddleware:
    """Setzt ``Permissions-Policy`` auf jede Antwort und die CSP (je nach ``CSP_MODUS``) auf HTML-Seiten.

    Vorhandene Header einer Antwort bleiben stehen (eine View kann eine eigene Policy setzen).
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if "Permissions-Policy" not in response:
            response["Permissions-Policy"] = PERMISSIONS_POLICY
        header = MODI[modus()]
        if (
            header
            and header not in response
            and response.get("Content-Type", "").startswith("text/html")
            and not 300 <= response.status_code < 400
            and not request.path.startswith(OHNE_CSP)
        ):
            response[header] = richtlinie(getattr(request, _ANGEMELDET, None))
        return response
