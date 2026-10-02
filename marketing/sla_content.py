"""
Zentrale Quelle für das Service Level Agreement (SLA) des Managed Hosting.

Die verbindliche Fassung liegt im Hauptrepository unter
`mandariOSS/mandari/docs/SLA.md`. Dieses Modul hält die für die Website
gegliederte Fassung an genau einer Stelle, damit

  * der StreamField-Seed der Seite /sla/ (`migrate_pages_to_streamfield`),
  * die druckoptimierte Ansicht /sla/druck/ (`marketing/sla_print.html`) und
  * das PDF-Skript `scripts/build_sla_pdf.py`

denselben Text ausspielen. Änderungen am SLA gehören zuerst in docs/SLA.md
des Hauptrepos und werden dann hier mit neuer Versionsnummer nachgezogen.
Keine Preise, keine Infrastrukturdetails.
"""

SLA_VERSION = "1.0"
SLA_DATE = "17.09.2026"
SLA_DATE_ISO = "2026-09-17"

# Ablage der PDF-Fassung unterhalb von static/ (ausgeliefert unter STATIC_URL).
SLA_PDF_FILENAME = f"mandari-sla-v{SLA_VERSION}.pdf"
SLA_PDF_URL = f"/wstatic/downloads/{SLA_PDF_FILENAME}"

SLA_SOURCE_URL = "https://github.com/mandariOSS/mandari/blob/dev/docs/SLA.md"
STATUS_PAGE_URL = "https://status.mandari.de"

SLA_INTRO = (
    "Vertragsanlage „Service Level“ für Kunden im Managed Hosting. Grundlage sind das "
    "Verfügbarkeitskonzept und die seit September 2026 laufende Messung über die Statusseite."
)

# Abschnitte in Reihenfolge: (Nummer, Anker, Titel, HTML-Body)
SLA_SECTIONS = [
    {
        "number": "1",
        "anchor": "geltungsbereich",
        "title": "Geltungsbereich",
        "body": (
            "<p>Gilt für die vom Betreiber gehosteten Instanzen von mandari work, mandari session und dem "
            "Bürgerportal einschließlich OParl-API. Nicht erfasst sind Selbst-Hosting, Testinstanzen, "
            "Vorschau-Funktionen („Beta“) und Drittsysteme (Ratsinformationssysteme der Kommunen, "
            "Mailversand über kundeneigene Server, Videokonferenzdienste).</p>"
        ),
    },
    {
        "number": "2",
        "anchor": "verfuegbarkeit",
        "title": "Verfügbarkeit",
        "body": (
            "<table>"
            "<thead><tr><th>Stufe</th><th>Zusage je Kalendermonat</th><th>Messung</th></tr></thead>"
            "<tbody>"
            "<tr><td><strong>Standard</strong></td><td><strong>99,5 %</strong></td>"
            f'<td>Statusseite <a href="{STATUS_PAGE_URL}" rel="noopener" target="_blank">status.mandari.de</a>, '
            "Prüfintervall 60 s</td></tr>"
            "<tr><td><strong>Premium</strong></td><td><strong>99,7 %</strong></td>"
            "<td>wie Standard, zusätzlich 24/7-Bereitschaft für Klasse 1</td></tr>"
            "<tr><td><strong>Enterprise</strong></td><td><strong>99,9 %</strong></td>"
            "<td>wie Premium, mit zweitem Standort</td></tr>"
            "</tbody></table>"
            "<h3>Messregel</h3>"
            "<p>Ein Dienst gilt als nicht verfügbar, wenn zwei aufeinanderfolgende Prüfungen der Statusseite "
            "scheitern; die Ausfallzeit beginnt mit der ersten gescheiterten Prüfung und endet mit der ersten "
            "erfolgreichen. Einzelne fehlgeschlagene Prüfungen zählen als Prüfintervall, nicht als Ausfall. "
            "Der Monatswert ist <em>(Minuten im Monat − Ausfallminuten − ausgenommene Minuten) / "
            "(Minuten im Monat − ausgenommene Minuten)</em>. Gemessen werden die Anmeldeseite von mandari work, "
            "die Sitzungsübersicht von mandari session, die Startseite des Bürgerportals und der "
            "OParl-Systemendpunkt.</p>"
            "<h3>Ausnahmen</h3>"
            "<p>Ausgenommen sind angekündigte Wartungsfenster (Abschnitt 3), höhere Gewalt, Ausfälle von "
            "Vorleistungen außerhalb des Einflusses des Betreibers (Netzanbindung des Rechenzentrums, "
            "DNS-Registrare), Störungen durch den Kunden (Fehlkonfiguration, Sperrung durch eigene Firewalls, "
            "Überlast durch kundeneigene Skripte) sowie Angriffe, die den Dienst trotz angemessener "
            "Schutzmaßnahmen beeinträchtigen.</p>"
            "<h3>Warum 99,5 % und nicht mehr für Standard</h3>"
            "<p>99,5 % entsprechen 3,6 Stunden je Monat. Der heutige Betrieb (ein Standort, Sicherung an zwei "
            "Standorten, Deploy mit Rückfall) erreicht das mit Messung belegbar; 99,9 % (44 Minuten je Monat) "
            "setzen einen zweiten Standort voraus und sind deshalb der Enterprise-Stufe vorbehalten.</p>"
        ),
    },
    {
        "number": "3",
        "anchor": "wartungsfenster",
        "title": "Wartungsfenster",
        "body": (
            "<ul>"
            "<li><strong>Regelfenster:</strong> Dienstag und Donnerstag, 05:00–06:00 Uhr (Europe/Berlin).</li>"
            "<li>Wartungen werden mindestens <strong>48 Stunden</strong> vorher auf der Statusseite angekündigt; "
            "Wartungen mit Unterbrechung über zehn Minuten zusätzlich per Mail.</li>"
            "<li>Sicherheitskorrekturen der Klassen „kritisch“ und „hoch“ dürfen außerhalb des Fensters mit "
            "kürzerer Ankündigung eingespielt werden; sie zählen nicht als Ausfall, wenn die Unterbrechung "
            "unter fünf Minuten bleibt.</li>"
            "<li>Nicht in Wartungsfenster fallen Sitzungstage, die der Kunde bis 14 Tage vorher im Kundenportal "
            "hinterlegt hat.</li>"
            "</ul>"
        ),
    },
    {
        "number": "4",
        "anchor": "stoerungsklassen",
        "title": "Störungsklassen, Reaktion und Wiederherstellung",
        "body": (
            "<table>"
            "<thead><tr><th>Klasse</th><th>Beschreibung</th><th>Reaktion Standard</th>"
            "<th>Reaktion Premium/Enterprise</th><th>Wiederherstellungsziel</th></tr></thead>"
            "<tbody>"
            "<tr><td><strong>1 – Ausfall</strong></td>"
            "<td>Dienst für alle Nutzer nicht erreichbar; Datenverlust droht; Sicherheitsvorfall</td>"
            "<td>1 Stunde (Servicezeit)</td><td>30 Minuten (24/7)</td><td>4 Stunden</td></tr>"
            "<tr><td><strong>2 – Erhebliche Störung</strong></td>"
            "<td>Kernfunktion (Sitzungsmappe, Abstimmung, Editor, Ladung) unbenutzbar, Umgehung nicht möglich</td>"
            "<td>4 Stunden</td><td>2 Stunden</td><td>1 Werktag</td></tr>"
            "<tr><td><strong>3 – Störung</strong></td>"
            "<td>Einschränkung mit Umgehung, Darstellungsfehler, einzelne Nutzer betroffen</td>"
            "<td>1 Werktag</td><td>4 Stunden</td><td>nächstes Release</td></tr>"
            "</tbody></table>"
            "<p>Reaktion heißt: qualifizierte Rückmeldung mit Einschätzung und nächstem Schritt. "
            "Wiederherstellung heißt: Dienst benutzbar, ggf. mit Umgehung; die endgültige Korrektur folgt "
            'nach <a href="https://mandari.de/releases/#release-politik">Release-Politik</a>.</p>'
        ),
    },
    {
        "number": "5",
        "anchor": "datensicherung",
        "title": "Datensicherung, RPO und RTO",
        "body": (
            "<table>"
            "<thead><tr><th>Kennzahl</th><th>Zusage</th><th>Grundlage</th></tr></thead>"
            "<tbody>"
            "<tr><td><strong>Sicherung</strong></td>"
            "<td>täglich, verschlüsselt, an zwei getrennten Standorten, 30 Tage Aufbewahrung</td>"
            "<td>wöchentliche Integritätsprüfung, monatlicher Wiederherstellungstest</td></tr>"
            "<tr><td><strong>RPO</strong> (höchstens verlorene Daten)</td>"
            "<td><strong>24 Stunden</strong> (Standard/Premium); <strong>1 Stunde</strong> Enterprise</td>"
            "<td>Enterprise setzt die stündliche Replikation aus dem Verfügbarkeitskonzept voraus</td></tr>"
            "<tr><td><strong>RTO</strong> (Wiederanlauf nach Totalverlust des Standorts)</td>"
            "<td><strong>8 Stunden</strong> Standard, <strong>4 Stunden</strong> Premium/Enterprise</td>"
            "<td>Datenbankwiederherstellung aus dem Offsite-Backup gemessen unter fünf Minuten; der vollständige "
            "Neuaufbau wird in der Notfallübung gemessen und die Zahl danach geschärft</td></tr>"
            "</tbody></table>"
        ),
    },
    {
        "number": "6",
        "anchor": "servicezeiten",
        "title": "Servicezeiten und Kanäle",
        "body": (
            "<table>"
            "<thead><tr><th>Stufe</th><th>Servicezeit</th><th>Kanäle</th></tr></thead>"
            "<tbody>"
            "<tr><td>Standard</td>"
            "<td>Mo–Fr 08:00–17:00 Uhr (Europe/Berlin), außer gesetzliche Feiertage NRW</td>"
            '<td>Kundenportal (Ticket), E-Mail <a href="mailto:support@mandari.de">support@mandari.de</a></td></tr>'
            "<tr><td>Premium</td><td>Mo–Fr 07:00–19:00 Uhr; Klasse 1 zusätzlich 24/7</td>"
            "<td>zusätzlich Bereitschaftsnummer</td></tr>"
            "<tr><td>Enterprise</td>"
            "<td>wie Premium; benannte Ansprechperson; Sitzungstag-Begleitung auf Anfrage</td>"
            "<td>zusätzlich direkter Kanal zur Ansprechperson</td></tr>"
            "</tbody></table>"
            "<h3>Eskalation</h3>"
            "<p>Stufe 1 Support → Stufe 2 Betrieb/Entwicklung (nach Ablauf der halben Wiederherstellungszeit) "
            "→ Stufe 3 Geschäftsführung (nach Ablauf der Wiederherstellungszeit). Der Kunde kann jede Stufe "
            "über das Ticket anfordern.</p>"
        ),
    },
    {
        "number": "7",
        "anchor": "gutschriften",
        "title": "Gutschriften",
        "body": (
            "<p>Unterschreitet die gemessene Monatsverfügbarkeit die Zusage, erhält der Kunde auf Antrag "
            "(binnen 30 Tagen nach Monatsende) eine Gutschrift auf das Monatsentgelt der betroffenen Instanz:</p>"
            "<table>"
            "<thead><tr><th>Gemessene Verfügbarkeit</th><th>Gutschrift</th></tr></thead>"
            "<tbody>"
            "<tr><td>unter Zusage, mindestens 99,0 %</td><td>10 %</td></tr>"
            "<tr><td>unter 99,0 %, mindestens 98,0 %</td><td>25 %</td></tr>"
            "<tr><td>unter 98,0 %</td><td>50 %</td></tr>"
            "</tbody></table>"
            "<p>Gutschriften sind der einzige Anspruch aus einer Unterschreitung; weitergehende gesetzliche "
            "Rechte bei grober Fahrlässigkeit oder Vorsatz bleiben unberührt. Die Abwicklung erfolgt bis zur "
            "Automatisierung manuell über das Kundenportal (Ticket, Vermerk auf der Folgerechnung).</p>"
        ),
    },
    {
        "number": "8",
        "anchor": "berichtswesen",
        "title": "Berichtswesen",
        "body": (
            "<ul>"
            f'<li>Die <a href="{STATUS_PAGE_URL}" rel="noopener" target="_blank">Statusseite</a> zeigt die '
            "gemessene Verfügbarkeit der letzten 24 Stunden, 7 und 30 Tage je Dienst öffentlich.</li>"
            "<li>Monatlich erstellt der Betreiber einen Verfügbarkeitsbericht je Dienst mit Gesamtverfügbarkeit, "
            "Störungen (Beginn, Ende, Klasse, Ursache, Maßnahme) und Wartungen; Premium- und Enterprise-Kunden "
            "erhalten ihn im Kundenportal.</li>"
            "<li>Störungen der Klasse 1 erhalten binnen fünf Werktagen einen Störungsbericht (Ursache, "
            "Auswirkung, Abhilfe, Vorbeugung).</li>"
            "</ul>"
        ),
    },
    {
        "number": "9",
        "anchor": "mitwirkung",
        "title": "Voraussetzungen und Mitwirkung",
        "body": (
            "<p>Der Kunde benennt eine Kontaktadresse für Störungs- und Wartungsmeldungen, hält Sitzungstage im "
            "Kundenportal aktuell, nutzt unterstützte Browser (jeweils aktuelle und vorherige Hauptversion von "
            "Firefox, Chrome, Edge, Safari) und meldet Störungen über die genannten Kanäle mit Zeitpunkt, "
            "betroffener Funktion und Beispiel.</p>"
        ),
    },
    {
        "number": "10",
        "anchor": "pflege",
        "title": "Pflege",
        "body": (
            "<p>Änderungen an dieser Anlage erhalten eine neue Versionsnummer und ein Datum; bestehende Kunden "
            "werden mindestens 30 Tage vor Wirksamwerden informiert. Der RTO-Wert wird nach der ersten "
            "gemessenen Notfallübung überprüft.</p>"
        ),
    },
]


def sla_toc_items() -> list[dict]:
    """Einträge für den TableOfContents-Block der Seite /sla/."""
    return [{"number": f"{s['number']}.", "text": s["title"], "anchor": s["anchor"]} for s in SLA_SECTIONS]
