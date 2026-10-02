"""
Marketing-specific Django views.

Most marketing pages are rendered by Wagtail. This module holds the few routes
that live outside the page tree: Altcha challenges, robots.txt, security.txt,
the Responsible-Disclosure policy and the crawler info page. /status/ is a plain
301 to the public status page (see website/urls.py).
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets

from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_http_methods

logger = logging.getLogger(__name__)


# ─────────────────────────── Altcha (DSGVO-konformer Captcha-Ersatz) ─────────
#
# Altcha ist ein Open-Source-Captcha auf Proof-of-Work-Basis. Kein Drittland,
# keine User-Tracking, kein externes API. Wir hosten die JS-Library lokal
# unter static/vendor/altcha/ und betreiben Challenge-Generierung +
# Validierung selbst.
#
# Algorithmus (aus der Altcha-Spec):
#   1. Server würfelt salt + number, bildet challenge = sha256(salt + number)
#   2. Server signiert challenge mit HMAC-SHA256(secret) → signature
#   3. Client (Browser) versucht number durch Brute-Force zu finden (PoW)
#   4. Client schickt payload (base64-JSON) zurück mit number, salt, sig
#   5. Server prüft: hash stimmt + signature stimmt + (Replay-Schutz, optional)
#
# Dependency-frei — alles in Python-stdlib.


@require_GET
def altcha_challenge(request):
    """Generiert eine Altcha-Challenge (JSON), die der <altcha-widget> abholt."""
    secret = getattr(settings, "ALTCHA_HMAC_KEY", "")
    max_number = getattr(settings, "ALTCHA_MAX_NUMBER", 100000)

    salt = secrets.token_hex(16)
    number = secrets.randbelow(max_number)
    challenge = hashlib.sha256(f"{salt}{number}".encode()).hexdigest()
    signature = hmac.new(
        secret.encode(),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()

    return JsonResponse(
        {
            "algorithm": "SHA-256",
            "challenge": challenge,
            "salt": salt,
            "signature": signature,
            "maxnumber": max_number,
        }
    )


def verify_altcha_payload(payload_b64: str) -> bool:
    """Verifiziert eine Altcha-Lösung. Aufrufen im Form-Handler.

    Beispiel im Kontakt-View:

        from marketing.views import verify_altcha_payload

        def kontakt(request):
            if request.method == "POST":
                if not verify_altcha_payload(request.POST.get("altcha", "")):
                    messages.error(request, "Captcha-Prüfung fehlgeschlagen.")
                    return redirect("kontakt")
                # ...rest der Form-Verarbeitung...

    Returns ``True`` bei gültiger Signatur + korrektem PoW, sonst ``False``.
    """
    if not payload_b64:
        return False
    try:
        payload = json.loads(base64.b64decode(payload_b64))
        salt = payload["salt"]
        number = payload["number"]
        challenge = payload["challenge"]
        signature = payload["signature"]
        algorithm = payload.get("algorithm", "")
    except (KeyError, ValueError, TypeError, json.JSONDecodeError):
        logger.warning("Altcha payload malformed")
        return False

    if algorithm != "SHA-256":
        return False

    # Prüfe: Hash der Lösung entspricht der Challenge
    expected_challenge = hashlib.sha256(f"{salt}{number}".encode()).hexdigest()
    if not hmac.compare_digest(expected_challenge, challenge):
        return False

    # Prüfe: Signatur ist valide (challenge wurde von uns ausgestellt)
    secret = getattr(settings, "ALTCHA_HMAC_KEY", "")
    expected_signature = hmac.new(
        secret.encode(),
        challenge.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected_signature, signature)


# ─────────────────────────── robots.txt (RFC 9309) ──────────────────────────


@require_http_methods(["GET", "HEAD"])
def robots_txt(request):
    """Serves /robots.txt according to RFC 9309.

    Standardized crawl directives for search engines and bots. Must be served
    as text/plain at the site root and return 200.

    Format reference: https://www.rfc-editor.org/rfc/rfc9309
    """
    site_url = (getattr(settings, "SITE_URL", "") or "https://mandari.de").rstrip("/")

    body = f"""# Mandari robots.txt
# RFC 9309 — https://www.rfc-editor.org/rfc/rfc9309
#
# Welcome, crawler. Mandari is an open-source Ratsinformationssystem.
# Public source: https://github.com/mandariOSS/mandari

# Default rule: crawl everything except admin & system endpoints
User-agent: *
Allow: /
Disallow: /cms-admin/
Disallow: /django-admin/
Disallow: /documents/
Disallow: /altcha/
Disallow: /work/
Crawl-delay: 1

# Sitemaps (sitemaps.org)
Sitemap: {site_url}/sitemap.xml
Sitemap: {site_url}/sitemap-insight-index.xml
"""
    return HttpResponse(body, content_type="text/plain; charset=utf-8")


# ─────────────────────────── Security.txt (RFC 9116) ────────────────────────


def security_disclosure_view(request):
    """Render /sicherheit/disclosure/ — Responsible Disclosure policy.

    Served via Django (not Wagtail) because Wagtail's MarketingPage tree
    doesn't allow nesting under /sicherheit/. This route is registered in
    website/urls.py BEFORE the Wagtail catch-all.
    """
    return render(request, "marketing/sicherheit_disclosure.html")


def crawler_info_view(request):
    """Render /crawler/ — Infoseite zum mandari-ingestor.

    Der Crawler-User-Agent verweist auf diese Seite (Transparenz gegenüber
    RIS-Betreibern); via Django-View vor dem Wagtail-Catch-all registriert.
    """
    return render(request, "marketing/crawler.html")


@require_http_methods(["GET", "HEAD"])
def security_txt(request):
    """Serves /.well-known/security.txt according to RFC 9116.

    Standardized location for security researchers to find disclosure
    contact information. Must be served as text/plain over HTTPS.

    Format reference: https://www.rfc-editor.org/rfc/rfc9116
    """
    site_url = (getattr(settings, "SITE_URL", "") or "https://mandari.de").rstrip("/")

    # Expiration date — RFC 9116 requires this. Fixed date, aligned with the
    # published PGP key (valid until 07/2028); regenerate before expiry.
    expires = "2027-07-31T00:00:00.000Z"

    body = f"""# Mandari Security Disclosure
# RFC 9116 — https://www.rfc-editor.org/rfc/rfc9116

Contact: mailto:security@mandari.de
Contact: {site_url}/sicherheit/disclosure/
Expires: {expires}
Encryption: {site_url}/wstatic/security/mandari-pgp-key.asc
Preferred-Languages: de, en
Canonical: {site_url}/.well-known/security.txt
Policy: {site_url}/sicherheit/disclosure/
Acknowledgments: {site_url}/sicherheit/disclosure/#hall-of-fame

# PGP-Fingerprint: 5D06 A2BC B71C 6095 7A23 0BD8 7E96 93FD 0505 3234
# Eingangsbestätigung innerhalb von 3 Werktagen, erste Einschätzung mit
# Schweregrad (CVSS 3.1) innerhalb von 7 Tagen, Zwischenstand spätestens
# nach zwei Wochen.
# Korrektur nach Schweregrad: kritisch innerhalb von 72 Stunden, hoch
# innerhalb von 7 Tagen, mittel innerhalb von 30 Tagen.
# Vollständige Offenlegung 90 Tage nach Veröffentlichung des Fixes, früher
# bei bereits ausgenutzten Lücken. Safe-Harbor für gutgläubige Forschung —
# siehe Policy. Fristen wie in
# https://github.com/mandariOSS/mandari/blob/main/SECURITY.md

# Andere Meldewege (RFC 2142):
#   abuse@mandari.de         — Spam, illegaler Content, Belästigung, Urheberrecht
#                              ({site_url}/abuse/)
#   privacy@mandari.de       — DSGVO-Anfragen, Auskunft, Löschung
#   legal@mandari.de         — Behörden-Anfragen, Rechtliches
#   conduct@mandari.de       — Code-of-Conduct-Verstöße in der Community
#   barrierefreiheit@mandari.de — BFSG-Feedback ({site_url}/barrierefreiheit/)
#   postmaster@mandari.de    — E-Mail-Probleme
"""
    return HttpResponse(body, content_type="text/plain; charset=utf-8")
