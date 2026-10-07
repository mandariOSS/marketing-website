"""
Seed-Inhalt der Sachseite /ratsinformationssystem/ (SEO, Issue mandariOSS/mandari#914).

Die Seite erklärt den Begriff und zeigt, was mandari davon abdeckt. Vorgaben (Sven, 07.10.2026):

* keine Preise, kein Kostenabschnitt, keine Aussagen zu Lizenzkosten oder Finanzierung; der einzige
  Verweis auf Kosten ist der Weg „Preise“ im Schlussband,
* jede Frage-Überschrift beantwortet sich in den ersten beiden Sätzen (Antwort zuerst),
* nur Aussagen über mandari, die schon auf mandari.de stehen (Produkte, Kommunen, Fraktionen, Migration,
  Vergabe, RIS-Vergleich), mit denselben Status-Etiketten; über andere Anbieter nur, was der RIS-Vergleich
  mit Quelle belegt,
* Abschnitte nach dem Musterkatalog, nie zweimal dasselbe Muster hintereinander.

Nach Änderungen: ``refresh_seeded_page ratsinformationssystem --force``.
"""

from __future__ import annotations

from marketing import seeds_muster as m

KONTAKT = "/kontakt/?subject=Ratsinformationssystem-Demo#termin"


def seite():
    """Blockliste von /ratsinformationssystem/."""
    from marketing.management.commands.migrate_pages_to_streamfield import cta
    from marketing.seeds_vergleich import ANZAHL_FUNKTIONEN

    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "Ratsinformationssystem für die offene Verwaltung.", "title_highlight": "",
            "subline": (
                "mandari verbindet Sitzungsdienst, Fraktionsarbeit und Bürgerportal auf einer Plattform: mit offener "
                "OParl-Schnittstelle, vollständig Open Source und betrieben in Deutschland oder in Ihrem eigenen "
                "Rechenzentrum."
            ),
            "subline_secondary": "",
            "ctas": [cta("Erstgespräch vereinbaren", KONTAKT),
                     cta("RIS-Vergleich ansehen", "/vergleich/", style="outline")],
            "background_color": "primary",
        }),
        # Muster 5a: Definition, Stichworte für die drei Seiten, rechts der Weg einer Vorlage
        m.randspalte(
            "Was ist ein Ratsinformationssystem?",
            "<p><strong>Verwaltung.</strong> Der Sitzungsdienst plant Sitzungen, stellt Tagesordnungen auf, lädt ein, "
            "führt Vorlagen durch die Beratungsfolge und schreibt die Niederschrift. Im RIS geschieht das in einem "
            "System statt in Textdateien, Mailverläufen und PDF-Stapeln.</p>"
            "<p><strong>Rat und Fraktionen.</strong> Ratsmitglieder erhalten Ladung und Unterlagen, auch die "
            "nichtöffentlichen, und bereiten ihre Sitzungen vor. Fraktionen bringen Anträge und Anfragen ein und "
            "stimmen ihre Positionen ab.</p>"
            "<p><strong>Öffentlichkeit.</strong> Bürger:innen, Presse und Zivilgesellschaft finden öffentliche "
            "Sitzungen, Vorlagen und Beschlüsse im Bürgerinformationssystem, ohne Anmeldung.</p>",
            [
                m.rand_ablauf("Der Weg einer Vorlage",
                              ("Vorlage", "aus der Verwaltung oder als Antrag aus dem Rat"),
                              ("Beratung", "in den Ausschüssen, laut Beratungsfolge"),
                              ("Beschluss", "im Rat, mit dem Ergebnis der Abstimmung"),
                              ("Veröffentlichung", "Niederschrift und Beschluss für alle einsehbar")),
            ],
            subline="Ein Ratsinformationssystem, kurz RIS, ist die Software für die Gremienarbeit einer Kommune: "
                    "Sitzungen, Tagesordnungen, Vorlagen, Niederschriften und Beschlüsse an einem Ort. Es verbindet "
                    "die Verwaltung, die Sitzungen vorbereitet, den Rat, der entscheidet, und die Öffentlichkeit, die "
                    "nachvollzieht, was beschlossen wird.",
            anchor="was-ist-ein-ris",
        ),
        # Muster 3: Begriffe als Tabelle, Kopf in der Randspalte
        m.register(
            "Welcher Begriff meint was?",
            [
                m.gruppe(
                    "",
                    m.zeile("Ratsinformationssystem (RIS)",
                            "Oberbegriff für die Software der Gremienarbeit: von der Vorlage über Sitzung und "
                            "Beschluss bis zur Veröffentlichung.",
                            stand="Session, Work und Insight"),
                    m.zeile("Sitzungsdienst, Sitzungsmanagement",
                            "Die Arbeit der Verwaltung rund um die Sitzung, vom Sitzungskalender bis zum Sitzungsgeld, "
                            "und die Software dafür.",
                            stand="mandari Session"),
                    m.zeile("Gremieninformationssystem",
                            "Geschützter Zugang für Ratsmitglieder zu allen Unterlagen ihrer Gremien, auch den "
                            "nichtöffentlichen. Bei mandari kommen die Unterlagen heute mit der Ladung, Fraktionen "
                            "arbeiten in Work; ein eigener Bereich für alle Ratsmitglieder ist in Prüfung.",
                            stand="Session und Work"),
                    m.zeile("Bürgerinformationssystem",
                            "Der öffentliche Teil: Sitzungstermine, Tagesordnungen, Vorlagen und Beschlüsse für alle, "
                            "ohne Anmeldung.",
                            stand="mandari Insight"),
                ),
            ],
            spalten=["Begriff", "Was gemeint ist", "Bei mandari"],
            subline="Ratsinformationssystem ist der Oberbegriff. Sitzungsdienst, Gremieninformationssystem und "
                    "Bürgerinformationssystem sind seine Teile – für Verwaltung, Ratsmitglieder und Öffentlichkeit.",
            anchor="begriffe",
        ),
        # Muster 7: die drei Produkte mit echten Bildschirmen, Status wie auf /produkte/
        m.produktbilder(
            "Was mandari abdeckt",
            [
                m.produktbild("session", "mandari Session",
                              "Der Sitzungsdienst Ihrer Verwaltung: Sitzungsplanung, Tagesordnung und Ladung, "
                              "Vorlagen mit Mitzeichnung, Niederschrift mit Genehmigung, Beschlusskontrolle und "
                              "Sitzungsgeld – in einem System.",
                              fakten=[("Für", "Verwaltungen"), ("Stand", "Pilotphase")],
                              link_label="mandari Session für Verwaltungen", link_url="/kommunen/", anchor="session"),
                m.produktbild("work", "mandari Work",
                              "Der Arbeitsplatz Ihrer Fraktion: Sitzungen im Team vorbereiten, Anträge mit Fristen und "
                              "Freigaben schreiben und digital einreichen, Positionen abstimmen – mit den Ratsdaten "
                              "Ihrer Kommune.",
                              fakten=[("Für", "Fraktionen und Mandatsträger:innen"), ("Stand", "Offene Beta")],
                              link_label="mandari Work für Fraktionen", link_url="/fraktionen/", anchor="work"),
                m.produktbild("insight", "mandari Insight",
                              "Das Bürgerinformationssystem: Sitzungen, Vorlagen und Beschlüsse im Volltext "
                              "durchsuchbar und auf der Karte verortet, ohne Anmeldung und ohne Tracking.",
                              fakten=[("Für", "Bürger:innen"), ("Stand", "Im Einsatz")],
                              link_label="Bürgerportal öffnen", link_url="/insight/", anchor="insight"),
            ],
            subline="Alle drei Seiten der Ratsarbeit auf einem Datenbestand: Session für die Verwaltung, Work für "
                    "Fraktionen und Insight für Bürger:innen.",
            anchor="abdeckung",
            note="<p>Was jedes Produkt im Einzelnen kann und was noch fehlt, zeigt die "
                 "<a href=\"/produkte/#funktionen\">Funktionsübersicht</a>.</p>",
        ),
        # Muster 5a: OParl, rechts die Eckdaten der Schnittstelle und die Dokumentation
        m.randspalte(
            "Was ist OParl?",
            "<p><strong>Offen für alle.</strong> Presse, Zivilgesellschaft und andere Anwendungen verwenden Ihre "
            "Ratsdaten direkt weiter: maschinenlesbar statt als PDF-Stapel.</p>"
            "<p><strong>Ohne Mehraufwand.</strong> mandari veröffentlicht Beschlüsse und Sitzungsunterlagen "
            "automatisch über OParl. Ihr Sitzungsdienst pflegt nichts doppelt.</p>"
            "<p><strong>Wechsel.</strong> Spricht Ihr bisheriges System OParl, etwa ALLRIS, regisafe, Somacos oder "
            "SD.NET RIM, übernimmt mandari den Bestand strukturiert. Ihre Daten bekommen Sie jederzeit vollständig "
            "heraus.</p>",
            [
                m.rand_fakten("Schnittstelle", ("Standard", "OParl 1.1"),
                              ("Je Kommune", "in mandari Session"),
                              ("Über alle Kommunen", "im Bürgerportal, mit Änderungsfeed"),
                              ("Export", "OParl, CSV, JSON")),
                m.rand_links("Dokumentation",
                             ("OParl-API des Bürgerportals", "https://docs.mandari.de/insight/oparl-api/"),
                             ("OParl-API von mandari Session", "https://docs.mandari.de/session/oparl-api/")),
            ],
            subline="OParl ist der offene Standard für die Schnittstelle von Ratsinformationssystemen. Er legt fest, "
                    "wie Sitzungen, Vorlagen, Beschlüsse und Dokumente maschinenlesbar bereitstehen, unabhängig vom "
                    "Hersteller.",
            anchor="oparl",
        ),
        # Muster 2: Vergleichen, ausschreiben, umsteigen; Ergebnis mit dem Weg zur Migration
        m.schrittfolge(
            "So wechseln Sie Ihr Ratsinformationssystem",
            [
                ("Vergleichen",
                 "Stellen Sie mandari und Ihr bisheriges System Funktion für Funktion nebeneinander, mit Quellen und "
                 "offen benannten Lücken.", ""),
                ("Ausschreiben",
                 "AVV, technische und organisatorische Maßnahmen, Löschkonzept, Funktionsübersicht und "
                 "Software-Stückliste gehen direkt in Ihre Vergabeakte.", ""),
                ("Umsteigen",
                 "Wir übernehmen Ihren Bestand über OParl, schulen Ihr Team, und beide Systeme laufen parallel bis "
                 "zum festen Umstellungstag.", "7 bis 14 Wochen vom ersten Termin bis zur Umstellung"),
            ],
            subline="Drei Schritte vom bisherigen System zu mandari. Für jeden liegen die Grundlagen öffentlich "
                    "bereit.",
            anchor="wechsel",
            ergebnis={"titel": "Ihr neues RIS",
                      "text": "Sitzungsdienst, Fraktionen und Bürgerportal auf einer offenen Plattform; das "
                              "bisherige System bleibt lesbar.",
                      "link_label": "So läuft die Migration", "link_url": "/migration/"},
            note="<p>Grundlagen für jeden Schritt: der <a href=\"/vergleich/\">RIS-Vergleich</a> mit Quellen und die "
                 "<a href=\"/vergabe/\">Unterlagen für Beschaffung und Prüfung</a>.</p>",
        ),
        ("accordion_faq", {
            "header": m.kopf("Häufige Fragen zum Ratsinformationssystem",
                             "Steht Ihre Frage nicht dabei? Schreiben Sie uns."),
            "anchor_id": "faq", "background": "white",
            "rand": [
                m.rand_fakten("Direkt fragen", ("E-Mail", "hello@mandari.de"),
                              ("Antwort", "in der Regel innerhalb eines Werktags")),
                m.rand_links("Zum Nachlesen", ("RIS-Vergleich", "/vergleich/"), ("Migration", "/migration/"),
                             ("Vergabe und Unterlagen", "/vergabe/"), ("Trust Center", "/trust/")),
            ],
            "items": [
                {"question": "Was ist ein Ratsinformationssystem?",
                 "answer": "<p>Ein Ratsinformationssystem (RIS) ist die Software für die Gremienarbeit einer Kommune. "
                           "Verwaltung, Ratsmitglieder und Öffentlichkeit finden darin Sitzungen, Tagesordnungen, "
                           "Vorlagen, Niederschriften und Beschlüsse.</p>"},
                {"question": "Was unterscheidet Sitzungsdienst und Ratsinformationssystem?",
                 "answer": "<p>Der Sitzungsdienst ist die Arbeit der Verwaltung rund um die Sitzung, oft auch die "
                           "Software dafür. Das Ratsinformationssystem ist der Oberbegriff: Es umfasst den "
                           "Sitzungsdienst, den Zugang der Ratsmitglieder und das Bürgerinformationssystem.</p>"},
                {"question": "Was ist OParl?",
                 "answer": "<p>OParl ist der offene Standard für die Schnittstelle von Ratsinformationssystemen. "
                           "mandari stellt alle Ratsdaten über OParl 1.1 bereit und übernimmt Daten aus jedem "
                           "System, das OParl spricht.</p>"},
                {"question": "Können wir unser bisheriges RIS ablösen?",
                 "answer": "<p>Ja. Spricht Ihr System OParl, übernehmen wir Sitzungen, Vorlagen, Gremien, Personen "
                           "und Dokumente strukturiert; Sonderfelder und Bestände ohne OParl-Export klären wir in der "
                           "Bestandsaufnahme. Bis zum Umstellungstag laufen beide Systeme parallel; für die ganze "
                           "<a href=\"/migration/\">Migration</a> rechnen wir vom ersten Termin an mit 7 bis 14 "
                           "Wochen.</p>"},
                {"question": "Läuft mandari in Deutschland, und können wir es selbst betreiben?",
                 "answer": "<p>Ja, beides. Als Dienst betreiben wir mandari in ISO-27001-zertifizierten "
                           "Rechenzentren in Deutschland, ohne US-Cloud-Anbieter; im eigenen Rechenzentrum läuft es "
                           "per Docker Compose, auf Wunsch mit Betreuungsvertrag.</p>"
                           "<p>Der Funktionsumfang ist in beiden Fällen derselbe, der Quellcode steht unter "
                           "AGPL-3.0.</p>"},
                {"question": "Wie unterscheidet sich mandari von ALLRIS, SessionNet, SD.NET und regisafe?",
                 "answer": "<p>mandari ist Open Source mit öffentlicher Roadmap und verbindet Sitzungsdienst, "
                           "Fraktionsarbeit und Bürgerportal auf einer Plattform. Die etablierten Systeme bieten heute "
                           "Funktionen, die mandari erst entwickelt.</p>"
                           f"<p>Der <a href=\"/vergleich/\">RIS-Vergleich</a> stellt {ANZAHL_FUNKTIONEN} Funktionen "
                           "mit Quellen nebeneinander und nennt offen, was mandari noch fehlt.</p>"},
            ],
        }),
        m.einladung(
            "Sprechen wir über Ihr Ratsinformationssystem.",
            "In 30 Minuten klären wir, wie Ihr Sitzungsdienst heute arbeitet, welche Daten mitkommen und wie ein "
            "Umstieg aussieht – per Video, am Telefon oder persönlich in Münster.",
            "Erstgespräch vereinbaren", KONTAKT,
            link_label="Bürgerportal ansehen", link_url="/insight/",
            wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                  ("Für Vergabestellen", "Unterlagen", "/vergabe/"), ("Preise", "Was mandari kostet", "/preise/")],
        ),
    ]
