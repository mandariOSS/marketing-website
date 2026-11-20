"""
Strukturierte Daten nach schema.org (JSON-LD) für Suchmaschinen.

Jede Seite trägt genau ein ``<script type="application/ld+json">`` mit einem ``@graph``
(``{% strukturdaten %}`` im ``<head>`` von ``templates/base.html``; auf der Startseite ist das die einzige
Änderung, Entscheidung vom 07.10.2026):

* **Organization** und **WebSite** auf allen Seiten. Ohne Rechtsform und Anschrift: Beides bestimmt der
  Stufenschalter Vorgründung/Gesellschaft (*Einstellungen → Unternehmensangaben*), die Daten hier sollen
  ihm nie widersprechen.
* **SoftwareApplication** auf den Seiten in ``SOFTWARE_SEITEN`` – bewusst ohne ``offers``: Preise stehen nur
  auf /preise/ und in der Preisliste, nicht in Daten, die Suchmaschinen als Angebot auswerten.
* Je Produkt (mandari Session, Work, Insight) eine eigene **SoftwareApplication** auf seiner Seite und auf den
  Übersichten (``PRODUKTE``), mit Zielgruppe und Stand aus ``SPRACHE.md`` („Stand der Produkte“). So ordnen
  Suchmaschinen und KI-Suchen jedes Produkt mit eigenem Namen ein, statt Angaben zu raten (mandari#1309).
* **SoftwareSourceCode** mit dem Repository auf /open-source/ und /produkte/.
* **FAQPage** aus jedem Baustein ``accordion_faq`` der Seite (Frage und Antwort als Klartext).
* **BreadcrumbList** auf Unterseiten, etwa /vergleich/mandari-vs-allris/.

Content-Security-Policy: Ein ``<script>`` mit ``type="application/ld+json"`` ist ein Datenblock. Der Browser
führt ihn nicht aus, ``script-src`` greift nicht (HTML Standard, „prepare the script element“); er braucht
weder Nonce noch Hash. Damit kein Text das Element beenden kann, sind ``<``, ``>`` und ``&`` im JSON als
Unicode-Escape geschrieben (wie bei Djangos ``json_script``).
"""

from __future__ import annotations

import json
import re
from html import unescape

from django.templatetags.static import static
from django.utils.html import strip_tags

from marketing import seo

BESCHREIBUNG = "mandari ist ein Open-Source-Ratsinformationssystem für Verwaltungen, Fraktionen und Bürger:innen."
SAME_AS = ["https://github.com/mandariOSS"]
LOGO = "brand/mandari-logo.png"
# Seiten, auf denen die Software selbst beschrieben ist (Slugs)
SOFTWARE_SEITEN = {"ratsinformationssystem", "kommunen", "produkte",
                   # Sachseiten zu weiteren Suchbegriffen (Issue mandariOSS/mandari#939)
                   "sitzungsmanagement", "buergerinformationssystem", "oparl-schnittstelle"}
SOFTWARE_URL = "/produkte/"
LIZENZ = "https://spdx.org/licenses/AGPL-3.0-or-later.html"
REPOSITORY = "https://github.com/mandariOSS/mandari"
DOKUMENTATION = "https://docs.mandari.de"
#: Worin sich mandari auskennt (``knowsAbout``): die Begriffe, unter denen man uns finden soll
FACHGEBIETE = ["Ratsinformationssystem", "Sitzungsdienst", "Fraktionsarbeit", "Bürgerinformationssystem", "OParl",
               "Open Government", "Kommunalpolitik"]
#: Seiten, auf denen die Organisation ausführlich steht (Fachgebiete, Gebiet, Kontaktweg), neben der Startseite. Auf allen
#: übrigen Seiten nur die Grundangaben: Jedes Byte im Kopf zählt gegen die Grenze der ersten TCP-Pakete
#: (scripts/check_kritisches_css.py)
ORGANISATION_SEITEN = {"unternehmen"}
#: Seiten mit allen Produkten (Slugs)
UEBERSICHTEN = {"produkte", "ratsinformationssystem"}
#: Seiten mit dem Quellcode (Slugs)
QUELLCODE_SEITEN = {"produkte", "open-source"}
#: Die drei Produkte: Kennung (Teil der ``@id``), Name, eigene Seite, Seiten (Slugs), Beschreibung, Zielgruppe und
#: Stand. Beschreibungen nach den Texten der Produktseiten, Stand wie in SPRACHE.md; keine Preise.
PRODUKTE = (
    {
        "kennung": "session",
        "name": "mandari Session",
        "url": "/kommunen/",
        "seiten": {"kommunen", "sitzungsmanagement"},
        "description": "Sitzungsdienst für Kommunalverwaltungen: Sitzungen, Ladung, Vorlagen, Niederschrift und "
                       "Beschlusskontrolle in einem System, mit offener OParl-Schnittstelle.",
        "zielgruppe": "Kommunalverwaltungen und ihr Sitzungsdienst",
        "stand": "Pilotphase",
    },
    {
        "kennung": "work",
        "name": "mandari Work",
        "url": "/fraktionen/",
        "seiten": {"fraktionen"},
        "description": "Fraktionssoftware: Sitzungen im Team vorbereiten, Anträge mit Fristen und Freigaben führen, "
                       "mit den Ratsdaten der eigenen Kommune.",
        "zielgruppe": "Fraktionen, Ratsmitglieder und Fraktionsgeschäftsstellen",
        "stand": "Offene Beta",
    },
    {
        "kennung": "insight",
        "name": "mandari Insight",
        "url": "/buergerinformationssystem/",
        "seiten": {"buergerinformationssystem"},
        "description": "Bürgerportal mit den öffentlichen Ratsinformationen der Kommunen: Sitzungen, Vorlagen und "
                       "Beschlüsse im Volltext finden und auf der Karte sehen, ohne Anmeldung.",
        "zielgruppe": "Bürger:innen, Presse und Zivilgesellschaft",
        "stand": "Im Einsatz",
        # Das Bürgerportal ist kostenlos (/preise/); das ist eine Eigenschaft, kein Angebot mit Preis
        "kostenlos": True,
    },
)

_ESCAPES = {ord("<"): "\\u003C", ord(">"): "\\u003E", ord("&"): "\\u0026"}
_ABSATZENDE = re.compile(r"<(?:/p|/li|br\s*/?|/h\d)\s*>", re.IGNORECASE)


def klartext(html) -> str:
    """Rich Text → einzeiliger Klartext; Absätze und Listenpunkte bleiben durch ein Leerzeichen getrennt."""
    text = _ABSATZENDE.sub(" ", str(html or ""))
    return " ".join(unescape(strip_tags(text)).split())


def _bloecke(page):
    """StreamField-Blöcke einer Seite (MarketingPage.body, LegalPage.body_stream)."""
    for feld in ("body", "body_stream"):
        wert = getattr(page, feld, None)
        if wert and hasattr(wert, "raw_data"):
            yield from wert


def faq(page) -> list[dict]:
    """Fragen und Antworten aller Bausteine ``accordion_faq`` einer Seite."""
    fragen = []
    for block in _bloecke(page):
        if block.block_type != "accordion_faq":
            continue
        for item in block.value.get("items") or []:
            frage, antwort = klartext(item.get("question")), klartext(item.get("answer"))
            if frage and antwort:
                fragen.append({
                    "@type": "Question",
                    "name": frage,
                    "acceptedAnswer": {"@type": "Answer", "text": antwort},
                })
    return fragen


def brotkrumen(page) -> list[dict]:
    """Pfad von der Startseite bis zur Seite, nur für Unterseiten (Startseite → Bereich → Seite)."""
    if page is None or getattr(page, "depth", 0) < 4:
        return []
    eintraege = []
    for vorfahr in page.get_ancestors(inclusive=True).filter(depth__gte=2).specific():
        teile = vorfahr.get_url_parts()
        if not teile:
            return []
        name = seo.BRAND if vorfahr.depth == 2 else vorfahr.title
        eintraege.append({
            "@type": "ListItem",
            "position": len(eintraege) + 1,
            "name": name,
            "item": seo.absolute_url(teile[2]),
        })
    return eintraege


def _produkt(produkt: dict, basis: str, organisation: str) -> dict:
    """Ein Produkt als ``SoftwareApplication``, Teil von mandari (``#software``)."""
    knoten = {
        "@type": "SoftwareApplication",
        "@id": f"{basis}#{produkt['kennung']}",
        "name": produkt["name"],
        "applicationCategory": "BusinessApplication",
        "operatingSystem": "Web",
        "url": seo.absolute_url(produkt["url"]),
        "license": LIZENZ,
        "description": produkt["description"],
        "audience": {"@type": "Audience", "audienceType": produkt["zielgruppe"]},
        "creativeWorkStatus": produkt["stand"],
        "softwareHelp": {"@type": "CreativeWork", "url": DOKUMENTATION},
        "isPartOf": {"@id": basis + "#software"},
        "publisher": {"@id": organisation},
    }
    if produkt.get("kostenlos"):
        knoten["isAccessibleForFree"] = True
    return knoten


def graph(page=None) -> list[dict]:
    """Alle Knoten für eine Seite (``page`` ist ``None`` bei Django-Seiten wie /ingestor/)."""
    basis = seo.absolute_url("/")
    organisation = basis + "#organisation"
    knoten = [
        {
            "@type": "Organization",
            "@id": organisation,
            "name": seo.BRAND,
            "url": basis,
            "logo": seo.absolute_url(static(LOGO)),
            "sameAs": SAME_AS,
            "description": BESCHREIBUNG,
        },
        {
            "@type": "WebSite",
            "@id": basis + "#website",
            "name": seo.BRAND,
            "url": basis,
            "inLanguage": "de",
            "publisher": {"@id": organisation},
        },
    ]
    if page is None:
        return knoten
    slug = getattr(page, "slug", "")
    if getattr(page, "depth", 0) == 2 or slug in ORGANISATION_SEITEN:
        knoten[0].update({
            "knowsAbout": FACHGEBIETE,
            "areaServed": {"@type": "Country", "name": "Deutschland"},
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "Erstgespräch und Beratung",
                "url": seo.absolute_url("/kontakt/"),
                "availableLanguage": "de",
            },
        })
    if slug in SOFTWARE_SEITEN:
        knoten.append({
            "@type": "SoftwareApplication",
            "@id": basis + "#software",
            "name": seo.BRAND,
            "applicationCategory": "BusinessApplication",
            "operatingSystem": "Web",
            "url": seo.absolute_url(SOFTWARE_URL),
            "license": LIZENZ,
            "description": BESCHREIBUNG,
            "publisher": {"@id": organisation},
            "hasPart": [{"@id": f"{basis}#{produkt['kennung']}"} for produkt in PRODUKTE],
        })
    for produkt in PRODUKTE:
        if slug in UEBERSICHTEN or slug in produkt["seiten"]:
            knoten.append(_produkt(produkt, basis, organisation))
    if slug in QUELLCODE_SEITEN:
        knoten.append({
            "@type": "SoftwareSourceCode",
            "@id": basis + "#quellcode",
            "name": seo.BRAND,
            "codeRepository": REPOSITORY,
            "programmingLanguage": "Python",
            "license": LIZENZ,
            "targetProduct": {"@id": basis + "#software"},
            "publisher": {"@id": organisation},
        })
    fragen = faq(page)
    if fragen:
        knoten.append({"@type": "FAQPage", "mainEntity": fragen})
    pfad = brotkrumen(page)
    if pfad:
        knoten.append({"@type": "BreadcrumbList", "itemListElement": pfad})
    return knoten


def json_ld(page=None, zusatz=None) -> str:
    """
    JSON-LD für ``<script type="application/ld+json">``, sicher für den Einbau in HTML. ``zusatz``: weitere Knoten
    einer Django-Seite (``strukturdaten_zusatz`` im Kontext, etwa der Datenkatalog von /offene-daten/).
    """
    daten = {"@context": "https://schema.org", "@graph": [*graph(page), *(zusatz or [])]}
    return json.dumps(daten, ensure_ascii=False, separators=(",", ":")).translate(_ESCAPES)
