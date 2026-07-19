"""
Marketing-specific Django views.

Most marketing pages are rendered by Wagtail. This module is reserved for
pages that need server-side data fetching beyond a simple template — e.g.
the live system-status page, which pulls data from the Kener API.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import logging
import secrets
from typing import Any

import httpx
from django.conf import settings
from django.core.cache import cache
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


# ─────────────────────────── Kener (Status-Page Integration) ─────────────────

KENER_CACHE_KEY = "kener:monitors:v2"
KENER_CACHE_TTL = 60  # seconds — uptime windows pull a lot of data, cache longer
KENER_UPTIME_WINDOW_S = 24 * 3600  # uptime is computed over the last 24 hours


def _fetch_kener_status() -> dict[str, Any] | None:
    """Fetch live monitor status from the local Kener instance.

    Returns a normalized dict the template can render directly:

        {
          "available": True,
          "overall":   "UP" | "DEGRADED" | "DOWN" | "UNKNOWN",
          "summary":   {"up": N, "degraded": N, "down": N, "unknown": N},
          "monitors":  [{"name": str, "status": str, "tag": str, "uptime": float|None}, …],
        }

    Returns ``None`` when Kener is not configured or unreachable — the
    template falls back to a "open status page directly" card.
    """
    cached = cache.get(KENER_CACHE_KEY)
    if cached is not None:
        return cached or None  # negative-cache value is False/None

    token = getattr(settings, "KENER_API_TOKEN", "") or ""
    base = (getattr(settings, "KENER_INTERNAL_URL", "") or "").rstrip("/")
    if not token or not base:
        return None

    monitors_url = f"{base}/api/v4/monitors"
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}

    # Kener splits "what monitors exist" (cheap) from "monitoring history per
    # monitor" (one call per monitor). We do both in a single httpx client to
    # reuse the TCP connection.
    import time

    now_ts = int(time.time())
    start_ts = now_ts - KENER_UPTIME_WINDOW_S  # 24h window

    try:
        with httpx.Client(timeout=5.0, headers=headers) as client:
            list_resp = client.get(monitors_url)
            list_resp.raise_for_status()
            list_payload = list_resp.json()
            raw_monitors = (
                list_payload if isinstance(list_payload, list) else list_payload.get("monitors", [])
            )

            monitors: list[dict[str, Any]] = []
            for entry in raw_monitors:
                if not isinstance(entry, dict):
                    continue
                tag = entry.get("tag", "")
                if not tag or entry.get("is_hidden") == "YES":
                    continue

                live_status = "UNKNOWN"
                latency = None
                uptime_pct: float | None = None
                sample_count = 0

                try:
                    data_resp = client.get(
                        f"{base}/api/v4/monitors/{tag}/data",
                        params={"start_ts": start_ts, "end_ts": now_ts},
                    )
                    if data_resp.status_code == 200:
                        data_payload = data_resp.json()
                        points = (
                            data_payload
                            if isinstance(data_payload, list)
                            else data_payload.get("data", [])
                        )
                        if points:
                            # Most recent point = current status
                            latest = max(points, key=lambda p: p.get("timestamp", 0))
                            live_status = str(latest.get("status", "UNKNOWN")).upper()
                            latency = latest.get("latency")

                            # Uptime % over the window — Kener's default formula:
                            #   (UP + MAINTENANCE) / (UP + MAINTENANCE + DOWN + DEGRADED)
                            # Points with status outside these are ignored (e.g.
                            # PAUSED, missing data — treated as "no signal").
                            counted = 0
                            up_like = 0
                            for p in points:
                                s = str(p.get("status", "")).upper()
                                if s in ("UP", "MAINTENANCE"):
                                    up_like += 1
                                    counted += 1
                                elif s in ("DOWN", "DEGRADED", "WARN", "WARNING"):
                                    counted += 1
                            sample_count = counted
                            if counted:
                                uptime_pct = (up_like / counted) * 100.0
                except httpx.HTTPError:
                    pass  # leave defaults — partial data is acceptable

                monitors.append(
                    {
                        "name": entry.get("name") or tag,
                        "status": live_status,
                        "tag": tag,
                        "latency": latency,
                        "uptime_pct": uptime_pct,
                        "sample_count": sample_count,
                        "description": entry.get("description", ""),
                        "category": entry.get("category_name", ""),
                    }
                )
    except (httpx.HTTPError, ValueError) as exc:
        logger.warning("Kener API call failed (%s): %s", monitors_url, exc)
        # Negative cache for a short window to avoid hammering during outages
        cache.set(KENER_CACHE_KEY, False, 10)
        return None

    counts = {"up": 0, "degraded": 0, "down": 0, "unknown": 0}
    for monitor in monitors:
        status = monitor["status"]
        if status == "UP":
            counts["up"] += 1
        elif status in ("DEGRADED", "WARN", "WARNING"):
            counts["degraded"] += 1
        elif status == "DOWN":
            counts["down"] += 1
        else:
            counts["unknown"] += 1

    # Overall uptime = average of monitor uptimes that have data
    monitors_with_uptime = [m["uptime_pct"] for m in monitors if m["uptime_pct"] is not None]
    overall_uptime_pct = (
        sum(monitors_with_uptime) / len(monitors_with_uptime) if monitors_with_uptime else None
    )

    if counts["down"]:
        overall = "DOWN"
    elif counts["degraded"]:
        overall = "DEGRADED"
    elif counts["up"]:
        overall = "UP"
    else:
        overall = "UNKNOWN"

    data = {
        "available": True,
        "overall": overall,
        "summary": counts,
        "monitors": monitors,
        "uptime_pct": overall_uptime_pct,
        "uptime_window_hours": KENER_UPTIME_WINDOW_S // 3600,
    }
    cache.set(KENER_CACHE_KEY, data, KENER_CACHE_TTL)
    return data


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

# Sitemap (sitemaps.org)
Sitemap: {site_url}/sitemap.xml
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
Encryption: {site_url}/static/security/mandari-pgp-key.asc
Preferred-Languages: de, en
Canonical: {site_url}/.well-known/security.txt
Policy: {site_url}/sicherheit/disclosure/
Acknowledgments: {site_url}/sicherheit/disclosure/#hall-of-fame

# PGP-Fingerprint: 5D06 A2BC B71C 6095 7A23 0BD8 7E96 93FD 0505 3234
# Eingangsbestätigung innerhalb von 5 Werktagen, Erstbewertung innerhalb
# von 14 Tagen. Koordinierte Veröffentlichung in der Regel nach spätestens
# 90 Tagen. Safe-Harbor für gutgläubige Forschung — siehe Policy.

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


def status_view(request):
    """Public system-status page.

    Server-side renders Kener data so we never depend on iframes (which
    most browsers block via X-Frame-Options, CSP, or third-party-cookie
    rules). When the Kener API is not reachable, the template degrades
    gracefully to a prominent link to the live status page.
    """
    return render(
        request,
        "marketing/status.html",
        {
            "kener": _fetch_kener_status(),
            "STATUS_PAGE_URL": getattr(settings, "STATUS_PAGE_URL", ""),
        },
    )
