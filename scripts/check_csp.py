#!/usr/bin/env python3
"""
Content-Security-Policy im Browser prüfen: keine Verstöße auf irgendeiner Seite.

Öffnet jede Seite der Sitemap (dazu Disclosure, Crawler und eine 404-Seite) in Chromium und sammelt jeden Verstoß gegen
die Policy (Ereignis ``securitypolicyviolation``; im Report-Modus meldet der Browser, statt zu blockieren). Auf
/kontakt/ betritt das Skript ein Formularfeld, damit der Spamschutz (Altcha: Stil, Worker, Abruf der Aufgabe) lädt
und rechnet. Außerdem: Kopfzeilen ``Permissions-Policy`` und CSP vorhanden, keine Fehlermeldung des Browsers zur
Permissions-Policy (unbekannte Funktionen landen als Fehler in der Konsole).

Jeder Verstoß hier ginge im Betrieb mit jedem Seitenaufruf als Meldung an /csp-report/ – und bräche die Seite, sobald
CSP_MODUS=scharf gilt. Neuer Inline-Code gehört in ``{% csp_inline %}`` (marketing/sicherheit.py).

Aufruf (Server läuft, am besten wie im Betrieb ohne DEBUG, damit das kritische CSS inline steht):
    python scripts/check_csp.py                      # alle Seiten aus der Sitemap
    python scripts/check_csp.py /kontakt/ /preise/   # einzelne Seiten
Umgebung: BASE_URL (Standard http://127.0.0.1:8191).
Braucht Playwright mit Chromium (``pip install playwright && python -m playwright install chromium``).
"""

from __future__ import annotations

import os
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8191").rstrip("/")
ZUSATZ = ["/sicherheit/disclosure/", "/crawler/", "/gibt-es-nicht/"]
CSP_HEADER = ("content-security-policy", "content-security-policy-report-only")

MITSCHNITT = """
window.__csp = [];
document.addEventListener("securitypolicyviolation", (e) => {
  window.__csp.push({richtlinie: e.violatedDirective, blockiert: e.blockedURI, quelle: e.sourceFile,
                     zeile: e.lineNumber, auszug: e.sample});
});
"""


def seiten():
    if len(sys.argv) > 1:
        return sys.argv[1:]
    xml = urllib.request.urlopen(f"{BASE_URL}/sitemap.xml").read().decode()
    pfade = [re.sub(r"^https?://[^/]+", "", u) or "/" for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
    return sorted(set(pfade + ZUSATZ))


def main():
    fehler = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        kontext = browser.new_context(viewport={"width": 1440, "height": 900})
        kontext.add_init_script(MITSCHNITT)
        for pfad in seiten():
            seite = kontext.new_page()
            konsole = []
            seite.on("console", lambda m, k=konsole: k.append(m.text) if m.type == "error" else None)
            antwort = seite.goto(BASE_URL + pfad, wait_until="load")
            kopf = {k.lower(): v for k, v in antwort.all_headers().items()}
            if "permissions-policy" not in kopf:
                fehler.append(f"{pfad}: Permissions-Policy fehlt")
            if not any(h in kopf for h in CSP_HEADER):
                fehler.append(f"{pfad}: Content-Security-Policy fehlt")
            if pfad.startswith("/kontakt/") and seite.locator("form input[name=name]").count():
                seite.locator("form input[name=name]").first.focus()
                # Altcha lädt beim ersten Fokus und rechnet im Worker; fertig, wenn das Widget „verified“ meldet
                seite.wait_for_function(
                    "() => [...document.querySelectorAll('altcha-widget')].some("
                    "w => typeof w.getState === 'function' && w.getState() === 'verified')",
                    timeout=20_000,
                )
            seite.wait_for_timeout(300)
            for v in seite.evaluate("window.__csp"):
                fehler.append(
                    f"{pfad}: Verstoß gegen {v['richtlinie']} – {v['blockiert'] or 'inline'} "
                    f"({v['quelle']}:{v['zeile']}) {v['auszug'] or ''}".rstrip()
                )
            fehler += [f"{pfad}: Konsole: {t}" for t in konsole if "Permissions-Policy" in t]
            seite.close()
        browser.close()
    if fehler:
        sys.exit("Content-Security-Policy:\n  " + "\n  ".join(fehler))
    print(f"OK: {len(seiten())} Seiten ohne Verstoß gegen die Content-Security-Policy")


if __name__ == "__main__":
    main()
