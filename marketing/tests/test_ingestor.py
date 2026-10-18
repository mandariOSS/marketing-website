"""Ingestor-Seite /ingestor/ (mandariOSS/mandari#1027): vollständige Kennung, Abruf-Adresse und Kontakt, Takt aus
marketing/muster_daten.py; frühere Angaben, die nicht mehr stimmten, kehren nicht zurück. Bis 18.10.2026 hieß die
Seite /crawler/; die alte Adresse leitet dauerhaft weiter (UmbenennungTests)."""

import re
from io import StringIO
from pathlib import Path

from django.core.management import call_command
from django.template.loader import get_template
from django.test import TestCase, override_settings

from marketing import muster_daten


def text(html):
    """Fließtext ohne Zeilenumbrüche aus dem Template, damit Sätze über Zeilen hinweg gefunden werden."""
    return " ".join(html.split())


class IngestorSeiteTests(TestCase):
    def html(self):
        antwort = self.client.get("/ingestor/")
        self.assertEqual(antwort.status_code, 200)
        return antwort.content.decode("utf-8")

    def test_kennung_adresse_und_kontakt(self):
        html = self.html()
        # Vollständiger User-Agent wie shared/mandari_oparl/crawler.py im mandari-Repository (Version als Platzhalter)
        self.assertIn("mandari-ingestor/&lt;Version&gt; (+https://mandari.de/ingestor/; support@mandari.de)", html)
        # Abruf-Adresse mit eigener Sprungmarke, damit man sie direkt verlinken und übernehmen kann
        self.assertIn('id="abruf-adresse"', html)
        self.assertIn(muster_daten.ABRUF_ADRESSE, html)
        self.assertIn("nur über IPv4", html)
        # Die Adresse teilen sich womöglich weitere Dienste; ob wir das nennen, entscheidet Sven. Deshalb nur der Rat:
        self.assertIn("Machen Sie Freigaben deshalb nicht allein an der Adresse fest.", text(html))
        # „unverändert übernehmen“ passt nicht zum Platzhalter <Version>
        self.assertIn("beim User-Agent genügt der Anfang mandari-ingestor", text(html))
        self.assertIn(f'href="{muster_daten.ABRUF_MAILTO}"', html)
        self.assertIn(muster_daten.ABRUF_REGELN, html)

    def test_takt_und_haeufigkeit_aus_den_daten(self):
        html = self.html()
        self.assertIn("<b>eine Anfrage pro Sekunde</b>", html)
        for zeile in muster_daten.ABRUF_TAKT["zeilen"]:
            self.assertIn(zeile["abruf"], html)
            self.assertIn(zeile["wann"], html)

    def test_takt_je_hostname_und_zwei_gleichzeitig_nur_im_abgleich(self):
        # Gedrosselt wird je Hostname über Redis für alle Dienste; die Grenze von zwei offenen Anfragen ist eine
        # Semaphore je Prozess (host_pacing.py) und gilt deshalb nur für den Abgleich, nicht für alle Dienste.
        html = self.html()
        self.assertIn("<b>eine Anfrage pro Sekunde</b> je Hostname, über alle unsere Dienste zusammen", html)
        self.assertIn("jeder Abgleich hält höchstens zwei Anfragen gleichzeitig offen", text(html))
        self.assertNotIn("<b>zwei</b>", html)
        self.assertNotIn("pro Sekunde</b> je Server", html)

    def test_aenderungsabgleich_nur_nach_aenderungen(self):
        # orchestrator.py modified_since_for und stale_pages_to_stop; Fenster und Uhrzeit-Listen nur auf docs.mandari.de
        html = text(self.html())
        self.assertIn("Wir fragen nur nach Änderungen (modified_since), ohne Änderung ist das eine Seite je Liste; "
                      "filtert Ihr System nicht, hören wir nach fünf Seiten ohne Änderung auf.", html)
        self.assertNotIn("seit dem letzten vollständigen Abgleich", html)
        # Der Takt je Quelle (mandari#1039) macht „vor 10 Minuten“ falsch: nachts und am Wochenende liegt mehr
        # dazwischen
        self.assertNotIn("meist also seit dem vorigen vor 10 Minuten", html)

    def test_takt_je_quelle_nach_bedarf(self):
        # mandari#1026/#1039, ingestor/src/scheduler/takt.py: WORKDAY_MINUTES 10 (07–19 Uhr), OFF_HOURS_MINUTES 60,
        # WEEKEND_MINUTES 120, MEETING_MINUTES 5 an Sitzungstag und Vortag 07–22 Uhr; ohne Änderung bis
        # MEETING_IDLE_MAX_MINUTES 10 bzw. IDLE_MAX_MINUTES 120; nächster Lauf ab dem Ende des vorigen (next_due)
        html = text(self.html())
        self.assertIn("nach Bedarf, alle 5 Minuten bis alle 2 Stunden", html)
        self.assertIn("Werktags von 7 bis 19 Uhr alle 10 Minuten, sonst stündlich, am Wochenende alle 2 Stunden; an "
                      "Sitzungstagen und am Vortag von 7 bis 22 Uhr alle 5 Minuten.", html)
        self.assertIn("Ändert sich mehrmals in Folge nichts, fragen wir seltener.", html)

    def test_langsame_listen_ruhen(self):
        # mandari#1033/#1040, ingestor/src/sync/slices.py: nur optionale Listen, 1 h, verdoppelt, höchstens 24 h;
        # danach Tagesscheiben nur bei Servern, die filtern
        html = text(self.html())
        self.assertIn("Langsame Listen", html)
        self.assertIn("nach 60 Sekunden ohne Antwort oder mit HTTP 504 ab, lassen wir diese Liste ruhen, auch im "
                      "Vollabgleich", html)
        self.assertIn("zuerst eine Stunde, danach jeweils doppelt so lange, höchstens 24 Stunden", html)
        self.assertIn("Die übrigen Listen gleichen wir weiter ab; danach holen wir die ausgelassenen Änderungen nach.",
                      html)

    def test_zeitfenster_des_vollabgleichs_nicht_an_1_uhr_gebunden(self):
        # Seit mandari#1039 beginnt der Vollabgleich im eigenen Fenster der Quelle, unabhängig von --full-sync-hour;
        # das Standardfenster reicht in Produktion von 1 bis 6 Uhr (FULL_SYNC_DEFAULT_HOURS 5)
        html = text(self.html())
        self.assertNotIn("Zeitfenster ab 1 Uhr nachts", html)
        self.assertIn("nachts im Zeitfenster, standardmäßig ab 1 Uhr", html)
        self.assertIn("höchstens einmal je Nacht, standardmäßig mit Beginn zwischen 1 und 6 Uhr", html)
        self.assertIn("den Vollabgleich nur in einem bestimmten Zeitfenster oder seltener fahren sollen", html)
        # Kurzfassung (Prüfung Runde 2): Zweck des Vollabgleichs steht auf docs.mandari.de, nicht in der Tabelle
        self.assertIn("Alle Listen vollständig, höchstens einmal je Nacht", html)
        self.assertNotIn("Sicherheitsnetz", html)

    def test_eigenes_zeitfenster_nur_bei_oparl(self):
        # orchestrator.py sync_source: Scraper-Quellen gehen vor _full_sync_plan in ScraperSyncRunner.run(full=full),
        # von Hand gilt dort kein Fenster und eine Frist (FetchWindowClosedError) gibt es nicht. Eigenes Fenster und
        # Ende mit dem Fenster deshalb nur für Systeme mit OParl-Schnittstelle; von Hand ohne eigenes Fenster auch
        # tagsüber.
        html = text(self.html())
        self.assertIn("Bei Systemen mit OParl-Schnittstelle legen wir ihn auf Wunsch in ein eigenes Zeitfenster; er "
                      "endet mit dem Fenster, das auch gilt, wenn wir ihn ausnahmsweise von Hand starten.", html)
        self.assertIn("Ohne eigenes Fenster kann er von Hand auch tagsüber laufen.", html)
        self.assertEqual(html.count("eigenes Zeitfenster"), 1)
        for alt in ["Auf Wunsch legen wir ihn in ein eigenes Zeitfenster",
                    "ein vereinbartes Zeitfenster gilt auch dann", "Reicht es nicht, endet er mit dem Fenster",
                    "folgt in der nächsten Nacht", "beginnt in der nächsten Nacht von vorn"]:
            self.assertNotIn(alt, html, alt)

    def test_neue_systeme_erst_nach_aktivierung(self):
        # mandari#1037: add_oparl_source und der Ingestor legen Quellen inaktiv an, neue Kommunen ungelistet
        html = text(self.html())
        # Zusage nur mit der Bedingung im PR (Standardwert von OParlSource.is_active, mandari#555). Ungelistete
        # Kommunen bleiben über ihre direkte Adresse erreichbar, deshalb „in Listen und Übersichten“.
        self.assertIn("regelmäßig fragen wir ein neues System erst ab, wenn wir es eigens aktivieren", html)
        self.assertIn("Neu entdeckte Kommunen nehmen wir erst in Listen und Übersichten auf, wenn wir sie geprüft "
                      "haben", html)
        self.assertNotIn("Kommunen zeigen wir erst", html)

    def test_kein_gemeinsamer_zyklus_mehr(self):
        # Vor mandari#1039 lief ein Zyklus alle 10 Minuten über alle Quellen (max_instances=1)
        html = text(self.html())
        for alt in ["Läuft ein Abgleich noch, entfällt der nächste", ">alle 10 Minuten<"]:
            self.assertNotIn(alt, html, alt)

    def test_erstpruefung_mit_hoechstens_fuenf_anfragen(self):
        # probe-ris (mandari#1031): höchstens fünf Anfragen, Weiterleitungen mitgezählt, im Takt je Host; die
        # Vergleichsanfrage nach HTTP 403 mit python-httpx wie im Abgleich, keine Browserkennung
        html = text(self.html())
        self.assertIn("Ob eine Kommune für uns infrage kommt, prüfen wir mit höchstens fünf Anfragen, robots.txt und "
                      "Weiterleitungen eingerechnet.", html)
        self.assertIn("je Server und Abgleich sowie je Erstprüfung höchstens eine Vergleichsanfrage", html)
        self.assertIn("im Takt und ohne Weiterleitung", html)
        self.assertNotIn("Mozilla", html)

    def test_dokumentabruf_ohne_freischaltung(self):
        # Der Dokumentabruf ist je Quelle standardmäßig an und lässt sich nur abschalten (sync_config file_downloads)
        html = text(self.html())
        self.assertIn("keine Dokumente mehr laden sollen", html)
        self.assertNotIn("freigeschaltet", html)

    def test_fehlende_listen_robots_und_dokumente_wie_in_den_abrufregeln(self):
        # docs/ABRUFREGELN.md im mandari-Repository: vermerkte Listen inkrementell einmal am Tag (MISSING_LIST_RECHECK),
        # bei nicht erreichbarer robots.txt gilt die letzte gültige Fassung, Dokumente nicht zugesagt „einmal je Datei“
        html = text(self.html())
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
        self.assertNotIn("Abruf-Adresse", [weg["label"] for weg in muster_daten.WEGE["ingestor"]])
        self.assertEqual(self.html().count(muster_daten.ABRUF_ADRESSE), 1)

    def test_keine_zusage_gegen_einen_adresswechsel(self):
        # Ob die Abruf-Adresse bleibt, ist offen; zugesagt wird nur, Sperren nicht durch einen Wechsel zu umgehen
        html = text(self.html())
        self.assertIn("Um eine Sperre zu umgehen, wechseln wir weder Kennung noch Adresse.", html)
        self.assertNotIn("Kennung und Adresse wechseln wir nicht", html)

    def test_keine_betriebsinterna_im_quelltext(self):
        # Das Repository ist öffentlich: keine internen Hostnamen und keine Nummern aus dem privaten Repository
        dateien = [Path(muster_daten.__file__), Path(get_template("marketing/ingestor.html").origin.name)]
        for datei in dateien:
            inhalt = datei.read_text(encoding="utf-8")
            for intern in ["web01", "intern#"]:
                self.assertNotIn(intern, inhalt, f"{datei.name}: {intern}")

    def test_robots_beispiel_fuer_unser_token(self):
        html = self.html()
        self.assertIn("User-agent: mandari-ingestor\nDisallow: /</code>", html.replace("\r\n", "\n"))
        # Die Gruppe sperrt nur Abrufe beim Ratsinformationssystem, nicht ein Geoportal unter demselben Hostnamen
        self.assertIn("Alle Abrufe bei Ihrem Ratsinformationssystem ausschließen", html)
        self.assertNotIn("Alle Abrufe von mandari ausschließen", html)

    def test_keine_ueberholten_angaben(self):
        html = self.html()
        for alt in [
            "mandari-ingestor (+https://mandari.de/crawler)",
            # Seit 18.10.2026 /ingestor/ (Entscheidung Sven): keine Verweise mehr auf die alte Adresse
            "https://mandari.de/crawler",
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

    def test_streaming_und_geodienste_mit_unserer_kennung_ohne_robots(self):
        # mandari#1036/#1038 (insight_core/services/dienste.py, ABRUFREGELN.md „Andere Abrufe“): Live-Übertragung und
        # Geodienste senden dieselbe Kennung und werten die robots.txt nicht aus. Die Zusage zur robots.txt gilt
        # deshalb nur für Abrufe bei Ratsinformationssystemen.
        html = text(self.html())
        self.assertIn("Dieselbe Kennung tragen auch unsere Abrufe bei Streaming-Anbietern und Geodiensten", html)
        self.assertIn("Dort gelten die Nutzungsregeln des Dienstes, nicht die robots.txt.", html)
        # Seit #1038 teilen sie den Zeitstempel je Hostname mit den RIS-Abrufen; „eigener Takt“ wäre irreführend
        self.assertNotIn("ein eigener Takt", html)
        self.assertIn("Eine Gruppe für dieses Token gilt für alle unsere Abrufe bei Ratsinformationssystemen", html)
        self.assertIn("Regeln für dieses Token gelten für alle unsere Abrufe bei Ratsinformationssystemen", html)
        self.assertIn("wenn wir Ihr System oder Ihr Geoportal nicht mehr abrufen", html)
        self.assertNotIn("Regeln für dieses Token gelten für alle unsere Abrufe,", html)

    def test_live_und_geoportale_im_takt_je_hostname(self):
        # dienste.py ABSTAND (1 s für LIVE und GEOPORTAL, gemeinsamer Zeitstempel in Redis), NEBEN_RIS mit
        # QUELLEN_TAKTE_SEKUNDEN 300; hub/live/services.py VORLAUF 45 min, FENSTER 10 h, live_status_abfragen jede
        # Minute; sync_plan_boundaries täglich 04:50. Einzige schnellere Ausnahme: KACHELN 0,05 s bei OpenStreetMap.
        html = text(self.html())
        self.assertIn("Live-Übertragung und Geoportale", html)
        self.assertIn("rund um Sitzungen und täglich um 4:50 Uhr", html)
        self.assertIn("einmal je Minute, ob übertragen wird, ab 45 Minuten vor dem Beginn und längstens bis 10 Stunden "
                      "danach", html)
        self.assertIn("lesen wir standardmäßig alle 10 Sekunden ein Einzelbild, mit 2 bis 4 Anfragen", html)
        self.assertIn("Ihre robots.txt werten diese Abrufe nicht aus; möchten Sie sie nicht, schreiben Sie uns.", html)
        self.assertIn("Den Takt halten auch unsere Abrufe bei Streaming-Anbietern und Geoportalen ein; schneller laden "
                      "wir nur Kartenkacheln vom Kachelserver von OpenStreetMap, bis zu 20 je Sekunde.", html)

    def test_robots_txt_je_hostname(self):
        # shared/mandari_oparl/robots.py host_key (mandari#1036): Schema und Port ergeben keinen eigenen Eintrag
        html = text(self.html())
        self.assertIn("Jeder unserer Dienste liest sie vor seinem ersten Abruf, eine je Hostname, und nutzt sie "
                      "höchstens 24 Stunden, solange sie erreichbar ist.", html)

    def test_einzelheiten_nur_auf_docs(self):
        # Rückmeldung 16.10.2026: Kurzfassung für IT-Verantwortliche. Zeitscheiben, Filterprüfung, Uhrzeit-Listen und
        # fehlende optionale Listen stehen auf docs.mandari.de, verlinkt unter der Tabelle.
        html = text(self.html())
        for intern in ["modified_until", "30 Tage lang nur Änderungen", "nachweislich eine Uhrzeit",
                       "außer wenn wir ihn in Zeitabschnitten ausführen", "in Abschnitten zu einem Tag"]:
            self.assertNotIn(intern, html, intern)
        self.assertEqual(muster_daten.ABRUF_EINZELHEITEN, "https://docs.mandari.de/datenschutz/ingestor/")
        self.assertIn(f'<a class="textlink" href="{muster_daten.ABRUF_EINZELHEITEN}">Alle Einzelheiten auf '
                      "docs.mandari.de</a>", html)

    def test_kurzfassung_je_zeile(self):
        # „Weniger ist mehr“: je Umfang-Zelle höchstens vier kurze Sätze und 70 Wörter (vorher bis 172 Wörter)
        for zeile in muster_daten.ABRUF_TAKT["zeilen"]:
            umfang = zeile["umfang"]
            self.assertLessEqual(len(umfang.split()), 70, zeile["abruf"])
            self.assertLessEqual(len(re.findall(r"[.!?](?:\s|$)", umfang)), 4, zeile["abruf"])

    def test_robots_txt_nicht_erreichbar_und_eigene_gruppe(self):
        # shared/mandari_oparl/robots.py: 4xx gilt als nicht vorhanden, 5xx/408/429/Netzfehler als nicht erreichbar,
        # neuer Abruf nach RETRY_UNREACHABLE_SECONDS (15 Minuten); eine Gruppe für mandari-ingestor gilt anstelle von *
        html = text(self.html())
        # 408 und 429 sind 4xx, gelten aber als nicht erreichbar
        self.assertIn("Fehlt sie (HTTP 4xx außer 408 und 429), ist alles erlaubt.", html)
        self.assertIn("Ist sie nicht erreichbar, versuchen wir es frühestens nach 15 Minuten wieder.", html)
        self.assertIn("mit eigener Gruppe gelten nur deren Regeln", html)
        self.assertIn("mandari-file-cache und mandari", html)

    def test_weiterleitungen_im_takt_und_nach_robots(self):
        # redirects.py (Ingestor und Anwendung): höchstens fünf, vor jeder die robots.txt des Ziels und der Takt
        html = text(self.html())
        self.assertIn("Jede Anfrage zählt, auch der Abruf Ihrer robots.txt und jede Weiterleitung.", html)
        # Live-Übertragung und Geoportale (dienste.py vor_weiterleitung) reservieren nur den Takt, ohne robots.txt
        satz = ("Bei Ratsinformationssystemen folgen wir einer Weiterleitung höchstens fünfmal je Abruf und nur, wenn "
                "die robots.txt ihres Ziels es erlaubt")
        self.assertIn(satz, html)
        self.assertLess(html.index(satz), html.index("Den Takt halten auch unsere Abrufe bei Streaming-Anbietern"))

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
        self.assertIn("Jedes Foto fragen wir höchstens alle 30 Tage an, auch wenn es fehlte oder der Abruf fehlschlug",
                      html)
        self.assertIn("pausieren wir es nach wiederholten Fehlern, laden wir keine Fotos", html)

    def test_dokumente_wiederholungen_und_pruefung(self):
        # abruf.py BACKOFF und ERROR_RETRY (failure_state: alle sieben Tage, ohne Obergrenze); loeschabgleich
        # --head-limit 30
        html = text(self.html())
        self.assertIn("frühestens nach 15 Minuten, 1, 6, 24 und 72 Stunden erneut, danach alle sieben Tage.", html)
        self.assertNotIn("danach frühestens nach sieben Tagen", html)
        self.assertIn("höchstens 30 je Kommune und Lauf", html)
        self.assertIn("Retry-After-Header werten wir nicht aus", html)

    def test_loeschungen_sofort_gesperrt_und_ohne_frist_bei_stichproben(self):
        # file_reconcile.py: gesperrt, sobald OParl deleted oder ein per GET bestätigtes 404/410 bemerkt ist; Kopie und
        # Text nach FILE_PURGE_AFTER_DAYS 30 gelöscht. Nicht gemeldete Löschungen nur über die Stichprobe (30 je
        # Kommune und Stunde, gelistete Kommunen, Bremse FILE_RECONCILE_MAX_MISSING): keine Frist zusagen.
        html = text(self.html())
        self.assertIn("Meldet Ihre Schnittstelle ein Dokument als gelöscht oder ist es bei Ihnen nicht mehr abrufbar, "
                      "sperren wir es bei uns, sobald wir das bemerken; Kopie und Text löschen wir 30 Tage später.",
                      html)
        self.assertIn("Nicht gemeldete Löschungen finden wir über Stichproben per HEAD, höchstens 30 je Kommune und "
                      "Lauf; das kann dauern.", html)
        self.assertNotIn("entfernen wir nach 30 Tagen auch bei uns", html)
        # Bremse FILE_RECONCILE_MAX_MISSING: Liefern in einem Lauf mehr als 10 Dokumente einer Quelle neu 404/410,
        # sperrt der Löschabgleich keines davon, und das wiederholt sich jede Stunde. Viele Löschungen auf einmal
        # brauchen deshalb einen Eingriff von Hand; die Seite bittet um eine Nachricht.
        self.assertIn("Löschen Sie viele Dokumente auf einmal, schreiben Sie uns bitte.", html)

    def test_wiederholung_einer_anfrage_fruehestens(self):
        # OParl: oparl_max_retries 3, Pausen 1 und 2 s; Scraper (politeness.py): bei 5xx 2 und 4 s, Netzfehler im
        # 2-Sekunden-Takt. Beides passt nur zu „frühestens“.
        html = text(self.html())
        self.assertIn("höchstens zweimal, frühestens nach einer und nach zwei Sekunden", html)

    def test_entfernen_und_antwortzeit_wie_auf_docs(self):
        # docs.mandari.de/datenschutz/ingestor/ („Inhalte entfernen“): Wünsche werden geprüft, Reaktionszeit fünf
        # Werktage. Den Wortlaut gibt Sven frei.
        html = text(self.html())
        self.assertIn("Wünsche, Inhalte bei uns zu entfernen, prüfen wir im Einzelfall.", html)
        self.assertIn("Wir antworten innerhalb von fünf Werktagen", html)
        for alt in ["zeitnah", "und Ihre Inhalte bei uns entfernen sollen"]:
            self.assertNotIn(alt, html, alt)

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
        # Live-Übertragung und Geoportale werten die robots.txt nicht aus; „alle Abrufe“ wäre zu viel
        self.assertIn("Eine Sperre per robots.txt beachten diese Abrufe immer", html)
        self.assertNotIn("beachten alle Abrufe immer", html)
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
            muster_daten.ABRUF_REGELN, "https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md"
        )
        self.assertIn(f'href="{muster_daten.ABRUF_REGELN}"', self.html())


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["mandari.de", "testserver"])
class UmbenennungTests(TestCase):
    """Entscheidung Sven (18.10.2026): Die Seite heißt /ingestor/, der Ingestor ist kein Crawler, und Server können
    User-Agents mit dem Wort „crawler“ ablehnen. /crawler/ steht in älteren User-Agents, Mails und fremden Logs."""

    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_ingestor_mit_kennung_und_kontakt(self):
        antwort = self.client.get("/ingestor/")
        self.assertEqual(antwort.status_code, 200)
        html = antwort.content.decode("utf-8")
        self.assertIn("mandari-ingestor/&lt;Version&gt; (+https://mandari.de/ingestor/; support@mandari.de)", html)
        self.assertIn(f'href="{muster_daten.ABRUF_MAILTO}"', html)
        self.assertIn('<link rel="canonical" href="https://mandari.de/ingestor/">', html)

    def test_crawler_leitet_dauerhaft_auf_ingestor(self):
        antwort = self.client.get("/crawler/")
        self.assertEqual(antwort.status_code, 301)
        self.assertEqual(antwort["Location"], "/ingestor/")

    def test_weiterleitung_behaelt_den_query_string(self):
        antwort = self.client.get("/crawler/?utm_source=log&quelle=ris")
        self.assertEqual(antwort.status_code, 301)
        self.assertEqual(antwort["Location"], "/ingestor/?utm_source=log&quelle=ris")

    def test_alte_adresse_ohne_schraegstrich(self):
        # Frühere User-Agents nannten https://mandari.de/crawler ohne Schrägstrich (APPEND_SLASH, dann 301)
        antwort = self.client.get("/crawler", follow=True)
        self.assertEqual(antwort.redirect_chain, [("/crawler/", 301), ("/ingestor/", 301)])
        self.assertEqual(antwort.status_code, 200)

    def test_seite_nennt_unseren_dienst_nicht_crawler(self):
        html = self.client.get("/ingestor/").content.decode("utf-8")
        titel = re.search(r"<title>(.*?)</title>", html, re.S).group(1)
        self.assertEqual(" ".join(titel.split()), "mandari-ingestor: Kennung, Takt und Abruf-Adresse | mandari")
        # Auch nicht in Attributen: Der Link auf docs.mandari.de zeigt seit docs#9 auf /datenschutz/ingestor/
        self.assertNotIn("crawler", html.lower())

    def test_quellen_verlinken_die_neue_adresse(self):
        html = self.client.get("/quellen/").content.decode("utf-8")
        self.assertIn('href="/ingestor/"', html)
        self.assertIn("Über unseren Ingestor", html)
        self.assertNotIn('href="/crawler/"', html)
        self.assertNotIn("Crawler", html)

    def test_sitemap_nennt_ingestor(self):
        body = self.client.get("/sitemap.xml").content.decode("utf-8")
        self.assertIn("<loc>https://mandari.de/ingestor/</loc>", body)
        self.assertNotIn("/crawler/", body)
        # Die Wagtail-Seiten stehen weiter darin
        self.assertIn("<loc>https://mandari.de/quellen/</loc>", body)
