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
        {"label": "E-Mail", "wert": "hello@mandari.de", "url": ""},
        {"label": "User-Agent", "wert": "mandari-ingestor", "url": ""},
        {"label": "Datenquellen", "wert": "Quellennachweise", "url": "/quellen/"},
        {"label": "Schnittstelle", "wert": "oparl.mandari.de", "url": "https://oparl.mandari.de"},
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

CRAWLER_RAND = [
    {"type": "fakten", "value": {"titel": "", "fakten": [
        {"begriff": "User-Agent", "wert": "mandari-ingestor (+https://mandari.de/crawler)"},
        {"begriff": "Abrufrate", "wert": "höchstens eine Anfrage alle zwei Sekunden je Server"},
        {"begriff": "Regeln", "wert": "robots.txt nach RFC 9309"},
        {"begriff": "Kontakt", "wert": "hello@mandari.de"},
    ]}},
]


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
    "crawler_rand": CRAWLER_RAND,
}
