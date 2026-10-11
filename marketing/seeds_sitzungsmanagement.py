"""
Seed-Inhalt der Sachseite /sitzungsmanagement/ (SEO-Kaufbegriffe, Issue mandariOSS/mandari#939).

Die Seite erklärt Sitzungsmanagement, Sitzungsdienst, Gremienmanagement, digitale Gremienarbeit und die papierlose
Sitzung und zeigt, was mandari Session davon abdeckt. Vorgaben wie bei /ratsinformationssystem/
(``marketing/seeds_ris.py``):

* keine Preise und keine Kostenaussagen; der einzige Verweis auf Kosten ist der Weg „Preise“ im Schlussband,
* keine Aussagen zu KI (Anbieter noch nicht freigegeben, mandariOSS/mandari#950),
* nur Aussagen über mandari Session, die schon auf mandari.de (Funktionsübersicht auf /produkte/, Releases) oder in
  der Dokumentation (docs.mandari.de/session/) stehen, mit denselben Status-Etiketten,
* Abschnitte nach dem Musterkatalog, nie zweimal dasselbe Muster hintereinander.

Abgrenzung zu /kommunen/: Diese Seite erklärt den Begriff Sitzungsmanagement, /kommunen/ ist die Seite für
Verwaltungen (Betrieb, Anbindung, Pilotkommunen) mit dem Suchbegriff Sitzungsdienst.

Nach Änderungen: ``refresh_seeded_page sitzungsmanagement --force``.
"""

from __future__ import annotations

from marketing import seeds_muster as m

KONTAKT = "/kontakt/?subject=Sitzungsmanagement-Demo#termin"


def seite():
    """Blockliste von /sitzungsmanagement/."""
    from marketing.management.commands.migrate_pages_to_streamfield import cta

    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "Sitzungsmanagement von der Ladung bis zum Beschluss.", "title_highlight": "",
            "subline": (
                "mandari Session führt Ihren Sitzungsdienst in einem System: Sitzungen planen und laden, Vorlagen "
                "durch die Beratung führen, Niederschriften genehmigen und Beschlüsse nachhalten."
            ),
            "subline_secondary": "",
            "ctas": [cta("Erstgespräch vereinbaren", KONTAKT),
                     cta("mandari Session für Verwaltungen", "/kommunen/", style="outline")],
            "background_color": "primary",
        }),
        # Muster 5a: Begriff und Teilbegriffe, rechts der Ablauf einer Sitzung
        m.randspalte(
            "Was ist Sitzungsmanagement?",
            "<p><strong>Sitzungsdienst.</strong> So heißt die Stelle in der Verwaltung, die Rat und Ausschüsse "
            "betreut, oft im Ratsbüro oder im Hauptamt. Sie trägt Fristen, Formalien und Unterlagen jeder "
            "Sitzung.</p>"
            "<p><strong>Gremienmanagement.</strong> Rat, Ausschüsse, Beiräte und Fraktionen mit ihren Mitgliedern, "
            "Stellvertretungen und Wahlperioden. Daraus ergibt sich, wer zu welcher Sitzung geladen wird.</p>"
            "<p><strong>Digitale Gremienarbeit.</strong> Ladung, Unterlagen, Abstimmung und Niederschrift laufen "
            "über ein System statt über Textdateien, Mailverläufe und PDF-Stapel. Was einmal erfasst ist, wird "
            "nicht noch einmal abgetippt.</p>"
            "<p><strong>Papierlose Sitzung.</strong> Ladung und Sitzungsmappe kommen digital, Sitzungen laufen auf "
            "Wunsch hybrid. Den Zustellweg legen Sie je Person fest: Papier bekommt nur, wer es möchte.</p>",
            [
                m.rand_ablauf("Eine Sitzung im Sitzungsdienst",
                              ("Planung", "Sitzungskalender und Tagesordnung"),
                              ("Ladung", "fristgerecht, digital oder auf Papier"),
                              ("Sitzung", "Anwesenheit und Abstimmungen, auch hybrid"),
                              ("Niederschrift", "mit Genehmigung, danach geschützt"),
                              ("Beschlusskontrolle", "Zuständigkeit, Frist und Umsetzungsstand")),
                m.rand_links("Mehr dazu", ("Was ein Ratsinformationssystem ist", "/ratsinformationssystem/")),
            ],
            subline="Sitzungsmanagement ist die Organisation der Gremienarbeit einer Kommune: Sitzungen planen, "
                    "Tagesordnungen aufstellen, laden, Vorlagen beraten, Beschlüsse fassen und dokumentieren. "
                    "Software dafür bündelt diese Arbeit des Sitzungsdienstes in einem System.",
            anchor="was-ist-sitzungsmanagement",
        ),
        # Muster 3: Aufgaben des Sitzungsdienstes mit Stand (Status wie in der Funktionsübersicht auf /produkte/)
        m.register(
            "Was mandari Session leistet",
            [
                m.gruppe(
                    "Gremien und Personen",
                    m.zeile("Gremien und Mitgliedschaften",
                            "Rat, Ausschüsse, Beiräte und Fraktionen mit Mitgliedschaften und Wahlperioden; "
                            "Kontaktdaten liegen verschlüsselt.", stand="Verfügbar", status="da"),
                    m.zeile("Gemeinsame Sitzungen",
                            "Gemeinsame Sitzungen mehrerer Gremien. Mehrere Körperschaften führen Sie als Gruppe mit "
                            "einer gemeinsamen Leitstelle.", stand="Verfügbar", status="da"),
                ),
                m.gruppe(
                    "Vor der Sitzung",
                    m.zeile("Sitzungsplanung und Tagesordnung",
                            "Sitzungskalender, Tagesordnung mit öffentlichem und nichtöffentlichem Teil.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Ladung",
                            "Digital und auf Papier, mit Ladungsfristen, Empfangsbestätigung und Rückmeldung.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Sitzungsmappe",
                            "Alle Unterlagen als ein PDF mit Inhaltsverzeichnis und Lesezeichen oder als ZIP-Archiv.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Vorlagen und Mitzeichnung",
                            "Drucksachen mit eigenem Nummernkreis, Anlagen und Beratungsfolge über mehrere Gremien. "
                            "Freigaben nach dem Vier-Augen-Prinzip mit Vertretung; jede Fassung bleibt erhalten.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Anträge aus den Fraktionen",
                            "Eingang digital aus mandari Work, mit Statusrückmeldung an die Fraktion, Prüfung und "
                            "Übernahme als Vorlage.", stand="Verfügbar", status="da"),
                    m.zeile("Raum- und Ressourcenplanung", "Räume und Ressourcen für Sitzungen planen.",
                            stand="Geplant 2027", status="offen"),
                ),
                m.gruppe(
                    "In der Sitzung",
                    m.zeile("Hybride Sitzungen",
                            "Live-Cockpit mit Teilnahmeart, Beschlussfähigkeit und Störungen.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Abstimmungen",
                            "Ergebnisse je Tagesordnungspunkt: offen, geheim, summiert oder namentlich.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Stimmabgabe und Rednerliste",
                            "Abstimmen am eigenen Gerät, Rednerliste mit Saalanzeige.",
                            stand="Geplant 2027", status="offen"),
                    m.zeile("App für Ratsmitglieder", "Die Sitzungsunterlagen in einer App, auch offline.",
                            stand="Geplant 2027", status="offen"),
                ),
                m.gruppe(
                    "Nach der Sitzung",
                    m.zeile("Niederschrift",
                            "Öffentlicher und nichtöffentlicher Teil getrennt, mit Genehmigung. Danach ist sie "
                            "geschützt, Korrekturen laufen als nachvollziehbare Berichtigung.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Beschlusskontrolle",
                            "Beschlussregister mit Zuständigkeit, Frist und Umsetzungsstand; auf Wunsch öffentlich im "
                            "Bürgerportal.", stand="Verfügbar", status="da"),
                    m.zeile("Sitzungsgeld",
                            "Abrechnung nach dem Vier-Augen-Prinzip, mit SEPA-Export.", stand="Verfügbar", status="da"),
                    m.zeile("Fristen-Erinnerungen",
                            "Automatische E-Mails zu Ladung, Vorlagen und Wiedervorlage.",
                            stand="Verfügbar", status="da"),
                ),
            ],
            spalten=["Aufgabe", "Umsetzung in mandari Session", "Stand"],
            subline="Jede Aufgabe des Sitzungsdienstes mit ihrem Stand: was heute läuft und was als Nächstes kommt.",
            anchor="funktionen",
            bestand="{da} von {gesamt} sind heute verfügbar, {offen} sind für 2027 geplant.",
            note="<p>Alle Funktionen der drei Produkte zeigt die "
                 "<a href=\"/produkte/#funktionen\">Funktionsübersicht</a>, den Abgleich mit etablierten Systemen "
                 "der <a href=\"/vergleich/\">RIS-Vergleich</a>.</p>",
        ),
        # Muster 5b: Grundsätze als Begriffe, mit den Wegen zu Bürgerportal und Schnittstelle
        m.begriffe(
            "Worauf sich Ihr Sitzungsdienst verlassen kann",
            [
                m.begriff("Öffentlich, was öffentlich ist",
                          "Jede Sitzung, jeder Tagesordnungspunkt, jede Vorlage und jede Anlage ist als öffentlich "
                          "oder nichtöffentlich gekennzeichnet. Nach außen geht nur Öffentliches: auf Knopfdruck ins "
                          "Bürgerportal und über die <a href=\"/oparl-schnittstelle/\">OParl-Schnittstelle</a>.",
                          link_label="Zum Bürgerinformationssystem", link_url="/buergerinformationssystem/"),
                m.begriff("Lückenlos nachvollziehbar",
                          "Jede Änderung steht revisionssicher im Audit-Log, auch Lesezugriffe. Inhalte liegen je "
                          "Kommune verschlüsselt, die Anmeldung unterstützt einen zweiten Faktor.",
                          link_label="Sicherheit im Trust Center", link_url="/trust/"),
                m.begriff("Offener Code",
                          "Der gesamte Quellcode steht unter AGPL-3.0. Ihre IT prüft ihn bis zur letzten Zeile, Ihre "
                          "Daten exportieren Sie jederzeit in offenen Formaten.",
                          link_label="Quellcode ansehen", link_url="https://github.com/mandariOSS/mandari"),
                m.begriff("Ihr Betrieb, Ihre Wahl",
                          "Als Dienst aus ISO-27001-zertifizierten Rechenzentren in Deutschland oder per Docker "
                          "Compose in Ihrem eigenen Rechenzentrum, mit demselben Funktionsumfang.",
                          link_label="Unterlagen für die Vergabe", link_url="/vergabe/"),
            ],
            subline="Der Sitzungsdienst trägt Verantwortung für Fristen, Vertrauliches und die Öffentlichkeit. "
                    "Dafür ist mandari Session gebaut.",
            anchor="grundsaetze",
        ),
        ("accordion_faq", {
            "header": m.kopf("Häufige Fragen zum Sitzungsmanagement",
                             "Steht Ihre Frage nicht dabei? Schreiben Sie uns."),
            "anchor_id": "faq", "background": "white",
            "rand": [
                m.rand_fakten("Direkt fragen", ("E-Mail", "hello@mandari.de"),
                              ("Antwort", "in der Regel innerhalb eines Werktags")),
                m.rand_links("Zum Nachlesen", ("Dokumentation zu mandari Session", "https://docs.mandari.de/session/"),
                             ("Migration", "/migration/"), ("Vergabe und Unterlagen", "/vergabe/"),
                             ("RIS-Vergleich", "/vergleich/")),
            ],
            "items": [
                {"question": "Was ist Sitzungsmanagement?",
                 "answer": "<p>Sitzungsmanagement ist die Organisation der Gremienarbeit einer Kommune: Sitzungen "
                           "planen, Tagesordnungen aufstellen, laden, Vorlagen beraten, Beschlüsse fassen und "
                           "dokumentieren. Sitzungsmanagement-Software bündelt diese Arbeit des Sitzungsdienstes in "
                           "einem System.</p>"},
                {"question": "Was unterscheidet Sitzungsmanagement und Ratsinformationssystem?",
                 "answer": "<p>Sitzungsmanagement meint die Arbeit der Verwaltung rund um die Sitzung. Das "
                           "<a href=\"/ratsinformationssystem/\">Ratsinformationssystem</a> ist der Oberbegriff: Es "
                           "umfasst das Sitzungsmanagement, den Zugang der Ratsmitglieder und das "
                           "Bürgerinformationssystem für die Öffentlichkeit.</p>"},
                {"question": "Was gehört zum Gremienmanagement?",
                 "answer": "<p>Die Gremien, ihre Mitglieder mit Funktionen und Stellvertretungen und die "
                           "Wahlperioden. In mandari Session pflegen Sie Rat, Ausschüsse, Beiräte und Fraktionen an "
                           "einer Stelle; Ladung und Anwesenheit bauen darauf auf.</p>"},
                {"question": "Geht die papierlose Sitzung mit mandari Session?",
                 "answer": "<p>Ja. Ladung und Unterlagen kommen digital, die Sitzungsmappe als ein PDF mit "
                           "Inhaltsverzeichnis, und Sitzungen laufen auf Wunsch hybrid. Papier erhält nur, wer es "
                           "möchte.</p>"
                           "<p>Eine App mit den Unterlagen offline ist für 2027 geplant, ein eigener Bereich für alle "
                           "Ratsmitglieder ist in Prüfung.</p>"},
                {"question": "Wie kommen Beschlüsse in die Öffentlichkeit?",
                 "answer": "<p>Auf Knopfdruck: Ein Schalter in den Einstellungen veröffentlicht öffentliche "
                           "Sitzungen, Vorlagen und Beschlüsse im "
                           "<a href=\"/buergerinformationssystem/\">Bürgerinformationssystem</a> und über die "
                           "OParl-Schnittstelle. Nichtöffentliches bleibt intern, jede Umstellung steht im "
                           "Audit-Log.</p>"},
                {"question": "Können wir unsere Daten aus dem bisherigen System übernehmen?",
                 "answer": "<p>Ja. Spricht Ihr System OParl, übernehmen wir Sitzungen, Vorlagen, Gremien, Personen "
                           "und Dokumente strukturiert. Gremien, Personen und Besetzungen kommen auch aus Listen der "
                           "Verwaltung; den Weg klären wir in der Bestandsaufnahme. Wie der Umstieg abläuft, zeigt "
                           "die Seite <a href=\"/migration/\">Migration</a>.</p>"},
            ],
        }),
        m.einladung(
            "Sprechen wir über Ihren Sitzungsdienst.",
            "In 30 Minuten klären wir, wie Ihr Sitzungsdienst heute arbeitet, welche Daten mitkommen und wie ein "
            "Umstieg aussieht. Per Video, am Telefon oder persönlich in Münster.",
            "Erstgespräch vereinbaren", KONTAKT,
            link_label="So läuft die Migration", link_url="/migration/",
            wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                  ("Für Vergabestellen", "Unterlagen", "/vergabe/"), ("Preise", "Was mandari kostet", "/preise/")],
        ),
    ]
