"""
Verkleinert die selbst gehosteten Inter-Dateien (static/fonts/inter-*.woff2) für die Website.

* Achse ``wght`` auf 400–700 begrenzt: Die Website nutzt Stärken von 400 bis 700 (``font-weight: 400 700`` in
  templates/base.html). Innerhalb dieses Bereichs zeichnet die Schrift unverändert.
* Nur die Zeichen, die die Datei schon hat (Teilmengen latin und latin-ext wie bei Google Fonts), und die
  OpenType-Funktionen, die Text braucht (Kerning, Akzente, Ziffernbreiten für ``tabular-nums``); Bruchziffern
  (frac, numr, dnom) entfallen.

Aufruf (fontTools ist keine Abhängigkeit der Website):

    uv run --with fonttools --with brotli python scripts/schrift_teilmenge.py

Nur einmal auf die Originaldateien anwenden (Inter 4, Teilmengen von Google Fonts); ein zweiter Lauf ist
unschädlich, ändert aber die Bytes.
"""

import io
from pathlib import Path

from fontTools import subset
from fontTools.ttLib import TTFont
from fontTools.varLib import instancer

ORDNER = Path(__file__).resolve().parent.parent / "static" / "fonts"
DATEIEN = ("inter-latin.woff2", "inter-latin-ext.woff2")
STAERKEN = (400, 700)
FUNKTIONEN = ["calt", "ccmp", "locl", "kern", "mark", "mkmk", "liga", "tnum", "pnum"]


def verkleinern(pfad: Path) -> tuple[int, int]:
    vorher = pfad.stat().st_size
    schrift = TTFont(pfad)
    zeichen = list(schrift.getBestCmap())
    if "fvar" in schrift:
        schrift = instancer.instantiateVariableFont(schrift, {"wght": STAERKEN})
        # Neu laden, damit der Subsetter die Glyphen der begrenzten Schrift sieht
        puffer = io.BytesIO()
        schrift.save(puffer)
        puffer.seek(0)
        schrift = TTFont(puffer)
    optionen = subset.Options()
    optionen.flavor = "woff2"
    optionen.layout_features = FUNKTIONEN
    optionen.name_IDs = ["*"]
    optionen.notdef_outline = True
    teilmenge = subset.Subsetter(optionen)
    teilmenge.populate(unicodes=zeichen)
    teilmenge.subset(schrift)
    schrift.flavor = "woff2"
    schrift.save(pfad)
    return vorher, pfad.stat().st_size


if __name__ == "__main__":
    for name in DATEIEN:
        vorher, nachher = verkleinern(ORDNER / name)
        print(f"{name}: {vorher:,} -> {nachher:,} Bytes".replace(",", "."))
