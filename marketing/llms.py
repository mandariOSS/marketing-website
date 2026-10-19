"""
/llms.txt (https://llmstxt.org/): Übersicht der Website für Sprachmodelle und KI-Suchen (mandari#939).

Titel und Beschreibung jeder Seite kommen aus dem CMS (``seo_title`` bzw. Titel und ``search_description``), die
Kurzbeschreibung oben aus der Meta-Description der Startseite. So steht hier nichts, was nicht auch auf der Seite
steht, und neue Texte wirken ohne Codeänderung. Verlinkt werden nur veröffentlichte, öffentliche Seiten; fehlt eine
Seite, entfällt ihre Zeile.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.http import HttpResponse
from django.views.decorators.http import require_http_methods
from wagtail.models import Page, Site

from marketing import seo

#: Abschnitte und ihre Seiten (Pfade relativ zur Website) in der Reihenfolge der Ausgabe
ABSCHNITTE: tuple[tuple[str, tuple[str, ...]], ...] = (
    (
        "Produkte",
        (
            "/produkte/",
            "/ratsinformationssystem/",
            "/sitzungsmanagement/",
            "/kommunen/",
            "/buergerinformationssystem/",
            "/fraktionen/",
            "/oparl-schnittstelle/",
        ),
    ),
    (
        "Vergleich und Umstieg",
        (
            "/vergleich/",
            "/vergleich/mandari-vs-allris/",
            "/vergleich/mandari-vs-somacos/",
            "/vergleich/mandari-vs-sternberg/",
            "/vergleich/mandari-vs-regisafe/",
            "/migration/",
            "/vergabe/",
        ),
    ),
    (
        "Preise, Vertrauen und offener Code",
        ("/preise/", "/trust/", "/barrierefreiheit/", "/transparenz/", "/open-source/", "/roadmap/", "/releases/"),
    ),
    ("Unternehmen", ("/unternehmen/", "/presse/", "/partner/", "/kontakt/")),
    ("Optional", ("/impressum/", "/datenschutz/", "/quellen/")),
)

#: Feste Angaben über die Website hinaus (Anwendung, Dokumentation, Code); nur, was dort öffentlich beschrieben ist
GRUNDDATEN = (
    "Bürgerportal mandari Insight mit den öffentlichen Ratsinformationen angebundener Kommunen: {basis}/insight/",
    "Offene Schnittstelle nach OParl 1.1 (lesend, ohne Anmeldung, JSON): {basis}/oparl/v1/system",
    "Dokumentation: https://docs.mandari.de, eigene Übersicht für Sprachmodelle: https://docs.mandari.de/llms.txt",
    "Quellcode: https://github.com/mandariOSS",
    "Wie mandari öffentliche Ratsinformationen abruft (Kennung, Takt, Kontakt): {basis}/ingestor/",
)


def _seiten() -> dict[str, Page]:
    """Veröffentlichte, öffentliche Seiten der Standard-Site nach Pfad (``/kontakt/``)."""
    site = Site.objects.select_related("root_page").filter(is_default_site=True).first()
    if site is None:
        return {}
    seiten = {}
    for seite in site.root_page.get_descendants(inclusive=True).live().public().specific():
        adresse = seite.get_url()
        if adresse:
            seiten[urlsplit(adresse).path or "/"] = seite
    return seiten


def _zeile(seite: Page) -> str:
    titel = (getattr(seite, "seo_title", "") or seite.title).strip()
    beschreibung = " ".join((getattr(seite, "search_description", "") or "").split())
    adresse = seo.absolute_url(urlsplit(seite.get_url() or "/").path)
    return f"- [{titel}]({adresse})" + (f": {beschreibung}" if beschreibung else "")


def inhalt() -> str:
    """Text der /llms.txt im Markdown-Format von llmstxt.org."""
    basis = seo.site_url()
    seiten = _seiten()
    start = seiten.get("/")
    zusammenfassung = " ".join((getattr(start, "search_description", "") or "").split()) if start else ""
    zeilen = ["# mandari", ""]
    if zusammenfassung:
        zeilen += [f"> {zusammenfassung}", ""]
    zeilen += [f"- {angabe.format(basis=basis)}" for angabe in GRUNDDATEN]
    for ueberschrift, pfade in ABSCHNITTE:
        eintraege = [_zeile(seiten[pfad]) for pfad in pfade if pfad in seiten]
        if eintraege:
            zeilen += ["", f"## {ueberschrift}", "", *eintraege]
    return "\n".join(zeilen) + "\n"


@require_http_methods(["GET", "HEAD"])
def llms_txt(request):
    antwort = HttpResponse(inhalt(), content_type="text/plain; charset=utf-8")
    antwort["Cache-Control"] = "public, max-age=3600"
    return antwort
