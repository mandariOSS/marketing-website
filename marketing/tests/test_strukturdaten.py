"""Strukturierte Daten (schema.org, JSON-LD): ein Block je Seite, parsebar, die richtigen Typen, keine Preise."""

import json
import re
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from wagtail.models import Page

from marketing import strukturdaten
from marketing.management.commands.migrate_pages_to_streamfield import get_marketing_definitions

LD = re.compile(r'<script type="application/ld\+json">(.*?)</script>', re.S)
PREIS_SCHLUESSEL = {"offers", "price", "priceCurrency", "priceSpecification", "lowPrice", "highPrice"}


def schluessel(wert):
    """Alle Schlüssel eines verschachtelten JSON-Werts."""
    if isinstance(wert, dict):
        for k, v in wert.items():
            yield k
            yield from schluessel(v)
    elif isinstance(wert, list):
        for v in wert:
            yield from schluessel(v)


class MaskierungTests(SimpleTestCase):
    def test_klartext_trennt_absaetze_und_loest_entitaeten_auf(self):
        self.assertEqual(strukturdaten.klartext("<p>Erster&nbsp;Satz.</p><p>Zweiter &amp; dritter.</p>"),
                         "Erster Satz. Zweiter & dritter.")

    def test_kein_text_kann_das_skript_beenden(self):
        class Seite:
            slug = "x"
            depth = 3
            body = None

        roh = strukturdaten.json_ld(Seite())
        self.assertNotIn("<", roh)
        self.assertNotIn(">", roh)
        daten = json.loads(roh)
        self.assertEqual(daten["@context"], "https://schema.org")


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["testserver"])
class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def graph(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        html = antwort.content.decode("utf-8")
        bloecke = LD.findall(html)
        self.assertEqual(len(bloecke), 1, f"{url}: {len(bloecke)} JSON-LD-Blöcke")
        # Unsichtbar im Kopf der Seite (Entscheidung vom 07.10.2026: auf der Startseite nur das)
        self.assertEqual(LD.findall(html[:html.find("</head>")]), bloecke, f"{url}: JSON-LD nicht im <head>")
        daten = json.loads(bloecke[0])
        self.assertEqual(daten["@context"], "https://schema.org", url)
        return daten["@graph"]

    def knoten(self, url, typ):
        return [k for k in self.graph(url) if k["@type"] == typ]

    def test_jede_seite_ein_parsebarer_block_ohne_preise(self):
        urls = sorted({p.url for p in Page.objects.live().specific() if p.url})
        urls += ["/crawler/", "/sicherheit/disclosure/"]
        self.assertIn("/ratsinformationssystem/", urls)
        for url in urls:
            graph = self.graph(url)
            self.assertFalse(PREIS_SCHLUESSEL & set(schluessel(graph)), url)

    def test_organisation_und_website_ueberall(self):
        for url in ["/", "/kontakt/", "/preise/", "/impressum/", "/crawler/", "/vergleich/mandari-vs-allris/"]:
            typen = [k["@type"] for k in self.graph(url)]
            self.assertEqual(typen.count("Organization"), 1, url)
            self.assertEqual(typen.count("WebSite"), 1, url)
        organisation = self.knoten("/", "Organization")[0]
        self.assertEqual(organisation["name"], "mandari")
        self.assertEqual(organisation["url"], "https://mandari.de/")
        self.assertEqual(organisation["sameAs"], ["https://github.com/mandariOSS"])
        self.assertEqual(organisation["description"], "mandari ist ein Open-Source-Ratsinformationssystem für "
                                                      "Verwaltungen, Fraktionen und Bürger:innen.")
        self.assertTrue(organisation["logo"].startswith("https://mandari.de/"))
        # Rechtsform und Anschrift folgen dem Stufenschalter Vorgründung/Gesellschaft, nicht den Strukturdaten
        for feld in ("legalName", "address", "foundingDate", "vatID", "email", "telephone"):
            self.assertNotIn(feld, organisation)
        website = self.knoten("/", "WebSite")[0]
        self.assertEqual(website["publisher"], {"@id": organisation["@id"]})

    def test_software_nur_auf_den_produktseiten_und_ohne_angebot(self):
        for url in ["/ratsinformationssystem/", "/kommunen/", "/produkte/"]:
            software = self.knoten(url, "SoftwareApplication")
            self.assertEqual(len(software), 1, url)
            s = software[0]
            self.assertEqual(s["name"], "mandari")
            self.assertEqual(s["applicationCategory"], "BusinessApplication")
            self.assertEqual(s["operatingSystem"], "Web")
            self.assertTrue(s["url"].startswith("https://mandari.de/"))
            self.assertIn("AGPL-3.0-or-later", s["license"])
            self.assertNotIn("offers", s)
        for url in ["/", "/preise/", "/vergleich/", "/fraktionen/"]:
            self.assertEqual(self.knoten(url, "SoftwareApplication"), [], url)

    def test_faq_aus_jedem_akkordeon(self):
        definitionen = get_marketing_definitions()
        for slug in ["preise", "ratsinformationssystem"]:
            fragen = [item for typ, wert in definitionen[slug] if typ == "accordion_faq" for item in wert["items"]]
            faq = self.knoten(f"/{slug}/", "FAQPage")
            self.assertEqual(len(faq), 1, slug)
            eintraege = faq[0]["mainEntity"]
            self.assertEqual([e["name"] for e in eintraege], [f["question"] for f in fragen])
            for eintrag in eintraege:
                self.assertEqual(eintrag["@type"], "Question")
                self.assertEqual(eintrag["acceptedAnswer"]["@type"], "Answer")
                self.assertGreater(len(eintrag["acceptedAnswer"]["text"]), 40)
                self.assertNotIn("<", eintrag["acceptedAnswer"]["text"])
        self.assertEqual(self.knoten("/vergabe/", "FAQPage"), [])

    def test_brotkrumen_auf_den_vergleichsseiten(self):
        for slug in ["mandari-vs-allris", "mandari-vs-somacos", "mandari-vs-sternberg", "mandari-vs-regisafe"]:
            pfad = self.knoten(f"/vergleich/{slug}/", "BreadcrumbList")
            self.assertEqual(len(pfad), 1, slug)
            eintraege = pfad[0]["itemListElement"]
            self.assertEqual([e["position"] for e in eintraege], [1, 2, 3])
            self.assertEqual([e["item"] for e in eintraege],
                             ["https://mandari.de/", "https://mandari.de/vergleich/",
                              f"https://mandari.de/vergleich/{slug}/"])
            self.assertEqual(eintraege[0]["name"], "mandari")
            self.assertEqual(eintraege[1]["name"], "RIS-Vergleich")
        for url in ["/", "/vergleich/", "/ratsinformationssystem/"]:
            self.assertEqual(self.knoten(url, "BreadcrumbList"), [], url)
