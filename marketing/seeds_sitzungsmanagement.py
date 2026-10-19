"""
Seed-Inhalt der Sachseite /sitzungsmanagement/ (SEO-Kaufbegriffe, Issue mandariOSS/mandari#939).

Die Seite erklärt Sitzungsmanagement, Gremienmanagement, digitale Gremienarbeit, die papierlose Sitzung und den
Sitzungsdienst und zeigt, was mandari Session davon abdeckt. Vorgaben wie bei /ratsinformationssystem/
(``marketing/seeds_ris.py``):

* keine Preise und keine Kostenaussagen; der einzige Verweis auf Kosten ist der Weg „Preise“ im Schlussband,
* keine Aussagen zu KI (Anbieter noch nicht freigegeben, mandariOSS/mandari#950),
* Faktentreue vor Glanz: nur, was in Produktion heute verfügbar ist, steht ohne Etikett da; mandari Session trägt
  überall das Etikett „Pilotphase“ (wie auf /ratsinformationssystem/ und /produkte/), Geplantes seinen Zeitpunkt,
* keine Übernahme des Altbestands in Session versprechen: Stammdaten kommen aus Listen der Verwaltung, der öffentliche
  Altbestand bleibt im Bürgerportal (docs/SESSION_UMSTIEG_SESSIONNET.md im Repository mandariOSS/mandari; die
  Übernahme über OParl steht auf der Roadmap für Version 1.0),
* Open Source ohne Absolutheit (keine „gesamter Quellcode“- oder „derselbe Funktionsumfang“-Aussagen),
* Abschnitte nach dem Musterkatalog, nie zweimal dasselbe Muster hintereinander.

Abgrenzung zu /kommunen/: Diese Seite trägt die Begriffe Sitzungsmanagement und Gremienmanagement, /kommunen/ ist die
Seite für Verwaltungen (Betrieb, Anbindung, Pilotkommunen) mit dem Suchbegriff Sitzungsdienst.

Nach Änderungen: ``refresh_seeded_page sitzungsmanagement --force``.
"""

from __future__ import annotations

from marketing import seeds_muster as m

KONTAKT = "/kontakt/?subject=Sitzungsmanagement-Demo#termin"
PILOT = "Pilotphase"


def seite():
    """Blockliste von /sitzungsmanagement/."""
    from marketing.management.commands.migrate_pages_to_streamfield import cta

    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "Sitzungsmanagement von der Ladung bis zum Beschluss.", "title_highlight": "",
            "subline": (
                "mandari Session bündelt das Sitzungs- und Gremienmanagement Ihrer Verwaltung in einem System: "
                "Sitzungen planen und laden, Vorlagen durch die Beratung führen, Niederschriften genehmigen und "
                "Beschlüsse nachhalten."
            ),
            "subline_secondary": "",
            "ctas": [cta("Erstgespräch vereinbaren", KONTAKT),
                     cta("mandari Session für Verwaltungen", "/kommunen/", style="outline")],
            "background_color": "primary",
        }),
        # Muster 5a: Begriff und Teilbegriffe, rechts Stand des Produkts und Ablauf einer Sitzung
        m.randspalte(
            "Was ist Sitzungsmanagement?",
            "<p><strong>Gremienmanagement.</strong> Rat, Ausschüsse, Beiräte und Fraktionen mit ihren Mitgliedern, "
            "Stellvertretungen und Wahlperioden. Daraus ergibt sich, wer zu welcher Sitzung geladen wird.</p>"
            "<p><strong>Digitale Gremienarbeit.</strong> Ladung, Unterlagen, Abstimmung und Niederschrift laufen "
            "über ein System statt über Textdateien, Mailverläufe und PDF-Stapel. Was einmal erfasst ist, wird "
            "nicht noch einmal abgetippt.</p>"
            "<p><strong>Papierlose Sitzung.</strong> Ladung und Sitzungsmappe kommen digital, Sitzungen laufen auf "
            "Wunsch hybrid. Den Zustellweg legen Sie je Person fest: Papier bekommt nur, wer es möchte.</p>"
            "<p><strong>Sitzungsdienst.</strong> So heißt die Stelle in der Verwaltung, die das "
            "Sitzungsmanagement verantwortet, oft im Ratsbüro oder im Hauptamt.</p>",
            [
                m.rand_fakten("mandari Session", ("Für", "Verwaltungen"), ("Stand", PILOT)),
                m.rand_ablauf("Eine Sitzung im Sitzungsmanagement",
                              ("Planung", "Sitzungskalender und Tagesordnung"),
                              ("Ladung", "fristgerecht, digital oder auf Papier"),
                              ("Sitzung", "Anwesenheit und Abstimmungen, auch hybrid"),
                              ("Niederschrift", "mit Genehmigung, danach geschützt"),
                              ("Beschlusskontrolle", "Zuständigkeit, Frist und Umsetzungsstand")),
                m.rand_links("Mehr dazu", ("Was ein Ratsinformationssystem ist", "/ratsinformationssystem/")),
            ],
            subline="Sitzungsmanagement ist die Organisation der Gremienarbeit einer Kommune: Sitzungen planen, "
                    "Tagesordnungen aufstellen, laden, Vorlagen beraten, Beschlüsse fassen und dokumentieren. "
                    "Sitzungsmanagement-Software bündelt diese Arbeit in einem System.",
            anchor="was-ist-sitzungsmanagement",
        ),
        # Muster 3: Aufgaben mit Stand (Status wie in der Funktionsübersicht auf /produkte/, Session in der Pilotphase)
        m.register(
            "Was mandari Session leistet",
            [
                m.gruppe(
                    "Gremien und Personen",
                    m.zeile("Gremien und Mitgliedschaften",
                            "Rat, Ausschüsse, Beiräte und Fraktionen mit Mitgliedschaften und Wahlperioden; Telefon, "
                            "Anschrift und Bankdaten liegen verschlüsselt.", stand=PILOT, status="da"),
                    m.zeile("Gemeinsame Sitzungen",
                            "Gemeinsame Sitzungen mehrerer Gremien. Mehrere Körperschaften führen Sie als Gruppe mit "
                            "einer gemeinsamen Leitstelle.", stand=PILOT, status="da"),
                ),
                m.gruppe(
                    "Vor der Sitzung",
                    m.zeile("Sitzungsplanung und Tagesordnung",
                            "Sitzungskalender, Tagesordnung mit öffentlichem und nichtöffentlichem Teil.",
                            stand=PILOT, status="da"),
                    m.zeile("Ladung",
                            "Digital und auf Papier, mit Ladungsfristen, Empfangsbestätigung und Rückmeldung.",
                            stand=PILOT, status="da"),
                    m.zeile("Sitzungsmappe",
                            "Alle Unterlagen als ein PDF mit Inhaltsverzeichnis und Lesezeichen oder als ZIP-Archiv.",
                            stand=PILOT, status="da"),
                    m.zeile("Vorlagen und Mitzeichnung",
                            "Drucksachen mit eigenem Nummernkreis, Anlagen und Beratungsfolge über mehrere Gremien. "
                            "Freigaben nach dem Vier-Augen-Prinzip mit Vertretung; jede Fassung bleibt erhalten.",
                            stand=PILOT, status="da"),
                    m.zeile("Anträge aus den Fraktionen",
                            "Eingang digital aus mandari Work, mit Statusrückmeldung an die Fraktion, Prüfung und "
                            "Übernahme als Vorlage.", stand=PILOT, status="da"),
                    m.zeile("Raum- und Ressourcenplanung", "Räume und Ressourcen für Sitzungen planen.",
                            stand="Geplant 2027", status="offen"),
                ),
                m.gruppe(
                    "In der Sitzung",
                    m.zeile("Hybride Sitzungen",
                            "Live-Cockpit mit Teilnahmeart, Beschlussfähigkeit und Störungen.",
                            stand=PILOT, status="da"),
                    m.zeile("Abstimmungen",
                            "Ergebnisse je Tagesordnungspunkt: offen, geheim, summiert oder namentlich.",
                            stand=PILOT, status="da"),
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
                            stand=PILOT, status="da"),
                    m.zeile("Beschlusskontrolle",
                            "Beschlussregister mit Zuständigkeit, Frist und Umsetzungsstand; nach Ihrer Freigabe "
                            "öffentlich im Bürgerportal.", stand=PILOT, status="da"),
                    m.zeile("Sitzungsgeld",
                            "Abrechnung nach dem Vier-Augen-Prinzip, mit SEPA-Export.", stand=PILOT, status="da"),
                    m.zeile("Fristen-Erinnerungen",
                            "Automatische E-Mails zu Ladung, Vorlagen und Wiedervorlage.",
                            stand=PILOT, status="da"),
                ),
            ],
            spalten=["Aufgabe", "Umsetzung in mandari Session", "Stand"],
            subline="Jede Aufgabe im Sitzungs- und Gremienmanagement mit ihrem Stand. mandari Session ist in der "
                    "Pilotphase.",
            anchor="funktionen",
            bestand="{da} von {gesamt} gibt es in der Pilotphase, {offen} sind für 2027 geplant.",
            note="<p>Alle Funktionen der drei Produkte zeigt die "
                 "<a href=\"/produkte/#funktionen\">Funktionsübersicht</a>, den Abgleich mit etablierten Systemen "
                 "der <a href=\"/vergleich/\">RIS-Vergleich</a>.</p>",
        ),
        # Muster 5b: Grundsätze als Begriffe, mit den Wegen zu Bürgerportal und Schnittstelle
        m.begriffe(
            "Worauf Sie sich verlassen können",
            [
                m.begriff("Öffentlich, was öffentlich ist",
                          "Jede Sitzung, jeder Tagesordnungspunkt, jede Vorlage und jede Anlage ist als öffentlich "
                          "oder nichtöffentlich gekennzeichnet. Nach außen geht nur, was als öffentlich gekennzeichnet "
                          "ist: nach Ihrer Freigabe in den Einstellungen ins Bürgerportal und über die "
                          "<a href=\"/oparl-schnittstelle/\">OParl-Schnittstelle</a>.",
                          link_label="Zum Bürgerinformationssystem", link_url="/buergerinformationssystem/"),
                m.begriff("Nachvollziehbar und verschlüsselt",
                          "Jede Änderung und jeder Zugriff auf Nichtöffentliches steht im Audit-Log. Nichtöffentliche "
                          "Inhalte und sensible Personendaten liegen je Kommune verschlüsselt; die Anmeldung "
                          "unterstützt einen zweiten Faktor.",
                          link_label="Sicherheit im Trust Center", link_url="/trust/"),
                m.begriff("Offen und prüfbar",
                          "Der Quellcode steht unter AGPL-3.0, Ihre IT kann ihn prüfen. Öffentliches geben Sie über "
                          "OParl heraus, Beschlüsse, Berichte und Sitzungsgeld als CSV und JSON.",
                          link_label="Quellcode ansehen", link_url="https://github.com/mandariOSS/mandari"),
                m.begriff("Ihr Betrieb, Ihre Wahl",
                          "Als Dienst aus ISO-27001-zertifizierten Rechenzentren in Deutschland oder per Docker "
                          "Compose in Ihrem eigenen Rechenzentrum.",
                          link_label="Unterlagen für die Vergabe", link_url="/vergabe/"),
            ],
            subline="Sitzungsmanagement heißt Verantwortung für Fristen, Vertrauliches und die Öffentlichkeit. Dafür "
                    "ist mandari Session gebaut.",
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
                           "dokumentieren. Sitzungsmanagement-Software bündelt diese Arbeit in einem System.</p>"},
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
                 "answer": "<p>Per Freigabe in den Einstellungen. Danach erscheinen öffentliche Sitzungen, Vorlagen "
                           "und Beschlüsse im <a href=\"/buergerinformationssystem/\">Bürgerinformationssystem</a> "
                           "und über die OParl-Schnittstelle. Nichtöffentliches bleibt intern, jede Umstellung steht "
                           "im Audit-Log.</p>"},
                {"question": "Können wir unsere Daten aus dem bisherigen System übernehmen?",
                 "answer": "<p>Gremien, Personen und Besetzungen übernehmen wir aus Listen Ihrer Verwaltung. Ihren "
                           "öffentlichen Altbestand liest mandari über OParl ein; er bleibt im Bürgerportal "
                           "durchsuchbar. Die Übernahme dieses Bestands in mandari Session ist für Version 1.0 "
                           "geplant.</p>"
                           "<p>Den Weg für Ihre Kommune klären wir in der Bestandsaufnahme, siehe "
                           "<a href=\"/migration/\">Migration</a>.</p>"},
            ],
        }),
        m.einladung(
            "Sprechen wir über Ihr Sitzungsmanagement.",
            "In 30 Minuten klären wir, wie Ihr Sitzungsmanagement heute arbeitet, was mandari Session in der "
            "Pilotphase leistet und wie ein Umstieg aussieht. Per Video, am Telefon oder persönlich in Münster.",
            "Erstgespräch vereinbaren", KONTAKT,
            link_label="So läuft die Migration", link_url="/migration/",
            wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                  ("Für Vergabestellen", "Unterlagen", "/vergabe/"), ("Preise", "Was mandari kostet", "/preise/")],
        ),
    ]
