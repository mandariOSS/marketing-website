"""
Seed-Inhalt der Seite /anfragen-beantworten/ (mandariOSS/mandari#1488): Antwortentwurf mit Fundstellen in mandari Work.

Die Seite zeigt an einem Fall, wie aus einer Bürger- oder Presseanfrage eine Antwort mit Quellen wird, und sagt
ebenso deutlich, was mandari Work dabei nicht tut. Vorgaben:

* Ein Fall statt einer Funktionsliste: Die Schritte folgen einer Anfrage vom Eingang bis zum Versand.
* Das Bild ist der Gegenstand selbst: der Entwurf mit Fußnoten, markiertem Absatz, Platzhalter und offenen Punkten,
  so groß, dass er sich lesen lässt (``work-anfrage`` in ``marketing/bildschirme.py``, Musterdaten).
* Nichts versprechen, was die Prüfung nicht leistet: Sie gleicht Zahlen und Daten je Absatz ab und ersetzt das
  Gegenlesen nicht (docs/KI.md im Repository mandariOSS/mandari, Abschnitt „Antwortentwurf in Work“).
* KI-Anbieter und Verarbeitungsort nennt nur das Trust Center; diese Seite verweist dorthin und macht selbst keine
  Aussage zum Ort.
* Keine Preise und keine Kostenaussagen; der einzige Verweis auf Kosten ist der Weg „Preise“ im Schlussband.
* Abschnitte nach dem Musterkatalog, nie zweimal dasselbe Muster hintereinander; keine neuen Bausteine.

Die Funktion kommt mit mandari 0.14 in den Betrieb. Die Seite geht erst danach live.

Nach Änderungen: ``refresh_seeded_page anfragen-beantworten --force``.
"""

from __future__ import annotations

from marketing import seeds_muster as m

KI_DOKU = "https://github.com/mandariOSS/mandari/blob/main/docs/KI.md"


def seite():
    """Blockliste von /anfragen-beantworten/."""
    from marketing.management.commands.migrate_pages_to_streamfield import WORK_AUFRUF, WORK_AUFRUF_URL, cta

    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "Auf Anfragen antworten, mit den Fundstellen aus dem Rat.", "title_highlight": "",
            "subline": (
                "Die Lokalzeitung fragt nach dem Radweg, eine Bürgerin nach dem Gewerbegebiet. mandari Work sucht "
                "in den Ratsdaten Ihrer Kommune und schreibt den Antwortentwurf, mit jeder Fundstelle als Fußnote. "
                "Sie prüfen, ergänzen die Haltung Ihrer Fraktion und versenden selbst."
            ),
            "subline_secondary": "",
            "ctas": [cta(WORK_AUFRUF, WORK_AUFRUF_URL),
                     cta("mandari Work für Fraktionen", "/fraktionen/", style="outline")],
            "background_color": "primary",
        }),
        # Muster 11c: ein Fall entlang seiner Schritte, daneben der Entwurf selbst in lesbarer Größe
        m.kette(
            "Donnerstag, 9:30 Uhr: Die Zeitung fragt nach dem Radweg.",
            [
                m.kettenschritt(
                    "Anfrage einfügen",
                    "Sie fügen das Anliegen ein und wählen, ob eine Bürgerin oder die Presse fragt. Die Anrede "
                    "tragen Sie getrennt ein, sie bleibt in mandari.",
                    "Die Recherche läuft, bis zu anderthalb Minuten", ort="ohne Namen und Kontaktdaten"),
                m.kettenschritt(
                    "Entwurf lesen",
                    "mandari Work zerlegt die Anfrage in Einzelfragen und sucht dazu in Vorlagen, Beschlüssen, "
                    "Sitzungen und Dokumenten Ihrer Kommune. Jede Fundstelle steht als Fußnote am Satz und mit "
                    "derselben Nummer im Verzeichnis daneben.",
                    "Brief mit nummerierten Fundstellen"),
                m.kettenschritt(
                    "Prüfen und ergänzen",
                    "Ein Programm gleicht Zahlen und Daten mit dem ab, was die Recherche gefunden hat, und markiert "
                    "Absätze, die Sie ansehen müssen. Wozu die Ratsdaten nichts hergeben, steht getrennt neben dem "
                    "Brief. Die Haltung Ihrer Fraktion tragen Sie am Platzhalter ein.",
                    "Geprüfter Text, offene Punkte geklärt", ort="der Grund steht am Absatz"),
                m.kettenschritt(
                    "Freigeben und versenden",
                    "Mit einem Klick wird aus dem Entwurf ein Dokument: Prüfhinweise und offene Punkte stehen dort "
                    "als Checkliste, dazu Freigabe in der Fraktion, Briefkopf und Export als Word oder PDF. Den "
                    "Versand übernehmen Sie aus Ihrem Postfach.",
                    "Antwort mit Quellenverzeichnis"),
            ],
            produkt="work", bild="work-anfrage", spalten=["Schritt", "Was geschieht", "Ergebnis"],
            subline="Was wurde beschlossen, wann wird gebaut, was kostet der Ausbau? Die Antworten stehen in "
                    "Vorlagen, Niederschriften und Tagesordnungen. mandari Work sucht sie heraus und schreibt den "
                    "Entwurf.",
            anchor="ablauf",
        ),
        # Muster 5b: Grenzen als Zusagen
        m.begriffe(
            "Die Antwort bleibt Ihre.",
            [
                m.begriff("Versendet nichts",
                          "Der Entwurf bleibt in mandari Work und wird erst gespeichert, wenn Sie ihn als Dokument "
                          "übernehmen. Verschickt wird aus Ihrem Mailprogramm."),
                m.begriff("Nimmt keine Haltung ein",
                          "Der Entwurf bewertet keine Parteien und gibt keine Empfehlung. Fragt die Anfrage nach der "
                          "Position Ihrer Fraktion, steht an der Stelle ein Platzhalter, den Sie füllen."),
                m.begriff("Erfindet keine Quelle",
                          "Fundstelle wird nur, was die Recherche in den Ratsdaten gefunden hat. Zahlen und Daten, "
                          "die dort nicht stehen, markiert ein Programm. Das ersetzt Ihr Gegenlesen nicht: "
                          "Maßgeblich bleiben die Fundstellen."),
                m.begriff("Gibt nichts aus Ihrer Fraktion weiter",
                          "An den KI-Dienst gehen nur das Anliegen und öffentliche Ratsdaten. Anrede, Namen, "
                          "Dokumente und Notizen Ihrer Fraktion bleiben in mandari. Eine Anfrage mit Kontaktdaten "
                          "geht nicht hinaus, die Seite sagt, was zu entfernen ist.",
                          link_label="KI-Anbieter im Trust Center", link_url="/trust/"),
            ],
            subline="mandari Work recherchiert und entwirft. Was Ihre Fraktion sagt und was hinausgeht, entscheiden "
                    "Sie.",
            anchor="grenzen",
        ),
        # Muster 5a: woher die Antworten kommen, rechts Stand und Voraussetzungen
        m.randspalte(
            "Die Antworten liegen schon in den Ratsdaten.",
            "<p><strong>Vorlagen und Beschlüsse.</strong> Jede Vorlage mit Beratungsfolge, Beschlusstext und dem "
            "Ergebnis je Gremium.</p>"
            "<p><strong>Sitzungen.</strong> Tagesordnungen und Termine: was beraten wurde und was als Nächstes "
            "ansteht.</p>"
            "<p><strong>Dokumente im Volltext.</strong> Begründungen, Anlagen und Niederschriften, auch aus "
            "gescannten PDFs.</p>"
            "<p><strong>Nur Öffentliches.</strong> Nichtöffentliche Punkte nennt der Entwurf nur als solche, ihr "
            "Inhalt geht in keine Antwort ein.</p>",
            [
                m.rand_fakten("mandari Work", ("Für", "Fraktionen und Geschäftsstellen"), ("Stand", "Offene Beta"),
                              ("Voraussetzung", "KI-Funktionen Ihrer Organisation eingeschaltet")),
                m.rand_links("Mehr dazu", ("mandari Work für Fraktionen", "/fraktionen/"),
                             ("Wie die KI-Funktionen arbeiten", KI_DOKU)),
            ],
            subline="mandari liest die öffentlichen Ratsdaten Ihrer Kommune laufend aus dem "
                    "Ratsinformationssystem ein. Niemand muss Dokumente hochladen, bevor die erste Antwort "
                    "entstehen kann.",
            anchor="ratsdaten",
        ),
        ("accordion_faq", {
            "header": m.kopf("Häufige Fragen zum Antwortentwurf",
                             "Steht Ihre Frage nicht dabei? Schreiben Sie uns."),
            "anchor_id": "faq", "background": "white",
            "rand": [
                m.rand_fakten("Direkt fragen", ("E-Mail", "hello@mandari.de"),
                              ("Antwort", "in der Regel innerhalb eines Werktags")),
                m.rand_links("Zum Nachlesen", ("Sicherheit im Trust Center", "/trust/"),
                             ("Alle Funktionen von mandari Work", "/produkte/#funktionen")),
            ],
            "items": [
                {"question": "Welche Daten gehen an den KI-Dienst?",
                 "answer": "<p>Der Text der Anfrage und die öffentlichen Ratsdaten, die die Recherche dazu findet. "
                           "Anrede, Absender und alle Inhalte Ihrer Fraktion bleiben in mandari. Welchen Anbieter "
                           "mandari einsetzt und wo er verarbeitet, steht im <a href=\"/trust/\">Trust Center</a>.</p>"},
                {"question": "Wie verlässlich ist der Entwurf?",
                 "answer": "<p>Er ist ein Entwurf und als KI-Entwurf gekennzeichnet. Jede Fundstelle führt zu der "
                           "Vorlage oder Sitzung, aus der sie stammt. Zahlen und Daten gleicht ein Programm mit dem "
                           "abgerufenen Material ab und markiert Abweichungen; Aussagen ohne Zahl und Datum prüft es "
                           "nicht.</p><p>Lesen Sie den Entwurf gegen die Fundstellen, bevor Sie ihn versenden.</p>"},
                {"question": "Was geschieht, wenn die Ratsdaten nichts hergeben?",
                 "answer": "<p>Dann steht der Punkt getrennt neben dem Brief, unter „Dazu liegt in den Ratsdaten "
                           "nichts vor“. Sie ergänzen ihn aus eigenem Wissen oder schreiben, dass dazu nichts "
                           "vorliegt.</p>"},
                {"question": "Wird die Anfrage gespeichert?",
                 "answer": "<p>Nein, solange Sie den Entwurf nicht als Dokument übernehmen. Dann liegen Anfrage und "
                           "Entwurf verschlüsselt im Bereich Ihrer Organisation, wie jedes Dokument. Sonst zählt "
                           "mandari nur den Verbrauch.</p>"},
                {"question": "Arbeitet das mit dem Ratsinformationssystem unserer Kommune?",
                 "answer": "<p>Ja, sobald mandari die öffentlichen Ratsdaten Ihrer Kommune einliest: aus mandari "
                           "Session oder über die <a href=\"/oparl-schnittstelle/\">OParl-Schnittstelle</a> Ihres "
                           "Ratsinformationssystems. Ob Ihre Kommune angebunden ist, klären wir im ersten "
                           "Gespräch.</p>"},
            ],
        }),
        m.einladung(
            "Sehen Sie den Weg von der Anfrage zur Antwort.",
            "Wir zeigen Ihnen den Antwortentwurf an den Ratsdaten einer angebundenen Kommune und klären, was für "
            "Ihre Kommune nötig ist. Per Video, am Telefon oder persönlich in Münster.",
            WORK_AUFRUF, WORK_AUFRUF_URL,
            link_label="Preise ansehen", link_url="/preise/",
            wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                  ("Für Fraktionen", "mandari Work", "/fraktionen/"),
                  ("Alle Funktionen", "Funktionsübersicht", "/produkte/#funktionen")],
        ),
    ]
