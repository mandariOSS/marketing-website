"""Unternehmensseiten: Inhalte, Stufenschalter, Logo-Paket, Weiterleitung und Seed-Befehle."""

import io
import re
import zipfile
from html.parser import HTMLParser
from io import StringIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.management import call_command
from django.test import TestCase

from company.models import STAGE_COMPANY, CompanySettings
from marketing.models import ContactPage, MarketingPage

DU_FORM = re.compile(r"\b(du|dich|dir|dein|deine|deinen|deinem|deiner|deines|euch|euer|eure|euren|eurem|eurer)\b",
                     re.IGNORECASE)


class _MainText(HTMLParser):
    """Sammelt den sichtbaren Text innerhalb von <main> (ohne Skripte und Styles)."""

    def __init__(self):
        super().__init__()
        self.depth = 0
        self.skip = 0
        self.parts = []

    def handle_starttag(self, tag, attrs):
        if tag == "main":
            self.depth += 1
        elif tag in ("script", "style"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag == "main":
            self.depth -= 1
        elif tag in ("script", "style"):
            self.skip -= 1

    def handle_data(self, data):
        if self.depth and not self.skip:
            self.parts.append(data)


def main_text(response):
    """Sichtbarer Text des Hauptbereichs (ohne Kopf- und Fußzeile)."""
    parser = _MainText()
    parser.feed(response.content.decode("utf-8"))
    return " ".join(" ".join(parser.parts).replace("\u00ad", "").split())  # ohne weiche Trennstriche


class UnternehmensseitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_seiten_liefern_inhalt(self):
        checks = {
            "/unternehmen/": ["Wir bauen die digitale Infrastruktur", "Unser Wertekompass", 'id="werte"',
                              'id="wegmarken"', 'id="angaben"', "Angaben zum Unternehmen", "DE353231778"],
            "/karriere/": ["Bau mit an der Software", "Initiativ bewerben", 'id="stellen"', 'id="ablauf"',
                           "bewerbung@mandari.de"],
            "/presse/": ["Kurzprofil", "Stand 2. Oktober 2026", "204.819", 'id="material"',
                         "/presse/mandari-logopaket.zip"],
            "/partner/": ["Vier Wege, mit uns zu arbeiten", "So entsteht eine Partnerschaft", "/unternehmen/#werte"],
            "/open-source/": ["Öffentliches Geld. Öffentlicher Code.", 'id="danke"', "AGPL-3.0"],
            "/kontakt/": ['id="termin"', 'id="nachricht"', 'id="termin-buchen"', "Erstgespräch vereinbaren",
                          "Nachricht schreiben", "bewerbung@mandari.de", "Aegidiistraße 61/62"],
        }
        for url, needles in checks.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertEqual(response.status_code, 200)
                body = response.content.decode("utf-8")
                for needle in needles:
                    self.assertIn(needle, body)

    def test_angaben_stehen_vor_der_einladung(self):
        body = self.client.get("/unternehmen/").content.decode("utf-8")
        self.assertLess(body.index('id="wegmarken"'), body.index('id="angaben"'))
        self.assertLess(body.index('id="angaben"'), body.index("Lernen wir uns kennen."))

    def test_sie_form_ausser_karriere(self):
        for url in ("/unternehmen/", "/presse/", "/partner/", "/open-source/", "/kontakt/", "/datenschutz/",
                    "/impressum/"):
            with self.subTest(url=url):
                self.assertEqual(DU_FORM.findall(main_text(self.client.get(url))), [])
        self.assertTrue(DU_FORM.findall(main_text(self.client.get("/karriere/"))))

    def test_ueber_uns_leitet_dauerhaft_weiter(self):
        response = self.client.get("/ueber-uns/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/unternehmen/")

    def test_logo_paket(self):
        response = self.client.get("/presse/mandari-logopaket.zip")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/zip")
        names = zipfile.ZipFile(io.BytesIO(response.content)).namelist()
        self.assertIn("mandari-logos/LIESMICH.txt", names)
        self.assertIn("mandari-logos/mandari-wortmarke-dunkel.svg", names)
        self.assertEqual(len(names), 7)


class StufenschalterTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_vorgruendung_ist_standard(self):
        body = self.client.get("/unternehmen/").content.decode("utf-8")
        self.assertIn("topixmedia, Inhaber Sven Konopka", body)
        self.assertIn("mandari wird eigenständig.", body)

    def test_einstellung_im_wagtail_admin(self):
        admin = get_user_model().objects.create_superuser("redaktion", "redaktion@example.org", "x" * 32)
        self.client.force_login(admin)
        page = self.client.get("/cms-admin/settings/company/companysettings/", follow=True)
        url = page.redirect_chain[-1][0] if page.redirect_chain else "/cms-admin/settings/company/companysettings/"
        self.assertContains(page, "Unternehmensangaben")
        self.assertContains(page, "Gesellschaft (gilt ab Stufe „Gesellschaft“)")

        # Stufe „Gesellschaft“ ohne Pflichtangaben wird abgelehnt
        response = self.client.post(url, {"stage": STAGE_COMPANY, "announce_founding": "on",
                                          "company_name": "mandari UG (haftungsbeschränkt)",
                                          "legal_form": "Unternehmergesellschaft (haftungsbeschränkt)"})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(CompanySettings.load().is_company)

    def test_gesellschaft_braucht_pflichtangaben(self):
        settings = CompanySettings.load()
        settings.stage = STAGE_COMPANY
        with self.assertRaises(ValidationError) as raised:
            settings.full_clean()
        self.assertIn("managing_directors", raised.exception.message_dict)
        self.assertIn("register_number", raised.exception.message_dict)

    def test_gesellschaft_ersetzt_rechtstraeger_auf_unternehmen_und_kontakt(self):
        settings = CompanySettings.load()
        settings.stage = STAGE_COMPANY
        settings.managing_directors = "Erika Beispiel"
        settings.street = "Beispielweg 1"
        settings.postal_city = "48143 Münster"
        settings.register_court = "Amtsgericht Münster"
        settings.register_number = "HRB 00000"
        settings.full_clean()
        settings.save()

        unternehmen = self.client.get("/unternehmen/").content.decode("utf-8")
        self.assertIn("mandari UG (haftungsbeschränkt)", unternehmen)
        self.assertIn("Geschäftsführung", unternehmen)
        self.assertIn("Amtsgericht Münster, HRB 00000", unternehmen)
        self.assertNotIn("topixmedia", main_text(self.client.get("/unternehmen/")))
        self.assertNotIn("mandari wird eigenständig.", unternehmen)

        kontakt = self.client.get("/kontakt/").content.decode("utf-8")
        self.assertIn("Beispielweg 1", kontakt)

        # Rechtstexte schalten bewusst nicht automatisch um
        self.assertIn("topixmedia", self.client.get("/impressum/").content.decode("utf-8"))


class SeedBefehleTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_eigenes_template_bleibt_nach_neuem_seed(self):
        call_command("refresh_seeded_page", "unternehmen", "--force", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", "--pages", "presse", "--force", stdout=StringIO())
        self.assertEqual(MarketingPage.objects.get(slug="unternehmen").custom_template, "company/unternehmen.html")
        self.assertEqual(MarketingPage.objects.get(slug="presse").custom_template, "company/presse.html")
        self.assertEqual(MarketingPage.objects.get(slug="partner").custom_template, "")

    def test_kontaktseite_titel_und_beschreibung(self):
        page = ContactPage.objects.get()
        page.seo_title = "Kontakt – Mandari"
        page.search_description = "Kontaktformular und Ansprechpartner."
        page.save()

        call_command("refresh_seeded_page", "kontakt", stdout=StringIO())
        page.refresh_from_db()
        self.assertEqual(page.seo_title, "Kontakt – Mandari")

        call_command("refresh_seeded_page", "kontakt", "--force", stdout=StringIO())
        page.refresh_from_db()
        self.assertEqual(page.seo_title, "Kontakt")
        self.assertTrue(page.search_description.startswith("Erstgespräch mit mandari vereinbaren"))

    def test_bestand_mit_alter_ueber_uns_seite(self):
        """Datenbank im Stand design-v1: /ueber-uns/ existiert noch als Wagtail-Seite."""
        home = MarketingPage.objects.get(slug="preise").get_parent()
        alt = MarketingPage(title="Über uns", slug="ueber-uns")
        home.add_child(instance=alt)
        alt.save_revision().publish()

        call_command("setup_initial_pages", stdout=StringIO())
        self.assertEqual(MarketingPage.objects.filter(slug="unternehmen").count(), 1)
        response = self.client.get("/ueber-uns/")
        self.assertEqual(response.status_code, 301)
        self.assertEqual(response["Location"], "/unternehmen/")
