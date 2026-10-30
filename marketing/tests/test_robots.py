"""robots.txt: Crawler sollen ihr Budget für Seiten mit Inhalt nutzen, nicht für Varianten und Dateien."""

from django.test import SimpleTestCase, override_settings


@override_settings(SITE_URL="https://mandari.de")
class RobotsTests(SimpleTestCase):
    def _zeilen(self):
        antwort = self.client.get("/robots.txt")
        self.assertEqual(antwort.status_code, 200)
        self.assertTrue(antwort["Content-Type"].startswith("text/plain"))
        return antwort.content.decode("utf-8").splitlines()

    def test_varianten_und_dateien_gesperrt(self):
        zeilen = self._zeilen()
        for regel in (
            "/oparl/",
            "/insight/dokumente/",
            "/*?download=",
            "/*&download=",
            "/*?subject=",
            "/insight/?body=",
            "/insight/kommunen/?",
        ):
            self.assertIn(f"Disallow: {regel}", zeilen)

    def test_inhalte_bleiben_erlaubt(self):
        """``/oparl/`` trifft die Seite ``/oparl-schnittstelle/`` nicht, ``/insight/kommunen/?`` nicht die Auswahl."""
        gesperrt = [z.removeprefix("Disallow: ") for z in self._zeilen() if z.startswith("Disallow: ")]
        for pfad in ("/oparl-schnittstelle/", "/insight/", "/insight/kommunen/", "/insight/vorgaenge/x/", "/kontakt/"):
            self.assertFalse([r for r in gesperrt if "*" not in r and pfad.startswith(r)], pfad)

    def test_sitemaps(self):
        zeilen = self._zeilen()
        self.assertIn("Sitemap: https://mandari.de/sitemap.xml", zeilen)
        self.assertIn("Sitemap: https://mandari.de/sitemap-insight-index.xml", zeilen)
