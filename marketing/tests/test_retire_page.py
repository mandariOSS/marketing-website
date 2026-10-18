"""Tests für `retire_page`: Seiten idempotent zurückziehen und dauerhaft weiterleiten."""

from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Page

from marketing.models import MarketingPage


def run(*args):
    out = StringIO()
    call_command("retire_page", *args, stdout=out)
    return out.getvalue()


@override_settings(SITE_URL="https://mandari.de", ALLOWED_HOSTS=["mandari.de", "testserver"])
class RetirePageTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        cls.home = Page.objects.get(depth=2).specific
        cls.alt = MarketingPage(title="Altes Angebot", slug="altes-angebot")
        cls.home.add_child(instance=cls.alt)
        cls.alt.save_revision().publish()
        cls.unterseite = MarketingPage(title="Unterseite", slug="unterseite")
        cls.alt.add_child(instance=cls.unterseite)
        cls.unterseite.save_revision().publish()

    def test_zieht_seite_und_unterseiten_zurueck_und_leitet_weiter(self):
        output = run("/altes-angebot/", "--redirect", "/preise/")

        self.alt.refresh_from_db()
        self.unterseite.refresh_from_db()
        self.assertFalse(self.alt.live)
        self.assertFalse(self.unterseite.live)

        redirect = Redirect.objects.get(old_path="/altes-angebot")
        self.assertTrue(redirect.is_permanent)
        self.assertEqual(redirect.redirect_page.specific.slug, "preise")

        response = self.client.get("/altes-angebot/", HTTP_HOST="mandari.de")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/preise/")
        self.assertIn("geprüft: /altes-angebot/ → 301", output)

    def test_zweiter_lauf_aendert_nichts(self):
        run("altes-angebot", "--redirect", "/preise/")
        output = run("altes-angebot", "--redirect", "/preise/")

        self.assertIn("bereits zurückgezogen – unverändert", output)
        self.assertIn("vorhanden – unverändert", output)
        self.assertEqual(Redirect.objects.filter(old_path="/altes-angebot").count(), 1)

    def test_neues_ziel_korrigiert_vorhandene_weiterleitung(self):
        run("/altes-angebot/", "--redirect", "/preise/")
        output = run("/altes-angebot/", "--redirect", "/kontakt/")

        redirect = Redirect.objects.get(old_path="/altes-angebot")
        self.assertEqual(redirect.redirect_page.specific.slug, "kontakt")
        self.assertIn("wird auf /kontakt/ gesetzt", output)

    def test_externes_ziel_und_ziel_mit_anker(self):
        run("/altes-angebot/", "--redirect", "https://status.mandari.de/")
        self.assertEqual(Redirect.objects.get(old_path="/altes-angebot").redirect_link, "https://status.mandari.de/")

        run("/altes-angebot/", "--redirect", "/kontakt/#termin")
        redirect = Redirect.objects.get(old_path="/altes-angebot")
        self.assertIsNone(redirect.redirect_page)
        self.assertEqual(redirect.redirect_link, "/kontakt/#termin")

    def test_django_route_als_ziel(self):
        run("/altes-angebot/", "--redirect", "/sicherheit/disclosure/")
        self.assertEqual(Redirect.objects.get(old_path="/altes-angebot").redirect_link, "/sicherheit/disclosure/")

    def test_fehlendes_ziel_bricht_ohne_aenderung_ab(self):
        with self.assertRaisesMessage(CommandError, "existiert nicht"):
            run("/altes-angebot/", "--redirect", "/gibt-es-nicht/")
        self.alt.refresh_from_db()
        self.assertTrue(self.alt.live)
        self.assertFalse(Redirect.objects.filter(old_path="/altes-angebot").exists())

    def test_ziel_unterhalb_der_seite_wird_abgelehnt(self):
        with self.assertRaisesMessage(CommandError, "unterhalb"):
            run("/altes-angebot/", "--redirect", "/altes-angebot/unterseite/")

    def test_probelauf_schreibt_nichts(self):
        output = run("/altes-angebot/", "--redirect", "/preise/", "--dry-run")
        self.alt.refresh_from_db()
        self.assertTrue(self.alt.live)
        self.assertFalse(Redirect.objects.exists())
        self.assertIn("[Probelauf]", output)

    def test_fehlende_seite_legt_nur_die_weiterleitung_an(self):
        output = run("/gab-es-mal/", "--redirect", "/releases/")
        self.assertIn("existiert nicht – nur die Weiterleitung", output)
        response = self.client.get("/gab-es-mal/", HTTP_HOST="mandari.de")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/releases/")

    def test_startseite_ist_geschuetzt(self):
        with self.assertRaises(CommandError):
            run("/", "--redirect", "/preise/")

    def test_mehrdeutiger_slug(self):
        andere = MarketingPage(title="Unterseite 2", slug="unterseite")
        MarketingPage.objects.get(slug="vergleich").add_child(instance=andere)
        with self.assertRaisesMessage(CommandError, "mehrdeutig"):
            run("unterseite", "--redirect", "/preise/")

    def test_blog_weiterleitung_aus_dem_code_besteht_die_pruefung(self):
        # /blog/ leitet bereits in website/urls.py weiter; der Befehl legt zusätzlich die
        # Wagtail-Weiterleitung an und prüft das Ergebnis.
        output = run("/blog/", "--redirect", "/releases/")
        self.assertIn("geprüft: /blog/ → 301 /releases/", output)
        self.assertTrue(Redirect.objects.filter(old_path="/blog").exists())
