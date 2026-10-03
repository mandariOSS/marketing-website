#!/usr/bin/env python
"""
Struktur-Test für mandari.de.

Läuft gegen eine migrierte und geseedete Datenbank (wie in der CI) und verfolgt
ausgehend von ``/`` alle internen Links mit dem Django-Test-Client. Fehler sind:

* interne Links, die mit 4xx/5xx antworten,
* veröffentlichte Seiten, die über keinen Link erreichbar sind („nicht verlinkt“),
  Unterseiten, die ihre Elternseite nicht verlinkt,
* doppelte oder falsch gebaute Seitentitel („<Titel> | mandari“),
  fehlende oder doppelte Meta-Descriptions, Canonicals, die nicht auf SITE_URL zeigen,
* Kopf- und Fußzeile, die von der Zielstruktur abweichen, oder Seiten, die sie
  nicht genau einmal enthalten; in der Kopfzeile außerdem „Bürgerportal“ genau
  einmal als direkter Link und der Knopf „Menü“ für das Slide-Menü (Dialog),
* Anker-Links (``/seite/#anker``) auf Abschnitte, die es nicht gibt.

Interne Links auf Weiterleitungen sind Warnungen: Sie funktionieren, sollten
aber auf das Ziel zeigen.

Aufruf (nach ``migrate``, ``setup_initial_pages`` und ``migrate_pages_to_streamfield``):

    SITE_URL=https://mandari.de python scripts/check_site_structure.py
    SITE_URL=https://mandari.de python scripts/check_site_structure.py --strict
"""

from __future__ import annotations

import argparse
import os
import sys
from collections import defaultdict, deque
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
os.environ.setdefault("ALLOWED_HOSTS", "testserver")

# ── Zielstruktur der Website ────────────────────────────────────────────────

PRODUKTE_MENUE = [
    ("Übersicht", "/produkte/"),
    ("Für Verwaltungen", "/kommunen/"),
    ("Für Fraktionen", "/fraktionen/"),
    ("Für Bürger:innen", "/produkte/#insight"),
    ("Roadmap", "/roadmap/"),
]
HAUPTMENUE = PRODUKTE_MENUE + [("Preise", "/preise/"), ("Unternehmen", "/unternehmen/"), ("Kontakt", "/kontakt/")]
BUERGERPORTAL = ("Bürgerportal", "/insight/")
ANMELDEN = ("Anmelden", "/work/")
PORTALE = [BUERGERPORTAL, ANMELDEN]
WORTMARKE = ("mandari.", "/")
# Reihenfolge im Quelltext: Wortmarke, Hauptmenü (Desktop), Portale, dann das Slide-Menü (mobil). Das
# Bürgerportal steht auch mobil in der Leiste und deshalb nur einmal in der Kopfzeile.
KOPFZEILE = [WORTMARKE] + HAUPTMENUE + PORTALE + HAUPTMENUE + [ANMELDEN]

FUSSZEILE = {
    "Produkte": [
        ("Übersicht", "/produkte/"),
        ("Für Verwaltungen", "/kommunen/"),
        ("Für Fraktionen", "/fraktionen/"),
        ("Für Bürger:innen", "/produkte/#insight"),
        ("Umstieg", "/migration/"),
        ("Vergleich", "/vergleich/"),
        ("Roadmap", "/roadmap/"),
        ("Releases", "/releases/"),
    ],
    "Vertrauen": [
        ("Trust Center", "/trust/"),
        ("Vergabe und Unterlagen", "/vergabe/"),
        ("Transparenzbericht", "/transparenz/"),
        ("Barrierefreiheit", "/barrierefreiheit/"),
        ("Sicherheitslücke melden", "/sicherheit/disclosure/"),
        ("Missbrauch melden", "/abuse/"),
        ("Status", "https://status.mandari.de/"),
    ],
    "Unternehmen": [
        ("Über mandari", "/unternehmen/"),
        ("Partner", "/partner/"),
        ("Presse", "/presse/"),
        ("Open Source", "/open-source/"),
        ("Mitmachen", "/mitmachen/"),
    ],
    "Hilfe": [
        ("Dokumentation", "https://docs.mandari.de/"),
        ("Kontakt", "/kontakt/"),
    ],
    "Rechtliches": [
        ("Impressum", "/impressum/"),
        ("Datenschutz", "/datenschutz/"),
        ("AGB", "/agb/"),
        ("AVV", "/avv/"),
        ("Quellennachweise", "/quellen/"),
        ("Verträge hier kündigen", "/kuendigung/"),
    ],
}

STARTSEITE_TITEL = "mandari – Software für die offene Verwaltung"

# TODO(Relaunch-Abnahme): Diese Ziele legen die parallelen Relaunch-PRs an (Produkte/Fraktionen,
# Unternehmen/Karriere, neue Startseite). Solange sie fehlen, meldet der Test Warnungen statt Fehler.
# Nach dem Merge aller Relaunch-PRs die Mengen leeren (oder in der CI mit --strict aufrufen).
AUSSTEHENDE_PFADE = {"/produkte/", "/fraktionen/", "/unternehmen/"}
# Seiten, die die Relaunch-PRs mit `retire_page` zurückziehen; bis dahin dürfen sie unverlinkt sein.
AUSSTEHENDE_RUECKZUEGE = {"/ueber-uns/", "/produkt/"}
AUSSTEHEND_STARTSEITENTITEL = True

# Pfade, die in Produktion die mandari-Anwendung bedient (nicht diese Website).
ANWENDUNGS_PFADE = ("/insight/", "/work/", "/session/", "/api/", "/accounts/")
NICHT_PRUEFEN = ("/wstatic/", "/media/", "/documents/", "/cms-admin/", "/django-admin/", "/admin/")
# Django-Seiten außerhalb des Wagtail-Baums, die erreichbar sein müssen.
PFLICHT_PFADE = ["/sicherheit/disclosure/", "/crawler/"]
ALTER_PLATZHALTER = "Kommunalpolitische Transparenz"


class SeitenParser(HTMLParser):
    """Sammelt Titel, Meta-Angaben, Links, IDs sowie Kopf- und Fußzeilen-Einträge."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = None
        self.canonical = None
        self.links: list[tuple[str, str]] = []
        self.ids: set[str] = set()
        self.banner_count = 0
        self.contentinfo_count = 0
        self.header_links: list[tuple[str, str]] = []
        self.footer_links: list[tuple[str, str]] = []
        self.footer_headings: list[str] = []
        self.header_buttons: list[tuple[str, dict]] = []
        self.header_dialogs: list[dict] = []
        self._in_title = False
        self._region_stack: list[str | None] = []
        self._anchor: dict | None = None
        self._button: dict | None = None
        self._heading: list[str] | None = None

    @property
    def _region(self):
        for region in reversed(self._region_stack):
            if region:
                return region
        return None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if attrs.get("id"):
            self.ids.add(attrs["id"])
        if tag == "title":
            self._in_title = True
        elif tag == "meta" and attrs.get("name") == "description":
            self.description = attrs.get("content", "")
        elif tag == "link" and attrs.get("rel") == "canonical":
            self.canonical = attrs.get("href", "")
        if tag in ("header", "footer"):
            role = attrs.get("role")
            region = {"banner": "kopf", "contentinfo": "fuss"}.get(role)
            if role == "banner":
                self.banner_count += 1
            if role == "contentinfo":
                self.contentinfo_count += 1
            self._region_stack.append(region)
        if tag == "a" and attrs.get("href") is not None:
            self._anchor = {"href": attrs["href"], "text": []}
        if tag == "button" and self._region == "kopf":
            self._button = {"attrs": attrs, "text": []}
        if attrs.get("role") == "dialog" and self._region == "kopf":
            self.header_dialogs.append(attrs)
        if tag == "h2" and self._region == "fuss":
            self._heading = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False
        elif tag in ("header", "footer") and self._region_stack:
            self._region_stack.pop()
        elif tag == "a" and self._anchor is not None:
            entry = (" ".join("".join(self._anchor["text"]).split()), self._anchor["href"])
            self.links.append(entry)
            if self._region == "kopf":
                self.header_links.append(entry)
            elif self._region == "fuss":
                self.footer_links.append(entry)
            self._anchor = None
        elif tag == "button" and self._button is not None:
            self.header_buttons.append((" ".join("".join(self._button["text"]).split()), self._button["attrs"]))
            self._button = None
        elif tag == "h2" and self._heading is not None:
            self.footer_headings.append(" ".join("".join(self._heading).split()))
            self._heading = None

    def handle_data(self, data):
        if self._in_title:
            self.title += data
        if self._anchor is not None:
            self._anchor["text"].append(data)
        if self._button is not None:
            self._button["text"].append(data)
        if self._heading is not None:
            self._heading.append(data)


def abweichung(ist, soll) -> str:
    """Kurze Beschreibung, wie eine Linkliste von der Zielstruktur abweicht."""
    fehlt = [eintrag for eintrag in soll if eintrag not in ist]
    zusaetzlich = [eintrag for eintrag in ist if eintrag not in soll]
    teile = []
    if fehlt:
        teile.append(f"fehlt {fehlt}")
    if zusaetzlich:
        teile.append(f"zusätzlich {zusaetzlich}")
    return "; ".join(teile) or "Reihenfolge oder Anzahl weicht ab"


class Bericht:
    def __init__(self, strict: bool):
        self.strict = strict
        self.fehler: list[str] = []
        self.warnungen: list[str] = []

    def fehler_(self, text):
        self.fehler.append(text)

    def warnung(self, text):
        self.warnungen.append(text)

    def ausstehend(self, text):
        (self.fehler if self.strict else self.warnungen).append(text + " (ausstehend)")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--strict", action="store_true", help="Ausstehende Ziele der Relaunch-PRs als Fehler werten")
    args = parser.parse_args()

    import django

    django.setup()

    import logging

    logging.getLogger("django.request").setLevel(logging.CRITICAL)

    from django.conf import settings
    from django.test import Client
    from wagtail.models import Site

    from marketing import seo

    bericht = Bericht(strict=args.strict)
    ausstehend = set(AUSSTEHENDE_PFADE)
    struktur_hrefs = {href for _, href in KOPFZEILE} | {
        href for eintraege in FUSSZEILE.values() for _, href in eintraege
    }
    site_url = seo.site_url()
    interne_hosts = {urlsplit(site_url).netloc, "mandari.de", "www.mandari.de", "testserver"}
    status_url = getattr(settings, "STATUS_PAGE_URL", "https://status.mandari.de/")
    fusszeile = {
        name: [(label, status_url if label == "Status" else href) for label, href in eintraege]
        for name, eintraege in FUSSZEILE.items()
    }

    def normalisieren(href: str, aktuell: str):
        """→ (pfad, anker) für interne Seitenlinks, sonst None."""
        href = (href or "").strip()
        if not href or href.startswith(("mailto:", "tel:", "javascript:")):
            return None
        parts = urlsplit(urljoin("https://intern" + aktuell, href) if not urlsplit(href).scheme else href)
        if parts.scheme in ("http", "https") and parts.netloc not in interne_hosts | {"intern"}:
            return None
        pfad = parts.path or "/"
        if pfad.startswith(NICHT_PRUEFEN) or pfad.startswith(ANWENDUNGS_PFADE):
            return None
        return pfad, parts.fragment

    client = Client()
    warteschlange = deque(["/"])
    gesehen: set[str] = set()
    seiten: dict[str, SeitenParser] = {}
    weiterleitungen: dict[str, str] = {}
    verweise: dict[str, set[str]] = defaultdict(set)
    anker: list[tuple[str, str, str, str]] = []
    fehlerhaft: dict[str, int] = {}

    while warteschlange:
        pfad = warteschlange.popleft()
        if pfad in gesehen:
            continue
        gesehen.add(pfad)
        antwort = client.get(pfad)
        if 300 <= antwort.status_code < 400:
            ziel = antwort.get("Location", "")
            weiterleitungen[pfad] = ziel
            ziel_intern = normalisieren(ziel, pfad)
            if ziel_intern:
                warteschlange.append(ziel_intern[0])
            continue
        if antwort.status_code != 200:
            fehlerhaft[pfad] = antwort.status_code
            continue
        if not antwort.get("Content-Type", "").startswith("text/html"):
            continue
        html = SeitenParser()
        html.feed(antwort.content.decode("utf-8"))
        seiten[pfad] = html
        for _, href in html.links:
            ziel = normalisieren(href, pfad)
            if ziel is None:
                continue
            ziel_pfad, fragment = ziel
            if ziel_pfad != pfad:
                verweise[ziel_pfad].add(pfad)
            if fragment:
                anker.append((pfad, ziel_pfad, fragment, href))
            if ziel_pfad not in gesehen:
                warteschlange.append(ziel_pfad)

    def von_liste(pfad):
        quellen = sorted(verweise.get(pfad, ())) or ["Start"]
        return ", ".join(quellen[:5]) + (f" und {len(quellen) - 5} weiteren" if len(quellen) > 5 else "")

    # ── Interne Links auf Fehlerseiten ───────────────────────────────────────
    for pfad, status in sorted(fehlerhaft.items()):
        meldung = f"{pfad}: HTTP {status} (verlinkt von {von_liste(pfad)})"
        if pfad in ausstehend:
            bericht.ausstehend(meldung)
        else:
            bericht.fehler_(meldung)

    # ── Weiterleitungen, die noch verlinkt sind ──────────────────────────────
    for alt, ziel in sorted(weiterleitungen.items()):
        if verweise.get(alt):
            bericht.warnung(f"Link auf Weiterleitung {alt} → {ziel} (verlinkt von {von_liste(alt)})")

    # ── Anker ────────────────────────────────────────────────────────────────
    # Anker aus Kopf- und Fußzeile sind Pflicht, Anker im Seiteninhalt melden wir als Warnung.
    gemeldet = set()
    for von, ziel_pfad, fragment, href in anker:
        ziel_seite = seiten.get(ziel_pfad)
        if ziel_seite is None or fragment in ziel_seite.ids or (ziel_pfad, fragment) in gemeldet:
            continue
        gemeldet.add((ziel_pfad, fragment))
        meldung = f"Anker #{fragment} fehlt auf {ziel_pfad} (verlinkt von {von})"
        if href in struktur_hrefs:
            bericht.fehler_(meldung)
        else:
            bericht.warnung(meldung)

    # ── Erreichbarkeit aller veröffentlichten Seiten ─────────────────────────
    site = Site.objects.select_related("root_page").get(is_default_site=True)
    veroeffentlicht = {}
    for page in site.root_page.get_descendants(inclusive=True).live().public().specific():
        url_teile = page.get_url_parts()
        if url_teile:
            veroeffentlicht[url_teile[2]] = page
    for pfad, page in sorted(veroeffentlicht.items()):
        if pfad not in seiten:
            meldung = f"{pfad}: veröffentlicht, aber nicht verlinkt ({page.title})"
            if pfad in AUSSTEHENDE_RUECKZUEGE:
                bericht.ausstehend(meldung + " – wird mit retire_page zurückgezogen")
            else:
                bericht.fehler_(meldung)
            continue
        if page.depth > site.root_page.depth + 1:
            eltern = page.get_parent().specific
            eltern_pfad = eltern.get_url_parts()[2]
            if eltern_pfad not in verweise.get(pfad, set()):
                bericht.fehler_(f"{pfad}: nicht von der Elternseite {eltern_pfad} verlinkt")
    for pfad in PFLICHT_PFADE:
        if pfad not in seiten:
            bericht.fehler_(f"{pfad}: nicht verlinkt oder nicht erreichbar")

    # ── Titel, Beschreibung, Canonical ───────────────────────────────────────
    struktur: dict[str, list[str]] = defaultdict(list)
    titel: dict[str, list[str]] = defaultdict(list)
    beschreibungen: dict[str, list[str]] = defaultdict(list)
    for pfad, html in sorted(seiten.items()):
        t = " ".join(html.title.split())
        titel[t].append(pfad)
        if pfad == "/":
            if t != STARTSEITE_TITEL:
                meldung = f"/: Titel '{t}' statt '{STARTSEITE_TITEL}'"
                if AUSSTEHEND_STARTSEITENTITEL:
                    bericht.ausstehend(meldung)
                else:
                    bericht.fehler_(meldung)
        elif not t.endswith(" | mandari") or seo.clean_title(t[: -len(" | mandari")]) != t[: -len(" | mandari")]:
            bericht.fehler_(f"{pfad}: Titel '{t}' hat nicht die Form '<Titel> | mandari'")
        if "Mandari" in t:
            bericht.fehler_(f"{pfad}: Titel '{t}' schreibt die Marke groß")

        d = " ".join((html.description or "").split())
        if not d:
            bericht.fehler_(f"{pfad}: Meta-Description fehlt")
        elif d == ALTER_PLATZHALTER or d.startswith("Mandari - "):
            bericht.fehler_(f"{pfad}: Meta-Description ist ein Platzhalter ('{d}')")
        else:
            beschreibungen[d].append(pfad)

        erwartet = seo.absolute_url(pfad)
        if html.canonical != erwartet:
            bericht.fehler_(f"{pfad}: Canonical '{html.canonical}' statt '{erwartet}'")

        # ── Kopf- und Fußzeile ──────────────────────────────────────────────
        if html.banner_count != 1 or html.contentinfo_count != 1:
            struktur[
                f"Kopfzeile {html.banner_count}×, Fußzeile {html.contentinfo_count}× statt je genau einmal"
            ].append(pfad)
            continue
        if html.header_links != KOPFZEILE:
            meldung = f"Kopfzeile weicht von der Zielstruktur ab: {abweichung(html.header_links, KOPFZEILE)}"
            struktur[meldung].append(pfad)
        produkte = [attrs for text, attrs in html.header_buttons if text == "Produkte"]
        if len(produkte) != 1 or "aria-expanded" not in produkte[0] or "aria-controls" not in produkte[0]:
            struktur["Kopfzeile ohne Aufklappknopf 'Produkte' mit aria-expanded und aria-controls"].append(pfad)
        if [eintrag for eintrag in html.header_links if eintrag[0] == BUERGERPORTAL[0]] != [BUERGERPORTAL]:
            struktur["Kopfzeile: 'Bürgerportal' nicht genau einmal als direkter Link auf /insight/"].append(pfad)
        menue = [attrs for text, attrs in html.header_buttons if text == "Menü"]
        dialoge = {attrs.get("id"): attrs for attrs in html.header_dialogs}
        dialog = dialoge.get(menue[0].get("aria-controls")) if len(menue) == 1 else None
        if (
            dialog is None
            or "aria-expanded" not in menue[0]
            or dialog.get("aria-modal") != "true"
            or not (dialog.get("aria-label") or dialog.get("aria-labelledby"))
        ):
            struktur[
                "Kopfzeile ohne Knopf 'Menü' (aria-expanded, aria-controls) für ein beschriftetes Slide-Menü "
                "mit role=dialog und aria-modal=true"
            ].append(pfad)
        erwartet_fuss = [WORTMARKE] + [eintrag for eintraege in fusszeile.values() for eintrag in eintraege]
        if html.footer_headings != list(fusszeile):
            struktur[f"Fußzeile: Spalten {html.footer_headings} statt {list(fusszeile)}"].append(pfad)
        if html.footer_links != erwartet_fuss:
            meldung = f"Fußzeile weicht von der Zielstruktur ab: {abweichung(html.footer_links, erwartet_fuss)}"
            struktur[meldung].append(pfad)

    for meldung, pfade in struktur.items():
        bericht.fehler_(f"{meldung} (auf {len(pfade)} Seiten, z. B. {', '.join(pfade[:3])})")
    for t, pfade in titel.items():
        if len(pfade) > 1:
            bericht.fehler_(f"doppelter Titel '{t}': {', '.join(pfade)}")
    for d, pfade in beschreibungen.items():
        if len(pfade) > 1:
            bericht.fehler_(f"doppelte Meta-Description '{d[:60]}…': {', '.join(pfade)}")

    # ── Ergebnis ─────────────────────────────────────────────────────────────
    for text in bericht.warnungen:
        print(f"WARNUNG: {text}")
    for text in bericht.fehler:
        print(f"FEHLER: {text}")
    print(
        f"{len(seiten)} Seiten geprüft, {len(veroeffentlicht)} veröffentlichte Wagtail-Seiten, "
        f"{len(weiterleitungen)} Weiterleitungen, {len(bericht.warnungen)} Warnungen, {len(bericht.fehler)} Fehler"
    )
    return 1 if bericht.fehler else 0


if __name__ == "__main__":
    sys.exit(main())
