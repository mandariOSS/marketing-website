"""Logo-Paket für /presse/: eine ZIP-Datei mit allen Fassungen und den Nutzungshinweisen.

Das Paket wird aus den Dateien in static/brand/ gebaut (siehe scripts/generate_logo.py) –
es gibt also keine zweite, veraltende Kopie im Repository.
"""

from __future__ import annotations

import io
import zipfile
from functools import lru_cache

from django.contrib.staticfiles import finders

LOGO_RULES = [
    "Rund um die Wortmarke mindestens die Breite des Punkts freihalten.",
    "Nicht strecken, stauchen oder drehen und nicht mit Schatten, Kontur oder Verlauf versehen.",
    "Der Punkt steht immer in Indigo (#4F46E5, auf dunklem Grund #818CF8), der Schriftzug in #111827 oder Weiß.",
    "Die dunkle Fassung auf hellem Grund verwenden, die weiße auf dunklem.",
]

# Dateiname im Paket -> Pfad unter static/
LOGO_FILES = {
    "mandari-wortmarke-dunkel.svg": "brand/mandari-logo.svg",
    "mandari-wortmarke-dunkel.png": "brand/mandari-logo.png",
    "mandari-wortmarke-weiss.svg": "brand/mandari-logo-white.svg",
    "mandari-wortmarke-weiss.png": "brand/mandari-logo-white.png",
    "mandari-wortmarke-druck.png": "brand/mandari-logo-print.png",
    "mandari-bildmarke.svg": "brand/favicon.svg",
}

README = """mandari – Logo-Paket

Wortmarke und Bildmarke von mandari, frei verwendbar unter
Creative Commons Namensnennung (CC BY). Namensnennung: mandari.

Schreibweise: mandari wird klein geschrieben, auch am Satzanfang.
Die Produkte heißen mandari Insight, mandari Work und mandari Session.

Nutzungshinweise:
{rules}

Presseanfragen: presse@mandari.de
Pressebereich: https://mandari.de/presse/
"""


@lru_cache(maxsize=1)
def logo_package() -> bytes:
    """ZIP mit allen Logo-Dateien und einer LIESMICH.txt (einmal je Prozess gebaut)."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        rules = "\n".join(f"- {rule}" for rule in LOGO_RULES)
        archive.writestr("mandari-logos/LIESMICH.txt", README.format(rules=rules))
        for name, static_path in LOGO_FILES.items():
            source = finders.find(static_path)
            if source:
                archive.write(source, f"mandari-logos/{name}")
    return buffer.getvalue()
