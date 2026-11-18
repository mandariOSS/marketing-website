"""
Bildschirme im Raster (Muster 11): Bildliste und Dateien, Weg auf der Startseite, Tagesfolge und Kette.

Die Bilder stammen aus der öffentlichen Demo und aus dem Bürgerportal (marketing/bildschirme.py). Geprüft wird,
dass jede eingetragene Breite als AVIF und WebP vorliegt, dass Breite und Höhe im HTML zur Datei passen (sonst
springt die Seite beim Laden) und dass die Seeds nur Bilder nennen, die es gibt.
"""

import re
from io import StringIO

from django.contrib.staticfiles import finders
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from PIL import Image

from marketing.bildschirme import BILDSCHIRME, BREITEN, ORDNER, bildschirm, breiten
from marketing.management.commands.migrate_pages_to_streamfield import get_marketing_definitions


class BildlisteTests(SimpleTestCase):
    def test_jede_breite_liegt_als_avif_und_webp_vor(self):
        for name in BILDSCHIRME:
            self.assertTrue(breiten(name), name)
            for breite in breiten(name):
                for endung in ("avif", "webp"):
                    datei = f"{name}-{breite}.{endung}"
                    self.assertIsNotNone(finders.find(f"{ORDNER}/{datei}"), datei)

    def test_keine_breite_ueber_der_vorlage(self):
        # Hochgerechnete Dateien wären unscharf und größer als nötig
        for name, daten in BILDSCHIRME.items():
            self.assertLessEqual(max(breiten(name)), daten["groesse"][0], name)
            self.assertGreaterEqual(daten["groesse"][0], BREITEN[1], f"{name}: Vorlage zu klein für doppelte Dichte")

    def test_seitenverhaeltnis_im_html_passt_zur_datei(self):
        for name, daten in BILDSCHIRME.items():
            breite, hoehe = daten["groesse"]
            kleinste = breiten(name)[0]
            with Image.open(finders.find(f"{ORDNER}/{name}-{kleinste}.webp")) as bild:
                self.assertEqual(bild.width, kleinste, name)
                self.assertAlmostEqual(bild.height, hoehe * kleinste / breite, delta=1, msg=name)

    def test_angaben_fuer_das_bild(self):
        b = bildschirm("work-start")
        self.assertIn("work-start-640.avif 640w", b["srcset_avif"])
        self.assertIn("work-start-1600.webp 1600w", b["srcset"])
        self.assertEqual((b["breite"], b["hoehe"]), BILDSCHIRME["work-start"]["groesse"])
        self.assertTrue(b["alt"] and b["herkunft"])
        self.assertIsNone(bildschirm("gibt-es-nicht"))

    def test_seeds_nennen_nur_vorhandene_bilder(self):
        genannt = []
        for slug, bloecke in get_marketing_definitions().items():
            for typ, wert in bloecke:
                if typ == "tagesfolge":
                    genannt += [(slug, tag["bild"]) for tag in wert["tage"]]
                elif typ == "kette":
                    genannt.append((slug, wert["bild"]))
        self.assertTrue(genannt)
        for slug, name in genannt:
            self.assertIn(name, BILDSCHIRME, f"/{slug}/")


class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def test_startseite_fuehrt_eine_sitzung_durch_die_drei_produkte(self):
        html = self.seite("/")
        self.assertIn("Eine Ratssitzung, drei Blickwinkel.", html)
        halte = re.findall(r'<li class="weg-halt produkt-(\w+)">', html)
        self.assertEqual(halte, ["session", "work", "insight"])
        for name in ("session-tagesordnung", "work-start", "insight-beschluesse"):
            self.assertIn(f"images/bildschirme/{name}-", html)
        # Die Zahlen des Bürgerportals stehen mit ihrem Stand im Satz, nicht als Platzhalter
        self.assertNotIn("[kommunen]", html)
        self.assertRegex(html, r"aus \d+ Kommunen durchsuchbar")
        self.assertRegex(html, r"Stand \d{1,2}\. \w+ 20\d\d")
        # Jeder Halt führt auf die Seite seines Produkts
        for ziel in ('href="/kommunen/"', 'href="/fraktionen/"', 'href="/insight/"'):
            self.assertIn(ziel, html)

    def test_bildschirme_haben_groesse_text_und_herkunft(self):
        html = self.seite("/")
        bilder = re.findall(r'<figure class="schirm".*?</figure>', html, re.S)
        self.assertEqual(len(bilder), 3)
        for bild in bilder:
            self.assertRegex(bild, r'<source type="image/avif" srcset="[^"]+" sizes="[^"]+">')
            self.assertRegex(bild, r'width="\d+" height="\d+" alt="[^"]{20,}" loading="lazy"')
            self.assertRegex(bild, r"<figcaption>(Aus der Demo|Echte Daten): [^<]+</figcaption>")

    def test_fraktionen_zeigt_die_sitzungswoche(self):
        html = self.seite("/fraktionen/")
        self.assertIn("Eine Sitzungswoche mit mandari Work.", html)
        achse = re.search(r'<div class="tf-achse" role="radiogroup".*?</div>', html, re.S).group(0)
        felder = re.findall(r'<input type="radio" name="([^"]+)"( checked)?>', achse)
        self.assertEqual(len(felder), 4)
        self.assertEqual(len({name for name, _ in felder}), 1, "eine Gruppe, damit die Pfeiltasten wechseln")
        self.assertEqual([bool(gewaehlt) for _, gewaehlt in felder], [True, False, False, False])
        # Jeder Tag steht auch ohne Achse vollständig da (Handy, Browser ohne :has): Zeitpunkt, Titel, Text, Bild
        tage = re.findall(r'<article class="tf-tag">.*?</article>', html, re.S)
        self.assertEqual(len(tage), 4)
        for tag in tage:
            self.assertRegex(tag, r'<p class="wann">[^<]+: [^<]+</p>')
            self.assertIn('<figure class="schirm"', tag)
        # Was die Begriffe vorher trugen, steht jetzt im Register; die Verweise bleiben
        for text in ("Anträge und Anfragen", "Recherche", "Vertraulichkeit", "docs.mandari.de/work/fraktions-api/",
                     'href="/trust/"', "Funktioniert mit dem RIS Ihrer Kommune"):
            self.assertIn(text, html)

    def test_kommunen_zeigt_den_sitzungsdienst_als_kette(self):
        html = self.seite("/kommunen/")
        self.assertIn("Einmal erfasst, bis zur Niederschrift verwendet.", html)
        self.assertEqual(re.findall(r'<span class="kette-nr">(\d)</span>', html), ["1", "2", "3", "4", "5", "6"])
        self.assertEqual(html.count('data-spalte="Daraus entsteht"'), 6)
        self.assertIn("images/bildschirme/session-sitzung-", html)
        # Sprungmarke und die Verweise auf die Sachseiten bleiben (Suchbegriffe, #939)
        self.assertIn('id="bausteine"', html)
        for ziel in ("/ratsinformationssystem/", "/sitzungsmanagement/", "/buergerinformationssystem/",
                     "/oparl-schnittstelle/", "/insight/"):
            self.assertIn(f'href="{ziel}"', html)
