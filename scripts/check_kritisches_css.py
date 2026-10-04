"""
Kritisches CSS prüfen (CI, nach ``npm run build:css`` und den Seeds): ``python scripts/check_kritisches_css.py``

* ``static/css/kritisch.css`` existiert, bleibt unter der Größengrenze (gzip) und enthält keine ``url()`` (inline
  stünden sie ohne die Hashes von collectstatic) und kein ``</``.
* Jede Seite der Sitemap hat in ``<main>`` einen Seitenkopf (Klasse ``hero``); bis styles.css geladen ist, bleibt
  alles danach unsichtbar (static/css/erste-ansicht.css).
* Abdeckung: Jede Klasse, die in Kopfzeile oder Seitenkopf einer Seite steht und die styles.css für das erste Bild
  gestaltet (nicht nur für Zeiger, Fokus oder Übergänge), steht auch im kritischen CSS. Sonst sähe die erste Ansicht
  vor styles.css anders aus und verschöbe sich danach (CLS). Ausgenommen ist, was vorab ausgeblendet bleibt: das
  Innere der geschlossenen Menüs, Fließtext (.prose) und auf Dokumentseiten alles nach dem <header> des Seitenkopfs.
* Die HTML-Antworten von Startseite und /kontakt/ bleiben mit dem kritischen CSS unter GRENZE_HTML (gzip), damit
  sie in die ersten TCP-Pakete passen.

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
# HTML mit kritischem CSS (gzip wie Caddy): Bis 10 × 1460 Bytes einschließlich der Kopfzeilen der Antwort (rund
# 600–900 Bytes) kommt es in der ersten Runde; jede weitere kostet am Handy rund 150 ms bis zum ersten Bild.
GRENZE_HTML = 13_800
SEITEN_HTML = ("/", "/kontakt/")
KRITISCH = WURZEL / "static/css/kritisch.css"
VOLL = WURZEL / "static/css/styles.css"
OHNE_IDS = {"produkte-menue", "mobilmenue"}  # geschlossene Menüs der Kopfzeile
OHNE_KLASSEN = {"prose"}  # Fließtext im Seitenkopf bleibt vorab unsichtbar
LEER = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}


# Wie scripts/kritisches_css.js: Zustände durch Bedienen und reine Übergänge braucht das erste Zeichnen nicht.
ZUSTAND = re.compile(r":hover|:focus|:active|::backdrop|\[aria-expanded=true\]")
NUR_UEBERGANG = re.compile(r"^(?:\s*(?:transition|animation)[\w-]*\s*:[^;]*;?)*\s*$")


def _teile(selektor):
    """Selektorliste an Kommas außerhalb von Klammern trennen."""
    teile, tiefe, start = [], 0, 0
    for i, zeichen in enumerate(selektor):
        tiefe += {"(": 1, "[": 1, ")": -1, "]": -1}.get(zeichen, 0)
        if zeichen == "," and tiefe == 0:
            teile.append(selektor[start:i])
            start = i + 1
    return teile + [selektor[start:]]


def klassen_im_css(css, erstes_bild=False):
    """Klassennamen aus den Selektoren (nicht aus Werten wie 0.5rem), Maskierungen aufgelöst. Mit ``erstes_bild``
    nur aus Regeln, die das erste Zeichnen betreffen."""
    klassen = set()
    for selektor, block in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        if selektor.lstrip().startswith("@") or (erstes_bild and NUR_UEBERGANG.match(block)):
            continue
        for teil in _teile(selektor):
            if erstes_bild and ZUSTAND.search(teil):
                continue
            for roh in re.findall(r"\.((?:\\[0-9a-fA-F]{1,6} ?|\\.|[\w-])+)", teil):
                name = re.sub(r"\\([0-9a-fA-F]{1,6}) ?", lambda m: chr(int(m.group(1), 16)), roh)
                klassen.add(re.sub(r"\\(.)", r"\1", name))
    return klassen


class ErsteAnsicht(HTMLParser):
    """Klassen in Kopfzeile (header[role=banner]) und Seitenkopf (erstes .hero in <main>)."""

    def __init__(self):
        super().__init__()
        self.stapel = []  # [tag, "kopf"/"hero" oder None, <header> als Kind geschlossen] je offenem Element
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
        if zaehlt == "hero" and self.stapel and self.stapel[-1][2]:
            zaehlt = None  # Geschwister nach dem <header> einer Dokumentseite (.hero header ~ *)
        if zaehlt:
            self.klassen.update(klassen)
        if tag not in LEER:
            self.stapel.append([tag, zaehlt, False])

    def handle_endtag(self, tag):
        if tag == "main":
            self.in_main = False
        for i in range(len(self.stapel) - 1, -1, -1):
            if self.stapel[i][0] == tag:
                if tag == "header" and self.stapel[i][1] == "hero" and i:
                    self.stapel[i - 1][2] = True
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

    im_vollen = klassen_im_css(VOLL.read_text(encoding="utf-8"), erstes_bild=True)
    im_kritischen = klassen_im_css(kritisch)
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
    # Größe der ersten Antwort wie in Produktion: kritisches CSS inline, Kontaktformulare mit Zustellweg
    from django.test.utils import override_settings

    os.environ.setdefault("CONTACT_SMTP_HOST", "127.0.0.1")
    groessen = {}
    with override_settings(DEBUG=False):
        for url in SEITEN_HTML:
            html = client.get(url).content
            groessen[url] = len(gzip.compress(html, 6))
            if b"<style>*" not in html[: html.find(b"</head>")] or b"<form" not in html and url == "/kontakt/":
                fehler.append(f"{url}: nicht wie in Produktion gerendert (kritisches CSS, Formulare)")
            if groessen[url] > GRENZE_HTML:
                fehler.append(
                    f"{url}: HTML {groessen[url]} Bytes gzip (Grenze {GRENZE_HTML}) – passt nicht mehr in die ersten "
                    "TCP-Pakete, das erste Bild kommt am Handy rund 150 ms später"
                )
    if fehler:
        sys.exit("Kritisches CSS:\n  " + "\n  ".join(fehler))
    html = ", ".join(f"{url} {groesse}" for url, groesse in groessen.items())
    print(
        f"OK: kritisches CSS {roh} Bytes ({gz} gzip, Grenze {GRENZE_GZIP}), {len(urls)} Seiten abgedeckt; "
        f"HTML gzip {html} (Grenze {GRENZE_HTML})"
    )


if __name__ == "__main__":
    main()
