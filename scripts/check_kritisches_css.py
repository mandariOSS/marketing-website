"""
Kritisches CSS prüfen (CI, nach ``npm run build:css`` und den Seeds): ``python scripts/check_kritisches_css.py``

* ``static/css/kritisch.css`` existiert, bleibt unter der Größengrenze (gzip) und enthält keine ``url()`` (inline
  stünden sie ohne die Hashes von collectstatic) und kein ``</``.
* Jede Seite der Sitemap hat in ``<main>`` einen Seitenkopf (Klasse ``hero``); bis styles.css geladen ist, bleibt
  alles danach unsichtbar (static/css/erste-ansicht.css).
* Abdeckung: Jede Klasse, die in Kopfzeile oder Seitenkopf einer Seite steht und die styles.css gestaltet, steht
  auch im kritischen CSS. Sonst sähe die erste Ansicht vor styles.css anders aus und verschöbe sich danach (CLS).
  Ausgenommen sind das Innere der geschlossenen Menüs und der Fließtext (.prose) im Seitenkopf der Rechtstexte.

Fehlt eine Klasse: die Vorlage mit dem Seitenkopf in tailwind.kritisch.config.js eintragen oder, wenn Python oder
JavaScript die Klasse setzt, in IMMER in scripts/kritisches_css.js.
"""

import gzip
import os
import pathlib
import re
import sys
from html.parser import HTMLParser

WURZEL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

GRENZE_GZIP = 6_000  # Bytes; die erste Antwort soll mit dem HTML in die ersten TCP-Pakete passen
KRITISCH = WURZEL / "static/css/kritisch.css"
VOLL = WURZEL / "static/css/styles.css"
OHNE_IDS = {"produkte-menue", "mobilmenue"}  # geschlossene Menüs der Kopfzeile
OHNE_KLASSEN = {"prose"}  # Fließtext im Seitenkopf der Rechtstexte bleibt vorab unsichtbar
LEER = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


def klassen_im_css(css):
    """Klassennamen aus den Selektoren (nicht aus Werten wie 0.5rem), Maskierungen aufgelöst."""
    klassen = set()
    for selektor in re.findall(r"([^{}]+)\{", css):
        if selektor.lstrip().startswith("@"):
            continue
        for roh in re.findall(r"\.((?:\\[0-9a-fA-F]{1,6} ?|\\.|[\w-])+)", selektor):
            name = re.sub(r"\\([0-9a-fA-F]{1,6}) ?", lambda m: chr(int(m.group(1), 16)), roh)
            klassen.add(re.sub(r"\\(.)", r"\1", name))
    return klassen


class ErsteAnsicht(HTMLParser):
    """Klassen in Kopfzeile (header[role=banner]) und Seitenkopf (erstes .hero in <main>)."""

    def __init__(self):
        super().__init__()
        self.stapel = []  # (tag, "kopf"/"hero" oder None) je offenem Element
        self.klassen = set()
        self.in_main = False
        self.hero_gefunden = False

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        klassen = (a.get("class") or "").split()
        oben = self.stapel[-1][1] if self.stapel else None
        if tag == "main":
            self.in_main = True
        if tag == "header" and a.get("role") == "banner":
            zaehlt = "kopf"
        elif self.in_main and not self.hero_gefunden and "hero" in klassen:
            zaehlt, self.hero_gefunden = "hero", True
        else:
            zaehlt = oben
        if zaehlt and (a.get("id") in OHNE_IDS or OHNE_KLASSEN & set(klassen)):
            zaehlt = None
        if zaehlt:
            self.klassen.update(klassen)
        if tag not in LEER:
            self.stapel.append((tag, zaehlt))

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        for i in range(len(self.stapel) - 1, -1, -1):
            if self.stapel[i][0] == tag:
                del self.stapel[i:]
                break


def main():
    fehler = []
    if not KRITISCH.exists():
        sys.exit(f"{KRITISCH.relative_to(WURZEL)} fehlt – erst npm run build:css")
    kritisch = KRITISCH.read_text(encoding="utf-8")
    roh, gz = len(kritisch.encode()), len(gzip.compress(kritisch.encode(), 9))
    if gz > GRENZE_GZIP:
        fehler.append(
            f"kritisches CSS {gz} Bytes gzip (Grenze {GRENZE_GZIP}) – Vorlagen in tailwind.kritisch.config.js prüfen"
        )
    for verboten in ("url(", "</"):
        if verboten in kritisch:
            fehler.append(f"kritisches CSS enthält {verboten!r}")
    for pflicht in (".vorab", ".kopfleiste", ".hero-karte", ".t-h1", ".wrap", ".dark"):
        if pflicht not in kritisch:
            fehler.append(f"kritisches CSS ohne {pflicht}")

    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    os.environ.setdefault("ALLOWED_HOSTS", "testserver")
    import django

    django.setup()
    from django.test import Client
    from wagtail.models import Page

    im_vollen, im_kritischen = klassen_im_css(VOLL.read_text(encoding="utf-8")), klassen_im_css(kritisch)
    client = Client()
    urls = sorted({p.url for p in Page.objects.live().specific() if p.url})
    for url in urls:
        antwort = client.get(url)
        if antwort.status_code != 200:
            continue
        leser = ErsteAnsicht()
        leser.feed(antwort.content.decode("utf-8"))
        if not leser.hero_gefunden:
            fehler.append(f"{url}: kein Seitenkopf (class hero) in <main> – vor styles.css bliebe die Seite leer")
        fehlt = sorted(k for k in leser.klassen if k in im_vollen and k not in im_kritischen)
        if fehlt:
            fehler.append(f"{url}: Klassen der ersten Ansicht fehlen im kritischen CSS: {', '.join(fehlt)}")
    if fehler:
        sys.exit("Kritisches CSS:\n  " + "\n  ".join(fehler))
    print(f"OK: kritisches CSS {roh} Bytes ({gz} gzip, Grenze {GRENZE_GZIP}), {len(urls)} Seiten abgedeckt")


if __name__ == "__main__":
    main()
