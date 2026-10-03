"""Tests für SEO-Grundlagen, Weiterleitungen, Sitemap und Release-Seiten."""

import re
from datetime import timedelta
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from blog.models import ReleasePage
from marketing import seo
from marketing.models import LegalPage, MarketingPage


def head(response, pattern):
    match = re.search(pattern, response.content.decode("utf-8"))
    return match.group(1) if match else None


class TitelUndBeschreibungTests(SimpleTestCase):
    def test_markenzusatz_wird_vereinheitlicht(self):
        self.assertEqual(seo.full_title("Preise – Mandari"), "Preise | mandari")
        self.assertEqual(seo.full_title("Kontakt | Mandari"), "Kontakt | mandari")
        self.assertEqual(
            seo.full_title("Vergabe & Unterlagen – Dokumente | mandari"),
            "Vergabe & Unterlagen – Dokumente | mandari",
        )
        self.assertEqual(seo.full_title("Über Mandari"), "Über mandari | mandari")

    def test_startseite_ohne_suffix(self):
        self.assertEqual(
            seo.full_title("mandari – Software für die offene Verwaltung", is_home=True),
            "mandari – Software für die offene Verwaltung",
        )
        self.assertEqual(seo.full_title("Software für die offene Verwaltung", is_home=True),
                         "mandari – Software für die offene Verwaltung")

    def test_kuerzen_an_wortgrenze(self):
        text = "Wort " * 60
        gekuerzt = seo.truncate(text)
        self.assertLessEqual(len(gekuerzt), 160)
        self.assertTrue(gekuerzt.endswith("Wort…"))


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["mandari.de", "angreifer.example", "testserver"])
class SeitenkopfTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_canonical_und_og_url_aus_site_url_trotz_gefaelschtem_host(self):
        response = self.client.get("/preise/", HTTP_HOST="angreifer.example")
        self.assertEqual(head(response, r'<link rel="canonical" href="([^"]+)"'), "https://mandari.de/preise/")
        self.assertEqual(head(response, r'<meta property="og:url" content="([^"]+)"'), "https://mandari.de/preise/")
        self.assertTrue(head(response, r'<meta property="og:image" content="([^"]+)"').startswith("https://mandari.de/"))

    def test_titel_ein_suffix_marke_klein(self):
        response = self.client.get("/kontakt/")
        self.assertEqual(head(response, r"<title>([^<]+)</title>"), "Kontakt | mandari")
        response = self.client.get("/trust/")
        title = head(response, r"<title>([^<]+)</title>")
        self.assertTrue(title.endswith(" | mandari"))
        self.assertEqual(title.count("mandari"), 1)
        self.assertIn('<meta property="og:site_name" content="mandari">', response.content.decode())

    def test_meta_description_aus_search_description(self):
        page = MarketingPage.objects.get(slug="roadmap")
        response = self.client.get("/roadmap/")
        self.assertEqual(head(response, r'<meta name="description" content="([^"]+)"'),
                         seo.truncate(seo.normalize_brand(page.search_description)))

    def test_meta_description_rueckfall_aus_dem_inhalt(self):
        page = MarketingPage.objects.get(slug="roadmap")
        page.search_description = ""
        page.save_revision().publish()
        response = self.client.get("/roadmap/")
        beschreibung = head(response, r'<meta name="description" content="([^"]+)"')
        self.assertTrue(beschreibung)
        self.assertNotIn("Kommunalpolitische Transparenz", beschreibung)
        self.assertLessEqual(len(beschreibung), 160)

    def test_rechtstexte_haben_eigene_beschreibung(self):
        for slug in ("impressum", "datenschutz", "agb", "quellen"):
            self.assertTrue(LegalPage.objects.get(slug=slug).search_description, slug)

    def test_leere_beschreibung_bestehender_rechtsseite_wird_ergaenzt(self):
        LegalPage.objects.filter(slug="impressum").update(search_description="")
        call_command("setup_initial_pages", stdout=StringIO())
        self.assertIn("§ 5 DDG", LegalPage.objects.get(slug="impressum").search_description)

    def test_kopf_und_fusszeile_ohne_versionspille_und_ohne_blog(self):
        body = self.client.get("/preise/").content.decode()
        self.assertNotIn("0.9 Beta", body)
        self.assertNotIn('href="/status/"', body)
        self.assertNotIn('href="/blog/', body)
        self.assertIn('aria-controls="produkte-menue"', body)
        self.assertEqual(body.count('role="banner"'), 1)
        self.assertEqual(body.count('role="contentinfo"'), 1)


@override_settings(SITE_URL="https://mandari.de", STATUS_PAGE_URL="https://status.mandari.de/")
class WeiterleitungenTests(TestCase):
    def test_status_leitet_auf_statusseite(self):
        response = self.client.get("/status/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "https://status.mandari.de/")

    def test_blog_und_feed_leiten_auf_releases(self):
        for path in ("/blog/", "/blog/feed/"):
            response = self.client.get(path)
            self.assertEqual(response.status_code, 301, path)
            self.assertEqual(response["Location"], "/releases/", path)


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["mandari.de", "testserver"])
class ReleaseUndSitemapTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())

    def test_neueste_version_zuerst(self):
        body = self.client.get("/releases/").content.decode()
        self.assertLess(body.index("mandari 0.11"), body.index("mandari 0.9 (Beta)"))

    def test_release_seite_mit_nachbarversion(self):
        body = self.client.get("/releases/mandari-0-11/").content.decode()
        self.assertIn("Vorherige Version", body)
        self.assertIn("mandari 0.9 (Beta)", body)
        self.assertNotIn("Neuere Version", body)
        body = self.client.get("/releases/mandari-0-9-beta/").content.decode()
        self.assertIn("Neuere Version", body)
        self.assertIn("v0.9.0-beta", body)

    def test_blog_index_wird_nicht_mehr_angelegt(self):
        from blog.models import BlogIndexPage

        self.assertFalse(BlogIndexPage.objects.exists())

    def test_sitemap_https_und_plausibles_lastmod(self):
        neu = timezone.now() + timedelta(days=3)
        ReleasePage.objects.filter(slug="mandari-0-11").update(last_published_at=neu)
        body = self.client.get("/sitemap.xml").content.decode()
        self.assertNotIn("<loc>http://", body)
        self.assertIn("<loc>https://mandari.de/releases/mandari-0-11/</loc>", body)
        datum = timezone.localdate(neu).isoformat()  # Sitemap schreibt das Datum in TIME_ZONE (Europe/Berlin)
        self.assertIn(f"<loc>https://mandari.de/</loc><lastmod>{datum}</lastmod>", body)
        self.assertIn(f"<loc>https://mandari.de/releases/</loc><lastmod>{datum}</lastmod>", body)


class MetaTextTests(SimpleTestCase):
    def test_kuerzt_ohne_halbe_entitaeten_und_maskiert(self):
        from django.utils.safestring import mark_safe

        from marketing.templatetags.seo import meta_text

        text = mark_safe("Vergabe &amp; Unterlagen " * 12 + '<b>"fett"</b>')
        ergebnis = meta_text(text)
        self.assertNotRegex(ergebnis, r"&[a-z]*…")
        self.assertIn("&amp;", ergebnis)
        self.assertNotIn("<b>", ergebnis)
        self.assertLessEqual(len(ergebnis.replace("&amp;", "&")), 160)
