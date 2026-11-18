"""
Bildschirme der Produkte für die Abschnitte unterhalb des Seitenkopfs (static/images/bildschirme).

Jeder Eintrag ist ein Ausschnitt aus der öffentlichen Demo (demo.mandari.de) oder aus dem Bürgerportal: nur der
Inhaltsbereich ohne Seitenleiste, aufgenommen mit doppelter Pixeldichte. ``groesse`` ist die Größe der Vorlage in
Pixeln, daraus entstehen Breite und Höhe des ``<img>`` (kein Springen beim Laden). ``herkunft`` steht als
Bildunterschrift unter dem Bild, damit niemand erfundene Musterdaten für einen Kunden hält.

Neue Bilder: Vorlage als PNG aufnehmen, hier eintragen, dann ``python scripts/bildschirme.py name=pfad.png``.
Die Dateien liegen je Breite als AVIF und als WebP vor (README, „Bildschirme“).
"""

from django.templatetags.static import static

ORDNER = "images/bildschirme"
BREITEN = (640, 960, 1280, 1600)

# Angezeigte Breite (.ausschnitt img in static/css/input.css): am Handy 34 rem, ab 640 px 40 rem, ab 1024 px
# höchstens 52 rem. Ändert sich das Raster, hier nachziehen.
GROESSEN = "(min-width: 1024px) 52rem, (min-width: 640px) 40rem, 34rem"

DEMO_SESSION = "Aus der Demo: Stadtverwaltung Musterstadt"
DEMO_WORK = "Aus der Demo: Musterfraktion"

BILDSCHIRME = {
    "session-tagesordnung": {
        "groesse": (1280, 940), "herkunft": DEMO_SESSION,
        "alt": "Tagesordnung einer Ratssitzung in mandari Session mit zehn Punkten, Vorlagen und Beratungsfolge",
    },
    "session-sitzung": {
        "groesse": (2048, 1400), "herkunft": DEMO_SESSION,
        "alt": "Ratssitzung in mandari Session mit Tagesordnung, Ladungsfrist und den Unterlagen als PDF",
    },
    "work-start": {
        "groesse": (1720, 1240), "herkunft": DEMO_WORK,
        "alt": "Startseite von mandari Work mit den nächsten Sitzungen und dem Stand der Vorbereitung",
    },
    "work-vorbereitung": {
        "groesse": (2048, 1152), "herkunft": DEMO_WORK,
        "alt": "Vorbereitung eines Tagesordnungspunkts in mandari Work: Vorlage, Begründung und Position der Fraktion",
    },
    "work-fraktionssitzung": {
        "groesse": (2048, 1320), "herkunft": DEMO_WORK,
        "alt": "Fraktionssitzung in mandari Work mit Tagesordnung, Einladung und den Punkten aus der Ratssitzung",
    },
    "work-zusammenfassung": {
        # Ein Dialog, schmaler als die Fläche: füllt sie in der Breite, statt daneben einen leeren Streifen zu lassen
        "groesse": (1344, 1280), "herkunft": DEMO_WORK, "anzeige": "100%",
        "alt": "Zusammenfassung der Vorbereitung in mandari Work: Positionen je Tagesordnungspunkt und geplante "
               "Redebeiträge",
    },
    "insight-beschluesse": {
        "groesse": (1656, 1168), "herkunft": "Echte Daten: Stadt Münster im Bürgerportal",
        "alt": "Beschlüsse der Stadt Münster im Bürgerportal, nach Sitzung geordnet, mit Ergebnis je Vorgang",
    },
}

def breiten(name):
    """Breiten, in denen ein Bild vorliegt: die Stufen aus ``BREITEN`` bis zur Breite der Vorlage."""
    voll = BILDSCHIRME[name]["groesse"][0]
    return tuple(b for b in BREITEN if b <= voll)


def bildschirm(name):
    """Angaben für ``<picture>``: ``url``, ``srcset`` (WebP), ``srcset_avif``, ``sizes``, ``breite``, ``hoehe``,
    ``alt``, ``herkunft`` und ``anzeige`` (abweichende Breite ab 1024 px, sonst leer). Unbekannte Namen ergeben
    ``None`` (der Abschnitt bleibt dann ohne Bild)."""
    daten = BILDSCHIRME.get(name)
    if not daten:
        return None
    stufen = breiten(name)

    def srcset(endung):
        return ", ".join(f"{static(f'{ORDNER}/{name}-{b}.{endung}')} {b}w" for b in stufen)

    breite, hoehe = daten["groesse"]
    return {
        "name": name, "alt": daten["alt"], "herkunft": daten["herkunft"], "breite": breite, "hoehe": hoehe,
        "anzeige": daten.get("anzeige", ""),
        "url": static(f"{ORDNER}/{name}-{stufen[min(1, len(stufen) - 1)]}.webp"),
        "srcset": srcset("webp"), "srcset_avif": srcset("avif"), "sizes": GROESSEN,
    }
