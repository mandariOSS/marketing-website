"""
Suchmaschinen-Titel und Meta-Descriptions einzelner Seiten (SEO-Nachtrag, Issue mandariOSS/mandari#914).

Ziel nach zwei externen SEO-Prüfungen: Titel mit 30–60 Zeichen einschließlich „ | mandari“, Descriptions mit
120–155 Zeichen. Kurze Titel wie „Preise | mandari“ sagen in der Trefferliste nichts; Descriptions unter 120 Zeichen
ersetzt Google oft durch einen beliebigen Textausschnitt. Keine Preisangaben im Titel. Descriptions versprechen nur,
was auf der Seite steht; Rechtsgrundlagen (DSA, BITV 2.0 …) nur, wenn die Seite sie nennt.

Die Einträge überschreiben ``seo_title`` und ``search_description`` aus ``MARKETING_PAGE_META``
(``setup_initial_pages``), sie gelten damit für neue Datenbanken, ``migrate_pages_to_streamfield`` und
``refresh_seeded_page``. Bestehende Seiten bringt ``python manage.py refresh_seeded_page <slug> --nur-meta`` auf
diesen Stand, ohne den Inhalt anzurühren. Ausgenommen sind Startseite, Rechtstexte und Kontakt.
``marketing/tests/test_seo_texte.py`` prüft Längen und Eindeutigkeit.
"""

SEO_TEXTE = {
    "preise": {
        "seo_title": "Preise für Verwaltung, Fraktionen und Bürgerportal",
    },
    "migration": {
        "search_description": (
            "Wechsel von ALLRIS, regisafe oder Somacos zu mandari Session: der Plan in vier Schritten, was an Daten "
            "mitkommt und was Pilotkommunen erhalten."
        ),
    },
    "roadmap": {
        "seo_title": "Roadmap: was wir als Nächstes bauen",
        "search_description": (
            "Die öffentliche Roadmap von mandari: was als Nächstes kommt für Sitzungsdienst, Fraktionen und "
            "Bürgerportal – mit Zeitpunkt und Verbindlichkeitsstufe."
        ),
    },
    "vergabe": {
        "seo_title": "Vergabeunterlagen für Beschaffung und Prüfung",
    },
    "transparenz": {
        "search_description": (
            "Transparenzbericht von mandari: Behördenanfragen, Sicherheitsvorfälle, Einnahmen und Ausgaben, Reichweite "
            "des Bürgerportals, vierteljährlich aktualisiert."
        ),
    },
    "barrierefreiheit": {
        "search_description": (
            "Erklärung zur Barrierefreiheit von mandari nach BITV 2.0 und EN 301 549: was schon funktioniert, wo wir "
            "noch arbeiten, Feedback und Schlichtung."
        ),
    },
    "abuse": {
        "search_description": (
            "Missbrauch melden bei mandari: Spam, rechtswidrige Inhalte, Verstöße gegen Datenschutz oder Urheberrecht "
            "und Belästigung. Meldestelle nach dem DSA."
        ),
    },
    "open-source": {
        "seo_title": "Open Source: öffentliches Geld, öffentlicher Code",
        "search_description": (
            "mandari steht vollständig unter AGPL-3.0: freie Anbieterwahl, Prüfbarkeit bis zur letzten Zeile und "
            "dauerhafte Verfügbarkeit für Ihre Verwaltung."
        ),
    },
    # Community-Seite in Du-Form (Leitfaden mandari-texte)
    "mitmachen": {
        "seo_title": "Mitmachen: Code, Doku und Übersetzungen",
        "search_description": (
            "Bau mit an mandari: Code, Dokumentation oder Übersetzungen beitragen, Fehler melden oder Ideen "
            "einbringen. Wir helfen dir beim Einstieg."
        ),
    },
    "unternehmen": {
        "seo_title": "Unternehmen: GovTech-Startup aus Münster",
        "search_description": (
            "mandari ist ein GovTech-Startup aus Münster: wofür wir stehen, Wertekompass, Geschäftsmodell, der Weg zu "
            "Version 1.0 und Angaben für Vergabeverfahren."
        ),
    },
    "partner": {
        "seo_title": "Partner werden: vier Wege der Zusammenarbeit",
    },
    "presse": {
        "seo_title": "Presse: Kurzprofil, Fakten und Logo-Paket",
    },
}

# Felder, die ``SEO_TEXTE`` setzen darf (alles andere bleibt Sache der Seed-Definition).
FELDER = ("seo_title", "search_description")


def anwenden(seiten_meta: list[dict]) -> list[dict]:
    """Überträgt ``SEO_TEXTE`` in die Seed-Metadaten (``MARKETING_PAGE_META``), an Ort und Stelle.

    Ein Eintrag für eine Seite, die es im Seed nicht gibt, ist ein Fehler: Er wirkte sonst nirgends.
    """
    nach_slug = {meta["slug"]: meta for meta in seiten_meta}
    unbekannt = sorted(set(SEO_TEXTE) - set(nach_slug))
    if unbekannt:
        raise KeyError(f"SEO_TEXTE für unbekannte Seiten: {', '.join(unbekannt)}")
    for slug, texte in SEO_TEXTE.items():
        for feld, wert in texte.items():
            if feld not in FELDER:
                raise KeyError(f"SEO_TEXTE[{slug!r}]: Feld {feld!r} ist nicht vorgesehen")
            nach_slug[slug][feld] = wert
    return seiten_meta
