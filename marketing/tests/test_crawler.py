"""Crawler-Seite /crawler/ (mandariOSS/mandari#1027): vollständige Kennung, Abruf-Adresse und Kontakt, Takt aus
marketing/muster_daten.py; frühere Angaben, die nicht mehr stimmten, kehren nicht zurück."""

import re
from pathlib import Path

from django.template.loader import get_template
from django.test import TestCase

from marketing import muster_daten


def text(html):
    """Fließtext ohne Zeilenumbrüche aus dem Template, damit Sätze über Zeilen hinweg gefunden werden."""
    return " ".join(html.split())


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

    def test_takt_je_hostname_und_zwei_gleichzeitig_nur_im_abgleich(self):
        # Gedrosselt wird je Hostname über Redis für alle Dienste; die Grenze von zwei offenen Anfragen ist eine
        # Semaphore je Prozess (host_pacing.py) und gilt deshalb nur für den Abgleich, nicht für alle Dienste.
        html = self.html()
        self.assertIn("<b>eine Anfrage pro Sekunde</b> je Hostname, über alle unsere Dienste zusammen", html)
        self.assertIn("Unser Abgleich hält dabei höchstens zwei Anfragen gleichzeitig offen", html)
        self.assertNotIn("<b>zwei</b>", html)
        self.assertNotIn("pro Sekunde</b> je Server", html)

    def test_aenderungsfenster_seit_dem_letzten_erfolgreichen_durchlauf(self):
        # Beginn des letzten vollständig gelesenen Laufs (auch inkrementell), nicht des letzten Vollabgleichs
        html = self.html()
        self.assertIn(
            "seit dem letzten erfolgreichen Durchlauf geändert hat, meist also seit dem vorigen vor 10 Minuten", html
        )
        self.assertNotIn("seit dem letzten vollständigen Abgleich", html)

    def test_zeitfenster_des_vollabgleichs_ab_1_uhr(self):
        # Der geplante Vollabgleich startet um 1 Uhr; ein Fenster, das später beginnt, führte nie zu einem Vollabgleich
        self.assertEqual(text(self.html()).count("Zeitfenster ab 1 Uhr nachts"), 2)

    def test_vollabgleich_von_hand_und_ende_des_fensters(self):
        # Ein Vollabgleich, der mit dem Fenster endet, wird nicht fortgesetzt: In der nächsten Nacht beginnt er von
        # vorn. Von Hand (Admin-Trigger, sync --full) startet er zu jeder Tageszeit, auch dann im Fenster.
        html = text(self.html())
        self.assertIn("endet der Vollabgleich mit dem Fenster und beginnt in der nächsten Nacht von vorn", html)
        self.assertIn("Von Hand starten wir ihn nur ausnahmsweise", html)
        self.assertIn("ein vereinbartes Zeitfenster gilt auch dann", html)
        self.assertNotIn("folgt in der nächsten Nacht", html)

    def test_erstpruefung_mit_hoechstens_fuenf_anfragen(self):
        # probe-ris (mandari#1031): höchstens fünf Anfragen, Weiterleitungen mitgezählt, im Takt je Host; die
        # Vergleichsanfrage nach HTTP 403 mit python-httpx wie im Abgleich, keine Browserkennung
        html = text(self.html())
        self.assertIn("prüfen wir mit höchstens fünf Anfragen", html)
        self.assertIn("je Abgleich und je Erstprüfung höchstens eine Vergleichsanfrage", html)
        self.assertNotIn("Mozilla", html)

    def test_dokumentabruf_ohne_freischaltung(self):
        # Der Dokumentabruf ist je Quelle standardmäßig an und lässt sich nur abschalten (sync_config file_downloads)
        html = self.html()
        self.assertIn("Für einzelne Systeme schalten wir den Dokumentabruf ab", html)
        self.assertNotIn("freigeschaltet", html)

    def test_kopf_mit_einem_satz(self):
        # Slop-Regel 2: Überschrift, ein erklärender Satz, genau ein Aufruf
        kopf = re.search(r'<section class="band-hell hero">(.*?)</section>', self.html(), re.S).group(1)
        lead = text(re.search(r'<p class="t-lead[^"]*">(.*?)</p>', kopf, re.S).group(1))
        self.assertEqual(len(re.findall(r"[.!?](?:\s|$)", lead)), 1, lead)
        self.assertEqual(kopf.count("<a "), 1)

    def test_einladung_ohne_abruf_adresse(self):
        # Eine IP-Adresse ist kein Kontaktweg; sie steht nur in der Kennung
        self.assertNotIn("Abruf-Adresse", [weg["label"] for weg in muster_daten.WEGE["crawler"]])
        self.assertEqual(self.html().count(muster_daten.CRAWLER_ADRESSE), 1)

    def test_keine_zusage_gegen_einen_adresswechsel(self):
        # Ob die Abruf-Adresse bleibt, ist offen; zugesagt wird nur, Sperren nicht durch einen Wechsel zu umgehen
        html = text(self.html())
        self.assertIn("Um eine Sperre zu umgehen, wechseln wir weder Kennung noch Adresse.", html)
        self.assertNotIn("Kennung und Adresse wechseln wir nicht", html)

    def test_keine_betriebsinterna_im_quelltext(self):
        # Das Repository ist öffentlich: keine internen Hostnamen und keine Nummern aus dem privaten Repository
        dateien = [Path(muster_daten.__file__), Path(get_template("marketing/crawler.html").origin.name)]
        for datei in dateien:
            inhalt = datei.read_text(encoding="utf-8")
            for intern in ["web01", "intern#"]:
                self.assertNotIn(intern, inhalt, f"{datei.name}: {intern}")

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
            "Nur für Kommunen, die wir dafür freigeschaltet haben",
        ]:
            self.assertNotIn(alt, html, alt)
