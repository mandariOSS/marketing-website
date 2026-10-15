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
        self.assertIn("nur über IPv4", html)
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
        self.assertIn("Jeder Abgleich hält dabei höchstens zwei Anfragen gleichzeitig offen", html)
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
        self.assertIn("Ob eine Kommune für uns infrage kommt, prüfen wir mit höchstens fünf Anfragen", html)
        self.assertIn("liegen zwischen zwei Kommunen zusätzlich 2 Sekunden", html)
        self.assertIn("je Server und Abgleich sowie je Erstprüfung höchstens eine Vergleichsanfrage", html)
        self.assertIn("im Takt und ohne Weiterleitung", html)
        self.assertNotIn("Mozilla", html)

    def test_dokumentabruf_ohne_freischaltung(self):
        # Der Dokumentabruf ist je Quelle standardmäßig an und lässt sich nur abschalten (sync_config file_downloads)
        html = self.html()
        self.assertIn("Für einzelne Systeme schalten wir den Dokumentabruf ab", html)
        self.assertNotIn("freigeschaltet", html)

    def test_fehlende_listen_robots_und_dokumente_wie_in_den_abrufregeln(self):
        # docs/ABRUFREGELN.md im mandari-Repository: vermerkte Listen inkrementell einmal am Tag (MISSING_LIST_RECHECK),
        # bei nicht erreichbarer robots.txt gilt die letzte gültige Fassung, Dokumente nicht zugesagt „einmal je Datei“
        html = text(self.html())
        self.assertIn("fragen wir höchstens einmal am Tag und in jedem Vollabgleich wieder an", html)
        self.assertIn("gilt die zuletzt gelesene Fassung weiter; gab es keine, stellen wir die Abrufe zurück", html)
        self.assertIn("mit dem Abgleich und stündlich", html)
        for alt in ["erst im nächsten Vollabgleich wieder an", "stellen wir alle Abrufe zurück", "einmal je Datei"]:
            self.assertNotIn(alt, html, alt)

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

    def test_abruf_adresse_kann_sich_aendern(self):
        # ABRUFREGELN.md „Abruf-Adresse“: erkennen am User-Agent, die Adresse kann sich ändern; keine Zusage zur
        # Exklusivität der Adresse
        html = text(self.html())
        self.assertIn("Erkennen Sie uns bitte vor allem am User-Agent: Die Adresse kann sich ändern", html)
        self.assertNotIn("exklusiv", html)

    def test_selbstbetrieb_mit_eigener_kennung(self):
        # Selbstbetreiber rufen von eigener Adresse ab, können INGESTOR_USER_AGENT setzen; mandari-ingestor gilt weiter
        html = text(self.html())
        self.assertIn("Selbst betriebene Installationen.", html)
        self.assertIn("kann für den Abgleich eine eigene Kennung mit eigener Kontaktadresse setzen", html)
        self.assertIn("Abrufe mit unserer Kennung von anderen Adressen als der oben genannten", html)
        self.assertIn("Ihre Regeln für mandari-ingestor gelten auch für solche Installationen", html)

    def test_robots_txt_nicht_erreichbar_und_eigene_gruppe(self):
        # shared/mandari_oparl/robots.py: 4xx gilt als nicht vorhanden, 5xx/408/429/Netzfehler als nicht erreichbar,
        # neuer Abruf nach RETRY_UNREACHABLE_SECONDS (15 Minuten); eine Gruppe für mandari-ingestor gilt anstelle von *
        html = text(self.html())
        self.assertIn("Fehlt sie (HTTP 4xx), ist alles erlaubt.", html)
        self.assertIn("HTTP 408 oder 429, Netzfehler, mehr als fünf Weiterleitungen", html)
        self.assertIn("versuchen wir es frühestens nach 15 Minuten wieder", html)
        self.assertIn("mit eigener Gruppe gelten nur deren Regeln", html)
        self.assertIn("mandari-file-cache und mandari", html)

    def test_weiterleitungen_im_takt_und_nach_robots(self):
        # redirects.py (Ingestor und Anwendung): höchstens fünf, vor jeder die robots.txt des Ziels und der Takt
        html = text(self.html())
        self.assertIn("Jede Anfrage zählt, auch der Abruf Ihrer robots.txt und jede Weiterleitung.", html)
        self.assertIn("höchstens fünfmal je Abruf und nur, wenn die robots.txt ihres Ziels es erlaubt", html)

    def test_takt_ohne_redis_offen_benannt(self):
        # pacing.py: ohne Redis drosselt jeder Prozess für sich; deshalb keine Zusage „nie schneller“
        html = text(self.html())
        self.assertIn("Schneller rufen wir nicht ab, auf Ihren Wunsch langsamer.", html)
        self.assertIn("hält jeder Dienst den Takt für sich, bis sie wieder steht; in dieser Zeit können mehr als eine "
                      "Anfrage pro Sekunde ankommen", html)
        self.assertNotIn("Schneller rufen wir nie ab", html)

    def test_personenfotos_zeitplan_menge_und_wiederholung(self):
        # schedules.py fetch_person_photos montags 03:00; person_photos.py limit 500, max_age_days 30, _source_blocked
        html = text(self.html())
        self.assertIn("Personenfotos", html)
        self.assertIn("montags um 3 Uhr", html)
        self.assertIn("höchstens 500 Personen je Kommune", html)
        self.assertIn("vor mehr als 30 Tagen geprüft haben, auch wenn es fehlte oder der Abruf fehlschlug", html)
        self.assertIn("pausieren wir es nach wiederholten Fehlern, laden wir keine Fotos", html)

    def test_dokumente_wiederholungen_und_pruefung(self):
        # abruf.py BACKOFF und ERROR_RETRY; loeschabgleich --head-limit 30, --interval 2, FILE_PURGE_AFTER_DAYS 30
        html = text(self.html())
        self.assertIn(
            "frühestens nach 15 Minuten, 1, 6, 24 und 72 Stunden erneut, danach frühestens nach sieben Tagen", html
        )
        self.assertIn("höchstens 30 je Kommune", html)
        self.assertIn("mindestens 2 Sekunden", html)
        self.assertIn("Retry-After-Header werten wir nicht aus", html)

    def test_quellenangabe_wie_im_buergerportal(self):
        # insight_footer.html nennt das RIS der Kommune als Text, einen Link gibt es nur auf der Vorlagenseite
        # (insight_core/views/papers.py source_url aus raw_json.web)
        html = text(self.html())
        self.assertIn("Auf unseren Seiten zu Ihrer Kommune nennen wir Ihr Ratsinformationssystem als Quelle", html)
        self.assertIn("bei Vorlagen verlinken wir die Seite in Ihrem System, wenn Ihre Schnittstelle sie angibt", html)
        self.assertNotIn("auf jeder Detailseite nennen und verlinken wir", html)

    def test_pausen_gelten_fuer_den_abgleich(self):
        # ABRUFREGELN.md „Fehler und Schonung“: Pausen für Abgleich und Scraper; die Anwendung ruht erst nach
        # INSIGHT_SOURCE_BACKOFF_FAILURES Läufen, robots.txt beachtet sie immer; nicht erreichbare robots.txt
        # pausiert nur ohne frühere Fassung (_Entry.last_good)
        html = text(self.html())
        self.assertIn("nicht erreichbar ist und wir keine frühere Fassung haben, pausiert unser Abgleich", html)
        self.assertIn(
            "Das stündliche Nachholen und Prüfen von Dokumenten, das Laden beim Öffnen und die Personenfotos ruhen "
            "erst, wenn drei Abgleiche in Folge Ihr System nicht erreichen",
            html,
        )
        self.assertIn("Eine Sperre per robots.txt beachten alle Abrufe immer", html)
        self.assertIn("höchstens 24 Stunden, solange sie erreichbar ist", html)
        self.assertNotIn("nicht erreichbar ist, pausieren wir", html)

    def test_texterkennung_ruht_nicht_in_der_pause(self):
        # extract-daemon (ingestor/src/main.py, extractor.py) prüft nur file_downloads und robots.txt, nicht
        # source_backoff_until: Die Seite darf nicht zusagen, dass alle Dokumentabrufe ruhen
        html = text(self.html())
        self.assertIn("Neue Dateien, deren Text noch fehlt, lädt unsere Texterkennung auch während einer Pause", html)
        self.assertNotIn("übrigen Abrufe von Dokumenten und Fotos ruhen erst", html)

    def test_zeitfenster_nur_fuer_den_vollabgleich(self):
        # full_sync_window begrenzt nur die Listen des Vollabgleichs
        html = text(self.html())
        self.assertIn("ein Zeitfenster für den Vollabgleich", html)
        self.assertIn("Änderungsabgleich und Dokumentabrufe laufen auch dann rund um die Uhr im Takt", html)
        self.assertNotIn("Zeitfenster vereinbaren", html)
        self.assertNotIn("nach Ihren Vorgaben", html)

    def test_pdf_beispiel_mit_grenzen(self):
        # robots.py: $ verankert das Ende, Groß- und Kleinschreibung zählt im Pfad
        html = text(self.html())
        self.assertIn("Adressen ausschließen, die auf .pdf enden; die Schnittstelle bleibt frei", html)
        self.assertIn("sperren Sie deren Pfad", html)
        self.assertNotIn("Nur PDF-Dateien ausschließen", html)

    def test_abweichende_kennung_nur_mit_vereinbarung(self):
        # config.py DEFAULT_USER_AGENT (#123): Kennung je Quelle für Server, die Wörter im User-Agent filtern
        html = text(self.html())
        self.assertIn("Eine abweichende Kennung für Ihr System setzen wir nur, wenn Sie sie mit uns vereinbaren", html)

    def test_link_auf_die_abrufregeln_im_zweig_dev(self):
        self.assertEqual(
            muster_daten.CRAWLER_ABRUFREGELN, "https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md"
        )
        self.assertIn(f'href="{muster_daten.CRAWLER_ABRUFREGELN}"', self.html())
