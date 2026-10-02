"""Hintergrundbänder und Produktfarben: Reihenfolge der Bänder, Produkterkennung, Darstellung der Seiten."""

import re
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.utils.safestring import mark_safe

from marketing.templatetags.baender import band_folge, kernsatz_html, produkt_aus

BAND = re.compile(r'<(?:section|div|nav|article)[^>]*class="[^"]*\bband-([a-z]+)\b')


def baender_der_seite(html):
    """Bänder in der Reihenfolge des Hauptbereichs (ohne Fußzeile)."""
    haupt = html[html.find('role="main"'):html.find('role="contentinfo"')]
    return BAND.findall(haupt)


class BandFolgeTests(SimpleTestCase):
    def test_hero_hell_wechsel_einladung_dunkel(self):
        typen = ["hero", "mandari_cards", "split_rows", "feature_matrix", "gradient_cta"]
        self.assertEqual(band_folge(typen), ["hell", "grau", "hell", "grau", "tinte"])

    def test_nie_zwei_gleiche_baender_nebeneinander(self):
        typen = ["hero", "pricing_table", "mandari_cards", "gradient_cta", "feature_matrix",
                 "two_column_use_case", "mandari_cards", "accordion_faq", "gradient_cta"]
        baender = band_folge(typen)
        self.assertEqual(baender[3], "marke")  # Einladung mitten auf der Seite
        self.assertEqual(baender[-1], "tinte")
        for links, rechts in zip(baender, baender[1:]):
            self.assertNotEqual(links, rechts)

    def test_zusaetze_und_fortlaufende_artikel_bleiben_auf_dem_band(self):
        typen = ["hero", "trust_banner", "mandari_cards", "numbered_article", "disclaimer_box",
                 "numbered_article", "numbered_article", "gradient_cta"]
        self.assertEqual(band_folge(typen), ["hell", "hell", "grau", "hell", "hell", "hell", "hell", "tinte"])

    def test_produktseite_hero_in_der_produktflaeche(self):
        typen = ["hero", "mandari_cards", "two_column_use_case", "gradient_cta"]
        self.assertEqual(band_folge(typen, produkt="work"), ["work", "hell", "grau", "tinte"])

    def test_rechtstexte_ruhig(self):
        typen = ["hero", "richtext_section", "richtext_section", "disclaimer_box"]
        self.assertEqual(band_folge(typen, ruhig=True), ["grau", "hell", "hell", "hell"])


class ProduktTests(SimpleTestCase):
    def test_eindeutiger_bezug(self):
        self.assertEqual(produkt_aus("Bürgerportal mandari Insight"), "insight")
        self.assertEqual(produkt_aus("Verwaltungs-RIS mandari Session"), "session")
        self.assertEqual(produkt_aus("Work (Fraktionen)"), "work")

    def test_mehrere_oder_keins(self):
        self.assertEqual(produkt_aus("Session · Work · Insight"), "")
        self.assertEqual(produkt_aus("Ein Datenbestand"), "")
        self.assertEqual(produkt_aus("Workshop für Ihre Fraktion"), "")

    def test_kernsatz_nur_bei_gerendertem_text(self):
        html = mark_safe(
            "<p>Sitzungsdienst ohne Medienbrüche. Das Ratsinformationssystem führt Ihren Sitzungsdienst von der "
            "Tagesordnung bis zur freigegebenen Niederschrift.</p>"
        )
        self.assertIn('<span class="kernsatz">Sitzungsdienst ohne Medienbrüche.</span> Das', kernsatz_html(html))
        self.assertEqual(kernsatz_html("<p>Nicht maskiert. " + "x" * 200 + "</p>"), "<p>Nicht maskiert. " + "x" * 200 + "</p>")


class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def test_benachbarte_baender_unterscheiden_sich(self):
        for url in ["/", "/produkte/", "/fraktionen/", "/kommunen/", "/preise/", "/unternehmen/", "/presse/",
                    "/roadmap/", "/vergabe/", "/open-source/", "/karriere/"]:
            baender = baender_der_seite(self.seite(url))
            self.assertGreater(len(baender), 2, url)
            for links, rechts in zip(baender, baender[1:]):
                self.assertNotEqual(links, rechts, f"{url}: zweimal {links} nebeneinander ({baender})")

    def test_startseite_und_produkte_zeigen_drei_produktflaechen(self):
        for url in ["/", "/produkte/"]:
            html = self.seite(url)
            for produkt in ["session", "work", "insight"]:
                self.assertEqual(html.count(f'class="produkt produkt-{produkt} '), 1, f"{url}: {produkt}")
        # Echter Screenshot nur bei Insight; die Startseite zeigt ihn schon im Hero
        produkte = self.seite("/produkte/")
        insight = produkte[produkte.find('id="insight"'):]
        self.assertIn("insight-muenster-1280.webp", insight[:insight.find("</article>")])
        self.assertEqual(produkte.count("insight-muenster-1280.webp"), 1)

    def test_produktseiten_tragen_ihre_flaeche(self):
        self.assertEqual(baender_der_seite(self.seite("/fraktionen/"))[0], "work")
        self.assertEqual(baender_der_seite(self.seite("/kommunen/"))[0], "session")

    def test_einladung_am_ende_dunkel(self):
        for url in ["/produkte/", "/preise/", "/unternehmen/"]:
            self.assertEqual(baender_der_seite(self.seite(url))[-1], "tinte", url)

    def test_kontakt_hat_ueberschrift(self):
        self.assertIn(">Sprechen wir über Ihre Verwaltung.</h1>", self.seite("/kontakt/"))
