"""Sprachregel der Website (SPRACHE.md, mandariOSS/mandari#1481): Seeds und Vorlagen gegen die prüfbaren Regeln."""

import re
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase

from marketing.management.commands import migrate_pages_to_streamfield as seeds

#: Wörter, für die das Glossar ein anderes vorsieht (ohne Groß-/Kleinschreibung)
VERBOTEN = [
    "Subprocessor", "Subprozessor", "Subunternehmer", "Unterauftragnehmer",
    "Self-Hosting", "Selbst-Hosting", "Eigenbetrieb", "On-Premises", "Managed Hosting", "Managed Service",
    "Lock-in", "Alt-RIS", "Beta-Phase", "Pilot-Phase", "General-Availability", "Userlimit", "Workspace",
    "Compliance-Call", "Hosting-Stack", "Bürger:innen-Portal", "Verwaltungs-RIS", "Bürgerinnen und Bürger",
    "Prospektsprache", "Andere SaaS", "Marketing-Übertreibung",
]
#: Knopftexte, die durch die Aufrufe aus SPRACHE.md ersetzt sind
ALTE_AUFRUFE = {"Termin vereinbaren", "Vorführung anfragen", "Kontakt aufnehmen", "Beta-Zugang anfragen",
                "Jetzt buchen", "Frage stellen", "Compliance-Call buchen", "Konkrete Frage stellen"}
_ADRESSE = re.compile(r"""(?:href|src)=\\?["'][^"']*["']|https?://\S+""")
_KLEIN = re.compile(r"mandari (work|session|insight)\b")
#: Feste Schreibweisen, die ein „&“ enthalten dürfen (Firmennamen, Zitat aus einer Anbieterquelle)
_AUSNAHMEN = re.compile(r"GmbH & Co\. KG|Drag & Drop")
#: Felder mit Adressen und Ankern: keine Texte, die jemand liest
_KEIN_TEXT = (".anchor", ".anchor_id", ".url", "_url")


def texte(wert, pfad="", *, alles=False):
    """Alle Zeichenketten einer Seed-Definition mit ihrem Ort; Adressen und Anker nur mit ``alles``."""
    if isinstance(wert, str):
        if alles or not pfad.endswith(_KEIN_TEXT):
            yield pfad, wert
    elif isinstance(wert, dict):
        for schluessel, inhalt in wert.items():
            yield from texte(inhalt, f"{pfad}.{schluessel}", alles=alles)
    elif isinstance(wert, (list, tuple)):
        for nummer, inhalt in enumerate(wert):
            yield from texte(inhalt, f"{pfad}[{nummer}]", alles=alles)


def seiten():
    """Marketingseiten und Quellennachweise; Release-Notes und Rechtstexte gehören nicht dazu."""
    yield from seeds.get_marketing_definitions().items()
    yield from seeds.get_legal_definitions().items()


def verstoesse(text):
    ohne_adressen = _AUSNAHMEN.sub(" ", _ADRESSE.sub(" ", text))
    if "—" in ohne_adressen:
        yield "Geviertstrich"
    if " & " in ohne_adressen or " &amp; " in ohne_adressen:
        yield "„&“ statt „und“"
    klein = ohne_adressen.lower()
    for wort in VERBOTEN:
        if wort.lower() in klein:
            yield f"Glossar: „{wort}“"
    if _KLEIN.search(ohne_adressen):
        yield "Produktname klein geschrieben"


class SprachregelTests(SimpleTestCase):
    def test_seeds_halten_die_sprachregel(self):
        funde = []
        for slug, bloecke in seiten():
            for pfad, text in texte(bloecke):
                funde += [f"/{slug}/{pfad}: {art}: {text[:90]}" for art in verstoesse(text)]
        self.assertEqual(funde, [], "\n" + "\n".join(funde))

    def test_keine_alten_aufrufe(self):
        funde = []
        for slug, bloecke in seiten():
            for pfad, text in texte(bloecke):
                if text.strip() in ALTE_AUFRUFE or any(f">{alt}</a>" in text for alt in ALTE_AUFRUFE):
                    funde.append(f"/{slug}/{pfad}: {text[:90]}")
        self.assertEqual(funde, [], "\n" + "\n".join(funde))

    def test_vorlagen_halten_die_sprachregel(self):
        """Fest geschriebene Texte in den Vorlagen (Startseite, Kontakt, Kopf- und Fußzeile …)."""
        funde = []
        wurzel = Path(settings.BASE_DIR) / "templates"
        for datei in sorted(wurzel.rglob("*.html")):
            quelle = datei.read_text(encoding="utf-8")
            sichtbar = re.sub(r"\{% comment %\}.*?\{% endcomment %\}", " ", quelle, flags=re.S)
            sichtbar = re.sub(r"\{#.*?#\}|\{%.*?%\}|\{\{.*?\}\}", " ", sichtbar, flags=re.S)
            sichtbar = re.sub(r"<script.*?</script>|<style.*?</style>|<[^>]+>", " ", sichtbar, flags=re.S)
            funde += [f"{datei.relative_to(wurzel)}: {art}" for art in verstoesse(sichtbar)]
        self.assertEqual(funde, [], "\n" + "\n".join(funde))

    def test_ein_weg_zu_work(self):
        """Wer zu mandari Work führt, nutzt Beschriftung und Ziel aus den Konstanten."""
        for slug in ("fraktionen", "preise"):
            alle = [text for _, text in texte(seeds.get_marketing_definitions()[slug], alles=True)]
            self.assertGreaterEqual(alle.count(seeds.WORK_AUFRUF_URL), 2, slug)
            self.assertIn(seeds.WORK_AUFRUF, alle, slug)
            for text in alle:
                if "kunden.mandari.de/kunden/buchen" in text or "Beta-Zugang" in text or "subject=mandari-Work" in text:
                    self.assertEqual(text, seeds.WORK_AUFRUF_URL, f"/{slug}/: {text}")
