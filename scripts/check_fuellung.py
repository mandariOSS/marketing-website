#!/usr/bin/env python3
"""
Gestaltungssystem: keine leere rechte Hälfte (Musterkatalog, Regel 6).

Misst bei 1440 px Breite jeden Abschnitt (jedes direkte Kind von <main>, außer dem Seitenkopf): Wie weit
reicht der Inhalt nach rechts, in Prozent der Rasterbreite (``.wrap`` ohne Innenabstand)? Text, der schmal
bleiben muss, bekommt eine Randspalte oder ein Bild; sonst geht das Layout über die volle Breite. Ein
Abschnitt unter MINDESTENS Prozent ist ein Fehler.

Aufruf (Server läuft, z. B. ``python manage.py runserver 8191``):
    python scripts/check_fuellung.py                       # alle Seiten aus der Sitemap
    python scripts/check_fuellung.py /vergabe/ /presse/    # einzelne Seiten
Umgebung: BASE_URL (Standard http://127.0.0.1:8191), MINDESTENS (Standard 80).
Braucht Playwright mit Chromium (``pip install playwright && python -m playwright install chromium``).
"""

from __future__ import annotations

import os
import re
import sys
import urllib.request

from playwright.sync_api import sync_playwright

BASE_URL = os.environ.get("BASE_URL", "http://127.0.0.1:8191").rstrip("/")
MINDESTENS = int(os.environ.get("MINDESTENS", "80"))
ZUSATZ = ["/sicherheit/disclosure/", "/crawler/"]

MESSUNG = r"""
() => {
  const sichtbar = el => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const inhalt = 'p,h1,h2,h3,h4,li,img,svg,table,a,button,dd,dt,td,th,figure,pre,input,textarea,select,blockquote,picture,video,iframe';
  const main = document.querySelector('main');
  return [...main.children].filter(sichtbar).map((band, i) => {
    const wrap = band.classList.contains('wrap') ? band : band.querySelector('.wrap');
    const titel = (band.querySelector('h1,h2') || band).innerText.trim().replace(/\s+/g, ' ').slice(0, 70);
    if (!wrap) return {i, titel, kopf: band.classList.contains('hero'), fuellung: null};
    const r = wrap.getBoundingClientRect(), s = getComputedStyle(wrap);
    const links = r.left + parseFloat(s.paddingLeft), breite = r.width - parseFloat(s.paddingLeft) - parseFloat(s.paddingRight);
    let rechts = links;
    for (const el of band.querySelectorAll(inhalt)) {
      if (!sichtbar(el) || el.closest('[aria-hidden="true"]') && !el.closest('.zk')) continue;
      rechts = Math.max(rechts, el.getBoundingClientRect().right);
    }
    return {i, titel, kopf: band.classList.contains('hero') && !band.querySelector('h2'), fuellung: Math.round(100 * (rechts - links) / breite)};
  });
}
"""


def seiten():
    if len(sys.argv) > 1:
        return sys.argv[1:]
    xml = urllib.request.urlopen(f"{BASE_URL}/sitemap.xml").read().decode()
    pfade = [re.sub(r"^https?://[^/]+", "", u) or "/" for u in re.findall(r"<loc>([^<]+)</loc>", xml)]
    return sorted(set(pfade + ZUSATZ))


def main():
    fehler, gemessen = [], 0
    with sync_playwright() as pw:
        browser = pw.chromium.launch()
        seite = browser.new_page(viewport={"width": 1440, "height": 900})
        for pfad in seiten():
            antwort = seite.goto(BASE_URL + pfad, wait_until="load")
            if not antwort or antwort.status != 200:
                continue
            for abschnitt in seite.evaluate(MESSUNG):
                if abschnitt["kopf"] or abschnitt["fuellung"] is None:
                    continue
                gemessen += 1
                if abschnitt["fuellung"] < MINDESTENS:
                    fehler.append(f"{pfad} #{abschnitt['i']} „{abschnitt['titel']}“: {abschnitt['fuellung']} %")
        browser.close()
    if fehler:
        print(f"Leere rechte Hälfte (Inhalt endet vor {MINDESTENS} % der Rasterbreite bei 1440 px):")
        print("\n".join(f"  {f}" for f in fehler))
        sys.exit(1)
    print(f"OK: {gemessen} Abschnitte füllen mindestens {MINDESTENS} % der Rasterbreite")


if __name__ == "__main__":
    main()
