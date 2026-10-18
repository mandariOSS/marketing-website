"""
Inhalte der Abschnittsmuster auf festen Seiten (ohne StreamField).

Startseite, Responsible Disclosure, Ingestor-Seite und die Rechtstexte haben eigene Templates. Damit
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
    "ingestor": [
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


# ── /ingestor/ ────────────────────────────────────────────────────────────────
# Bis 18.10.2026 /crawler/ (leitet dauerhaft hierher, website/urls.py): Der Ingestor ist kein Crawler, und Server
# können User-Agents mit dem Wort „crawler“ ablehnen.
# Angaben zu unseren Abrufen bei Ratsinformationssystemen (mandariOSS/mandari#1027). Maßgeblich ist der Code im Zweig
# dev des mandari-Repositorys; die technische Referenz mit allen Fundstellen ist dort docs/ABRUFREGELN.md (Stand nach
# mandari#1029, #1031, #1030, #1036, #1037, #1039, #1040 und #1042). Die Fundstelle jeder Angabe steht am Eintrag.
# Ändert sich der Abruf, werden nur diese Daten angepasst, das Template bleibt.

#: shared/mandari_oparl/crawler.py, user_agent(): Produkt-Token, Version (nur der Ingestor: ingestor/pyproject.toml,
#: ingestor/src/config.py DEFAULT_USER_AGENT), Infoseite (/ingestor/ seit der Umbenennung vom 18.10.2026), Kontakt
ABRUF_USER_AGENT = "mandari-ingestor/<Version> (+https://mandari.de/ingestor/; support@mandari.de)"
#: shared/mandari_oparl/crawler.py, PRODUCT_TOKEN; ausgewertet in shared/mandari_oparl/robots.py (RFC 9309)
ABRUF_TOKEN = "mandari-ingestor"
#: Ausgehende Adresse der von uns betriebenen Instanz, nur IPv4 (ABRUFREGELN.md, „Abruf-Adresse“). Sie kann sich
#: ändern; die Seite nennt deshalb den User-Agent als Erkennungsmerkmal zuerst.
ABRUF_ADRESSE = "144.76.153.200"
#: shared/mandari_oparl/crawler.py, CONTACT
ABRUF_KONTAKT = "support@mandari.de"
ABRUF_MAILTO = "mailto:support@mandari.de?subject=Abrufe%20von%20mandari-ingestor"
ABRUF_REGELN = "https://github.com/mandariOSS/mandari/blob/dev/docs/ABRUFREGELN.md"
#: Alle Einzelheiten für Kommunen (Repository mandariOSS/docs, docs/datenschutz/ingestor.md). Erst mit oder nach
#: mandariOSS/docs#9 live schalten: Dort heißt die Seite seither /datenschutz/ingestor/ (301 von
#: /datenschutz/crawler/); ohne docs#9 führt der Link ins Leere.
ABRUF_EINZELHEITEN = "https://docs.mandari.de/datenschutz/ingestor/"

ABRUF_KENNUNG = [
    {"anker": "user-agent", "begriff": "User-Agent", "wert": ABRUF_USER_AGENT,
     # Die Anwendung sendet die Kennung ohne Version: mandari/insight_core/services/robots.py USER_AGENT (Dokument-
     # Cache, Vorschau, Löschabgleich, Personenfotos, Texterkennung im Worker, add_oparl_source). Die Version ist die
     # Paketversion des Ingestors, keine Ausgabe-Nummer; sie kann sich ändern. Live-Übertragung und Geodienste
     # (mandari#1036/#1038, insight_core/services/dienste.py USER_AGENT) senden dieselbe Kennung ohne Version und
     # werten die robots.txt nicht aus; ihren Takt (ABSTAND, gemeinsamer Zeitstempel in Redis) nennt ABRUF_TAKT
     # (ABRUFREGELN.md, „Andere Abrufe“).
     "notiz": "Die Version kann sich ändern; einige Abrufe, etwa von Dokumenten und Fotos, senden die Kennung ohne "
              "Version. Dieselbe Kennung tragen auch unsere Abrufe bei Streaming-Anbietern und Geodiensten, etwa dem "
              "Geoportal einer Kommune. Dort gelten die Nutzungsregeln des Dienstes, nicht die robots.txt."},
    {"anker": "robots-token", "begriff": "Token für robots.txt", "wert": ABRUF_TOKEN,
     # robots.py _rules_for: eine Gruppe für das Token gilt anstelle von *, nicht zusätzlich; geprüft wird immer
     # mandari-ingestor (ingestor/src/client/robots.py, insight_core/services/robots.py, probe/ris_probe.py).
     # crawler.py LEGACY_TOKENS: frühere Kennungen nur mit eigener Gruppe, und sie können nur sperren.
     "notiz": "Eine Gruppe für dieses Token gilt für alle unsere Abrufe bei Ratsinformationssystemen; Groß- und "
              "Kleinschreibung zählt nicht. "
              "Gruppen für unsere früheren Kennungen mandari-file-cache und mandari beachten wir weiter, soweit sie "
              "etwas sperren."},
    {"anker": "abruf-adresse", "begriff": "Abruf-Adresse", "wert": ABRUF_ADRESSE,
     # Ob die Adresse uns allein gehört, sagt die Seite bewusst nicht (Entscheidung Sven); deshalb der Rat, Freigaben
     # nicht allein an ihr festzumachen. „nur über IPv4“ setzt voraus, dass die Docker-Netze von Ingestor und Worker
     # in Produktion kein IPv6 haben (vor dem Deploy prüfen, siehe PR).
     "notiz": "Von dieser Adresse ruft derzeit die Instanz ab, die wir betreiben, nur über IPv4. Erkennen Sie uns "
              "bitte vor allem am User-Agent: Die Adresse kann sich ändern, etwa bei einem Serverumzug. Machen Sie "
              "Freigaben deshalb nicht allein an der Adresse fest."},
    {"anker": "kontakt-abrufe", "begriff": "Kontakt", "wert": ABRUF_KONTAKT, "url": ABRUF_MAILTO,
     "notiz": "Für Fragen, einen langsameren Takt, ein Zeitfenster für den Vollabgleich oder den Ausschluss Ihres "
              "Systems."},
]

# Selbst betriebene Installationen (ABRUFREGELN.md, „Für Selbstbetreiber“): Abruf von der Adresse des eigenen Servers;
# eigene Kennung für den Ingestor (Abgleich, Scraper, Texterkennung, Sondierung) über INGESTOR_USER_AGENT
# (ingestor/src/config.py). Die Abrufe der Anwendung (Dokument-Cache, Vorschau, Löschabgleich, Personenfotos,
# Quellenanlage) senden die feste Kennung samt support@mandari.de (insight_core/services/robots.py USER_AGENT),
# abweichend nur je Quelle über sync_config["download_headers"]; ein Sync aus dem Admin läuft ohne Daemon und für
# abgeschaltete Quellen im Worker und nutzt dort ohne eigene Umgebungsvariable ebenfalls unsere Kennung. Regeln für
# mandari-ingestor gelten trotzdem, weil Ingestor und Anwendung dieses Token immer zusätzlich prüfen.
ABRUF_SELBSTBETRIEB = (
    "mandari ist Open Source. Wer es selbst betreibt, ruft von der Adresse des eigenen Servers ab und kann für den "
    "Abgleich eine eigene Kennung mit eigener Kontaktadresse setzen. Andere Abrufe, etwa von Dokumenten, senden auch "
    "dort meist unsere Kennung. Abrufe mit unserer Kennung von anderen Adressen als der oben genannten können also "
    "von solchen Installationen stammen. Ihre Regeln für mandari-ingestor gelten auch für solche Installationen, denn "
    "mandari prüft dieses Token immer mit."
)

# Takt (Zahl im Satz) und Häufigkeit je Abrufart (Tabelle). Fundstellen im mandari-Repository, Zweig dev:
# - eine Anfrage je Sekunde: shared/mandari_oparl/pacing.py DEFAULT_INTERVAL, Zeitstempel je Hostname in Redis über
#   Ingestor, Anwendung und Werkzeuge (RESERVE_SCRIPT, host_of); je Quelle nur langsamer (request_interval, Werte unter
#   1 s angehoben: MIN_REQUEST_INTERVAL, at_least_minimum; höchstens MAX_REQUEST_INTERVAL 30 s). Ohne Redis drosselt
#   jeder Prozess für sich und versucht es nach 60 s wieder (REDIS_RETRY_SECONDS in beiden host_pacing.py); deshalb
#   „nicht schneller“ statt „nie“, und der Ausfall steht im Text.
# - Andere Dienste (mandari#1036/#1038, mandari/insight_core/services/dienste.py, ABRUFREGELN.md „Andere Abrufe“):
#   derselbe Zeitstempel je Hostname in Redis, ABSTAND 1 s für LIVE, GEOPORTAL, NOMINATIM, OVERPASS, PHOTON; für LIVE
#   und GEOPORTAL (NEBEN_RIS) gilt der größere request_interval einer registrierten Quelle, auch einer inaktiven, auf
#   demselben Hostnamen, spätestens nach QUELLEN_TAKTE_SEKUNDEN 300. Ausnahme vom Satz „eine Anfrage pro Sekunde“:
#   KACHELN 0,05 s (tile.openstreetmap.org, bis zu 20 je Sekunde), deshalb steht sie in der Erläuterung.
#   Live (nur mit LIVE_UEBERTRAGUNG_AKTIV): mandari/hub/live/schedules.py live_status_abfragen jede Minute,
#   hub/live/services.py VORLAUF 45 min, FENSTER 10 h; Einzelbilder im Takt der Übertragungsquelle
#   (BroadcastSource.interval_seconds, Standard 10 s, mindestens 5 s). Geoportale: sync_plan_boundaries täglich 04:50
#   (mandari/apps/common/schedules.py), plan_boundaries.py mit 1 s Pause zwischen zwei Seiten. Abschalten nur über uns
#   (PlanBoundarySource.is_active); eine robots.txt-Gruppe stoppt diese Abrufe nicht.
# - Weiterleitungen: höchstens fünf je Abruf (MAX_REDIRECTS in ingestor/src/client/redirects.py und
#   insight_core/services/redirects.py), vor jeder die robots.txt des Ziels und ein eigener Zeitpunkt im Takt; auch
#   der Abruf der robots.txt reserviert einen Zeitpunkt. Live-Übertragung und Geoportale (dienste.py
#   vor_weiterleitung) reservieren vor einer Weiterleitung nur den Takt, ohne robots.txt; der Satz zur robots.txt des
#   Ziels gilt deshalb nur „bei Ratsinformationssystemen“.
# - zwei gleichzeitig: ingestor/src/client/host_pacing.py HostPacer.limit mit config.py host_max_concurrent, eine
#   Semaphore je Prozess und Hostname. Deshalb nur je Abgleich zugesagt, nicht für alle Dienste: Ein Sync aus dem
#   Admin läuft ohne Daemon und für abgeschaltete Quellen im Worker der Anwendung, also in einem eigenen Prozess mit
#   eigenen zwei Plätzen.
# - Takt je Quelle nach Bedarf (mandari#1026, #1039; ingestor/src/scheduler/takt.py, ABRUFREGELN.md „Rhythmus“):
#   werktags 07–19 Uhr WORKDAY_MINUTES 10 (daemon --interval, docker-compose.yml ${INGESTOR_INTERVAL:-10}), sonst
#   OFF_HOURS_MINUTES 60, Samstag und Sonntag WEEKEND_MINUTES 120; Sitzungstag und Vortag 07–22 Uhr MEETING_MINUTES 5
#   (Sitzungen laut eigenem Bestand, get_meeting_starts); nach IDLE_RUNS 3 Läufen ohne Änderung doppelter Abstand bis
#   IDLE_MAX_MINUTES 120, an Sitzungstagen bis MEETING_IDLE_MAX_MINUTES 10. Nächster Lauf einen Abstand nach dem Ende
#   des vorigen (SyncSchedule.next_due); je Quelle höchstens ein Lauf, höchstens 4 Quellen zugleich
#   (INGESTOR_SYNC_POOL_SIZE). Einen gemeinsamen 10-Minuten-Zyklus mit max_instances=1 gibt es nicht mehr.
# - Langsame Listen (mandari#1033, #1040; ingestor/src/sync/slices.py slow_backoff): eine optionale Liste
#   (OPTIONAL_LIST_TYPES) nach Zeitüberschreitung oder HTTP 504 ausgesetzt, SLOW_LIST_BASE 1 h, verdoppelt bis
#   SLOW_LIST_MAX 24 h; währenddessen fragt kein Lauf die Liste an, auch kein Vollabgleich. Danach ab ihrem eigenen
#   Fensteranfang nachgeholt (slow_lists since), in Scheiben zu einem Tag (SLOW_LIST_SLICE) nur bei Servern, die
#   filtern (OParlClient.filters_list), sonst ohne Scheiben (_slice_fallback).
# - Neue Quellen und Kommunen (mandari#1037, ABRUFREGELN.md „Neue Quellen und Kommunen“): add_oparl_source und der
#   Ingestor (upsert_source) legen Quellen inaktiv an, neue Kommunen ungelistet (upsert_body). Das Admin-Formular ist
#   mit „Aktiv“ vorbelegt; die Seite sagt deshalb „wenn wir es eigens aktivieren“, als Ablauf bei uns (Bedingung vor
#   der Freigabe im PR: Standardwert von OParlSource.is_active, mandari#555). Eine ungelistete Kommune bleibt über ihre
#   direkte Adresse erreichbar; die Seite sagt deshalb „in Listen und Übersichten“, nicht „zeigen“.
# - Änderungsfenster: ingestor/src/sync/orchestrator.py modified_since_for (Beginn des letzten vollständig
#   erfolgreichen Abgleichs der Kommune minus INGESTOR_MODIFIED_SINCE_MARGIN_MINUTES 120), kurzes Fenster nur für
#   Listen in sync_config timed_lists, sonst ab Tagesbeginn (day_start_window); fehlende optionale Listen
#   (OPTIONAL_LIST_TYPES) in missing_lists vermerkt, inkrementell einmal am Tag (MISSING_LIST_RECHECK), im
#   Vollabgleich jedes Mal; Abbruch nach fünf Seiten ohne Änderung (stale_pages_to_stop)
# - Vollabgleich (ABRUFREGELN.md „Vollabgleich“): einmal je Fenster (takt.py full_sync_due, sync_state
#   full_attempted). Standardfenster ab --full-sync-hour für 5 Stunden (default_full_sync_window,
#   FULL_SYNC_DEFAULT_HOURS); Produktion INGESTOR_FULL_SYNC_HOUR=1 (Standard 3), also Beginn zwischen 1 und 6 Uhr. Ein
#   eigenes full_sync_window gilt unabhängig von --full-sync-hour (mandari#1039). Läuft noch ein Änderungsabgleich der
#   Quelle, folgt er direkt danach; während er läuft, entfallen nur die Änderungsabgleiche derselben Quelle. Je Quelle
#   full_sync_every_days (heute 28 bei Quellen mit verlässlichem Filter; ingestor/src/client/source_options.py
#   full_sync_plan); ein Vollabgleich mit Lücke zählt nicht. Das Standardfenster begrenzt nur den Beginn; nach dem Ende
#   eines eigenen Fensters keine weitere Seite (FetchWindowClosedError), der nächste beginnt neu. Zeitscheiben
#   (full_sync_slices, mandari#1040) nur im Fenster, sie setzen am Fortschritt fort (full_sync_progress). Nie ohne
#   Filter (oparl_client.py strict_filter, kein Rückfall bei 400/401/403); die Begrenzung auf einzelne Listen
#   (full_sync_slices.lists) deckt „diese Listen“. Ignoriert der Server den Filter (SLICE_TOLERANCE 1 Tag), Abbruch
#   und 30 Tage nur Änderungsabgleich (full_sync_filter_ignored, FILTER_IGNORED_RECHECK). Von Hand
#   (Admin-Trigger, sync --full): ein eigenes Fenster gilt auch dann; ohne eigenes Fenster beginnt er sofort, in
#   Zeitscheiben nur im Standardfenster. Scraper-Quellen (sync_config source_type „scraper:…“) verlassen
#   orchestrator.py sync_source vor _full_sync_plan über ScraperSyncRunner.run(full=full): Von Hand gilt kein Fenster,
#   und eine Frist (FetchWindowClosedError) kennt der Scraper nicht. Eigenes Fenster und Ende mit dem Fenster sagt die
#   Seite deshalb nur für Systeme mit OParl-Schnittstelle zu. Zeitscheiben, Filterprüfung und die Uhrzeit-Listen des
#   Änderungsfensters stehen nur auf docs.mandari.de (Kurzfassung, Rückmeldung 16.10.2026).
# - Dokumente: Texterkennung im Ingestor mit dem Abgleich (ingestor/src/extraction/extractor.py), Dokument-Cache
#   stündlich um :40 (mandari/apps/common/schedules.py cache_files, DOCUMENT_FETCH_MAX_QUEUED 200 je Quelle),
#   Wiederholungen mandari/hub/ris/abruf.py BACKOFF (15 min, 1, 6, 24, 72 h) und ERROR_RETRY (7 Tage, wiederholt
#   ohne Obergrenze: failure_state), Vorschau auf
#   Anforderung (insight_core/views/files.py); abschaltbar je Quelle mit sync_config file_downloads false
# - Dokumente prüfen: loeschabgleich stündlich um :15 (--changed-limit 200, --head-limit 30, --interval 2 s), nach 429
#   oder 503 Schluss für den Server im Lauf. mandari/insight_core/services/file_reconcile.py: gesperrt (keine Vorschau,
#   kein Text, nicht in Suche und OParl-Ausgabe), sobald OParl deleted oder ein per GET bestätigtes 404/410 bemerkt
#   ist; Kopie und Text erst nach FILE_PURGE_AFTER_DAYS 30 gelöscht (vorher GET, liefert die Quelle wieder: entsperrt).
#   HEAD-Stichproben nur bei gelisteten Kommunen, die am längsten nicht geprüften zuerst (sample_queryset), dazu die
#   Bremse FILE_RECONCILE_MAX_MISSING: Für Löschungen ohne OParl deleted gibt es deshalb keine Frist. Liefern in einem
#   Lauf mehr als 10 Dokumente einer Quelle neu 404/410, sperrt Run.commit_missing keines davon und setzt auch
#   source_checked_at nicht; dieselben kommen im nächsten Lauf wieder zuerst, die Bremse greift erneut. Gemeldet wird
#   das nur im Protokoll des Workers (logger.warning, stderr von loeschabgleich). Viele Löschungen auf einmal bleiben
#   so bis zu einem Eingriff von Hand sichtbar; deshalb die Bitte um eine Nachricht (Prüfung Runde 2, 16.10.2026).
# - Personenfotos: fetch_person_photos montags 03:00 (schedules.py), insight_core/services/person_photos.py
#   fetch_photos_for_body (limit 500, max_age_days 30), ruht wie der Dokument-Cache (_source_blocked)
# - robots.txt: shared/mandari_oparl/robots.py CACHE_SECONDS 24 h, from_response (4xx: nicht vorhanden; 5xx, 408, 429,
#   Netzfehler, zu viele Weiterleitungen: nicht erreichbar), RETRY_UNREACHABLE_SECONDS 15 min; eine Fassung je
#   Hostname und Kennung, Schema und Port ergeben keinen eigenen Eintrag (host_key, mandari#1036); letzte gültige
#   Fassung gilt weiter (ingestor/src/client/robots.py _Entry.last_good, insight_core/services/robots.py).
#   Zwischenspeicher je Ingestor-Prozess bzw. gemeinsam in der Anwendung, deshalb „jeder unserer Dienste“
# - Erstprüfung: ingestor/src/probe/ris_probe.py (MAX_REQUESTS 5 je Kommune, Weiterleitungen und robots.txt neuer
#   Hosts eingerechnet, robots.txt nicht erreichbar: keine weitere Anfrage), zwischen zwei Kommunen 2 s Pause
#   (ingestor/src/main.py probe_ris); Aufnahme: add_oparl_source (MAX_BODY_PAGES 20)
# - Pausen im Fehlerfall (Template, „Automatische Pause“): orchestrator.py BACKOFF_* gelten für Abgleich samt
#   Texterkennung im Sync-Daemon und Scraper. Wiederholung einer Anfrage: OParl config.py oparl_max_retries 3,
#   oparl_retry_backoff (1 und 2 s); Scraper politeness.py max_retries 3, bei 5xx 2 und 4 s, nach Netzfehlern nur
#   im 2-Sekunden-Takt. Deshalb „frühestens“. Template, „Dokumente und Fotos“: Dokument-Cache, Vorschau,
#   Löschabgleich und Personenfotos ruhen erst nach INSIGHT_SOURCE_BACKOFF_FAILURES (3) fehlgeschlagenen Läufen
#   in Folge (ABRUFREGELN.md, „Fehler und Schonung“). Der getrennte OCR-Worker extract-daemon
#   (ingestor/src/main.py, extractor.py) prüft nur file_downloads und robots.txt, nicht source_backoff_until: Er
#   lädt ausstehende Dateien auch während einer Pause, im Takt (host_pacer). Die Seite sagt deshalb nicht, dass alle
#   Dokumentabrufe ruhen.
# - Wiederholungen der Dokumente: BACKOFF sind frühestmögliche Zeitpunkte, ausgeführt im Dokument-Cache um :40
ABRUF_TAKT = {
    "satz": "Höchstens <b>eine Anfrage pro Sekunde</b> je Hostname, über alle unsere Dienste zusammen. "
            "Schneller rufen wir nicht ab, auf Ihren Wunsch langsamer.",
    "erlaeuterung": "Das gilt auch, wenn mehrere Kommunen unter demselben Hostnamen liegen; verschiedene Hostnamen "
                    "zählen getrennt, auch auf demselben Server. Jede Anfrage zählt, auch der Abruf Ihrer robots.txt "
                    "und jede Weiterleitung. Bei Ratsinformationssystemen folgen wir einer Weiterleitung höchstens "
                    "fünfmal je Abruf und nur, wenn die robots.txt ihres Ziels es erlaubt; jeder Abgleich hält "
                    "höchstens zwei Anfragen gleichzeitig offen. Den Takt halten auch unsere Abrufe bei "
                    "Streaming-Anbietern und Geoportalen ein; schneller laden wir nur Kartenkacheln vom Kachelserver "
                    "von OpenStreetMap, bis zu 20 je Sekunde. Ist die Abstimmung zwischen unseren Diensten gestört, "
                    "hält jeder Dienst den Takt für sich, bis sie wieder steht; in dieser Zeit können mehr als eine "
                    "Anfrage pro Sekunde ankommen.",
    # Kurzfassung (Rückmeldung 16.10.2026): je Zeile höchstens drei bis vier kurze Sätze, nur weglassen, nichts so
    # vereinfachen, dass es falsch wird. Alle Einzelheiten stehen auf docs.mandari.de (ABRUF_EINZELHEITEN).
    "zeilen": [
        {"abruf": "Änderungsabgleich", "wann": "nach Bedarf, alle 5 Minuten bis alle 2 Stunden",
         "umfang": "Werktags von 7 bis 19 Uhr alle 10 Minuten, sonst stündlich, am Wochenende alle 2 Stunden; an "
                   "Sitzungstagen und am Vortag von 7 bis 22 Uhr alle 5 Minuten. Ändert sich mehrmals in Folge nichts, "
                   "fragen wir seltener. Wir fragen nur nach Änderungen (modified_since), ohne Änderung ist das eine "
                   "Seite je Liste; filtert Ihr System nicht, hören wir nach fünf Seiten ohne Änderung auf."},
        {"abruf": "Langsame Listen", "wann": "nach einer Zeitüberschreitung",
         "umfang": "Bricht eine optionale Liste, etwa die Beratungen, nach 60 Sekunden ohne Antwort oder mit HTTP 504 "
                   "ab, lassen wir diese Liste ruhen, auch im Vollabgleich: zuerst eine Stunde, danach jeweils doppelt "
                   "so lange, höchstens 24 Stunden. Die übrigen Listen gleichen wir weiter ab; danach holen wir die "
                   "ausgelassenen Änderungen nach."},
        {"abruf": "Vollabgleich", "wann": "nachts im Zeitfenster, standardmäßig ab 1 Uhr",
         "umfang": "Alle Listen vollständig, höchstens einmal je Nacht, standardmäßig mit Beginn zwischen 1 und 6 "
                   "Uhr, bei zuverlässig filternden Systemen derzeit alle 28 Tage. Bei Systemen mit "
                   "OParl-Schnittstelle legen wir ihn auf Wunsch in ein eigenes Zeitfenster; er endet mit dem "
                   "Fenster, das auch gilt, wenn wir ihn ausnahmsweise von Hand starten. Ohne eigenes Fenster kann er "
                   "von Hand auch tagsüber laufen."},
        {"abruf": "Dokumente", "wann": "mit dem Abgleich und stündlich",
         "umfang": "Neue Dateien laden wir, um ihren Text durchsuchbar zu machen und sie bei uns abzulegen; stündlich "
                   "holen wir höchstens 200 fehlende je System nach. Schlägt ein Abruf fehl, versuchen wir es "
                   "frühestens nach 15 Minuten, 1, 6, 24 und 72 Stunden erneut, danach alle sieben Tage. Öffnet "
                   "jemand bei uns ein Dokument, das wir nicht abgelegt haben, laden wir es dafür bei Ihnen."},
        {"abruf": "Dokumente prüfen", "wann": "stündlich",
         "umfang": "Meldet Ihre Schnittstelle ein Dokument als gelöscht oder ist es bei Ihnen nicht mehr abrufbar, "
                   "sperren wir es bei uns, sobald wir das bemerken; Kopie und Text löschen wir 30 Tage später. "
                   "Nicht gemeldete Löschungen finden wir über Stichproben per HEAD, höchstens 30 je Kommune und "
                   "Lauf; das kann dauern. Löschen Sie viele Dokumente auf einmal, schreiben Sie uns bitte. Geänderte "
                   "Dokumente laden wir neu, höchstens 200 je Lauf."},
        {"abruf": "Personenfotos", "wann": "montags um 3 Uhr",
         "umfang": "Nur bei Systemen, für die wir die Adressen der Fotos eingerichtet haben, höchstens 500 Personen je "
                   "Kommune. Jedes Foto fragen wir höchstens alle 30 Tage an, auch wenn es fehlte oder der Abruf "
                   "fehlschlug. Ist der Dokumentabruf für Ihr System abgeschaltet oder pausieren wir es nach "
                   "wiederholten Fehlern, laden wir keine Fotos."},
        {"abruf": "robots.txt", "wann": "vor dem ersten Abruf, dann täglich",
         "umfang": "Jeder unserer Dienste liest sie vor seinem ersten Abruf, eine je Hostname, und nutzt sie "
                   "höchstens 24 Stunden, solange sie erreichbar ist. Fehlt sie (HTTP 4xx außer 408 und 429), ist "
                   "alles erlaubt. Ist sie nicht erreichbar, versuchen wir es frühestens nach 15 Minuten wieder. Bis "
                   "das gelingt, gilt die zuletzt gelesene Fassung weiter; gab es keine, stellen wir die Abrufe "
                   "zurück."},
        {"abruf": "Erstprüfung", "wann": "vor der Aufnahme",
         "umfang": "Ob eine Kommune für uns infrage kommt, prüfen wir mit höchstens fünf Anfragen, robots.txt und "
                   "Weiterleitungen eingerechnet. Bei der Aufnahme lesen wir das System und die Liste der Kommunen, "
                   "höchstens 20 Seiten; regelmäßig fragen wir ein neues System erst ab, wenn wir es eigens "
                   "aktivieren. Neu entdeckte Kommunen nehmen wir erst in Listen und Übersichten auf, wenn wir sie "
                   "geprüft haben."},
        {"abruf": "Live-Übertragung und Geoportale", "wann": "rund um Sitzungen und täglich um 4:50 Uhr",
         "umfang": "Begleiten wir eine Sitzung live, fragen wir beim Streaming-Anbieter einmal je Minute, ob "
                   "übertragen wird, ab 45 Minuten vor dem Beginn und längstens bis 10 Stunden danach; während der "
                   "Übertragung lesen wir standardmäßig alle 10 Sekunden ein Einzelbild, mit 2 bis 4 Anfragen. "
                   "Geoportale fragen wir täglich nach den Umrissen von Bebauungsplänen. Ihre robots.txt werten diese "
                   "Abrufe nicht aus; möchten Sie sie nicht, schreiben Sie uns."},
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
        "verweise": [("Über unseren Ingestor", "/ingestor/"), ("Open Source", "/open-source/"),
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
    "ingestor": {"kennung": ABRUF_KENNUNG, "selbstbetrieb": ABRUF_SELBSTBETRIEB, "takt": ABRUF_TAKT,
                 "mailto": ABRUF_MAILTO, "abrufregeln": ABRUF_REGELN,
                 "einzelheiten": ABRUF_EINZELHEITEN},
}
