"""
Bildschirme für die Abschnitte (static/images/bildschirme): je Bild und Breite eine ``.avif`` und eine ``.webp``.

    python scripts/bildschirme.py work-start=pfad/work-start.png session-sitzung=pfad/session-sitzung.png

Vorlage ist das Bildschirmfoto als PNG: nur der Inhaltsbereich ohne Seitenleiste, doppelte Pixeldichte, heller
Modus, Hinweis „Demo-Umgebung“ ausgeblendet. Name und Größe stehen in ``marketing/bildschirme.py``; das Skript
bricht ab, wenn die Vorlage dort fehlt oder eine andere Größe hat (sonst stimmen Breite und Höhe im HTML nicht).

Qualität wie bei den Hero-Bildern (scripts/hero_avif.py): AVIF 55 mit voller Farbauflösung, damit Schrift farbrein
bleibt, WebP 82. Verkleinert wird mit Lanczos. Braucht Pillow mit AVIF (ab 11.3).
"""

import pathlib
import sys

from PIL import Image, features

WURZEL = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WURZEL))

from marketing.bildschirme import BILDSCHIRME, ORDNER, breiten  # noqa: E402

ZIEL = WURZEL / "static" / ORDNER


def main(argumente):
    if not features.check("avif"):
        sys.exit("Pillow ohne AVIF: pip install 'pillow>=11.3'")
    if not argumente:
        sys.exit(__doc__)
    ZIEL.mkdir(parents=True, exist_ok=True)
    for argument in argumente:
        name, _, pfad = argument.partition("=")
        if name not in BILDSCHIRME:
            sys.exit(f"{name}: nicht in marketing/bildschirme.py eingetragen")
        vorlage = Image.open(pfad).convert("RGB")
        if vorlage.size != tuple(BILDSCHIRME[name]["groesse"]):
            sys.exit(f"{name}: Vorlage hat {vorlage.size}, eingetragen ist {BILDSCHIRME[name]['groesse']}")
        for breite in breiten(name):
            bild = vorlage.resize((breite, round(vorlage.height * breite / vorlage.width)), Image.LANCZOS)
            bild.save(ZIEL / f"{name}-{breite}.webp", quality=82, method=6)
            bild.save(ZIEL / f"{name}-{breite}.avif", quality=55, subsampling="4:4:4", speed=4)
            kb = [round((ZIEL / f"{name}-{breite}.{e}").stat().st_size / 1024) for e in ("avif", "webp")]
            print(f"{name}-{breite}: AVIF {kb[0]} KB, WebP {kb[1]} KB")


if __name__ == "__main__":
    main(sys.argv[1:])
