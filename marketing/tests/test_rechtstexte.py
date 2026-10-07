"""Rechtstexte: Anschrift des Rechtsträgers, Lizenzangabe im Impressum und Ausrollen auf laufende Instanzen."""

import re
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase

from company.models import PRE_FOUNDING
from marketing.legal_content import LEGAL_CONTENT_DIR, load_legal_content
from marketing.models import LegalPage

STRASSE = "Robert-Koch-Straße 44"
ORT = "48149 Münster"
# Frühere Anschrift (Aegidiistraße 61/62, 48143 Münster) – darf in keinem Rechtstext zurückkehren.
ALTE_ANSCHRIFT = re.compile(r"Aegidii|Ägidii|\b48143\b", re.IGNORECASE)
ALTE_ANSCHRIFT_SEITE = re.compile(r"Aegidii|Ägidii|48143 Münster", re.IGNORECASE)

LIZENZSATZ = (
    "Die Software der mandari-Plattform ist freie Software unter der GNU Affero General Public License, "
    "Version 3 oder später (AGPL-3.0-or-later). Die Dokumentation steht unter Creative Commons Namensnennung 4.0 "
    "(CC BY 4.0). Name und Logo „mandari“ sind nicht frei lizenziert. Quellcode: github.com/mandariOSS/mandari."
)
QUELLCODE = "https://github.com/mandariOSS/mandari"


def ohne_tags(html):
    """Text eines HTML-Ausschnitts, Leerraum und Zeilenumbrüche zu je einem Leerzeichen zusammengefasst."""
    return " ".join(re.sub(r"<[^>]+>", " ", html).replace("­", "").split()).replace(" .", ".")


def abschnitt(html, titel):
    """HTML zwischen ``<h2>titel</h2>`` und der nächsten Überschrift zweiter Ordnung."""
    kopf = f"<h2>{titel}</h2>"
    return html.split(kopf, 1)[1].split("<h2", 1)[0]


class AnschriftInDenRechtstextenTests(SimpleTestCase):
    def test_keine_alte_anschrift_in_den_rechtstexten(self):
        dateien = sorted(LEGAL_CONTENT_DIR.iterdir())
        self.assertGreaterEqual(len(dateien), 5)
        for datei in dateien:
            with self.subTest(datei=datei.name):
                self.assertIsNone(ALTE_ANSCHRIFT.search(datei.read_text(encoding="utf-8")))

    def test_neue_anschrift_in_impressum_datenschutz_und_avv(self):
        texte = load_legal_content()
        # Impressum: Angaben nach § 5 DDG und Verantwortlicher nach § 18 Abs. 2 MStV
        erwartet = {"impressum": 2, "datenschutz": 1, "avv": 1}
        for slug, anzahl in erwartet.items():
            with self.subTest(slug=slug):
                text = ohne_tags(texte[slug])
                self.assertEqual(text.count(STRASSE), anzahl)
                self.assertEqual(len(re.findall(rf"{STRASSE},? {ORT}", text)), anzahl)
        self.assertIn(f"{STRASSE} {ORT} Deutschland", ohne_tags(abschnitt(texte["impressum"], "Angaben gemäß § 5 DDG")))
        self.assertIn(
            f"Sven Konopka {STRASSE}, {ORT}",
            ohne_tags(abschnitt(texte["impressum"], "Verantwortlich für den Inhalt nach § 18 Abs. 2 MStV")),
        )

    def test_unternehmensangaben_wie_im_impressum(self):
        self.assertEqual(PRE_FOUNDING.street, STRASSE)
        self.assertEqual(PRE_FOUNDING.postal_city, ORT)
        self.assertIn(f"{PRE_FOUNDING.street} {PRE_FOUNDING.postal_city}", ohne_tags(load_legal_content()["impressum"]))


class LizenzangabeImImpressumTests(SimpleTestCase):
    def setUp(self):
        self.html = load_legal_content()["impressum"]

    def test_lizenzsatz_wortgleich(self):
        self.assertEqual(self.html.count("<h2>Hinweis zu Open Source</h2>"), 1)
        self.assertEqual(ohne_tags(abschnitt(self.html, "Hinweis zu Open Source")), LIZENZSATZ)

    def test_quellcode_verlinkt(self):
        self.assertIn(
            f'<a href="{QUELLCODE}" rel="noopener" target="_blank">github.com/mandariOSS/mandari</a>.',
            abschnitt(self.html, "Hinweis zu Open Source"),
        )

    def test_lizenzhinweis_nicht_gedoppelt(self):
        self.assertEqual(self.html.count("AGPL-3.0-or-later"), 1)
        self.assertEqual(self.html.count("CC BY 4.0"), 1)
        self.assertNotIn("(Insight, Work, Session)", self.html)

    def test_kein_markenzeichen_und_keine_markenrichtlinie(self):
        self.assertNotIn("®", self.html)
        self.assertNotIn("&reg;", self.html)
        self.assertNotIn("markenrichtlinie", self.html.lower())


class RechtsseitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, url):
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200, url)
        return " ".join(response.content.decode("utf-8").split())

    def test_seiten_nennen_die_neue_anschrift(self):
        for url in ("/impressum/", "/datenschutz/", "/avv/", "/unternehmen/", "/kontakt/"):
            with self.subTest(url=url):
                html = self.seite(url)
                self.assertIn(STRASSE, html)
                self.assertIn(ORT, html)
                self.assertIsNone(ALTE_ANSCHRIFT_SEITE.search(html))
        self.assertIn(f"{STRASSE}, {ORT}", self.seite("/unternehmen/"))

    def test_impressum_zeigt_lizenzsatz_mit_link(self):
        html = self.seite("/impressum/")
        text = ohne_tags(html)
        self.assertIn(LIZENZSATZ.removesuffix(" Quellcode: github.com/mandariOSS/mandari."), text)
        self.assertIn(f'href="{QUELLCODE}"', html)

    def test_refresh_seeded_page_rollt_rechtstexte_aus(self):
        """Laufende Instanzen: Die alte Fassung in der Datenbank wird mit --force ersetzt, sie bleibt als Revision."""
        alt = {STRASSE: "Aegidiistraße 61/62", ORT: "48143 Münster"}
        for slug in ("impressum", "datenschutz", "avv"):
            with self.subTest(slug=slug):
                page = LegalPage.objects.get(slug=slug)
                for neu, vorher in alt.items():
                    page.body = page.body.replace(neu, vorher)
                page.save()
                page.save_revision().publish()
                revisionen = page.revisions.count()
                self.assertIsNotNone(ALTE_ANSCHRIFT_SEITE.search(self.seite(f"/{slug}/")))

                # ohne --force bleibt der Inhalt in der Datenbank unangetastet
                call_command("refresh_seeded_page", slug, stdout=StringIO())
                page.refresh_from_db()
                self.assertIn("Aegidiistraße 61/62", page.body)

                call_command("refresh_seeded_page", slug, "--force", stdout=StringIO())
                page.refresh_from_db()
                self.assertEqual(page.body, load_legal_content()[slug])
                self.assertEqual(page.revisions.count(), revisionen + 1)
                self.assertFalse(page.has_unpublished_changes)
                html = self.seite(f"/{slug}/")
                self.assertIn(STRASSE, html)
                self.assertIsNone(ALTE_ANSCHRIFT_SEITE.search(html))
