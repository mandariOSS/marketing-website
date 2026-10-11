"""SEO-Kaufbegriffe (Issue mandariOSS/mandari#939): Sachseiten /sitzungsmanagement/, /buergerinformationssystem/ und
/oparl-schnittstelle/, der Seitentitel der Startseite und die Entflechtung von /kommunen/ (Sitzungsdienst) und
/fraktionen/ (Fraktionssoftware)."""

import json
import re
from io import StringIO

from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase, override_settings

from marketing import seo
from marketing.management.commands.migrate_pages_to_streamfield import get_marketing_definitions
from marketing.management.commands.setup_initial_pages import HOME_PAGE_META, MARKETING_PAGE_META
from marketing.seeds_unternehmen import KENNZAHLEN_STAND
from marketing.tests.test_ris_seo import DU, hauptteil, head, links, sichtbarer_text

STARTSEITE_TITEL = "mandari – Ratsinformationssystem und Software für die offene Verwaltung"

# Slug → Begriff in der Überschrift und Suchbegriffe, die im sichtbaren Text stehen
SEITEN = {
    "sitzungsmanagement": ("Sitzungsmanagement", ("Sitzungsmanagement", "Sitzungsdienst", "Gremienmanagement",
                                                  "digitale Gremienarbeit", "papierlose Sitzung")),
    "buergerinformationssystem": ("Bürgerinformationssystem", ("Bürgerinformationssystem", "Bürgerportal",
                                                              "Volltextsuche", "Barrierefrei", "OParl")),
    "oparl-schnittstelle": ("OParl-Schnittstelle", ("OParl", "maschinenlesbar", "offene Daten", "DCAT-AP.de",
                                                    "bisherigen RIS")),
}
META = {m["slug"]: m for m in MARKETING_PAGE_META}

# Pfade, die in Produktion die mandari-Anwendung bedient (Caddyfile im Repository mandariOSS/mandari). Eine Seite der
# Website darf dort nicht liegen – deshalb /oparl-schnittstelle/ statt /oparl/.
ANWENDUNG = ("/insight/", "/work/", "/session/", "/accounts/", "/admin/", "/api/", "/public/", "/ws/", "/oparl/",
             "/nachweis/", "/kalender/", "/feedback/", "/csp-report/", "/data/", "/static/", "/media/", "/offline/")

# Keine Preise, keine Kostenaussagen, keine KI (mandari#950), keine Ratsfragen (pausiert), regisafe nie als
# OParl-Beispiel, Marke klein
VERBOTEN = ["€", "Euro", "kostenlos", "kostenfrei", "Lizenzkosten", "lizenzkostenfrei", "Finanzier", "querfinanziert",
            "39,90", "Preisliste", "Mandari", "künstliche Intelligenz", "Zusammenfassung", "Ratsfrage", "regisafe"]


def json_ld(html):
    return json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))["@graph"]


class SeedTests(SimpleTestCase):
    def test_titel_und_beschreibungen_im_zielbereich(self):
        for slug in [*SEITEN, "kommunen", "fraktionen"]:
            titel = seo.full_title(META[slug]["seo_title"])
            beschreibung = META[slug]["search_description"]
            self.assertTrue(30 <= len(titel) <= 60, f"{slug}: {len(titel)} Zeichen: {titel}")
            self.assertTrue(120 <= len(beschreibung) <= 155, f"{slug}: Description {len(beschreibung)} Zeichen")
            for text in (titel, beschreibung):
                self.assertNotRegex(text, r"€|\d+,\d\d|kostenlos|kostenfrei", slug)

    def test_kaufbegriffe_in_titeln(self):
        self.assertIn("Sitzungsmanagement", META["sitzungsmanagement"]["seo_title"])
        self.assertIn("Bürgerinformationssystem", META["buergerinformationssystem"]["seo_title"])
        self.assertIn("OParl-Schnittstelle", META["oparl-schnittstelle"]["seo_title"])
        self.assertIn("Fraktionssoftware", META["fraktionen"]["seo_title"])
        self.assertIn("Fraktionssoftware", META["fraktionen"]["search_description"])
        # Entflechtung: Ratsinformationssystem (Einzahl) steht nur noch im Titel der Sachseite dazu; der Vergleich
        # („Ratsinformationssysteme im Vergleich“) zielt auf eine andere Suche
        mit_ris = [slug for slug, m in META.items() if re.search(r"\bRatsinformationssystem\b", m.get("seo_title", ""))]
        self.assertEqual(mit_ris, ["ratsinformationssystem"])

    def test_startseitentitel(self):
        # Nur der Seitentitel ändert sich; Titel im CMS, Unterzeile und Description bleiben
        self.assertEqual(HOME_PAGE_META["seo_title"], STARTSEITE_TITEL)
        self.assertEqual(seo.full_title(HOME_PAGE_META["seo_title"], is_home=True), STARTSEITE_TITEL)
        self.assertEqual(HOME_PAGE_META["title"], "mandari")
        self.assertEqual(HOME_PAGE_META["subtitle"], "Software für die offene Verwaltung")

    def test_ohne_preise_ki_und_fremde_beispiele(self):
        definitionen = get_marketing_definitions()
        for slug in SEITEN:
            text = repr(definitionen[slug])
            for wort in VERBOTEN:
                self.assertNotIn(wort, text, f"{slug}: {wort}")
            self.assertNotRegex(text, r"\bKI\b", slug)
            self.assertEqual(text.count("/preise/"), 1, slug)

    def test_nach_dem_musterkatalog(self):
        definitionen = get_marketing_definitions()
        for slug in SEITEN:
            typen = [typ for typ, _ in definitionen[slug]]
            self.assertEqual(typen[0], "hero", slug)
            self.assertEqual(typen.count("hero"), 1, slug)
            self.assertEqual(typen[-1], "gradient_cta", slug)
            faq = dict(definitionen[slug])["accordion_faq"]
            self.assertTrue(5 <= len(faq["items"]) <= 7, slug)
            hero = dict(definitionen[slug])["hero"]
            self.assertEqual(hero["ctas"][0]["label"], "Erstgespräch vereinbaren", slug)
            self.assertIn(SEITEN[slug][0], hero["title"], slug)

    def test_adressen_nicht_im_bereich_der_anwendung(self):
        for slug in SEITEN:
            self.assertFalse(f"/{slug}/".startswith(ANWENDUNG), slug)

    def test_zahlen_mit_stand(self):
        bloecke = dict(get_marketing_definitions()["buergerinformationssystem"])
        fakten = bloecke["produktbilder"]["eintraege"][0]["fakten"]
        self.assertIn({"begriff": "Stand", "wert": KENNZAHLEN_STAND}, fakten)

    def test_fusszeile_nennt_die_sachseiten_unter_dem_ratsinformationssystem(self):
        html = render_to_string("components/footer.html", {})
        produkte = html[html.find('id="fuss-produkte"'):html.find('id="fuss-vertrauen"')]
        ziele = ["/ratsinformationssystem/", "/sitzungsmanagement/", "/buergerinformationssystem/",
                 "/oparl-schnittstelle/", "/kommunen/"]
        stellen = [produkte.find(f'href="{ziel}"') for ziel in ziele]
        self.assertNotIn(-1, stellen)
        self.assertEqual(stellen, sorted(stellen))
        self.assertEqual(links(produkte, "/sitzungsmanagement/"), ["Sitzungsmanagement"])
        self.assertEqual(links(produkte, "/buergerinformationssystem/"), ["Bürgerinformationssystem"])
        self.assertEqual(links(produkte, "/oparl-schnittstelle/"), ["OParl-Schnittstelle"])


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["testserver"])
class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def test_neue_seiten(self):
        for slug, (begriff, suchbegriffe) in SEITEN.items():
            url = f"/{slug}/"
            html = self.seite(url)
            self.assertEqual(head(html, r"<title>([^<]+)</title>"), f"{META[slug]['seo_title']} | mandari", url)
            self.assertIn(begriff, head(html, r"<h1[^>]*>([^<]+)</h1>"), url)
            self.assertEqual(head(html, r'<meta name="description" content="([^"]+)"'),
                             META[slug]["search_description"], url)
            haupt = hauptteil(html)
            self.assertEqual(len(re.findall(r'<section class="[^"]*\bhero\b', haupt)), 1, url)
            weiter = "/insight/" if slug == "buergerinformationssystem" else "/migration/"
            for ziel in ("/ratsinformationssystem/", weiter):
                self.assertTrue(links(haupt, ziel), f"{url}: {ziel}")
            self.assertEqual(len(links(haupt, "/preise/")), 1, url)
            text = sichtbarer_text(haupt)
            self.assertNotIn("€", text, url)
            self.assertFalse(DU.search(text), f"{url}: {DU.search(text)}")
            for wort in suchbegriffe:
                self.assertIn(wort.lower(), text.lower(), f"{url}: {wort}")

    def test_sachseiten_verlinken_einander(self):
        sachseiten = [f"/{slug}/" for slug in SEITEN]
        for url in sachseiten:
            haupt = hauptteil(self.seite(url))
            for ziel in sachseiten:
                if ziel != url:
                    self.assertTrue(links(haupt, ziel), f"{url} → {ziel}")

    def test_textlinks_aus_produkte_kommunen_und_ratsinformationssystem(self):
        for url in ("/produkte/", "/kommunen/", "/ratsinformationssystem/"):
            haupt = hauptteil(self.seite(url))
            for slug in SEITEN:
                self.assertTrue(links(haupt, f"/{slug}/"), f"{url} → /{slug}/")

    def test_startseite_nur_mit_neuem_titel(self):
        html = self.seite("/")
        self.assertEqual(head(html, r"<title>([^<]+)</title>"), STARTSEITE_TITEL)
        self.assertEqual(head(html, r'<meta property="og:title" content="([^"]+)"'), STARTSEITE_TITEL)
        self.assertIn("Software für die offene Verwaltung", re.search(r"<h1[^>]*>(.*?)</h1>", html, re.S).group(1))
        for slug in SEITEN:
            self.assertEqual(links(hauptteil(html), f"/{slug}/"), [], slug)

    def test_kommunen_und_fraktionen_entflochten(self):
        kommunen = self.seite("/kommunen/")
        self.assertEqual(head(kommunen, r"<title>([^<]+)</title>"), "Sitzungsdienst-Software für Kommunen | mandari")
        self.assertNotIn("kostenlos", sichtbarer_text(hauptteil(kommunen))[:600])
        fraktionen = self.seite("/fraktionen/")
        self.assertEqual(head(fraktionen, r"<title>([^<]+)</title>"), "Fraktionssoftware für die Ratsarbeit | mandari")
        self.assertEqual(head(fraktionen, r"<h1[^>]*>([^<]+)</h1>"), "Politik machen statt PDFs sortieren.")
        self.assertIn("Fraktionssoftware", sichtbarer_text(hauptteil(fraktionen)))
        self.assertNotIn("€", head(fraktionen, r'<meta name="description" content="([^"]+)"'))

    def test_sitemap(self):
        sitemap = self.client.get("/sitemap.xml").content.decode("utf-8")
        for slug in SEITEN:
            self.assertIn(f"<loc>https://mandari.de/{slug}/</loc>", sitemap)

    def test_strukturdaten_wie_auf_der_ris_seite(self):
        for slug in SEITEN:
            typen = [k["@type"] for k in json_ld(self.seite(f"/{slug}/"))]
            self.assertEqual(typen.count("SoftwareApplication"), 1, slug)
            self.assertEqual(typen.count("FAQPage"), 1, slug)
            self.assertNotIn("BreadcrumbList", typen, slug)

    def test_startseite_mit_nur_meta(self):
        from marketing.models import HomePage

        home = HomePage.objects.get()
        home.seo_title = "mandari – Software für die offene Verwaltung"
        home.save()
        home.save_revision().publish()
        ausgabe = StringIO()
        call_command("refresh_seeded_page", "startseite", "--nur-meta", stdout=ausgabe)
        self.assertIn("seo_title", ausgabe.getvalue())
        self.assertNotIn("search_description", ausgabe.getvalue())
        self.assertEqual(HomePage.objects.get().seo_title, STARTSEITE_TITEL)
        self.assertEqual(head(self.seite("/"), r"<title>([^<]+)</title>"), STARTSEITE_TITEL)
