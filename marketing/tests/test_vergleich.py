"""RIS-Vergleich: jede Angabe zu einem Anbieter belegt, Lücken von mandari offen benannt (§ 6 UWG)."""

import re
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from marketing import seeds_vergleich as sv

KUERZEL = re.compile(r"\[([A-Z]{2}\d+(?:, [A-Z]{2}\d+)*)\]")
STUFEN = ("Geplant", "In Prüfung", "Zugesagt", "Prüfbericht")


def kuerzel_in(text):
    return [k for gruppe in KUERZEL.findall(text) for k in gruppe.split(", ")]


class DatenTests(SimpleTestCase):
    def test_jede_funktion_hat_eine_mandari_zelle(self):
        keys = {key for _, rows in sv.GRUPPEN for key, _ in rows}
        self.assertEqual(keys, set(sv.MANDARI))
        self.assertEqual(sv.ANZAHL_FUNKTIONEN, len(keys))

    def test_anbieterangaben_nur_mit_quelle_und_nie_nein(self):
        keys = {key for _, rows in sv.GRUPPEN for key, _ in rows}
        for slug, v in sv.ANBIETER.items():
            self.assertLessEqual(set(v["cells"]), keys, slug)
            for key, (status, note) in v["cells"].items():
                # Über Anbieter behaupten wir nie, dass etwas fehlt – nur „keine öffentliche Angabe“.
                self.assertIn(status, ("yes", "partial", "unknown"), f"{slug}/{key}")
                if status in ("yes", "partial"):
                    self.assertTrue(kuerzel_in(note), f"{slug}/{key}: Angabe ohne Quellenkürzel")
                for k in kuerzel_in(note):
                    self.assertIn(k, sv.QUELLEN, f"{slug}/{key}: unbekannte Quelle {k}")
                    self.assertTrue(k.startswith(sv.QUELLEN_JE_ANBIETER[slug]), f"{slug}/{key}: Quelle {k}")

    def test_fehlendes_bei_mandari_nennt_die_roadmap_stufe(self):
        for key, (status, note) in sv.MANDARI.items():
            self.assertIn(status, ("yes", "partial", "open"), key)
            if status == "open":
                self.assertTrue(note.startswith(STUFEN), f"{key}: {note}")
                self.assertTrue(sv.MANDARI_KURZ.get(key, "").startswith(STUFEN), key)

    def test_luecken_haengen_an_fehlenden_funktionen(self):
        for luecke in sv.LUECKEN:
            self.assertIn(luecke["art"], ("geplant", "pruefung"))
            self.assertTrue(luecke["stufe"].startswith(STUFEN), luecke["key"])
            for key in luecke["zeilen"]:
                self.assertNotEqual(sv.MANDARI[key][0], "yes", f"{luecke['key']}: {key} ist bei mandari vorhanden")
            self.assertTrue(sv.anbieter_mit(luecke) or luecke.get("auch"), luecke["key"])
            if luecke["link"]:
                self.assertTrue(luecke["link"][1].startswith("https://github.com/mandariOSS/mandari/issues/"))
            if luecke["art"] == "geplant":
                self.assertTrue(luecke.get("karten"), f"{luecke['key']}: geplante Lücke ohne Roadmap-Karte")

    def test_weitere_anbieter_nur_mit_quelle(self):
        # Auch Anbieter außerhalb der vier stehen nur mit belegter Angabe auf der Seite.
        for luecke in sv.LUECKEN:
            for name, kuerzel, status in luecke.get("auch", []):
                self.assertIn(status, ("yes", "partial"), f"{luecke['key']}/{name}")
                for k in kuerzel.split(", "):
                    self.assertIn(k, sv.QUELLEN, f"{luecke['key']}/{name}: unbekannte Quelle {k}")
                    self.assertTrue(k.startswith(tuple(sv.PRAEFIXE_WEITERE)), f"{luecke['key']}/{name}: {k}")

    def test_vorhanden_nur_wenn_alle_zeilen_ja(self):
        # „Vorhanden bei“ nur für Anbieter mit „Ja“ in allen Zeilen der Lücke, sonst „teilweise bei“.
        for luecke in sv.LUECKEN:
            label = sv._beleg_label(luecke)
            vorhanden = label.split(";")[0] if label.startswith("Vorhanden bei") else ""
            for slug in sv.anbieter_mit(luecke):
                name = sv.ANBIETER[slug]["spalte"]
                self.assertEqual(name in vorhanden, sv.anbieter_voll(luecke, slug), f"{luecke['key']}/{name}: {label}")

    def test_hoechstens_acht_zeilen_je_abschnitt(self):
        for slug in [None, *sv.ANBIETER]:
            for _, block in sv.luecken_bloecke(slug):
                self.assertLessEqual(len(block["rows"]), 8, slug)
                self.assertGreater(len(block["rows"]), 0, slug)


class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_uebersicht_mit_allen_anbietern_luecken_und_quellen(self):
        html = self.client.get("/vergleich/").content.decode("utf-8")
        for slug in sv.ANBIETER:
            self.assertIn(f'href="/vergleich/{slug}/"', html)
        self.assertIn("Alle Funktionen auf einen Blick", html)
        self.assertIn('id="fehlt"', html)
        self.assertIn("Was mandari noch fehlt: in Prüfung", html)
        for kuerzel in sv.QUELLEN:
            self.assertIn(f"[{kuerzel}]", html)
        # Kürzel in den Lücken (auch die weiteren Anbieter) stehen im Quellenverzeichnis der Seite.
        haupt = html[html.find('role="main"'):]
        quellen = haupt[haupt.find('id="quellen"'):]
        for k in set(kuerzel_in(haupt[:haupt.find('id="quellen"')])):
            self.assertIn(f"[{k}]", quellen, f"Quelle {k} fehlt im Quellenverzeichnis")
        self.assertNotIn("PROVOX", html)

    def test_anbieterseiten_zitieren_nur_aufgefuehrte_quellen(self):
        for slug in sv.ANBIETER:
            html = self.client.get(f"/vergleich/{slug}/").content.decode("utf-8")
            haupt = html[html.find('role="main"'):]
            quellen = haupt[haupt.find('id="quellen"'):]
            tabelle = haupt[:haupt.find('id="quellen"')]
            self.assertIn("Noch nicht verfügbar", tabelle, slug)
            self.assertIn(f"Stand {sv.STAND}", tabelle, slug)
            for k in set(kuerzel_in(tabelle)):
                self.assertIn(f"[{k}]", quellen, f"{slug}: Quelle {k} fehlt im Quellenverzeichnis")

    def test_kein_anbieterprodukt_in_mandari_kennfarbe(self):
        # „Session“ im Produktnamen eines Anbieters darf keine Fläche in der Farbe von mandari Session bekommen.
        html = self.client.get("/vergleich/mandari-vs-somacos/").content.decode("utf-8")
        self.assertNotIn("produkt-session", html)

    def test_roadmap_fuehrt_die_luecken(self):
        html = self.client.get("/roadmap/").content.decode("utf-8")
        self.assertIn('id="marktvergleich"', html)
        self.assertIn('href="/vergleich/#fehlt"', html)
        self.assertNotIn("Aus dem Marktvergleich: zugesagt und geplant", html)
        for luecke in sv.LUECKEN:
            if luecke["art"] == "pruefung":
                self.assertIn(luecke["titel"], html)
            else:
                # Zugesagte und geplante Lücken stehen als Karte auf der Roadmap, nicht noch einmal als Zeile.
                for karte in luecke["karten"]:
                    self.assertIn(karte, html, f"{luecke['key']}: Karte {karte} fehlt auf der Roadmap")

    def test_barrierefreiheit_ohne_unbelegte_zusage(self):
        # Zugesagt ist die Selbstbewertung (#44), nicht eine unabhängige Prüfung.
        for url in ("/vergleich/", "/roadmap/", "/vergleich/mandari-vs-regisafe/"):
            html = self.client.get(url).content.decode("utf-8")
            self.assertNotIn("lassen wir die Barrierefreiheit", html, url)
        self.assertTrue(sv.MANDARI["bitv"][1].startswith("In Prüfung"))
