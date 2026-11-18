"""
Kennzahlen des Bürgerportals auf der Website (mandariOSS/mandari#1481).

Die Website hat keinen Zugriff auf die Datenbank der Anwendung. Sie liest die Zahlen aus der öffentlichen Statistik
der Anwendung (``KENNZAHLEN_URL``, Felder ``bodies``, ``papers``, ``meetings``, ``persons``, ``organizations``) und
hält sie im Zwischenspeicher. Fällt der Abruf aus, gilt der letzte bekannte Stand, sonst der Rückfall unten. So
veralten die Zahlen auf /presse/, /transparenz/ und /buergerinformationssystem/ nicht mehr, und jede Angabe nennt
ihren Stand.

In den Seeds stehen Platzhalter in eckigen Klammern (``[kommunen]``, ``[vorgaenge]``, ``[sitzungen]``,
``[personen]``, ``[gremien]``, ``[kennzahlen-stand]``); der Filter ``kennzahlen`` setzt sie beim Rendern ein
(``marketing/templatetags/kennzahlen.py``).
"""

from __future__ import annotations

import http.client
import json
import logging
import threading
import urllib.request
from dataclasses import dataclass
from datetime import date

from django.conf import settings
from django.core.cache import cache

logger = logging.getLogger(__name__)

#: So lange gilt ein Abruf als frisch (Sekunden); die Zahlen ändern sich täglich, nicht minütlich
FRISCH_SEKUNDEN = 6 * 3600
#: So lange bleibt der letzte gelungene Abruf als Rückfall liegen (Sekunden)
RUECKFALL_SEKUNDEN = 14 * 24 * 3600
#: Zeitgrenze des Abrufs (Sekunden); er läuft im Hintergrund, keine Seite wartet darauf
ZEITGRENZE_SEKUNDEN = 15
#: Größte Antwort, die gelesen wird (Bytes)
HOECHSTENS_BYTES = 10_000
#: So lange gilt ein gescheiterter Abruf (Sekunden): Währenddessen fragt keine Seite erneut
PAUSE_NACH_FEHLER_SEKUNDEN = 300
_CACHE_FRISCH = "kennzahlen:frisch"
_CACHE_RUECKFALL = "kennzahlen:rueckfall"
_KEIN_STAND = "kein-stand"

#: Feld der Statistik → Platzhalter in den Seeds
FELDER = {
    "bodies": "kommunen",
    "papers": "vorgaenge",
    "meetings": "sitzungen",
    "persons": "personen",
    "organizations": "gremien",
}
_MONATE = ["Januar", "Februar", "März", "April", "Mai", "Juni", "Juli", "August", "September", "Oktober",
           "November", "Dezember"]


@dataclass(frozen=True)
class Kennzahlen:
    kommunen: int
    vorgaenge: int
    sitzungen: int
    personen: int
    gremien: int
    #: Tag, an dem die Zahlen gelesen wurden
    stand: date

    def stand_text(self) -> str:
        return f"{self.stand.day}. {_MONATE[self.stand.month - 1]} {self.stand.year}"

    def platzhalter(self) -> dict[str, str]:
        """Platzhalter → eingesetzter Text (Zahlen mit Tausenderpunkt)."""
        werte = {name: zahl(getattr(self, name)) for name in FELDER.values()}
        werte["kennzahlen-stand"] = self.stand_text()
        return werte


#: Rückfall, solange es keinen gelungenen Abruf gibt (Entwicklung, Tests, erster Aufruf nach dem Start).
#: Gelesen aus der öffentlichen Statistik am genannten Tag; bei größeren Änderungen nachziehen.
RUECKFALL = Kennzahlen(kommunen=40, vorgaenge=383_983, sitzungen=61_909, personen=18_366, gremien=3_043,
                       stand=date(2026, 11, 18))


def zahl(wert: int) -> str:
    """Ganze Zahl mit Tausenderpunkt, wie im Deutschen üblich."""
    return f"{wert:,}".replace(",", ".")


def quelle() -> str:
    """Adresse der Statistik; leer schaltet den Abruf ab (Entwicklung, Tests, CI)."""
    return (getattr(settings, "KENNZAHLEN_URL", "") or "").strip()


def auswerten(daten: object, heute: date) -> Kennzahlen | None:
    """Antwort der Statistik übersetzen; ``None``, wenn ein Feld fehlt oder keine positive ganze Zahl ist."""
    if not isinstance(daten, dict):
        return None
    werte = {}
    for feld, name in FELDER.items():
        wert = daten.get(feld)
        # bool ist in Python ein int und wäre hier eine falsche Zahl
        if isinstance(wert, bool) or not isinstance(wert, int) or wert <= 0:
            return None
        werte[name] = wert
    return Kennzahlen(stand=heute, **werte)


def _abrufen(adresse: str) -> Kennzahlen | None:
    anfrage = urllib.request.Request(adresse, headers={"Accept": "application/json", "User-Agent": "mandari-website"})
    try:
        with urllib.request.urlopen(anfrage, timeout=ZEITGRENZE_SEKUNDEN) as antwort:  # noqa: S310 - feste Adresse
            daten = json.loads(antwort.read(HOECHSTENS_BYTES + 1)[:HOECHSTENS_BYTES])
    except (OSError, ValueError, http.client.HTTPException) as fehler:
        logger.warning("Statistik des Bürgerportals nicht abrufbar (%s)", type(fehler).__name__)
        return None
    kennzahlen_neu = auswerten(daten, date.today())
    if kennzahlen_neu is None:
        logger.warning("Statistik des Bürgerportals in unerwarteter Form")
    return kennzahlen_neu


def _erneuern(adresse: str) -> None:
    """Statistik abrufen und bei Erfolg im Zwischenspeicher ablegen (läuft im Hintergrund)."""
    neu = _abrufen(adresse)
    if neu is not None:
        cache.set(_CACHE_FRISCH, neu, FRISCH_SEKUNDEN)
        cache.set(_CACHE_RUECKFALL, neu, RUECKFALL_SEKUNDEN)


def _starten(funktion, *argumente) -> None:
    """Im Hintergrund ausführen; die Tests ersetzen das durch einen direkten Aufruf."""
    threading.Thread(target=funktion, args=argumente, daemon=True).start()


def kennzahlen() -> Kennzahlen:
    """
    Die Kennzahlen: frisch aus dem Zwischenspeicher, sonst der letzte bekannte Stand, sonst der Rückfall aus dem
    Code. Liefert immer sofort einen Stand.

    Ist der Zwischenspeicher abgelaufen, erneuert ein Hintergrundlauf die Zahlen; die Seite wartet nie auf die
    Statistik. Deren Zählung über große Tabellen dauert bei kaltem Zwischenspeicher der Anwendung mehrere Sekunden.
    """
    adresse = quelle()
    if not adresse:
        return RUECKFALL
    frisch = cache.get(_CACHE_FRISCH)
    if frisch is not None:
        return RUECKFALL if frisch == _KEIN_STAND else frisch
    alt = cache.get(_CACHE_RUECKFALL)
    # Bis der Hintergrundlauf fertig ist (oder nach einem Fehler) gilt der letzte Stand; in dieser Zeit startet
    # kein weiterer Abruf
    cache.set(_CACHE_FRISCH, alt if alt is not None else _KEIN_STAND, PAUSE_NACH_FEHLER_SEKUNDEN)
    _starten(_erneuern, adresse)
    return alt if alt is not None else RUECKFALL


def einsetzen(text: str) -> str:
    """Platzhalter in einem Text durch die aktuellen Kennzahlen ersetzen; Text ohne Platzhalter bleibt gleich."""
    if "[" not in text:
        return text
    for name, wert in kennzahlen().platzhalter().items():
        text = text.replace(f"[{name}]", wert)
    return text
