"""Fehlerseiten: 404 im Seiten-Design mit Wegweisern, 500 statisch ohne Datenbank."""

import re
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from marketing import fehlerseiten


@override_settings(SITE_URL="https://mandari.de")
class NichtGefundenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())

    def test_status_404_mit_kopf_fusszeile_und_wegweisern(self):
        antwort = self.client.get("/gibt-es-nicht/")
        self.assertEqual(antwort.status_code, 404)
        html = antwort.content.decode("utf-8")
        self.assertIn("<title>Seite nicht gefunden | mandari</title>", html)
        self.assertIn("Diese Seite gibt es nicht.", html)
        self.assertEqual(html.count('role="banner"'), 1)
        self.assertEqual(html.count('role="contentinfo"'), 1)
        main = re.search(r"<main.*?</main>", html, re.S).group(0)
        for ziel, text in (
            ("/", "Zur Startseite"),
            ("/produkte/", "Produkte"),
            ("/preise/", "Preise"),
            ("/insight/", "Bürgerportal"),
            ("/kontakt/", "Kontakt"),
        ):
            self.assertRegex(main, rf'<a href="{re.escape(ziel)}"[^>]*>{text}</a>')

    def test_nicht_fuer_suchmaschinen(self):
        html = self.client.get("/gibt-es-nicht/").content.decode("utf-8")
        kopf = html[: html.find("</head>")]
        self.assertIn('<meta name="robots" content="noindex">', kopf)
        # Kein Hero-Bild einer anderen Seite vorladen
        self.assertNotIn('rel="preload" as="image"', kopf)

    def test_auch_unter_tieferen_pfaden(self):
        antwort = self.client.get("/vergleich/gibt-es-nicht/")
        self.assertEqual(antwort.status_code, 404)
        self.assertContains(antwort, "Wohin möchten Sie?", status_code=404)


class ServerfehlerTests(SimpleTestCase):
    # SimpleTestCase verbietet Datenbankzugriffe: Die Fehlerseite muss ohne Datenbank auskommen.
    def test_statisch_ohne_datenbank(self):
        antwort = fehlerseiten.server_error(RequestFactory().get("/irgendwo/"))
        self.assertEqual(antwort.status_code, 500)
        html = antwort.content.decode("utf-8")
        self.assertIn("Da ist etwas schiefgegangen.", html)
        self.assertIn('<meta name="robots" content="noindex">', html)
        self.assertIn('href="https://status.mandari.de/"', html)
        # Kein Inline-Code: Für die Fehlerseite gibt es keine Hashes in der Content-Security-Policy
        self.assertNotRegex(html, r"<script(?![^>]*\bsrc=)[^>]*>|<style\b")

    def test_notfalltext_wenn_die_vorlage_scheitert(self):
        with mock.patch.object(fehlerseiten, "render_to_string", side_effect=ValueError("Manifest fehlt")):
            with self.assertLogs("marketing.fehlerseiten", "ERROR"):
                antwort = fehlerseiten.server_error(RequestFactory().get("/"))
        self.assertEqual(antwort.status_code, 500)
        self.assertIn("Da ist etwas schiefgegangen.", antwort.content.decode("utf-8"))

    def test_als_handler500_eingetragen(self):
        from website import urls

        self.assertEqual(urls.handler500, "marketing.fehlerseiten.server_error")
