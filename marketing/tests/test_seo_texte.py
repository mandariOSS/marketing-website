"""SEO-Texte (marketing/seo_texte.py): Längen, Eindeutigkeit, Übernahme in die Seeds und ``refresh_seeded_page
--nur-meta``, das nur Titel und SEO-Felder setzt und den Inhalt einer Seite stehen lässt."""

import re
from html import unescape
from io import StringIO

from django.core.management import CommandError, call_command
from django.test import SimpleTestCase, TestCase

from marketing import seo, seo_texte
from marketing.management.commands.setup_initial_pages import (
    MARKETING_PAGE_META,
    RELEASE_INDEX_LEGACY,
    RELEASE_INDEX_META,
)
from marketing.models import MarketingPage

TITEL = (30, 60)
DESCRIPTION = (120, 155)
# Rechtsgrundlagen und Normen: Eine Description nennt sie nur, wenn die Seite sie selbst nennt.
NORMEN = r"\b(?:DSA|NetzDG|DDG|BFSG|BITV 2\.0|EN 301 549|WCAG|BGG|DSGVO|AGPL-3\.0|OZG)\b"


class LaengenTests(SimpleTestCase):
    def pruefen(self, name, seo_title=None, search_description=None):
        if seo_title is not None:
            voll = seo.full_title(seo_title)
            self.assertTrue(TITEL[0] <= len(voll) <= TITEL[1], f"{name}: Titel {len(voll)} Zeichen: {voll}")
            # Keine Preisangaben im Titel
            self.assertNotRegex(seo_title, r"\d+,\d\d|€|EUR", name)
        if search_description is not None:
            self.assertTrue(
                DESCRIPTION[0] <= len(search_description) <= DESCRIPTION[1],
                f"{name}: Description {len(search_description)} Zeichen",
            )
            self.assertEqual(search_description, seo.normalize_brand(search_description), name)

    def test_titel_und_descriptions_im_zielbereich(self):
        for slug, texte in seo_texte.SEO_TEXTE.items():
            self.pruefen(slug, texte.get("seo_title"), texte.get("search_description"))
        self.pruefen("releases", RELEASE_INDEX_META["seo_title"], RELEASE_INDEX_META["search_description"])

    def test_aufgabenliste_des_nachtrags_ist_abgedeckt(self):
        # Kurze Titel aus den SEO-Prüfungen und Descriptions unter 120 Zeichen (Issue mandariOSS/mandari#914)
        for slug in ("preise", "roadmap", "open-source", "mitmachen", "partner", "presse", "unternehmen"):
            self.assertIn("seo_title", seo_texte.SEO_TEXTE[slug], slug)
        for slug in ("roadmap", "transparenz", "barrierefreiheit", "migration", "mitmachen", "abuse"):
            self.assertIn("search_description", seo_texte.SEO_TEXTE[slug], slug)

    def test_in_den_seed_metadaten_wirksam(self):
        meta = {m["slug"]: m for m in MARKETING_PAGE_META}
        for slug, texte in seo_texte.SEO_TEXTE.items():
            for feld, wert in texte.items():
                self.assertEqual(meta[slug][feld], wert, f"{slug}.{feld}")

    def test_titel_und_descriptions_eindeutig(self):
        titel = [seo.full_title(m.get("seo_title") or m["title"]) for m in MARKETING_PAGE_META]
        beschreibungen = [m["search_description"] for m in MARKETING_PAGE_META]
        self.assertEqual(len(titel), len(set(titel)), "doppelter Titel")
        self.assertEqual(len(beschreibungen), len(set(beschreibungen)), "doppelte Description")

    def test_unbekannte_seite_oder_feld_ist_ein_fehler(self):
        with self.assertRaises(KeyError):
            seo_texte.anwenden([{"slug": "andere"}])
        alt = dict(seo_texte.SEO_TEXTE)
        try:
            seo_texte.SEO_TEXTE["preise"] = {"title": "Preise"}
            with self.assertRaises(KeyError):
                seo_texte.anwenden([{"slug": slug} for slug in alt])
        finally:
            seo_texte.SEO_TEXTE.clear()
            seo_texte.SEO_TEXTE.update(alt)

    def test_startseite_bleibt_unveraendert(self):
        # Entscheidung 07.10.2026: Titel, H1 und Texte der Startseite bleiben
        self.assertNotIn("startseite", seo_texte.SEO_TEXTE)
        self.assertNotIn("kommunen", seo_texte.SEO_TEXTE)
        self.assertFalse(any(slug.startswith(("vergleich", "mandari-vs")) for slug in seo_texte.SEO_TEXTE))


class NurMetaTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, slug):
        return MarketingPage.objects.get(slug=slug)

    def im_cms_bearbeitet(self, slug):
        """Simuliert den Stand im Betrieb: alter Titel, im CMS geänderter Inhalt (veröffentlicht)."""
        page = self.seite(slug)
        page.seo_title = "Preise – Mandari"
        page.search_description = "Alte Beschreibung."
        daten = page.body.raw_data
        daten[0]["value"]["title"] = "Im CMS geänderte Überschrift"
        page.body = daten
        page.save()
        page.save_revision().publish()
        return self.seite(slug)

    def test_setzt_nur_titel_und_seo_felder(self):
        vorher = self.im_cms_bearbeitet("preise")
        inhalt = vorher.body.raw_data
        ausgabe = StringIO()
        call_command("refresh_seeded_page", "preise", "--nur-meta", stdout=ausgabe)
        page = self.seite("preise")
        self.assertEqual(page.seo_title, seo_texte.SEO_TEXTE["preise"]["seo_title"])
        self.assertNotEqual(page.search_description, "Alte Beschreibung.")
        self.assertEqual(list(page.body.raw_data), list(inhalt))
        self.assertIn("Im CMS geänderte Überschrift", str(page.body.raw_data))
        self.assertFalse(page.has_unpublished_changes)
        self.assertIn("Inhalt unverändert", ausgabe.getvalue())
        # Die Seite zeigt den neuen Titel und behält den Inhalt
        html = self.client.get("/preise/").content.decode("utf-8")
        self.assertIn(f"<title>{seo_texte.SEO_TEXTE['preise']['seo_title']} | mandari</title>", html)
        self.assertIn("Im CMS geänderte Überschrift", html)

    def test_probelauf_zeigt_alt_und_neu_und_speichert_nichts(self):
        # Befund aus der Prüfung: --nur-meta setzt auch einen im CMS umbenannten Seitentitel auf den Seed zurück. Der
        # Probelauf zeigt das vorher; jeder Lauf nennt je Feld den alten und den neuen Wert.
        page = self.im_cms_bearbeitet("preise")
        page.title = "Preise und Pakete"
        page.save()
        page.save_revision().publish()
        revisionen = page.revisions.count()
        neuer_titel = seo_texte.SEO_TEXTE["preise"]["seo_title"]
        for schalter in ("--probelauf", "--dry-run"):
            ausgabe = StringIO()
            call_command("refresh_seeded_page", "preise", "--nur-meta", schalter, stdout=ausgabe)
            text = ausgabe.getvalue()
            self.assertIn("Probelauf, nichts gespeichert", text)
            self.assertIn("title: „Preise und Pakete“ → „Preise“", text)
            self.assertIn(f"seo_title: „Preise – Mandari“ → „{neuer_titel}“", text)
        page = self.seite("preise")
        self.assertEqual((page.title, page.seo_title), ("Preise und Pakete", "Preise – Mandari"))
        self.assertEqual(page.revisions.count(), revisionen)
        # Der echte Lauf nennt dieselben Werte und setzt sie
        ausgabe = StringIO()
        call_command("refresh_seeded_page", "preise", "--nur-meta", stdout=ausgabe)
        self.assertIn("title: „Preise und Pakete“ → „Preise“", ausgabe.getvalue())
        self.assertEqual((self.seite("preise").title, self.seite("preise").seo_title), ("Preise", neuer_titel))

    def test_force_ueberschreibt_den_inhalt_deshalb_nur_meta(self):
        # Befund aus der Prüfung: --force setzt die ganze Seite auf den Seed zurück
        self.im_cms_bearbeitet("preise")
        call_command("refresh_seeded_page", "preise", "--force", stdout=StringIO())
        self.assertNotIn("Im CMS geänderte Überschrift", str(self.seite("preise").body.raw_data))

    def test_entwurf_bleibt_unberuehrt(self):
        page = self.seite("roadmap")
        page.seo_title = "Roadmap – Mandari"
        page.save()
        page.save_revision().publish()
        page.seo_title = "Entwurf"
        page.save_revision()  # nur Entwurf, nicht veröffentlicht
        ausgabe = StringIO()
        call_command("refresh_seeded_page", "roadmap", "--nur-meta", stdout=ausgabe)
        page = self.seite("roadmap")
        self.assertTrue(page.has_unpublished_changes)
        self.assertEqual(page.seo_title, "Roadmap – Mandari")
        self.assertEqual(page.get_latest_revision_as_object().seo_title, "Entwurf")
        self.assertIn("übersprungen", ausgabe.getvalue())

    def test_bereits_aktuell(self):
        call_command("refresh_seeded_page", "presse", "--nur-meta", stdout=StringIO())
        ausgabe = StringIO()
        call_command("refresh_seeded_page", "presse", "--nur-meta", stdout=ausgabe)
        self.assertIn("bereits auf dem Stand", ausgabe.getvalue())

    def test_kontakt_und_startseite(self):
        from marketing.models import ContactPage, HomePage

        kontakt = ContactPage.objects.get()
        kontakt.seo_title = "Kontakt – Mandari"
        kontakt.save()
        kontakt.save_revision().publish()
        call_command("refresh_seeded_page", "kontakt", "--nur-meta", stdout=StringIO())
        self.assertEqual(ContactPage.objects.get().seo_title, "Kontakt")
        ausgabe = StringIO()
        call_command("refresh_seeded_page", "startseite", "--nur-meta", stdout=ausgabe)
        self.assertIn("bereits auf dem Stand", ausgabe.getvalue())
        self.assertEqual(HomePage.objects.get().seo_title, "mandari – Software für die offene Verwaltung")

    def test_fehler(self):
        with self.assertRaisesMessage(CommandError, "schließen sich aus"):
            call_command("refresh_seeded_page", "preise", "--nur-meta", "--force", stdout=StringIO())
        with self.assertRaisesMessage(CommandError, "Keine Metadaten"):
            call_command("refresh_seeded_page", "gibt-es-nicht", "--nur-meta", stdout=StringIO())
        with self.assertRaisesMessage(CommandError, "nur zusammen mit --nur-meta"):
            call_command("refresh_seeded_page", "preise", "--probelauf", stdout=StringIO())


class ReleaseUebersichtTests(TestCase):
    def test_alte_seed_texte_werden_beim_start_ersetzt(self):
        from blog.models import ReleaseIndexPage

        call_command("setup_initial_pages", stdout=StringIO())
        index = ReleaseIndexPage.objects.get()
        index.seo_title = "Releases"
        index.search_description = sorted(RELEASE_INDEX_LEGACY["search_description"])[0]
        index.save()
        call_command("setup_initial_pages", stdout=StringIO())
        index = ReleaseIndexPage.objects.get()
        self.assertEqual(index.seo_title, RELEASE_INDEX_META["seo_title"])
        self.assertEqual(index.search_description, RELEASE_INDEX_META["search_description"])

    def test_im_cms_gepflegte_texte_bleiben(self):
        from blog.models import ReleaseIndexPage

        call_command("setup_initial_pages", stdout=StringIO())
        index = ReleaseIndexPage.objects.get()
        index.seo_title = "Eigener Titel aus dem CMS"
        index.save()
        call_command("setup_initial_pages", stdout=StringIO())
        self.assertEqual(ReleaseIndexPage.objects.get().seo_title, "Eigener Titel aus dem CMS")


class SeitenTitelTests(TestCase):
    """Die gerenderten Seiten tragen die neuen Titel und Descriptions."""

    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_gerendert(self):
        for slug, texte in seo_texte.SEO_TEXTE.items():
            html = self.client.get(f"/{slug}/").content.decode("utf-8")
            titel = re.search(r"<title>(.*?)</title>", html).group(1)
            if "seo_title" in texte:
                self.assertEqual(titel.replace("&amp;", "&"), f"{texte['seo_title']} | mandari", slug)
            if "search_description" in texte:
                self.assertIn(f'<meta name="description" content="{texte["search_description"]}">', html, slug)

    def test_rechtsgrundlagen_der_description_stehen_auf_der_seite(self):
        # Befund aus der Prüfung: „Meldestelle nach DSA und NetzDG“ und „nach BFSG“, die Seiten nennen aber nur den DSA
        # bzw. BITV 2.0 und EN 301 549. Rechtliche Angaben im Suchtreffer müssen zur Seite passen.
        geprueft = 0
        for slug, texte in seo_texte.SEO_TEXTE.items():
            normen = set(re.findall(NORMEN, texte.get("search_description", "")))
            if not normen:
                continue
            html = self.client.get(f"/{slug}/").content.decode("utf-8")
            main = re.search(r"<main.*?</main>", html, re.S).group(0)
            text = re.sub(r"\s+", " ", unescape(re.sub(r"<[^>]+>", " ", main)))
            for norm in sorted(normen):
                self.assertRegex(text, rf"\b{re.escape(norm)}\b", f"/{slug}/ nennt {norm} nicht")
                geprueft += 1
        self.assertGreaterEqual(geprueft, 3)
