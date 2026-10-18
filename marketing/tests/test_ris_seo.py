"""SEO-Welle (mandariOSS/mandari#914): Titel und Beschreibungen, Sachseite /ratsinformationssystem/, interne Links,
robots.txt und die Marke klein in allen SEO-Feldern."""

import re
from html import unescape
from io import StringIO

from django.core.management import call_command
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from wagtail.models import Page

from marketing.blocks import HeroBlock, langes_wort
from marketing.management.commands import setup_initial_pages as seeds
from marketing.management.commands.migrate_pages_to_streamfield import get_marketing_definitions

TITEL = {
    "/ratsinformationssystem/": "Ratsinformationssystem für Kommunen | mandari",
    "/kommunen/": "Sitzungsdienst & Ratsinformationssystem für Kommunen | mandari",
    "/vergleich/": "Ratsinformationssysteme im Vergleich | mandari",
    "/vergleich/mandari-vs-allris/": "ALLRIS-Alternative? mandari vs. ALLRIS im Vergleich | mandari",
    "/vergleich/mandari-vs-somacos/": "SessionNet-Alternative? mandari vs. Somacos Session | mandari",
    "/vergleich/mandari-vs-sternberg/": "SD.NET-Alternative? mandari vs. Sternberg im Vergleich | mandari",
    "/vergleich/mandari-vs-regisafe/": "regisafe-Alternative? mandari vs. regisafe im Vergleich | mandari",
}
DU = re.compile(r"\b(du|dich|dir|dein\w*|euch|euer|eure\w*)\b", re.IGNORECASE)


def head(html, muster):
    treffer = re.search(muster, html)
    return unescape(treffer.group(1)) if treffer else None


def hauptteil(html):
    return html[html.find('role="main"'):html.find('role="contentinfo"')]


def sichtbarer_text(html):
    html = re.sub(r"<(script|style)\b.*?</\1>", " ", html, flags=re.S)
    return " ".join(unescape(re.sub(r"<[^>]+>", " ", html)).replace("\u00ad", "").split())


def links(html, href):
    """Linktexte zu ``href`` ohne Tags und weiche Trennstellen."""
    return [" ".join(unescape(re.sub(r"<[^>]+>", "", t)).replace("\u00ad", "").split())
            for t in re.findall(rf'<a\b[^>]*href="{re.escape(href)}"[^>]*>(.*?)</a>', html, re.S)]


class SeedTests(SimpleTestCase):
    def test_marke_in_allen_seo_feldern_klein(self):
        felder = [seeds.HOME_PAGE_META, seeds.CONTACT_PAGE_META, seeds.RELEASE_INDEX_META,
                  seeds.SEO_DESCRIPTION_DEFAULTS, *seeds.MARKETING_PAGE_META]
        for eintrag in felder:
            for name, wert in eintrag.items():
                self.assertNotIn("Mandari", str(wert), f"{name}: {wert}")
        # Seiten, deren SEO-Felder direkt im Befehl stehen (Rechtstexte, Blog)
        quelle = open(seeds.__file__, encoding="utf-8").read()
        quelle = quelle[:quelle.find("RELEASE_INDEX_LEGACY")] + quelle[quelle.find("class Command"):]
        for zeile in quelle.splitlines():
            if re.search(r"seo_title|search_description|site_name", zeile):
                self.assertNotIn("Mandari", zeile)

    def test_marke_im_ruhenden_blog_feed_klein(self):
        # /blog/feed/ leitet heute auf /releases/ weiter; reaktiviert soll der Feed die Marke klein schreiben
        from blog.feeds import BlogFeed

        for wert in (BlogFeed.title, BlogFeed.description):
            self.assertNotIn("Mandari", wert)

    def test_titel_und_beschreibungen_der_kernseiten(self):
        meta = {m["slug"]: m for m in seeds.MARKETING_PAGE_META}
        kommunen = meta["kommunen"]["search_description"]
        self.assertNotIn("Verwaltungs-RIS", kommunen)
        for wort in ("Ratsinformationssystem", "Sitzungsdienst"):
            self.assertIn(wort, kommunen)
        ris = meta["ratsinformationssystem"]["search_description"]
        for wort in ("Ratsinformationssystem", "Sitzungsdienst", "OParl"):
            self.assertIn(wort, ris)
        for slug in ("kommunen", "ratsinformationssystem"):
            self.assertLessEqual(len(meta[slug]["search_description"]), 155, slug)
        for titel in TITEL.values():
            self.assertLessEqual(len(titel), 65, titel)

    def test_neue_seite_ohne_preise_und_ohne_kostenaussagen(self):
        text = repr(get_marketing_definitions()["ratsinformationssystem"])
        for verboten in ["€", "Euro", "kostenlos", "kostenfrei", "Lizenzkosten", "lizenzkostenfrei", "Finanzier",
                         "querfinanziert", "39,90", "Preisliste", "Mandari"]:
            self.assertNotIn(verboten, text, verboten)
        self.assertEqual(text.count("/preise/"), 1)

    def test_neue_seite_nach_dem_musterkatalog(self):
        typen = [typ for typ, _ in get_marketing_definitions()["ratsinformationssystem"]]
        self.assertEqual(typen[0], "hero")
        self.assertEqual(typen[-1], "gradient_cta")
        self.assertIn("accordion_faq", typen)
        faq = dict(get_marketing_definitions()["ratsinformationssystem"])["accordion_faq"]
        self.assertTrue(5 <= len(faq["items"]) <= 7)


class KopfUndFussTests(SimpleTestCase):
    def kopfzeile(self, pfad):
        return render_to_string("components/navbar.html", {"request": RequestFactory().get(pfad)})

    def test_produkte_menue_nennt_die_neue_seite_nach_der_uebersicht(self):
        html = self.kopfzeile("/preise/")
        self.assertEqual(links(html, "/ratsinformationssystem/"), ["Ratsinformationssystem", "Ratsinformationssystem"])
        reihenfolge = re.findall(r'href="(/produkte/|/ratsinformationssystem/|/kommunen/)"', html)
        self.assertEqual(reihenfolge, ["/produkte/", "/ratsinformationssystem/", "/kommunen/"] * 2)

    def test_aufklappknopf_markiert_die_neue_seite(self):
        html = self.kopfzeile("/ratsinformationssystem/")
        knopf = re.search(r'<button[^>]*aria-controls="produkte-menue"[^>]*>', html)
        self.assertIn('data-aktiv="true"', knopf.group(0))

    def test_fusszeile_spalte_produkte(self):
        html = render_to_string("components/footer.html", {})
        produkte = html[html.find('id="fuss-produkte"'):html.find('id="fuss-vertrauen"')]
        self.assertEqual(links(produkte, "/ratsinformationssystem/"), ["Ratsinformationssystem"])
        # In der schmalen Spalte trennt das Wort an der Wortfuge, nicht mitten in einer Silbe
        self.assertIn(">Rats&shy;informations&shy;system</a>", produkte)
        self.assertLess(produkte.find('"/produkte/"'), produkte.find('"/ratsinformationssystem/"'))
        self.assertLess(produkte.find('"/ratsinformationssystem/"'), produkte.find('"/kommunen/"'))


class HeroTests(SimpleTestCase):
    def test_langes_wort(self):
        self.assertTrue(langes_wort("Ratsinformationssystem und Sitzungsdienst ohne Medienbrüche."))
        self.assertFalse(langes_wort("Politik machen statt PDFs sortieren."))
        self.assertFalse(langes_wort("Eine Plattform, die mit Ihrer Verwaltung wächst."))

    def test_kontext_kennt_langes_wort(self):
        block = HeroBlock()
        kontext = block.get_context(block.to_python({"title": "Ratsinformationssystem für alle"}))
        self.assertTrue(kontext["langes_wort"])


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

    def test_titel(self):
        for url, titel in TITEL.items():
            self.assertEqual(head(self.seite(url), r"<title>([^<]+)</title>"), titel, url)

    def test_seo_felder_in_der_datenbank_ohne_grosse_marke(self):
        for page in Page.objects.all().specific():
            self.assertNotIn("Mandari", page.seo_title, page.url_path)
            self.assertNotIn("Mandari", page.search_description, page.url_path)

    def test_kommunen_ueberschrift_und_textlink(self):
        html = self.seite("/kommunen/")
        self.assertEqual(head(html, r"<h1[^>]*>([^<]+)</h1>"),
                         "Ratsinformationssystem und Sitzungsdienst ohne Medienbrüche.")
        self.assertIn("Ratsinformationssystem", links(hauptteil(html), "/ratsinformationssystem/"))
        text = sichtbarer_text(hauptteil(html))
        for begriff in ("Sitzungsmanagement", "Gremieninformationssystem", "digitale Gremienarbeit"):
            self.assertIn(begriff, text)
        # Inhalte bleiben: alle Abschnitte von vorher
        for abschnitt in ("Drei Bausteine, ein Ziel", "Betrieb, den Ihre IT und Ihr Datenschutz mittragen",
                          "Zwei Wege zur Anbindung", "Pilotkommunen gestalten mit."):
            self.assertIn(abschnitt, text)

    def test_kommunen_hero_gibt_dem_langen_wort_platz(self):
        kopf = hauptteil(self.seite("/kommunen/"))
        kopf = kopf[:kopf.find("</section>")]
        self.assertIn('class="lg:col-span-7"', kopf)
        self.assertIn('<figure class="lg:col-span-5">', kopf)
        self.assertNotIn("max-w-[15ch]", kopf)
        fraktionen = hauptteil(self.seite("/fraktionen/"))
        fraktionen = fraktionen[:fraktionen.find("</section>")]
        self.assertIn("lg:max-w-[15ch]", fraktionen)
        self.assertIn('<figure class="lg:col-span-6">', fraktionen)

    def test_vergleich_verlinkt_die_neue_seite(self):
        self.assertIn("Ratsinformationssystem", links(hauptteil(self.seite("/vergleich/")), "/ratsinformationssystem/"))

    def test_startseite_verlinkt_die_neue_seite_nicht_im_text(self):
        html = self.seite("/")
        self.assertEqual(links(hauptteil(html), "/ratsinformationssystem/"), [])
        self.assertEqual(head(html, r"<title>([^<]+)</title>"), "mandari – Software für die offene Verwaltung")

    def test_neue_seite(self):
        html = self.seite("/ratsinformationssystem/")
        self.assertIn("Ratsinformationssystem", head(html, r"<h1[^>]*>([^<]+)</h1>"))
        self.assertEqual(len(re.findall(r'<section class="[^"]*\bhero\b', hauptteil(html))), 1)
        beschreibung = head(html, r'<meta name="description" content="([^"]+)"')
        for wort in ("Ratsinformationssystem", "Sitzungsdienst", "OParl"):
            self.assertIn(wort, beschreibung)
        haupt = hauptteil(html)
        for ziel in ["/kommunen/", "/fraktionen/", "/insight/", "/vergabe/", "/migration/", "/vergleich/",
                     "https://docs.mandari.de/insight/oparl-api/"]:
            self.assertTrue(links(haupt, ziel), ziel)
        self.assertEqual(len(links(haupt, "/preise/")), 1)
        text = sichtbarer_text(haupt)
        self.assertNotIn("€", text)
        self.assertFalse(DU.search(text), DU.search(text))
        for frage in ("Was ist ein Ratsinformationssystem?", "Was ist OParl?"):
            self.assertIn(frage, text)

    def test_robots_und_security_txt(self):
        robots = self.client.get("/robots.txt").content.decode()
        self.assertNotIn("Crawl-delay", robots)
        self.assertNotIn("Mandari", robots)
        self.assertIn("# mandari robots.txt", robots)
        self.assertIn("Sitemap: https://mandari.de/sitemap.xml", robots)
        self.assertIn("Disallow: /cms-admin/", robots)
        security = self.client.get("/.well-known/security.txt").content.decode()
        self.assertNotIn("Mandari", security)
        self.assertIn("Contact: mailto:security@mandari.de", security)
