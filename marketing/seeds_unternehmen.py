"""
Seed-Inhalte der Unternehmensseiten: /unternehmen/, /karriere/, /presse/, /partner/, /open-source/.

Zusammengeführt aus mandari.de und mandari.dev (Website-Relaunch 2026). Sprache nach dem
Leitfaden „mandari-texte“: Sie-Form, nur /karriere/ in Du-Form. Gestaltung nach „Design ohne
KI-Slop“: Hero mit genau einem Aufruf, keine Pillen, keine Kartenraster, Listen nur für echte
Aufzählungen, Schritte nur für echte Abfolgen.

Die Definitionen hängt `migrate_pages_to_streamfield.get_marketing_definitions()` ein; Live-Seiten
aktualisiert `python manage.py refresh_seeded_page <slug> --force`.

Die Angaben zum Unternehmen (/unternehmen/#angaben) und das Logo-Paket (/presse/#material) stehen
bewusst nicht hier: Sie kommen aus „Einstellungen → Unternehmensangaben“ bzw. static/brand/ und
werden von templates/company/*.html eingefügt.
"""

from __future__ import annotations

# Kennzahlen aus dem Bürgerportal mandari Insight – Stand und Werte gehören zusammen.
KENNZAHLEN_STAND = "2. Oktober 2026"
KENNZAHLEN = [
    ("204.819", "Dokumente im Volltext durchsuchbar"),
    ("91.662", "Vorgänge und Vorlagen"),
    ("13.903", "Sitzungen"),
    ("5", "Kommunen und Körperschaften im Bürgerportal"),
]

BEWERBUNG = "bewerbung@mandari.de"
PRESSE = "presse@mandari.de"


# ── Bausteine ──────────────────────────────────────────────────────────────


def _hdr(title, subline="", anchor=""):
    from marketing.management.commands.migrate_pages_to_streamfield import hdr

    return hdr(title=title, subline=subline, anchor_id=anchor)


def _cta(label, url):
    from marketing.management.commands.migrate_pages_to_streamfield import cta

    return cta(label, url, "", "primary")


def _hero(title, subline, *, cta_label="", cta_url="", secondary=""):
    return ("hero", {
        "badge_text": "", "badge_icon": "", "badge_color": "primary",
        "title": title, "title_highlight": "",
        "subline": subline, "subline_secondary": secondary,
        "ctas": [_cta(cta_label, cta_url)] if cta_label else [],
        "background_color": "gray",
    })


def _section(title, body, *, anchor="", subline="", background="white", aside=""):
    """Fließtext (Block richtext_section); ``aside`` steht rechts daneben (Randspalte)."""
    return ("richtext_section", {"header": _hdr(title, subline, anchor), "body": body, "aside": aside,
                                 "background": background})


def _row(title, text, *, label="", status="", link_label="", link_url=""):
    return {"title": title, "label": label, "status": status, "text": f"<p>{text}</p>",
            "link_label": link_label, "link_url": link_url, "anchor_id": ""}


def _split_rows_available() -> bool:
    from marketing.blocks import MarketingStreamBlock

    return "split_rows" in MarketingStreamBlock.base_blocks


def _rows(title, rows, *, anchor="", subline="", note="", background="white", layout="raster"):
    """Einträge (Block split_rows): Titel über dem Text im Raster oder als Zeitleiste (``layout``).

    Übergang: Solange der Block split_rows im Code fehlt, entsteht derselbe Inhalt als
    Richtext-Abschnitt (Zwischenüberschrift und Absatz je Zeile).
    """
    if _split_rows_available():
        return ("split_rows", {"header": _hdr(title, subline, anchor), "layout": layout, "rows": rows,
                               "note": note, "background": background})
    body = ""
    for row in rows:
        heading = f"{row['title']}: {row['label']}" if row["label"] else row["title"]
        if row["status"]:
            heading += f" ({row['status']})"
        body += f"<h3>{heading}</h3>{row['text']}"
        if row["link_label"] and row["link_url"]:
            body += f'<p><a href="{row["link_url"]}">{row["link_label"]}</a></p>'
    return _section(title, body + note, anchor=anchor, subline=subline, background=background)


def _steps(title, steps, *, anchor="", subline="", note="", background="white"):
    """Echte Abfolge (Block step_process): Nummer, Titel, ein Satz."""
    return ("step_process", {
        "header": _hdr(title, subline, anchor),
        "columns": "4" if len(steps) >= 4 else "3",
        "steps": [
            {"number": str(number), "color": "primary", "icon": "arrow-right", "title": step_title,
             "description": text, "duration": "", "meta_text": ""}
            for number, (step_title, text) in enumerate(steps, start=1)
        ],
        "background": background,
        "note_html": note,
    })


def _invitation(title, subline, label, url):
    return ("gradient_cta", {"title": title, "subline": subline, "ctas": [_cta(label, url)],
                             "gradient_from": "primary"})


# ── Seiten ─────────────────────────────────────────────────────────────────


def get_company_page_definitions() -> dict:
    from marketing import seeds_muster as m

    return {
        # ════════════════════════════════════════════════════════════
        # /unternehmen/ — Mission, Wertekompass, Geschäftsmodell, Wegmarken
        # (Angaben zum Unternehmen: templates/company/_angaben.html)
        # ════════════════════════════════════════════════════════════
        "unternehmen": [
            _hero(
                "Wir bauen die digitale Infrastruktur der lokalen Demokratie.",
                "mandari ist ein GovTech-Startup aus Münster. Wir sind überzeugt: Software, die das "
                "Gemeinwesen trägt, muss offen, sicher und für alle verständlich sein.",
                cta_label="Erstgespräch vereinbaren", cta_url="/kontakt/#termin",
            ),
            # Muster 6b: die Mission als Leitsatz, die Begründung rechts versetzt darunter
            m.leitsatz(
                "Wir machen Kommunalpolitik für alle zugänglich – und geben Verwaltungen die Werkzeuge, die sie "
                "dafür brauchen.",
                "<p>Was den Alltag einer Stadt bestimmt, entscheidet sich im Rat und in seinen Ausschüssen: "
                "der Bebauungsplan, der Kita-Ausbau, die neue Buslinie. Die Unterlagen dazu sind öffentlich. "
                "Wer sie sucht, braucht trotzdem Geduld, Vorwissen und das richtige PDF aus dem richtigen Jahr.</p>"
                "<p>Sitzungsdienste stemmen ihre Arbeit mit Software, die nie dafür gedacht war, Daten zu teilen. "
                "Ehrenamtliche Politiker:innen bereiten sich nach Feierabend mit Papierstapeln und Mailketten auf "
                "Entscheidungen vor, die Millionen bewegen.</p>"
                "<p><strong>Das geht besser.</strong> Wir bauen Software, die alle drei Seiten zusammenbringt – "
                "und wir bauen sie offen, damit sie den Kommunen gehört und nicht uns.</p>"
                "<p><strong>Unsere Vision:</strong> eine offene Verwaltungswelt. Jede Kommune arbeitet mit Software, "
                "deren Code sie kennt, deren Daten ihr gehören und deren Anbieter sie frei wählen kann.</p>",
                anchor="warum",
            ),
            # Muster 5b: Werte als Begriffe in der Marginalie
            m.begriffe(
                "Unser Wertekompass",
                [
                    m.begriff("Demokratie stärken",
                              "Vertrauen in Politik entsteht, wenn Entscheidungen nachvollziehbar sind. Wir zeigen "
                              "Ratsdaten vollständig und unverändert und arbeiten mit allen demokratischen Parteien "
                              "gleichermaßen."),
                    m.begriff("Offen aus Überzeugung",
                              "Unser gesamter Code steht unter AGPL-3.0. Öffentliches Geld verdient öffentlichen Code: "
                              "prüfbar, wiederverwendbar, unabhängig von uns."),
                    m.begriff("Souverän und sicher",
                              "Betrieb in deutschen Rechenzentren, Daten in der Hand der Kommune, Export jederzeit. "
                              "Digitale Souveränität ist bei uns der Normalfall."),
                    m.begriff("Für alle gemacht",
                              "Das Bürgerportal ist kostenlos und braucht keine Anmeldung. Wir gestalten barrierearm "
                              "und schreiben so, dass man uns versteht."),
                    m.begriff("Verlässlich",
                              "Wir sagen, was fertig ist und was kommt – mit Datum und Verbindlichkeit. Verwaltungen "
                              "planen in Haushaltsjahren. Wir auch."),
                    m.begriff("Nah an der Praxis",
                              "Wir entwickeln mit Sitzungsdiensten, Fraktionen und Bürger:innen, nicht über ihre Köpfe "
                              "hinweg. Pilotkommunen gestalten die Roadmap mit."),
                ],
                anchor="werte", subline="Sechs Zusagen. Wenn Ziele in Konflikt geraten, entscheiden sie.",
            ),
            # Muster 8, Variante „Davon leben wir / Davon nie“
            m.vergleich(
                "Ein Geschäftsmodell, so offen wie unser Code",
                [("Davon leben wir", "Leistung, die Sie beauftragen"), ("Davon nie", "was es bei uns nicht gibt")],
                [
                    ("Software", ["<strong>Betrieb:</strong> Wir betreiben mandari für Fraktionen und ab dem "
                                  "Pilotbetrieb auch für Verwaltungen – sicher, aktuell, aus Deutschland.",
                                  "<strong>Lizenzgebühren:</strong> Der Code steht unter AGPL-3.0."]),
                    ("Selbstbetrieb", ["<strong>Betreuung:</strong> Wer mandari selbst betreibt, sichert sich "
                                       "Unterstützung und Wartung vertraglich.",
                                       "<strong>Datenhandel:</strong> Ihre Daten sind nicht unser Geschäft."]),
                    ("Umstieg", ["<strong>Einführung:</strong> Datenübernahme aus dem Altsystem, Einrichtung und "
                                 "Schulung – damit der Umstieg gelingt.",
                                 "<strong>Werbung:</strong> keine, auch nicht im Bürgerportal."]),
                    ("Finanzierung", ["Einnahmen aus diesen Leistungen",
                                      "<strong>Investoren,</strong> die morgen den Kurs ändern"]),
                ],
                subline="Wir verdienen unser Geld mit Leistung, nicht mit Lizenzen.",
                anchor="geschaeftsmodell",
                note='<p><a href="/preise/">Preise ansehen</a></p>',
            ),
            # Muster 1a als Chronik: ein Jahr maßstäblich, Version 1.0 am Ende
            m.zeitskala(
                "Wir stehen am Anfang. Genau da wollen wir sein.",
                subline="Vom ersten öffentlichen Commit zur Plattform für die offene Verwaltung.",
                anchor="wegmarken",
                tage=365,
                marken=[
                    m.marke(0, "Januar", "Der erste öffentliche Commit"),
                    m.marke(185, "Juli", "mandari 0.9 geht online"),
                    m.marke(269, "September", "mandari 0.11"),
                    m.marke(280, "Herbst", "Transparenz wird Standard"),
                    m.marke(365, "2027", "Version 1.0", offen=True),
                ],
                skala=[m.skalenpunkt(0, "Januar 2026"), m.skalenpunkt(90, "April"), m.skalenpunkt(181, "Juli"),
                       m.skalenpunkt(273, "Oktober"), m.skalenpunkt(365, "2027")],
                schritte=[
                    m.schritt("Januar 2026", "Der erste öffentliche Commit",
                              "Wir starten so, wie wir arbeiten wollen: mit offenem Quellcode unter AGPL-3.0, vom "
                              "ersten Tag an."),
                    m.schritt("Juli 2026", "mandari 0.9 geht online",
                              "Das Bürgerportal läuft im Dauerbetrieb und macht Hunderttausende Ratsdokumente "
                              "durchsuchbar. Work und Session starten in die offene Beta."),
                    m.schritt("September 2026", "mandari 0.11",
                              "Session führt Niederschriften mit Freigabe und Berichtigung, Fraktionen sehen in Work, "
                              "was aus ihren Anträgen wird."),
                    m.schritt("Herbst 2026", "Transparenz wird Standard",
                              "Dokumentation, Live-Status, Trust Center und Roadmap sind öffentlich – für alle, ohne "
                              "Anmeldung."),
                    m.schritt("2027, geplant", "Version 1.0",
                              "Übernahme aus Bestandssystemen, vereinbarte Service-Level, externer Penetrationstest."),
                ],
                note='<p><a href="/releases/">Alle Releases</a> und die <a href="/roadmap/">Roadmap</a> zeigen, was '
                     "seitdem dazugekommen ist und was als Nächstes kommt.</p>",
            ),
            m.einladung(
                "Lernen wir uns kennen.",
                "Ob Verwaltung, Fraktion, Partner oder Presse: Wir nehmen uns Zeit für Ihre Fragen.",
                "Erstgespräch vereinbaren", "/kontakt/#termin",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video, am Telefon oder in Münster", ""),
                      ("Für die Presse", "presse@mandari.de", ""), ("Zusammenarbeit", "Partner werden", "/partner/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /karriere/ — Du-Form (Startup-Kultur, wie /mitmachen/)
        # ════════════════════════════════════════════════════════════
        "karriere": [
            _hero(
                "Bau mit an der Software, auf der Demokratie läuft.",
                "Wir sind ein GovTech-Startup mit einer großen Aufgabe: die Verwaltung öffnen. Dafür suchen wir "
                "Menschen, die lieber etwas bewegen, als etwas zu verwalten.",
                cta_label="Initiativ bewerben", cta_url=f"mailto:{BEWERBUNG}?subject=Initiativbewerbung",
            ),
            _rows(
                "Warum mandari",
                [
                    _row("Arbeit mit Wirkung",
                         "Dein Code landet nicht in einer Werbeplattform, sondern im Rathaus. Du machst sichtbar, "
                         "wie deine Stadt entscheidet – und sprichst mit den Menschen, die damit arbeiten."),
                    _row("Offen by default",
                         "Alles, was du baust, ist Open Source. Issues, Roadmap und Releases sind öffentlich, dein "
                         "Name steht in den Commits."),
                    _row("Früh dabei, voll verantwortlich",
                         "Wir stehen am Anfang. Du prägst Architektur, Produkt und Kultur und übernimmst ein Thema "
                         "ganz – vom Gespräch mit der Kommune bis zum Release."),
                    _row("Kurze Wege, hohe Ansprüche",
                         "Entscheidungen fallen im Gespräch, nicht in der dritten Abstimmungsrunde. Tests, Reviews "
                         "und dokumentierte Architekturentscheidungen sorgen dafür, dass sich Verwaltungen auf uns "
                         "verlassen."),
                ],
                anchor="arbeitsweise", subline="Schnell wie ein Startup, gründlich, wie es Verwaltungen brauchen.",
            ),
            _rows(
                "Woran du arbeitest",
                [
                    _row("Plattform",
                         "Python, Django, PostgreSQL, HTMX. Eine Anwendung, die Sitzungsdienst, Fraktionsarbeit "
                         "und Bürgerportal trägt – gebaut, um in zehn Jahren noch wartbar zu sein."),
                    _row("Daten und Suche",
                         "Hunderttausende Ratsdokumente einlesen, per Texterkennung erschließen und so durchsuchbar "
                         "machen, dass man auch findet, was man nicht exakt benennen kann."),
                    _row("Betrieb und Sicherheit",
                         "Eigene Infrastruktur in deutschen Rechenzentren, eine nachvollziehbare Lieferkette, "
                         "Monitoring und Backups, auf die sich Verwaltungen verlassen."),
                    _row("Einführung und Kundenerfolg",
                         "Kommunen beim Umstieg begleiten: Daten übernehmen, Abläufe verstehen, schulen – und ins "
                         "Produkt zurückspielen, was fehlt."),
                ],
                anchor="felder", subline="Vier Felder – und bei uns bleibt niemand nur in einem.",
            ),
            _section(
                "Dein Einstieg",
                "<p>Wir besetzen Rollen über Initiativbewerbungen und wachsen mit den Menschen, die zu uns passen. "
                "Wenn dich eines unserer Felder reizt, schreib uns ein paar Zeilen und einen Link zu Arbeit, auf die "
                "du stolz bist. Ein Anschreiben nach Schema brauchst du nicht.</p>"
                "<p>Der schnellste Weg zu uns führt über das Repository: Wer einen Fehler behebt oder eine "
                "Verbesserung einreicht, hat das halbe Gespräch schon geführt. "
                '<a href="https://github.com/mandariOSS/mandari/issues">Offene Aufgaben auf GitHub</a></p>',
                anchor="stellen", background="gray",
            ),
            _steps(
                "In drei Schritten zu uns",
                [
                    ("Du schreibst uns",
                     f"Eine E-Mail an {BEWERBUNG} – mit Lebenslauf oder Profil-Link und gern mit Arbeitsproben."),
                    ("Wir lernen uns kennen",
                     "Ein Gespräch per Video oder in Münster: über deine Arbeit, unsere Arbeit und das, was wir "
                     "zusammen vorhaben könnten."),
                    ("Wir entscheiden gemeinsam",
                     "Du bekommst in jedem Fall eine ehrliche Rückmeldung."),
                ],
                anchor="ablauf",
                note="<p>Deine Unterlagen sind bei uns sicher: Nur wer an der Entscheidung beteiligt ist, liest "
                     "deine Bewerbung. Kommt es nicht zur Zusammenarbeit, löschen wir sie sechs Monate nach "
                     'Abschluss des Verfahrens. Details stehen in der <a href="/datenschutz/#bewerbungen">'
                     "Datenschutzerklärung</a>.</p>",
            ),
            _invitation(
                "Klingt nach dir?",
                "Dann schreib uns – auch wenn du noch nicht sicher bist, welche Rolle passt. Das finden wir "
                "zusammen heraus.",
                "Initiativ bewerben", f"mailto:{BEWERBUNG}?subject=Initiativbewerbung",
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /presse/ — Kurzprofil, Fakten und Kennzahlen mit Stand
        # (Logo-Paket: templates/company/_logopaket.html)
        # ════════════════════════════════════════════════════════════
        "presse": [
            _hero(
                "Presse und Medien.",
                "Offene Verwaltung, digitale Souveränität, Transparenz in der Kommunalpolitik: Dazu haben wir etwas "
                "zu sagen – und antworten schnell, auch kurz vor Redaktionsschluss.",
                cta_label="Presseanfrage stellen", cta_url=f"mailto:{PRESSE}?subject=Presseanfrage",
            ),
            # Muster 5a: Kurzprofil zum Übernehmen, rechts die Eckdaten und die Schreibweise
            m.randspalte(
                "Kurzprofil",
                "<p>mandari ist ein GovTech-Startup aus Münster und entwickelt offene Software für Verwaltung, Politik "
                "und Bürger:innen. Die Plattform startet dort, wo kommunale Demokratie entschieden wird: im Rat. Das "
                "Bürgerportal mandari Insight macht Sitzungen, Vorlagen und Beschlüsse im Volltext durchsuchbar – "
                "kostenlos und ohne Anmeldung. mandari Work ist der digitale Arbeitsplatz für Fraktionen, mandari "
                "Session das Ratsinformationssystem für Verwaltungen. Der gesamte Code steht unter der freien Lizenz "
                "AGPL-3.0, betrieben wird mandari in Rechenzentren in Deutschland. Das Unternehmen ist unabhängig "
                "finanziert.</p>"
                "<p>Zur Übernahme freigegeben, auch gekürzt.</p>",
                [
                    m.rand_fakten("", ("Sitz", "Münster (Westfalen)"),
                                  ("Produkte", "mandari Session, mandari Work, mandari Insight"),
                                  ("Lizenz", "AGPL-3.0, freie Software"), ("Pressekontakt", PRESSE)),
                    m.rand_text("<p><strong>Schreibweise:</strong> mandari klein, auch am Satzanfang. Rechtsträger und "
                                "Anschrift stehen in den <a href=\"/unternehmen/#angaben\">Angaben zum Unternehmen</a>.</p>"),
                ],
                anchor="kurzprofil",
            ),
            # Muster 9a: Kennzahlen in einem Satz, mit Stand
            m.zahlensatz(
                "Fakten und Kennzahlen",
                f"Das Bürgerportal mandari Insight macht <b>{KENNZAHLEN[0][0]}</b> Dokumente, "
                f"<b>{KENNZAHLEN[1][0]}</b> Vorgänge und Vorlagen und <b>{KENNZAHLEN[2][0]}</b> Sitzungen aus "
                f"<b>{KENNZAHLEN[3][0]}</b> Kommunen und Körperschaften im Volltext durchsuchbar.",
                rand=f"<p>Stand {KENNZAHLEN_STAND}, gezählt im Datenbestand des Bürgerportals.</p>"
                     "<p><strong>Aktuelle Version:</strong> mandari 0.11.0 vom 27. September 2026, "
                     "<a href=\"/releases/\">Releases</a></p>"
                     "<p><strong>Quellcode:</strong> <a href=\"https://github.com/mandariOSS/mandari\">GitHub</a></p>",
                anchor="fakten",
            ),
            # (hier folgt das Logo-Paket als Download-Leiste: templates/company/_logopaket.html)
            # Muster 5b: Themen als Begriffe
            m.begriffe(
                "Themen, zu denen wir sprechen",
                [
                    m.begriff("Open Source in der öffentlichen Verwaltung",
                              "„Public Money, Public Code“: warum Software, die mit öffentlichem Geld entsteht, "
                              "öffentlich sein sollte."),
                    m.begriff("Digitale Souveränität",
                              "Herstellerabhängigkeit in Kommunen und wie offene Standards sie auflösen."),
                    m.begriff("Transparenz in der Kommunalpolitik",
                              "Offene Ratsdaten, die man findet und versteht."),
                    m.begriff("GovTech gründen in Deutschland",
                              "Was es heißt, Software für Verwaltungen zu bauen."),
                ],
                anchor="themen",
                note="<p>Was gerade neu ist, steht in den <a href=\"/releases/\">Releases</a> und im "
                     "<a href=\"/transparenz/\">Transparenzbericht</a>.</p>",
            ),
            m.einladung(
                "Sie recherchieren zu offener Verwaltung?",
                "Nennen Sie uns Ihre Frist: Anfragen mit Redaktionsschluss haben Vorrang. Interviews, "
                "Hintergrundgespräche und O-Töne gern auch kurzfristig.",
                "Presseanfrage stellen", f"mailto:{PRESSE}?subject=Presseanfrage",
                wege=[("E-Mail", PRESSE, ""), ("Formate", "Interview, Hintergrund, O-Ton", ""),
                      ("Bildmaterial", "Logo-Paket", "/presse/mandari-logopaket.zip"),
                      ("Hintergrund", "Transparenzbericht", "/transparenz/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /partner/ — vier Wege der Zusammenarbeit, Ablauf, Zusagen
        # ════════════════════════════════════════════════════════════
        "partner": [
            _hero(
                "Die offene Verwaltung bauen wir gemeinsam.",
                "Offene Software entfaltet ihre Kraft im Netzwerk: mit IT-Dienstleistern, die sie betreiben, "
                "Kommunen, die sie prägen, und Förderern, die Gemeinwohl möglich machen. Werden Sie Teil davon.",
                cta_label="Partnergespräch vereinbaren", cta_url="/kontakt/?subject=Partnerschaft#termin",
            ),
            # Muster 8: vier Partnerarten nach denselben Fragen
            m.vergleich(
                "Vier Wege, mit uns zu arbeiten",
                [("IT-Dienstleister", "kommunal oder Systemhaus"), ("Pilotkommunen", "mit mandari Session"),
                 ("Förderer", "Stiftungen und Programme"), ("Civic Tech", "und Zivilgesellschaft")],
                [
                    ("Ausgangslage", [
                        "Sie betreuen Kommunen und wollen ihnen ein offenes Ratsinformationssystem anbieten.",
                        "Sie setzen mandari Session früh ein und bestimmen mit, was als Nächstes gebaut wird.",
                        "Das Bürgerportal ist kostenlos und soll es bleiben.",
                        "Initiativen, Redaktionen und Forschende arbeiten mit den offenen Ratsdaten.",
                    ]),
                    ("Was Sie bekommen", [
                        "Software, Dokumentation und Unterstützung im Hintergrund – der Kunde bleibt Ihrer. mandari "
                        "läuft auch in Ihrem Rechenzentrum, Installation und Aktualisierung sind dokumentiert.",
                        "Kurze Wege in die Entwicklung, die Übernahme Ihrer bestehenden Daten und ein System, das zu "
                        "Ihren Abläufen passt.",
                        "Förderung fließt in klar umrissene Vorhaben, deren Ergebnis als freie Software allen Kommunen "
                        "zugutekommt – mit Fortschritt, den jede:r in Roadmap, Code und Releases nachvollziehen kann.",
                        "Eine OParl-Schnittstelle, die wir stabil und ohne Anmeldung abrufbar halten – und ein offenes "
                        "Ohr, wenn etwas fehlt.",
                    ]),
                    ("Erster Schritt", [
                        "<a href=\"https://docs.mandari.de/betrieb/\">Betriebsdokumentation lesen</a>",
                        "<a href=\"/kommunen/\">mandari Session ansehen</a>",
                        "<a href=\"/roadmap/\">Roadmap ansehen</a>",
                        "<a href=\"https://docs.mandari.de/insight/oparl-api/\">Zur Schnittstelle</a>",
                    ]),
                ],
                anchor="wege",
            ),
            # Muster 2: vier Schritte in einer Zeile, das Ergebnis am Ende
            m.schrittfolge(
                "So entsteht eine Partnerschaft",
                [("Erstgespräch", "30 Minuten per Video oder Telefon: Sie erzählen, was Sie vorhaben, wir sagen, was wir "
                  "beitragen können.", ""),
                 ("Umfang und Konditionen", "Eine Seite, die Aufgaben, Aufwand und Verantwortung klar festhält.", ""),
                 ("Vertrag oder Absichtserklärung", "Pilotkommunen schließen einen Pilotvertrag mit "
                  "Auftragsverarbeitungsvertrag, für Allianzen genügt oft eine Absichtserklärung.", "")],
                ergebnis={"titel": "Loslegen.", "text": "Ein gemeinsamer Kanal, feste Ansprechpartner:innen und der "
                          "direkte Draht in die Entwicklung."},
                note="<p>Für jede Partnerschaft gilt unser Wertekompass: Ratsdaten bleiben vollständig und "
                     "unverändert, wir arbeiten mit allen demokratischen Parteien gleichermaßen, und jede Zeile "
                     'Code bleibt offen. <a href="/unternehmen/#werte">Wertekompass lesen</a></p>',
                anchor="ablauf",
            ),
            m.einladung(
                "Finden wir heraus, was wir zusammen bewegen.",
                "30 Minuten, unverbindlich. Danach wissen beide Seiten, wie eine Partnerschaft aussehen kann.",
                "Partnergespräch vereinbaren", "/kontakt/?subject=Partnerschaft#termin",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Gespräch", "per Video oder am Telefon", ""),
                      ("Für die IT", "Trust Center", "/trust/"), ("Was kommt", "Roadmap", "/roadmap/")],
            ),
        ],

        # ════════════════════════════════════════════════════════════
        # /open-source/ — was offener Code für Auftraggeber bedeutet
        # ════════════════════════════════════════════════════════════
        "open-source": [
            _hero(
                "Öffentliches Geld. Öffentlicher Code.",
                "Software, die das Gemeinwesen trägt, gehört offengelegt. Deshalb steht mandari vollständig unter "
                "AGPL-3.0: jede Zeile, jedes Produkt, ohne Premium-Ausgabe hinter verschlossener Tür.",
                cta_label="Quellcode ansehen", cta_url="https://github.com/mandariOSS/mandari",
            ),
            # Muster 5b: vier Freiheiten als Begriffe
            m.begriffe(
                "Was offener Code für Ihre Verwaltung bedeutet",
                [
                    m.begriff("Frei in der Wahl des Anbieters",
                              "Ihre IT, Ihr kommunaler Dienstleister oder ein anderes Unternehmen kann mandari betreiben "
                              "und weiterentwickeln. Eine stärkere Verhandlungsposition gibt es nicht."),
                    m.begriff("Prüfbar bis zur letzten Zeile",
                              "Ihre Informationssicherheit, ein externer Prüfer oder der Rechnungshof sieht sich den Code "
                              "einfach an – ohne Geheimhaltungsvereinbarung, ohne Termin bei uns."),
                    m.begriff("Dauerhaft verfügbar",
                              "Der Quellcode liegt öffentlich und bleibt es. Die übliche Hinterlegung beim Treuhänder "
                              "können Sie sich sparen – Ihr Investitionsschutz ist eingebaut."),
                    m.begriff("Gemeinsam stärker",
                              "Was eine Kommune beauftragt, kommt allen zugute. Erweiterungen fließen ins Hauptprojekt "
                              "zurück, so wächst mit jedem Auftrag die Software aller."),
                ],
                anchor="freiheiten", subline="Vier Freiheiten, die Ihnen keine geschlossene Software geben kann.",
            ),
            # Muster 3: was Sie nachprüfen können, und wo
            m.register(
                "Wir entwickeln vor aller Augen",
                [
                    m.gruppe("Nachprüfen statt glauben",
                             m.zeile("Eine Ausgabe für alle", "Was wir betreiben, liegt im Repository. Keine "
                                     "Enterprise-Variante, keine zurückgehaltenen Funktionen.",
                                     zusatz="<a href=\"https://github.com/mandariOSS/mandari\">Repository</a>"),
                             m.zeile("Öffentliche Releases", "Jede Version erscheint mit Änderungsprotokoll auf GitHub "
                                     "und in verständlicher Form auf dieser Website.",
                                     zusatz="<a href=\"/releases/\">Releases ansehen</a>"),
                             m.zeile("Nachvollziehbare Lieferkette", "Festgeschriebene Abhängigkeiten, eine "
                                     "Schwachstellenprüfung, die den Bau bei Befund stoppt, und eine Stückliste (SBOM) je "
                                     "Release.", zusatz="<a href=\"/trust/#audits\">Lieferkette im Trust Center</a>"),
                             m.zeile("Geregelte Meldewege", "Sicherheitslücken nehmen wir vertraulich unter "
                                     "security@mandari.de entgegen – mit zugesagten Fristen und Schutz für gutgläubige "
                                     "Forschung.", zusatz="<a href=\"/sicherheit/disclosure/\">Sicherheitslücke melden</a>")),
                    m.gruppe("Unsere Repositories",
                             m.zeile("mandari", "die Plattform: Insight, Work, Session und die OParl-Anbindung",
                                     url="https://github.com/mandariOSS/mandari", zusatz="AGPL-3.0"),
                             m.zeile("marketing-website", "diese Website",
                                     url="https://github.com/mandariOSS/marketing-website", zusatz="AGPL-3.0"),
                             m.zeile("docs", "die Dokumentation unter docs.mandari.de",
                                     url="https://github.com/mandariOSS/docs", zusatz="")),
                ],
                spalten=["Was", "Worum es geht", "Wo"],
                subline="Sie müssen uns nicht glauben. Sie können nachsehen: Roadmap, Releases, Sicherheitsprozesse und "
                        "Betriebsstatus sind öffentlich.",
                anchor="entwicklung",
            ),
            # Muster 5a: die freien Projekte, rechts der Weg zum Mitwirken
            m.randspalte(
                "Auf wessen Schultern wir stehen",
                "<p>mandari wäre ohne diese freien Projekte nicht möglich. Sie verdienen Sichtbarkeit – und Beiträge "
                "zurück.</p>"
                "<ul>"
                '<li><a href="https://www.python.org">Python</a> – Programmiersprache (PSF-Lizenz)</li>'
                '<li><a href="https://www.djangoproject.com/">Django</a> – Web-Framework (BSD-3)</li>'
                '<li><a href="https://wagtail.org/">Wagtail</a> – Redaktionssystem dieser Website (BSD-3)</li>'
                '<li><a href="https://www.postgresql.org/">PostgreSQL</a> – Datenbank (PostgreSQL-Lizenz)</li>'
                '<li><a href="https://oparl.org/">OParl</a> – Standard für offene Ratsdaten (CC BY-SA)</li>'
                '<li><a href="https://htmx.org/">HTMX</a> – Oberfläche ohne schwere Skripte (BSD-2)</li>'
                '<li><a href="https://tailwindcss.com/">Tailwind CSS</a> – Gestaltung (MIT)</li>'
                '<li><a href="https://lucide.dev/">Lucide</a> – Symbole (ISC)</li>'
                '<li><a href="https://altcha.org/">Altcha</a> – Spamschutz ohne Captcha (MIT)</li>'
                '<li><a href="https://www.docker.com/">Docker</a> – Container für den Betrieb (Apache-2.0)</li>'
                "</ul>",
                [
                    m.rand_text("<p>Mitwirken können Sie mit einem Fehlerbericht ebenso wie mit Code. Wie das geht, "
                                "steht in der Datei CONTRIBUTING im jeweiligen Repository.</p>"),
                    m.rand_links("Mitmachen", ("Wege zum ersten Beitrag", "/mitmachen/"),
                                 ("CONTRIBUTING", "https://github.com/mandariOSS/mandari/blob/main/CONTRIBUTING.md"),
                                 ("Alle Repositories", "https://github.com/mandariOSS")),
                ],
                anchor="danke",
            ),
            m.einladung(
                "Fragen aus IT und Informationssicherheit?",
                "Wir beantworten sie direkt und im Detail – gern im gemeinsamen Termin mit Ihrem Team.",
                "Termin vereinbaren", "/kontakt/#termin",
                wege=[("E-Mail", "hello@mandari.de", ""), ("Sicherheitslücke", "security@mandari.de", ""),
                      ("Für die IT", "Trust Center", "/trust/"), ("Lizenz", "AGPL-3.0", "https://github.com/mandariOSS/mandari/blob/main/LICENSE")],
            ),
        ],
    }
