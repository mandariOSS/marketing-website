"""
Seed-Inhalte des RIS-Vergleichs: /vergleich/ und /vergleich/mandari-vs-<anbieter>/.

Rechtlicher Rahmen (vergleichende Werbung, § 6 UWG): nur objektiv nachprüfbare, öffentlich belegte
Aussagen, sachlicher Ton, keine Herabsetzung. Jede Angabe zu einem Anbieter trägt ein Quellenkürzel
([SO1], [ST2] …), die Quellen stehen mit Abrufdatum am Ende jeder Seite. Wo wir keine öffentliche Angabe
gefunden haben, steht genau das – nie eine Behauptung, dass etwas fehlt. Was mandari noch fehlt, steht
ausdrücklich dabei, mit der Stufe aus der Roadmap (zugesagt, geplant, in Prüfung).

Grundlage ist die interne Funktionsanalyse vom 2. Oktober 2026. Ändert sich ein Stand, hier anpassen und
die Seiten mit `refresh_seeded_page vergleich --force` und `refresh_seeded_page mandari-vs-<anbieter>
--force` neu seeden; die Lücken erscheinen zusätzlich auf /roadmap/ (`refresh_seeded_page roadmap --force`).

Zellen: (Status, Zusatz). Status für Anbieter: yes, partial, unknown; für mandari zusätzlich open
(noch nicht verfügbar, der Zusatz nennt die Roadmap-Stufe).
"""

from __future__ import annotations

STAND = "Oktober 2026"
ABRUF = "2. Oktober 2026"

# ── Quellen ──────────────────────────────────────────────────────────────────
# Kürzel → (Bezeichnung, Adresse). Abgerufen am ABRUF, soweit nicht anders vermerkt.
QUELLEN = {
    "SO1": ("SOMACOS: Session", "https://somacos.de/loesungen/sitzungsmanagement/session/"),
    "SO2": ("SOMACOS: Session – Technik", "https://somacos.de/loesungen/sitzungsmanagement/technik/"),
    "SO3": ("SOMACOS: SessionNet", "https://somacos.de/loesungen/digitale-gremienarbeit/sessionnet/"),
    "SO4": ("SOMACOS: Mandatos", "https://somacos.de/loesungen/digitale-gremienarbeit/mandatos/"),
    "SO5": ("SOMACOS: Digitale Gremienarbeit – Sicherheit", "https://somacos.de/loesungen/digitale-gremienarbeit/sicherheit/"),
    "SO6": ("SOMACOS: Online-Abstimmung", "https://somacos.de/loesungen/sonstige/onlineabstimmung/"),
    "SO7": ("SOMACOS: Cloudlösungen", "https://somacos.de/loesungen/sonstige/cloudspeicher/"),
    "SO8": ("SOMACOS: Aufwandsentschädigung", "https://somacos.de/loesungen/sonstige/aufwandsentschaedigung/"),
    "SO9": ("SOMACOS: Beschlusscontrolling", "https://somacos.de/loesungen/sonstige/beschlusskontrolle/"),
    "SO10": ("SOMACOS: Sitzungsmappe", "https://somacos.de/loesungen/sonstige/druckauftrag/"),
    "SO11": ("SOMACOS: Schnittstellen", "https://somacos.de/loesungen/sonstige/schnittstellen/"),
    "SO12": ("SOMACOS: Web-API für KI-gestützte Protokollierung", "https://somacos.de/loesungen/sonstige/ki-protokollierung/"),
    "SO13": ("SOMACOS: Unternehmen", "https://somacos.de/unternehmen/somacos/"),
    "ST1": ("STERNBERG: SD.NET Sitzungsmanagement", "https://www.sitzungsdienst.net/sitzungsmanagement/"),
    "ST2": ("STERNBERG: Infosystem SD.NET RIM", "https://www.sitzungsdienst.net/informationssystem-sdnet-rim/"),
    "ST3": ("STERNBERG: RICH SitzungsApps für SD.NET", "https://www.sitzungsdienst.net/sdnet-rich-sitzungsapps/"),
    "ST4": ("STERNBERG: Protokoll-Erstellung mit KI", "https://www.sitzungsdienst.net/ki-audiomanagement/"),
    "ST5": ("ekom21: Broschüre SD.NET Sitzungsmanagement", "https://www.ekom21.de/infocenter/mediathek/broschueren/ekom21-sd-net-broschuere-04062018-dig.pdf"),
    "ST6": ("STERNBERG: Modul „Interaktive Virtuelle Sitzung“ GPA-NRW-zertifiziert", "https://www.sitzungsdienst.net/unser-modul-interaktive-virtuelle-sitzung-jetzt-gpa-nrw-zertifiziert/"),
    "ST7": ("kommunal-edv.de: Anbieterprofil Sternberg SD.NET", "https://www.kommunal-edv.de/anbieter/sitzungsdienst/sternberg-sd-net/"),
    "ST8": ("STERNBERG: S24-Cloud", "https://www.sitzungsdienst.net/s24-cloud/"),
    "AL1": ("CC e-gov: ALLRIS 4", "https://www.cc-egov.de/allris-4/"),
    "AL2": ("CC e-gov: Produktbeschreibung ALLRIS 4 (Ausgabe Juni 2022)", "https://www.k21media.de/_files/mod_itguide/CC_Produkt_ALLRIS.pdf"),
    "AL3": ("CC e-gov: Software as a Service", "https://www.cc-egov.de/software-as-a-service/"),
    "AL4": ("CC e-gov: KI für Kommunen", "https://www.cc-egov.de/ki-fuer-kommunen/"),
    "AL5": ("CC e-gov: ALLRIS kompakt", "https://www.cc-egov.de/allris-kompakt/"),
    "AL6": ("CC e-gov: Referenzen", "https://www.cc-egov.de/referenzen/"),
    "RS1": ("regisafe: Ratsinformationssystem", "https://www.regisafe.de/produkt/ratsinformationssystem/"),
    "RS2": ("regisafe: Fachverfahren Sitzungsdienst", "https://www.regisafe.de/produkt/fachverfahren-sitzungsdienst/"),
    "RS3": ("regisafe: Digitales Verfahren Ratsinformation", "https://www.regisafe.de/produkt/digitales-verfahren-ratsinformation/"),
    "RS4": ("regisafe: GenAI-Niederschrift", "https://www.regisafe.de/genai-niederschrift/"),
    "RS5": ("regisafe: regisafe in der Cloud", "https://www.regisafe.de/produkt/regisafe-in-der-cloud/"),
}

# ── Funktionen ───────────────────────────────────────────────────────────────
GRUPPEN = [
    ("Offenheit und Betrieb", [
        ("quellcode", "Quellcode offen unter Open-Source-Lizenz"),
        ("preise", "Öffentliche Preisliste"),
        ("eigenbetrieb", "Betrieb im eigenen Rechenzentrum"),
        ("cloud", "Betrieb als Dienst aus Rechenzentren in Deutschland"),
    ]),
    ("Sitzungsdienst", [
        ("sitzung", "Sitzungsplanung, Tagesordnung und Ladung"),
        ("niederschrift", "Niederschrift und Beschlussauszüge"),
        ("beschlusskontrolle", "Beschlusskontrolle"),
        ("sitzungsgeld", "Sitzungsgeld mit Zahlungsdatei"),
        ("mitteilung", "Mitteilung an das Finanzamt (Mitteilungsverordnung)"),
        ("umlauf", "Umlaufverfahren mit Stimmabgabe online"),
        ("mappe", "Personalisierte Sitzungsmappe mit Wasserzeichen"),
        ("raeume", "Raum- und Ressourcenplanung"),
        ("bekanntmachung", "Bekanntmachung und Amtsblatt"),
    ]),
    ("Vorlagen und Abläufe", [
        ("freigabe", "Freigabe und Mitzeichnung"),
        ("ablaeufe", "Konfigurierbare Abläufe mit Fristen"),
        ("word", "Bearbeitung in Word oder Word-Import"),
        ("signatur", "Elektronische Signatur"),
        ("mobilfreigabe", "Freigabe unterwegs per App oder mobiler Ansicht"),
    ]),
    ("Ratsmitglieder und Fraktionen", [
        ("gremieninfo", "Alle Unterlagen, auch nichtöffentliche, in einem geschützten Webbereich"),
        ("app", "App mit Unterlagen offline und Anmerkungen"),
        ("notizen", "Notizen teilen und gemeinsam arbeiten"),
        ("antraege", "Anträge digital einreichen"),
        ("fraktion", "Arbeitsplatz für Fraktionen (Sitzungen, Anträge, Aufgaben)"),
    ]),
    ("Sitzung live", [
        ("hybrid", "Hybride Sitzungen"),
        ("abstimmung", "Stimmabgabe am eigenen Gerät"),
        ("zertifikat", "Online-Abstimmung von der gpaNRW zertifiziert"),
        ("redner", "Rednerliste oder Saalanzeige"),
        ("stream", "Livestream mit Sprungmarken je Tagesordnungspunkt"),
        ("saaltechnik", "Anbindung von Konferenz- oder Abstimmungsanlagen"),
    ]),
    ("Öffentlichkeit", [
        ("portal", "Bürgerinformation ohne Anmeldung"),
        ("suche", "Volltextsuche in Dokumenten"),
        ("uebergreifend", "Suche über Kommunengrenzen, Karte und Umkreis"),
        ("abo", "E-Mail-Benachrichtigungen für die Öffentlichkeit"),
        ("website", "Einbindung in die Website der Kommune"),
        ("buergerapp", "App für Bürger:innen"),
        ("schwaerzung", "Schwärzung bei der Veröffentlichung"),
        ("ki_buerger", "KI-Zusammenfassungen für Bürger:innen"),
    ]),
    ("Schnittstellen", [
        ("oparl", "OParl-Schnittstelle"),
        ("dcat", "Datenkatalog nach DCAT-AP.de"),
        ("dms", "Übergabe an DMS oder E-Akte"),
        ("verzeichnis", "Anmeldung über Verzeichnisdienst (Active Directory, LDAP, SSO)"),
        ("kalender", "Kalender-Abgleich (Outlook, ICS)"),
    ]),
    ("Barrierefreiheit und Sicherheit", [
        ("bitv", "Barrierefreiheit mit unabhängiger Prüfung"),
        ("zwei_faktor", "Zwei-Faktor-Anmeldung"),
        ("protokoll", "Protokollierung von Änderungen und Zugriffen"),
        ("pruefung", "Unabhängige Prüfung von Sicherheit oder Datenschutz"),
    ]),
    ("Künstliche Intelligenz", [
        ("ki_protokoll", "KI-Entwurf der Niederschrift aus der Aufzeichnung"),
        ("ki_schreiben", "KI-Schreibhilfe für Texte"),
    ]),
]

ANZAHL_FUNKTIONEN = sum(len(rows) for _, rows in GRUPPEN)

# ── mandari (Eigenangaben, geprüft am Code-Stand vom 2. Oktober 2026) ─────────
# open = noch nicht verfügbar; der Zusatz beginnt mit der Roadmap-Stufe.
MANDARI = {
    "quellcode": ("yes", "AGPL-3.0, vollständiger Quellcode auf GitHub"),
    "preise": ("partial", "Insight kostenlos, Work 39,90 € im Monat inkl. MwSt.; Preisliste für Session in Vorbereitung"),
    "eigenbetrieb": ("yes", "Docker Compose, auf Wunsch mit Betreuungsvertrag"),
    "cloud": ("yes", "ISO-27001-zertifizierte Rechenzentren in Deutschland"),
    "sitzung": ("yes", "Sitzungskalender, Tagesordnung mit Nachträgen, Ladung per E-Mail, im Portal oder per Brief"),
    "niederschrift": ("yes", "Genehmigung, Sperre nach Genehmigung, Auszüge je Tagesordnungspunkt"),
    "beschlusskontrolle": ("yes", "Umsetzungsstand, Zuständigkeit, Wiedervorlage"),
    "sitzungsgeld": ("yes", "Vier-Augen-Prinzip, SEPA-Datei; Formate für Finanzverfahren geplant 2027"),
    "mitteilung": ("open", "In Prüfung; heute Jahresübersicht als Grundlage"),
    "umlauf": ("partial", "Rücklauf erfasst der Sitzungsdienst; Stimmabgabe online in Prüfung"),
    "mappe": ("partial", "Gesamt-PDF mit Inhaltsverzeichnis und Lesezeichen; Wasserzeichen in Prüfung"),
    "raeume": ("open", "Geplant 2027"),
    "bekanntmachung": ("open", "In Prüfung"),
    "freigabe": ("yes", "Mehrstufig, mit Vier-Augen-Prinzip und Vertretung"),
    "ablaeufe": ("partial", "Feste Stufen mit Fristen-Erinnerung; parallele Stationen und Eskalation geplant 2027"),
    "word": ("partial", "In Work Import aus Word und PDF; im Sitzungsdienst geplant 2027"),
    "signatur": ("open", "Geplant 2027"),
    "mobilfreigabe": ("partial", "Im Browser möglich, ohne eigene mobile Ansicht; in Prüfung"),
    "gremieninfo": ("partial", "Unterlagen je Berechtigung mit der Ladung per E-Mail; eigener Bereich in Prüfung"),
    "app": ("open", "Geplant 2027; Work heute als installierbare Web-App"),
    "notizen": ("yes", "In Work: Notizen und Kommentare an TOPs und Vorlagen, privat oder geteilt"),
    "antraege": ("yes", "Aus Work an die Verwaltung, mit Eingangsnummer und Status"),
    "fraktion": ("yes", "mandari Work: Fraktionssitzungen, Anträge, Aufgaben, Gastzugänge"),
    "hybrid": ("yes", "Sitzungsformat, Teilnahmeart, Live-Cockpit mit Beschlussfähigkeit"),
    "abstimmung": ("open", "Geplant 2027; heute Erfassung im Live-Cockpit"),
    "zertifikat": ("open", "Geplant 2027 (Zertifizierungsfähigkeit)"),
    "redner": ("open", "Geplant 2027"),
    "stream": ("partial", "Stream-Adresse je Sitzung; Sprungmarken geplant 2027"),
    "saaltechnik": ("open", "In Prüfung"),
    "portal": ("yes", "mandari Insight, kostenlos und ohne Tracking"),
    "suche": ("yes", "Mit Texterkennung, Synonymen und Fehlertoleranz"),
    "uebergreifend": ("yes", "Über alle angebundenen Kommunen, mit Karte und Umkreissuche"),
    "abo": ("yes", "Themen, Orte und Beschlüsse, mit Bestätigung per E-Mail"),
    "website": ("partial", "Kalender-Feed und OParl; einbettbare Bausteine in Prüfung"),
    "buergerapp": ("open", "Geplant 2027"),
    "schwaerzung": ("open", "Geplant 2027"),
    "ki_buerger": ("partial", "Zusammenfassungen und Fragen an die Ratsdaten, für ausgewählte Kommunen"),
    "oparl": ("yes", "OParl 1.1 je Kommune und über alle Kommunen, mit Änderungsfeed"),
    "dcat": ("partial", "Katalog je Kommune vorhanden und zuschaltbar; Anbindung an Datenportale folgt"),
    "dms": ("open", "Geplant 2027; heute Export als PDF, JSON und OParl"),
    "verzeichnis": ("open", "Geplant 2027 (SAML 2.0, OpenID Connect)"),
    "kalender": ("yes", "ICS-Feeds für Outlook und andere Kalender"),
    "bitv": ("open", "Prüfbericht für Session zugesagt für Q4/2026"),
    "zwei_faktor": ("yes", "App-Codes oder Sicherheitsschlüssel, als Pflicht einstellbar"),
    "protokoll": ("yes", "Änderungen, Anmeldungen und Lesezugriffe, mit Prüfexport"),
    "pruefung": ("open", "Geplant 2027: externer Penetrationstest; Quellcode öffentlich prüfbar"),
    "ki_protokoll": ("open", "Geplant 2027"),
    "ki_schreiben": ("partial", "In Work für Anträge; im Sitzungsdienst in Prüfung"),
}

# Kurzfassung der mandari-Zelle in der Übersicht: Roadmap-Stufe statt Erläuterung.
MANDARI_KURZ = {
    "mitteilung": "In Prüfung", "raeume": "Geplant 2027", "bekanntmachung": "In Prüfung",
    "signatur": "Geplant 2027", "app": "Geplant 2027",
    "abstimmung": "Geplant 2027", "zertifikat": "Geplant 2027", "redner": "Geplant 2027",
    "saaltechnik": "In Prüfung", "buergerapp": "Geplant 2027", "schwaerzung": "Geplant 2027",
    "dms": "Geplant 2027", "verzeichnis": "Geplant 2027", "bitv": "Zugesagt Q4/2026",
    "pruefung": "Geplant 2027", "ki_protokoll": "Geplant 2027",
}

# ── Anbieter ─────────────────────────────────────────────────────────────────
# Reihenfolge = Spalten der Übersicht und Karten. Zellen ohne Eintrag: keine öffentliche Angabe.
ANBIETER = {
    "mandari-vs-somacos": {
        "kurzname": "Somacos Session",
        "kartenname": "Somacos",  # ohne „Session“: Karten färben Produktnamen in mandari-Kennfarben
        "spalte": "Somacos",
        "anbieter": "SOMACOS GmbH & Co. KG (Salzwedel)",
        "produkt": "Session (Sitzungsmanagement), SessionNet (Bürger- und Gremieninformation), App Mandatos",
        "kunden": "Über 2.200 Projekte (Eigenangabe) [SO13]",
        "website": "https://somacos.de/",
        "cells": {
            "preise": ("unknown", "Angebot auf Anfrage"),
            "eigenbetrieb": ("yes", "Installation in der eigenen IT [SO2]"),
            "cloud": ("yes", "„Sessionasp“ aus BSI-zertifizierten kommunalen Rechenzentren in Deutschland [SO7]"),
            "sitzung": ("yes", "Planung, Vorbereitung, Durchführung und Nachbereitung [SO1]"),
            "niederschrift": ("yes", "Beschlussauszüge nach Fachbereich oder Tagesordnungspunkt [SO9]"),
            "beschlusskontrolle": ("yes", "Berichtswesen mit Ampel [SO9]"),
            "sitzungsgeld": ("yes", "SEPA-Datei, Schnittstellen zu Finanzverfahren und Personalabrechnung [SO8]"),
            "umlauf": ("yes", "Umlaufverfahren und Online-Abstimmung in Mandatos [SO4]"),
            "mappe": ("yes", "Persönliches Wasserzeichen je Empfänger:in [SO10]"),
            "freigabe": ("yes", "Mitzeichnung, Freigabe und Genehmigung [SO1]"),
            "ablaeufe": ("yes", "Workflow mit Terminen je Bearbeitungsschritt [SO1]"),
            "word": ("yes", "MS Office, OpenOffice oder LibreOffice [SO11]"),
            "mobilfreigabe": ("yes", "Session App für iPhone und iPad [SO1]"),
            "gremieninfo": ("yes", "SessionNet mit Rollen- und Rechtesystem [SO3]"),
            "app": ("yes", "Mandatos für Windows, iOS und Android, offline [SO4]"),
            "notizen": ("yes", "Kommentare und Markierungen, geräteübergreifend abgeglichen [SO4]"),
            "abstimmung": ("yes", "Offen, namentlich oder geheim [SO6]"),
            "zertifikat": ("yes", "Zertifiziert durch die gpaNRW [SO6]"),
            "redner": ("partial", "Präsentationsmodus für den Saal [SO6]"),
            "portal": ("yes", "SessionNet [SO3]"),
            "suche": ("yes", "Recherche in SessionNet, Volltextsuche in Mandatos [SO3, SO4]"),
            "website": ("yes", "Integration in Internet- und Intranet-Portale [SO3]"),
            "oparl": ("yes", "OParl-API [SO11]"),
            "dms": ("yes", "DMS- und Archivschnittstelle [SO11]"),
            "verzeichnis": ("yes", "LDAP und Single Sign-on [SO11]"),
            "kalender": ("yes", "Groupware- und E-Mail-Integration [SO11]"),
            "zwei_faktor": ("yes", "Wahlweise [SO5]"),
            "protokoll": ("yes", "Datenschutzgerechte Protokollierung [SO5]"),
            "ki_protokoll": ("yes", "Schnittstelle zu externen KI-Anbietern, etwa SpeechMind oder Scriba [SO12]"),
        },
    },
    "mandari-vs-sternberg": {
        "kurzname": "Sternberg SD.NET",
        "kartenname": "Sternberg SD.NET",  # ohne „Session“: Karten färben Produktnamen in mandari-Kennfarben
        "spalte": "Sternberg",
        "anbieter": "STERNBERG Software GmbH & Co. KG (Bielefeld)",
        "produkt": "SD.NET (Sitzungsmanagement), Gremieninfosystem SD.NET RIM, RICH SitzungsApps, App voteRICH",
        "kunden": "Mehr als 900 Installationen mit über 31.000 Anwender:innen in Deutschland, Österreich und der Schweiz (Eigenangabe) [ST7]",
        "website": "https://www.sitzungsdienst.net/",
        "cells": {
            "preise": ("unknown", "Staffel nach Einwohnerzahl oder Sitzungen, Preise auf Anfrage [ST7]"),
            "eigenbetrieb": ("yes", "Autonomer Betrieb [ST5]"),
            "cloud": ("yes", "S24-Cloud, Serverstandort Deutschland, ISO 27001 [ST8]"),
            "sitzung": ("yes", "Automatische Tagesordnung, Nachträge, Einladung [ST1, ST5]"),
            "niederschrift": ("yes", "Protokoll, Auszüge und Beschlussblätter [ST5]"),
            "beschlusskontrolle": ("yes", "Beschluss- und Antragskontrolle [ST1]"),
            "sitzungsgeld": ("yes", "SEPA und Schnittstellen zu Finanzverfahren [ST1]"),
            "mitteilung": ("yes", "Übermittlung im KONSENS-Mitteilungsverfahren [ST1]"),
            "umlauf": ("yes", "Umlaufbeschlüsse über WorkflowPlus [ST2]"),
            "mappe": ("yes", "Personalisiertes Wasserzeichen, Druck- und Versandmanager [ST2, ST5]"),
            "raeume": ("yes", "Raumbelegung mit Doppelbelegungsanzeige [ST1]"),
            "bekanntmachung": ("yes", "Amtsblattinformationssystem ABI.NET [ST1]"),
            "freigabe": ("yes", "Freigabestatus und Workflow [ST1]"),
            "ablaeufe": ("yes", "Individuell anpassbare Workflows [ST7]"),
            "word": ("yes", "Ganzheitliche Textverarbeitung, Import aus Word [ST5]"),
            "mobilfreigabe": ("yes", "WorkflowPlus im Gremieninfosystem und in der App [ST2]"),
            "gremieninfo": ("yes", "Geschützter Bereich in SD.NET RIM [ST2]"),
            "app": ("yes", "RICH für iOS, Android und Windows, offline [ST3]"),
            "notizen": ("yes", "Randnotizen mit anderen Mitgliedern teilen, Modul Akte [ST2, ST3]"),
            "antraege": ("yes", "Anträge über den Formularmanager [ST5]"),
            "fraktion": ("partial", "Fraktionssitzungen im Gremieninfosystem [ST2]"),
            "hybrid": ("yes", "Modul Interaktive Virtuelle Sitzung [ST6]"),
            "abstimmung": ("yes", "App voteRICH [ST1]"),
            "zertifikat": ("yes", "Interaktive Virtuelle Sitzung, zertifiziert durch die gpaNRW [ST6]"),
            "redner": ("partial", "Präsentation der Tagesordnung in der Sitzung [ST5]"),
            "portal": ("yes", "SD.NET RIM [ST2]"),
            "suche": ("yes", "Recherche mit markierter Fundstelle [ST2]"),
            "abo": ("partial", "E-Mail über neue Dokumente, Newsletter [ST2]"),
            "website": ("yes", "Portalsuche für die eigene Website, Layout im Erscheinungsbild der Kommune [ST2]"),
            "buergerapp": ("yes", "BürgerApp für iOS und Android [ST3]"),
            "schwaerzung": ("yes", "Automatisches Schwärzen einzelner Passagen [ST2]"),
            "oparl": ("yes", "OParl-Schnittstelle [ST2]"),
            "dms": ("yes", "DMS-Schnittstelle [ST5]"),
            "verzeichnis": ("yes", "Active Directory [ST7]"),
            "kalender": ("yes", "Outlook, GroupWise, Tobit [ST5]"),
            "bitv": ("unknown", "Entwicklung nach BITV 2.0 (Eigenangabe), zu einer Prüfung keine Angabe [ST2]"),
            "zwei_faktor": ("yes", "Auf Wunsch [ST2]"),
            "pruefung": ("yes", "Regelmäßige Penetrationstests durch unabhängige Stellen (Eigenangabe) [ST2]"),
            "ki_protokoll": ("yes", "Schnittstelle zu wählbaren KI-Anbietern [ST4]"),
        },
    },
    "mandari-vs-allris": {
        "kurzname": "ALLRIS (CC e-gov)",
        "kartenname": "ALLRIS",  # ohne „Session“: Karten färben Produktnamen in mandari-Kennfarben
        "spalte": "CC e-gov",
        "anbieter": "CC e-gov GmbH (Hamburg)",
        "produkt": "ALLRIS 4 (Sitzungsmanagement und Gremieninformation), ALLRIS kompakt für Gemeinden bis etwa 10.000 Einwohner:innen, ALLRIS-Apps",
        "kunden": "Über 650 Organisationen im Echtbetrieb (Eigenangabe) [AL6]",
        "website": "https://www.cc-egov.de/",
        "cells": {
            "preise": ("unknown", "Angebot auf Anfrage"),
            "eigenbetrieb": ("yes", "Installation beim Kunden [AL2]"),
            "cloud": ("yes", "Deutsches Rechenzentrum, ISO 27001, auf STACKIT [AL3]"),
            "sitzung": ("yes", "Periodische Planung, Standardtagesordnung, Einladung [AL2]"),
            "niederschrift": ("yes", "Niederschrift, automatische Beschlussauszüge [AL2]"),
            "beschlusskontrolle": ("yes", "Realisierungsworkflow [AL2]"),
            "sitzungsgeld": ("yes", "Übergabe an Kassenverfahren, HKR-Verfahren [AL1, AL2]"),
            "umlauf": ("yes", "Online-Abstimmung, häufigster Fall laut Anbieter das Umlaufverfahren [AL2]"),
            "raeume": ("yes", "Raum- und Ressourcenverwaltung [AL2]"),
            "freigabe": ("yes", "Mitzeichnungs- und Freigabeprozesse [AL1]"),
            "ablaeufe": ("yes", "Konfigurierbare Workflow-Engine mit Terminüberwachung [AL2]"),
            "word": ("yes", "MS Word oder integrierter Editor [AL2]"),
            "signatur": ("yes", "Signaturvorgänge [AL1]"),
            "gremieninfo": ("yes", "Personenbezogene Zugriffssteuerung [AL2]"),
            "app": ("yes", "Apps für iOS, Android und Windows, offline [AL2]"),
            "notizen": ("yes", "Notizen und Foren für Fraktionen und Gremien [AL2]"),
            "antraege": ("yes", "Online-Antragsverfahren [AL2]"),
            "fraktion": ("partial", "Foren und Antragsverfahren je Fraktion [AL2]"),
            "hybrid": ("yes", "Präsenz, hybrid und Videokonferenz [AL2]"),
            "abstimmung": ("yes", "Online-Abstimmung [AL2]"),
            "zertifikat": ("yes", "Zertifiziert durch die gpaNRW seit September 2023 [AL1]"),
            "stream": ("partial", "Audio und Video per Webcast; zu Sprungmarken keine Angabe [AL2]"),
            "saaltechnik": ("yes", "Einbindung von Konferenzanlagen [AL2]"),
            "portal": ("yes", "ALLRIS Bürgerinformationssystem [AL2]"),
            "suche": ("yes", "Volltextrecherche mit Ergebnisranking [AL2]"),
            "website": ("yes", "Schnittstellen zur Einbindung in die Website [AL2]"),
            "buergerapp": ("yes", "Bürger-App [AL2]"),
            "oparl": ("yes", "OParl-Schnittstelle [AL2]"),
            "kalender": ("yes", "WebCal-Funktion [AL2]"),
            "bitv": ("yes", "Gutachten: BITV-konform (Produktbeschreibung 2022) [AL2]"),
            "zwei_faktor": ("yes", "Einmalkennwort-App oder SMS [AL1]"),
            "protokoll": ("yes", "ALLRIS Audit-Log [AL1]"),
            "pruefung": ("yes", "Datenschutz-Zertifikat der datenschutz cert GmbH [AL2]"),
            "ki_protokoll": ("yes", "Protokollvorschläge direkt im System [AL4]"),
        },
    },
    "mandari-vs-regisafe": {
        "kurzname": "regisafe",
        "kartenname": "regisafe",  # ohne „Session“: Karten färben Produktnamen in mandari-Kennfarben
        "spalte": "regisafe",
        "anbieter": "regisafe GmbH (Waiblingen)",
        "produkt": "Fachverfahren Sitzungsdienst (KommunalPLUS Sitzung) mit Ratsinformationssystem, Bürgerinfoportal und Mandatsträger-App",
        "kunden": "Mehr als 500 Verwaltungen mit dem Ratsinformationssystem (Eigenangabe) [RS1]",
        "website": "https://www.regisafe.de/",
        "fairness_extra": (
            " Ausdrücklich hervorzuheben: Das regisafe-Ratsinformationssystem ist seit dem 7. Oktober 2024 "
            "als barrierefrei zertifiziert (Eigenangabe) – einen solchen geprüften Nachweis hat mandari "
            "derzeit noch nicht."
        ),
        "cells": {
            "preise": ("unknown", "Angebot auf Anfrage"),
            "eigenbetrieb": ("yes", "Lokaler Betrieb, Wechsel in die Cloud möglich [RS5]"),
            "cloud": ("partial", "Rechenzentren in Deutschland und Österreich, ISO 27001 [RS5]"),
            "sitzung": ("yes", "Tagesordnung, Einladungen und Bekanntmachungen [RS2]"),
            "niederschrift": ("yes", "Beschlüsse erfassen, Beratung dokumentieren [RS2]"),
            "beschlusskontrolle": ("yes", "Kontrolle der Beschlussumsetzung [RS2]"),
            "sitzungsgeld": ("yes", "KommunalPLUS Sitzungsgeld [RS2]"),
            "umlauf": ("yes", "Digitales Verfahren mit elektronischer Abstimmung [RS3]"),
            "bekanntmachung": ("yes", "Versand von Bekanntmachungen [RS2]"),
            "freigabe": ("yes", "Workflows für die Freigabe [RS2]"),
            "ablaeufe": ("yes", "Anpassbare Workflows [RS2]"),
            "signatur": ("yes", "Elektronische Signatur [RS2]"),
            "gremieninfo": ("yes", "Unterlagen je Öffentlichkeitsstatus [RS3]"),
            "app": ("yes", "Apps für iOS und Android, offline [RS1]"),
            "abstimmung": ("partial", "Einfache Abstimmungen elektronisch [RS1, RS3]"),
            "portal": ("yes", "Bürgerinfoportal [RS1]"),
            "dms": ("yes", "Verknüpfung mit der E-Akte [RS2]"),
            "bitv": ("yes", "Zertifiziert barrierefrei seit 7. Oktober 2024 [RS1]"),
            "ki_protokoll": ("yes", "GenAI-Niederschrift auf deutschen Servern, Löschung nach einer Woche [RS4]"),
        },
    },
}

QUELLEN_JE_ANBIETER = {
    "mandari-vs-somacos": "SO",
    "mandari-vs-sternberg": "ST",
    "mandari-vs-allris": "AL",
    "mandari-vs-regisafe": "RS",
}


def zelle(slug, key):
    """Zelle eines Anbieters; ohne Eintrag „keine öffentliche Angabe“."""
    return ANBIETER[slug]["cells"].get(key, ("unknown", ""))


# ── Lücken: was andere Systeme können und mandari noch nicht ─────────────────
# stufe: Text der Roadmap-Stufe; art: "geplant" (zugesagt oder geplant) oder "pruefung".
# zeilen: Funktionen aus GRUPPEN, an denen die Lücke hängt. Ein Anbieter zählt, wenn er dort „Ja“ oder
# „Teilweise“ hat. auch: weitere Anbieter aus der internen Analyse (öffentlich belegt).
LUECKEN = [
    {
        "key": "bitv", "art": "geplant", "stufe": "Zugesagt für Q4/2026",
        "titel": "Barrierefreiheit mit Prüfbericht",
        "zeilen": ["bitv"],
        "text": "Für mandari Session lassen wir die Barrierefreiheit nach BITV 2.0 prüfen und "
                "veröffentlichen den Prüfbericht. Bürgerportal und Work folgen 2026/27.",
        "link": ("Issue #44 ansehen", "https://github.com/mandariOSS/mandari/issues/44"),
    },
    {
        "key": "abstimmung", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "Stimmabgabe am eigenen Gerät",
        "zeilen": ["abstimmung", "zertifikat"], "auch": "OpenSlides",
        "text": "Heute erfasst der Sitzungsdienst die Stimmen im Live-Cockpit. Geplant ist die "
                "Stimmabgabe am eigenen Gerät, offen und namentlich, mit Freigabe, Zeitfenster und "
                "Prüfpfad – so gebaut, dass eine Prüfstelle sie zertifizieren kann.",
        "link": ("Issue #141 ansehen", "https://github.com/mandariOSS/mandari/issues/141"),
    },
    {
        "key": "sitzungsleitung", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "Rednerliste, Saalanzeige und Livestream mit Sprungmarken",
        "zeilen": ["redner", "stream"], "auch": "OpenSlides",
        "text": "Teil des Vorhabens „Hybride und digitale Gremiensitzungen“: Wortmeldungen mit "
                "Redezeit, Anzeige im Saal und Aufzeichnungen, die sich je Tagesordnungspunkt "
                "abspielen lassen.",
        "link": ("Vorhaben #156 ansehen", "https://github.com/mandariOSS/mandari/issues/156"),
    },
    {
        "key": "ki_protokoll", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "KI-Entwurf der Niederschrift",
        "zeilen": ["ki_protokoll"], "auch": "more! software",
        "text": "Aus der Aufzeichnung entsteht ein Entwurf je Tagesordnungspunkt, den der Sitzungsdienst "
                "prüft und übernimmt. Transkription ohne Übermittlung in Drittländer, Nichtöffentliches "
                "nur mit einem selbst betriebenen Sprachmodell.",
        "link": ("Issue #49 ansehen", "https://github.com/mandariOSS/mandari/issues/49"),
    },
    {
        "key": "app", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "App für Ratsmitglieder und Bürger:innen",
        "zeilen": ["app", "buergerapp"],
        "text": "Eine App für Android und iOS: zuerst für Bürger:innen, danach ein Modus für "
                "Ratsmitglieder mit Sitzungsmappen offline und persönlichen Anmerkungen.",
        "link": ("Vorhaben #113 ansehen", "https://github.com/mandariOSS/mandari/issues/113"),
    },
    {
        "key": "vorlagen", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "Vorlagen und Abläufe im vollen Umfang",
        "zeilen": ["ablaeufe", "word", "signatur", "schwaerzung", "raeume"],
        "text": "Vorlagenarten mit Word-Import, parallele Mitzeichnung mit Stellvertretung und "
                "Eskalation, elektronische Signatur, Veröffentlichungsfassung mit Schwärzung sowie "
                "Räume und Ressourcen als Stammdaten.",
        "link": ("Vorhaben #496 ansehen", "https://github.com/mandariOSS/mandari/issues/496"),
    },
    {
        "key": "anbindung", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "Anbindung an E-Akte und Verzeichnisdienst",
        "zeilen": ["dms", "verzeichnis"],
        "text": "Übergabe von Vorlagen, Niederschriften und Beschlüssen an DMS und E-Akte "
                "(CMIS, XDomea) sowie Anmeldung über den Verzeichnisdienst der Verwaltung "
                "(SAML 2.0, OpenID Connect, <a href=\"https://github.com/mandariOSS/mandari/issues/95\">Issue #95</a>).",
        "link": ("Issue #154 ansehen", "https://github.com/mandariOSS/mandari/issues/154"),
    },
    {
        "key": "pruefung", "art": "geplant", "stufe": "Geplant für 2027",
        "titel": "Unabhängige Sicherheitsprüfung",
        "zeilen": ["pruefung"],
        "text": "Externer Penetrationstest von Anwendung, Schnittstellen, Anmeldung und "
                "Mandantentrennung; die Zusammenfassung veröffentlichen wir im Trust Center.",
        "link": ("Issue #97 ansehen", "https://github.com/mandariOSS/mandari/issues/97"),
    },
    {
        "key": "mandatsbereich", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Eigener Bereich für Ratsmitglieder",
        "zeilen": ["gremieninfo", "mappe"],
        "text": "Ein geschützter Webbereich mit allen Unterlagen der eigenen Gremien, auch den "
                "nichtöffentlichen, mit Hinweis auf Nachträge, personalisierter Sitzungsmappe mit "
                "Wasserzeichen und Einsicht in die eigene Sitzungsgeld-Abrechnung. Heute kommen die "
                "Unterlagen mit der Ladung per E-Mail.",
        "link": ("Issue #46 ansehen", "https://github.com/mandariOSS/mandari/issues/46"),
    },
    {
        "key": "unterwegs", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Freigabe unterwegs",
        "zeilen": ["mobilfreigabe"],
        "text": "Eine Ansicht für Smartphone und Tablet, in der die Verwaltungsleitung Vorlagen "
                "freigibt und mitzeichnet, mit Hinweis auf Vertretungen.",
        "link": ("Issue #151 ansehen", "https://github.com/mandariOSS/mandari/issues/151"),
    },
    {
        "key": "umlauf", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Umlaufverfahren mit Stimmabgabe online",
        "zeilen": ["umlauf"],
        "text": "Heute erfasst der Sitzungsdienst den Rücklauf eines Umlaufbeschlusses. Geprüft wird "
                "die Stimmabgabe der Mitglieder online, mit Fristen und den Regeln des jeweiligen "
                "Landesrechts.",
        "link": None,
    },
    {
        "key": "mitteilung", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Mitteilungen an das Finanzamt",
        "zeilen": ["mitteilung"],
        "text": "Zahlungen für ehrenamtliche Tätigkeit sind nach der Mitteilungsverordnung oberhalb "
                "der Bagatellgrenze elektronisch an die Finanzverwaltung zu melden "
                "(<a href=\"https://www.bundesfinanzministerium.de/Content/DE/Downloads/BMF_Schreiben/Weitere_Steuerthemen/Abgabenordnung/2024-12-12-anwendung-der-mv-ab-2025.pdf?__blob=publicationFile&amp;v=2\">BMF-Schreiben vom 12.12.2024</a>). "
                "Das Sitzungsgeld in mandari liefert heute die Jahresübersicht; die Übermittlung prüfen wir.",
        "link": ("Issue #152 ansehen", "https://github.com/mandariOSS/mandari/issues/152"),
    },
    {
        "key": "bekanntmachung", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Bekanntmachung und Amtsblatt",
        "zeilen": ["bekanntmachung"],
        "text": "Öffentliche Bekanntmachung der Sitzungen nach der Hauptsatzung, etwa auf der "
                "Website oder im Amtsblatt, mit Nachweis über Zeitpunkt und Ort.",
        "link": None,
    },
    {
        "key": "website", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Einbindung in die Website der Kommune",
        "zeilen": ["website"],
        "text": "Suche, nächste Sitzungen und aktuelle Beschlüsse als einbettbare Bausteine für die "
                "Website der Kommune, ohne Tracking. Heute gibt es dafür Kalender-Feeds und die "
                "OParl-Schnittstelle.",
        "link": None,
    },
    {
        "key": "saaltechnik", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "Konferenz- und Abstimmungsanlagen im Saal",
        "zeilen": ["saaltechnik"], "auch": "PROVOX",
        "text": "Anbindung vorhandener Saaltechnik, damit Wortmeldungen und Stimmen aus der Anlage "
                "in Rednerliste, Abstimmung und Niederschrift einfließen.",
        "link": None,
    },
    {
        "key": "ki_schreiben", "art": "pruefung", "stufe": "In Prüfung",
        "titel": "KI-Schreibhilfe im Sitzungsdienst",
        "zeilen": ["ki_schreiben"], "auch": "more! software",
        "text": "In mandari Work hilft eine KI beim Formulieren von Anträgen. Geprüft wird dieselbe "
                "Hilfe für Vorlagen im Sitzungsdienst, mit wählbarem Anbieter und Betrieb in der EU.",
        "link": None,
    },
]


def anbieter_mit(luecke):
    """Slugs der vier Anbieter, die bei einer Lücke laut Quelle „Ja“ oder „Teilweise“ haben."""
    treffer = []
    for slug in ANBIETER:
        if any(zelle(slug, key)[0] in ("yes", "partial") for key in luecke["zeilen"]):
            treffer.append(slug)
    return treffer


def _aufzaehlung(namen):
    if len(namen) <= 1:
        return "".join(namen)
    return ", ".join(namen[:-1]) + " und " + namen[-1]


def _ohne_kuerzel(text):
    import re

    return re.sub(r"\s*\[[A-Z]{2}\d+(?:, [A-Z]{2}\d+)*\]", "", text).strip()


# ── Blöcke ───────────────────────────────────────────────────────────────────


def _hdr(title, subline="", anchor=""):
    from marketing.management.commands.migrate_pages_to_streamfield import hdr

    return hdr(title=title, subline=subline, anchor_id=anchor)


def _cta(label, url, style="primary"):
    from marketing.management.commands.migrate_pages_to_streamfield import cta

    return cta(label, url, "", style)


def _cell(status, note=""):
    return {"status": status, "note": note}


def hinweis(name):
    """Rechtlich saubere Fußnote für jede Vergleichsseite."""
    return ("disclaimer_box", {
        "icon": "scale", "color": "gray",
        "body": (
            "<p><strong>Hinweis zu diesem Vergleich:</strong> Alle Aussagen über "
            f"{name} beruhen auf öffentlich verfügbaren Informationen – Websites und "
            f"Produktbeschreibungen der Anbieter, abgerufen am {ABRUF}. Jede Angabe trägt ein "
            "Quellenkürzel, die Quellen stehen am Ende der Seite. Wo wir keine öffentliche Angabe "
            "gefunden haben, steht „keine öffentliche Angabe“ – das ist keine Aussage über das Produkt "
            "selbst. Alle genannten Marken und Produktnamen sind Eigentum ihrer jeweiligen Inhaber. "
            "Fehler oder neuere Angaben bitte an <a href=\"mailto:hello@mandari.de\">hello@mandari.de</a> – "
            "wir korrigieren umgehend.</p>"
        ),
    })


def _quellen_html(prefixe):
    zeilen = []
    for kuerzel, (titel, url) in QUELLEN.items():
        if any(kuerzel.startswith(p) for p in prefixe):
            domain = url.split("//", 1)[1].split("/", 1)[0].removeprefix("www.")
            zeilen.append(f"<li>[{kuerzel}] <a href=\"{url}\">{titel}</a> ({domain})</li>")
    return "<ul>" + "".join(zeilen) + "</ul>"


def quellen_block(prefixe, *, anchor="quellen"):
    return ("richtext_section", {
        "header": _hdr("Quellen", f"Abgerufen am {ABRUF}. Kundenzahlen und Leistungsmerkmale sind "
                                  "Eigenangaben der Anbieter.", anchor),
        "background": "white",
        "body": _quellen_html(prefixe) + (
            "<p>Die Angaben in der Spalte mandari beruhen auf dem Stand der Software vom "
            f"{ABRUF}. mandari ist in der Beta-Phase; was neu ist, zeigen die "
            "<a href=\"/releases/\">Release-Notes</a>, was kommt, die <a href=\"/roadmap/\">Roadmap</a>.</p>"
        ),
    })


def vergleichstabelle(slug):
    """comparison_table einer Anbieterseite: alle Funktionen, mit Erläuterung und Quelle."""
    v = ANBIETER[slug]
    gruppen = []
    for titel, rows in GRUPPEN:
        gruppen.append({
            "title": titel,
            "rows": [{
                "label": label,
                "mandari": _cell(*MANDARI[key]),
                "competitor": _cell(*zelle(slug, key)),
            } for key, label in rows],
        })
    return ("comparison_table", {
        "header": _hdr("Der Vergleich im Detail",
                       f"{ANZAHL_FUNKTIONEN} Funktionen in {len(GRUPPEN)} Bereichen, Stand {STAND}. "
                       "Was mandari noch fehlt, steht als „Noch nicht verfügbar“ mit der Stufe aus der Roadmap dabei.",
                       "tabelle"),
        "competitor_label": v["kurzname"],
        "groups": gruppen,
        "footnote": (
            f"<p><sup>1</sup> <strong>„Keine öffentliche Angabe“ (Stand {STAND}):</strong> In den genannten "
            "Quellen war zum Abrufzeitpunkt keine entsprechende Angabe auffindbar. Das ist keine Aussage "
            "über den tatsächlichen Funktionsumfang. Angaben in der Spalte mandari sind Eigenangaben; "
            "„Noch nicht verfügbar“ nennt die Stufe aus der <a href=\"/roadmap/\">Roadmap</a>.</p>"
        ),
    })


def marktuebersicht():
    """market_matrix der Übersichtsseite: mandari und alle vier Anbieter, nur Status."""
    spalten = [{"name": "mandari", "url": ""}] + [
        {"name": v["spalte"], "url": f"/vergleich/{slug}/"} for slug, v in ANBIETER.items()
    ]
    gruppen = []
    for titel, rows in GRUPPEN:
        zeilen = []
        for key, label in rows:
            status, _ = MANDARI[key]
            zellen = [_cell(status, MANDARI_KURZ.get(key, "") if status == "open" else "")]
            zellen += [_cell(zelle(slug, key)[0]) for slug in ANBIETER]
            zeilen.append({"label": label, "cells": zellen})
        gruppen.append({"title": titel, "rows": zeilen})
    return ("market_matrix", {
        "header": _hdr("Alle Funktionen auf einen Blick",
                       f"{ANZAHL_FUNKTIONEN} Funktionen in {len(GRUPPEN)} Bereichen. Erläuterungen und Belege "
                       "stehen in den Einzelvergleichen, die Spaltenköpfe führen dorthin.", "uebersicht"),
        "columns": spalten,
        "groups": gruppen,
        "footnote": (
            "<p>„Ja“ und „Teilweise“ bei den Anbietern folgen deren öffentlichen Angaben; „k. A.“ heißt: keine "
            "öffentliche Angabe gefunden, nicht „fehlt“. Bei mandari steht für Fehlendes die Stufe aus der "
            "<a href=\"/roadmap/\">Roadmap</a>.</p>"
        ),
    })


def _luecken_zeilen(art, slug=None):
    """split_rows-Zeilen der Lücken: alle (Übersicht, Roadmap) oder die eines Anbieters."""
    zeilen = []
    for luecke in LUECKEN:
        if luecke["art"] != art:
            continue
        mit = anbieter_mit(luecke)
        if slug is not None:
            if slug not in mit:
                continue
            belege = [_ohne_kuerzel(zelle(slug, key)[1]) for key in luecke["zeilen"]
                      if zelle(slug, key)[0] in ("yes", "partial")]
            label = f"Bei {ANBIETER[slug]['spalte']}: " + "; ".join(b for b in belege if b)
        else:
            namen = [ANBIETER[s]["spalte"] for s in mit]
            if luecke.get("auch"):
                namen.append(luecke["auch"])
            if not namen:
                continue
            label = "Vorhanden bei " + _aufzaehlung(namen)
        link_label, link_url = luecke["link"] or ("", "")
        zeilen.append({
            "title": luecke["titel"], "label": label, "status": luecke["stufe"],
            "text": f"<p>{luecke['text']}</p>", "link_label": link_label, "link_url": link_url,
            "anchor_id": "",
        })
    return zeilen


def luecken_bloecke(slug=None, *, anchor="fehlt"):
    """Zwei split_rows-Blöcke: zugesagt/geplant und in Prüfung (je höchstens acht Zeilen)."""
    name = ANBIETER[slug]["kurzname"] if slug else ""
    bloecke = []
    geplant = _luecken_zeilen("geplant", slug)
    pruefung = _luecken_zeilen("pruefung", slug)
    if geplant:
        sub = (f"Was {name} laut öffentlicher Angabe bietet und mandari noch nicht – mit Zeitraum aus der Roadmap."
               if slug else
               "Funktionen, die etablierte Systeme bieten und mandari noch nicht. Für diese steht ein Zeitraum in der Roadmap.")
        bloecke.append(("split_rows", {
            "header": _hdr("Was mandari noch fehlt: zugesagt und geplant", sub, anchor),
            "rows": geplant[:8], "note": "", "background": "white",
        }))
    if pruefung:
        sub = ("Auch das bietet " + name + " laut öffentlicher Angabe. Wir prüfen es, einen Termin nennen wir erst, "
               "wenn er belastbar ist." if slug else
               "Ebenfalls Lücken aus dem Vergleich. Wir prüfen sie, einen Termin nennen wir erst, wenn er belastbar ist.")
        bloecke.append(("split_rows", {
            "header": _hdr("Was mandari noch fehlt: in Prüfung", sub, "" if geplant else anchor),
            "rows": pruefung[:8],
            "note": "<p>Fehlt Ihnen etwas, das hier nicht steht? <a href=\"/kontakt/?subject=Roadmap-Idee\">Schreiben Sie uns.</a></p>",
            "background": "gray",
        }))
    return bloecke


def anbieterseite(slug):
    """Blockliste einer mandari-vs-X-Seite."""
    v = ANBIETER[slug]
    name = v["kurzname"]
    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "mandari vs.", "title_highlight": name,
            "subline": (
                f"{ANZAHL_FUNKTIONEN} Funktionen nebeneinander, Stand {STAND}, jede Angabe zu {name} mit Quelle. "
                "Was mandari noch fehlt, steht ausdrücklich dabei."
            ),
            "ctas": [_cta("Erstgespräch vereinbaren", "/kontakt/?subject=RIS-Vergleich"),
                     _cta("Alle Vergleiche", "/vergleich/", "secondary")],
            "background_color": "primary",
        }),
        hinweis(name),
        ("two_column_use_case", {
            "header": _hdr(f"mandari und {name} im Überblick",
                           "Zwei unterschiedliche Ansätze – hier die Eckdaten beider Anbieter."),
            "left_card": {
                "color": "primary", "icon": "sparkles", "badge": "", "status_badges": [],
                "title": "mandari", "subtitle": "Open-Source-Plattform in der Beta-Phase",
                "description": "Drei Produkte auf einer offenen Plattform: Session für die Verwaltung, Work für "
                               "Fraktionen, Insight als Bürgerportal.",
                "bullets": [{"icon": "check", "text": "Quellcode öffentlich (AGPL-3.0)"},
                            {"icon": "check", "text": "Bürgerportal immer inklusive"},
                            {"icon": "check", "text": "Jung und aktiv entwickelt, Roadmap öffentlich"}],
                "cta_label": "Produkte ansehen", "cta_url": "/produkte/", "cta_icon": "arrow-right",
            },
            "right_card": {
                "color": "gray", "icon": "building-2", "badge": "", "status_badges": [],
                "title": v["kartenname"], "subtitle": v["anbieter"],
                "description": v["produkt"] + ".",
                "bullets": [{"icon": "users", "text": v["kunden"]},
                            {"icon": "history", "text": "Etabliertes Produkt mit langjähriger Praxis in Verwaltungen"}],
                "cta_label": "Website des Anbieters", "cta_url": v["website"], "cta_icon": "external-link",
            },
        }),
        vergleichstabelle(slug),
        *luecken_bloecke(slug),
        ("disclaimer_box", {
            "icon": "flask-conical", "color": "amber",
            "body": (
                f"<p><strong>Fairerweise:</strong> {name} ist ein etabliertes Produkt mit langjähriger Praxis im "
                "Verwaltungsalltag und bietet heute Funktionen, die mandari erst entwickelt – die Liste oben "
                "nennt sie. mandari ist jung und in der Beta-Phase. Dafür ist mandari offen: Quellcode, Preise "
                "und Roadmap sind öffentlich, das Bürgerportal ist kostenlos."
                + v.get("fairness_extra", "") + "</p>"
            ),
        }),
        quellen_block([QUELLEN_JE_ANBIETER[slug]]),
        ("gradient_cta", {
            "title": "Selbst vergleichen ist besser.",
            "subline": "Sehen Sie sich mandari im Bürgerportal an oder vereinbaren Sie eine Vorführung – "
                       "unverbindlich und ohne Vertriebsdruck.",
            "ctas": [_cta("Vorführung anfragen", "/kontakt/?subject=Demo-RIS-Vergleich"),
                     _cta("Bürgerportal ansehen", "/insight/", "outline")],
            "gradient_from": "primary",
        }),
    ]


def uebersichtsseite():
    """Blockliste von /vergleich/."""
    karten = []
    for slug, v in ANBIETER.items():
        karten.append({
            "color": "gray", "icon": "scale", "badge": "", "status_badges": [],
            "title": f"mandari vs. {v['kartenname']}", "subtitle": v["anbieter"],
            "description": v["produkt"] + ".", "bullets": [],
            "cta_label": "Zum Einzelvergleich", "cta_url": f"/vergleich/{slug}/", "cta_icon": "arrow-right",
        })
    return [
        ("hero", {
            "badge_text": "", "badge_icon": "", "badge_color": "primary",
            "title": "mandari im Vergleich", "title_highlight": "mit etablierten RIS-Anbietern",
            "subline": (
                f"Was etablierte Ratsinformationssysteme können, was mandari kann und was mandari noch fehlt: "
                f"{ANZAHL_FUNKTIONEN} Funktionen, Stand {STAND}, jede Angabe mit Quelle."
            ),
            "ctas": [_cta("Erstgespräch vereinbaren", "/kontakt/?subject=RIS-Vergleich"),
                     _cta("Was mandari noch fehlt", "#fehlt", "secondary")],
            "background_color": "primary",
        }),
        hinweis("die verglichenen Anbieter"),
        marktuebersicht(),
        *luecken_bloecke(),
        ("mandari_cards", {
            "header": _hdr("Die Einzelvergleiche",
                           "Jede Funktion mit Erläuterung und Quelle, dazu die Lücken gegenüber dem jeweiligen Anbieter.",
                           "anbieter"),
            "columns": "4", "background": "white",
            "cards": karten,
        }),
        ("richtext_section", {
            "header": _hdr("Wie wir vergleichen", "", "methodik"),
            "background": "gray",
            "body": (
                f"<p>Wir vergleichen {ANZAHL_FUNKTIONEN} Funktionen in {len(GRUPPEN)} Bereichen: Offenheit und "
                "Betrieb, Sitzungsdienst, Vorlagen und Abläufe, Ratsmitglieder und Fraktionen, Sitzung live, "
                "Öffentlichkeit, Schnittstellen, Barrierefreiheit und Sicherheit sowie künstliche Intelligenz. "
                "Die Auswahl folgt dem, was Kommunen in Ausschreibungen und Markterkundungen abfragen, und dem, "
                "was die Anbieter selbst als Leistung nennen.</p>"
                "<p>Grundlage sind ausschließlich öffentliche Quellen: Produktseiten, Produktbeschreibungen und "
                f"Broschüren, abgerufen am {ABRUF}. Kundenzahlen und Leistungsmerkmale sind Eigenangaben der "
                "Anbieter. Wo wir nichts gefunden haben, schreiben wir „keine öffentliche Angabe“. Die Lücken "
                "von mandari nennen wir ausdrücklich, mit der Stufe aus der Roadmap: zugesagt, geplant mit "
                "Zeitraum oder in Prüfung. Weitere Anbieter wie more! software, PROVOX und OpenSlides haben "
                "wir in die Lückenanalyse einbezogen.</p>"
                "<p>Bei den Preisen gilt: Keiner der vier Anbieter veröffentlicht eine Preisliste; die Angebote "
                "kommen auf Anfrage. mandari nennt die Preise für Work und das kostenlose Bürgerportal öffentlich, "
                "die Preisliste für Session ist in Vorbereitung.</p>"
            ),
        }),
        quellen_block(["SO", "ST", "AL", "RS"]),
        ("gradient_cta", {
            "title": "Die beste Entscheidung ist eine informierte.",
            "subline": "Sprechen Sie mit uns über Ihre Anforderungen – wir sagen Ihnen auch offen, wenn mandari "
                       "(noch) nicht passt.",
            "ctas": [_cta("Erstgespräch vereinbaren", "/kontakt/?subject=RIS-Vergleich"),
                     _cta("Bürgerportal ansehen", "/insight/", "outline")],
            "gradient_from": "primary",
        }),
    ]


def roadmap_luecken():
    """Abschnitt für /roadmap/: alle Lücken aus dem Vergleich, nach Stufe."""
    bloecke = []
    for art, titel, sub, bg in (
        ("geplant", "Aus dem Marktvergleich: zugesagt und geplant",
         f"Funktionen, die etablierte Ratsinformationssysteme bieten und mandari noch nicht (Stand {STAND}). "
         "Details im RIS-Vergleich.", "white"),
        ("pruefung", "Aus dem Marktvergleich: in Prüfung",
         "Lücken ohne Termin. Wir nennen einen Zeitraum, sobald er belastbar ist.", "gray"),
    ):
        bloecke.append(("split_rows", {
            "header": _hdr(titel, sub, "marktvergleich" if art == "geplant" else ""),
            "rows": _luecken_zeilen(art)[:8],
            "note": ("<p><a href=\"/vergleich/\">Zum RIS-Vergleich mit Quellen</a></p>" if art == "pruefung" else ""),
            "background": bg,
        }))
    return bloecke
