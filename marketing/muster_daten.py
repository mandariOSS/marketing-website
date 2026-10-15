"""
Inhalte der Abschnittsmuster auf festen Seiten (ohne StreamField).

Startseite, Responsible Disclosure, Crawler-Seite und die Rechtstexte haben eigene Templates. Damit
sie dieselben Muster nutzen wie die Redaktionsseiten, stehen ihre Daten hier in derselben Form wie die
StreamField-Werte (dicts mit denselben Schlüsseln); die Templates lesen sie über
``{% muster_daten "<name>" as d %}`` bzw. ``{% dokument_rand page.slug as rand %}``.

Fristen der Disclosure-Policy müssen mit SECURITY.md im mandari-Repository übereinstimmen (CI-Schritt
„Sicherheitsfristen“).
"""

from __future__ import annotations

# ── M5c: direkte Wege im Einladungsband ──────────────────────────────────────

STANDARD_WEGE = [
    {"label": "E-Mail", "wert": "hello@mandari.de", "url": ""},
    {"label": "Gespräch", "wert": "per Video, am Telefon oder in Münster", "url": ""},
]

WEGE = {
    "start": [
        {"label": "E-Mail", "wert": "hello@mandari.de", "url": ""},
        {"label": "Gespräch", "wert": "per Video, am Telefon oder in Münster", "url": ""},
        {"label": "Für Vergabestellen", "wert": "Unterlagen für die Vergabeakte", "url": "/vergabe/"},
        {"label": "Für die IT", "wert": "Trust Center", "url": "/trust/"},
    ],
    "disclosure": [
        {"label": "E-Mail", "wert": "security@mandari.de", "url": ""},
        {"label": "Eingangsbestätigung", "wert": "innerhalb von 3 Werktagen", "url": ""},
        {"label": "Vorfälle und Zahlen", "wert": "Transparenzbericht", "url": "/transparenz/"},
        {"label": "Maschinenlesbar", "wert": "security.txt", "url": "/.well-known/security.txt"},
    ],
    "crawler": [
        {"label": "E-Mail", "wert": "support@mandari.de", "url": ""},
        {"label": "Datenquellen", "wert": "Quellennachweise", "url": "/quellen/"},
        {"label": "Unsere Schnittstelle", "wert": "oparl.mandari.de", "url": "https://oparl.mandari.de"},
    ],
}


# ── /sicherheit/disclosure/ ───────────────────────────────────────────────────

DISCLOSURE_ZUSAGE = {
    "aussage": "Wer gutgläubig forscht, bekommt von uns keine Anzeige und keine Abmahnung.",
    "grundlage": "<p>Safe Harbor: Wir verzichten bei gutgläubiger Forschung auf zivil- und strafrechtliche "
                 "Schritte, auch nach § 202c StGB.</p>",
    "bedingungen_titel": "Das gilt, solange Sie",
    "bedingungen": [
        "nur im Geltungsbereich und mit eigenen Testkonten prüfen,",
        "keine Dienste stören und keine echten Nutzerdaten abrufen,",
        "die Lücke erst nach der abgestimmten Veröffentlichung nennen.",
    ],
    "geltung": "<p>Geltungsbereich: alle mandari-Domains, das Repository mandariOSS/mandari und selbst "
               "betriebene mandari-Instanzen mit Erlaubnis der Betreiber. "
               '<a href="#geltungsbereich">Im Detail</a></p>',
    "neben": [
        {"stichwort": "Sie sprechen mit Menschen.",
         "text": "Kein Ticket-Bot, keine automatische Antwort: Es antworten die Menschen, die die Lücke beheben."},
        {"stichwort": "Wir nennen Ihren Namen.",
         "text": "In der Hall of Fame und im Security-Advisory, auf Wunsch mit persönlichem Empfehlungsschreiben."},
    ],
}

# Achse: 30 Tage linear, ab dem Fix eine eigene Strecke über 90 Tage (Fristen aus SECURITY.md)
DISCLOSURE_ZEITSKALA = {
    "strecke1_tage": 30,
    "strecke2_label": "Fix",
    "strecke2_tage": 90,
    "marken": [
        {"tag": 0, "strecke": "1", "frist": "Tag 0", "notiz": "Ihre Meldung geht ein"},
        {"tag": 3, "strecke": "1", "frist": "3 Werktage", "notiz": "Eingangsbestätigung"},
        {"tag": 7, "strecke": "1", "frist": "7 Tage", "notiz": "Einstufung (CVSS 3.1)"},
        {"tag": 14, "strecke": "1", "frist": "zwei Wochen", "notiz": "Zwischenstand, spätestens"},
        {"tag": 0, "strecke": "2", "frist": "Fix", "notiz": "Korrektur ausgerollt", "offen": True},
        {"tag": 90, "strecke": "2", "frist": "+90 Tage", "notiz": "Veröffentlichung, spätestens"},
    ],
    "balken_titel": "Behebung spätestens, je nach Schweregrad",
    "balken": [
        {"label": "kritisch", "wert": "72 Stunden", "tage": 3},
        {"label": "hoch", "wert": "7 Tage", "tage": 7},
        {"label": "mittel", "wert": "30 Tage", "tage": 30},
    ],
    "fenster": "Koordinierte Veröffentlichung als Security-Advisory, mit Ihnen abgestimmt; früher, wenn die "
               "Lücke bereits ausgenutzt wird. Auf Wunsch mit Ihrem Namen in der Hall of Fame.",
    "skala": [
        {"tag": 0, "strecke": "1", "label": "Tag 0"},
        {"tag": 7, "strecke": "1", "label": "1 Woche"},
        {"tag": 14, "strecke": "1", "label": "2 Wochen"},
        {"tag": 21, "strecke": "1", "label": "3 Wochen"},
        {"tag": 28, "strecke": "1", "label": "4 Wochen"},
        {"tag": 0, "strecke": "2", "label": "Fix"},
        {"tag": 30, "strecke": "2", "label": "+30"},
        {"tag": 60, "strecke": "2", "label": "+60"},
        {"tag": 90, "strecke": "2", "label": "+90 Tage"},
    ],
    "schritte": [
        {"frist": "Tag 0", "frist_zusatz": "Ihre Meldung geht ein", "titel": "Meldung",
         "text": "Sie schreiben an security@mandari.de, gern PGP-verschlüsselt: Beschreibung, Nachweis, "
                 "betroffene Adresse."},
        {"frist": "höchstens 3 Werktage", "frist_zusatz": "Einstufung nach CVSS 3.1 innerhalb von 7 Tagen",
         "titel": "Eingangsbestätigung",
         "text": "Wir bestätigen den Eingang Ihrer Meldung. Danach folgt die Erstbewertung mit Einordnung des "
                 "Schweregrads nach CVSS 3.1 – innerhalb von 7 Tagen."},
        {"frist": "72 Stunden, 7 Tage oder 30 Tage", "frist_zusatz": "je nach Schweregrad",
         "titel": "Behebung",
         "text": "Wir entwickeln, testen und rollen die Korrektur aus. Einen Zwischenstand bekommen Sie "
                 "spätestens nach zwei Wochen, danach laufend Statusinformationen.",
         "details": [{"begriff": "kritisch", "wert": "72 Stunden"}, {"begriff": "hoch", "wert": "7 Tage"},
                     {"begriff": "mittel", "wert": "30 Tage"}]},
        {"frist": "90 Tage nach dem Fix", "frist_zusatz": "früher bei bereits ausgenutzten Lücken",
         "titel": "Koordinierte Veröffentlichung",
         "text": "Die Veröffentlichung stimmen wir mit Ihnen ab – vollständige Offenlegung 90 Tage nach dem Fix: "
                 "Security-Advisory und, wenn Sie möchten, ein Eintrag in der Hall of Fame."},
    ],
}

DISCLOSURE_GELTUNG = {
    "header": {"title": "Was Sie testen dürfen und was nicht",
               "subline": "Klare Grenzen schützen alle: Sie, uns und unsere Nutzer:innen.",
               "anchor_id": "geltungsbereich"},
    "optionen": [
        {"name": "Im Geltungsbereich", "satz": "Hier freuen wir uns über Ihre Prüfung"},
        {"name": "Außerhalb", "satz": "Bitte nicht testen"},
    ],
    "kriterien": [
        {"kriterium": "Systeme",
         "werte": ["<p><code>mandari.de</code> und alle Subdomains, Container-Images aus der mandari-Registry</p>",
                   "<p>OParl-Quellsysteme der Kommunen (nicht unser System), Dienste von Drittanbietern</p>"]},
        {"kriterium": "Quellcode und Instanzen",
         "werte": ["<p>Repository <code>mandariOSS/mandari</code>; selbst betriebene mandari-Instanzen "
                   "<em>mit Erlaubnis der Betreiber</em></p>",
                   "<p>Physische Angriffe auf Hosting-Standorte</p>"]},
        {"kriterium": "Schwachstellen",
         "werte": ["<p>Anmeldung, Sitzungsverwaltung, Rollen und Rechte; SQL-Injection, XSS, CSRF, IDOR</p>",
                   "<p><strong>DoS und DDoS</strong> jeglicher Art; automatisierte Scanner ohne Rückprüfung "
                   "der Treffer</p>"]},
        {"kriterium": "Menschen und Daten",
         "werte": ["<p>Eigene Testkonten</p>",
                   "<p>Social Engineering gegen Mitwirkende oder Nutzer:innen; echte Nutzerdaten</p>"]},
    ],
}


# ── /crawler/ ─────────────────────────────────────────────────────────────────
# Angaben zu unseren Abrufen bei Ratsinformationssystemen (mandariOSS/mandari#1027). Jeder Wert ist im
# mandari-Repository oder in der Produktionskonfiguration belegt, die Fundstelle steht am Eintrag; die technische
# Referenz ist docs/ABRUFREGELN.md dort. Ändert sich der Abruf (etwa der Takt nach Bedarf, mandari#1026), werden
# nur diese Daten angepasst, das Template bleibt.

#: shared/mandari_oparl/crawler.py, user_agent(): Produkt-Token, Version (nur der Ingestor), Infoseite, Kontakt
CRAWLER_USER_AGENT = "mandari-ingestor/<Version> (+https://mandari.de/crawler/; support@mandari.de)"
#: shared/mandari_oparl/crawler.py, PRODUCT_TOKEN; ausgewertet in shared/mandari_oparl/robots.py (RFC 9309)
CRAWLER_TOKEN = "mandari-ingestor"
#: Ausgehende Adresse der von uns betriebenen Instanz, nur IPv4
CRAWLER_ADRESSE = "144.76.153.200"
#: shared/mandari_oparl/crawler.py, CONTACT
CRAWLER_KONTAKT = "support@mandari.de"
CRAWLER_MAILTO = "mailto:support@mandari.de?subject=Abrufe%20von%20mandari-ingestor"
CRAWLER_ABRUFREGELN = "https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md"

CRAWLER_KENNUNG = [
    {"anker": "user-agent", "begriff": "User-Agent", "wert": CRAWLER_USER_AGENT,
     # Django (Dokumente, Vorschau) ruft user_agent() ohne Version auf: mandari/insight_core/services/robots.py
     "notiz": "Abrufe von Dokumenten aus der Anwendung tragen dieselbe Kennung ohne Versionsnummer. Die Version "
              "wechselt mit jeder Ausgabe; prüfen Sie deshalb auf den Anfang mandari-ingestor."},
    {"anker": "abruf-adresse", "begriff": "Abruf-Adresse", "wert": CRAWLER_ADRESSE,
     "notiz": "IPv4. Über IPv6 rufen wir nicht ab. Die Adresse gilt für die Instanz, die wir betreiben. mandari ist "
              "Open Source: Installationen anderer Betreiber rufen mit derselben Kennung von eigenen Adressen ab."},
    {"anker": "robots-token", "begriff": "Token für robots.txt", "wert": CRAWLER_TOKEN,
     "notiz": "Eine Regel für dieses Token gilt für alle unsere Abrufe; Groß- und Kleinschreibung zählt nicht."},
    {"anker": "kontakt-abrufe", "begriff": "Kontakt", "wert": CRAWLER_KONTAKT, "url": CRAWLER_MAILTO,
     "notiz": "Für Fragen, einen langsameren Takt, ein Zeitfenster oder den Ausschluss Ihres Systems."},
]

# Takt (Zahl im Satz) und Häufigkeit je Abrufart (Tabelle). Fundstellen:
# - eine Anfrage je Sekunde: shared/mandari_oparl/pacing.py DEFAULT_INTERVAL (Redis-Zeitstempel je Hostname über
#   alle Prozesse; ist Redis nicht erreichbar, drosselt jeder Prozess für sich, LocalSchedule); je Quelle nur
#   langsamer (sync_config request_interval, Werte unter 1,0 s angehoben, mandari#1025; höchstens
#   MAX_REQUEST_INTERVAL 30 s). Gezählt wird je Hostname (host_of), nicht je Server.
# - zwei gleichzeitig: ingestor/src/client/host_pacing.py HostPacer.limit mit ingestor/src/config.py
#   host_max_concurrent, eine asyncio-Semaphore je Prozess und Hostname. Deshalb nur für den Abgleich zugesagt: Die
#   Texterkennung hat eigene zwei Plätze, die Anwendung (Dokument-Cache, Vorschau, Löschabgleich, Personenfotos)
#   nur den Takt. Eine Grenze über alle Dienste bräuchte zuerst eine Grenze in Redis im Code, nicht diesen Text.
# - alle 10 Minuten: docker-compose.yml, Dienst ingestor, --interval ${INGESTOR_INTERVAL:-10}; läuft ein Abgleich
#   noch, entfällt der nächste (ingestor/src/scheduler, _is_syncing)
# - Änderungsfenster: Beginn des letzten vollständig erfolgreichen Durchlaufs der Kommune, inkrementell oder voll
#   (ingestor/src/sync/orchestrator.py, set_body_sync_started bei leerem stats["incomplete"]), meist also der
#   vorige 10-Minuten-Lauf, abzüglich INGESTOR_MODIFIED_SINCE_MARGIN_MINUTES (120); fehlende Listen bis zum
#   nächsten Vollabgleich nicht anfragen (sync_config missing_lists), beides mandari#1025 (vorher fest 7 Tage);
#   ohne Filter Abbruch nach fünf Seiten ohne Änderung (orchestrator.py, stale_pages_to_stop)
# - Vollabgleich 1 Uhr: Produktion INGESTOR_FULL_SYNC_HOUR=1 (Cron im Scheduler, der einzige Start eines
#   Vollabgleichs); Abstand und Zeitfenster je Quelle: sync_config full_sync_every_days (heute 28 für Köln, Münster,
#   Bezirksregierung Köln, Bonn) und full_sync_window (ingestor/src/client/source_options.py, mandari#1023). Liegt
#   der Start außerhalb des Fensters, läuft nur der Änderungsabgleich (orchestrator.py, _full_sync_plan): Ein
#   vereinbartes Fenster muss deshalb 1 Uhr enthalten.
# - Dokumente: Abruf je Quelle standardmäßig an und nur abschaltbar (sync_config file_downloads false:
#   ingestor/src/client/source_options.py FILE_DOWNLOADS_KEY, mandari/hub/ris/abruf.py source_fetch_allowed), es
#   gibt keine Freischaltung. Einmal je Datei (Ablage, mandari/hub/ris/abruf.py) gilt erst mit der Dokumentkette
#   (mandari#919, Texterkennung aus der Ablage); vorher lädt die Texterkennung jede Datei zusätzlich selbst.
#   insight_core/services/file_reconcile.py: neu laden bei gemeldeter Änderung, HEAD-Stichproben.
# - robots.txt: shared/mandari_oparl/robots.py CACHE_SECONDS (24 Stunden), Störung zurückstellen
CRAWLER_TAKT = {
    "satz": "Höchstens <b>eine Anfrage pro Sekunde</b> je Hostname, über alle unsere Dienste zusammen. "
            "Schneller rufen wir nie ab, auf Ihren Wunsch langsamer.",
    "erlaeuterung": "Das gilt auch, wenn mehrere Kommunen unter demselben Hostnamen liegen. Verschiedene Hostnamen "
                    "zählen getrennt, auch auf demselben Server. Unser Abgleich hält dabei höchstens zwei Anfragen "
                    "gleichzeitig offen.",
    "zeilen": [
        {"abruf": "Änderungsabgleich", "wann": "alle 10 Minuten",
         "umfang": "Je Liste nur, was sich seit dem letzten erfolgreichen Durchlauf geändert hat, meist also seit dem "
                   "vorigen vor 10 Minuten, mit zwei Stunden Puffer (OParl-Filter modified_since); ohne Änderung ist "
                   "das eine Seite je Liste. Listen, die Ihr System nicht anbietet, fragen wir erst im nächsten "
                   "Vollabgleich wieder an. Filtert ein System nicht nach Änderungsdatum, lesen wir die Liste von "
                   "vorn und hören nach fünf Seiten ohne Änderung auf. Läuft ein Abgleich noch, entfällt der nächste."},
        {"abruf": "Vollabgleich", "wann": "nachts ab 1 Uhr",
         "umfang": "Alle Listen vollständig, als Sicherheitsnetz für Änderungen, die ein Filter nicht meldet. Wie oft, "
                   "stellen wir je Quelle ein: bei Systemen, die zuverlässig nach Änderungsdatum filtern, höchstens "
                   "alle 28 Tage, sonst jede Nacht. Auf Wunsch nur in einem vereinbarten Zeitfenster ab 1 Uhr nachts; "
                   "was bis zu dessen Ende fehlt, folgt in der nächsten Nacht."},
        {"abruf": "Dokumente", "wann": "einmal je Datei",
         "umfang": "Wir laden Dokumente, um ihren Text durchsuchbar zu machen. Für einzelne Systeme schalten wir den "
                   "Dokumentabruf ab, etwa wenn Dokumente nur hinter einer Prüfung für Menschen liegen oder Sie das "
                   "wünschen. Erneut laden wir eine Datei nur, wenn ein Abruf fehlschlug oder sie sich geändert hat. "
                   "Einzelne HEAD-Anfragen prüfen, ob ein Dokument noch vorhanden ist: Was Sie löschen, verschwindet "
                   "so auch bei uns."},
        {"abruf": "robots.txt", "wann": "alle 24 Stunden",
         "umfang": "Wir lesen sie vor dem ersten Abruf und danach spätestens alle 24 Stunden neu. Ist sie nicht "
                   "erreichbar (Serverfehler, HTTP 429), stellen wir alle Abrufe zurück, bis sie es wieder ist."},
    ],
}


# ── M4: Randspalte der Dokumentseiten (Rechtstexte, Quellen) ───────────────────
# Nur Angaben, die es gibt: Verweise auf bestehende Seiten und Dokumente, Ansprechpartner. „Stand“ liest
# das Template aus dem Text selbst (dokument_stand), sonst entfällt die Zeile.

DOKUMENTE = {
    "impressum": {
        "kontakt": "hello@mandari.de",
        "verweise": [("Datenschutzerklärung", "/datenschutz/"), ("Angaben zum Unternehmen", "/unternehmen/#angaben"),
                     ("Quellennachweise", "/quellen/")],
    },
    "datenschutz": {
        "kontakt": "datenschutz@mandari.de",
        "verweise": [("Muster-AVV", "/avv/"), ("Unterauftragsverarbeiter", "/trust/#subprocessors"),
                     ("Impressum", "/impressum/")],
    },
    "agb": {
        "kontakt": "hello@mandari.de",
        "verweise": [("Muster-AVV", "/avv/"), ("Kündigung und Widerruf", "/kuendigung/"), ("Preise", "/preise/")],
    },
    "avv": {
        "kontakt": "hello@mandari.de",
        "abschliessen": "Unterschriftsreif mit dem Namen Ihrer Organisation: kurze Mail an hello@mandari.de",
        "verweise": [("Technische und organisatorische Maßnahmen", "https://docs.mandari.de/datenschutz/tom/"),
                     ("Löschkonzept", "https://docs.mandari.de/datenschutz/loeschkonzept/"),
                     ("Unterauftragsverarbeiter", "/trust/#subprocessors")],
        "verweise_titel": "Anlagen",
    },
    "kuendigung": {
        "kontakt": "hello@mandari.de",
        "verweise": [("AGB", "/agb/"), ("Muster-AVV", "/avv/"), ("Datenexport im Trust Center", "/trust/#backup")],
    },
    "quellen": {
        "kontakt": "hello@mandari.de",
        "verweise": [("Über unseren Crawler", "/crawler/"), ("Open Source", "/open-source/"),
                     ("Bürgerportal", "/insight/")],
    },
    "trust": {
        "kontakt": "hello@mandari.de",
        "verweise": [("Muster-AVV", "/avv/"), ("Vergabe und Unterlagen", "/vergabe/"),
                     ("Responsible Disclosure", "/sicherheit/disclosure/"), ("Statusseite", "https://status.mandari.de/")],
    },
}

DATEN = {
    "disclosure_zusage": DISCLOSURE_ZUSAGE,
    "disclosure_zeitskala": DISCLOSURE_ZEITSKALA,
    "disclosure_geltung": DISCLOSURE_GELTUNG,
    "crawler": {"kennung": CRAWLER_KENNUNG, "takt": CRAWLER_TAKT, "mailto": CRAWLER_MAILTO,
                "abrufregeln": CRAWLER_ABRUFREGELN},
}
