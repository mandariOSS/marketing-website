"""Crawler-Seite /crawler/ (mandariOSS/mandari#1027): vollständige Kennung, Abruf-Adresse und Kontakt, Takt aus
marketing/muster_daten.py; frühere Angaben, die nicht mehr stimmten, kehren nicht zurück."""

from django.test import TestCase

from marketing import muster_daten


class CrawlerSeiteTests(TestCase):
    def html(self):
        antwort = self.client.get("/crawler/")
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode("utf-8")

    def test_kennung_adresse_und_kontakt(self):
        html = self.html()
        # Vollständiger User-Agent wie shared/mandari_oparl/crawler.py im mandari-Repository (Version als Platzhalter)
        self.assertIn("mandari-ingestor/&lt;Version&gt; (+https://mandari.de/crawler/; support@mandari.de)", html)
        # Abruf-Adresse mit eigener Sprungmarke, damit man sie direkt verlinken und übernehmen kann
        self.assertIn('id="abruf-adresse"', html)
        self.assertIn(muster_daten.CRAWLER_ADRESSE, html)
        self.assertIn("Über IPv6 rufen wir nicht ab", html)
        self.assertIn(f'href="{muster_daten.CRAWLER_MAILTO}"', html)
        self.assertIn(muster_daten.CRAWLER_ABRUFREGELN, html)

    def test_takt_und_haeufigkeit_aus_den_daten(self):
        html = self.html()
        self.assertIn("<b>eine Anfrage pro Sekunde</b>", html)
        for zeile in muster_daten.CRAWLER_TAKT["zeilen"]:
            self.assertIn(zeile["abruf"], html)
            self.assertIn(zeile["wann"], html)

    def test_robots_beispiel_fuer_unser_token(self):
        self.assertIn("User-agent: mandari-ingestor\nDisallow: /</code>", self.html().replace("\r\n", "\n"))

    def test_keine_ueberholten_angaben(self):
        html = self.html()
        for alt in [
            "mandari-ingestor (+https://mandari.de/crawler)",
            "alle zwei Sekunden je Server",
            "alle zwei Sekunden pro Server",
            "keine parallelen Zugriffe",
            "nur bei tatsächlichen Änderungen",
            "hello@mandari.de",
        ]:
            self.assertNotIn(alt, html, alt)
