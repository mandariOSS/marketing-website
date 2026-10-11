"""
Seed-Inhalt der Sachseite /oparl-schnittstelle/ (SEO-Kaufbegriffe, Issue mandariOSS/mandari#939).

Die Seite erklärt OParl und zeigt, was die Schnittstelle von mandari liefert: Ausgabe über alle Kommunen im
Bürgerportal und je Kommune in mandari Session, Übernahme aus dem bisherigen Ratsinformationssystem, Datenkatalog für
Open-Data-Portale.

Adresse: ``/oparl-schnittstelle/``, nicht ``/oparl/``. Unter ``/oparl/`` liegt in jeder Installation die
OParl-Schnittstelle der mandari-Anwendung selbst (Caddyfile im Repository mandariOSS/mandari leitet ``/oparl/*`` an die
Anwendung, ``https://mandari.de/oparl/`` antwortet mit JSON). Eine Website-Seite dort wäre nie erreichbar.

Vorgaben wie bei /ratsinformationssystem/ (``marketing/seeds_ris.py``):

* keine Preise und keine Kostenaussagen; der einzige Verweis auf Kosten ist der Weg „Preise“ im Schlussband,
* keine Aussagen zu KI (mandariOSS/mandari#950), deshalb ohne die Zusammenfassungen der Aggregations-API,
* Fakten nur aus der Dokumentation im Repository mandariOSS/mandari (docs/OPARL_API.md, docs/SESSION_OPARL_API.md,
  docs/DCAT_KATALOG.md) und aus mandari.de; was in der Installation erst eingeschaltet werden muss (Änderungsfeed,
  Datenkatalog), steht nicht als verfügbar da,
* OParl als offener Standard ohne Vereinnahmung der Community; regisafe nie als Beispiel für OParl,
* Abschnitte nach dem Musterkatalog, nie zweimal dasselbe Muster hintereinander.

Nach Änderungen: ``refresh_seeded_page oparl-schnittstelle --force``.
"""

from __future__ import annotations

from marketing import seeds_muster as m

KONTAKT = "/kontakt/?subject=OParl-Schnittstelle#termin"
DOKU_AGGREGATOR = "https://docs.mandari.de/insight/oparl-api/"
DOKU_SESSION = "https://docs.mandari.de/session/oparl-api/"


def seite():
    """Blockliste von /oparl-schnittstelle/."""
    from marketing.management.commands.migrate_pages_to_streamfield import cta

    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "OParl-Schnittstelle: Ratsdaten maschinenlesbar.", "title_highlight": "",
            "subline": (
                "mandari stellt Sitzungen, Vorlagen, Beschlüsse und Dokumente nach dem offenen Standard OParl 1.1 "
                "bereit: lesend, ohne Anmeldung und für jede Anwendung."
            ),
            "subline_secondary": "",
            "ctas": [cta("Erstgespräch vereinbaren", KONTAKT),
                     cta("API-Dokumentation", DOKU_AGGREGATOR, style="outline")],
            "background_color": "primary",
        }),
        # Muster 5a: der Standard in drei Stichworten, rechts die Eckdaten der Schnittstelle
        m.randspalte(
            "Was ist OParl?",
            "<p><strong>Offene Daten statt PDF-Stapel.</strong> Presse, Wissenschaft, Zivilgesellschaft und andere "
            "Anwendungen lesen Ratsdaten direkt aus, statt sie von Webseiten abzuschreiben.</p>"
            "<p><strong>Ein Weg für viele Systeme.</strong> Wer OParl liest, liest jedes Ratsinformationssystem, das "
            "den Standard spricht, auf dieselbe Weise, ob ALLRIS, SessionNet von Somacos oder SD.NET RIM.</p>"
            "<p><strong>Unabhängig vom Anbieter.</strong> Ihre Ratsdaten liegen in einem offenen Format. Beim Wechsel "
            "kommen sie strukturiert mit, und Sie bekommen sie jederzeit vollständig heraus.</p>",
            [
                m.rand_fakten("Die Schnittstelle von mandari", ("Standard", "OParl 1.1"),
                              ("Zugang", "lesend, ohne Anmeldung"), ("Format", "JSON"),
                              ("Übernahme", "aus OParl 1.0 und 1.1")),
                m.rand_links("Zum Nachlesen", ("OParl-Spezifikation", "https://oparl.org/spezifikation/"),
                             ("Was ein Ratsinformationssystem ist", "/ratsinformationssystem/")),
            ],
            subline="OParl ist der offene Standard für die Schnittstelle von Ratsinformationssystemen. Er legt fest, "
                    "wie Sitzungen, Vorlagen, Beschlüsse, Gremien, Personen und Dokumente maschinenlesbar "
                    "bereitstehen, unabhängig vom Hersteller.",
            anchor="was-ist-oparl",
        ),
        # Muster 3: was die Schnittstelle liefert, mit Stand
        m.register(
            "Was die Schnittstelle liefert",
            [
                m.gruppe(
                    "Zwei Ausgaben",
                    m.zeile("Über alle Kommunen",
                            "Ein Endpunkt für die öffentlichen Ratsdaten aller Kommunen im "
                            "<a href=\"/buergerinformationssystem/\">Bürgerportal</a>, statt jede Kommune einzeln "
                            "abzufragen.",
                            url=DOKU_AGGREGATOR, ort="Dokumentation", stand="Verfügbar", status="da"),
                    m.zeile("Je Kommune in mandari Session",
                            "Jede Kommune, die ihr <a href=\"/sitzungsmanagement/\">Sitzungsmanagement</a> in "
                            "mandari Session führt, hat eine eigene Schnittstelle, sobald die Verwaltung sie "
                            "freischaltet. Sie gibt nur Öffentliches aus; die Lizenz der Daten wählt die Kommune.",
                            url=DOKU_SESSION, ort="Dokumentation", stand="Verfügbar", status="da"),
                ),
                m.gruppe(
                    "Für Abnehmer",
                    m.zeile("Abgleich seit dem letzten Abruf",
                            "Zeitfilter wie modified_since liefern nur, was sich geändert hat. Gelöschte Objekte "
                            "bleiben als Tombstone abrufbar, damit Kopien sie entfernen.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Bedingte Anfragen",
                            "Jede Antwort trägt einen ETag; unveränderte Seiten kommen als 304 ohne Inhalt zurück.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Dokumente",
                            "Dateien über stabile Adressen, auch wenn der Server der Kommune gerade nicht erreichbar "
                            "ist.", stand="Verfügbar", status="da"),
                ),
                m.gruppe(
                    "Übernahme und offene Daten",
                    m.zeile("Import aus dem bisherigen RIS",
                            "Sitzungen, Tagesordnungen, Vorlagen mit Beratungsfolge, Gremien, Personen, "
                            "Mitgliedschaften, Wahlperioden, Orte und Dokumente kommen strukturiert mit.",
                            stand="Verfügbar", status="da"),
                    m.zeile("Open-Data-Portale",
                            "Ein Katalog je Kommune nach DCAT-AP.de verweist auf die Schnittstelle; Landesportale und "
                            "GovData können ihn einsammeln. Er ist in der Installation einschaltbar, die Anbindung an "
                            "die Portale folgt.", stand="Geplant 2027", status="offen"),
                ),
            ],
            spalten=["Was", "Wie es funktioniert", "Stand"],
            subline="Für Entwickler:innen, Open-Data-Verantwortliche und IT-Leitungen: was die Schnittstelle heute "
                    "leistet.",
            anchor="leistung",
            bestand="{da} von {gesamt} sind heute verfügbar.",
            note=f"<p>Alle Endpunkte, Felder und Beispiele stehen in der <a href=\"{DOKU_AGGREGATOR}\">"
                 "API-Dokumentation</a>, der Quellcode auf <a href=\"https://github.com/mandariOSS/mandari\">"
                 "GitHub</a>.</p>",
        ),
        # Muster 2: Anbindung eines Systems mit OParl; Ergebnis mit dem Weg zur Migration
        m.schrittfolge(
            "So kommt Ihr Bestand zu mandari",
            [
                ("Endpunkt nennen",
                 "Sie nennen uns die Adresse der OParl-Schnittstelle Ihres bisherigen Systems.", ""),
                ("Testabgleich",
                 "Wir gleichen Ihren Bestand zur Probe ab und klären offene Punkte.", ""),
                ("Produktivbetrieb",
                 "Ihre Ratsdaten erscheinen im Bürgerportal und stehen über die Schnittstelle bereit.",
                 "typisch 1 bis 2 Wochen"),
            ],
            subline="Spricht Ihr Ratsinformationssystem OParl, ist die Anbindung kurz: drei Schritte bis zum "
                    "Produktivbetrieb.",
            anchor="anbindung",
            ergebnis={"titel": "Umstieg auf mandari Session",
                      "text": "Soll mandari Session Ihr bisheriges System ablösen, rechnen wir vom ersten Termin an "
                              "mit 7 bis 14 Wochen.",
                      "link_label": "So läuft die Migration", "link_url": "/migration/"},
            note="<p>Ohne OParl-Schnittstelle klären wir die Anbindung gemeinsam, gegebenenfalls mit einem eigenen "
                 "Adapter: <a href=\"/kommunen/#anbindung\">Zwei Wege zur Anbindung</a>.</p>",
        ),
        ("accordion_faq", {
            "header": m.kopf("Häufige Fragen zur OParl-Schnittstelle",
                             "Steht Ihre Frage nicht dabei? Schreiben Sie uns."),
            "anchor_id": "faq", "background": "white",
            "rand": [
                m.rand_fakten("Direkt fragen", ("E-Mail", "hello@mandari.de"),
                              ("Antwort", "in der Regel innerhalb eines Werktags")),
                m.rand_links("Zum Nachlesen", ("OParl-API des Bürgerportals", DOKU_AGGREGATOR),
                             ("OParl-API von mandari Session", DOKU_SESSION), ("Quellennachweise", "/quellen/"),
                             ("RIS-Vergleich", "/vergleich/")),
            ],
            "items": [
                {"question": "Was ist OParl?",
                 "answer": "<p>OParl ist der offene Standard für die Schnittstelle von Ratsinformationssystemen. Er "
                           "beschreibt, wie Sitzungen, Vorlagen, Beschlüsse, Gremien, Personen und Dokumente "
                           "maschinenlesbar bereitstehen, unabhängig vom Hersteller.</p>"},
                {"question": "Welche OParl-Versionen unterstützt mandari?",
                 "answer": "<p>mandari gibt alle Daten nach OParl 1.1 aus. Übernehmen kann mandari Daten aus "
                           "Systemen mit OParl 1.0 und 1.1.</p>"},
                {"question": "Brauche ich einen Zugang zur Schnittstelle?",
                 "answer": "<p>Nein. Die Schnittstelle ist lesend und ohne Anmeldung nutzbar, auch direkt aus "
                           "Webanwendungen im Browser. Damit sie für alle schnell bleibt, begrenzt sie die Zahl der "
                           "Anfragen je Adresse.</p>"},
                {"question": "Gibt die Schnittstelle nichtöffentliche Inhalte aus?",
                 "answer": "<p>Nein. Sie liefert ausschließlich, was öffentlich ist. Wird ein Objekt nachträglich "
                           "nichtöffentlich oder gelöscht, erscheint es nur noch als gekürztes Objekt mit der "
                           "Markierung „gelöscht“, damit Kopien es entfernen.</p>"},
                {"question": "Unter welcher Lizenz stehen die Daten?",
                 "answer": "<p>Die Lizenz bestimmt die Kommune. In mandari Session wählt sie etwa die Datenlizenz "
                           "Deutschland oder eine Creative-Commons-Lizenz; bei Daten aus anderen Systemen gibt "
                           "mandari die Angabe der Kommune weiter.</p>"},
                {"question": "Können wir unser bisheriges RIS über OParl ablösen?",
                 "answer": "<p>Ja. Spricht Ihr System OParl, übernehmen wir Sitzungen, Vorlagen, Gremien, Personen "
                           "und Dokumente strukturiert; Sonderfelder und Bestände ohne OParl-Export klären wir in der "
                           "Bestandsaufnahme. Wie der Umstieg abläuft, zeigt die Seite "
                           "<a href=\"/migration/\">Migration</a>.</p>"},
            ],
        }),
        m.einladung(
            "Sprechen wir über Ihre Ratsdaten.",
            "In 30 Minuten klären wir, wie Ihr Bestand über OParl zu mandari kommt und wie Ihre Daten offen "
            "bereitstehen. Per Video, am Telefon oder persönlich in Münster.",
            "Erstgespräch vereinbaren", KONTAKT,
            link_label="API-Dokumentation", link_url=DOKU_AGGREGATOR,
            wege=[("E-Mail", "hello@mandari.de", ""),
                  ("Quellcode", "auf GitHub", "https://github.com/mandariOSS/mandari"),
                  ("Für Vergabestellen", "Unterlagen", "/vergabe/"), ("Preise", "Was mandari kostet", "/preise/")],
        ),
    ]
