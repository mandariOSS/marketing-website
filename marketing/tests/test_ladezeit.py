"""Ladezeit: Symbole ohne JavaScript, vorgeladenes Hero-Bild passend zur Bildquelle, Schrift früh geladen."""

import re
from html import unescape
from io import StringIO

from django.core.management import call_command
from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase, TestCase

PRELOAD_BILD = re.compile(r'<link rel="preload" as="image"[^>]*>')
ATTR = re.compile(r'([\w-]+)="([^"]*)"')


def attribute(tag):
    return {name: unescape(wert) for name, wert in ATTR.findall(tag)}


class SymbolTests(SimpleTestCase):
    def test_inline_svg_ohne_javascript(self):
        html = Template('{% load icons %}{% icon "check" "w-4 h-4" %}').render(Context())
        self.assertTrue(html.startswith("<svg "))
        self.assertIn('class="w-4 h-4"', html)
        self.assertIn('aria-hidden="true"', html)
        self.assertIn('<path d="M20 6 9 17l-5-5"/>', html)

    def test_unbekanntes_symbol_ist_ein_fehler(self):
        with self.assertRaises(TemplateSyntaxError):
            Template('{% load icons %}{% icon "gibt-es-nicht" %}').render(Context())


class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def html(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def test_kein_lucide_mehr(self):
        for url in ("/", "/produkte/", "/vergleich/", "/vergleich/mandari-vs-allris/", "/kontakt/"):
            html = self.html(url)
            self.assertNotIn("lucide", html.lower(), url)
            self.assertNotIn("data-lucide", html, url)

    def test_alpine_startet_nicht_am_html_element(self):
        # x-data am <html> ließe Alpine beim Start jedes Element der Seite durchlaufen (lange Aufgabe).
        html = self.html("/produkte/")
        self.assertNotIn("x-data", html[:html.find("<head")])
        self.assertIn('document.documentElement.classList.add("dark")', html)

    def test_schrift_wird_mit_crossorigin_vorgeladen(self):
        html = self.html("/preise/")
        self.assertRegex(html, r'<link rel="preload" href="[^"]*inter-latin\.[^"]*woff2" as="font" '
                               r'type="font/woff2" crossorigin>')

    def test_vorgeladenes_bild_entspricht_der_bildquelle(self):
        # Weichen srcset oder sizes von Bild und Preload ab, lädt der Browser zwei Dateien.
        for url, mobil in (("/", True), ("/produkte/", True), ("/fraktionen/", False), ("/kommunen/", False)):
            html = self.html(url)
            hero = html[html.find('role="main"'):]
            hero = hero[:hero.find("</section>")]
            links = [attribute(tag) for tag in PRELOAD_BILD.findall(html)]
            self.assertEqual(len(links), 2 if mobil else 1, url)
            for link in links:
                self.assertEqual(link.get("fetchpriority"), "high", url)
                quellen = [attribute(tag) for tag in re.findall(r"<(?:source|img)\b[^>]*>", hero)]
                treffer = [q for q in quellen if q.get("srcset") == link["imagesrcset"]
                           and q.get("sizes") == link["imagesizes"]]
                self.assertEqual(len(treffer), 1, f"{url}: Preload ohne passende Bildquelle ({link})")
                self.assertEqual(treffer[0].get("fetchpriority", "high"), "high", url)
                if "media" in link:
                    self.assertEqual(treffer[0].get("media", "(min-width: 640px)"), link["media"], url)

    def test_ohne_hero_bild_kein_preload(self):
        self.assertNotRegex(self.html("/preise/"), PRELOAD_BILD)

    def test_hero_bilder_mit_zwischengroessen(self):
        hero = self.html("/")
        for breite in ("mobil-400", "mobil-480", "mobil-640", "mobil-780"):
            self.assertIn(f"hero-work-{breite}.webp", hero)
        for breite in (600, 800, 1200, 1600):
            self.assertIn(f"hero-insight-muenster-{breite}.webp", hero)

    def test_karriere_nicht_mehr_verlinkt(self):
        for url in ("/", "/unternehmen/", "/kontakt/"):
            self.assertNotIn('href="/karriere/"', self.html(url), url)
