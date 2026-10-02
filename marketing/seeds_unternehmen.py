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
    kennzahlen = "".join(f"<li><strong>{zahl}</strong> {label}</li>" for zahl, label in KENNZAHLEN)

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
            _section(
                "Warum wir das tun",
                "<p>Was den Alltag einer Stadt bestimmt, entscheidet sich im Rat und in seinen Ausschüssen: "
                "der Bebauungsplan, der Kita-Ausbau, die neue Buslinie. Die Unterlagen dazu sind öffentlich. "
                "Wer sie sucht, braucht trotzdem Geduld, Vorwissen und das richtige PDF aus dem richtigen Jahr.</p>"
                "<p>Sitzungsdienste stemmen ihre Arbeit mit Software, die nie dafür gedacht war, Daten zu teilen. "
                "Ehrenamtliche Politiker:innen bereiten sich nach Feierabend mit Papierstapeln und Mailketten auf "
                "Entscheidungen vor, die Millionen bewegen.</p>"
                "<p><strong>Das geht besser.</strong> Wir bauen Software, die alle drei Seiten zusammenbringt – "
                "und wir bauen sie offen, damit sie den Kommunen gehört und nicht uns.</p>",
                anchor="warum",
                aside=(
                    "<h3>Unsere Mission</h3>"
                    "<p>Wir machen Kommunalpolitik für alle zugänglich – und geben Verwaltungen die Werkzeuge, "
                    "die sie dafür brauchen.</p>"
                    "<h3>Unsere Vision</h3>"
                    "<p>Eine offene Verwaltungswelt: Jede Kommune arbeitet mit Software, deren Code sie kennt, "
                    "deren Daten ihr gehören und deren Anbieter sie frei wählen kann.</p>"
                ),
            ),
            _rows(
                "Unser Wertekompass",
                [
                    _row("Demokratie stärken",
                         "Vertrauen in Politik entsteht, wenn Entscheidungen nachvollziehbar sind. Wir zeigen "
                         "Ratsdaten vollständig und unverändert und arbeiten mit allen demokratischen Parteien "
                         "gleichermaßen."),
                    _row("Offen aus Überzeugung",
                         "Unser gesamter Code steht unter AGPL-3.0. Öffentliches Geld verdient öffentlichen Code: "
                         "prüfbar, wiederverwendbar, unabhängig von uns."),
                    _row("Souverän und sicher",
                         "Betrieb in deutschen Rechenzentren, Daten in der Hand der Kommune, Export jederzeit. "
                         "Digitale Souveränität ist bei uns der Normalfall."),
                    _row("Für alle gemacht",
                         "Das Bürgerportal ist kostenlos und braucht keine Anmeldung. Wir gestalten barrierearm "
                         "und schreiben so, dass man uns versteht."),
                    _row("Verlässlich",
                         "Wir sagen, was fertig ist und was kommt – mit Datum und Verbindlichkeit. Verwaltungen "
                         "planen in Haushaltsjahren. Wir auch."),
                    _row("Nah an der Praxis",
                         "Wir entwickeln mit Sitzungsdiensten, Fraktionen und Bürger:innen, nicht über ihre Köpfe "
                         "hinweg. Pilotkommunen gestalten die Roadmap mit."),
                ],
                anchor="werte", subline="Sechs Zusagen. Wenn Ziele in Konflikt geraten, entscheiden sie.",
            ),
            _rows(
                "Ein Geschäftsmodell, so offen wie unser Code",
                [
                    _row("Betrieb",
                         "Wir betreiben mandari für Fraktionen und Verwaltungen: sicher, aktuell, aus Deutschland."),
                    _row("Betreuung",
                         "Wer mandari selbst betreibt, sichert sich Unterstützung und Wartung vertraglich."),
                    _row("Einführung",
                         "Datenübernahme aus dem Altsystem, Einrichtung und Schulung – damit der Umstieg gelingt."),
                ],
                anchor="geschaeftsmodell",
                subline="Wir verdienen unser Geld mit Leistung, nicht mit Lizenzen. Keine Werbung, kein "
                        "Datenhandel, keine Investoren, die morgen den Kurs ändern.",
                note='<p><a href="/preise/">Preise ansehen</a></p>',
            ),
            _rows(
                "Wir stehen am Anfang. Genau da wollen wir sein.",
                [
                    _row("Januar 2026",
                         "Wir starten so, wie wir arbeiten wollen: mit offenem Quellcode unter AGPL-3.0, vom "
                         "ersten Tag an.",
                         label="Der erste öffentliche Commit"),
                    _row("Juli 2026",
                         "Das Bürgerportal läuft im Dauerbetrieb und macht Hunderttausende Ratsdokumente "
                         "durchsuchbar. Work und Session starten in die offene Beta.",
                         label="mandari 0.9 geht online"),
                    _row("September 2026",
                         "Session führt Niederschriften mit Freigabe und Berichtigung, Fraktionen sehen in Work, "
                         "was aus ihren Anträgen wird.",
                         label="mandari 0.11", link_label="Alle Releases", link_url="/releases/"),
                    _row("Herbst 2026",
                         "Dokumentation, Live-Status, Trust Center und Roadmap sind öffentlich – für alle, ohne "
                         "Anmeldung.",
                         label="Transparenz wird Standard"),
                    _row("2027",
                         "Übernahme aus Bestandssystemen, vereinbarte Service-Level, externer Penetrationstest.",
                         label="Version 1.0", status="Geplant",
                         link_label="Zur Roadmap", link_url="/roadmap/"),
                ],
                anchor="wegmarken", subline="Vom ersten öffentlichen Commit zur Plattform für die offene Verwaltung.",
                layout="zeitleiste",
            ),
            _invitation(
                "Lernen wir uns kennen.",
                "Ob Verwaltung, Fraktion, Partner oder Presse: Wir nehmen uns Zeit für Ihre Fragen.",
                "Erstgespräch vereinbaren", "/kontakt/#termin",
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
            _section(
                "Kurzprofil",
                "<p>mandari ist ein GovTech-Startup aus Münster und entwickelt offene Software für Verwaltung, Politik "
                "und Bürger:innen. Die Plattform startet dort, wo kommunale Demokratie entschieden wird: im Rat. Das "
                "Bürgerportal mandari Insight macht Sitzungen, Vorlagen und Beschlüsse im Volltext durchsuchbar – "
                "kostenlos und ohne Anmeldung. mandari Work ist der digitale Arbeitsplatz für Fraktionen, mandari "
                "Session das Ratsinformationssystem für Verwaltungen. Der gesamte Code steht unter der freien Lizenz "
                "AGPL-3.0, betrieben wird mandari in Rechenzentren in Deutschland. Das Unternehmen ist unabhängig "
                "finanziert.</p>"
                "<p>Zur Übernahme freigegeben, auch gekürzt.</p>",
                anchor="kurzprofil",
                aside=(
                    "<h3>Schreibweise</h3>"
                    "<p>Der Name wird klein geschrieben: <strong>mandari</strong>, auch am Satzanfang. Die Produkte "
                    "heißen <strong>mandari Session</strong>, <strong>mandari Work</strong> und "
                    "<strong>mandari Insight</strong>.</p>"
                ),
            ),
            _section(
                "Fakten und Kennzahlen",
                "<ul>"
                "<li><strong>Sitz:</strong> Münster (Westfalen)</li>"
                "<li><strong>Was wir tun:</strong> offene Software für Verwaltung, Politik und Bürger:innen "
                "(GovTech)</li>"
                "<li><strong>Produkte:</strong> mandari Session, mandari Work, mandari Insight</li>"
                "<li><strong>Lizenz:</strong> AGPL-3.0 (freie Software), Quellcode auf "
                '<a href="https://github.com/mandariOSS/mandari">GitHub</a></li>'
                "<li><strong>Aktuelle Version:</strong> mandari 0.11.0 vom 27. September 2026 "
                '(<a href="/releases/">Releases</a>)</li>'
                "<li><strong>Rechtsträger und Anschrift:</strong> "
                '<a href="/unternehmen/#angaben">Angaben zum Unternehmen</a></li>'
                "</ul>",
                anchor="fakten", background="gray",
                aside=(
                    "<h3>Kennzahlen</h3>"
                    f"<p>Aus dem Bürgerportal mandari Insight, Stand {KENNZAHLEN_STAND}:</p>"
                    f"<ul>{kennzahlen}</ul>"
                ),
            ),
            _section(
                "Themen, zu denen wir sprechen",
                "<ul>"
                "<li>Open Source in der öffentlichen Verwaltung: „Public Money, Public Code“</li>"
                "<li>Digitale Souveränität und Herstellerabhängigkeit in Kommunen</li>"
                "<li>Transparenz in der Kommunalpolitik und offene Ratsdaten</li>"
                "<li>GovTech gründen in Deutschland</li>"
                "</ul>"
                '<p>Was gerade neu ist, steht in den <a href="/releases/">Releases</a> und im '
                '<a href="/transparenz/">Transparenzbericht</a>.</p>',
                anchor="themen",
            ),
            _invitation(
                "Sie recherchieren zu offener Verwaltung?",
                "Nennen Sie uns Ihre Frist: Anfragen mit Redaktionsschluss haben Vorrang. Interviews, "
                "Hintergrundgespräche und O-Töne gern auch kurzfristig.",
                "Presseanfrage stellen", f"mailto:{PRESSE}?subject=Presseanfrage",
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
            _rows(
                "Vier Wege, mit uns zu arbeiten",
                [
                    _row("Kommunale IT-Dienstleister und Systemhäuser",
                         "Sie betreuen Kommunen und wollen ihnen ein offenes Ratsinformationssystem anbieten. Wir "
                         "liefern Software, Dokumentation und Unterstützung im Hintergrund – der Kunde bleibt Ihrer. "
                         "mandari läuft auch in Ihrem Rechenzentrum, Installation und Aktualisierung sind "
                         "dokumentiert.",
                         link_label="Betriebsdokumentation lesen", link_url="https://docs.mandari.de/betrieb/"),
                    _row("Pilotkommunen",
                         "Sie setzen mandari Session früh ein und bestimmen mit, was als Nächstes gebaut wird. Dafür "
                         "bekommen Sie kurze Wege in die Entwicklung, die Übernahme Ihrer bestehenden Daten und ein "
                         "System, das zu Ihren Abläufen passt.",
                         link_label="mandari Session ansehen", link_url="/kommunen/"),
                    _row("Förderer und Stiftungen",
                         "Das Bürgerportal ist kostenlos und soll es bleiben. Förderung fließt in klar umrissene "
                         "Vorhaben, deren Ergebnis als freie Software allen Kommunen zugutekommt – mit Fortschritt, "
                         "den jede:r in Roadmap, Code und Releases nachvollziehen kann.",
                         link_label="Roadmap ansehen", link_url="/roadmap/"),
                    _row("Civic Tech und Zivilgesellschaft",
                         "Initiativen, Redaktionen und Forschende arbeiten mit den offenen Ratsdaten. Wir halten die "
                         "OParl-Schnittstelle stabil und ohne Anmeldung abrufbar – und hören zu, wenn etwas fehlt.",
                         link_label="Zur Schnittstelle", link_url="https://docs.mandari.de/insight/oparl-api/"),
                ],
                anchor="wege",
            ),
            _steps(
                "So entsteht eine Partnerschaft",
                [
                    ("Erstgespräch",
                     "30 Minuten per Video oder Telefon: Sie erzählen, was Sie vorhaben, wir sagen, was wir "
                     "beitragen können."),
                    ("Umfang und Konditionen",
                     "Eine Seite, die Aufgaben, Aufwand und Verantwortung klar festhält."),
                    ("Vertrag oder Absichtserklärung",
                     "Pilotkommunen schließen einen Pilotvertrag mit Auftragsverarbeitungsvertrag, für Allianzen "
                     "genügt oft eine Absichtserklärung."),
                    ("Loslegen",
                     "Ein gemeinsamer Kanal, feste Ansprechpartner:innen und der direkte Draht in die Entwicklung."),
                ],
                anchor="ablauf", background="gray",
                note="<p>Für jede Partnerschaft gilt unser Wertekompass: Ratsdaten bleiben vollständig und "
                     "unverändert, wir arbeiten mit allen demokratischen Parteien gleichermaßen, und jede Zeile "
                     'Code bleibt offen. <a href="/unternehmen/#werte">Wertekompass lesen</a></p>',
            ),
            _invitation(
                "Finden wir heraus, was wir zusammen bewegen.",
                "30 Minuten, unverbindlich. Danach wissen beide Seiten, wie eine Partnerschaft aussehen kann.",
                "Partnergespräch vereinbaren", "/kontakt/?subject=Partnerschaft#termin",
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
            _rows(
                "Was offener Code für Ihre Verwaltung bedeutet",
                [
                    _row("Frei in der Wahl des Anbieters",
                         "Ihre IT, Ihr kommunaler Dienstleister oder ein anderes Unternehmen kann mandari betreiben "
                         "und weiterentwickeln. Eine stärkere Verhandlungsposition gibt es nicht."),
                    _row("Prüfbar bis zur letzten Zeile",
                         "Ihre Informationssicherheit, ein externer Prüfer oder der Rechnungshof sieht sich den Code "
                         "einfach an – ohne Geheimhaltungsvereinbarung, ohne Termin bei uns."),
                    _row("Dauerhaft verfügbar",
                         "Der Quellcode liegt öffentlich und bleibt es. Die übliche Hinterlegung beim Treuhänder "
                         "können Sie sich sparen – Ihr Investitionsschutz ist eingebaut."),
                    _row("Gemeinsam stärker",
                         "Was eine Kommune beauftragt, kommt allen zugute. Erweiterungen fließen ins Hauptprojekt "
                         "zurück, so wächst mit jedem Auftrag die Software aller."),
                ],
                anchor="freiheiten", subline="Vier Freiheiten, die Ihnen keine geschlossene Software geben kann.",
            ),
            _rows(
                "Wir entwickeln vor aller Augen",
                [
                    _row("Eine Ausgabe für alle",
                         "Was wir betreiben, liegt im Repository. Keine Enterprise-Variante, keine zurückgehaltenen "
                         "Funktionen."),
                    _row("Öffentliche Releases",
                         "Jede Version erscheint mit Änderungsprotokoll auf GitHub und in verständlicher Form auf "
                         "dieser Website.",
                         link_label="Releases ansehen", link_url="/releases/"),
                    _row("Nachvollziehbare Lieferkette",
                         "Festgeschriebene Abhängigkeiten, eine Schwachstellenprüfung, die den Bau bei Befund "
                         "stoppt, und eine Stückliste (SBOM) je Release.",
                         link_label="Lieferkette im Trust Center", link_url="/trust/"),
                    _row("Geregelte Meldewege",
                         "Sicherheitslücken nehmen wir vertraulich unter "
                         '<a href="mailto:security@mandari.de">security@mandari.de</a> entgegen – mit zugesagten '
                         "Fristen und Schutz für gutgläubige Forschung.",
                         link_label="Sicherheitslücke melden", link_url="/sicherheit/disclosure/"),
                ],
                anchor="entwicklung", background="gray",
                subline="Sie müssen uns nicht glauben. Sie können nachsehen: Roadmap, Releases, "
                        "Sicherheitsprozesse und Betriebsstatus sind öffentlich.",
            ),
            _section(
                "Schauen Sie uns in den Code",
                "<p>Alle Repositories liegen unter "
                '<a href="https://github.com/mandariOSS">github.com/mandariOSS</a>:</p>'
                "<ul>"
                '<li><a href="https://github.com/mandariOSS/mandari">mandari</a> – die Plattform: Insight, Work, '
                "Session und die OParl-Anbindung</li>"
                '<li><a href="https://github.com/mandariOSS/marketing-website">marketing-website</a> – '
                "diese Website</li>"
                '<li><a href="https://github.com/mandariOSS/docs">docs</a> – die Dokumentation unter '
                "docs.mandari.de</li>"
                "</ul>"
                "<p>Mitwirken können Sie mit einem Fehlerbericht ebenso wie mit Code. Wie das geht, steht in der Datei "
                'CONTRIBUTING im jeweiligen Repository und unter <a href="/mitmachen/">Mitmachen</a>.</p>',
                anchor="repositories",
                # Randspalte: die freien Projekte, auf denen mandari aufbaut (ein Band statt zwei halbleerer)
                aside=(
                    '<h3 id="danke">Auf wessen Schultern wir stehen</h3>'
                    "<p>mandari wäre ohne diese freien Projekte nicht möglich. Sie verdienen Sichtbarkeit – und "
                    "Beiträge zurück.</p>"
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
                    "</ul>"
                ),
            ),
            _invitation(
                "Fragen aus IT und Informationssicherheit?",
                "Wir beantworten sie direkt und im Detail – gern im gemeinsamen Termin mit Ihrem Team.",
                "Termin vereinbaren", "/kontakt/#termin",
            ),
        ],
    }
