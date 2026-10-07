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


def cell(status="yes", note=""):
    """Zelle der Feature-Matrix: yes | partial | planned | no | info."""
    return {"status": status, "note": note}


def frow(label, *cells, description=""):
    return {"label": label, "description": description, "cells": list(cells)}


def fgroup(title, *rows):
    return {"title": title, "rows": list(rows)}


def srow(title, *, text, label="", status="", link_label="", link_url="", anchor_id=""):
    """Zeile im Block split_rows: Titel links (Etikett, Status), Text und ein Textlink rechts."""
    return {
        "title": title, "label": label, "status": status, "text": text,
        "link_label": link_label, "link_url": link_url, "anchor_id": anchor_id,
    }


# ════════════════════════════════════════════════════════════════════════
#  VERGLEICHSSEITEN — mandari vs. etablierte RIS-Anbieter
#
#  Daten, Quellen und Aufbau stehen in marketing/seeds_vergleich.py (Funktionsanalyse
#  vom 2. Oktober 2026, § 6 UWG: objektiv, nachprüfbar, jede Angabe mit Quelle).
# ════════════════════════════════════════════════════════════════════════


# ════════════════════════════════════════════════════════════════════════
#  PAGE-DEFINITIONEN — pro Slug eine Liste von (block_type, value)-Tupeln
# ════════════════════════════════════════════════════════════════════════


def get_marketing_definitions() -> dict:
    """Marketing-Pages (MarketingPage Model) → body StreamField."""
    from marketing import seeds_vergleich  # Vergleichsseiten und Lücken auf /roadmap/
    from marketing import seeds_muster as m  # Abschnittsmuster (Musterkatalog)
    from marketing import seeds_ris  # Sachseite /ratsinformationssystem/
    from marketing.seeds_unternehmen import get_company_page_definitions

    return {
        # ════════════════════════════════════════════════════════════
        # /transparenz/ — Quartals-Bericht
        # ════════════════════════════════════════════════════════════
        "transparenz": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "Transparenzbericht", "title_highlight": "2026",
                "subline": "Was andere SaaS gerne verstecken, legen wir offen: Behördenanfragen, Sicherheitsvorfälle, Finanzlage, Hosting-Realität, Open-Source-Beiträge.",
                "subline_secondary": "Berichtszeitraum: 1. Januar bis 31. Dezember 2026 · Veröffentlicht: 26. April 2026 · Aktualisiert: 20. Juli 2026 · Nächste Aktualisierung: Oktober 2026",
                "ctas": [], "background_color": "primary",
            }),
            # Muster 6a: die eine Aussage der Seite, direkt unter dem Kopf
            m.zusage(
                "Bis zum 20. Juli 2026 wurden wir nicht verpflichtet, Auskünfte unter Geheimhaltung zu erteilen.",
                grundlage="Warrant Canary: keine Geheimhalteanordnung, etwa nach § 95 GWB oder § 100b StPO.",
                bedingungen_titel="So lesen Sie diese Erklärung",
                bedingungen=["Wir erneuern sie vierteljährlich, die nächste Fassung folgt im Oktober 2026.",
                             "Verschwindet sie oder veraltet sie, interpretieren Sie das entsprechend."],
                anchor="warrant-canary",
            ),
            # Muster 9b: zwei Nullen mit einer Tabelle statt sieben gleicher Kacheln
            m.nullen(
                "Anfragen und Vorfälle 2026",
                [("Behördenanfragen", "0"), ("Sicherheitsvorfälle", "0")],
                [
                    ("Behördenanfragen", [
                        ("Strafverfolgung", "Auskunftsersuchen und Beschlagnahmen von Polizei und Staatsanwaltschaft", "0"),
                        ("Geheimdienste", "Anfragen von Nachrichtendiensten", "0"),
                        ("Zivilrechtlich", "Auskunfts- und Herausgabeverlangen Dritter", "0"),
                        ("Datenherausgaben", "tatsächlich herausgegebene Datensätze", "0"),
                    ]),
                    ("Sicherheitsvorfälle", [
                        ("Datenschutzvorfälle", "Verletzungen des Schutzes personenbezogener Daten", "0"),
                        ("DSGVO-Meldungen", "Meldungen an die Aufsichtsbehörde nach Art. 33 DSGVO", "0"),
                        ("Gemeldete CVEs", "veröffentlichte Schwachstellen mit CVE-Kennung", "0"),
                    ]),
                ],
                text="Stand 20. Juli 2026, Berichtszeitraum seit 1. Januar 2026. Wir aktualisieren vierteljährlich; "
                     "jede Zahl über null erläutern wir an dieser Stelle.",
                spalten=("Art", "Was dazu zählt", "2026"), anchor="anfragen",
            ),
            # Muster 3 als Kontenblatt
            m.register(
                "Finanztransparenz",
                [
                    m.gruppe("Einnahmen 2026",
                             m.zeile("Work-Lizenzen", "Beta-Phase, noch keine Lizenzeinnahmen", stand="0 €", status="zahl"),
                             m.zeile("Fördermittel", "in Beantragung", stand="–", status="zahl"),
                             summe_label="Einnahmen 2026", summe="~ 0 €"),
                    m.gruppe("Ausgaben 2026, laufende Kosten",
                             m.zeile("Hosting", "Hetzner, Rechenzentren in Deutschland", stand="~ 60 € im Monat", status="zahl"),
                             m.zeile("Domain und DNS", "", stand="~ 30 € im Jahr", status="zahl"),
                             m.zeile("Werkzeuge und Buchhaltung", "", stand="~ 40 € im Monat", status="zahl"),
                             m.zeile("KI-Inferenz", "Tests", stand="~ 20 € im Monat", status="zahl"),
                             summe_label="Hochgerechnet auf das Jahr", summe="~ 1.200 €"),
                ],
                spalten=["Posten", "Anmerkung", "Betrag"],
                subline="Wir legen offen, wie das Geld fließt: Einnahmen wie Ausgaben.",
                anchor="finanzen",
            ),
            # Muster 9a. Dieselben Kennzahlen mit Stand wie auf /presse/ (KENNZAHLEN in
            # marketing/seeds_unternehmen.py) – bei jeder Aktualisierung beide Stellen nachziehen.
            m.zahlensatz(
                "Reichweite des Bürgerportals",
                "Am 2. Oktober 2026 machte das Bürgerportal <b>204.819</b> Dokumente, <b>91.662</b> Vorgänge und "
                "Vorlagen und <b>13.903</b> Sitzungen aus <b>5</b> Kommunen und Körperschaften frei durchsuchbar.",
                rand="<p><strong>So zählen wir:</strong> den Bestand im Bürgerportal am Stichtag, nicht Besuche. "
                     "Ohne Tracker und ohne individuelle Profile.</p><p><a href=\"/quellen/\">Quellennachweise</a></p>",
                anchor="reichweite",
            ),
            m.einladung(
                "Fehlt Ihnen eine Zahl?",
                "Sagen Sie uns, welche Angabe Sie hier sehen möchten. Wir nehmen sie auf.",
                "Vorschlag einreichen", "/kontakt/?subject=Transparenz",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Nächste Aktualisierung", "Oktober 2026", ""),
                      ("Sicherheit", "Responsible Disclosure", "/sicherheit/disclosure/"),
                      ("Was neu ist", "Releases", "/releases/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /preise/ — Insight + Work + Session
        # ════════════════════════════════════════════════════════════
        "preise": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "Faire Preise für", "title_highlight": "faire Demokratie.",
                "subline": "Das Bürgerportal ist kostenlos, mandari Work hat einen festen Preis je Fraktion, "
                            "mandari Session kalkulieren wir je Kommune – ohne versteckte Kosten und ohne Lock-in.",
                "subline_secondary": "",
                "ctas": [cta("Beta-Zugang anfragen", "/kontakt/?subject=Beta-Zugang-Work", "zap", "primary"),
                         cta("Erstgespräch vereinbaren", "/kontakt/#termin", "calendar", "secondary")],
                "background_color": "primary",
            }),
            # Die eine erlaubte Rasterstelle der Seite: drei gleichrangige Preisstufen
            ("pricing_table", {
                "header": hdr(title="Was mandari kostet", align="center",
                              subline="Alle Preise inkl. 19 % MwSt."),
                "tiers": [
                    {"color": "green", "name": "mandari Insight", "subtitle": "Bürger:innen-Portal",
                     "badge": "Immer kostenlos", "price_main": "0 €", "price_unit": "für immer",
                     "price_note": "Querfinanziert über Work & Session",
                     "description": "Öffentlicher Zugang zu Ratsinformationen — ohne Anmeldung, ohne Tracker, ohne Limit.",
                     "features": [bullet("Volltextsuche & Kartenansicht"), bullet("KI-Zusammenfassungen & Chat (geplant)"),
                                  bullet("Abstimmungsverhalten einsehen"), bullet("Keine Anmeldung nötig"),
                                  bullet("Selbst-Hosting möglich")],
                     "is_highlighted": False, "cta_label": "Insight öffnen", "cta_url": "/insight/"},
                    {"color": "primary", "name": "mandari Work", "subtitle": "Für Fraktionen · Pauschale ohne Userlimit",
                     "badge": "Beta-Phase", "price_main": "39,90 €", "price_unit": "/Monat inkl. MwSt.",
                     "price_net": "33,53 € netto zzgl. 19 % USt",
                     "price_alt": "oder 399 € pro Jahr (335,29 € netto) – zwei Monate gespart",
                     "price_note": "Beta-Kunden erhalten dauerhaft vergünstigte Konditionen",
                     "description": "Professionelle Sitzungsvorbereitung mit Team, KI und Antragsdatenbank.",
                     "features": [bullet("Alles aus Insight"), bullet("Team-Workspaces & Notizen"),
                                  bullet("Antragsdatenbank & Vorlagen"), bullet("Interne Abstimmungen & Termine"),
                                  bullet("KI-gestützte Recherche"), bullet("Unbegrenzte Nutzer:innen pro Fraktion & Gruppe"),
                                  bullet("Prioritäts-Support per E-Mail")],
                     "is_highlighted": True, "cta_label": "Jetzt buchen", "cta_url": "https://portal.mandari.de/buchen/"},
                    {"color": "blue", "name": "mandari Session", "subtitle": "Verwaltungs-RIS",
                     "badge": "Pilotphase 2026", "price_main": "Individuell",
                     "price_note": "Staffel nach Einwohnerzahl, Einrichtung einmalig, alle Module und das Bürgerportal inklusive. Öffentliche Preisliste in Vorbereitung.",
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
            # Muster 3 als Preisliste
            m.register(
                "Addons und Zusatzleistungen",
                [
                    m.gruppe("Addon, monatlich kündbar",
                             m.zeile("Eigene Domain", "Ihr Arbeitsportal unter eigener Adresse, z. B. mandari.fraktion.de – "
                                     "die Einrichtung übernehmen wir. Monatlich kündbar zum Monatsende.",
                                     stand="5,00 € im Monat", status="zahl")),
                    m.gruppe("Zusatzleistungen auf Anfrage, Abrechnung nach Angebot",
                             m.zeile("Schulung digital", "Online-Schulung für Ihre Fraktion, Termin nach Absprache.",
                                     stand="ab 250 €", status="zahl"),
                             m.zeile("Schulung vor Ort", "Präsenz-Schulung bei Ihnen, inklusive Vor- und Nachbereitung.",
                                     stand="ab 500 €", status="zahl"),
                             m.zeile("Einrichtungsassistent", "Wir richten mandari Work komplett für Sie ein: Struktur, "
                                     "Mitglieder, Vorlagen.", stand="ab 99 €", status="zahl")),
                ],
                spalten=["Leistung", "Was enthalten ist", "Preis inkl. MwSt."],
                subline="Erweitern Sie mandari Work bei Bedarf. Alle Preise brutto inklusive Mehrwertsteuer.",
                anchor="addons",
            ),
            # Muster 10: eine Datei, ein Button
            m.downloads(
                "Tagesaktuelle und vollständige Preisliste", "Vollständige Preisliste öffnen",
                "https://portal.mandari.de/preise/",
                subline="Alle Tarife, Addons und Zusatzleistungen mit allen Preisen, immer aktuell im Kundenportal.",
                hinweis="Webseite im Kundenportal unter portal.mandari.de/preise/", anchor="preisliste",
            ),
            ("feature_matrix", {
                "header": hdr(title="Wer macht was?", align="center",
                              subline="Drei Wege, mandari zu betreiben. Die Software ist in allen Fällen dieselbe und kostenlos, der Unterschied liegt in Verantwortung und Aufwand.",
                              anchor_id="betriebsmodelle"),
                "columns": ["Selbst-Hosting", "Managed Hosting", "On-Premises mit Support"],
                "show_legend": False,
                "groups": [
                    fgroup("Verantwortung",
                        frow("Server, Betriebssystem, Netzwerk", cell("info", "Kommune"), cell("info", "mandari, Rechenzentrum in Deutschland"), cell("info", "Kommune oder ihr Rechenzentrum")),
                        frow("Installation und Updates", cell("info", "Kommune"), cell("info", "mandari, automatisch"), cell("info", "Kommune, von mandari begleitet")),
                        frow("Backups", cell("info", "Kommune"), cell("info", "mandari, täglich, 30 Tage"), cell("info", "Kommune")),
                        frow("Monitoring und Störungsbehebung", cell("info", "Kommune"), cell("info", "mandari, Statusseite öffentlich"), cell("info", "Kommune, Unterstützung laut Vertrag")),
                        frow("Sicherheitsupdates", cell("info", "Kommune, Hinweise über GitHub"), cell("info", "mandari"), cell("info", "Kommune, Advisories von mandari")),
                        frow("Datenschutzrolle", cell("info", "Kommune ist allein verantwortlich"), cell("info", "mandari ist Auftragsverarbeiter mit AVV"), cell("info", "Kommune ist allein verantwortlich")),
                    ),
                    fgroup("Leistung und Kosten",
                        frow("Support", cell("info", "Community über GitHub"), cell("info", "inklusive, Premium-SLA optional"), cell("info", "Support- und Wartungsvertrag mit Reaktionszeiten")),
                        frow("Kosten", cell("info", "0 € Software, eigene Infrastruktur"), cell("info", "Monatspreis, Einrichtung einmalig"), cell("info", "Jahresvertrag nach Einwohnerzahl, Installation einmalig")),
                        frow("Für wen", cell("info", "IT-affine Kommunen, Rechenzentren, Community"), cell("info", "Kommunen ohne eigenen Betrieb, Fraktionen"), cell("info", "Kommunen mit Vorgaben zum Eigenbetrieb")),
                    ),
                ],
                "footnote": "<p>Betriebsdokumentation für Self-Hosting und On-Premises: <a href=\"https://docs.mandari.de/betrieb/\">docs.mandari.de/betrieb</a>. Unterlagen für Beschaffung und Prüfung: <a href=\"/vergabe/\">Vergabe und Unterlagen</a>.</p>",
            }),
            # Muster 8: zwei Optionen nach denselben Kriterien statt zwei Karten mit Aufzählungen
            m.vergleich(
                "Selbst hosten oder uns lassen",
                [("Selbst-Hosting", "Sie betreiben, wir liefern die Software"),
                 ("Managed Service", "Wir betreiben, Sie nutzen")],
                [
                    ("Kosten", ["keine Lizenzkosten; Server und Betrieb tragen Sie",
                                "monatlich laut <a href=\"https://portal.mandari.de/preise/\">Preisliste</a>"]),
                    ("Server, Backups, Monitoring", ["Ihre IT; Docker-Compose-Stack für jeden Linux-Server",
                                                     "übernehmen wir, kein Server-Management auf Ihrer Seite"]),
                    ("Updates und Sicherheitspatches", ["spielen Sie ein, sobald wir sie veröffentlichen",
                                                        "automatisch"]),
                    ("Daten", ["volle Kontrolle über Daten und Infrastruktur",
                               "Rechenzentren in Deutschland, Datenexport jederzeit, kein Lock-in"]),
                    ("Hilfe", ["Community-Support über GitHub, Support-Vertrag optional, Dokumentation auf docs.mandari.de",
                               "Support inklusive, Premium-SLA optional"]),
                    ("Erster Schritt", ["<a href=\"https://docs.mandari.de/betrieb/\">Self-Hosting-Anleitung</a>",
                                        "<a href=\"/kontakt/?subject=Managed-Service\">Managed Service anfragen</a>"]),
                ],
                subline="Open Source heißt: Sie haben die Wahl. Dieselbe Software, zwei Arten, sie zu betreiben.",
                anchor="selbst-hosten",
            ),
            # Muster 5b: Begründungen als Begriffe statt drittem Raster
            m.begriffe(
                "Warum genau diese Preise?",
                [
                    m.begriff("Unabhängig finanziert",
                              "mandari wird ohne Investoren und ohne große Vertriebsorganisation entwickelt — kein "
                              "VC-Geld, keine Sales-Abteilung. Damit das nachhaltig bleibt, müssen die Lizenzen die "
                              "Entwicklungszeit decken."),
                    m.begriff("Infrastruktur kostet",
                              "Server, Backups, Monitoring, TLS, Datenbank-Cluster, KI-Inferenz: ein paar 100 €/Monat "
                              "allein für die Infrastruktur. Davon fließt jeder Cent an deutsche Hosting-Partner."),
                    m.begriff("Demokratie-Bonus",
                              "Schulen, Universitäten, NGOs, Studierende — wer Demokratie stärkt, soll keine "
                              "kommerziellen Preise zahlen. Vergünstigungen auf Anfrage."),
                ],
                subline="Andere SaaS verstecken ihre Kalkulation. Wir nicht. Hier ist, woraus sich 39,90 € zusammensetzen.",
                anchor="kalkulation",
            ),
            ("accordion_faq", {
                "header": hdr(title="Was Sie sonst noch wissen sollten",
                              subline="Steht Ihre Frage nicht dabei? Schreiben Sie uns."),
                "anchor_id": "faq", "background": "gray",
                "rand": [
                    m.rand_fakten("Direkt fragen", ("E-Mail", "hello@mandari.de"),
                                  ("Antwort", "in der Regel innerhalb eines Werktags")),
                    m.rand_links("Zum Nachlesen", ("Vollständige Preisliste", "https://portal.mandari.de/preise/"),
                                 ("AGB", "/agb/"), ("Kündigung und Widerruf", "/kuendigung/")),
                ],
                "items": [
                    {"question": "Warum ist Insight kostenlos?",
                     "answer": "<p>Zugang zu kommunalpolitischen Informationen ist ein Grundrecht — nicht ein Premium-Feature. Insight finanziert sich quer über Work und Session. So bleibt der Bürger:innen-Zugang dauerhaft frei.</p>"},
                    {"question": "Wie viele Nutzer:innen sind in einer Lizenz enthalten?",
                     "answer": "<p><strong>Unbegrenzt viele.</strong> Eine mandari-Work-Lizenz gilt pauschal pro Organisation und hat kein Nutzer-Limit.</p><p>Ob Ihre Fraktion 3 oder 30 Mandatsträger:innen hat, dazu Büromitarbeitende und sachkundige Bürger:innen: Der Pauschalpreis bleibt gleich.</p>"},
                    {"question": "Sind die Preise inkl. MwSt.?",
                     "answer": "<p>Ja, alle hier genannten Preise verstehen sich inkl. 19 % deutscher Mehrwertsteuer. Für Angebotsvergleiche in Vergabeverfahren weisen wir den Nettopreis zusätzlich aus, zum Beispiel 39,90 € brutto entsprechen 33,53 € netto.</p>"},
                    {"question": "Was kostet mandari, wenn wir selbst hosten?",
                     "answer": "<p>Die Software kostet nichts, sie steht unter AGPL-3.0. Community-Support gibt es über GitHub. Für Verwaltungen, die verbindliche Reaktionszeiten, begleitete Updates und Sicherheitshinweise brauchen, bieten wir Support- und Wartungsverträge mit jährlicher Laufzeit an; die Konditionen richten sich nach der Einwohnerzahl. Sprechen Sie uns an.</p>"},
                    {"question": "Gibt es Rabatte für Studierende, Schulen oder NGOs?",
                     "answer": "<p>Ja. Studierende, Schulen, Universitäten, gemeinnützige Vereine und NGOs bekommen vergünstigte Konditionen, bis hin zu kostenfreien Lizenzen für die Lehre. Schicken Sie uns kurz Ihr Anliegen mit Nachweis.</p>"},
                    {"question": "Was passiert mit meinen Daten bei Kündigung?",
                     "answer": "<p>Sie bekommen vor der Kündigung einen vollständigen Export Ihrer Daten — JSON oder CSV, wahlweise auch im OParl-Format.</p><p>Nach Vertragsende behalten wir die Daten 30 Tage als Backup, danach werden sie unwiderruflich gelöscht. Auf Wunsch sofort.</p>"},
                    {"question": "Kann ich mandari komplett selbst hosten?",
                     "answer": "<p>Ja. mandari ist AGPL-3.0 lizenziert. Laden Sie den Code von GitHub und starten Sie den Docker-Compose-Stack auf Ihrem Server.</p>"},
                    {"question": "Was kostet mandari Session und wann ist es verfügbar?",
                     "answer": "<p>Session richtet sich an Verwaltungen und wird pro Kommune individuell kalkuliert. Pilotkommunen starten jetzt und erhalten Sonderkonditionen. Sprechen Sie uns früh an.</p>"},
                ],
            }),
            m.einladung(
                "Probieren Sie es aus.",
                "Die ersten 14 Tage mit mandari Work sind kostenfrei – ohne Kreditkarte.",
                "Beta-Zugang anfragen", "/kontakt/?subject=Beta-Zugang-Work",
                link_label="Erstgespräch vereinbaren", link_url="/kontakt/#termin",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                      ("Selbst hosten", "Quellcode auf GitHub", "https://github.com/mandariOSS/mandari"),
                      ("Für Vergabestellen", "Unterlagen für die Vergabeakte", "/vergabe/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /produkte/ — Plattform-Übersicht (ersetzt mit /fraktionen/
        # das frühere /produkt/; Text aus mandari.dev/produkte, gekürzt)
        # ════════════════════════════════════════════════════════════
        "produkte": [
            ("hero", {
                "title": "Eine Plattform, die mit Ihrer Verwaltung wächst.",
                "subline": "Wir starten im Herzen der kommunalen Demokratie: im Rat. Von dort wächst mandari Werkzeug für Werkzeug – auf einem gemeinsamen, offenen Fundament.",
                "ctas": [cta("Erstgespräch vereinbaren", "/kontakt/#termin"),
                         cta("Preise ansehen", "/preise/", style="outline")],
            }),
            # Muster 7: echte Bildschirme, angeschnitten, im Wechsel rechts und links
            m.produktbilder(
                "Heute im Einsatz",
                [
                    m.produktbild("session", "mandari Session",
                                  "Sitzungsdienst ohne Medienbrüche. Das Ratsinformationssystem führt Ihren Sitzungsdienst "
                                  "von der Tagesordnung bis zur freigegebenen Niederschrift – als Dienst aus deutschen "
                                  "Rechenzentren oder im eigenen Haus.",
                                  fakten=[("Für", "Verwaltungen"), ("Stand", "Pilotphase")],
                                  link_label="mandari Session ansehen", link_url="/kommunen/", anchor="session"),
                    m.produktbild("work", "mandari Work",
                                  "Politik machen statt PDFs sortieren. Sitzungen im Team vorbereiten, Anträge mit Fristen "
                                  "und Freigaben führen, Positionen abstimmen – in einem Werkzeug, das die Ratsdaten "
                                  "schon kennt.",
                                  fakten=[("Für", "Fraktionen und Mandatsträger:innen"), ("Stand", "Offene Beta")],
                                  link_label="mandari Work ansehen", link_url="/fraktionen/", anchor="work"),
                    m.produktbild("insight", "mandari Insight",
                                  "Kommunalpolitik, die man findet und versteht. Sitzungen, Vorlagen und Beschlüsse einer "
                                  "Kommune an einem Ort – im Volltext durchsuchbar, auf der Karte verortet, ohne Anmeldung "
                                  "und kostenlos.",
                                  fakten=[("Für", "Bürger:innen"), ("Stand", "Im Einsatz")],
                                  link_label="Bürgerportal öffnen", link_url="/insight/", anchor="insight"),
                ],
                subline="Drei Produkte für die drei Seiten der Ratsarbeit. Einzeln stark, zusammen ein System.",
                anchor="heute",
                # Weitere Werkzeuge kündigen wir nicht auf den Produktseiten an; was geplant ist, steht in der Roadmap.
                note="<p>Was wir als Nächstes bauen, steht mit Zeitraum und Verbindlichkeit in der <a href=\"/roadmap/\">Roadmap</a>.</p>",
            ),
            # Muster 5b: Plattform-Eigenschaften als Begriffe
            m.begriffe(
                "Ein Fundament für alles",
                [
                    m.begriff("Ein Datenbestand",
                              "Sitzungen, Vorlagen, Beschlüsse und Dokumente liegen einmal vor. Jedes Produkt arbeitet auf "
                              "demselben Stand – ohne Export, ohne Abgleich."),
                    m.begriff("Offene Standards",
                              "Alle Ratsdaten stehen über OParl 1.1 bereit. Ihre Daten bekommen Sie jederzeit vollständig heraus.",
                              link_label="Zur Schnittstelle", link_url="https://docs.mandari.de/insight/oparl-api/"),
                    m.begriff("Sicherheit, die man prüfen kann",
                              "Betrieb in ISO-27001-zertifizierten Rechenzentren in Deutschland, offener Code, Stückliste "
                              "je Release und geregelte Meldewege für Schwachstellen.",
                              link_label="Trust Center", link_url="/trust/"),
                    m.begriff("Ihr Betrieb, Ihre Wahl",
                              "Als Dienst von uns betrieben – oder per Docker Compose im eigenen Rechenzentrum, mit "
                              "Betreuungsvertrag. Der Funktionsumfang ist derselbe.",
                              link_label="Betriebsmodelle vergleichen", link_url="/preise/#betriebsmodelle"),
                ],
                subline="Was heute für die Ratsarbeit gilt, gilt für jedes künftige Produkt.",
                anchor="fundament",
            ),
            ("feature_matrix", {
                "header": hdr(title="Welches Modul kann was?", anchor_id="funktionen",
                              subline="Eine Tabelle statt Prospektsprache, Stand Oktober 2026. Auch was noch fehlt, steht hier: geplante Funktionen mit Zeitraum aus der Roadmap, offene Punkte als „in Prüfung“."),
                "columns": ["Insight (Bürgerportal)", "Work (Fraktionen)", "Session (Verwaltung)"],
                "show_legend": True,
                "groups": [
                    fgroup("Sitzungsdienst",
                        frow("Sitzungsplanung und Tagesordnung", cell("yes", "Anzeige"), cell("partial", "Vorbereitung und Notizen"), cell("yes")),
                        frow("Einladungen digital und als Druck", cell("no"), cell("partial", "Fraktionssitzungen"), cell("yes")),
                        frow("Sitzungsmappe als Gesamt-PDF", cell("no"), cell("no"), cell("yes", "mit Inhaltsverzeichnis und Lesezeichen")),
                        frow("Personalisiertes Wasserzeichen", cell("no"), cell("no"), cell("review")),
                        frow("Protokoll mit Genehmigungsworkflow", cell("no"), cell("yes", "Fraktionssitzungen"), cell("yes")),
                        frow("Anwesenheit und Rückmeldungen", cell("no"), cell("yes"), cell("yes")),
                        frow("Abstimmungsergebnisse, auch namentlich", cell("yes", "Anzeige"), cell("yes", "interne Abstimmungen"), cell("yes")),
                        frow("Umlaufbeschlüsse", cell("no"), cell("no"), cell("partial", "Rücklauf erfassen; Stimmabgabe online in Prüfung")),
                        frow("Beschlusskontrolle und Umsetzungsstand", cell("yes", "Beschlüsse verfolgen, Abo"), cell("yes", "Beschlüsse der Kommune"), cell("yes", "Beschlussregister")),
                        frow("Fristen-Erinnerungen (Ladung, Vorlagen, Wiedervorlage)", cell("no"), cell("no"), cell("yes")),
                        frow("Raum- und Ressourcenplanung", cell("no"), cell("no"), cell("planned", "2027")),
                        frow("Bekanntmachung und Amtsblatt", cell("no"), cell("no"), cell("review")),
                        frow("Sitzungsgeld und Aufwandsentschädigung", cell("no"), cell("no"), cell("yes", "mit Vier-Augen-Prinzip und SEPA")),
                        frow("Mitteilung an das Finanzamt (Mitteilungsverordnung)", cell("no"), cell("no"), cell("review")),
                        frow("Endgeräte der Ratsmitglieder verwalten", cell("no"), cell("no"), cell("yes", "Bestand und Zuschüsse")),
                    ),
                    fgroup("Sitzung live",
                        frow("Hybride Sitzungen mit Live-Cockpit", cell("no"), cell("no"), cell("yes", "Teilnahmeart, Beschlussfähigkeit, Störungen")),
                        frow("Stimmabgabe am eigenen Gerät", cell("no"), cell("no"), cell("planned", "2027")),
                        frow("Rednerliste und Saalanzeige", cell("no"), cell("no"), cell("planned", "2027")),
                        frow("Livestream mit Sprungmarken je Tagesordnungspunkt", cell("planned", "2027"), cell("no"), cell("partial", "Stream-Adresse je Sitzung; Sprungmarken 2027")),
                        frow("Konferenz- und Abstimmungsanlagen im Saal", cell("no"), cell("no"), cell("review")),
                        frow("KI-Entwurf der Niederschrift", cell("no"), cell("review", "Fraktionssitzungen in Prüfung"), cell("planned", "2027")),
                    ),
                    fgroup("Vorlagen und Anträge",
                        frow("Vorlagen und Drucksachen mit Beratungsfolge", cell("yes", "Anzeige"), cell("yes", "Anzeige und Kommentare"), cell("yes")),
                        frow("Mitzeichnung mit Vier-Augen-Prinzip und Vertretung", cell("no"), cell("no"), cell("yes")),
                        frow("Parallele Stationen und Eskalation", cell("no"), cell("no"), cell("planned", "2027")),
                        frow("Freigabe unterwegs in mobiler Ansicht", cell("no"), cell("no"), cell("review")),
                        frow("Fassungen mit Vergleich", cell("no"), cell("yes", "Versionshistorie"), cell("yes")),
                        frow("Import aus Word", cell("no"), cell("yes", "Word und PDF"), cell("planned", "2027")),
                        frow("Elektronische Signatur", cell("no"), cell("no"), cell("planned", "2027")),
                        frow("Anträge schreiben mit Versionen und Vorlagen", cell("no"), cell("yes"), cell("partial", "Antragseingang")),
                        frow("Digitale Einreichung Fraktion an Verwaltung", cell("no"), cell("yes"), cell("yes", "mit Statusrückmeldung")),
                        frow("Gemeinsames Schreiben in Echtzeit", cell("no"), cell("yes"), cell("planned", "nach 1.0")),
                        frow("KI-Schreibhilfe", cell("no"), cell("yes", "Antragsassistent"), cell("review")),
                    ),
                    fgroup("Für Ratsmitglieder",
                        frow("Alle Unterlagen, auch nichtöffentliche, im eigenen Bereich", cell("no"), cell("partial", "Unterlagen der Fraktion"), cell("review", "heute mit der Ladung per E-Mail")),
                        frow("Notizen an Tagesordnungspunkten und Vorlagen", cell("no"), cell("yes", "privat oder geteilt"), cell("no")),
                        frow("App mit Unterlagen offline", cell("planned", "Bürger-App 2027"), cell("partial", "installierbare Web-App; offline 2027"), cell("planned", "2027")),
                    ),
                    fgroup("Öffentlichkeit und Daten",
                        frow("Bürgerportal ohne Anmeldung", cell("yes"), cell("no"), cell("yes", "Veröffentlichung per Schalter")),
                        frow("Volltextsuche inklusive Texterkennung", cell("yes"), cell("yes"), cell("yes")),
                        frow("Schwärzung für die Veröffentlichung", cell("planned", "2027"), cell("no"), cell("planned", "2027")),
                        frow("Einbindung in die Website der Kommune", cell("partial", "Kalender-Feed, OParl; Bausteine in Prüfung"), cell("no"), cell("info", "über das Bürgerportal")),
                        frow("OParl-1.1-Schnittstelle", cell("yes", "Aggregations-API mit Änderungsfeed"), cell("no"), cell("yes", "je Kommune")),
                        frow("Datenkatalog nach DCAT-AP.de", cell("partial", "Katalog vorhanden, in der Installation einschaltbar; Anbindung an Datenportale folgt"), cell("no"), cell("partial", "je Kommune, in der Installation einschaltbar; Anbindung an Datenportale folgt")),
                        frow("Öffentliche Fraktions-API für die eigene Webseite", cell("no"), cell("yes"), cell("no")),
                        frow("Ratsfragen an Mandatsträger:innen", cell("yes"), cell("no"), cell("no")),
                        frow("Einwohnerfragestunde und Eingaben", cell("planned", "2027"), cell("no"), cell("planned", "2027")),
                        frow("KI-Zusammenfassungen", cell("partial", "für ausgewählte Quellen"), cell("yes", "Recherche"), cell("planned", "Sitzungsassistent")),
                        frow("Vorlagen in einfacher Sprache", cell("review"), cell("no"), cell("no")),
                    ),
                    fgroup("Betrieb und Sicherheit",
                        frow("Rollen und Rechte", cell("no", "ohne Anmeldung"), cell("yes", "über 50 Berechtigungen"), cell("yes")),
                        frow("Mandantentrennung, Verschlüsselung je Mandant", cell("no"), cell("yes"), cell("yes")),
                        frow("Zwei-Faktor-Authentifizierung", cell("no"), cell("yes"), cell("yes")),
                        frow("Revisionssicheres Audit-Log", cell("no"), cell("partial", "Änderungshistorie"), cell("yes", "inklusive Lesezugriffe")),
                        frow("Single Sign-on (SAML, OpenID Connect)", cell("no"), cell("planned", "2027"), cell("planned", "2027")),
                        frow("Übergabe an DMS und E-Akte", cell("no"), cell("no"), cell("planned", "2027")),
                        frow("Aufbewahrungsfristen und Löschlauf", cell("no"), cell("info", "Löschung bei Vertragsende"), cell("yes", "je Mandant konfigurierbar")),
                        frow("Datenexport (OParl, CSV, JSON)", cell("yes"), cell("yes"), cell("yes")),
                        frow("Self-Hosting mit Docker", cell("yes"), cell("yes"), cell("yes")),
                        frow("Barrierefreiheit nach BITV 2.0", cell("planned", "Prüfung 2026/27"), cell("planned", "Prüfung 2026/27"), cell("planned", "Selbstbewertung mit Prüfbericht Q4/2026")),
                        frow("Externer Penetrationstest", cell("planned", "2027"), cell("planned", "2027"), cell("planned", "2027")),
                    ),
                ],
                "footnote": "<p>Geplante Funktionen mit Zeitraum finden Sie in der <a href=\"/roadmap/\">Roadmap</a> und als Issues auf <a href=\"https://github.com/mandariOSS/mandari/issues\">GitHub</a>. Wie sich das zu etablierten Ratsinformationssystemen verhält, zeigt der <a href=\"/vergleich/\">RIS-Vergleich</a>. Details zu jeder Funktion in der <a href=\"https://docs.mandari.de/\">Dokumentation</a>.</p>",
            }),
            # Muster 3: Schnittstellen mit Stand statt sechs Kärtchen
            m.register(
                "Was sich anbinden lässt",
                [
                    m.gruppe("Heute verfügbar",
                             m.zeile("OParl 1.1", "Lesend und offen: Aggregations-API über alle Kommunen in Insight, eigene "
                                     "Schnittstelle je Kommune in Session. Import aus jedem OParl-fähigen RIS.",
                                     url="https://docs.mandari.de/insight/oparl-api/", ort="API-Dokumentation",
                                     stand="Verfügbar", status="da"),
                             m.zeile("Fraktions-API und Kalender", "Öffentliche Sitzungstermine der Fraktion per JSON auf "
                                     "der eigenen Webseite, OpenAPI-Schema, Kalender-Feeds für Sitzungstermine.",
                                     url="https://docs.mandari.de/work/fraktions-api/", ort="Anleitung",
                                     stand="Verfügbar", status="da")),
                    m.gruppe("Geplant für 2027",
                             m.zeile("Single Sign-on", "Anmeldung über den Verzeichnisdienst der Verwaltung: SAML 2.0 und "
                                     "OpenID Connect, etwa Entra ID oder Keycloak, mit Rollenzuordnung aus Gruppen.",
                                     url="https://github.com/mandariOSS/mandari/issues/95", ort="Issue #95",
                                     stand="Geplant 2027", status="offen"),
                             m.zeile("DMS und E-Akte", "Standardübergabe von Vorlagen, Niederschriften und Beschlüssen per "
                                     "CMIS und XDomea. Bis dahin richten wir die Übergabe je Kommune als Projekt ein; Export "
                                     "als PDF, JSON und OParl steht immer bereit.",
                                     url="https://github.com/mandariOSS/mandari/issues/154", ort="Issue #154",
                                     stand="Geplant 2027", status="offen"),
                             m.zeile("Livestream und Video", "Einbindung von Sitzungs-Livestreams und Aufzeichnungen mit "
                                     "Sprungmarken je Tagesordnungspunkt im Bürgerportal. Die Adresse des Streams lässt sich "
                                     "schon heute je Sitzung hinterlegen.",
                                     url="https://github.com/mandariOSS/mandari/issues/146", ort="Issue #146",
                                     stand="Geplant 2027", status="offen"),
                             m.zeile("Open-Data-Portale", "Ratsdaten automatisch als Open-Data-Katalog nach DCAT-AP.de, "
                                     "harvestbar durch Landesportale und GovData.",
                                     url="https://github.com/mandariOSS/mandari/issues/112", ort="Epic #112",
                                     stand="Geplant 2027", status="offen")),
                ],
                spalten=["Schnittstelle", "Was sie leistet", "Stand"],
                subline="Die ersten Fragen jeder IT-Leitung: was heute läuft, was geplant ist und was wir als Projekt umsetzen.",
                anchor="integrationen",
                bestand="{da} von {gesamt} sind heute verfügbar, {offen} sind für 2027 geplant.",
            ),
            m.einladung(
                "Sehen Sie mandari in Aktion.",
                "Wir zeigen Ihnen die Plattform an Ihren eigenen Fragen: 30 Minuten, per Video, am Telefon oder "
                "persönlich in Münster.",
                "Erstgespräch vereinbaren", "/kontakt/#termin",
                link_label="Bürgerportal ausprobieren", link_url="/insight/",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Preise", "Was mandari kostet", "/preise/"),
                      ("Für die IT", "Trust Center", "/trust/"), ("Im Vergleich", "RIS-Vergleich", "/vergleich/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /fraktionen/ — mandari Work (vorher Teil von /produkt/)
        # ════════════════════════════════════════════════════════════
        "fraktionen": [
            ("hero", {
                "title": "Politik machen statt PDFs sortieren.",
                "subline": "mandari Work ist der gemeinsame Arbeitsplatz Ihrer Fraktion: Sitzungen vorbereiten, Anträge schreiben, Positionen abstimmen – in einem Werkzeug, das die Ratsdaten Ihrer Kommune schon kennt.",
                "ctas": [cta("mandari Work buchen", "https://portal.mandari.de/buchen/"),
                         cta("Alle Funktionen im Überblick", "/produkte/#funktionen", style="outline")],
            }),
            # Muster 5b: sechs Vorteile als Begriffe (das Bild von Work steht schon im Kopf)
            m.begriffe(
                "Was Ihre Fraktion gewinnt",
                [
                    m.begriff("Sitzungen gemeinsam vorbereiten",
                              "Tagesordnung, Vorlagen und Beratungsfolge kommen aus dem Ratsinformationssystem. Ihre "
                              "Fraktion kommentiert, verteilt Zuständigkeiten und hält Positionen fest – an einem Ort statt "
                              "in zehn Mailverläufen."),
                    m.begriff("Anträge mit Fristen und Freigaben",
                              "Anträge und Anfragen entstehen gemeinsam, mit Versionen, Vorlagen und Schreiben in "
                              "Echtzeit. Wer freigeben muss, sieht es; welche Frist läuft, steht daneben."),
                    m.begriff("Eigene Sitzungen, sauber dokumentiert",
                              "Einladung, Tagesordnung, Anwesenheit, interne Abstimmungen und Protokoll Ihrer "
                              "Fraktionssitzungen – an einem Ort und für alle Mitglieder auffindbar."),
                    m.begriff("Recherche im ganzen Bestand",
                              "Volltextsuche über alle öffentlichen Ratsdokumente Ihrer Kommune, auch in gescannten PDFs, "
                              "dazu KI-gestützte Recherche."),
                    m.begriff("Ihre Termine auf Ihrer Webseite",
                              "Öffentliche Sitzungstermine der Fraktion per Schnittstelle und Kalender-Feed – für Ihre "
                              "Webseite und die Kalender Ihrer Mitglieder.",
                              link_label="Anleitung zur Fraktions-API", link_url="https://docs.mandari.de/work/fraktions-api/"),
                    m.begriff("Vertrauliches bleibt vertraulich",
                              "Jede Organisation arbeitet in einem eigenen, verschlüsselten Bereich, mit Rollen, Rechten "
                              "und Zwei-Faktor-Anmeldung. Ihre Daten exportieren Sie jederzeit vollständig.",
                              link_label="Sicherheit im Trust Center", link_url="/trust/"),
                ],
                subline="Weniger Abstimmung per Mail, weniger Suchen in PDF-Stapeln, mehr Zeit für Politik.",
                anchor="funktionen",
            ),
            # Muster 8: zwei Wege nach denselben Kriterien
            m.vergleich(
                "Funktioniert mit dem RIS Ihrer Kommune",
                [("Mit mandari Session", "Volle Integration"),
                 ("Mit einem anderen RIS", "Über die OParl-Schnittstelle")],
                [
                    ("Ihre Kommune", ["nutzt mandari Session",
                                      "nutzt ALLRIS, regisafe, SessionNet oder ein anderes System mit OParl-Schnittstelle "
                                      "– und muss nichts wechseln"]),
                    ("Ratsdaten", ["derselbe Datenbestand wie die Verwaltung, Änderungen kommen sofort an",
                                   "öffentliche Ratsdaten, automatisch übernommen"]),
                    ("Anträge", ["reichen Sie direkt digital bei der Verwaltung ein",
                                 "schreiben und verwalten Sie in Work, eingereicht wird auf dem Weg Ihrer Kommune"]),
                    ("Nichtöffentliche Vorlagen", ["stehen berechtigten Mitgliedern automatisch bereit",
                                                   "nein, nur öffentliche Ratsdaten"]),
                ],
                subline="Ob Ihre Kommune mandari Session nutzt oder ein anderes Ratsinformationssystem: mandari Work arbeitet mit beiden.",
                anchor="ris",
            ),
            m.einladung(
                "Starten Sie mit Ihrer Fraktion.",
                "39,90 € im Monat inklusive Mehrwertsteuer, pauschal für die ganze Fraktion – ohne Nutzerlimit, "
                "Mitarbeitende und sachkundige Bürger:innen eingeschlossen.",
                "mandari Work buchen", "https://portal.mandari.de/buchen/",
                link_label="Preise und Zusatzleistungen ansehen", link_url="/preise/",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                      ("Ausprobieren", "14 Tage kostenfrei", "/kontakt/?subject=Beta-Zugang-Work"),
                      ("Alle Funktionen", "Funktionsübersicht", "/produkte/#funktionen")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /mitmachen/ (Du-Form)
        # ════════════════════════════════════════════════════════════
        "mitmachen": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "mandari ist offen.", "title_highlight": "Bau mit.",
                "subline": "Du musst kein Profi sein, kein Vertrag, kein Geld. Eine Stunde reicht, manchmal sogar fünf Minuten.",
                "subline_secondary": "",
                "ctas": [cta("Auf GitHub ansehen", "https://github.com/mandariOSS", "github", "primary"),
                         cta("Good first issues", "https://github.com/mandariOSS/mandari/labels/good%20first%20issue", "sparkles", "secondary")],
                "background_color": "primary",
            }),
            # Muster 3b Wegweiser: Beitrag, was du tust, erster Schritt
            m.register(
                "Such dir aus, was zu dir passt",
                [m.gruppe("",
                    m.zeile("Code beitragen", "Pull Requests jeder Größe sind willkommen — vom Tippfehler bis zum neuen "
                            "OParl-Adapter. Klon das Repo, starte es mit docker compose up und such dir ein Issue mit dem "
                            "Label „good first issue“.", ort="Django, HTMX, PostgreSQL",
                            zusatz="<a href=\"https://github.com/mandariOSS/mandari/labels/good%20first%20issue\">Erstes Issue finden</a>"),
                    m.zeile("Testen und Fehler melden", "Du klickst dich durch mandari, findest etwas Komisches und "
                            "schreibst zwei Sätze auf — fertig. Ein Screenshot hilft, die Vorlage für Fehlerberichte "
                            "führt dich durch.", ort="Der niederschwelligste Beitrag",
                            zusatz="<a href=\"https://github.com/mandariOSS/mandari/issues/new?template=bug_report.md\">Fehler melden</a>"),
                    m.zeile("Übersetzen", "mandari soll europaweit zugänglich werden. Deutsch ist vollständig, Englisch "
                            "in Arbeit. Wenn du Französisch, Niederländisch, Polnisch oder eine andere EU-Sprache als "
                            "Muttersprache sprichst, brauchen wir dich.", ort="Aktuell nur Deutsch, EU-Sprachen folgen",
                            zusatz="<a href=\"/kontakt/?subject=Übersetzung-Sprache\">Sprache anbieten</a>"),
                    m.zeile("Doku schreiben", "Wenn du mandari verstanden hast, schreib's auf — die nächste Person spart "
                            "Stunden. Besonders gefragt: Anleitungen zum Selbstbetrieb, OParl-Adapter für eure Kommune und "
                            "Beispiele für die API.", ort="Markdown reicht, kein Setup nötig",
                            zusatz="<a href=\"https://github.com/mandariOSS/mandari/tree/main/docs\">Doku-Verzeichnis öffnen</a>"),
                    m.zeile("Design beitragen", "Du hast ein Auge für Oberflächen, die Bürger:innen verstehen? Wir suchen "
                            "Skizzen für komplexe Abläufe — in Figma, Penpot oder als markierter Screenshot. Auch eine "
                            "grobe Idee hilft.", ort="UI-Skizzen, Karten-Konzepte, Symbole",
                            zusatz="<a href=\"/kontakt/?subject=Design-Beitrag\">Konzept zeigen</a>"),
                    m.zeile("Verbreiten", "mandari braucht Reichweite. Halte einen Kurzvortrag in deinem OK Lab, schreib "
                            "über deine Erfahrungen oder empfiehl uns deiner Bürgermeisterin.",
                            ort="Vortrag, Blog, Empfehlung",
                            zusatz="<a href=\"/kontakt/?subject=mandari-verbreiten\">Materialien anfragen</a>"),
                )],
                spalten=["Beitrag", "Was du tust", "Erster Schritt"],
                subline="Du bist willkommen, auch mit einem Tippfehler. Wir kommentieren neue Issues und Pull Requests "
                        "zeitnah und persönlich und begleiten dich bei deinem ersten Beitrag.",
                anchor="wege",
            ),
            # Muster 2: kurze Folge ohne Fristen, das Ergebnis am Ende
            m.schrittfolge(
                "Drei Schritte vom „Hallo“ zum gemergten Beitrag",
                [("Hallo sagen", "Im Discussion-Thread auf GitHub oder per E-Mail: wer du bist und woran du Interesse hast.",
                  "Wir antworten zeitnah."),
                 ("Issue wählen", "Aus den offenen Issues oder ein neues. Wir kommentieren mit Kontext.",
                  "Mentoring inklusive."),
                 ("Beitrag einreichen", "Pull Request, Übersetzung, Doku-Patch oder Markdown im Issue — alles passt. "
                  "Die CI läuft, wir reviewen.", "")],
                subline="Kein bürokratisches CLA, keine 50-seitige Contributor-Doku.",
                ergebnis={"titel": "Gemergt.", "text": "Dein Beitrag steht in den Release-Notes.",
                          "link_label": "Offene Issues ansehen",
                          "link_url": "https://github.com/mandariOSS/mandari/labels/good%20first%20issue"},
                anchor="ablauf",
            ),
            m.einladung(
                "Schreib einfach Hallo.",
                "Egal ob du eine Stunde oder einen Nachmittag hast, ob Profi oder blutige Anfänger:in — wir freuen "
                "uns auf deine Nachricht.",
                "Auf GitHub starten", "https://github.com/mandariOSS",
                link_label="Nachricht schreiben", link_url="/kontakt/?subject=Hallo-aus-der-Community#nachricht",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Repository", "mandariOSS/mandari", "https://github.com/mandariOSS/mandari"),
                      ("Regeln", "CONTRIBUTING", "https://github.com/mandariOSS/mandari/blob/main/CONTRIBUTING.md"),
                      ("Sicherheitslücke", "vertraulich melden", "/sicherheit/disclosure/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /trust/ — Trust Center
        # ════════════════════════════════════════════════════════════
        "trust": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "Trust Center:", "title_highlight": "alle Antworten an einem Ort.",
                "subline": "Bevor Sie mit einem Anbieter sprechen, möchten Sie AVV, Subprozessorenliste, Hosting-Stack und Backup-Strategie sehen. Hier sind sie, vorbereitet und unterschriftsreif.",
                "subline_secondary": "Diese Seite richtet sich an Datenschutzbeauftragte, IT-Leiter:innen und Verwaltungs-Compliance.",
                "ctas": [cta("Muster-AVV ansehen", "/avv/", "file-signature", "primary"),
                         cta("Konkrete Frage stellen", "/kontakt/?subject=Trust-Center-Frage", "message-square", "outline")],
                "background_color": "primary",
            }),
            # Eckdaten: stehen auf der Dokumentseite (marketing/dokument.html) in der Randspalte
            ("trust_banner", {"color": "primary", "items": [
                trust_item("map-pin", "Hosting", "100 % in Deutschland"),
                trust_item("lock", "TLS 1.3", "AES-256 at rest"),
                trust_item("database-backup", "Backup", "täglich, Aufbewahrung 30 Tage"),
                trust_item("file-signature", "AVV", "nach Art. 28 DSGVO"),
            ]}),
            # ── 01 · AVV ─────────────────────────────────────────────
            ("numbered_article", {
                "number": "1", "anchor": "dpa",
                "title": "Auftragsverarbeitung (AVV)",
                "body": (
                    "<p><strong>mandari schließt mit jeder buchenden Organisation und jeder Kommune einen "
                    "Auftragsverarbeitungsvertrag (AVV) nach Art. 28 DSGVO ab.</strong> Der Vertrag regelt "
                    "Gegenstand und Dauer der Verarbeitung, Datenkategorien, Pflichten des Auftragsverarbeiters, "
                    "Unterauftragsverhältnisse, Löschung nach Vertragsende und Ihre Kontrollrechte. "
                    "Den vollständigen Mustertext können Sie vorab prüfen: "
                    "<a href=\"/avv/\">Muster-AVV online lesen</a>. Die Anlagen liegen in der Dokumentation: "
                    "<a href=\"https://docs.mandari.de/datenschutz/tom/\">Technische und organisatorische Maßnahmen</a>, "
                    "<a href=\"https://docs.mandari.de/datenschutz/loeschkonzept/\">Löschkonzept und Aufbewahrungsfristen</a>, "
                    "<a href=\"https://docs.mandari.de/datenschutz/avv-muster/\">Muster-AVV für mandari Session</a>.</p>"
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
                    "<p><strong>AVV anfordern:</strong> Schreiben Sie uns eine kurze Mail an "
                    "<a href=\"mailto:hello@mandari.de?subject=AVV-Anfrage\">hello@mandari.de</a> "
                    "mit dem Namen Ihrer Organisation — Sie erhalten den unterschriftsreifen AVV "
                    "als Dokument zurück. Den Mustertext gibt es unter <a href=\"/avv/\">mandari.de/avv</a>.</p>"
                ),
            }),
            # ── 02 · Subprocessoren: Muster 3 innerhalb der Dokumentseite ─
            ("numbered_article", {
                "number": "2", "anchor": "subprocessors",
                "title": "Subprocessoren — wer sonst noch Daten sieht",
                "body": (
                    "<p>Vollständige Liste aller Unterauftragsverarbeiter. Es gibt keine weiteren — "
                    "insbesondere keine Tracker, keine Analytics-Dienste und keine Anbieter außerhalb der EU.</p>"
                ),
            }),
            m.register(
                "",
                [m.gruppe("",
                    m.zeile("Hetzner Online GmbH", "Hosting aller Systeme in deutschen Rechenzentren. AVV nach Art. 28 "
                            "DSGVO besteht.", ort="Industriestr. 25, 91710 Gunzenhausen (DE)"),
                    m.zeile("Mollie B.V.", "Zahlungsabwicklung für mandari Work (Name, E-Mail, Zahlungs- und "
                            "Mandatsdaten).", ort="Keizersgracht 126, 1015 CW Amsterdam (NL/EU)"),
                    m.zeile("Haufe-Lexware GmbH & Co. KG", "Rechnungsstellung und Buchhaltung (lexware office).",
                            ort="Munzinger Str. 9, 79111 Freiburg (DE)"),
                )],
                spalten=["Unternehmen und Sitz", "Wofür"],
                note="<p>Über geplante Änderungen an dieser Liste informieren wir vorab; Sie haben ein "
                     "Widerspruchsrecht gegen neue Subunternehmer (Details im <a href=\"/avv/\">AVV, Ziff. 7</a>).</p>",
            ),
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
                    "<li>Eingesetzte Komponenten mit Lizenzen: <a href=\"https://docs.mandari.de/entwicklung/sbom/\">Software Bill of Materials</a></li>"
                    "<li>Betriebsmodelle und Self-Hosting: <a href=\"https://docs.mandari.de/betrieb/\">Betriebsdokumentation</a></li>"
                    "</ul>"
                ),
            }),
            # ── 04 · Backup: Muster 9a (Zahl im Satz) vor dem Text ─────
            ("numbered_article", {
                "number": "4", "anchor": "backup",
                "title": "Backup & Recovery",
                "body": (
                    "<p>Backups liegen getrennt vom Produktivsystem, ebenfalls in Deutschland. Wiederherstellungen "
                    "werden regelmäßig getestet.</p>"
                    "<p>Nach Vertragsende: Datenexport auf Anfrage innerhalb von 30 Tagen, danach unwiderrufliche "
                    "Löschung inklusive Vernichtung des mandantenspezifischen Schlüssels. Aufbewahrungsfristen und "
                    "Löschläufe je Mandant stehen im <a href=\"https://docs.mandari.de/datenschutz/loeschkonzept/\">Löschkonzept</a>.</p>"
                ),
            }),
            m.zahlensatz(
                "Sicherung",
                "Wir sichern alle Datenbanken <b>täglich</b> und bewahren jede Sicherung <b>30 Tage</b> auf.",
            ),
            # ── 05 · Verfügbarkeit ───────────────────────────────────
            ("numbered_article", {
                "number": "5", "anchor": "availability",
                "title": "Verfügbarkeit & Status",
                "body": (
                    "<p>Wir befinden uns in der Pilot-Phase und schulden vertraglich noch keine feste "
                    "Verfügbarkeitsquote (siehe <a href=\"/agb/\">AGB</a>). Ein SLA-Dokument mit Verfügbarkeitszusage, "
                    "Störungsklassen und Reaktionszeiten ist für die Version 1.0 in Vorbereitung "
                    "(<a href=\"https://github.com/mandariOSS/mandari/issues/93\">öffentlich nachverfolgbar</a>). "
                    "Was wir heute bieten:</p>"
                    "<ul>"
                    "<li>Öffentliche Live-Statusseite: <a href=\"https://status.mandari.de/\">status.mandari.de</a></li>"
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
                    "Zertifizierung ist in der Beta-Phase nicht realistisch — "
                    "und wir behaupten keine.</p>"
                    "<ul>"
                    "<li>Der gesamte Code ist Open Source (AGPL-3.0) und öffentlich auditierbar</li>"
                    "<li>Responsible-Disclosure-Programm nach RFC 9116: <a href=\"/sicherheit/disclosure/\">/sicherheit/disclosure/</a></li>"
                    "<li>Softwarelieferkette: alle Abhängigkeiten sind in Lockfiles festgeschrieben, jeder Build wird "
                    "automatisch gegen bekannte Schwachstellen geprüft (blockierend), und zu jedem Release entsteht eine "
                    "maschinenlesbare Stückliste (SBOM, CycloneDX) als Download bei den "
                    "<a href=\"https://github.com/mandariOSS/mandari/releases\">GitHub-Releases</a></li>"
                    "<li>Lizenzinventar nach REUSE-Standard: jede Datei im Repository trägt eine maschinenlesbare "
                    "Lizenz- und Urheberangabe, geprüft in der CI</li>"
                    "<li>Externes Security-Audit ist für die General-Availability-Phase geplant</li>"
                    "</ul>"
                ),
            }),
            m.register(
                "Fahrplan Nachweise",
                [m.gruppe("",
                    m.zeile("Barrierefreiheitsprüfung nach BITV 2.0", "Session, Erklärung mit Prüfbericht",
                            stand="Q4/2026", status="offen"),
                    m.zeile("Externer Penetrationstest", "mit veröffentlichter Zusammenfassung",
                            stand="2027", status="offen"),
                    m.zeile("Selbstbewertung nach BSI IT-Grundschutz", "Basis-Absicherung; ISO 27001 abhängig vom "
                            "Auftragsvolumen", stand="2027", status="offen"),
                )],
                spalten=["Nachweis", "Umfang", "Geplant"],
                note="<p>Fortschritt öffentlich: <a href=\"https://github.com/mandariOSS/mandari/issues/97\">Fahrplan "
                     "Sicherheitsnachweise</a></p>",
            ),
            m.einladung(
                "Frage übrig?",
                "Wenn Ihre Datenschutz- oder IT-Compliance hier keine Antwort findet, schreiben Sie uns. Wir "
                "antworten direkt und ohne Umwege.",
                "Frage stellen", "/kontakt/?subject=Trust-Center-Frage",
                link_label="Compliance-Call buchen", link_url="/kontakt/#termin-buchen",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Datenschutz", "datenschutz@mandari.de", ""),
                      ("Sicherheitslücke", "security@mandari.de", ""), ("Status", "status.mandari.de", "https://status.mandari.de/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /abuse/ — Missbrauch melden
        # ════════════════════════════════════════════════════════════
        "abuse": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "rose",
                "title": "Missbrauch melden,", "title_highlight": "wir kümmern uns",
                "subline": "Spam, illegaler Content, Datenschutz-Verletzungen, Urheberrechtsverstöße, Belästigung — wir bestätigen den Eingang innerhalb von 5 Werktagen.",
                "subline_secondary": "",
                "ctas": [cta("Missbrauch melden", "mailto:abuse@mandari.de?subject=Missbrauch-Meldung", "mail", "primary"),
                         cta("Kontaktformular", "/kontakt/?subject=Missbrauch-Meldung#nachricht", "message-square", "secondary")],
                "background_color": "primary",
            }),
            # Muster 3b Wegweiser: Anliegen, was wir brauchen, Adresse
            m.register(
                "Was möchten Sie melden?",
                [m.gruppe("",
                    m.zeile("Spam und unerwünschte Mails", "Die vollständige Mail mit Header, wann sie ankam und die "
                            "Absenderadresse.", ort="Sie bekommen Mails von @mandari.de, die Sie nicht erwartet haben",
                            zusatz="<a href=\"mailto:abuse@mandari.de?subject=Spam-Meldung\">abuse@mandari.de</a>"),
                    m.zeile("Illegaler Inhalt", "Die Adresse des Inhalts, eine Beschreibung des Verstoßes und, wenn "
                            "möglich, einen Screenshot.", ort="Strafbar, hetzerisch oder jugendgefährdend, auf Insight oder Work",
                            zusatz="<a href=\"mailto:abuse@mandari.de?subject=Illegaler-Content\">abuse@mandari.de</a>"),
                    m.zeile("Datenschutz-Verletzung", "Welche Daten betroffen sind, wo sie erschienen sind und einen "
                            "Identitätsnachweis.", ort="Auskunft, Löschung oder Beschwerde nach DSGVO",
                            zusatz="<a href=\"mailto:datenschutz@mandari.de?subject=DSGVO-Anfrage\">datenschutz@mandari.de</a>"),
                    m.zeile("Urheberrecht", "Welches Werk betroffen ist, die Adresse der Verletzung und warum Sie "
                            "berechtigt sind.", ort="Ihre Bilder, Texte oder Ihr Code ohne Erlaubnis auf mandari",
                            zusatz="<a href=\"mailto:abuse@mandari.de?subject=Urheberrecht\">abuse@mandari.de</a>"),
                    m.zeile("Belästigung und Drohungen", "<strong>Bei Gefahr zuerst die Polizei: 110.</strong> Dann "
                            "Screenshot und Adresse sichern und uns schreiben. Wir sperren das Konto und dokumentieren den "
                            "Vorfall für die Polizei.", ort="Hasskommentare, Mobbing, Stalking",
                            zusatz="<a href=\"mailto:abuse@mandari.de?subject=Belästigung\">abuse@mandari.de</a>"),
                    m.zeile("Behördenanfragen", "Gerichtlichen Beschluss, Aktenzeichen und Behörde sowie die konkrete "
                            "Datenangabe. Wir prüfen rechtlich und geben nur das Mindeste heraus.",
                            ort="Auskunftsersuchen und Beschlagnahmen",
                            zusatz="<a href=\"mailto:legal@mandari.de?subject=Behoerden-Anfrage\">legal@mandari.de</a>"),
                )],
                spalten=["Anliegen", "Was wir dafür brauchen", "Adresse"],
                kopfart="ueber",
                subline="Die Meldestelle ist für Bürger:innen, Behörden und Rechteinhaber da. Sicherheitslücken melden "
                        "Sie bitte über unser Meldeverfahren für Sicherheitslücken.",
                anchor="notfall",
            ),
            # Muster 1a: Fristen des Digital Services Act auf einer Achse
            m.zeitskala(
                "Was nach Ihrer Meldung passiert",
                subline="Wir behandeln jede Meldung vertraulich und persönlich, dokumentieren sie und halten die "
                        "Fristen des Digital Services Act ein.",
                anchor="ablauf",
                tage=21, zweite="Entscheidung",
                marken=[
                    m.marke(0, "Tag 0", "Ihre Meldung geht ein"),
                    m.marke(7, "5 Werktage", "Eingangsbestätigung mit Vorgangsnummer"),
                    m.marke(14, "14 Tage", "Prüfung, in der Regel abgeschlossen"),
                    m.marke(0, "je nach Fall", "Maßnahme", strecke="2", offen=True),
                    m.marke(1, "Abschluss", "Ihre Rückmeldung", strecke="2"),
                ],
                fenster="Bei Ablehnung erhalten Sie eine Begründung und einen Hinweis auf Rechtsbehelfe (DSA Art. 17).",
                skala=[m.skalenpunkt(0, "Tag 0"), m.skalenpunkt(7, "1 Woche"), m.skalenpunkt(14, "2 Wochen"),
                       m.skalenpunkt(21, "3 Wochen"), m.skalenpunkt(0, "Entscheidung", "2")],
                schritte=[
                    m.schritt("höchstens 5 Werktage", "Eingangsbestätigung",
                              "Sie erhalten eine Bestätigung mit Vorgangsnummer."),
                    m.schritt("in der Regel höchstens 14 Tage", "Prüfung",
                              "Wir prüfen die Meldung sachlich und rechtlich. Bei Unklarheiten fragen wir nach."),
                    m.schritt("je nach Fall", "Maßnahme",
                              "Bei berechtigter Meldung: Sperrung, Löschung, Korrektur oder Verweis an die zuständige Stelle."),
                    m.schritt("nach Abschluss", "Rückmeldung",
                              "Sie erfahren, was passiert ist. Bei Ablehnung: Begründung und Hinweis auf Rechtsbehelfe "
                              "(DSA Art. 17)."),
                ],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /barrierefreiheit/
        # ════════════════════════════════════════════════════════════
        "barrierefreiheit": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "Erklärung zur", "title_highlight": "Barrierefreiheit",
                "subline": "mandari ist bemüht, seine Website und alle Anwendungen barrierefrei zugänglich zu machen, nach den Maßgaben des BGG und der BITV 2.0.",
                "subline_secondary": "",
                "ctas": [], "background_color": "primary",
            }),
            # Muster 3: Stand je Bereich in einer Tabelle
            m.register(
                "Was funktioniert, und wo wir noch arbeiten",
                [
                    m.gruppe("Konform",
                             m.zeile("Tastatur-Navigation", stand="konform", status="da"),
                             m.zeile("Skip-Link", "WCAG 2.4.1", stand="konform", status="da"),
                             m.zeile("ARIA-Landmarks", stand="konform", status="da"),
                             m.zeile("Kontrast", "mindestens 4,5:1", stand="konform", status="da"),
                             m.zeile("Dunkelmodus", stand="konform", status="da"),
                             m.zeile("Touch-Ziele", "mindestens 44 × 44 px", stand="konform", status="da"),
                             m.zeile("Responsive Darstellung", "bis 320 px Breite", stand="konform", status="da")),
                    m.gruppe("Teilweise konform",
                             m.zeile("Karten-Layer", "Screenreader-Unterstützung im Aufbau", stand="teilweise", status="offen"),
                             m.zeile("Komplexe Filter", "Tastatur-Verbesserungen", stand="teilweise", status="offen"),
                             m.zeile("Symbole", "bessere ARIA-Beschriftungen nötig", stand="teilweise", status="offen"),
                             m.zeile("PDF-Dokumente", "teilweise nicht maschinenlesbar", stand="teilweise", status="offen"),
                             m.zeile("Leichte Sprache und Gebärdensprache", "in Planung", stand="teilweise", status="offen")),
                    m.gruppe("Ausnahmen, die wir nicht beeinflussen können",
                             m.zeile("OParl-Quelldokumente der Kommunen", stand="Ausnahme"),
                             m.zeile("Eingebettete Inhalte Dritter", "Kartenkacheln von OpenStreetMap", stand="Ausnahme"),
                             m.zeile("Archiv-Sitzungsprotokolle vor 2020", "gescannte PDFs", stand="Ausnahme")),
                ],
                spalten=["Bereich", "Anmerkung", "Stand"],
                subline="Diese Erklärung gilt für mandari.de und alle Subdomains, Stand 20. Juli 2026. Bei der letzten "
                        "Prüfung im April 2026 nach WCAG 2.1 AA und EN 301 549 war mandari teilweise konform mit der BITV 2.0.",
                anchor="stand",
            ),
            # Muster 5a: Weg mit Fristen in der Randspalte, Kontakt im Text
            m.randspalte(
                "Feedback und Durchsetzungsverfahren",
                "<p><strong>An uns direkt.</strong> Schreiben Sie uns, was nicht funktioniert hat: an "
                "<a href=\"mailto:barrierefreiheit@mandari.de\">barrierefreiheit@mandari.de</a> oder über das "
                "<a href=\"/kontakt/?subject=Barrierefreiheit\">Kontaktformular</a> mit dem Betreff „Barrierefreiheit“. "
                "Wir antworten in der Regel innerhalb von 5 Werktagen. Telefon und Gebärdensprache auf Anfrage.</p>"
                "<p><strong>Schlichtung.</strong> Wenn wir uns nicht einigen, können Sie sich an die Schlichtungsstelle "
                "nach § 16 BGG wenden – kostenlos und formfrei: Schlichtungsstelle nach dem "
                "Behindertengleichstellungsgesetz, Mauerstraße 53, 10117 Berlin, Telefon 030 18 527-2805, "
                "<a href=\"mailto:info@schlichtungsstelle-bgg.de\">info@schlichtungsstelle-bgg.de</a>.</p>",
                [
                    m.rand_ablauf("So geht es weiter", ("Ihre Meldung", "per E-Mail oder Formular"),
                                  ("5 Werktage", "unsere Antwort, in der Regel"),
                                  ("Keine Einigung", "Schlichtungsstelle nach § 16 BGG")),
                    m.rand_links("Direkt", ("Barriere melden", "/kontakt/?subject=Barrierefreiheit"),
                                 ("Zur Schlichtungsstelle", "https://www.schlichtungsstelle-bgg.de")),
                ],
                subline="Wenn Ihnen Barrieren auffallen, melden Sie sich. Wir antworten zeitnah und beheben sie so "
                        "schnell wie möglich.",
                anchor="feedback",
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /migration/
        # ════════════════════════════════════════════════════════════
        "migration": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "Wechsel von ALLRIS, regisafe oder Somacos?", "title_highlight": "Wir machen's planbar.",
                "subline": "Eine RIS-Ablösung ist kein Sprint, aber auch kein Drama: vier klare Schritte, eine ehrliche "
                            "Aufwandsschätzung und Parallelbetrieb, bis der Wechsel sitzt.",
                "subline_secondary": "",
                "ctas": [cta("Erstgespräch vereinbaren", "/kontakt/?subject=Migration-Beratung#termin", "calendar", "primary"),
                         cta("Was kommt mit?", "#scope", "list-checks", "secondary")],
                "background_color": "primary",
            }),
            # Muster 1b: Dauern aufeinanderfolgender Schritte, frühestens und spätestens
            m.dauerbalken(
                "So läuft eine Migration zu mandari",
                [
                    m.dauer("Bestandsaufnahme", "1–2 Wochen",
                            "Wir schauen uns Ihr Alt-RIS an: OParl-Verfügbarkeit, Datenmenge, Sonderfelder.", von=1, bis=2),
                    m.dauer("Mapping und Test", "2–4 Wochen",
                            "Wir bauen den Mapping-Layer und importieren in eine Test-Instanz.", von=2, bis=4),
                    m.dauer("Schulung und Parallelbetrieb", "4–8 Wochen",
                            "Ihr Team wird geschult, beide Systeme laufen parallel.", von=4, bis=8),
                    m.dauer("Umstellung", "an einem festen Tag",
                            "Definierter Termin für den Wechsel; das Alt-RIS bleibt danach lesbar.", meilenstein=True),
                ],
                subline="Für IT-Leiter:innen, Hauptamtsleiter:innen und Fraktionsgeschäftsführer:innen: realistische "
                        "Zeiten, klare Verantwortlichkeiten und kein Wechsel über Nacht – zwischen 7 und 14 Wochen "
                        "vom ersten Termin bis zur Umstellung.",
                anchor="ablauf",
            ),
            # Muster 8: Datenart × Weg der Übernahme
            m.vergleich(
                "Was kommt mit — und was prüfen wir individuell?",
                [("Über den OParl-Standard", "strukturiert und verlustfrei übernommen"),
                 ("In der Bestandsaufnahme", "gemeinsam vor der Umstellung geklärt")],
                [
                    ("Sitzungen, Tagesordnungen und TOPs", ["kommt mit", "–"]),
                    ("Vorlagen, Drucksachen und Beratungsfolgen", ["kommt mit", "–"]),
                    ("Gremien, Personen und Mitgliedschaften", ["kommt mit", "–"]),
                    ("Dokumente und PDFs", ["kommt mit, inklusive Volltext-Indexierung", "–"]),
                    ("Wahlperioden und Orte", ["kommt mit", "–"]),
                    ("Anbieterspezifische Sonderfelder und Vermerke", ["–", "prüfen wir individuell"]),
                    ("Historische Daten ohne OParl-Export", ["–", "prüfen wir individuell"]),
                    ("Interne, nichtöffentliche Vorlagen und Protokolle", ["–", "prüfen wir individuell"]),
                    ("Sitzungsgeld-Konfiguration und Abrechnungshistorie", ["–", "prüfen wir individuell"]),
                ],
                subline="Ehrliche Antwort statt „alles, kein Problem“: Der OParl-Standard trägt das meiste, der Rest ist Handarbeit.",
                anchor="scope",
            ),
            m.einladung(
                "Bereit für ein Erstgespräch?",
                "Pilotkommunen erhalten Sonderkonditionen für den Umstieg. In 30 Minuten klären wir, welches Alt-RIS, "
                "welche Datenmenge und welcher Zeitplan zu Ihrer Verwaltung passen.",
                "Erstgespräch vereinbaren", "/kontakt/?subject=Migration-Beratung#termin",
                link_label="Preise ansehen", link_url="/preise/",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                      ("Im Vergleich", "RIS-Vergleich", "/vergleich/"), ("Für Vergabestellen", "Unterlagen", "/vergabe/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /ratsinformationssystem/ — Sachseite zum Begriff (SEO, #914);
        # Inhalt in marketing/seeds_ris.py, ohne Preise
        # ════════════════════════════════════════════════════════════
        "ratsinformationssystem": seeds_ris.seite(),

        # ════════════════════════════════════════════════════════════
        # /kommunen/ — Für Kommunen & Verwaltungen (Zielgruppen-Seite)
        # ════════════════════════════════════════════════════════════
        "kommunen": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                # Suchbegriffe zuerst (SEO, #914); neben dem Bild von mandari Session bekommen lange Wörter
                # sieben Spalten (blocks.langes_wort, hero.html)
                "title": "Ratsinformationssystem und Sitzungsdienst ohne Medienbrüche.", "title_highlight": "",
                "subline": "mandari Session ist das Ratsinformationssystem für Ihre Verwaltung: von der Tagesordnung bis zur freigegebenen Niederschrift, mit kostenlosem Bürgerportal – auf deutschen Servern und vollständig Open Source.",
                "subline_secondary": "",
                "ctas": [cta("Erstgespräch vereinbaren", "/kontakt/?subject=Kommune-anbinden#termin", "calendar", "primary"),
                         cta("Migration vom Alt-RIS", "/migration/", "move-right", "secondary")],
                "background_color": "primary",
            }),
            # Muster 5b: drei Bausteine als Begriffe (das Bild von Session steht schon im Kopf)
            m.begriffe(
                "Drei Bausteine, ein Ziel: weniger Aufwand, mehr Transparenz",
                [
                    m.begriff("Sitzungsmanagement ohne Medienbrüche",
                              "Von der Sitzungsplanung bis zum Protokoll in einem System: Tagesordnungen, Einladungen "
                              "digital und auf Papier, Vorlagen und die Abrechnung des Sitzungsgelds. Was einmal erfasst "
                              "ist, wird nicht noch einmal abgetippt — das spart Zeit im Ratsbüro und vermeidet Fehler.",
                              marke="mandari Session", link_label="Angebot anfragen",
                              link_url="/kontakt/?subject=Session-Angebot"),
                    m.begriff("Veröffentlichung ohne Zusatzaufwand",
                              "Beschlüsse und Sitzungsunterlagen erscheinen automatisch nach dem offenen OParl-Standard, "
                              "maschinenlesbar statt in einer Insellösung. Transparenzpflichten erfüllen Sie im laufenden "
                              "Betrieb, und Presse wie Zivilgesellschaft können die Daten direkt weiterverwenden.",
                              marke="OParl 1.1"),
                    m.begriff("Bürgernähe, die keine Arbeit macht",
                              "Bürgerinnen und Bürger finden Beschlüsse, Vorlagen und Abstimmungen selbst — mit "
                              "Volltextsuche über alle Dokumente, ohne Anmeldung und ohne Tracking. Das entlastet "
                              "Verwaltung und Rat von Einzelanfragen, und für Ihre Kommune ist das Portal inklusive.",
                              marke="Bürgerportal mandari Insight", link_label="Insight ansehen", link_url="/insight/"),
                ],
                subline="Was im Verwaltungsalltag zählt – vom Ratsbüro bis zur Frage aus der Bürgerschaft.",
                anchor="bausteine",
                note="<p>Ein <a href=\"/ratsinformationssystem/\">Ratsinformationssystem</a> deckt die ganze digitale "
                     "Gremienarbeit ab: das Sitzungsmanagement der Verwaltung, das Gremieninformationssystem für "
                     "Ratsmitglieder und das Bürgerinformationssystem für die Öffentlichkeit. mandari bringt diese "
                     "Seiten auf einer Plattform zusammen.</p>",
            ),
            # Muster 5a: zwei Grundsatzentscheidungen, rechts die Eckdaten für die Prüfung
            m.randspalte(
                "Betrieb, den Ihre IT und Ihr Datenschutz mittragen",
                "<p><strong>Deutsches Hosting, DSGVO-konform.</strong> Alle Systeme laufen in deutschen Rechenzentren — "
                "ohne US-Cloud-Anbieter und ohne Übermittlung in Drittländer. Für Ihre Prüfung liegen der Mustervertrag "
                "zur Auftragsverarbeitung und die vollständige Liste der Unterauftragnehmer offen; gesichert wird "
                "täglich, gespeichert verschlüsselt.</p>"
                "<p><strong>Open Source heißt: kein Vendor-Lock-in.</strong> Der gesamte Quellcode steht unter "
                "AGPL-3.0, Ihre IT kann ihn jederzeit prüfen. Sie exportieren Ihre Daten in offenen Formaten und "
                "entscheiden selbst, ob Sie mandari betreiben oder betreiben lassen — unabhängig vom Anbieter und "
                "seinen Preisen.</p>",
                [
                    m.rand_fakten("Für Ihre Prüfung", ("Verschlüsselung", "AES-256-GCM je Mandant"),
                                  ("Sicherung", "täglich, 30 Tage aufbewahrt"),
                                  ("Datenexport", "OParl, CSV, JSON"), ("Lizenz", "AGPL-3.0")),
                    m.rand_links("Unterlagen", ("Trust Center", "/trust/"), ("Muster-AVV", "/avv/"),
                                 ("Open Source bei mandari", "/open-source/")),
                ],
                subline="Zwei Grundsatzentscheidungen, die Beschaffung und Prüfung einfacher machen.",
                anchor="betrieb",
            ),
            # Muster 8: zwei Wege der Anbindung
            m.vergleich(
                "Zwei Wege zur Anbindung",
                [("Mit OParl-Schnittstelle", "Der schnelle Weg"), ("Ohne OParl-Schnittstelle", "Der begleitete Weg")],
                [
                    ("Ihr RIS", ["spricht bereits OParl, etwa ALLRIS, regisafe, Somacos oder SD.NET RIM",
                                 "spricht noch kein OParl"]),
                    ("Ablauf", ["OParl-Endpunkt übermitteln, Test-Synchronisation, dann Produktivbetrieb",
                                "Vorbedingungen gemeinsam klären, Gespräche mit dem Anbieter koordinieren, Adapter "
                                "entwickeln – gegebenenfalls mit Förderung"]),
                    ("Dauer", ["typisch 1–2 Wochen", "nach gemeinsamer Klärung"]),
                    ("Erster Schritt", ["<a href=\"/kontakt/?subject=OParl-Anbindung\">Anbindung starten</a>",
                                        "<a href=\"/kontakt/?subject=Custom-Adapter\">Beratung anfragen</a>"]),
                ],
                subline="Entscheidend ist, ob Ihr bestehendes RIS bereits eine OParl-Schnittstelle hat.",
                anchor="anbindung",
            ),
            m.einladung(
                "Pilotkommunen gestalten mit.",
                "Sonderkonditionen, kurze Wege in die Entwicklung und die Übernahme Ihrer bestehenden Daten. Im "
                "Erstgespräch klären wir Anbindbarkeit, Zeitplan und Konditionen.",
                "Erstgespräch vereinbaren", "/kontakt/?subject=Pilot-Kommune#termin",
                link_label="Migration ansehen", link_url="/migration/",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                      ("Für Vergabestellen", "Unterlagen für die Vergabeakte", "/vergabe/"),
                      ("Im Vergleich", "RIS-Vergleich", "/vergleich/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # Unternehmensseiten: /unternehmen/, /karriere/, /presse/, /partner/,
        # /open-source/ — Inhalte in marketing/seeds_unternehmen.py
        # (/ueber-uns/ ist in /unternehmen/ aufgegangen, siehe setup_initial_pages)
        # ════════════════════════════════════════════════════════════
        **get_company_page_definitions(),

        # ════════════════════════════════════════════════════════════
        # /vergabe/ — Unterlagen für Beschaffung und Prüfung (B2G, Sie-Form)
        # ════════════════════════════════════════════════════════════
        "vergabe": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "Unterlagen für", "title_highlight": "Beschaffung und Prüfung",
                "subline": "Alles, was Sie für Markterkundung, Vergabe und Datenschutzprüfung brauchen, an einem Ort und ohne Anfrageformular.",
                "ctas": [cta("Muster-AVV", "/avv/", "file-signature", "primary"),
                         cta("Trust Center", "/trust/", "shield-check", "secondary")],
                "background_color": "primary",
            }),
            # Muster 3: eine Tabelle mit Stand statt 9 + 6 Kärtchen; Single Sign-on steht in der Roadmap
            m.register(
                "Unterlagen für Ihre Vergabeakte",
                [
                    m.gruppe("Datenschutz und Vertrag",
                             m.zeile("Muster-Auftragsverarbeitungsvertrag", "AVV nach Art. 28 DSGVO für Work und Session; "
                                     "unterschriftsreif mit Ihrem Organisationsnamen auf Anfrage", url="/avv/", status="da"),
                             m.zeile("Technische und organisatorische Maßnahmen", "Anlage zum AVV nach Art. 32 DSGVO: "
                                     "Vertraulichkeit, Integrität, Verfügbarkeit, Löschung",
                                     url="https://docs.mandari.de/datenschutz/tom/", ort="auf docs.mandari.de", status="da"),
                             m.zeile("Löschkonzept und Aufbewahrungsfristen", "Fristen je Mandant, auditierter Löschlauf, "
                                     "Betroffenenauskunft, Crypto-Shredding bei Vertragsende",
                                     url="https://docs.mandari.de/datenschutz/loeschkonzept/", ort="auf docs.mandari.de",
                                     status="da"),
                             m.zeile("Subprozessoren und Hosting-Stack", "Unterauftragsverarbeiter mit Standort und Zweck, "
                                     "Infrastruktur, Backup und Wiederherstellung", url="/trust/#subprocessors",
                                     ort="im Trust Center", status="da"),
                             m.zeile("Eigenerklärungen und Referenzblatt", "Ausschlussgründe und Eignung; Referenzen "
                                     "getrennt nach angebundenen Datenquellen und Kunden",
                                     url="https://github.com/mandariOSS/mandari/issues/101", ort="Fortschritt im Issue",
                                     status="offen")),
                    m.gruppe("Leistung und Preis",
                             m.zeile("Funktionsübersicht je Modul", "Grundlage Ihrer Leistungsbeschreibung, verfügbare und "
                                     "geplante Funktionen gekennzeichnet", url="/produkte/#funktionen", status="da"),
                             m.zeile("Leistungsbeschreibung je Modul", "Kriterienliste als DOCX und PDF, übernahmefähig in "
                                     "Ihre Vergabeunterlagen", url="https://github.com/mandariOSS/mandari/issues/94",
                                     ort="Fortschritt im Issue", status="offen"),
                             m.zeile("Preisblatt brutto und netto", "alle laufenden, einmaligen und optionalen Positionen, "
                                     "inklusive Session-Staffel und Support-Verträgen für On-Premises",
                                     url="https://github.com/mandariOSS/mandari/issues/100", ort="Fortschritt im Issue",
                                     status="offen"),
                             m.zeile("Service-Level-Vereinbarung", "Verfügbarkeit, Wartungsfenster, Störungsklassen, "
                                     "Reaktions- und Wiederherstellungszeiten, Gutschriften",
                                     url="https://github.com/mandariOSS/mandari/issues/93", ort="Fortschritt im Issue",
                                     status="offen")),
                    m.gruppe("Sicherheit, Betrieb und Zugänglichkeit",
                             m.zeile("Software-Stückliste (SBOM)", "Komponenten mit Versionen und Lizenzen für Ihre Lizenz- "
                                     "und Schwachstellenprüfung", url="https://docs.mandari.de/entwicklung/sbom/",
                                     ort="auf docs.mandari.de", status="da"),
                             m.zeile("Responsible Disclosure und security.txt", "Meldeweg für Sicherheitslücken nach RFC 9116 "
                                     "mit Reaktionsfristen", url="/sicherheit/disclosure/", status="da"),
                             m.zeile("Betriebs- und Self-Hosting-Dokumentation", "Installation, Konfiguration, Updates, "
                                     "Backups, Monitoring, Quellenanbindung", url="https://docs.mandari.de/betrieb/",
                                     ort="auf docs.mandari.de", status="da"),
                             m.zeile("Erklärung zur Barrierefreiheit", "Konformitätsstand und Feedbackweg; Prüfung nach "
                                     "BITV 2.0 für Session geplant für Q4/2026", url="/barrierefreiheit/", status="da"),
                             m.zeile("Externe Sicherheitsnachweise", "Penetrationstest mit veröffentlichter Zusammenfassung, "
                                     "IT-Grundschutz-Selbstbewertung", url="/trust/#audits", ort="Fahrplan im Trust Center",
                                     stand="Fahrplan", status="offen")),
                ],
                spalten=["Dokument", "Wofür Sie es brauchen", "Stand"],
                subline="Öffentlich, versioniert und ohne Registrierung. Was noch fehlt, steht mit seinem Stand in "
                        "derselben Liste.",
                bestand="{da} von {gesamt} liegen vor, {offen} sind in Arbeit.",
                stand="Stand 4. Oktober 2026",
                note="<p>Brauchen Sie ein Dokument früher, liefern wir eine Arbeitsfassung: "
                     "<a href=\"/kontakt/?subject=Vergabe\">Kontakt aufnehmen</a></p>",
                anchor="unterlagen",
            ),
            # Muster 5a: Stichworte im Text, rechts der Ausstieg als kleiner Ablauf
            m.randspalte(
                "Vertragsgrundlagen und Ausstieg",
                "<p><strong>Software.</strong> mandari steht vollständig unter der AGPL-3.0. Die Nutzung der Software "
                "ist lizenzkostenfrei, der Quellcode ist öffentlich. Das ist zugleich Ihre Absicherung gegen "
                "Anbieterausfall: Es braucht kein Software-Escrow, der Code liegt offen auf GitHub.</p>"
                "<p><strong>Betrieb.</strong> Für Managed Hosting gelten unsere <a href=\"/agb/\">AGB</a> und der "
                "<a href=\"/avv/\">AVV</a>. Vertragsschluss auf Basis Ihrer Vertragsmuster, etwa EVB-IT Cloud, "
                "prüfen wir gern im Einzelfall.</p>"
                "<p><strong>Ausstieg.</strong> Sie erhalten jederzeit einen vollständigen Export Ihrer Daten über OParl, "
                "CSV und JSON. Nach Vertragsende halten wir die Daten 30 Tage als Backup vor und löschen sie danach "
                "unwiderruflich, einschließlich des mandantenspezifischen Verschlüsselungsschlüssels.</p>"
                "<p><strong>Rechnungen.</strong> Rechnungen erhalten Sie elektronisch; die Angabe einer Leitweg-ID für "
                "XRechnung ist möglich.</p>",
                [
                    m.rand_ablauf("Ihr Ausstieg, Schritt für Schritt",
                                  ("bis Vertragsende", "vollständiger Export jederzeit: OParl, CSV, JSON"),
                                  ("Vertragsende", "die Daten liegen nur noch im Backup"),
                                  ("+30 Tage", "unwiderrufliche Löschung, auch des Schlüssels Ihres Mandanten")),
                    m.rand_links("Zum Nachlesen", ("AGB", "/agb/"), ("Muster-AVV", "/avv/"),
                                 ("Kündigung und Widerruf", "/kuendigung/")),
                    m.rand_text("<p>Eigene Vertragsmuster prüfen wir mit Ihnen: "
                                "<a href=\"mailto:hello@mandari.de?subject=Vergabe\">hello@mandari.de</a></p>"),
                ],
                anchor="vertragsgrundlagen",
            ),
            m.einladung(
                "Fragen zur Beschaffung?",
                "Wir beantworten Fragebögen, füllen Ihre Formulare aus und stellen Arbeitsfassungen fehlender "
                "Dokumente bereit. Antwort in der Regel innerhalb eines Werktags.",
                "Kontakt aufnehmen", "/kontakt/?subject=Vergabe",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                      ("Für die IT", "Trust Center", "/trust/"), ("Für Verwaltungen", "mandari Session", "/kommunen/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /roadmap/ — Verbindlichkeitsstufen, Swimlanes je Modul, Compliance, Änderungsprotokoll
        # ════════════════════════════════════════════════════════════
        "roadmap": [
            ("hero", {
                "badge_text": "", "badge_icon": "", "badge_color": "primary",
                "title": "mandari", "title_highlight": "Roadmap",
                "subline": "Was wir bauen, wann es kommt und wie verbindlich das ist. Stand 2. Oktober 2026, die nächste Aktualisierung folgt im Dezember; Verschiebungen nennen wir offen.",
                "subline_secondary": "Drei Verbindlichkeitsstufen: Zugesagt (im Angebot referenzierbar), Geplant (Zeitraum genannt, Änderungen möglich), In Prüfung (Idee ohne Termin).",
                "ctas": [cta("Meilensteine auf GitHub", "https://github.com/mandariOSS/mandari/milestones", "github", "primary"),
                         cta("Releases", "/releases/", "tag", "secondary")],
                "background_color": "primary",
            }),
            # Muster 3: was seit der letzten Roadmap geliefert wurde, mit Modul und Dokumentation
            m.register(
                "Neu seit Juli 2026",
                [m.gruppe("",
                    m.zeile("Anträge digital einreichen", "Fraktionen reichen Anträge direkt bei der Verwaltung ein und "
                            "erhalten Eingangsnummer, Status und Beratungstermine zurück.",
                            url="https://docs.mandari.de/work/antraege-einreichen/", ort="Dokumentation",
                            stand="Work und Session"),
                    m.zeile("Beschlusskontrolle und öffentliche Beschlussverfolgung", "Umsetzungsstand je Beschluss in "
                            "der Verwaltung, Sicht für Mandatsträger:innen und auf Wunsch öffentlich mit E-Mail-Abo.",
                            url="https://docs.mandari.de/session/beschlusskontrolle/", ort="Dokumentation",
                            stand="Session, Work, Insight"),
                    m.zeile("Abstimmungsergebnisse in der OParl-API", "Summen und namentliche Ergebnisse als "
                            "Vendor-Attribute, sichtbar im Bürgerportal.",
                            url="https://docs.mandari.de/session/oparl-api/", ort="API-Dokumentation",
                            stand="Session und Insight"),
                    m.zeile("Dokument-Cache und Quellen-Schonung", "Dokumente sind auch bei Ausfall des kommunalen "
                            "Systems verfügbar; Quellen mit Störungen werden automatisch geschont.",
                            url="https://docs.mandari.de/betrieb/dokument-cache/", ort="Dokumentation",
                            stand="Insight und Betrieb"),
                    m.zeile("Betriebsmonitor", "Zustand aller Quellen und Dienste im Admin, E-Mail-Alarme, "
                            "Datenstand-Hinweis im Bürgerportal.",
                            url="https://docs.mandari.de/betrieb/monitoring/", ort="Dokumentation", stand="Betrieb"),
                    m.zeile("Dokumentation auf docs.mandari.de", "Eigene Doku-Plattform mit Self-Hosting-Anleitung, "
                            "Konfigurationsreferenz, API-Referenzen, Datenschutzdokumenten. Ersetzt den geplanten "
                            "Self-Hosting-Guide.", url="https://docs.mandari.de/", ort="docs.mandari.de",
                            stand="Dokumentation"),
                )],
                spalten=["Geliefert", "Was sich ändert", "Modul"],
                subline="Was aus der letzten Roadmap umgesetzt wurde. Details in den Release-Notes und in der Dokumentation.",
                anchor="neu",
            ),
            # Muster 1a als Quartalsachse: Zeitpunkte als Spalten, Vorhaben mit Modul und Verbindlichkeit
            m.quartalsachse(
                "Was als Nächstes kommt",
                [
                    m.zeitpunkt(
                        "Q4/2026",
                        m.vorhaben("Pilotbetrieb mit ersten Kommunen", produkt="session", status="Zugesagt, Q3–Q4/2026",
                                   text="Sitzungsmanagement, Vorlagen, Protokolle und Beschlusskontrolle im "
                                        "Verwaltungsalltag. Pilotkonditionen auf der Preisseite.",
                                   link_label="Pilot-Kommune werden", link_url="/kontakt/?subject=Pilot-Kommune"),
                        m.vorhaben("Barrierefreiheit nach BITV 2.0", produkt="session", status="Zugesagt",
                                   text="Screenreader, Tastatur, Kontraste, Formulare; Selbstbewertung nach BITV 2.0 mit "
                                        "veröffentlichtem Prüfbericht. Eine unabhängige Prüfung ist in Prüfung.",
                                   link_label="Issue #44", link_url="https://github.com/mandariOSS/mandari/issues/44"),
                        m.vorhaben("Vergabeunterlagen", status="Zugesagt",
                                   text="Leistungsbeschreibung je Modul, Preisblatt brutto und netto, Eigenerklärungen, "
                                        "Referenzblatt. Erste Fassung der Seite ist online.",
                                   link_label="Vergabe und Unterlagen", link_url="/vergabe/"),
                        m.vorhaben("Code-Qualität und Frontend-Architektur", status="Zugesagt, bis Q1/2027",
                                   text="Sicherheits-Header und Content-Security-Policy in der Anwendung, echte Testgates, "
                                        "Komponentenbibliothek, Auslagerung von JavaScript und CSS, Typisierung, "
                                        "nachvollziehbare Lieferkette. Erste Schritte sind umgesetzt.",
                                   link_label="Epic ansehen", link_url="https://github.com/mandariOSS/mandari/issues/177"),
                        m.vorhaben("Release- und Support-Politik", status="Geplant",
                                   text="Versionierung, Kadenz, Fristen für Sicherheitsupdates, Stabilität der "
                                        "Schnittstellen, abonnierbare Sicherheitsmeldungen.",
                                   link_label="Issue #96", link_url="https://github.com/mandariOSS/mandari/issues/96"),
                        m.vorhaben("Adapter für Ratsinformationssysteme ohne OParl", produkt="insight",
                                   status="Geplant, 2026–2027",
                                   text="SessionNet läuft, ALLRIS über Bridge. Weitere Systeme folgen nach Reichweite und "
                                        "Machbarkeit, mit Rücksicht auf die kommunalen Server.",
                                   link_label="Epic ansehen", link_url="https://github.com/mandariOSS/mandari/issues/125"),
                    ),
                    m.zeitpunkt(
                        "Version 1.0",
                        m.vorhaben("Import aus Bestandssystemen", produkt="session", status="Geplant",
                                   text="OParl-Übernahme plus CSV für Personen und Gremienbesetzung, damit der Wechsel "
                                        "ohne Abtippen gelingt.",
                                   link_label="Issue #42", link_url="https://github.com/mandariOSS/mandari/issues/42"),
                        m.vorhaben("Geo-Verortung Ausbaustufe", produkt="insight", status="Geplant",
                                   text="Hausnummern, performante Umkreissuche, Korrektur-Workflow für falsch verortete "
                                        "Vorgänge.",
                                   link_label="Issue #54", link_url="https://github.com/mandariOSS/mandari/issues/54"),
                        m.vorhaben("Service-Level-Vereinbarung", status="Geplant",
                                   text="Verfügbarkeitszusage, Wartungsfenster, Störungsklassen, Reaktions- und "
                                        "Wiederherstellungszeiten, Gutschriften.",
                                   link_label="Issue #93", link_url="https://github.com/mandariOSS/mandari/issues/93"),
                        m.vorhaben("Mehr-Server-Betrieb", status="Geplant",
                                   text="Compose-Rollenprofile für getrennte Daten-, Web- und Worker-Server, Grundlage "
                                        "für Wachstum und dedizierte Instanzen.",
                                   link_label="Issue #55", link_url="https://github.com/mandariOSS/mandari/issues/55"),
                    ),
                    m.zeitpunkt(
                        "2027",
                        m.vorhaben("Version 1.0", status="Geplant",
                                   text="Externes Sicherheitsaudit, stabile Schnittstellen, SLA, Ende der Beta. Der "
                                        "Meilenstein bündelt die offenen Punkte.",
                                   link_label="Meilenstein 1.0", link_url="https://github.com/mandariOSS/mandari/milestone/4"),
                        m.vorhaben("Single Sign-on (SAML, OpenID Connect)", produkt="session", status="Geplant",
                                   text="Anmeldung über den Verzeichnisdienst der Verwaltung mit Rollenzuordnung aus Gruppen.",
                                   link_label="Issue #95", link_url="https://github.com/mandariOSS/mandari/issues/95"),
                        m.vorhaben("KI-Entwurf der Niederschrift", produkt="session", status="Geplant",
                                   text="Entwurf je Tagesordnungspunkt aus der Audioaufzeichnung, Transkription ohne "
                                        "Übermittlung in Drittländer, Nichtöffentliches nur mit selbst betriebenem "
                                        "Sprachmodell. Der Sitzungsdienst prüft und übernimmt.",
                                   link_label="Issue #180", link_url="https://github.com/mandariOSS/mandari/issues/180"),
                        m.vorhaben("Hybride und digitale Gremiensitzungen", produkt="session", status="Geplant",
                                   text="Sitzungsformat mit Landesprofil, Teilnahmeart und Live-Cockpit sind geliefert. Es "
                                        "folgen Abstimmung am eigenen Gerät mit zertifizierungsfähigem Modul, Rednerliste, Saalanzeige, "
                                        "Videokonferenz-Anbindung, Livestream mit Sprungmarken und automatische "
                                        "Niederschriftsvermerke.",
                                   link_label="Epic ansehen", link_url="https://github.com/mandariOSS/mandari/issues/156"),
                        m.vorhaben("Vollständige Ratsarbeit", produkt="session", status="Geplant",
                                   text="Vorlagenarten mit Nummernkreisen und Word-Import, Mitzeichnung mit parallelen "
                                        "Stationen, Veröffentlichungsfassung mit Schwärzung, Räume und Ressourcen, Eingang von "
                                        "Anfragen und Eingaben, Sitzungsgeld mit Fahrtkosten und Verdienstausfall, "
                                        "elektronische Signatur, E-Akte-Übergabe.",
                                   link_label="Vorhaben #496 ansehen", link_url="https://github.com/mandariOSS/mandari/issues/496"),
                        m.vorhaben("Native App für Android und iOS", produkt="insight", status="Geplant",
                                   text="Termine, Vorlagen, Suche und Benachrichtigungen aufs Smartphone; später "
                                        "Mandatsträger-Modus mit Offline-Sitzungsmappen.",
                                   link_label="Epic ansehen", link_url="https://github.com/mandariOSS/mandari/issues/113"),
                        m.vorhaben("mandari Data: Open-Data-Plattform", produkt="insight", status="Geplant",
                                   text="Offene Daten jeder Art (Tabellen, Geodaten, Dokumente, Dienste, Sensordaten) mit "
                                        "Daten-APIs, Redaktionsworkflow, DCAT-AP.de und GovData-Anbindung. Ratsdaten "
                                        "fließen automatisch ein.",
                                   link_label="Epic ansehen", link_url="https://github.com/mandariOSS/mandari/issues/112"),
                        m.vorhaben("Livestream und Video mit Sprungmarken", produkt="insight", status="Geplant",
                                   text="Livestream und Aufzeichnungen je Tagesordnungspunkt im Bürgerportal, Teil des "
                                        "Vorhabens „Hybride und digitale Gremiensitzungen“.",
                                   link_label="Issue #146", link_url="https://github.com/mandariOSS/mandari/issues/146"),
                        m.vorhaben("Externer Penetrationstest", status="Geplant",
                                   text="Prüfung von Web, API, Anmeldung und Mandantentrennung, Zusammenfassung im Trust "
                                        "Center, SBOM automatisiert je Release.",
                                   link_label="Issue #97", link_url="https://github.com/mandariOSS/mandari/issues/97"),
                    ),
                    m.zeitpunkt(
                        "Nach 1.0",
                        m.vorhaben("Vorlagen in einfacher Sprache", produkt="insight", status="In Prüfung",
                                   text="KI-Kurzfassung in einfacher Sprache, klar als solche gekennzeichnet.",
                                   link_label="Issue #51", link_url="https://github.com/mandariOSS/mandari/issues/51"),
                        satz="ohne Termin",
                    ),
                ],
                subline="Session ist unser Kerngeschäft: Hier liegt der Fokus bis zur Version 1.0. Die Farbe zeigt das "
                        "Modul, der Zusatz die Verbindlichkeit.",
                anchor="plan",
            ),
            *seeds_vergleich.roadmap_luecken(),
            # Muster 5b: Datum in der Marginalie, Änderungen daneben
            m.begriffe_aus_html(
                "Was sich an der Roadmap geändert hat",
                (
                    "<h3>Oktober 2026</h3>"
                    "<ul>"
                    "<li><strong>Marktvergleich:</strong> Funktionen, die etablierte Ratsinformationssysteme bieten und mandari noch nicht, sind jetzt der Roadmap zugeordnet: die zugesagten und geplanten in den Karten oben, acht neue in Prüfung im Abschnitt „Aus dem Marktvergleich“: eigener Bereich für Ratsmitglieder, Freigabe unterwegs, Umlaufverfahren mit Stimmabgabe online, Mitteilungen an das Finanzamt, Bekanntmachung und Amtsblatt, Einbindung in die Website der Kommune, Saaltechnik und KI-Schreibhilfe im Sitzungsdienst.</li>"
                    "<li><strong>Barrierefreiheit Session:</strong> präzisiert. Zugesagt für Q4/2026 ist die Selbstbewertung nach BITV 2.0 mit veröffentlichtem Prüfbericht; eine Prüfung durch eine unabhängige Stelle ist in Prüfung.</li>"
                    "<li><strong>KI-Entwurf der Niederschrift:</strong> von „In Prüfung, nach 1.0“ auf „Geplant 2027“, weil der Protokollentwurf (#180) zum Vorhaben „Vollständige Ratsarbeit“ (#496) gehört.</li>"
                    "<li><strong>Livestream mit Sprungmarken:</strong> von „In Prüfung, nach 1.0“ auf „Geplant 2027“, gleichgezogen mit dem Vorhaben „Hybride und digitale Gremiensitzungen“.</li>"
                    "<li><strong>Hybride Sitzungen:</strong> Sitzungsformat, Teilnahmeart und Live-Cockpit sind geliefert.</li>"
                    "</ul>"
                    "<h3>September 2026, gegenüber Juli 2026</h3>"
                    "<ul>"
                    "<li><strong>Self-Hosting-Guide (Q3/2026):</strong> geliefert, in erweiterter Form als eigene Dokumentationsplattform docs.mandari.de.</li>"
                    "<li><strong>OParl-Adapter erweitern:</strong> läuft weiter und wird zum Programm „Adapter für Ratsinformationssysteme ohne OParl“ mit eigenem Epic ausgebaut.</li>"
                    "<li><strong>WCAG-AA-Audit (Q4/2026):</strong> unverändert, jetzt als Zusage für Session; Insight und Work folgen 2026/27.</li>"
                    "<li><strong>i18n Englisch:</strong> zurückgestellt auf „In Prüfung“. Deutsche Kommunen sind unser Markt, Englisch bringt aktuell keinen Kundennutzen.</li>"
                    "<li><strong>Neu aufgenommen:</strong> Vergabeunterlagen, SLA, Release-Politik, Single Sign-on, Penetrationstest, Open-Data-Plattform, native App, hybride Gremiensitzungen, vollständige Ratsarbeit, Code-Qualität.</li>"
                    "<li><strong>Selbst-Abstimmung am eigenen Gerät:</strong> aus „In Prüfung“ in das Epic „Hybride Sitzungen“ überführt und dort mit hoher Priorität geplant.</li>"
                    "<li><strong>Open-Data-Portal:</strong> präzisiert zur vollwertigen Plattform für alle Verwaltungsdaten, nicht nur Ratsdaten.</li>"
                    "<li><strong>Version 1.0:</strong> bleibt bei 2027; ein konkretes Quartal nennen wir, sobald der Pilotbetrieb läuft.</li>"
                    "</ul>"
                    "<h3>Was wir bewusst nicht bauen</h3>"
                    "<ul>"
                    "<li>Kein Windows-Installer für den Eigenbetrieb; unterstützt wird Docker Compose auf Linux.</li>"
                    "<li>Keine Bezahlschranken für Sicherheitsfunktionen wie Zwei-Faktor-Authentifizierung, Verschlüsselung oder Audit-Log.</li>"
                    "<li>Kein Tracking und keine Werbung im Bürgerportal, auch nicht in der App.</li>"
                    "<li>Keine proprietären Erweiterungen: alles, was wir bauen, erscheint unter AGPL-3.0.</li>"
                    "</ul>"
                ),
                anchor="aenderungen",
            ),
            m.einladung(
                "Fehlt etwas?",
                "Kommunen und Fraktionen, die mandari einsetzen, gestalten die Roadmap mit. Erstellen Sie ein Issue, "
                "kommentieren Sie bestehende Vorschläge oder schreiben Sie uns direkt.",
                "Issue erstellen", "https://github.com/mandariOSS/mandari/issues/new",
                link_label="Direkt schreiben", link_url="/kontakt/?subject=Roadmap-Idee",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Nächste Aktualisierung", "Dezember 2026", ""),
                      ("Meilensteine", "auf GitHub", "https://github.com/mandariOSS/mandari/milestones"),
                      ("Was geliefert ist", "Releases", "/releases/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /vergleich/ + /vergleich/mandari-vs-<anbieter>/ — Daten und
        # Aufbau in marketing/seeds_vergleich.py.
        # ════════════════════════════════════════════════════════════
        "vergleich": seeds_vergleich.uebersichtsseite(),
        **{slug: seeds_vergleich.anbieterseite(slug) for slug in seeds_vergleich.ANBIETER},
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
                "subline": "mandari aggregiert öffentliche Daten aus Ratsinformationssystemen deutscher Kommunen. Hier eine vollständige Übersicht aller Quellen, Lizenzen und eingesetzten Standards.",
                "ctas": [], "background_color": "primary",
            }),
            ("richtext_section", {
                "header": hdr(title="Ratsinformationen aus OParl-Schnittstellen"),
                "background": "white",
                "body": "<p>mandari nutzt den offenen Standard <a href=\"https://oparl.org/\" target=\"_blank\" rel=\"noopener\">OParl</a> (Versionen 1.0 und 1.1), um Daten aus den Ratsinformationssystemen deutscher Kommunen strukturiert abzurufen. Es werden ausschließlich öffentlich zugängliche Daten verarbeitet.</p><p>Die jeweilige Kommune bleibt rechtlich verantwortliche Stelle für die bereitgestellten Inhalte. mandari nimmt keine inhaltlichen Veränderungen vor und verlinkt grundsätzlich auf die Originalquelle.</p><p>Wie unser Crawler die Daten abruft, welche Regeln er einhält und wie Kommunen Kontakt aufnehmen können, steht auf der Seite <a href=\"/crawler/\">Über unseren Crawler</a>.</p><p><a href=\"/insight/\">Alle Kommunen im Bürgerportal</a></p>",
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
                "body": "<p>Stand: <strong>20. Juli 2026</strong>. Bei Fehlern oder fehlenden Nachweisen: <a href=\"mailto:hello@mandari.de\">hello@mandari.de</a>.</p>",
            }),
        ],
    }


def _release_section(title, body):
    """Abschnitt einer Release-Seite: Zwischenüberschrift + Fließtext (gerendert von blog/release.html)."""
    return ("richtext_section", {"header": hdr(title=title), "background": "white", "body": body})


def get_release_definitions() -> dict:
    """Release-Seiten (blog.ReleasePage) → Meta-Felder + body StreamField.

    Struktur pro Slug: {"meta": {...}, "blocks": [...]}.
    Neue Releases werden hier einfach als weiterer Eintrag ergänzt —
    `setup_initial_pages` legt fehlende ReleasePages unter /releases/ an,
    `refresh_seeded_page <slug> --force` aktualisiert bestehende.

    Release-Seiten erklären eine Version für Laien: was neu ist und für wen, in
    Sie-Form. Technische Update-Hinweise für den Selbstbetrieb und Details zu
    Sicherheitskorrekturen stehen nur in den Release-Notes auf GitHub.
    """

    return {
        # ════════════════════════════════════════════════════════════
        # /releases/mandari-0-11/ — mandari 0.11, 27.09.2026
        # ════════════════════════════════════════════════════════════
        "mandari-0-11": {
            "meta": {
                "title": "mandari 0.11",
                "version": "0.11.0",
                "release_type": "minor",
                "release_date": "2026-09-27",
                "github_url": "https://github.com/mandariOSS/mandari/releases/tag/v0.11.0",
                "breaking_changes": False,
                "seo_title": "mandari 0.11 – Release-Notes",
                "search_description": (
                    "mandari 0.11 vom 27. September 2026: gemeinsame Sitzungen, geschützte "
                    "Niederschriften, Rückmeldungen zu Anträgen und Umkreissuche im Bürgerportal."
                ),
            },
            "blocks": [
                _release_section("Das Wichtigste in Kürze", (
                    "<p>mandari 0.11 ist das erste Release nach der Beta vom Juli. Es bringt vor allem den "
                    "Sitzungsdienst voran: mandari Session begleitet eine Sitzung jetzt von der Ladung bis zur "
                    "genehmigten Niederschrift. Fraktionen sehen in mandari Work, was aus ihren Anträgen wird, "
                    "und das Bürgerportal findet Vorgänge in Ihrer Nachbarschaft.</p>"
                    "<p>Alle Neuerungen liefen vor der Veröffentlichung bereits im Betrieb. Eine eigene "
                    "Version 0.10 gibt es nicht, ihre Inhalte sind in 0.11 aufgegangen.</p>"
                )),
                _release_section("Für Verwaltungen: mandari Session", (
                    "<ul>"
                    "<li>Gemeinsame Sitzungen mehrerer Gremien. Mehrere Körperschaften lassen sich als Gruppe "
                    "mit einer gemeinsamen Leitstelle führen.</li>"
                    "<li>Ladungen mit Empfangsbestätigung und Rückmeldung. Den Zustellweg legen Sie für jede "
                    "Person fest.</li>"
                    "<li>Nach der Genehmigung ist die Niederschrift geschützt. Korrekturen laufen als "
                    "nachvollziehbare Berichtigung, die öffentliche Fassung erscheint im Bürgerportal und in "
                    "der OParl-Schnittstelle.</li>"
                    "<li>Vorlagen und Anlagen behalten jede Fassung – mit Vergleich und Wiederherstellung.</li>"
                    "<li>Freigaben und Genehmigungen nach dem Vier-Augen-Prinzip, mit Vertretungen.</li>"
                    "<li>Die Sitzungsmappe als ein PDF oder ZIP-Archiv, eigene Nummernkreise für Vorlagen und "
                    "Drucksachen.</li>"
                    "<li>Jede Änderung wird lückenlos und manipulationssicher protokolliert, mit Prüfexport "
                    "und Archiv.</li>"
                    "<li>Neue Mandanten sind mit einem Assistenten in wenigen Schritten arbeitsfähig.</li>"
                    "</ul>"
                )),
                _release_section("Für Fraktionen: mandari Work", (
                    "<p>Ihre Fraktion sieht direkt in mandari Work, was die Verwaltung aus einem eingereichten "
                    "Antrag macht: Vorlagennummer, Beratungsfolge und Beschluss. Neue Mitglieder registrieren "
                    "sich selbst, die Fraktion gibt den Zugang frei. Die Anmeldung schützt ein zweiter Faktor – "
                    "ein Code aus einer App oder ein Sicherheitsschlüssel.</p>"
                )),
                _release_section("Für Bürger:innen: das Bürgerportal", (
                    "<p>Jede Körperschaft hat im <a href=\"/insight/\">Bürgerportal</a> einen eigenen "
                    "Einstieg. Neue Kommunen werden automatisch auf der Karte verortet, bis zur Hausnummer, "
                    "und die Umkreissuche findet Vorgänge rund um Ihre Adresse. Das Portal liest jetzt auch "
                    "Ratsinformationssysteme, die noch den älteren Standard OParl 1.0 verwenden.</p>"
                )),
                _release_section("Sicherheit und Betrieb", (
                    "<p>Rechte und Sichtbarkeit prüft mandari in allen Portalen und Schnittstellen "
                    "durchgängig auf dem Server, sensible Einstellungen liegen verschlüsselt. Updates spielen "
                    "wir mit automatischer Prüfung und Rückfall ein, Schlüssel wechseln wir ohne "
                    "Ausfallzeit.</p>"
                )),
                _release_section("Alle Änderungen im Detail", (
                    "<p>Die vollständige Liste steht im "
                    "<a href=\"https://github.com/mandariOSS/mandari/blob/main/CHANGELOG.md\">Changelog</a>. "
                    "Wenn Sie mandari selbst betreiben, finden Sie die Hinweise für das Update in den "
                    "<a href=\"https://github.com/mandariOSS/mandari/releases/tag/v0.11.0\">Release-Notes "
                    "auf GitHub</a>.</p>"
                )),
            ],
        },
        # ════════════════════════════════════════════════════════════
        # /releases/mandari-0-9-beta/ — mandari 0.9 (Beta), 19.07.2026
        # ════════════════════════════════════════════════════════════
        "mandari-0-9-beta": {
            "meta": {
                "title": "mandari 0.9 (Beta)",
                "version": "0.9.0-beta",
                "release_type": "beta",
                "release_date": "2026-07-19",
                "github_url": "https://github.com/mandariOSS/mandari/releases/tag/v0.9.0-beta",
                "breaking_changes": False,
                "seo_title": "mandari 0.9 (Beta) – Release-Notes",
                "search_description": (
                    "mandari 0.9 (Beta) vom 19. Juli 2026: drei Produkte, OParl-Schnittstelle mit "
                    "Tombstones, Karte, gemeinsamer Editor und Zwei-Faktor-Anmeldung."
                ),
            },
            "blocks": [
                _release_section("Das Wichtigste in Kürze", (
                    "<p>mandari 0.9 ist das erste öffentlich versionierte Release, veröffentlicht am "
                    "19. Juli 2026. Es bündelt den Stand aller drei Produkte – Bürgerportal, Fraktionsarbeit "
                    "und Sitzungsdienst – mit einer offenen OParl-Schnittstelle und der Sicherheitsausstattung "
                    "der Plattform. Die Funktionen sind im Einsatz, einzelne Bereiche verfeinern wir bis zur "
                    "Version 1.0.</p>"
                )),
                _release_section("Für Bürger:innen: das Bürgerportal", (
                    "<p>Das <a href=\"/insight/\">Bürgerportal</a> macht Ratsinformationen ohne Anmeldung und "
                    "ohne Tracking zugänglich. Die Volltextsuche versteht kommunale Begriffe und verzeiht "
                    "Tippfehler, eingescannte Sitzungsdokumente werden automatisch lesbar. Eine Karte zeigt "
                    "Vorgänge in Ihrer Nachbarschaft, jede Kommune hat eigene Seiten.</p>"
                )),
                _release_section("Für Fraktionen: mandari Work", (
                    "<p>Fraktionen bereiten Sitzungen gemeinsam vor – mit Positionen, Notizen und Diskussion "
                    "in Echtzeit. Anträge durchlaufen eine Antragsdatenbank mit Status, Fristen, Checklisten "
                    "und Freigaben. Im gemeinsamen Editor schreiben mehrere Personen zugleich, mit "
                    "Versionshistorie und Export im eigenen Briefkopf. Gastzugänge und ein modulares "
                    "Rechtesystem halten jede Fraktion strikt getrennt.</p>"
                )),
                _release_section("Für Verwaltungen: mandari Session", (
                    "<p>Der Sitzungsdienst verwaltet Sitzungen, Vorlagen und Drucksachen, Anträge und "
                    "Tagesordnungen. Niederschriften durchlaufen eine Genehmigung, Anwesenheit und "
                    "Sitzungsgelder sind erfasst, jede Änderung steht im Protokoll.</p>"
                )),
                _release_section("Offene Schnittstelle: OParl mit Tombstones", (
                    "<p>mandari stellt die zusammengeführten Daten selbst als OParl-1.1-Schnittstelle bereit: "
                    "<a href=\"https://oparl.mandari.de/oparl/v1/system\">oparl.mandari.de</a>. Tombstones "
                    "markieren zurückgezogene Objekte, damit nachnutzende Systeme Löschungen nachvollziehen "
                    "können. Enthalten sind alle zwölf OParl-Objekttypen, seitenweise Abfragen und der Filter "
                    "modified_since.</p>"
                )),
                _release_section("Sicherheit und Betrieb", (
                    "<p>Sensible Inhalte verschlüsselt mandari je Mandant (AES-256-GCM). Die Anmeldung "
                    "unterstützt einen zweiten Faktor, aktive Sitzungen lassen sich verwalten, öffentliche "
                    "Schnittstellen begrenzen die Zahl der Anfragen.</p>"
                )),
                _release_section("Alle Änderungen im Detail", (
                    "<p>Die vollständigen Release-Notes und den Quellcode finden Sie "
                    "<a href=\"https://github.com/mandariOSS/mandari/releases/tag/v0.9.0-beta\">auf GitHub</a>. "
                    "Wie es weitergeht, zeigt die <a href=\"/roadmap/\">Roadmap</a>.</p>"
                )),
            ],
        },
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
        from marketing.management.commands.setup_initial_pages import seeded_custom_template

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
            # Standard-Template, außer der Seed nennt ein eigenes (MARKETING_PAGE_META)
            page.custom_template = seeded_custom_template(slug)
            page.save()
            page.save_revision().publish()

            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {slug}/ - {len(blocks_data)} Blöcke (custom_template '{old_template}' → '{page.custom_template}')"
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
