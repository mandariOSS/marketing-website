"""
„Offene Daten“ auf der Website (mandariOSS/mandari#1309): die OParl-Schnittstelle mit den Adressen jeder Kommune.

Die Website hat keinen Zugriff auf die Datenbank der Anwendung. Sie liest die Kommunen aus der Übersicht der
Schnittstelle (``OPARL_UEBERSICHT_URL``, Feld ``bodyIndex``; in der Anwendung ``hub.api.verzeichnis``) und hält sie
im Zwischenspeicher. Fällt der Abruf aus, zeigt sie den letzten bekannten Stand; gibt es keinen, nennt die Seite den
Einstieg der Schnittstelle ohne die Liste.

Die Seiten zeigen die Kurzadresse mit dem Namen der Kommune (``…/body/muenster/papers``), weil man an ihr sieht, wo
man ist. Sie leitet auf die gültige Adresse mit der UUID weiter; diese bleibt die Kennung und steht daneben.

Suchmaschinen und Sprachmodelle finden JSON kaum, und Sprachmodelle rufen meist nur Adressen ab, die als Suchtreffer
erschienen sind. Deshalb stehen alle Adressen als sichtbarer Text auf eigenen, indexierbaren Seiten: eine Übersicht
und eine Seite je Kommune (Titel mit „OParl“, Kommune und „mandari“).
"""

from __future__ import annotations

import http.client
import json
import logging
import re
import urllib.request
from dataclasses import dataclass, field

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

#: So lange gilt ein Abruf als frisch (Sekunden); neue Kommunen kommen selten dazu
FRISCH_SEKUNDEN = 1800
#: So lange bleibt der letzte gelungene Abruf als Rückfall liegen (Sekunden)
RUECKFALL_SEKUNDEN = 7 * 24 * 3600
#: Zeitgrenze des Abrufs (Sekunden): Die Seite soll nie an der Schnittstelle hängen
ZEITGRENZE_SEKUNDEN = 4
#: Größte Antwort, die gelesen wird (Bytes)
HOECHSTENS_BYTES = 2_000_000
_CACHE_FRISCH = "offene-daten:frisch"
_CACHE_RUECKFALL = "offene-daten:rueckfall"
#: So lange gilt ein gescheiterter Abruf (Sekunden): Währenddessen fragt keine Seite die Schnittstelle erneut
PAUSE_NACH_FEHLER_SEKUNDEN = 120
#: Platzhalter im Zwischenspeicher für „gerade kein Stand“ (wird beim Lesen mit Gleichheit verglichen)
_KEIN_STAND = "kein-stand"

#: Listen je Kommune: Feld in ``bodyIndex`` → (Segment der Adresse, Beschriftung)
LISTEN = {
    "paper": ("papers", "Vorlagen, Anträge und Anfragen"),
    "meeting": ("meetings", "Sitzungen mit Tagesordnung"),
    "organization": ("organizations", "Gremien und Fraktionen"),
    "person": ("people", "Personen"),
}
_SLUG = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*\Z")
_ADRESSE = re.compile(r"https?://[^\s<>\"']+\Z")


@dataclass(frozen=True)
class Liste:
    feld: str
    name: str
    #: Kurzadresse mit dem Namen der Kommune; ohne Slug die gültige Adresse
    adresse: str
    #: Gültige Adresse mit der UUID
    kennung: str


@dataclass(frozen=True)
class Kommune:
    name: str
    anzeige: str
    slug: str
    ags: str
    #: Gültige Adresse des OParl-Body (Kennung der Kommune)
    kennung: str
    #: Kurzadresse des Body; ohne Slug die Kennung
    adresse: str
    web: str
    lizenz: str
    listen: tuple[Liste, ...] = field(default_factory=tuple)

    def liste(self, feld: str) -> Liste | None:
        return next((eintrag for eintrag in self.listen if eintrag.feld == feld), None)


@dataclass(frozen=True)
class Verzeichnis:
    """Die Kommunen der Schnittstelle und ihr Einstieg."""

    system: str
    uebersicht: str
    kommunen: tuple[Kommune, ...]

    def kommune(self, slug: str) -> Kommune | None:
        return next((k for k in self.kommunen if k.slug == slug), None)


def quelle() -> str:
    """Adresse der Übersicht der Schnittstelle; leer schaltet den Abruf ab (Entwicklung, Tests, CI)."""
    return (getattr(settings, "OPARL_UEBERSICHT_URL", "") or "").strip()


def _adresse(wert: object) -> str:
    """Nur vollständige http(s)-Adressen ohne Leerraum: Die Werte landen in Links."""
    text = wert.strip() if isinstance(wert, str) else ""
    return text if _ADRESSE.match(text) else ""


def _kommune(eintrag: dict) -> Kommune | None:
    kennung = _adresse(eintrag.get("body"))
    name = eintrag.get("name")
    if not kennung or not isinstance(name, str) or not name.strip():
        return None
    slug = eintrag.get("slug") if isinstance(eintrag.get("slug"), str) and _SLUG.match(eintrag["slug"]) else ""
    # Kurzadresse: dieselbe Adresse mit dem Namen an der Stelle der Kennung
    anfang = kennung.rsplit("/body/", 1)[0] if "/body/" in kennung else ""
    kurz = f"{anfang}/body/{slug}" if slug and anfang else kennung
    listen = []
    for feld, (segment, beschriftung) in LISTEN.items():
        gueltig = _adresse(eintrag.get(feld))
        if gueltig:
            listen.append(Liste(feld, beschriftung, f"{kurz}/{segment}" if kurz != kennung else gueltig, gueltig))
    anzeige = eintrag.get("displayName")
    ags = eintrag.get("ags")
    return Kommune(
        name=name.strip(),
        anzeige=anzeige.strip() if isinstance(anzeige, str) and anzeige.strip() else name.strip(),
        slug=slug,
        ags=ags if isinstance(ags, str) and ags.isdigit() else "",
        kennung=kennung,
        adresse=kurz,
        web=_adresse(eintrag.get("web")),
        lizenz=_adresse(eintrag.get("license")),
        listen=tuple(listen),
    )


def auswerten(daten: object, uebersicht: str) -> Verzeichnis | None:
    """Antwort der Übersicht in ein Verzeichnis übersetzen; ``None``, wenn sie nicht die erwartete Form hat."""
    if not isinstance(daten, dict) or not isinstance(daten.get("bodyIndex"), list):
        return None
    kommunen = [k for k in (_kommune(e) for e in daten["bodyIndex"] if isinstance(e, dict)) if k is not None]
    system = _adresse(daten.get("system")) or uebersicht.rstrip("/") + "/v1/system"
    return Verzeichnis(system=system, uebersicht=uebersicht, kommunen=tuple(kommunen))


def _abrufen(adresse: str) -> Verzeichnis | None:
    anfrage = urllib.request.Request(adresse, headers={"Accept": "application/json", "User-Agent": "mandari-website"})
    try:
        with urllib.request.urlopen(anfrage, timeout=ZEITGRENZE_SEKUNDEN) as antwort:  # noqa: S310 - feste Adresse
            daten = json.loads(antwort.read(HOECHSTENS_BYTES + 1)[:HOECHSTENS_BYTES])
    except (OSError, ValueError, http.client.HTTPException) as fehler:
        # HTTPException (abgeschnittene oder kaputte Antwort) ist kein OSError
        logger.warning("Übersicht der OParl-Schnittstelle nicht abrufbar (%s)", type(fehler).__name__)
        return None
    verzeichnis = auswerten(daten, adresse)
    if verzeichnis is None:
        logger.warning("Übersicht der OParl-Schnittstelle ohne bodyIndex")
    return verzeichnis


def verzeichnis() -> Verzeichnis | None:
    """
    Die Kommunen der Schnittstelle: frisch aus dem Zwischenspeicher, sonst neu abgerufen, sonst der letzte bekannte
    Stand. ``None``, wenn der Abruf abgeschaltet ist oder es noch nie einen gelungenen gab.
    """
    adresse = quelle()
    if not adresse:
        return None
    frisch = cache.get(_CACHE_FRISCH)
    if frisch is not None:
        return None if frisch == _KEIN_STAND else frisch
    neu = _abrufen(adresse)
    if neu is not None:
        cache.set(_CACHE_FRISCH, neu, FRISCH_SEKUNDEN)
        cache.set(_CACHE_RUECKFALL, neu, RUECKFALL_SEKUNDEN)
        return neu
    alt = cache.get(_CACHE_RUECKFALL)
    # Nicht bei jedem Aufruf erneut gegen die Zeitgrenze laufen, auch ohne letzten Stand: Sonst bindet jede Anfrage
    # an eine der Seiten oder die Sitemap einen Prozess, solange die Schnittstelle nicht antwortet
    cache.set(_CACHE_FRISCH, alt if alt is not None else _KEIN_STAND, PAUSE_NACH_FEHLER_SEKUNDEN)
    return alt


def datensatz(kommune: Kommune, seite: str) -> dict:
    """Eine Kommune als ``Dataset`` (schema.org)."""
    vorlagen = kommune.liste("paper")
    return {
        "@type": "Dataset",
        "name": f"Ratsinformationen {kommune.anzeige}",
        "description": (
            f"Sitzungen, Vorlagen, Gremien und Personen aus dem Ratsinformationssystem von {kommune.name}, "
            "maschinenlesbar nach OParl 1.1."
        ),
        "url": seite,
        "isAccessibleForFree": True,
        **({"license": kommune.lizenz} if kommune.lizenz else {}),
        **({"identifier": kommune.ags} if kommune.ags else {}),
        "distribution": [
            {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": kommune.kennung},
            *(
                [{"@type": "DataDownload", "name": "Vorlagen", "encodingFormat": "application/json",
                  "contentUrl": vorlagen.kennung}]
                if vorlagen
                else []
            ),
        ],
    }
