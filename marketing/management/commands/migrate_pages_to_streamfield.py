"""
Management Command: Migriert alle Marketing- und Legal-Pages auf das StreamField-System.

Übernimmt die Inhalte aus den hardcoded HTML-Templates und übersetzt sie in
strukturierte StreamField-Blöcke, die im Wagtail-Admin pflegbar sind.

Idempotent: kann mehrfach laufen, überschreibt aber bestehende body-Inhalte
nur mit --force.

Usage:
    python manage.py migrate_pages_to_streamfield                  # alle Pages
    python manage.py migrate_pages_to_streamfield --pages preise produkt
    python manage.py migrate_pages_to_streamfield --force          # überschreibt
"""

from __future__ import annotations

from django.core.management.base import BaseCommand
from wagtail.blocks import StreamValue


# ════════════════════════════════════════════════════════════════════════
#  HILFSFUNKTIONEN — wiederverwendbare Block-Strukturen
# ════════════════════════════════════════════════════════════════════════


def cta(label, url, icon="", style="primary"):
    return {"label": label, "url": url, "icon": icon, "style": style}


def trust_item(icon, bold, normal=""):
    return {"icon": icon, "label_bold": bold, "label_normal": normal}


def card(*, color, icon, title, subtitle="", description="", bullets=None,
         cta_label="", cta_url="", cta_icon="", badge="", status_badges=None):
    return {
        "color": color, "icon": icon, "badge": badge,
        "status_badges": status_badges or [],
        "title": title,
        "subtitle": subtitle, "description": description,
        "bullets": bullets or [],
        "cta_label": cta_label, "cta_url": cta_url, "cta_icon": cta_icon,
    }


def sbadge(text, icon="", color="auto"):
    """Status-Badge for use inside a Mandari-Card's status_badges list."""
    return {"text": text, "icon": icon, "color": color}


def bullet(text, icon="check"):
    return {"icon": icon, "text": text}


def hdr(*, badge_text="", badge_icon="", badge_color="primary",
        title, subline="", align="left", anchor_id=""):
    return {
        "badge_text": badge_text, "badge_icon": badge_icon,
        "badge_color": badge_color, "title": title, "subline": subline,
        "align": align, "anchor_id": anchor_id,
    }


def step(number, color, icon, title, description, duration="", meta_text=""):
    return {
        "number": number, "color": color, "icon": icon, "title": title,
        "description": description, "duration": duration, "meta_text": meta_text,
    }


def stat(value, label, color="primary"):
    return {"value": value, "label": label, "color": color}


# ════════════════════════════════════════════════════════════════════════
#  PAGE-DEFINITIONEN — pro Slug eine Liste von (block_type, value)-Tupeln
# ════════════════════════════════════════════════════════════════════════


def get_marketing_definitions() -> dict:
    """Marketing-Pages (MarketingPage Model) → body StreamField."""

    return {
        # ════════════════════════════════════════════════════════════
        # /transparenz/ — Quartals-Bericht
        # ════════════════════════════════════════════════════════════
        "transparenz": [
            ("hero", {
                "badge_text": "Transparenzbericht · jährlich", "badge_icon": "eye", "badge_color": "primary",
                "title": "Transparenzbericht", "title_highlight": "2026",
                "subline": "Was andere SaaS gerne verstecken, legen wir offen: Behördenanfragen, Sicherheitsvorfälle, Finanzlage, Hosting-Realität, Open-Source-Beiträge.",
                "subline_secondary": "Berichtszeitraum: 1. Januar bis 31. Dezember 2026 · Veröffentlicht: 26. April 2026 · Nächste Aktualisierung: Juli 2026",
                "ctas": [], "background_color": "primary",
            }),
            ("trust_banner", {"color": "primary", "items": [
                trust_item("gavel", "0", "Behördenanfragen"),
                trust_item("shield-check", "0", "Sicherheitsvorfälle"),
                trust_item("user", "1", "Solo-Founder"),
                trust_item("git-pull-request", "100 %", "Code offen"),
            ]}),
            ("stats_grid", {
                "header": hdr(badge_text="01 · Behördenanfragen", badge_icon="gavel", badge_color="blue",
                              title="Behördenanfragen",
                              subline="Auskunftsersuchen, Beschlagnahmungen, alles was rechtlich an uns herangetragen wurde."),
                "columns": "4", "border_color": "blue",
                "items": [stat("0", "Strafverfolgung", "blue"), stat("0", "Geheimdienste", "blue"),
                          stat("0", "Zivilrechtlich", "blue"), stat("0", "Datenherausgaben", "blue")],
            }),
            ("warrant_canary", {
                "date": "26.04.2026",
                "body": "<p>Mandari wurde nicht durch eine Geheimhalteanordnung (z.&nbsp;B. nach § 95 GWB oder § 100b StPO) verpflichtet, Auskünfte unter Geheimhaltung zu erteilen.</p><p>Diese Erklärung wird vierteljährlich aktualisiert. Sollte sie verschwinden oder veralten, interpretiere das entsprechend.</p>",
            }),
            ("stats_grid", {
                "header": hdr(badge_text="02 · Sicherheitsvorfälle", badge_icon="shield-alert", badge_color="rose",
                              title="Sicherheitsvorfälle",
                              subline="Datenschutzvorfälle, Sicherheitslücken, Downtime mit Datenrelevanz."),
                "columns": "3", "border_color": "green",
                "items": [stat("0", "Datenschutzvorfälle", "green"), stat("0", "Gemeldete CVEs", "green"),
                          stat("0", "DSGVO-Meldungen", "green")],
            }),
            ("stats_grid", {
                "header": hdr(badge_text="03 · Nutzung & Reichweite", badge_icon="bar-chart-3", badge_color="green",
                              title="Nutzung & Reichweite",
                              subline="Anonymisierte Aggregate, keine individuellen Profile, keine Tracker."),
                "columns": "4", "border_color": "primary",
                "items": [stat("0", "Pilot-Kommunen live", "green"), stat("~12", "Erstgespräche", "amber"),
                          stat("~3 k", "Insight-Aufrufe / Mon", "primary"), stat("2", "OParl-Quellen", "blue")],
            }),
            ("disclaimer_box", {
                "icon": "info", "color": "amber",
                "body": "<p><strong>Reality Check:</strong> Wir sind in der Beta-Phase. Diese Zahlen sind klein, und genau deshalb veröffentlichen wir sie. Wir gewinnen nichts, indem wir uns größer machen, als wir sind.</p>",
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="04 · Finanztransparenz", badge_icon="banknote", badge_color="teal",
                              title="Finanztransparenz",
                              subline="Solo-Founder-Vorteil: ich kann offen zeigen, wie das Geld fließt."),
                "left_card": card(color="green", icon="trending-up", title="Einnahmen 2026",
                                  subtitle="~ 0 € · Beta-Phase",
                                  description="Beta-Phase, noch keine Lizenzeinnahmen.",
                                  bullets=[bullet("Work-Lizenzen: noch nicht aktiv", "circle-dot"),
                                           bullet("Spenden: 0 € (Konzept in Vorbereitung)", "circle-dot"),
                                           bullet("Fördermittel: in Beantragung", "circle-dot")]),
                "right_card": card(color="rose", icon="trending-down", title="Ausgaben 2026",
                                   subtitle="~ 1.200 € hochgerechnet",
                                   description="Hochgerechnet auf das Jahr (laufende Kosten).",
                                   bullets=[bullet("Hosting (Hetzner): ~ 60 €/Mon", "server"),
                                            bullet("Domain & DNS: ~ 30 €/Jahr", "globe"),
                                            bullet("Tools & Buchhaltung: ~ 40 €/Mon", "briefcase"),
                                            bullet("KI-Inferenz Tests: ~ 20 €/Mon", "brain")]),
            }),
            ("mandari_cards", {
                "header": hdr(badge_text="07 · So kannst du beitragen", badge_icon="hand-heart", badge_color="green",
                              title="So kannst du beitragen",
                              subline="Wenn dir Mandari etwas wert ist: vier Wege, das Projekt finanziell mitzutragen.",
                              anchor_id="unterstuetzen"),
                "columns": "4", "background": "white",
                "cards": [
                    card(color="primary", icon="github", title="GitHub Sponsors", subtitle="0 % Plattformgebühr",
                         description="Für Devs und Tech-Community.",
                         cta_label="Öffnen", cta_url="https://github.com/sponsors/mandariOSS", cta_icon="external-link"),
                    card(color="amber", icon="coffee", title="Ko-fi", subtitle="3 € reicht schon",
                         description="Niedrigschwellig. „Spendier dem Founder einen Kaffee.\"",
                         cta_label="Öffnen", cta_url="https://ko-fi.com/mandari", cta_icon="external-link"),
                    card(color="rose", icon="cookie", title="Buy Me a Coffee", subtitle="Ein-Klick-Tip",
                         description="Ohne Account, ohne Hürde. PayPal oder Karte.",
                         cta_label="Öffnen", cta_url="https://buymeacoffee.com/mandari", cta_icon="external-link"),
                    card(color="green", icon="banknote", title="SEPA-Direkt", subtitle="0 % Gebühren",
                         description="Für Kommunen, Stiftungen, Großspender. Bankdaten auf Anfrage.",
                         cta_label="Anfragen", cta_url="/kontakt/?subject=SEPA-Spende-Bankdaten", cta_icon="mail"),
                ],
            }),
            ("disclaimer_box", {
                "icon": "info", "color": "gray",
                "body": "<p><strong>Ehrlich gesagt:</strong> Spenden sind aktuell <em>nicht</em> steuerlich absetzbar, da Mandari als Einzelunternehmen aufgestellt ist. Eine Überführung in eine <strong>gemeinwohlorientierte Trägerstruktur</strong> (z.&nbsp;B. e.&nbsp;V., Genossenschaft, gGmbH oder Verantwortungseigentum) prüfen wir für 2027.</p>",
            }),
            ("gradient_cta", {
                "title": "Vermisst du eine Zahl?",
                "subline": "Wenn du etwas spezifisches sehen möchtest, sag Bescheid. Wir nehmen es auf.",
                "ctas": [cta("Vorschlag einreichen", "/kontakt/?subject=Transparenz", "message-square", "primary"),
                         cta("Updates abonnieren", "/blog/feed/", "rss", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /preise/ — Insight + Work + Session
        # ════════════════════════════════════════════════════════════
        "preise": [
            ("hero", {
                "badge_text": "Transparent · Open Source · Hosting in Deutschland", "badge_icon": "receipt-text", "badge_color": "primary",
                "title": "Faire Preise für", "title_highlight": "faire Demokratie.",
                "subline": "Insight ist kostenlos für Bürger:innen. Work kostet so viel, wie eine Person zum Bauen braucht. Session verhandeln wir individuell.",
                "subline_secondary": "Keine versteckten Kosten, keine „Enterprise pricing on request\"-Tricks, kein Lock-in. Du kannst alles auch selbst hosten.",
                "ctas": [cta("Beta-Zugang anfragen", "/kontakt/?subject=Beta-Zugang-Work", "zap", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "secondary"),
                         cta("Häufige Fragen", "#faq", "help-circle", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "green", "items": [
                trust_item("shield-check", "30 Tage", "rückerstattbar"),
                trust_item("eye", "Keine", "versteckten Kosten"),
                trust_item("github", "Code immer", "offen (AGPL-3.0)"),
                trust_item("server", "Hosting", "in Deutschland"),
            ]}),
            ("pricing_table", {
                "header": hdr(badge_text="Drei Produkte, klare Preise", badge_icon="layout-grid",
                              title="Was Mandari kostet", align="center",
                              subline="Alle Preise inkl. 19 % MwSt."),
                "tiers": [
                    {"color": "green", "name": "Mandari Insight", "subtitle": "Bürger:innen-Portal",
                     "badge": "Immer kostenlos", "price_main": "0 €", "price_unit": "für immer",
                     "price_note": "Querfinanziert über Work & Session",
                     "description": "Öffentlicher Zugang zu Ratsinformationen — ohne Anmeldung, ohne Tracker, ohne Limit.",
                     "features": [bullet("Volltextsuche & Kartenansicht"), bullet("KI-Zusammenfassungen & Chat (geplant)"),
                                  bullet("Abstimmungsverhalten einsehen"), bullet("Keine Anmeldung nötig"),
                                  bullet("Selbst-Hosting möglich")],
                     "is_highlighted": False, "cta_label": "Insight öffnen", "cta_url": "/insight/"},
                    {"color": "primary", "name": "Mandari Work", "subtitle": "Für Fraktionen · Pauschale ohne Userlimit",
                     "badge": "Beta-Phase", "price_main": "39,90 €", "price_unit": "/Monat inkl. MwSt.",
                     "price_note": "Beta-Kunden erhalten dauerhaft vergünstigte Konditionen",
                     "description": "Professionelle Sitzungsvorbereitung mit Team, KI und Antragsdatenbank.",
                     "features": [bullet("Alles aus Insight"), bullet("Team-Workspaces & Notizen"),
                                  bullet("Antragsdatenbank & Vorlagen"), bullet("Interne Abstimmungen & Termine"),
                                  bullet("KI-gestützte Recherche"), bullet("Unbegrenzte Nutzer:innen pro Fraktion & Gruppe"),
                                  bullet("Prioritäts-Support per E-Mail")],
                     "is_highlighted": True, "cta_label": "Jetzt buchen", "cta_url": "https://portal.mandari.de/buchen/"},
                    {"color": "blue", "name": "Mandari Session", "subtitle": "Verwaltungs-RIS",
                     "badge": "Auf Anfrage · In Entwicklung", "price_main": "Individuell",
                     "price_note": "Pro Kommune kalkuliert · faire Skalierung",
                     "description": "Vollständiges Sitzungsmanagement für Verwaltungen — die moderne Alternative zu proprietären RIS.",
                     "features": [bullet("Sitzungsplanung & Tagesordnung", "calendar-clock"),
                                  bullet("Einladungen (digital & print)", "mail"),
                                  bullet("Vorlagenpflege & Protokollierung", "file-text"),
                                  bullet("Sitzungsgeld & Aufwandsentschädigung", "banknote"),
                                  bullet("OParl-Export (maschinenlesbar)", "file-json"),
                                  bullet("Migration vom Alt-RIS", "users")],
                     "is_highlighted": False, "cta_label": "Angebot anfragen", "cta_url": "/kontakt/?subject=Session-Angebot"},
                ],
            }),
            ("disclaimer_box", {
                "icon": "rocket", "color": "amber",
                "body": "<p><strong>Pilot-Phase 2026: Konditionen verhandelbar.</strong> Für die ersten Pilot-Kommunen bauen wir individuelle Konditionen — günstigere Lizenzen, längere Laufzeiten, Pilot-Rabatt auf Session. Dafür: echtes Feedback und Bereitschaft zur Referenz. <a href=\"/partner/?subject=Pilot-Kommune\">Pilot-Kommune werden →</a></p>",
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Du wählst, wie Mandari läuft", badge_icon="git-branch",
                              title="Selbst hosten oder uns lassen", align="center",
                              subline="Open Source heißt: Du hast die Wahl."),
                "left_card": card(color="green", icon="server", title="Selbst-Hosting", subtitle="Kostenlos · volle Kontrolle",
                                  description="Lade dir den Stack runter, starte docker compose up, fertig.",
                                  bullets=[bullet("Volle Kontrolle über Daten & Infrastruktur"),
                                           bullet("Docker-Compose-Stack für jeden Linux-Server"),
                                           bullet("Community-Support via GitHub Discussions"),
                                           bullet("Dokumentation auf GitHub")],
                                  cta_label="Repo öffnen", cta_url="https://github.com/mandariOSS/mandari", cta_icon="github"),
                "right_card": card(color="primary", icon="cloud", title="Managed Service", subtitle="Wir hosten, du nutzt",
                                   description="Wir übernehmen Server, Backups, Updates, Monitoring.",
                                   bullets=[bullet("Kein Server-Management auf eurer Seite"),
                                            bullet("Automatische Updates & Sicherheitspatches"),
                                            bullet("Hosting in Deutschland (Hetzner / IONOS)"),
                                            bullet("Datenexport jederzeit, kein Lock-in")],
                                   cta_label="Managed Service anfragen", cta_url="/kontakt/?subject=Managed-Service", cta_icon="mail"),
            }),
            ("mandari_cards", {
                "header": hdr(badge_text="Offener Brief vom Founder", badge_icon="message-square-quote", badge_color="teal",
                              title="Warum genau diese Preise?",
                              subline="Andere SaaS verstecken ihre Kalkulation. Wir nicht. Hier ist, woraus sich 39,90 € zusammensetzen."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="rose", icon="user", title="Solo-Founder-Realität",
                         description="Mandari wird von einer Person gebaut — kein VC-Geld, keine 30-köpfige Sales-Abteilung. Damit das nachhaltig bleibt, müssen die Lizenzen die Entwicklungszeit decken."),
                    card(color="primary", icon="server-cog", title="Infrastruktur kostet",
                         description="Server, Backups, Monitoring, TLS, Datenbank-Cluster, KI-Inferenz: ein paar 100 €/Monat allein für die Infrastruktur. Davon fließt jeder Cent an deutsche Hosting-Partner."),
                    card(color="teal", icon="vote", title="Demokratie-Bonus",
                         description="Schulen, Universitäten, NGOs, Studierende — wer Demokratie stärkt, soll keine kommerziellen Preise zahlen. Vergünstigungen auf Anfrage."),
                ],
            }),
            ("accordion_faq", {
                "header": hdr(badge_text="Häufige Fragen", badge_icon="help-circle",
                              title="Was du sonst noch wissen solltest", align="center",
                              subline="Falls deine Frage hier nicht steht, schreib uns einfach."),
                "anchor_id": "faq", "background": "gray",
                "items": [
                    {"question": "Warum ist Insight kostenlos?",
                     "answer": "<p>Zugang zu kommunalpolitischen Informationen ist ein Grundrecht — nicht ein Premium-Feature. Insight finanziert sich quer über Work und Session. So bleibt der Bürger:innen-Zugang dauerhaft frei.</p>"},
                    {"question": "Wie viele Nutzer:innen sind in einer Lizenz enthalten?",
                     "answer": "<p><strong>Unbegrenzt viele.</strong> Eine Mandari-Work-Lizenz gilt pauschal pro Organisation und hat kein Nutzer-Limit.</p><p>Egal ob ihr 3 oder 30 Mandatsträger:innen seid, plus Büromitarbeitende und sachkundige Bürger:innen, der Pauschalpreis bleibt gleich.</p>"},
                    {"question": "Sind die Preise inkl. MwSt.?",
                     "answer": "<p>Ja, alle hier genannten Preise verstehen sich inkl. 19 % deutscher Mehrwertsteuer.</p>"},
                    {"question": "Gibt es Rabatte für Studierende, Schulen oder NGOs?",
                     "answer": "<p>Ja. Studierende, Schulen, Universitäten, gemeinnützige Vereine und NGOs bekommen vergünstigte Konditionen, bis hin zu kostenfreien Lizenzen für die Lehre. Schick uns kurz dein Anliegen mit Nachweis.</p>"},
                    {"question": "Was passiert mit meinen Daten bei Kündigung?",
                     "answer": "<p>Du bekommst vor Kündigung einen vollständigen Export deiner Daten — JSON oder CSV, wahlweise auch im OParl-Format.</p><p>Nach Vertragsende behalten wir die Daten 30 Tage als Backup, danach werden sie unwiderruflich gelöscht. Auf Wunsch sofort.</p>"},
                    {"question": "Kann ich Mandari komplett selbst hosten?",
                     "answer": "<p>Ja. Mandari ist AGPL-3.0 lizenziert. Lade dir den Code von GitHub, starte den Docker-Compose-Stack auf deinem Server, fertig.</p>"},
                    {"question": "Was kostet Mandari Session und wann ist es verfügbar?",
                     "answer": "<p>Session richtet sich an Verwaltungen und wird pro Kommune individuell kalkuliert. Verfügbar ab Q3-Q4 2026 für die ersten Pilot-Kommunen. Sprich uns früh an, Pilot-Konditionen sind verhandelbar.</p>"},
                ],
            }),
            ("gradient_cta", {
                "title": "Probier's einfach aus.",
                "subline": "Beta-Zugang zu Mandari Work ist kostenfrei für die ersten 14 Tage — keine Kreditkarte nötig.",
                "ctas": [cta("Beta-Zugang anfragen", "/kontakt/?subject=Beta-Zugang-Work", "zap", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "outline"),
                         cta("Selbst hosten", "https://github.com/mandariOSS/mandari", "github", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /produkt/
        # ════════════════════════════════════════════════════════════
        "produkt": [
            ("hero", {
                "badge_text": "Offenes Ökosystem · 100 % Open Source", "badge_icon": "unlock", "badge_color": "green",
                "title": "Drei Säulen für", "title_highlight": "bessere Ratsarbeit",
                "subline": "Mandari verbindet öffentliche Transparenz mit professionellen Workflows. Keine Anbieterabhängigkeit — Daten gehören euch.",
                "ctas": [cta("Demo anfragen", "/kontakt/", "mail", "primary"),
                         cta("Preise ansehen", "/preise/", "credit-card", "secondary")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "green", "items": [
                trust_item("database", "Datenexport", "jederzeit"),
                trust_item("code", "Offene Schnittstelle", "für alle"),
                trust_item("file-json", "OParl-Standard", "Import & Export"),
                trust_item("github", "Open Source", "AGPL-3.0"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Drei Module", badge_icon="layers",
                              title="Insight, Work, Session",
                              subline="Drei Komponenten, ein Ökosystem. Einzeln oder zusammen einsetzbar."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="green", icon="eye", title="Mandari Insight", subtitle="Bürger:innen-Portal · Kostenlos",
                         description="Transparenter Zugang zu Ratsinformationen — ohne Anmeldung, ohne Tracker.",
                         bullets=[bullet("Einblick in Anträge & Beschlüsse"), bullet("Volltextsuche über alle Dokumente"),
                                  bullet("Geografische Karte (geplant)"), bullet("Abstimmungsverhalten einsehen"),
                                  bullet("KI-Zusammenfassungen")],
                         badge="Live"),
                    card(color="primary", icon="briefcase", title="Mandari Work", subtitle="Fraktions-Plattform · 39,90 €/Mon inkl. MwSt.",
                         description="Professionelle Kollaboration für das gesamte Team — pauschal pro Organisation, ohne Nutzer-Limit.",
                         bullets=[bullet("Sitzungsvorbereitung im Team"), bullet("Interne Abstimmungen & Notizen"),
                                  bullet("Antragsdatenbank & Vorlagen"), bullet("Terminplanung"),
                                  bullet("KI-gestützte Recherche")],
                         cta_label="Jetzt buchen", cta_url="https://portal.mandari.de/buchen/", cta_icon="zap",
                         badge="Beta"),
                    card(color="blue", icon="building-2", title="Mandari Session", subtitle="Verwaltungs-RIS · Auf Anfrage",
                         description="Vollständiges Sitzungsmanagement für Kommunen — die moderne Alternative zu proprietären RIS.",
                         bullets=[bullet("Sitzungsplanung & Tagesordnung", "calendar-clock"),
                                  bullet("Einladungen (digital & print)", "mail"),
                                  bullet("Vorlagen- & Datenpflege", "file-text"),
                                  bullet("Sitzungsgeld & Aufwand", "banknote"),
                                  bullet("OParl-Export aus der Box", "file-json")],
                         badge="Q3-Q4 2026"),
                ],
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Flexibel einsetzbar", badge_icon="git-branch",
                              title="Mandari Work: Zwei Einsatzszenarien", align="center",
                              subline="Egal ob eure Kommune Mandari Session nutzt oder ein anderes RIS — Mandari Work funktioniert immer.",
                              anchor_id="zielgruppen"),
                "left_card": card(color="blue", icon="link", title="Mit Mandari Session", subtitle="Volle Integration",
                                  description="Wenn eure Kommune Mandari Session als RIS nutzt, profitiert ihr von nahtloser Integration.",
                                  bullets=[bullet("Echtzeit-Synchronisation", "zap"),
                                           bullet("Nicht-öffentliche Vorlagen automatisch verfügbar", "zap"),
                                           bullet("Direkte Antragseinreichung", "zap"),
                                           bullet("Ein Ökosystem, ein Login", "zap")]),
                "right_card": card(color="green", icon="plug", title="Mit externem RIS", subtitle="Via OParl-Schnittstelle",
                                   description="Eure Kommune nutzt ALLRIS, regisafe, Somacos oder ein anderes RIS mit OParl? Kein Problem.",
                                   bullets=[bullet("Automatischer Import öffentlicher Daten", "check-circle"),
                                            bullet("Alle Work-Features nutzbar", "check-circle"),
                                            bullet("Unabhängig vom RIS-Anbieter", "check-circle"),
                                            bullet("Kein Wechsel des RIS nötig", "check-circle")]),
            }),
            ("gradient_cta", {
                "title": "Überzeugen Sie sich selbst",
                "subline": "Vereinbaren Sie eine kostenlose Demo und sehen Sie Mandari in Aktion. Alle Produkte sind zu 100 % Open Source.",
                "ctas": [cta("Jetzt Demo anfragen", "/kontakt/", "mail", "primary"),
                         cta("Work jetzt buchen", "https://portal.mandari.de/buchen/", "zap", "outline"),
                         cta("Open Source", "/open-source/", "github", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /partner/ — Sechs konkrete Partner-Wege
        # ════════════════════════════════════════════════════════════
        "partner": [
            ("hero", {
                "badge_text": "Solo-Founder · Beta-Phase · offen für Mit-Träger",
                "badge_icon": "hand-heart", "badge_color": "primary",
                "title": "Mandari wächst.", "title_highlight": "Komm dazu.",
                "subline": "Ein modernes, offenes Ratsinformationssystem für Deutschland baut sich nicht allein auf. Es gibt sechs konkrete Wege, dieses Projekt mitzutragen — vom unterzeichneten Pilot-Vertrag bis zum 5-Minuten-Pull-Request.",
                "subline_secondary": "Auf dieser Seite siehst du sie alle, ehrlich beschrieben, mit klaren nächsten Schritten und ohne Marketing-Phrasen.",
                "ctas": [cta("Partner werden", "/kontakt/?subject=Partnerschaft", "mail", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "secondary"),
                         cta("Finanziell unterstützen", "#mittragen", "heart", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "primary", "items": [
                trust_item("github", "AGPL-3.0", "Code öffentlich"),
                trust_item("user", "Solo-Founder", "Sven Konopka"),
                trust_item("rocket", "Pilot-Phase 2026", "jetzt einsteigen"),
                trust_item("hand-heart", "Förderung & Spenden", "möglich"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Sechs konkrete Wege", badge_icon="sparkles",
                              title="Wer Mandari mitträgt",
                              subline="Von Verwaltungen über Stiftungen und Parteien bis zu einzelnen Engagierten — Civic-Tech entsteht im Zusammenspiel vieler Rollen. Jede Säule zählt, keine ist wichtiger als die anderen."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="green", icon="building-2", title="Pilot-Kommunen",
                         subtitle="Verwaltungen & Räte, die starten wollen",
                         status_badges=[sbadge("Offen ab sofort", "rocket", "auto"),
                                        sbadge("Pilot-Konditionen", color="amber")],
                         description="Die ersten Kommunen, die ihre OParl-Quelle anbinden — wir bauen zusammen die Praxis-Erfahrung auf, die Mandari produktionsreif macht.",
                         bullets=[bullet("Anbindung in Tagen statt Monaten"),
                                  bullet("Pilot-Konditionen & direkter Draht zum Founder"),
                                  bullet("Mitgestaltung der Roadmap")],
                         cta_label="Pilot-Kommune werden", cta_url="/kontakt/?subject=Pilot-Kommune", cta_icon="rocket"),
                    card(color="primary", icon="hand-heart", title="Förderer & Mit-Träger",
                         subtitle="Stiftungen, Fonds, Kommunen mit Weitblick",
                         status_badges=[sbadge("Anträge laufend", "hand-heart", "auto"),
                                        sbadge("Co-Funding möglich", color="gray")],
                         description="Mandari ist demokratische Infrastruktur und braucht eine finanzielle Basis, die nicht von einzelnen Lizenzdeals abhängt. Hier ist Raum für Förderpartnerschaften.",
                         bullets=[bullet("Projekt- oder Jahresförderung"),
                                  bullet("Co-Funding & Antrags-Unterstützung"),
                                  bullet("Sichtbar gelistet als Mit-Träger")],
                         cta_label="Förderung besprechen", cta_url="/kontakt/?subject=Förderpartnerschaft", cta_icon="hand-heart"),
                    card(color="blue", icon="vote", title="Parteien & Fraktionen",
                         subtitle="Werkzeug für Mandatsträger:innen",
                         status_badges=[sbadge("Beta-Lizenzen aktiv", "vote", "auto"),
                                        sbadge("Parteien-neutral", color="gray")],
                         description="Wir machen Mandari Work für eure Fraktionen verfügbar — politisch neutral, parteienoffen, mit allen demokratischen Akteur:innen gleichermaßen.",
                         bullets=[bullet("Pauschale Fraktions-Lizenz, ohne Nutzer-Limit"),
                                  bullet("Onboarding für Mandatsträger:innen"),
                                  bullet("Empfehlung an Orts- & Kreisverbände")],
                         cta_label="Fraktion ausstatten", cta_url="/kontakt/?subject=Parteien-Partnerschaft", cta_icon="vote"),
                    card(color="amber", icon="megaphone", title="NGOs & Initiativen",
                         subtitle="Für mehr Transparenz & Beteiligung",
                         status_badges=[sbadge("Erste Allianzen", "megaphone", "auto"),
                                        sbadge("NGO-Konditionen", color="gray")],
                         description="Bürgerstiftungen, Demokratie-Vereine, Transparenz-Initiativen, OK Labs — wir verstärken eure Wirkung mit offenen Daten und teilbaren Bürger-Tools.",
                         bullets=[bullet("Whitelabel- & Embed-Möglichkeiten"),
                                  bullet("Co-Marketing & gemeinsame Veranstaltungen"),
                                  bullet("Vergünstigte NGO-Konditionen")],
                         cta_label="Allianz starten", cta_url="/kontakt/?subject=NGO-Partnerschaft", cta_icon="megaphone"),
                    card(color="rose", icon="briefcase", title="IT-Dienstleister",
                         subtitle="Setup & Betreuung als Reseller",
                         status_badges=[sbadge("Reseller ab Q2 2026", "briefcase", "auto"),
                                        sbadge("Marge verhandelbar", color="gray")],
                         description="Lokale IT-Häuser, die Mandari für ihre Kommunal-Kunden einrichten, konfigurieren und im Alltag begleiten — als verlängerter Arm in eurem Netzwerk.",
                         bullets=[bullet("Reseller-Marge (verhandelbar)"),
                                  bullet("Technische Schulung & Doku"),
                                  bullet("Listing als zertifizierter Partner")],
                         cta_label="Reseller-Gespräch starten", cta_url="/kontakt/?subject=Reseller-Partner", cta_icon="handshake"),
                    card(color="teal", icon="award", title="Beirat & Mentor:innen",
                         subtitle="Erfahrung aus Verwaltung & Civic-Tech",
                         status_badges=[sbadge("0 von 5 besetzt", "award", "auto"),
                                        sbadge("2–4 h pro Quartal", color="gray")],
                         description="Erfahrene Köpfe, die Mandari strategisch begleiten, Türen öffnen und Sparring auf Augenhöhe geben — 2 bis 4 Stunden im Quartal genügen schon.",
                         bullets=[bullet("Sichtbare Position auf Team-Seite"),
                                  bullet("Mitsprache an Produkt-Entscheidungen"),
                                  bullet("Optional: Aufwandsentschädigung")],
                         cta_label="Beirat anbieten", cta_url="/kontakt/?subject=Beirat-Position", cta_icon="users"),
                ],
            }),
            ("step_process", {
                "header": hdr(badge_text="Vom Erstkontakt zur Zusammenarbeit", badge_icon="route", badge_color="blue",
                              title="So läuft eine Partnerschaft konkret ab", align="center",
                              subline="Egal welche Rolle, der Weg ist immer derselbe: schlank, ohne Sales-Trichter, in vier nachvollziehbaren Schritten."),
                "columns": "4", "background": "gray",
                "steps": [
                    step("01", "primary", "message-square", "Erstgespräch",
                         "Per Mail oder direkt im 30-Minuten-Call. Du erzählst, was du dir vorstellst, ich erkläre, was realistisch ist.",
                         duration="30 Min", meta_text="kostenlos · unverbindlich"),
                    step("02", "green", "file-search", "Scope & Konditionen",
                         "Was passt zueinander? Schriftliches Ein-Seiten-Memorandum mit Aufwand, Konditionen und Verantwortlichkeiten.",
                         duration="1 Woche", meta_text="1 Seite · klar lesbar"),
                    step("03", "blue", "signature", "Vertrag oder MoU",
                         "Pilot-Kommunen unterschreiben einen schlanken AVV+Pilotvertrag, bei Allianzen reicht oft ein Memorandum.",
                         duration="2–3 Wochen", meta_text="DSGVO-fest"),
                    step("04", "amber", "rocket", "Loslegen",
                         "Onboarding, geteilter Slack/Matrix-Kanal, regelmäßiges Sync. Du bekommst direkten Draht zum Founder, kein Ticket-System.",
                         duration="Tage", meta_text="Anbindung in Tagen"),
                ],
                "note_html": "<p><strong>Solo-Founder-Realität:</strong> Du sprichst direkt mit Sven, ohne Sales-Pipeline und ohne Kundenservice-Schicht. Das macht uns schnell, hat aber natürliche Kapazitäts-Grenzen — ehrliche Wartezeit-Auskunft inklusive.</p>",
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Allianz statt Konkurrenz", badge_icon="network", badge_color="amber",
                              title="Wir spielen gerne mit anderen", align="center",
                              subline="Open-Source-Civic-Tech ist ein Ökosystem, kein Wettbewerb. Hosting in Deutschland ist Pflicht, nicht Kür."),
                "left_card": card(color="amber", icon="globe", title="Civic-Tech-Allianzen",
                                  subtitle="OParl, Code for Germany, OKFN, D64 …",
                                  description="Wir suchen den Austausch mit allen, die sich für offene Daten und demokratische Beteiligung einsetzen:",
                                  bullets=[bullet("Beiträge zum OParl-Standard (Vendor-Extensions, Bugfixes)", "git-branch"),
                                           bullet("Co-Marketing & gemeinsame Veranstaltungen", "megaphone"),
                                           bullet("Wissensaustausch & gegenseitige Verlinkung", "book-open")]),
                "right_card": card(color="gray", icon="server", title="Hosting-Partner",
                                   subtitle="Deutsche, DSGVO-konforme Anbieter",
                                   description="Mandari läuft auf deutschen Servern, Punkt. Wir suchen Hosting-Partner, die Spezialtarife für unsere Kunden anbieten:",
                                   bullets=[bullet("Hetzner, IONOS, Strato, Open Telekom Cloud & Vergleichbare", "shield-check"),
                                            bullet("Docker-Compose-Stack, läuft auf jedem Linux", "layers"),
                                            bullet("Auftragsverarbeitungsverträge nach Art. 28 DSGVO", "badge-check")]),
            }),
            ("tech_partner_grid", {
                "header": hdr(badge_text="Auf wessen Schultern wir stehen", badge_icon="package-open", badge_color="gray",
                              title="Unsere echten Tech-Partnerschaften", align="center",
                              subline="Mandari wäre ohne diese Open-Source-Projekte nicht möglich. Sie verdienen Sichtbarkeit — und Beiträge zurück."),
                "partners": [
                    {"name": "Django", "icon": "layout-template", "color": "green",
                     "description": "Web-Framework, das Fundament", "url": "https://www.djangoproject.com/"},
                    {"name": "Wagtail", "icon": "feather", "color": "blue",
                     "description": "CMS, Marketing-Site", "url": "https://wagtail.org/"},
                    {"name": "OParl", "icon": "plug", "color": "primary",
                     "description": "Standard, die Datenquelle", "url": "https://oparl.org/"},
                    {"name": "PostgreSQL", "icon": "database", "color": "blue",
                     "description": "Datenbank, alles persistent", "url": "https://www.postgresql.org/"},
                    {"name": "HTMX", "icon": "zap", "color": "primary",
                     "description": "Frontend, kein SPA-Overkill", "url": "https://htmx.org/"},
                    {"name": "Tailwind", "icon": "palette", "color": "blue",
                     "description": "CSS, was du gerade siehst", "url": "https://tailwindcss.com/"},
                    {"name": "Lucide", "icon": "sparkle", "color": "amber",
                     "description": "Icons, alle hier auf der Seite", "url": "https://lucide.dev/"},
                    {"name": "Altcha", "icon": "shield-check", "color": "green",
                     "description": "Spam-Schutz ohne CAPTCHA", "url": "https://altcha.org/"},
                ],
            }),
            ("disclaimer_box", {
                "icon": "git-pull-request", "color": "primary",
                "body": "<p><strong>Was wir zurückgeben:</strong> Mandari ist selbst <strong>AGPL-3.0</strong>, der gesamte Code ist offen. Vendor-Extensions zum OParl-Standard werden im <a href=\"https://github.com/mandariOSS\">öffentlichen Repository</a> dokumentiert und der OParl-Working-Group vorgeschlagen.</p>",
            }),
            ("mandari_cards", {
                "header": hdr(badge_text="Schon ab fünf Minuten", badge_icon="zap", badge_color="green",
                              title="Du musst keine Organisation sein", align="center",
                              subline="Die meisten Beiträge zu Open Source kommen von Einzelnen. Hier sind vier Wege, ohne Vertrag oder Verpflichtung mitzubauen."),
                "columns": "4", "background": "white",
                "cards": [
                    card(color="primary", icon="code-2", title="Code beitragen",
                         description="Pull Requests sind willkommen — von der Tippfehler-Korrektur bis zur neuen Funktion.",
                         cta_label="GitHub-Repo öffnen", cta_url="https://github.com/mandariOSS", cta_icon="external-link"),
                    card(color="amber", icon="languages", title="Übersetzen",
                         description="Aktuell nur Deutsch. Englisch und EU-Sprachen kommen — sprich deine Muttersprache?",
                         cta_label="Sprache anbieten", cta_url="/kontakt/?subject=Übersetzung", cta_icon="arrow-right"),
                    card(color="green", icon="bug", title="Testen & melden",
                         description="Beta-Tester:innen, die UI-Bugs, Datenfehler oder Verbesserungs­ideen rückmelden, sind Gold wert.",
                         cta_label="Tester werden", cta_url="/kontakt/?subject=Beta-Tester", cta_icon="arrow-right"),
                    card(color="blue", icon="share-2", title="Verbreiten",
                         description="Vortrag im OK Lab, Blog-Post, Social-Media-Hinweis, Empfehlung an deine Bürgermeisterin — alles hilft.",
                         cta_label="Materialien anfragen", cta_url="/kontakt/?subject=Mandari-verbreiten", cta_icon="arrow-right"),
                ],
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Finanziell mittragen", badge_icon="hand-heart",
                              title="Damit Mandari unabhängig bleiben kann", align="center",
                              subline="Open Source ist kostenfrei, Open-Source-Entwicklung nicht. Hier siehst du, wie du das Projekt finanziell stärkst.",
                              anchor_id="mittragen"),
                "left_card": card(color="primary", icon="landmark", title="Institutionelle Förderung",
                                  subtitle="Stiftungen & Fördermittel",
                                  description="Wir bewerben uns auf passende Programme — wenn du dort Kontakte hast oder uns weiterempfehlen kannst, freuen wir uns:",
                                  bullets=[bullet("Sovereign Tech Fund (BMWK), kritische Open-Source-Infrastruktur", "circle-dot"),
                                           bullet("Prototype Fund (OKFN / BMBF), frühe Civic-Tech-Projekte", "circle-dot"),
                                           bullet("NLnet Foundation, Open-Source-Förderung EU-weit", "circle-dot"),
                                           bullet("Mercator-, Bertelsmann-, Telekom-Stiftung & Vergleichbare", "circle-dot")],
                                  cta_label="Programm empfehlen oder co-bewerben", cta_url="/kontakt/?subject=Förderprogramm-Empfehlung", cta_icon="arrow-right"),
                "right_card": card(color="green", icon="heart-handshake", title="Direkte Unterstützung",
                                   subtitle="Spenden, Sponsoring & Kommunal-Mitfinanzierung",
                                   description="Schneller, unbürokratischer Weg — von Einzelpersonen, Unternehmen oder Kommunen, die Mandari als demokratische Infrastruktur stärken wollen:",
                                   bullets=[bullet("GitHub Sponsors — monatlich oder einmalig (0 % Plattformgebühr)", "github"),
                                            bullet("Ko-fi — niedrigschwellig ab 3 €", "coffee"),
                                            bullet("Buy Me a Coffee — Ein-Klick-Tip ohne Account", "cookie"),
                                            bullet("SEPA-Überweisung — Bankdaten auf Anfrage (0 % Gebühren)", "banknote"),
                                            bullet("Kommunale Ko-Finanzierung oder Unternehmens-Sponsoring mit Rechnung", "building")],
                                   cta_label="Beitragsweg besprechen", cta_url="/kontakt/?subject=Direkte-Unterstützung", cta_icon="arrow-right"),
            }),
            ("disclaimer_box", {
                "icon": "info", "color": "gray",
                "body": "<p><strong>Aktueller Stand:</strong> Mandari ist als Einzelunternehmen aufgestellt, Spenden sind aktuell <em>nicht</em> steuerlich absetzbar. Die Überführung in eine <strong>gemeinwohlorientierte Trägerstruktur</strong> (z.&nbsp;B. e.&nbsp;V., Genossenschaft, gGmbH oder Verantwortungseigentum) prüfen wir, sobald die Pilot-Phase Fahrt aufnimmt. Transparenz hat Vorrang.</p>",
            }),
            ("mandari_cards", {
                "header": hdr(badge_text="Worauf du dich verlassen kannst", badge_icon="shield-check",
                              title="Drei Versprechen an alle Partner", align="center",
                              subline="Weil Vertrauen die Grundlage jeder Zusammenarbeit ist."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="green", icon="check-check", title="Daten bleiben neutral",
                         description="OParl-Daten zeigen wir vollständig und unverändert an — egal wer Partner ist. Niemand kann unbequeme Beschlüsse rauspolieren."),
                    card(color="blue", icon="scale", title="Politisch ausgewogen",
                         description="Wir arbeiten mit allen demokratischen Akteur:innen gleichberechtigt. Mandari wird kein Werkzeug parteipolitischer Einseitigkeit."),
                    card(color="amber", icon="eye", title="Transparent nach innen & außen",
                         description="Code offen (AGPL), Förderquellen offen, Partnerlisten offen. Jede Partnerschaft hält dieser Transparenz stand."),
                ],
            }),
            ("gradient_cta", {
                "title": "Lass uns reden",
                "subline": "Egal in welcher Rolle du dabei sein möchtest — ein 30-Minuten-Erstgespräch ist immer drin. Kostenlos, unverbindlich, auf Augenhöhe.",
                "ctas": [cta("Direkt schreiben", "/kontakt/", "mail", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "outline"),
                         cta("GitHub", "https://github.com/mandariOSS", "github", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /mitmachen/
        # ════════════════════════════════════════════════════════════
        "mitmachen": [
            ("hero", {
                "badge_text": "Open Source, seit Tag eins", "badge_icon": "git-branch-plus", "badge_color": "primary",
                "title": "Mandari ist offen.", "title_highlight": "Bau mit.",
                "subline": "Du musst kein Profi sein, kein Vertrag, kein Geld. Eine Stunde reicht, manchmal sogar fünf Minuten.",
                "subline_secondary": "Open Source heißt: Du bist willkommen. Wir kommentieren neue Issues und PRs binnen 24 Stunden.",
                "ctas": [cta("Repo öffnen", "https://github.com/mandariOSS", "github", "primary"),
                         cta("Good first issues", "https://github.com/mandariOSS/mandari/labels/good%20first%20issue", "sparkles", "secondary"),
                         cta("Hallo sagen", "/kontakt/?subject=Hallo-aus-der-Community", "hand", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "green", "items": [
                trust_item("github", "AGPL-3.0", "100 % Open Source"),
                trust_item("sparkles", "Auch Tippfehler", "sind willkommen"),
                trust_item("user-plus", "Mentoring", "für deine erste PR"),
                trust_item("message-circle-heart", "Antwort", "binnen 24h"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Sechs Wege, heute zu starten", badge_icon="layout-grid",
                              title="Such dir aus, was zu dir passt",
                              subline="Jede Karte zeigt klar: Wie schwer, wie viel Zeit, was der erste Schritt ist."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="primary", icon="code-2", title="Code beitragen", subtitle="Django · HTMX · PostgreSQL",
                         description="Pull Requests jeder Größe sind willkommen — vom Tippfehler bis zum neuen OParl-Adapter.",
                         bullets=[bullet("Repo klonen, docker compose up", "terminal"),
                                  bullet("Label good first issue wählen", "search"),
                                  bullet("PR aufmachen, wir lesen mit", "git-pull-request")],
                         cta_label="Erstes Issue finden", cta_url="https://github.com/mandariOSS/mandari/labels/good%20first%20issue", cta_icon="github"),
                    card(color="green", icon="bug", title="Testen & Bugs melden", subtitle="Der niederschwelligste Beitrag",
                         description="Du klickst dich durch Mandari, findest etwas Komisches und schreibst zwei Sätze auf — fertig. Gold wert.",
                         bullets=[bullet("Auf Insight klicken, was ausprobieren", "mouse-pointer-click"),
                                  bullet("Screenshot machen wenn was schief geht", "camera"),
                                  bullet("Bug-Report öffnen, Template hilft", "message-square-warning")],
                         cta_label="Bug melden", cta_url="https://github.com/mandariOSS/mandari/issues/new?template=bug_report.md", cta_icon="bug"),
                    card(color="amber", icon="languages", title="Übersetzen", subtitle="Aktuell nur DE, EU-Sprachen folgen",
                         description="Mandari soll europaweit zugänglich werden. Wenn du eine EU-Sprache als Muttersprache sprichst, brauchen wir dich.",
                         bullets=[bullet("Deutsch (vollständig)", "check-circle-2"),
                                  bullet("Englisch (i18n-Setup läuft)", "loader"),
                                  bullet("Französisch, Niederländisch, Polnisch …", "circle-dashed")],
                         cta_label="Sprache anbieten", cta_url="/kontakt/?subject=Übersetzung-Sprache", cta_icon="languages"),
                    card(color="blue", icon="book-open", title="Doku schreiben", subtitle="Markdown reicht, kein Setup nötig",
                         description="Wenn du Mandari verstanden hast, schreib's auf — die nächste Person spart Stunden. Self-Hosting-Guides sind besonders gefragt.",
                         bullets=[bullet("Self-Hosting auf Hetzner / IONOS", "server"),
                                  bullet("OParl-Adapter für eure Kommune", "puzzle"),
                                  bullet("API-Beispiele & Cookbook", "file-text")],
                         cta_label="Doku-Verzeichnis öffnen", cta_url="https://github.com/mandariOSS/mandari/tree/main/docs", cta_icon="file-text"),
                    card(color="rose", icon="palette", title="Design beitragen", subtitle="UI-Skizzen, Karten-Konzepte, Icons",
                         description="Du hast Auge für Bürger:innen-UX? Wir suchen Skizzen für komplexe Workflows.",
                         bullets=[bullet("Figma, Penpot, Excalidraw — frei wählbar", "figma"),
                                  bullet("Screenshots mit Markup", "image"),
                                  bullet("Auch nur Ideen-Skizzen helfen", "lightbulb")],
                         cta_label="Konzept zeigen", cta_url="/kontakt/?subject=Design-Beitrag", cta_icon="palette"),
                    card(color="teal", icon="megaphone", title="Verbreiten", subtitle="Vortrag, Blog, Empfehlung",
                         description="Mandari braucht Reichweite. Sag's deinem OK Lab, schreib einen Blog-Post, empfiehl uns deiner Bürgermeisterin.",
                         bullets=[bullet("Lightning-Talk im OK Lab / Civic-Tech-Meetup", "presentation"),
                                  bullet("Erfahrungsbericht im Blog", "newspaper"),
                                  bullet("Direkter Tipp an deine Kommune", "users")],
                         cta_label="Materialien anfragen", cta_url="/kontakt/?subject=Mandari-verbreiten", cta_icon="megaphone"),
                ],
            }),
            ("step_process", {
                "header": hdr(badge_text="So läuft's", badge_icon="route",
                              title="Drei Schritte vom „Hi\" zum gemergten PR", align="center",
                              subline="Kein bürokratisches CLA, keine 50-seitige Contributor-Doku."),
                "columns": "3", "background": "gray",
                "steps": [
                    step("01", "primary", "hand", "Hallo sagen",
                         "Im GitHub Discussion-Thread oder per E-Mail. Sag wer du bist und woran du Interesse hast.",
                         "Reaktionszeit ≤ 24h"),
                    step("02", "green", "list-checks", "Issue wählen",
                         "Such dir was aus den offenen Issues — oder erstell ein neues. Wir kommentieren mit Kontext.",
                         "Mentoring inklusive"),
                    step("03", "blue", "git-pull-request", "Beitrag einreichen",
                         "Pull Request, Übersetzung, Doku-Patch oder Markdown im Issue — alles passt. CI rennt, wir reviewen.",
                         "Erwähnung in Release-Notes"),
                ],
            }),
            ("gradient_cta", {
                "title": "Schreib einfach Hallo.",
                "subline": "Egal ob du eine Stunde oder einen Nachmittag hast, ob Profi oder blutige Anfänger:in — wir freuen uns auf deine Nachricht.",
                "ctas": [cta("Auf GitHub starten", "https://github.com/mandariOSS", "github", "primary"),
                         cta("hi@mandari.de", "mailto:hi@mandari.de", "mail", "outline"),
                         cta("Kontaktformular", "/kontakt/?subject=Hallo-aus-der-Community", "message-square", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /trust/ — Trust Center
        # ════════════════════════════════════════════════════════════
        "trust": [
            ("hero", {
                "badge_text": "Alles für die DSGVO-Prüfung an einem Ort", "badge_icon": "shield-check", "badge_color": "primary",
                "title": "Trust Center:", "title_highlight": "alle Antworten an einem Ort.",
                "subline": "Bevor du mit einem SaaS-Anbieter sprichst, willst du DPA, Subprocessor-Liste, Hosting-Stack und Backup-Strategie sehen. Hier sind sie, vorbereitet, unterschriftsreif.",
                "subline_secondary": "Diese Seite richtet sich an Datenschutzbeauftragte, IT-Leiter:innen und Verwaltungs-Compliance.",
                "ctas": [cta("Muster-AVV ansehen", "/avv/", "file-signature", "primary"),
                         cta("Subprocessoren", "#subprocessors", "list-tree", "secondary"),
                         cta("Konkrete Frage stellen", "/kontakt/?subject=Trust-Center-Frage", "message-square", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "primary", "items": [
                trust_item("map-pin", "Hosting", "100 % in Deutschland"),
                trust_item("lock", "TLS 1.3", "AES-256 at rest"),
                trust_item("database-backup", "Backup", "täglich, Aufbewahrung 30 Tage"),
                trust_item("file-signature", "DPA", "nach Art. 28 DSGVO"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Sechs Kernbereiche", badge_icon="layout-grid",
                              title="Was du wissen musst, strukturiert",
                              subline="Statt 40 Seiten Whitepaper hier sechs klar abgegrenzte Themen."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="primary", icon="file-signature", title="DPA / AVV",
                         description="Auftragsverarbeitungsvertrag nach Art. 28 DSGVO — wir schließen ihn mit jeder Organisation, Muster online einsehbar.",
                         cta_label="Zum Abschnitt", cta_url="#dpa", cta_icon="arrow-right"),
                    card(color="blue", icon="list-tree", title="Subprocessoren",
                         description="Wer sonst noch Daten sieht — vollständige Liste mit Standort, Zweck und Status.",
                         cta_label="Zum Abschnitt", cta_url="#subprocessors", cta_icon="arrow-right"),
                    card(color="green", icon="server", title="Hosting-Stack",
                         description="Wo die Server stehen, welche Zertifikate, welche Standards.",
                         cta_label="Zum Abschnitt", cta_url="#hosting", cta_icon="arrow-right"),
                    card(color="amber", icon="database-backup", title="Backup & Recovery",
                         description="RPO, RTO, Aufbewahrungsfristen — was im Ernstfall wirklich passiert.",
                         cta_label="Zum Abschnitt", cta_url="#backup", cta_icon="arrow-right"),
                    card(color="rose", icon="activity", title="Verfügbarkeit",
                         description="SLA-Versprechen für die Beta-Phase und für die produktive Nutzung.",
                         cta_label="Zum Abschnitt", cta_url="#availability", cta_icon="arrow-right"),
                    card(color="teal", icon="award", title="Audits & Zertifikate",
                         description="Was bereits geprüft wurde — und was wir bis Ende 2026 vorhaben.",
                         cta_label="Zum Abschnitt", cta_url="#audits", cta_icon="arrow-right"),
                ],
            }),
            # ── 01 · AVV ─────────────────────────────────────────────
            ("numbered_article", {
                "number": "1", "anchor": "dpa",
                "title": "Auftragsverarbeitung (AVV)",
                "body": (
                    "<p><strong>mandari work schließt mit jeder buchenden Organisation einen "
                    "Auftragsverarbeitungsvertrag (AVV) nach Art. 28 DSGVO ab.</strong> Der Vertrag regelt "
                    "Gegenstand und Dauer der Verarbeitung, Datenkategorien, Pflichten des Auftragsverarbeiters, "
                    "Unterauftragsverhältnisse, Löschung nach Vertragsende und eure Kontrollrechte. "
                    "Den vollständigen Mustertext könnt ihr vorab prüfen: "
                    "<a href=\"/avv/\">Muster-AVV online lesen</a>.</p>"
                    "<h3>Eingesetzte Subunternehmer</h3>"
                    "<ul>"
                    "<li><strong>Hetzner Online GmbH</strong> — Hosting, Rechenzentren in Deutschland</li>"
                    "<li><strong>Mollie B.V.</strong> — Zahlungsabwicklung, Niederlande (EU)</li>"
                    "<li><strong>Haufe-Lexware GmbH &amp; Co. KG</strong> — Buchhaltung (lexware office), Deutschland</li>"
                    "</ul>"
                    "<h3>Technische und organisatorische Maßnahmen (Kurzübersicht)</h3>"
                    "<ul>"
                    "<li>Verschlüsselung sensibler Inhalte mit AES-256-GCM, organisationsspezifische Schlüssel</li>"
                    "<li>Transportverschlüsselung (TLS) für alle Verbindungen</li>"
                    "<li>Tägliche Backups mit definierter Aufbewahrung</li>"
                    "<li>Zugriffskontrolle über rollenbasiertes Berechtigungssystem (RBAC)</li>"
                    "<li>Betrieb ausschließlich in deutschen Rechenzentren</li>"
                    "</ul>"
                ),
            }),
            ("disclaimer_box", {
                "icon": "file-signature", "color": "primary",
                "body": (
                    "<p><strong>AVV anfordern:</strong> Schreib uns eine kurze Mail an "
                    "<a href=\"mailto:hello@mandari.de?subject=AVV-Anfrage\">hello@mandari.de</a> "
                    "mit dem Namen eurer Organisation — ihr bekommt den unterschriftsreifen AVV "
                    "als Dokument zurück. Den Mustertext gibt es unter <a href=\"/avv/\">mandari.de/avv</a>.</p>"
                ),
            }),
            # ── 02 · Subprocessoren ──────────────────────────────────
            ("numbered_article", {
                "number": "2", "anchor": "subprocessors",
                "title": "Subprocessoren — wer sonst noch Daten sieht",
                "body": (
                    "<p>Vollständige Liste aller Unterauftragsverarbeiter. Es gibt keine weiteren — "
                    "insbesondere keine Tracker, keine Analytics-Dienste und keine Anbieter außerhalb der EU.</p>"
                    "<ul>"
                    "<li><strong>Hetzner Online GmbH</strong>, Industriestr. 25, 91710 Gunzenhausen (DE) — "
                    "Hosting aller Systeme in deutschen Rechenzentren. AVV nach Art. 28 DSGVO besteht.</li>"
                    "<li><strong>Mollie B.V.</strong>, Keizersgracht 126, 1015 CW Amsterdam (NL/EU) — "
                    "Zahlungsabwicklung für mandari work (Name, E-Mail, Zahlungs- und Mandatsdaten).</li>"
                    "<li><strong>Haufe-Lexware GmbH &amp; Co. KG</strong>, Munzinger Str. 9, 79111 Freiburg (DE) — "
                    "Rechnungsstellung und Buchhaltung (lexware office).</li>"
                    "</ul>"
                    "<p>Über geplante Änderungen an dieser Liste informieren wir vorab; ihr habt ein "
                    "Widerspruchsrecht gegen neue Subunternehmer (Details im <a href=\"/avv/\">AVV, Ziff. 7</a>).</p>"
                ),
            }),
            # ── 03 · Hosting ─────────────────────────────────────────
            ("numbered_article", {
                "number": "3", "anchor": "hosting",
                "title": "Hosting-Stack",
                "body": (
                    "<p>Alle Systeme laufen bei der Hetzner Online GmbH in deutschen Rechenzentren "
                    "(kein US-Cloud-Anbieter, kein CDN mit Drittland-Transfer).</p>"
                    "<ul>"
                    "<li>TLS-Verschlüsselung für alle Verbindungen (Caddy, automatische Zertifikate)</li>"
                    "<li>Verschlüsselung sensibler Arbeitsinhalte at rest: AES-256-GCM mit organisationsspezifischen Schlüsseln</li>"
                    "<li>PostgreSQL 16, Redis und Elasticsearch — alles self-hosted im selben Stack</li>"
                    "<li>Kompletter Stack Open Source (AGPL-3.0) und damit auditierbar</li>"
                    "</ul>"
                ),
            }),
            # ── 04 · Backup ──────────────────────────────────────────
            ("numbered_article", {
                "number": "4", "anchor": "backup",
                "title": "Backup & Recovery",
                "body": (
                    "<ul>"
                    "<li><strong>Tägliche Backups</strong> aller Datenbanken, Aufbewahrung 30 Tage</li>"
                    "<li>Backups liegen getrennt vom Produktivsystem, ebenfalls in Deutschland</li>"
                    "<li>Wiederherstellungen werden regelmäßig getestet</li>"
                    "<li>Nach Vertragsende: Datenexport auf Anfrage innerhalb von 30 Tagen, danach unwiderrufliche Löschung</li>"
                    "</ul>"
                ),
            }),
            # ── 05 · Verfügbarkeit ───────────────────────────────────
            ("numbered_article", {
                "number": "5", "anchor": "availability",
                "title": "Verfügbarkeit & Status",
                "body": (
                    "<p>Ehrliche Beta-Ansage: Wir befinden uns in der Pilot-Phase und schulden vertraglich "
                    "noch keine feste Verfügbarkeitsquote (siehe <a href=\"/agb/\">AGB Ziff. 6</a>). "
                    "Was wir stattdessen bieten:</p>"
                    "<ul>"
                    "<li>Öffentliche Live-Statusseite: <a href=\"https://status.mandari.de\">status.mandari.de</a> "
                    "(auch unter <a href=\"/status/\">/status/</a> eingebunden)</li>"
                    "<li>Wartungsfenster werden vorab angekündigt</li>"
                    "<li>Vorfälle werden transparent dokumentiert — siehe <a href=\"/transparenz/\">Transparenzbericht</a></li>"
                    "</ul>"
                ),
            }),
            # ── 06 · Audits ──────────────────────────────────────────
            ("numbered_article", {
                "number": "6", "anchor": "audits",
                "title": "Audits & Zertifikate",
                "body": (
                    "<p>Auch hier keine Marketing-Übertreibung: Eine ISO-27001- oder BSI-Grundschutz-"
                    "Zertifizierung ist für ein Solo-Projekt in der Beta-Phase nicht realistisch — "
                    "und wir behaupten keine.</p>"
                    "<ul>"
                    "<li>Der gesamte Code ist Open Source (AGPL-3.0) und öffentlich auditierbar</li>"
                    "<li>Responsible-Disclosure-Programm nach RFC 9116: <a href=\"/sicherheit/disclosure/\">/sicherheit/disclosure/</a></li>"
                    "<li>Abhängigkeiten werden automatisiert auf bekannte Schwachstellen geprüft</li>"
                    "<li>Externes Security-Audit ist für die General-Availability-Phase geplant</li>"
                    "</ul>"
                ),
            }),
            ("gradient_cta", {
                "title": "Frage übrig?",
                "subline": "Wenn deine Datenschutz- oder IT-Compliance hier keine Antwort findet, schreib uns. Du redest direkt mit der Person, die das Setup verantwortet.",
                "ctas": [cta("Frage stellen", "/kontakt/?subject=Trust-Center-Frage", "message-square", "primary"),
                         cta("Compliance-Call buchen", "/kontakt/#termin-buchen", "calendar", "outline"),
                         cta("Datenschutz lesen", "/datenschutz/", "file-text", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /abuse/ — Missbrauch melden
        # ════════════════════════════════════════════════════════════
        "abuse": [
            ("hero", {
                "badge_text": "Abuse-Meldestelle · DSA & NetzDG-konform", "badge_icon": "shield-alert", "badge_color": "rose",
                "title": "Missbrauch melden,", "title_highlight": "wir reagieren schnell",
                "subline": "Spam, illegaler Content, Datenschutz-Verletzungen, Urheberrechtsverstöße, Belästigung — wir antworten binnen 24 Stunden.",
                "subline_secondary": "Diese Seite richtet sich an Bürger:innen, Behörden und Rechteinhaber. Sicherheitslücken bitte über Responsible Disclosure.",
                "ctas": [cta("abuse@mandari.de", "mailto:abuse@mandari.de", "mail", "primary"),
                         cta("Kontaktformular", "/kontakt/?subject=Missbrauch-Meldung", "message-square", "secondary"),
                         cta("Notfall-Kontakte", "#notfall", "phone", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "rose", "items": [
                trust_item("zap", "Antwort", "binnen 24 h"),
                trust_item("shield-check", "Vertraulich", "behandelt"),
                trust_item("scale", "DSA & NetzDG", "konform"),
                trust_item("user-check", "Direkter Kontakt", "zum Founder"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Sechs Meldewege", badge_icon="list-checks",
                              title="Was möchtest du melden?",
                              subline="Such die passende Kategorie, jede zeigt klar wer zuständig ist.",
                              anchor_id="notfall"),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="amber", icon="mail-warning", title="Spam & unerwünschte Mails", subtitle="Du bekommst Mails von @mandari.de",
                         description="Du hast eine Mail von einer Mandari-Adresse bekommen, die du nicht erwartet hast.",
                         bullets=[bullet("Vollständige Mail mit Header"), bullet("Wann angekommen"), bullet("Absender-Adresse")],
                         cta_label="Spam melden", cta_url="mailto:abuse@mandari.de?subject=Spam-Meldung", cta_icon="mail"),
                    card(color="rose", icon="alert-octagon", title="Illegaler Content", subtitle="Strafbar, hetzerisch, jugendgefährdend",
                         description="Inhalte auf Mandari Insight oder Work, die gegen deutsches Strafrecht verstoßen.",
                         bullets=[bullet("URL des Inhalts"), bullet("Beschreibung des Verstoßes"), bullet("Screenshot (falls möglich)")],
                         cta_label="Content melden", cta_url="mailto:abuse@mandari.de?subject=Illegaler-Content", cta_icon="alert-octagon"),
                    card(color="primary", icon="lock", title="Datenschutz-Verletzung", subtitle="DSGVO-Auskunft, Löschung, Beschwerde",
                         description="Du findest deine Daten unrechtmäßig auf Mandari, oder möchtest dein Auskunfts-/Löschrecht wahrnehmen.",
                         bullets=[bullet("Welche Daten betroffen sind"), bullet("Wo sie erschienen sind"), bullet("Identitätsnachweis")],
                         cta_label="DSGVO-Anfrage", cta_url="mailto:privacy@mandari.de?subject=DSGVO-Anfrage", cta_icon="lock"),
                    card(color="blue", icon="copyright", title="Urheberrecht", subtitle="UrhG-Beschwerde · Bilder, Texte, Code",
                         description="Du bist Rechteinhaber:in und siehst deine Werke unautorisiert auf Mandari.",
                         bullets=[bullet("Identifikation des Werks"), bullet("URL der Verletzung"), bullet("Erklärung der Berechtigung")],
                         cta_label="Beschwerde einreichen", cta_url="mailto:abuse@mandari.de?subject=Urheberrecht", cta_icon="copyright"),
                    card(color="rose", icon="user-x", title="Belästigung & Drohungen", subtitle="Hasskommentare, Mobbing, Stalking",
                         description="Du wirst über Mandari belästigt oder bedroht. Wir sperren Account, dokumentieren für Polizei.",
                         bullets=[bullet("Polizei: 110 zuerst!", "phone"), bullet("Screenshot & URL sichern"), bullet("Dann uns kontaktieren")],
                         cta_label="Vorfall melden", cta_url="mailto:abuse@mandari.de?subject=Belästigung", cta_icon="user-x"),
                    card(color="teal", icon="gavel", title="Behörden-Anfragen", subtitle="Auskunftsersuchen, Beschlagnahmen",
                         description="Strafverfolgungsbehörden mit gerichtlichem Beschluss. Wir prüfen rechtlich, geben nur das Mindeste.",
                         bullets=[bullet("Gerichtlicher Beschluss"), bullet("Aktenzeichen & Behörde"), bullet("Konkrete Datenangabe")],
                         cta_label="legal@mandari.de", cta_url="mailto:legal@mandari.de?subject=Behoerden-Anfrage", cta_icon="gavel"),
                ],
            }),
            ("step_process", {
                "header": hdr(badge_text="So läuft's", badge_icon="route",
                              title="Was nach deiner Meldung passiert", align="center",
                              subline="Transparent, dokumentiert, mit klaren Reaktionszeiten — DSA-konform."),
                "columns": "4", "background": "gray",
                "steps": [
                    step("01", "primary", "mail-check", "Eingangsbestätigung",
                         "Du erhältst binnen 24 h eine Bestätigung mit Vorgangsnummer.", "≤ 24 h"),
                    step("02", "amber", "search", "Prüfung",
                         "Wir prüfen die Meldung sachlich und rechtlich. Bei Unklarheiten fragen wir nach.", "1–7 Tage"),
                    step("03", "green", "hammer", "Maßnahme",
                         "Bei berechtigter Meldung: Sperrung, Löschung, Korrektur oder Verweis an zuständige Stelle.", "je nach Fall"),
                    step("04", "blue", "message-circle-reply", "Rückmeldung",
                         "Du erfährst, was passiert ist. Bei Ablehnung: Begründung und Rechtsmittel-Hinweis (DSA Art. 17).", "≤ 14 Tage"),
                ],
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /barrierefreiheit/
        # ════════════════════════════════════════════════════════════
        "barrierefreiheit": [
            ("hero", {
                "badge_text": "Pflichterklärung nach § 12 BFSG", "badge_icon": "accessibility", "badge_color": "primary",
                "title": "Erklärung zur", "title_highlight": "Barrierefreiheit",
                "subline": "Mandari ist bemüht, seine Website und alle Anwendungen barrierefrei zugänglich zu machen, nach den Maßgaben des BGG und der BITV 2.0.",
                "subline_secondary": "Diese Erklärung gilt für die Website mandari.de sowie alle Subdomains. Stand: 26. April 2026.",
                "ctas": [], "background_color": "primary",
            }),
            ("trust_banner", {"color": "amber", "items": [
                trust_item("circle-dot", "Teilweise konform", "mit BITV 2.0"),
                trust_item("ruler", "Standards:", "WCAG 2.1 AA · EN 301 549"),
                trust_item("calendar-days", "Letzte Prüfung:", "April 2026"),
                trust_item("message-square", "Feedback", "jederzeit willkommen"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Stand der Konformität", badge_icon="gauge",
                              title="Was funktioniert, und wo wir noch arbeiten",
                              subline="Wir sind ehrlich: Mandari ist teilweise konform."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="green", icon="check-circle-2", title="Konform", subtitle="Was schon gut funktioniert",
                         bullets=[bullet("Tastatur-Navigation"), bullet("Skip-Link (WCAG 2.4.1)"),
                                  bullet("ARIA-Landmarks"), bullet("Kontrast ≥ 4,5:1"),
                                  bullet("Dark-Mode"), bullet("Touch-Ziele ≥ 44 × 44 px"),
                                  bullet("Responsive bis 320 px")]),
                    card(color="amber", icon="alert-circle", title="Teilweise konform", subtitle="Wo es noch hakt",
                         bullets=[bullet("Karten-Layer: Screenreader im Aufbau", "alert-triangle"),
                                  bullet("Komplexe Filter: Tastatur-Verbesserungen", "alert-triangle"),
                                  bullet("Lucide-Icons: bessere ARIA-Labels nötig", "alert-triangle"),
                                  bullet("PDF-Dokumente teilweise nicht maschinenlesbar", "alert-triangle"),
                                  bullet("Leichte Sprache & Gebärdensprache geplant Q3/2026", "alert-triangle")]),
                    card(color="rose", icon="x-circle", title="Ausnahmen", subtitle="Was wir nicht beeinflussen können",
                         bullets=[bullet("OParl-Quelldokumente der Kommunen", "x"),
                                  bullet("Eingebettete Inhalte Dritter (OSM-Tiles)", "x"),
                                  bullet("Archiv-Sitzungsprotokolle vor 2020 (gescannte PDFs)", "x")]),
                ],
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Was tun wenn etwas nicht funktioniert", badge_icon="message-circle-heart", badge_color="green",
                              title="Feedback & Durchsetzungsverfahren",
                              subline="Wenn dir Barrieren auffallen, melde dich. Wir antworten zeitnah und beheben so schnell wir können."),
                "left_card": card(color="green", icon="mail", title="An uns direkt", subtitle="Schnellster Weg",
                                  description="Schreib uns, was nicht funktioniert hat. Wir antworten binnen 3 Werktagen.",
                                  bullets=[bullet("barrierefreiheit@mandari.de", "at-sign"),
                                           bullet("Kontaktformular Betreff „Barrierefreiheit\"", "message-square"),
                                           bullet("Telefon & Gebärdensprache auf Anfrage", "phone")],
                                  cta_label="Barriere melden", cta_url="/kontakt/?subject=Barrierefreiheit", cta_icon="message-square"),
                "right_card": card(color="blue", icon="scale", title="Schlichtungsstelle des Bundes",
                                   subtitle="Wenn wir uns nicht einigen",
                                   description="Schlichtungsstelle nach § 16 BGG, kostenlos, formfrei. Mauerstraße 53, 10117 Berlin.",
                                   bullets=[bullet("Tel: 030 18 527-2805", "phone"),
                                            bullet("info@schlichtungsstelle-bgg.de", "mail")],
                                   cta_label="Zur Schlichtungsstelle", cta_url="https://www.schlichtungsstelle-bgg.de", cta_icon="external-link"),
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /open-source/ — kompakte Version
        # ════════════════════════════════════════════════════════════
        "open-source": [
            ("hero", {
                "badge_text": "100 % Open Source", "badge_icon": "unlock", "badge_color": "green",
                "title": "Freie Software für", "title_highlight": "freie Demokratie",
                "subline": "Mandari ist vollständig quelloffen — alle drei Module stehen unter der AGPL-3.0 Lizenz. Keine versteckten proprietären Teile, keine Anbieterabhängigkeit.",
                "ctas": [cta("GitHub Repository", "https://github.com/mandariOSS/mandari", "github", "primary"),
                         cta("Mitmachen", "/mitmachen/", "heart", "secondary")],
                "background_color": "green",
            }),
            ("trust_banner", {"color": "green", "items": [
                trust_item("scale", "AGPL-3.0", "Lizenz"),
                trust_item("server", "Eigenes Hosting", "erlaubt"),
                trust_item("git-fork", "Eigene Kopie", "erlaubt"),
                trust_item("users", "Community", "getrieben"),
            ]}),
            ("tech_partner_grid", {
                "header": hdr(badge_text="Auf wessen Schultern wir stehen", badge_icon="package-open", badge_color="gray",
                              title="Unsere Tech-Partnerschaften", align="center",
                              subline="Mandari wäre ohne diese Open-Source-Projekte nicht möglich. Sie verdienen Sichtbarkeit und Beiträge zurück.",
                              anchor_id="danke"),
                "partners": [
                    {"name": "Python", "icon": "code-2", "color": "amber", "description": "Programmiersprache · PSF", "url": "https://www.python.org"},
                    {"name": "Django", "icon": "layout-template", "color": "green", "description": "Web-Framework · BSD-3", "url": "https://www.djangoproject.com/"},
                    {"name": "Wagtail", "icon": "feather", "color": "blue", "description": "CMS · BSD-3", "url": "https://wagtail.org/"},
                    {"name": "PostgreSQL", "icon": "database", "color": "blue", "description": "Datenbank", "url": "https://www.postgresql.org/"},
                    {"name": "OParl", "icon": "plug", "color": "primary", "description": "Standard · CC-BY-SA", "url": "https://oparl.org/"},
                    {"name": "HTMX", "icon": "zap", "color": "primary", "description": "Frontend · BSD-2", "url": "https://htmx.org/"},
                    {"name": "Tailwind", "icon": "palette", "color": "blue", "description": "CSS · MIT", "url": "https://tailwindcss.com/"},
                    {"name": "Lucide", "icon": "sparkle", "color": "amber", "description": "Icons · ISC", "url": "https://lucide.dev/"},
                    {"name": "Altcha", "icon": "shield-check", "color": "green", "description": "Spam-Schutz · MIT", "url": "https://altcha.org/"},
                    {"name": "Docker", "icon": "container", "color": "blue", "description": "Container · Apache-2.0", "url": "https://www.docker.com/"},
                ],
            }),
            ("gradient_cta", {
                "title": "Machen Sie mit!",
                "subline": "Ob als Entwickler:in, Kommune oder Bürger:in — Mandari lebt von der Community.",
                "ctas": [cta("GitHub Repository", "https://github.com/mandariOSS/mandari", "github", "primary"),
                         cta("Mitmachen", "/mitmachen/", "heart", "outline")],
                "gradient_from": "green",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /migration/ — kompakte Version
        # ════════════════════════════════════════════════════════════
        "migration": [
            ("hero", {
                "badge_text": "Migration · Pilot-Phase 2026", "badge_icon": "move-right", "badge_color": "primary",
                "title": "Wechsel von ALLRIS, regisafe oder Somacos?", "title_highlight": "Wir machen's planbar.",
                "subline": "Eine RIS-Ablösung ist kein Sprint, aber auch kein Drama. Vier klare Schritte, ehrliche Aufwandsschätzung und Pilot-Konditionen.",
                "subline_secondary": "Diese Seite richtet sich an IT-Leiter:innen, Hauptamtsleiter:innen und Fraktionsgeschäftsführer:innen.",
                "ctas": [cta("Migrations-Gespräch", "/kontakt/?subject=Migration-Beratung", "calendar-check", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "secondary"),
                         cta("Was kommt mit?", "#scope", "list-checks", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "green", "items": [
                trust_item("file-json", "OParl-Standard", "als Brücke"),
                trust_item("layers", "Parallelbetrieb", "möglich"),
                trust_item("shield-check", "Rollback", "jederzeit möglich"),
                trust_item("hand-heart", "Pilot-Konditionen", "verhandelbar"),
            ]}),
            ("step_process", {
                "header": hdr(badge_text="Vier Schritte", badge_icon="route",
                              title="So läuft eine Migration zu Mandari",
                              subline="Realistische Zeiten, klare Verantwortlichkeiten, keine Big-Bang-Risiken."),
                "columns": "4", "background": "white",
                "steps": [
                    step("01", "primary", "search", "Bestandsaufnahme",
                         "Wir schauen uns dein Alt-RIS an: OParl-Verfügbarkeit, Datenmenge, Sonderfelder.", "1–2 Wochen"),
                    step("02", "green", "git-merge", "Mapping & Test",
                         "Wir bauen den Mapping-Layer und importieren in eine Test-Instanz.", "2–4 Wochen"),
                    step("03", "amber", "users", "Schulung & Parallelbetrieb",
                         "Verwaltungsmitarbeitende werden geschult, beide Systeme laufen 4–8 Wochen parallel.", "4–8 Wochen"),
                    step("04", "blue", "rocket", "Cutover",
                         "Definierter Termin für den Wechsel. Alt-RIS wird in Read-Only überführt.", "1 Tag"),
                ],
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Migrations-Scope", badge_icon="list-checks",
                              title="Was kommt mit — und was prüfen wir individuell?", align="center",
                              subline="Ehrliche Antwort statt „alles, kein Problem\": Der OParl-Standard trägt das meiste, der Rest ist Handarbeit.",
                              anchor_id="scope"),
                "left_card": card(color="green", icon="check-circle", title="Das kommt mit", subtitle="Über den OParl-Standard",
                                  description="Alles, was euer Alt-RIS über OParl bereitstellt, übernehmen wir strukturiert und verlustfrei:",
                                  bullets=[bullet("Sitzungen, Tagesordnungen & TOPs", "calendar-clock"),
                                           bullet("Vorlagen, Drucksachen & Beratungsfolgen", "file-text"),
                                           bullet("Gremien, Personen & Mitgliedschaften", "users"),
                                           bullet("Dokumente / PDFs inkl. Volltext-Indexierung", "file-search"),
                                           bullet("Wahlperioden & Orte", "map-pin")]),
                "right_card": card(color="amber", icon="search", title="Das prüfen wir individuell", subtitle="Bestandsaufnahme in Schritt 01",
                                   description="Nicht alles liegt standardisiert vor — diese Punkte klären wir gemeinsam vor dem Cutover:",
                                   bullets=[bullet("Anbieterspezifische Sonderfelder & Vermerke", "puzzle"),
                                            bullet("Historische Daten ohne OParl-Export", "archive"),
                                            bullet("Interne, nicht-öffentliche Vorlagen & Protokolle", "lock"),
                                            bullet("Sitzungsgeld-Konfiguration & Abrechnungshistorie", "banknote")]),
            }),
            ("disclaimer_box", {
                "icon": "hand-heart", "color": "amber",
                "body": "<p><strong>Pilot-Kommunen bekommen Sonderkonditionen.</strong> Für die ersten 5 Migrations-Pilot-Kommunen bauen wir individuelle Konditionen — reduzierte Migrationskosten, längere Parallelbetrieb-Phasen, gemeinsame PR-Geschichten. Im Gegenzug: echtes Feedback und Bereitschaft zur Referenz. <a href=\"/kontakt/?subject=Migration-Pilot-Kondition\">Pilot-Konditionen anfragen →</a></p>",
            }),
            ("gradient_cta", {
                "title": "Bereit für ein Erstgespräch?",
                "subline": "30 Minuten reichen, um zu klären: Welches Alt-RIS, welche Datenmenge, welche Pilot-Konditionen passen zu eurer Situation. Unverbindlich.",
                "ctas": [cta("Migrations-Gespräch", "/kontakt/?subject=Migration-Beratung", "message-square", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "outline"),
                         cta("Preise sehen", "/preise/", "credit-card", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /kommunen/ — kompakt
        # ════════════════════════════════════════════════════════════
        "kommunen": [
            ("hero", {
                "badge_text": "Kommunen-Status · Beta-Phase 2026", "badge_icon": "map-pin", "badge_color": "primary",
                "title": "Welche Kommunen sind", "title_highlight": "schon dabei?",
                "subline": "Mandari ist in der Pilot-Phase. Hier siehst du ehrlich: welche Kommunen live sind, welche in Anbindung, und welche geplant.",
                "subline_secondary": "Du willst deine Kommune dabei haben? Wir freuen uns über jede Anfrage.",
                "ctas": [cta("Kommune anfragen", "/kontakt/?subject=Kommune-anbinden", "mail", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "secondary")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "amber", "items": [
                trust_item("circle-check", "0", "Live"),
                trust_item("loader", "2", "in Anbindung"),
                trust_item("circle-dashed", "viele", "geplant / interessiert"),
                trust_item("file-json", "OParl-konform", "vorausgesetzt"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Status pro Kommune", badge_icon="layers",
                              title="Status-Übersicht",
                              subline="Drei Status-Stufen: Live (produktiv), in Anbindung (technisches Setup läuft), geplant (Gespräche laufen)."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="green", icon="circle-check", title="Live", subtitle="Produktiv im Insight-Portal",
                         description="Aktuell noch keine Kommune produktiv live — wir sind in der Pilot-Phase 2026.",
                         bullets=[bullet("Daten täglich synchronisiert"),
                                  bullet("Volltext-Suche aktiv"),
                                  bullet("Karten-Layer (geplant)")],
                         cta_label="Pilot-Kommune werden", cta_url="/kontakt/?subject=Pilot-Kommune", cta_icon="rocket"),
                    card(color="amber", icon="loader", title="In Anbindung", subtitle="Technisches Setup läuft",
                         description="2 Kommunen, deren OParl-Schnittstelle wir gerade einbinden.",
                         bullets=[bullet("OParl-Quellen-Verifikation"),
                                  bullet("Anpassung an lokale Eigenheiten"),
                                  bullet("Test-Phase mit Verwaltung")],
                         cta_label="Mehr erfahren", cta_url="/kontakt/?subject=Anbindung-Status", cta_icon="message-square"),
                    card(color="blue", icon="circle-dashed", title="Geplant / Interessiert", subtitle="Gespräche laufen",
                         description="Mehrere Kommunen haben Interesse signalisiert. Genaue Reihenfolge nach OParl-Verfügbarkeit + Pilot-Bereitschaft.",
                         bullets=[bullet("Erstgespräche geführt"),
                                  bullet("Anbindungsfähigkeit geprüft"),
                                  bullet("Reihenfolge wird abgestimmt")],
                         cta_label="Eure Kommune anmelden", cta_url="/kontakt/?subject=Kommune-Interesse", cta_icon="mail"),
                ],
            }),
            ("two_column_use_case", {
                "header": hdr(badge_text="Wie kommt eure Kommune dazu?", badge_icon="git-branch",
                              title="Zwei Wege zur Anbindung", align="center",
                              subline="Hängt davon ab, ob eure Kommune schon eine OParl-Schnittstelle hat."),
                "left_card": card(color="green", icon="check-circle", title="Mit OParl-Schnittstelle", subtitle="Schneller Weg",
                                  description="Wenn euer RIS (ALLRIS, regisafe, Somacos, SD.NET RIM …) bereits OParl spricht, sind wir in Tagen statt Monaten startklar.",
                                  bullets=[bullet("OParl-Endpoint übermitteln"),
                                           bullet("Test-Sync, dann Production-Sync"),
                                           bullet("Anbindung typisch 1-2 Wochen")],
                                  cta_label="Anbindung starten", cta_url="/kontakt/?subject=OParl-Anbindung", cta_icon="rocket"),
                "right_card": card(color="amber", icon="puzzle", title="Ohne OParl-Schnittstelle", subtitle="Längerer Weg",
                                   description="Wenn euer RIS noch kein OParl spricht, sprechen wir mit dem Anbieter — oder bauen mit eurer Verwaltung einen Custom-Adapter.",
                                   bullets=[bullet("Vorbedingungen klären"),
                                            bullet("Anbieter-Gespräche koordinieren"),
                                            bullet("Custom-Adapter ggf. mit Förderung")],
                                   cta_label="Beratung anfragen", cta_url="/kontakt/?subject=Custom-Adapter", cta_icon="mail"),
            }),
            ("gradient_cta", {
                "title": "Eure Kommune dabei haben?",
                "subline": "Schreib uns, wir prüfen die Anbindbarkeit kostenlos und unverbindlich.",
                "ctas": [cta("Kommune anmelden", "/kontakt/?subject=Kommune-anbinden", "mail", "primary"),
                         cta("30-Min-Call buchen", "/kontakt/#termin-buchen", "calendar", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /ueber-uns/
        # ════════════════════════════════════════════════════════════
        "ueber-uns": [
            ("hero", {
                "badge_text": "Mission · Founder · Werte", "badge_icon": "compass", "badge_color": "primary",
                "title": "Mandari macht", "title_highlight": "Kommunalpolitik zugänglich.",
                "subline": "Hinter Mandari steht eine Person mit einer klaren Mission: Ratsinformationssysteme aus den frühen 2000ern in die Gegenwart zu holen.",
                "subline_secondary": "Kein Startup mit Investorenrunde. Kein Konzern. Ein Projekt aus Überzeugung mit offener Community drum herum.",
                "ctas": [cta("Founder kennenlernen", "#founder", "user-circle", "primary"),
                         cta("Werte ansehen", "#werte", "heart", "secondary"),
                         cta("Direkt schreiben", "/kontakt/", "mail", "outline")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "primary", "items": [
                trust_item("user", "Solo-Founder", "transparent"),
                trust_item("map-pin", "Aus", "Münster"),
                trust_item("github", "AGPL-3.0", "Open Source"),
                trust_item("flask-conical", "Beta-Phase", "2026"),
            ]}),
            ("two_column_use_case", {
                "header": hdr(badge_text="Founder", badge_icon="user-circle",
                              title="Hinter Mandari steht eine Person",
                              subline="Mandari ist kein Konzern und kein Startup mit Investorenrunde, sondern ein Projekt aus Überzeugung.",
                              anchor_id="founder"),
                "left_card": card(color="primary", icon="user-circle", title="Sven Konopka", subtitle="Gründer · Entwickler · Inhaber",
                                  description="Full-Stack-Entwickler und Inhaber von topixmedia.de aus Münster. Mandari ist sein persönliches Herzensprojekt.",
                                  bullets=[bullet("Beruf: Selbstständiger Full-Stack-Entwickler", "briefcase"),
                                           bullet("Mission: RIS modernisieren, Bürger:innen einbinden", "lightbulb"),
                                           bullet("Stack: Django, PostgreSQL, HTMX, Wagtail", "layers")],
                                  cta_label="GitHub-Profil", cta_url="https://github.com/mandariOSS", cta_icon="github"),
                "right_card": card(color="primary", icon="quote", title="Was Solo-Founder bedeutet", subtitle="Direkter Draht",
                                   description="Konzept, Code, Design, Hosting, Support — aktuell alles in einer Hand. Zwei Konsequenzen, die ich offen kommuniziere.",
                                   bullets=[bullet("Direkter Draht: kein Ticket-System, kein Vertriebs-Bot", "user-check"),
                                            bullet("Überschaubares Tempo: kein Versprechen, das ich nicht halten kann", "clock"),
                                            bullet("Realistische Roadmap statt Marketing-Ankündigungen", "map")]),
            }),
            ("mandari_cards", {
                "header": hdr(badge_text="Werte", badge_icon="compass",
                              title="Drei Werte, die jede Entscheidung prägen", align="center",
                              subline="Wo es Zielkonflikte gibt, entscheidet immer einer dieser drei Werte.",
                              anchor_id="werte"),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="green", icon="eye", title="Transparenz", subtitle="Offen statt verborgen",
                         description="Offene Prozesse — in der Politik wie in der Software. Code ist offen, Entscheidungen sind nachvollziehbar, Roadmap ist öffentlich.",
                         bullets=[bullet("Code unter AGPL-3.0 auf GitHub"),
                                  bullet("Öffentliche Roadmap & Releases"),
                                  bullet("Quellennachweise für jede Datenquelle")]),
                    card(color="primary", icon="lock", title="Datensouveränität", subtitle="Du behältst die Kontrolle",
                         description="Hosting in Deutschland, AES-256-Verschlüsselung, kein Tracking. Jede Kommune kann selbst hosten.",
                         bullets=[bullet("Deutsche Server, DSGVO-konform"),
                                  bullet("Self-Hosting jederzeit möglich"),
                                  bullet("Datenexport in offenen Formaten")]),
                    card(color="blue", icon="accessibility", title="Zugänglichkeit", subtitle="Für alle, nicht nur Profis",
                         description="Politische Information muss für alle zugänglich sein — unabhängig von Budget, technischem Wissen oder Endgerät.",
                         bullets=[bullet("Insight-Portal kostenlos & ohne Login"),
                                  bullet("Mobil-first, responsive Design"),
                                  bullet("BFSG-konform — siehe Barrierefreiheit")]),
                ],
            }),
            ("gradient_cta", {
                "title": "Lust mitzumachen?",
                "subline": "Mandari lebt von Menschen, die unsere Werte teilen. Ob als Entwickler:in, Kommune, Förderer oder einfach mit einer Idee — jeder Beitrag zählt.",
                "ctas": [cta("Mitmachen", "/mitmachen/", "heart", "primary"),
                         cta("Partner werden", "/partner/", "handshake", "outline"),
                         cta("Kontakt", "/kontakt/", "mail", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /presse/ — kompakte Version
        # ════════════════════════════════════════════════════════════
        "presse": [
            ("hero", {
                "badge_text": "Für Journalist:innen", "badge_icon": "megaphone", "badge_color": "primary",
                "title": "Presse-", "title_highlight": "Material",
                "subline": "Pressemitteilungen, Hintergrund-Material, Logos und direkter Founder-Kontakt für eure Berichterstattung über Civic-Tech und Mandari.",
                "subline_secondary": "Reaktionszeit: 24 h für Anfragen mit Deadline.",
                "ctas": [cta("Presse-Anfrage", "mailto:presse@mandari.de", "mail", "primary"),
                         cta("Founder-Interview", "/kontakt/?subject=Presse-Interview", "user-circle", "secondary")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "primary", "items": [
                trust_item("clock", "Reaktion", "binnen 24 h"),
                trust_item("user", "Direkter Draht", "zum Founder"),
                trust_item("download", "Logos & Bilder", "frei verwendbar (CC-BY)"),
                trust_item("file-text", "Hintergrund", "auf Anfrage"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Was wir bereitstellen", badge_icon="package",
                              title="Material für eure Berichterstattung", align="center"),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="primary", icon="image", title="Logos & Brand-Assets",
                         description="Wordmark, Icon, Farben — alles unter CC-BY frei verwendbar.",
                         cta_label="Downloads ansehen", cta_url="#logo-wortmarke", cta_icon="download"),
                    card(color="green", icon="user-circle", title="Founder-Interview",
                         description="Sven Konopka steht für Hintergrund-Gespräche zur Verfügung — Civic-Tech, Open Source, Demokratie & Software.",
                         cta_label="Termin anfragen", cta_url="/kontakt/?subject=Presse-Interview", cta_icon="calendar"),
                    card(color="blue", icon="newspaper", title="Pressemitteilungen",
                         description="Aktuelle Releases, Pilot-Kommunen-Updates, Förder-Meilensteine — alle Mitteilungen im Blog mit RSS-Feed.",
                         cta_label="Blog ansehen", cta_url="/blog/", cta_icon="external-link"),
                ],
            }),
            ("richtext_section", {
                "header": hdr(badge_text="Brand", badge_icon="image", badge_color="primary",
                              title="Logo & Wortmarke",
                              subline="Die mandari-Wortmarke zum Download — SVG für Web und Druck, PNG für Präsentationen. Alle Dateien CC-BY.",
                              anchor_id="logo-wortmarke"),
                "background": "gray",
                "body": (
                    "<h3>Downloads</h3>"
                    "<ul>"
                    '<li><a href="/static/brand/mandari-logo.svg">Wortmarke als SVG — dunkel, für helle Hintergründe</a></li>'
                    '<li><a href="/static/brand/mandari-logo-white.svg">Wortmarke als SVG — weiß, für dunkle Hintergründe</a></li>'
                    '<li><a href="/static/brand/mandari-logo.png">Wortmarke als PNG — dunkel, 2400 px, transparent</a></li>'
                    '<li><a href="/static/brand/mandari-logo-white.png">Wortmarke als PNG — weiß, 2400 px, transparent</a></li>'
                    '<li><a href="/static/brand/favicon.svg">Bildmarke „m.“ als SVG — Favicon/Avatar</a></li>'
                    "</ul>"
                    "<h3>Nutzungshinweise</h3>"
                    "<ul>"
                    "<li><strong>Schutzraum:</strong> Rund um die Wortmarke mindestens die Breite des Punkts freihalten.</li>"
                    "<li><strong>Keine Verzerrung:</strong> Nicht strecken, stauchen, drehen oder mit Effekten (Schatten, Kontur, Verlauf) versehen.</li>"
                    "<li><strong>Keine Umfärbung:</strong> Der Punkt steht immer in Indigo (#4F46E5, auf dunklem Grund #818CF8); der Schriftzug in Grau-900 (#111827) bzw. Weiß.</li>"
                    "<li><strong>Varianten:</strong> Dunkle Variante auf hellen, weiße Variante auf dunklen Hintergründen verwenden.</li>"
                    "</ul>"
                ),
            }),
            ("gradient_cta", {
                "title": "Frage übrig?",
                "subline": "Schreib direkt an presse@mandari.de — oder buch einen Founder-Slot für ein Hintergrund-Gespräch.",
                "ctas": [cta("presse@mandari.de", "mailto:presse@mandari.de", "mail", "primary"),
                         cta("Interview-Termin", "/kontakt/#termin-buchen", "calendar", "outline")],
                "gradient_from": "primary",
            }),
        ],

        # ════════════════════════════════════════════════════════════
        # /roadmap/ — kompakt
        # ════════════════════════════════════════════════════════════
        "roadmap": [
            ("hero", {
                "badge_text": "Was als Nächstes kommt", "badge_icon": "map", "badge_color": "primary",
                "title": "Mandari", "title_highlight": "Roadmap",
                "subline": "Was wir gerade bauen, was als Nächstes kommt, und wo ihr Einfluss nehmen könnt. Ehrlich aktualisiert nach jedem Quartal.",
                "subline_secondary": "Stand: Q1/2026 · Beta-Phase",
                "ctas": [cta("Issue vorschlagen", "https://github.com/mandariOSS/mandari/issues/new?template=feature_request.md", "github", "primary"),
                         cta("Releases ansehen", "/releases/", "tag", "secondary")],
                "background_color": "primary",
            }),
            ("trust_banner", {"color": "primary", "items": [
                trust_item("loader", "Q1/2026", "in Arbeit"),
                trust_item("calendar", "Q2/2026", "geplant"),
                trust_item("calendar-check", "Q3/2026", "Session-Pilot"),
                trust_item("rocket", "2027", "Allgemeine Verfügbarkeit"),
            ]}),
            ("mandari_cards", {
                "header": hdr(badge_text="Aktuell auf dem Tisch", badge_icon="hammer",
                              title="Was wir gerade bauen",
                              subline="Konkrete Themen aus den nächsten Wochen."),
                "columns": "3", "background": "white",
                "cards": [
                    card(color="primary", icon="plug", title="OParl-Adapter erweitern", subtitle="Backend",
                         description="Politik-Digital, Sternberg, More! — jeder Anbieter hat Eigenheiten, die wir kapseln wollen.",
                         badge="in Arbeit"),
                    card(color="amber", icon="languages", title="i18n-Grundgerüst Englisch", subtitle="Setup",
                         description="Django-i18n aufsetzen, Strings extrahieren, Übersetzer-Workflow entscheiden.",
                         badge="Q1/2026"),
                    card(color="rose", icon="smartphone", title="Mobile Layout Insight-Karten", subtitle="Frontend · Design",
                         description="Map-Layer und Filter brauchen mobil mehr Platz — Bottom-Sheet statt Sidebar.",
                         badge="Q1/2026"),
                    card(color="blue", icon="book-open", title="Self-Hosting-Guide Hetzner", subtitle="Docs",
                         description="Schritt-für-Schritt: Server bestellen, Docker-Compose deployen, TLS via Caddy.",
                         badge="Q2/2026"),
                    card(color="teal", icon="search", title="Synonym-Dictionary", subtitle="Search · Backend",
                         description="„Bauleitplanung\" ↔ „B-Plan\", „Aufstellungsbeschluss\" — Meilisearch lernt Verwaltungssprache.",
                         badge="Q2/2026"),
                    card(color="green", icon="accessibility", title="WCAG-AA-Audit", subtitle="A11y · Frontend",
                         description="Screenreader-Test, Tastaturnavigation, Kontrast-Check — wir wollen BITV 2.0 sauber erfüllen.",
                         badge="Q3/2026"),
                ],
            }),
            ("gradient_cta", {
                "title": "Hast du eine Idee?",
                "subline": "Erstell ein Issue, kommentiere bestehende Vorschläge oder schick uns einfach eine Mail — wir lesen mit.",
                "ctas": [cta("Issue erstellen", "https://github.com/mandariOSS/mandari/issues/new", "github", "primary"),
                         cta("Direkt schreiben", "/kontakt/?subject=Roadmap-Idee", "mail", "outline")],
                "gradient_from": "primary",
            }),
        ],
    }


def get_legal_definitions() -> dict:
    """Legal-Pages (LegalPage Model) → body_stream StreamField."""

    return {
        # Note: impressum / datenschutz / agb werden hier bewusst NICHT mehr
        # definiert. Die authoritative Fassung dieser Rechtstexte liegt in
        # .legal-content/*.html und wird von `setup_initial_pages` in das
        # RichText-Feld LegalPage.body geseedet (gerendert via
        # marketing/legal_page.html). Ein body_stream-Seed wuerde das
        # Template auf legal_streamfield_page.html umschalten und die
        # authoritative Fassung verdecken.

        # ════════════════════════════════════════════════════════════
        # /quellen/ — Quellennachweise
        # ════════════════════════════════════════════════════════════
        "quellen": [
            ("hero", {
                "badge_text": "Transparenz über Transparenz", "badge_icon": "list-tree", "badge_color": "primary",
                "title": "Quellen-", "title_highlight": "nachweise",
                "subline": "Mandari aggregiert öffentliche Daten aus Ratsinformationssystemen deutscher Kommunen. Hier eine vollständige Übersicht aller Quellen, Lizenzen und eingesetzten Standards.",
                "ctas": [], "background_color": "primary",
            }),
            ("richtext_section", {
                "header": hdr(title="Ratsinformationen aus OParl-Schnittstellen"),
                "background": "white",
                "body": "<p>Mandari nutzt den offenen Standard <a href=\"https://oparl.org/\" target=\"_blank\" rel=\"noopener\">OParl</a> (Versionen 1.0 und 1.1), um Daten aus den Ratsinformationssystemen deutscher Kommunen strukturiert abzurufen. Es werden ausschließlich öffentlich zugängliche Daten verarbeitet.</p><p>Die jeweilige Kommune bleibt rechtlich verantwortliche Stelle für die bereitgestellten Inhalte. Mandari nimmt keine inhaltlichen Veränderungen vor und verlinkt grundsätzlich auf die Originalquelle.</p><p><a href=\"/kommunen/\">→ Liste aller aktuell aggregierten Kommunen</a></p>",
            }),
            ("richtext_section", {
                "header": hdr(title="Lizenz der Ratsinformationen"),
                "background": "gray",
                "body": "<p>Die meisten Kommunen stellen ihre OParl-Daten unter einer der folgenden Lizenzen bereit:</p><ul><li><strong>Datenlizenz Deutschland – Zero – Version 2.0</strong> (<a href=\"https://www.govdata.de/dl-de/zero-2-0\" target=\"_blank\" rel=\"noopener\">DL-DE-Zero-2.0</a>)</li><li><strong>CC0 1.0 Universell</strong> (Public Domain)</li><li><strong>CC-BY 4.0</strong></li></ul><p>Falls eine Kommune ihre Daten unter einer einschränkenden Lizenz bereitstellt, indizieren wir nur Metadaten, keinen Volltext.</p>",
            }),
            ("richtext_section", {
                "header": hdr(title="Karten & Geokodierung"),
                "background": "white",
                "body": "<ul><li><strong>OpenStreetMap</strong> (ODbL) — Karten-Tiles und Geometrien (<a href=\"https://www.openstreetmap.org/copyright\" target=\"_blank\" rel=\"noopener\">openstreetmap.org/copyright</a>)</li><li><strong>Nominatim</strong> (BSD-2) — Geocoding-Service basierend auf OSM-Daten</li></ul>",
            }),
            ("richtext_section", {
                "header": hdr(title="KI-Komponenten"),
                "background": "gray",
                "body": "<p>KI-Inferenz primär self-hosted auf eigenen Hetzner-GPUs. Modelle:</p><ul><li><strong>Open-Weight LLMs</strong> für Zusammenfassungen (z.&nbsp;B. Mistral, Llama)</li><li><strong>BAAI/bge-m3</strong> für semantische Suche (Vektor-Embeddings)</li><li>Optional: EU-basierte Anbieter (z.&nbsp;B. <strong>Mistral La Plateforme</strong>) für komplexere Anfragen, nur nach Opt-in pro Kommune</li></ul>",
            }),
            ("richtext_section", {
                "header": hdr(title="Software-Lizenzen"),
                "background": "white",
                "body": "<p>Vollständige Liste aller Tech-Partner und Open-Source-Abhängigkeiten siehe <a href=\"/open-source/#danke\">Open Source · Schultern, auf denen wir stehen</a>.</p><p>Software Bill of Materials (SBOM) im GitHub-Repo: <a href=\"https://github.com/mandariOSS/mandari/blob/dev/docs/SBOM.md\" target=\"_blank\" rel=\"noopener\">docs/SBOM.md</a>.</p>",
            }),
            ("disclaimer_box", {
                "icon": "info", "color": "gray",
                "body": "<p>Stand: <strong>26. April 2026</strong>. Bei Fehlern oder fehlenden Nachweisen: <a href=\"mailto:hi@mandari.de\">hi@mandari.de</a>.</p>",
            }),
        ],
    }


# ════════════════════════════════════════════════════════════════════════
#  COMMAND-KLASSE
# ════════════════════════════════════════════════════════════════════════


class Command(BaseCommand):
    help = "Migriert alle Marketing- und Legal-Pages auf das StreamField-System."

    def add_arguments(self, parser):
        parser.add_argument("--pages", nargs="+", type=str, default=None,
                            help="Optionale Liste von Slugs (Default: alle definierten Pages)")
        parser.add_argument("--force", action="store_true",
                            help="Überschreibt bestehende body-Inhalte")
        parser.add_argument("--marketing-only", action="store_true", help="Nur Marketing-Pages migrieren")
        parser.add_argument("--legal-only", action="store_true", help="Nur Legal-Pages migrieren")

    def handle(self, *args, **options):
        from marketing.models import LegalPage, MarketingPage
        from marketing.blocks import MarketingStreamBlock

        marketing_defs = get_marketing_definitions()
        legal_defs = get_legal_definitions()

        slugs_filter = options["pages"]
        force = options["force"]
        marketing_only = options["marketing_only"]
        legal_only = options["legal_only"]

        stream_block = MarketingStreamBlock()

        def migrate(slug, blocks_data, page_class, body_field):
            page = page_class.objects.filter(slug=slug).first()
            if not page:
                self.stdout.write(self.style.ERROR(f"  ✗ {slug}/ - Page nicht in DB"))
                return False

            existing_body = getattr(page, body_field)
            if existing_body and len(list(existing_body)) > 0 and not force:
                self.stdout.write(self.style.WARNING(
                    f"  ◯ {slug}/ - body bereits gefüllt ({len(list(existing_body))} Blöcke), --force"
                ))
                return False

            new_value = StreamValue(stream_block, blocks_data, is_lazy=False)
            setattr(page, body_field, new_value)
            old_template = page.custom_template
            page.custom_template = ""
            page.save()
            page.save_revision().publish()

            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {slug}/ - {len(blocks_data)} Blöcke (custom_template '{old_template}' → leer)"
            ))
            return True

        # Marketing-Pages
        if not legal_only:
            self.stdout.write(self.style.MIGRATE_HEADING("\n=== Marketing-Pages ==="))
            for slug, blocks in marketing_defs.items():
                if slugs_filter and slug not in slugs_filter:
                    continue
                migrate(slug, blocks, MarketingPage, "body")

        # Legal-Pages
        if not marketing_only:
            self.stdout.write(self.style.MIGRATE_HEADING("\n=== Legal-Pages ==="))
            for slug, blocks in legal_defs.items():
                if slugs_filter and slug not in slugs_filter:
                    continue
                migrate(slug, blocks, LegalPage, "body_stream")

        self.stdout.write("\n" + self.style.SUCCESS("Migration komplett."))
