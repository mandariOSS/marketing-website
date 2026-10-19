"""/llms.txt: Übersicht für Sprachmodelle aus Titeln und Beschreibungen des CMS (mandari#939)."""

import re
from io import StringIO
from urllib.parse import urlsplit

from django.core.management import call_command
from django.test import TestCase, override_settings
from wagtail.models import Page

from marketing.models import MarketingPage

LINK = re.compile(r"^- \[(?P<titel>[^\]]+)\]\((?P<adresse>[^)]+)\)(?:: (?P<beschreibung>.+))?$")


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["mandari.de", "testserver"])
class LlmsTxtTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())

    def _text(self):
        antwort = self.client.get("/llms.txt", HTTP_HOST="mandari.de")
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort["Content-Type"], "text/plain; charset=utf-8")
        return antwort.content.decode()

    def test_aufbau_nach_llmstxt_org(self):
        zeilen = self._text().splitlines()

        self.assertEqual(zeilen[0], "# mandari")
        self.assertTrue(zeilen[2].startswith("> "), "Kurzbeschreibung aus der Meta-Description der Startseite")
        self.assertIn("## Produkte", zeilen)
        self.assertEqual(zeilen[-1].startswith("- ["), True)

    def test_titel_und_beschreibung_aus_dem_cms(self):
        seite = Page.objects.get(slug="ratsinformationssystem").specific
        zeile = next(z for z in self._text().splitlines() if "/ratsinformationssystem/)" in z)

        treffer = LINK.match(zeile)
        self.assertIsNotNone(treffer, zeile)
        self.assertEqual(treffer["titel"], seite.seo_title or seite.title)
        self.assertEqual(treffer["adresse"], "https://mandari.de/ratsinformationssystem/")
        self.assertEqual(treffer["beschreibung"], " ".join(seite.search_description.split()))

    def test_jeder_link_fuehrt_auf_eine_seite_der_website(self):
        for zeile in self._text().splitlines():
            treffer = LINK.match(zeile)
            if not treffer:
                continue
            pfad = urlsplit(treffer["adresse"]).path
            with self.subTest(pfad=pfad):
                self.assertEqual(self.client.get(pfad, HTTP_HOST="mandari.de").status_code, 200)

    def test_zurueckgezogene_seite_entfaellt(self):
        Page.objects.get(slug="vergabe").specific.unpublish()

        self.assertNotIn("/vergabe/", self._text())

    def test_neue_beschreibung_wirkt_ohne_codeaenderung(self):
        seite = MarketingPage.objects.get(slug="preise")
        seite.search_description = "Neue Beschreibung der Preise."
        seite.save_revision().publish()

        self.assertIn("/preise/): Neue Beschreibung der Preise.", self._text())

    def test_grunddaten_anwendung_dokumentation_code(self):
        text = self._text()

        self.assertIn("https://mandari.de/insight/", text)
        self.assertIn("https://mandari.de/oparl/v1/system", text)
        self.assertIn("https://docs.mandari.de/llms.txt", text)
        self.assertIn("https://github.com/mandariOSS", text)
