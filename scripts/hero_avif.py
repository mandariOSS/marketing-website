"""
AVIF-Varianten der Hero-Bilder (static/images/startseite): je Bild und Breite eine ``.avif`` neben der ``.webp``.

    python scripts/hero_avif.py [--quelle hero-work-mobil=pfad/zum/bildschirmfoto.png ...]

Vorlage ist je Bild die verlustfreie Aufnahme (``--quelle``, Bildschirmfoto als PNG in der Größe der breitesten
Variante oder größer), sonst die breiteste WebP-Variante. Die Dateien im Repository sind aus den PNG-Aufnahmen
entstanden. Aufnahme wie bei Session und Work: Querformat im Fenster 1280 × 800 mit Pixeldichte 1,25 (1600 × 1000),
Hochformat 390 × 633 mit Pixeldichte 2 (780 × 1266), heller Modus. Insight zeigt seit Oktober 2026 die Übersicht
für Münster im neuen Grün (mandari.de/insight/, Kommune Münster), ohne Personen in Nahaufnahme.

Qualität 55 und volle Farbauflösung (4:4:4, damit Schrift in den Bildschirmen farbrein bleibt): Gegen die Vorlage
gemessen (SSIM) liegt jede AVIF-Datei mindestens so nah wie das WebP derselben Breite und ist rund ein Drittel
kleiner. Verkleinert wird wie bei den WebP-Dateien mit Lanczos. Braucht Pillow mit AVIF (ab 11.3).
"""

import argparse
import pathlib
import sys

from PIL import Image, features

WURZEL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from marketing.templatetags.baender import BILD_ORDNER, MOBIL_BREITEN, PRODUKTE, QUER_BREITEN  # noqa: E402

ORDNER = WURZEL / "static" / BILD_ORDNER
QUALITAET = 55


def varianten():
    """Name ohne Breite → Breiten, wie sie srcset und Preload verwenden (marketing/templatetags/baender.py)."""
    for key, produkt in PRODUKTE.items():
        datei = produkt["bild"]["datei"]
        yield datei, QUER_BREITEN
        if key in ("work", "insight"):
            yield f"{datei}-mobil", MOBIL_BREITEN


def main():
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--quelle", action="append", default=[], metavar="NAME=PFAD")
    args = parser.parse_args()
    if not features.check("avif"):
        sys.exit("Pillow ohne AVIF – bitte Pillow ab 11.3 installieren")
    quellen = dict(q.split("=", 1) for q in args.quelle)
    for name, breiten in varianten():
        vorlage = Image.open(quellen.get(name) or ORDNER / f"{name}-{max(breiten)}.webp").convert("RGB")
        for breite in breiten:
            groesse = Image.open(ORDNER / f"{name}-{breite}.webp").size
            bild = vorlage if vorlage.size == groesse else vorlage.resize(groesse, Image.LANCZOS)
            ziel = ORDNER / f"{name}-{breite}.avif"
            bild.save(ziel, "AVIF", quality=QUALITAET, subsampling="4:4:4", speed=2)
            webp = (ORDNER / f"{name}-{breite}.webp").stat().st_size
            print(f"{ziel.name}: {ziel.stat().st_size} Bytes (WebP {webp}, {ziel.stat().st_size / webp:.0%})")


if __name__ == "__main__":
    main()
