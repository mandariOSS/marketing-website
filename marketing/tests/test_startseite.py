"""Hero der Startseite: Text links, rechts eine Figur aus drei echten Produktbildern."""

import re
from io import StringIO

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import TestCase

IMG = re.compile(r"<img\b[^>]*>")
SRC = re.compile(r"""\{% static '([^']+)' %\}""")


class StartseitenHeroTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())

    def setUp(self):
        html = self.client.get("/").content.decode("utf-8")
        haupt = html[html.find('role="main"'):]
        self.hero = haupt[:haupt.find("</section>")]
        self.html = html

    def bilder(self):
        return IMG.findall(self.hero)

    def test_ein_aufruf_und_ein_textlink(self):
        self.assertEqual(self.hero.count('class="btn-primary"'), 1)
        self.assertEqual(self.hero.count('class="textlink"'), 1)
        self.assertIn("Ratsinformationen im Bürgerportal ansehen", self.hero)

    def test_eine_figur_mit_unsichtbarer_beschreibung(self):
        self.assertEqual(self.hero.count("<figure"), 1)
        self.assertRegex(self.hero, r'<figcaption class="sr-only">[^<]{40,}</figcaption>')

    def test_drei_echte_bilder_mit_alt_und_masszahlen(self):
        bilder = self.bilder()
        self.assertEqual(len(bilder), 3)
        for produkt, img in zip(["session", "work", "insight-muenster"], bilder):
            self.assertIn(f"hero-{produkt}-800.webp", img)
            self.assertIn('width="800"', img)
            self.assertIn('height="500"', img)
            alt = re.search(r'alt="([^"]*)"', img).group(1)
            self.assertGreater(len(alt), 40, produkt)
            self.assertTrue(alt.startswith("mandari "), produkt)

    def test_vorderes_bild_wird_sofort_geladen(self):
        insight = self.bilder()[-1]
        self.assertNotIn('loading="lazy"', insight)
        self.assertIn('fetchpriority="high"', insight)
        self.assertNotIn('loading="lazy"', self.bilder()[1])

    def test_kein_zweiter_grosser_screenshot(self):
        # Der frühere Screenshot über volle Breite entfällt; Insight steht nur noch in der Figur.
        self.assertNotIn("insight-muenster-1280.webp", self.html)
        self.assertEqual(self.html.count("<figure"), 1)

    def test_bilddateien_vorhanden(self):
        with open("templates/marketing/landing.html", encoding="utf-8") as fh:
            vorlage = fh.read()
        dateien = set(SRC.findall(vorlage))
        self.assertGreaterEqual(len([d for d in dateien if d.startswith("images/startseite/hero-")]), 10)
        for datei in dateien:
            self.assertTrue(finders.find(datei), datei)
