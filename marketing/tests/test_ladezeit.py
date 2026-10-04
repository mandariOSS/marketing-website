"""Ladezeit: Symbole ohne JavaScript, vorgeladenes Hero-Bild passend zur Bildquelle, Schrift früh geladen,
kritisches CSS inline und styles.css ohne Blockade."""

import re
from html import unescape
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.template import Context, Template, TemplateSyntaxError
from django.test import SimpleTestCase, TestCase, override_settings

from marketing.templatetags import stile

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


class StileTests(SimpleTestCase):
    def render(self):
        return Template("{% load stile %}{% stile %}").render(Context())

    @override_settings(DEBUG=False)
    def test_kritisches_css_inline_und_styles_ohne_blockade(self):
        with mock.patch.object(stile, "kritisches_css", return_value=".hero{padding-top:3.5rem}"):
            html = self.render()
        self.assertTrue(html.startswith("<style>.hero{padding-top:3.5rem}</style>"))
        link = re.search(r'<link rel="stylesheet" href="([^"]+)" media="print" id="stile">', html)
        self.assertIsNotNone(link, html)
        self.assertIn(f"<script>{stile.LADER}</script>", html)
        self.assertIn(f'<noscript><link rel="stylesheet" href="{link.group(1)}"></noscript>', html)
        # Kein preload as=style (Chrome lädt das mit höchster Priorität, Lighthouse zählt es als blockierend)
        # und kein Inline-Handler (Content-Security-Policy): Das Skript schaltet um und hebt „vorab“ auf.
        self.assertNotIn('as="style"', html)
        self.assertNotIn("onload", html)
        self.assertIn('l.media="all"', stile.LADER)
        self.assertIn('classList.remove("vorab")', stile.LADER)
        # Sichtbar erst mit Alpine (x-cloak), spätestens mit load
        self.assertIn('"alpine:initialized"', stile.LADER)
        self.assertIn('addEventListener("load"', stile.LADER)

    @override_settings(DEBUG=False)
    def test_ohne_kritisches_css_blockierend_wie_bisher(self):
        with mock.patch.object(stile, "kritisches_css", return_value=""):
            html = self.render()
        self.assertRegex(html, r'^<link rel="stylesheet" href="[^"]*styles\.css">$')

    @override_settings(DEBUG=True)
    def test_entwicklung_ohne_kritisches_css(self):
        # Mit DEBUG passt das Ergebnis immer zum gerade gebauten styles.css (npm run watch:css baut nur dieses).
        with mock.patch.object(stile, "kritisches_css", return_value=".hero{}") as gelesen:
            html = self.render()
        gelesen.assert_not_called()
        self.assertNotIn("<style>", html)

    def test_kritisches_css_ohne_schliessendes_tag(self):
        with (
            mock.patch.object(stile.finders, "find", return_value=__file__),
            mock.patch("builtins.open", mock.mock_open(read_data="a{}</style><script>")),
        ):
            stile._gelesen.clear()
            self.assertEqual(stile.kritisches_css(), "")
        stile._gelesen.clear()


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
                # Vorgeladen wird das AVIF; Browser ohne AVIF überspringen den Preload wegen type.
                self.assertEqual(link.get("type"), "image/avif", url)
                self.assertEqual(treffer[0].get("type"), "image/avif", url)
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
