"""
Musterkatalog: Form folgt Inhalt, Rhythmus je Seite, keine Spendenwege.

Prüft die Seeds (marketing/management/commands/migrate_pages_to_streamfield.py, seeds_unternehmen.py,
seeds_vergleich.py), die Geometrie der Zeitskala und das Rendern der Muster. Dass kein Abschnitt eine
leere rechte Hälfte hat, misst scripts/check_fuellung.py im Browser (CI-Schritt „Gestaltungssystem:
keine leere rechte Hälfte“).
"""

from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from marketing import muster_daten
from marketing.management.commands.migrate_pages_to_streamfield import get_legal_definitions, get_marketing_definitions
from marketing.templatetags.muster import dauer_plan, dokument_gliederung, register_plan, zeitskala_plan

# Ruhende Seite (Weiterleitung auf /unternehmen/), bei Rückkehr nach dem Katalog umbauen
RUHEND = {"karriere"}
# Das alte Raster „fette Zeile + Absatz“ und seine Verwandten: auf aktiven Seiten nicht mehr
ALTE_RASTER = {"mandari_cards", "two_column_use_case", "step_process", "stats_grid", "trust_banner"}
# Bausteine, die sich wiederholen dürfen (Abschnitte eines Dokuments, Hinweise am Kopf)
WIEDERHOLBAR = {"numbered_article", "disclaimer_box", "richtext_section"}


def aktive_seiten():
    seiten = {**get_marketing_definitions(), **get_legal_definitions()}
    return {slug: bloecke for slug, bloecke in seiten.items() if slug not in RUHEND}


class RhythmusTests(SimpleTestCase):
    def test_nie_zweimal_dasselbe_muster_hintereinander(self):
        for slug, bloecke in aktive_seiten().items():
            typen = [typ for typ, _ in bloecke if typ != "disclaimer_box"]
            for links, rechts in zip(typen, typen[1:]):
                if links == rechts and links not in WIEDERHOLBAR:
                    self.fail(f"/{slug}/: zweimal {links} hintereinander ({typen})")

    def test_alte_raster_nur_noch_wo_erlaubt(self):
        # trust_banner bleibt auf dem Trust Center erlaubt: die Dokumentseite setzt die Eckdaten in die Randspalte
        for slug, bloecke in aktive_seiten().items():
            for typ, wert in bloecke:
                if typ in ALTE_RASTER and not (slug == "trust" and typ == "trust_banner"):
                    self.fail(f"/{slug}/: altes Raster {typ}")
                if typ == "split_rows" and wert.get("layout", "raster") == "raster" and slug != "vergleich":
                    self.fail(f"/{slug}/: Raster „fette Zeile + Absatz“ (split_rows)")

    def test_hoechstens_eine_grosse_aussage_je_seite(self):
        for slug, bloecke in aktive_seiten().items():
            gross = [typ for typ, _ in bloecke if typ in ("zusage", "leitsatz")]
            self.assertLessEqual(len(gross), 1, f"/{slug}/: {gross}")

    def test_jede_seite_hat_ein_nicht_text_element(self):
        nicht_text = {"zeitskala", "dauerbalken", "quartalsachse", "register", "vergleich", "zahlensatz", "nullen",
                      "produktbilder", "feature_matrix", "market_matrix", "comparison_table", "pricing_table",
                      "zusage", "leitsatz", "downloads", "schrittfolge"}
        for slug, bloecke in get_marketing_definitions().items():
            if slug in RUHEND:
                continue
            typen = {typ for typ, _ in bloecke}
            self.assertTrue(typen & nicht_text, f"/{slug}/: nur Text ({sorted(typen)})")

    def test_keine_spendenwege(self):
        # Punkt 1 der Rückmeldung vom 04.10.2026: Spendenabschnitt und „Ehrlich gesagt“-Kasten entfallen
        text = repr(aktive_seiten())
        for wort in ["Ko-fi", "ko-fi.com", "Buy Me a Coffee", "buymeacoffee", "GitHub Sponsors", "sponsors/mandariOSS",
                     "SEPA-Direkt", "Spende", "unterstuetzen", "Ehrlich gesagt"]:
            self.assertNotIn(wort, text, wort)


class ZeitskalaTests(SimpleTestCase):
    def zeitskalen(self):
        werte = [("disclosure", muster_daten.DISCLOSURE_ZEITSKALA)]
        for slug, bloecke in aktive_seiten().items():
            werte += [(slug, wert) for typ, wert in bloecke if typ == "zeitskala"]
        return werte

    def test_keine_leitlinie_durch_eine_beschriftung(self):
        # Reicht eine Beschriftung über die Linie einer späteren Marke, steht die spätere tiefer
        for name, wert in self.zeitskalen():
            marken = zeitskala_plan(wert)["marken"]
            for i, spaeter in enumerate(marken):
                for frueher in marken[:i]:
                    if frueher["rechts"] or spaeter["rechts"]:
                        continue
                    if frueher["pos"] + frueher["breite"] > spaeter["pos"]:
                        self.assertGreater(spaeter["stufe"], frueher["stufe"], f"{name}: {spaeter['frist']}")

    def test_massstab_und_bruch(self):
        plan = zeitskala_plan(muster_daten.DISCLOSURE_ZEITSKALA)
        lagen = {m["frist"]: round(m["pos"], 1) for m in plan["marken"]}
        self.assertEqual(lagen["Tag 0"], 0)
        self.assertAlmostEqual(lagen["zwei Wochen"], 14 / 30 * 61, places=0)
        self.assertEqual(lagen["Fix"], 64)
        self.assertEqual(lagen["+90 Tage"], 100)
        self.assertTrue(plan["zweite"])
        rechts = [m["frist"] for m in plan["marken"] if m["rechts"]]
        self.assertEqual(rechts, ["+90 Tage"])

    def test_dauerbalken_summiert_frueh_und_spaet(self):
        wert = dict(get_marketing_definitions()["migration"])["dauerbalken"]
        plan = dauer_plan(wert)
        umstellung = plan["zeilen"][-1]
        self.assertEqual(umstellung["art"], "meilenstein")
        self.assertEqual(umstellung["frueh"], "50%")    # 1 + 2 + 4 = 7 von 14 Wochen
        self.assertEqual(umstellung["spaet"], "100%")   # 2 + 4 + 8 = 14 Wochen


class RegisterTests(SimpleTestCase):
    def test_vergabe_bestand(self):
        wert = dict(get_marketing_definitions()["vergabe"])["register"]
        plan = register_plan(wert)
        self.assertEqual((plan["da"], plan["offen"], plan["gesamt"]), (9, 5, 14))
        self.assertEqual(plan["satz"], "9 von 14 liegen vor, 5 sind in Arbeit.")
        self.assertEqual(plan["segmente"], [True] * 9 + [False] * 5)

    def test_dokument_gliederung_vergibt_sprungmarken(self):
        dok = dokument_gliederung('<h2>1. Gegenstand und Dauer</h2><p>x</p><h2 id="eigen">Zwei</h2><h2>1. Gegenstand und Dauer</h2>')
        self.assertEqual([e["anker"] for e in dok["inhalt"]],
                         ["gegenstand-und-dauer", "eigen", "gegenstand-und-dauer-2"])
        self.assertIn('<h2 id="gegenstand-und-dauer">', dok["html"])


class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def test_rueckmeldung_vom_4_oktober(self):
        # 1 Spenden weg, 2 Register statt Kärtchen, 3 Randspalte, 4 Zeitskala, 5 Safe Harbor oben,
        # 6 Logos über die volle Breite, 7 je Seite unterschiedliche Muster
        transparenz = self.seite("/transparenz/")
        for wort in ["Ko-fi", "GitHub Sponsors", "Buy Me a Coffee", "SEPA", "Ehrlich gesagt"]:
            self.assertNotIn(wort, transparenz)
        self.assertIn('grosse-zahl', transparenz)
        vergabe = self.seite("/vergabe/")
        self.assertIn('class="reg"', vergabe)
        self.assertIn("9 von 14 liegen vor, 5 sind in Arbeit.", vergabe)
        self.assertIn('class="ablauf mt-5"', vergabe)
        disclosure = self.seite("/sicherheit/disclosure/")
        self.assertLess(disclosure.find('id="safe-harbor"'), disclosure.find('id="geltungsbereich"'))
        self.assertIn('class="zk"', disclosure)
        self.assertIn('class="zk"', self.seite("/abuse/"))
        presse = self.seite("/presse/")
        self.assertIn('class="vorschau vorschau-hell', presse)
        self.assertIn("Logo-Paket herunterladen", presse)

    def test_einladung_traegt_die_wege_rechts(self):
        for url in ["/", "/vergabe/", "/preise/", "/presse/", "/sicherheit/disclosure/", "/vergleich/"]:
            html = self.seite(url)
            einladung = html[html.rfind("band-tinte"):]
            self.assertIn("<dl", einladung, url)
            # rechts: ab 1280 px die Spalten 8–12, darunter 7–12 (sonst läuft datenschutz@mandari.de aus der Spalte)
            self.assertIn("lg:col-start-7 xl:col-span-5 xl:col-start-8", einladung, url)

    def test_dokumentseiten_mit_inhalt_und_randspalte(self):
        for url in ["/impressum/", "/datenschutz/", "/agb/", "/avv/", "/kuendigung/", "/quellen/", "/trust/"]:
            html = self.seite(url)
            self.assertIn('aria-label="Zum Dokument"', html, url)
            self.assertIn('class="dok-klebt dok-inhalt"', html, url)
        self.assertIn("<dd class=\"font-semibold\">Juli 2026</dd>", self.seite("/kuendigung/"))
