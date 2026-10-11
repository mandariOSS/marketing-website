"""
Seed-Inhalt der Sachseite /buergerinformationssystem/ (SEO-Kaufbegriffe, Issue mandariOSS/mandari#939).

Die Seite erklärt den Begriff Bürgerinformationssystem (BIS) und zeigt das Bürgerportal mandari Insight, das unter
/insight/ im Einsatz ist. Vorgaben wie bei /ratsinformationssystem/ (``marketing/seeds_ris.py``):

* keine Preise und keine Kostenaussagen (auch nicht „kostenlos“); der einzige Verweis auf Kosten ist der Weg „Preise“
  im Schlussband,
* keine Aussagen zu KI (Anbieter noch nicht freigegeben, mandariOSS/mandari#950), deshalb ohne die
  Zusammenfassungen im Bürgerportal und ohne das Bild des Bürgerportals (sein Menü zeigt den KI-Assistenten),
* keine Kommunen als Kunden; Zahlen nur mit Stand (``KENNZAHLEN`` in ``marketing/seeds_unternehmen.py``, dieselben
  wie auf /presse/ und /transparenz/),
* Faktentreue vor Glanz: nur Funktionen, die das Bürgerportal in Produktion heute hat (Dokumentation
  docs.mandari.de/insight/). Die Ratsfragen sind pausiert, Abos zu Suchbegriffen und Nachbarschaft ausgeschaltet;
  beides fehlt. Synonyme nur mit Beispielen aus ``insight_search/synonyms.py`` (Repository mandariOSS/mandari),
  die unscharfe Suche ist ein Rückfall. Was mandari Session voraussetzt, trägt das Etikett der Pilotphase,
* Abschnitte nach dem Musterkatalog, nie zweimal dasselbe Muster hintereinander.

Nach Änderungen: ``refresh_seeded_page buergerinformationssystem --force``.
"""

from __future__ import annotations

from marketing import seeds_muster as m

KONTAKT = "/kontakt/?subject=Buergerinformationssystem-Demo#termin"


def seite():
    """Blockliste von /buergerinformationssystem/."""
    from marketing.management.commands.migrate_pages_to_streamfield import cta
    from marketing.seeds_unternehmen import KENNZAHLEN, KENNZAHLEN_STAND

    dokumente, vorgaenge, sitzungen, kommunen = (wert for wert, _ in KENNZAHLEN)

    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "Ein Bürgerinformationssystem, das man versteht.", "title_highlight": "",
            "subline": (
                "mandari Insight macht Sitzungen, Vorlagen und Beschlüsse Ihrer Kommune für alle zugänglich: im "
                "Volltext durchsuchbar, auf der Karte verortet, ohne Anmeldung und ohne Tracking."
            ),
            "subline_secondary": "",
            "ctas": [cta("Erstgespräch vereinbaren", KONTAKT),
                     cta("Bürgerportal ansehen", "/insight/", style="outline")],
            "background_color": "primary",
        }),
        # Muster 5a: Begriff, warum es ein gutes BIS braucht, rechts die Eckdaten
        m.randspalte(
            "Was ist ein Bürgerinformationssystem?",
            "<p><strong>Öffentlich heißt nicht auffindbar.</strong> Oft stehen Ratsinformationen als lange Listen "
            "von PDF-Dateien im Netz. Wer wissen will, was der Rat zur eigenen Straße beschlossen hat, muss Sitzung "
            "und Vorlagennummer schon kennen.</p>"
            "<p><strong>Für alle, die mitreden wollen.</strong> Bürger:innen, Presse und Zivilgesellschaft fragen, "
            "was ansteht, was beschlossen wurde und was daraus geworden ist. In einem guten "
            "Bürgerinformationssystem finden sie Antworten, ohne Sitzung und Vorlagennummer zu kennen.</p>"
            "<p><strong>Weniger Einzelanfragen.</strong> Wer selbst findet, muss nicht nachfragen. Das entlastet "
            "Verwaltung und Rat.</p>",
            [
                m.rand_fakten("Auf einen Blick", ("Anmeldung", "keine"), ("Tracking und Werbung", "keine"),
                              ("Inhalte", "nur, was die Kommune öffentlich bereitstellt"),
                              ("Schnittstelle", "OParl 1.1")),
                m.rand_links("Mehr dazu", ("Was ein Ratsinformationssystem ist", "/ratsinformationssystem/")),
            ],
            subline="Ein Bürgerinformationssystem, kurz BIS, ist der öffentliche Teil des Ratsinformationssystems "
                    "einer Kommune. Dort finden alle ohne Anmeldung Sitzungstermine, Tagesordnungen, Vorlagen und "
                    "Beschlüsse.",
            anchor="was-ist-ein-bis",
        ),
        # Muster 5b: was das Bürgerportal heute kann
        m.begriffe(
            "Finden, verstehen, dranbleiben",
            [
                m.begriff("Volltextsuche",
                          "Die Suche reicht über Vorlagen, Sitzungen, Beschlüsse und den Text der Dokumente, auch "
                          "eingescannter. Sie kennt kommunalpolitische Synonyme: Wer „B-Plan“ sucht, findet auch den "
                          "Bebauungsplan. Findet die genaue Suche kaum etwas, sucht sie unscharf weiter, etwa bei "
                          "Tippfehlern."),
                m.begriff("Karte und Umkreis",
                          "Vorgänge stehen auf der Karte. Die Umkreissuche zeigt, was rund um eine Adresse beraten "
                          "wird."),
                m.begriff("Termine im eigenen Kalender",
                          "Der Sitzungskalender zeigt die Sitzungen mit Tagesordnung, als Liste oder im Jahresplan. "
                          "Als Kalender-Abo kommen die Termine in Outlook, Apple Kalender oder Google Kalender, auf "
                          "Wunsch nur für ein Gremium."),
                m.begriff("Gremien und Personen",
                          "Rat, Ausschüsse und Fraktionen mit ihren Mitgliedern, jede Person mit ihren Mandaten."),
                m.begriff("Was aus Beschlüssen wird",
                          "Gibt die Verwaltung den Umsetzungsstand frei, zeigt das Portal, was aus einem Beschluss "
                          "geworden ist: beschlossen, in Umsetzung, umgesetzt. Einzelne Beschlüsse lassen sich "
                          "abonnieren.",
                          marke="mit mandari Session (Pilotphase)"),
                m.begriff("Für alle bedienbar",
                          "Bedienung per Tastatur, Kontrast von mindestens 4,5:1, Dunkelmodus und Darstellung bis "
                          "320 px Breite. Laut unserer Erklärung zur Barrierefreiheit ist mandari teilweise konform "
                          "mit der BITV 2.0; an Karten und komplexen Filtern arbeiten wir.",
                          link_label="Erklärung zur Barrierefreiheit", link_url="/barrierefreiheit/"),
            ],
            subline="Was mandari Insight Bürger:innen bietet, ohne Konto und ohne Vorwissen.",
            anchor="funktionen",
            note="<p>Die Ratsdaten im Bürgerportal sind auch maschinenlesbar: über die "
                 "<a href=\"/oparl-schnittstelle/\">OParl-Schnittstelle</a>.</p>",
        ),
        # Muster 8: zwei Wege ins Bürgerportal nach denselben Kriterien
        m.vergleich(
            "Zwei Wege ins Bürgerportal",
            [("Mit mandari Session", "Pilotphase, Veröffentlichung per Freigabe"),
             ("Mit Ihrem bisherigen RIS", "Über die OParl-Schnittstelle")],
            [
                ("Ihre Kommune", ["führt den Sitzungsdienst in mandari Session",
                                  "nutzt ein System mit OParl-Schnittstelle, etwa ALLRIS, SessionNet von Somacos oder "
                                  "SD.NET RIM, und muss nichts wechseln"]),
                ("Veröffentlichung", ["per Freigabe in den Einstellungen, jede Umstellung im Audit-Log",
                                      "das Bürgerportal liest die öffentlichen Daten fortlaufend über OParl"]),
                ("Was erscheint", ["was als öffentlich gekennzeichnet ist: Gremien, Personen, Sitzungen, Vorlagen "
                                   "und Anlagen",
                                   "was Ihr System über OParl öffentlich bereitstellt"]),
                ("Umsetzungsstand von Beschlüssen", ["nach Ihrer Freigabe, mit eigener Statusmeldung je Beschluss",
                                                     "–"]),
            ],
            subline="Ob Ihre Verwaltung mandari Session nutzt oder ihr bisheriges Ratsinformationssystem behält: "
                    "Das Bürgerportal arbeitet mit beiden.",
            anchor="wege",
            note="<p>Ihr System spricht noch kein OParl? Den begleiteten Weg beschreibt die Seite "
                 "<a href=\"/kommunen/#anbindung\">für Verwaltungen</a>.</p>",
        ),
        # Muster 9a: das Bürgerportal im Einsatz, Zahlen mit Stand (ohne Bild, siehe oben)
        m.zahlensatz(
            "Das Bürgerportal im Einsatz",
            f"Am {KENNZAHLEN_STAND} machte das Bürgerportal <b>{dokumente}</b> Dokumente, <b>{vorgaenge}</b> "
            f"Vorgänge und Vorlagen und <b>{sitzungen}</b> Sitzungen aus <b>{kommunen}</b> Kommunen und "
            "Körperschaften im Volltext durchsuchbar.",
            rand="<p><strong>So zählen wir:</strong> den Bestand im Bürgerportal am Stichtag, nicht Besuche. Ist "
                 "eine Quelle länger nicht erreichbar, nennt das Portal den Datenstand.</p>"
                 "<p><a href=\"/insight/\">Bürgerportal öffnen</a></p>",
            anchor="im-einsatz",
        ),
        ("accordion_faq", {
            "header": m.kopf("Häufige Fragen zum Bürgerinformationssystem",
                             "Steht Ihre Frage nicht dabei? Schreiben Sie uns."),
            "anchor_id": "faq", "background": "white",
            "rand": [
                m.rand_fakten("Direkt fragen", ("E-Mail", "hello@mandari.de"),
                              ("Antwort", "in der Regel innerhalb eines Werktags")),
                m.rand_links("Zum Nachlesen", ("Dokumentation zum Bürgerportal", "https://docs.mandari.de/insight/"),
                             ("OParl-Schnittstelle", "/oparl-schnittstelle/"),
                             ("Barrierefreiheit", "/barrierefreiheit/"), ("Quellennachweise", "/quellen/")),
            ],
            "items": [
                {"question": "Was ist ein Bürgerinformationssystem?",
                 "answer": "<p>Ein Bürgerinformationssystem (BIS) ist der öffentliche Teil des "
                           "Ratsinformationssystems einer Kommune. Bürger:innen, Presse und Zivilgesellschaft finden "
                           "dort ohne Anmeldung Sitzungstermine, Tagesordnungen, Vorlagen und Beschlüsse.</p>"},
                {"question": "Was unterscheidet Bürgerinformationssystem und Ratsinformationssystem?",
                 "answer": "<p>Das <a href=\"/ratsinformationssystem/\">Ratsinformationssystem</a> ist der "
                           "Oberbegriff für die Software der Gremienarbeit. Das Bürgerinformationssystem ist sein "
                           "öffentlicher Teil; dazu kommen das "
                           "<a href=\"/sitzungsmanagement/\">Sitzungsmanagement</a> der Verwaltung und der Zugang "
                           "der Ratsmitglieder.</p>"},
                {"question": "Braucht unsere Kommune mandari Session für das Bürgerportal?",
                 "answer": "<p>Nein. Spricht Ihr Ratsinformationssystem OParl, liest das Bürgerportal die "
                           "öffentlichen Daten direkt daraus. Mit mandari Session (Pilotphase) veröffentlichen Sie per "
                           "Freigabe in den Einstellungen und können zusätzlich den Umsetzungsstand von Beschlüssen "
                           "freigeben.</p>"},
                {"question": "Welche Inhalte erscheinen im Bürgerportal?",
                 "answer": "<p>Das Bürgerportal zeigt nur, was in mandari Session als öffentlich gekennzeichnet ist "
                           "oder was Ihr bisheriges System über OParl öffentlich bereitstellt: Sitzungen und "
                           "Tagesordnungen, Vorlagen, Beschlüsse, Gremien und Personen. Nichtöffentliche "
                           "Sitzungsteile und interne Vermerke gehören nicht dazu.</p>"},
                {"question": "Wie barrierefrei ist das Bürgerportal?",
                 "answer": "<p>Laut unserer Erklärung zur Barrierefreiheit (Stand der Prüfung April 2026) ist mandari "
                           "teilweise konform mit der BITV 2.0. An Karten, komplexen Filtern und der Beschriftung "
                           "von Symbolen arbeiten wir; den Stand je Bereich nennt die "
                           "<a href=\"/barrierefreiheit/\">Erklärung zur Barrierefreiheit</a>.</p>"},
                {"question": "Braucht man ein Konto?",
                 "answer": "<p>Nein. Das Bürgerportal ist ohne Anmeldung nutzbar, ohne Tracking und ohne Werbung. "
                           "Auch das Kalender-Abo der Sitzungstermine funktioniert ohne Konto.</p>"},
            ],
        }),
        m.einladung(
            "Machen wir Ihre Ratsarbeit auffindbar.",
            "In 30 Minuten klären wir, wie Ihre Ratsinformationen ins Bürgerportal kommen: mit mandari Session oder "
            "über die OParl-Schnittstelle Ihres bisherigen Systems. Per Video, am Telefon oder persönlich in Münster.",
            "Erstgespräch vereinbaren", KONTAKT,
            link_label="Bürgerportal ansehen", link_url="/insight/",
            wege=[("E-Mail", "hello@mandari.de", ""), ("Für Verwaltungen", "mandari Session", "/kommunen/"),
                  ("Im Überblick", "Alle Produkte", "/produkte/"), ("Preise", "Was mandari kostet", "/preise/")],
        ),
    ]
