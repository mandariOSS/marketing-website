"""Tests für die Kopfzeile: Produkte-Menü, Slide-Menü und die Markierung des aktuellen Bereichs."""

import re

from django.conf import settings
from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase

from marketing.templatetags.navigation import current_page, current_section


def kopfzeile(pfad):
    return render_to_string("components/navbar.html", {"request": RequestFactory().get(pfad)})


def linktexte(html, href):
    return [" ".join(text.split()) for text in re.findall(rf'<a href="{re.escape(href)}"[^>]*>(.*?)</a>', html, re.S)]


class AktuellerBereichTests(SimpleTestCase):
    def test_seite_und_unterseiten(self):
        anfrage = RequestFactory().get("/vergleich/mandari-vs-allris/")
        self.assertEqual(current_page(anfrage, "/vergleich/"), ' aria-current="page"')
        self.assertEqual(current_page(anfrage, "/preise/"), "")
        self.assertEqual(current_page(anfrage, "/produkte/#insight"), "")

    def test_bereich_fuer_den_aufklappknopf(self):
        anfrage = RequestFactory().get("/fraktionen/")
        self.assertEqual(current_section(anfrage, "/produkte/", "/fraktionen/"), ' data-aktiv="true"')
        self.assertEqual(current_section(anfrage, "/preise/", "/kontakt/"), "")
        self.assertEqual(current_section(None, "/produkte/"), "")


class KopfzeileTests(SimpleTestCase):
    def test_buergerportal_genau_einmal_als_direkter_link(self):
        html = kopfzeile("/preise/")
        self.assertEqual(linktexte(html, "/insight/"), ["Bürgerportal"])
        self.assertEqual(html.count("Bürgerportal"), 1)

    def test_produkte_menue_nennt_buerger_innen(self):
        html = kopfzeile("/preise/")
        # Desktop-Menü und Slide-Menü
        self.assertEqual(linktexte(html, "/produkte/#insight"), ["Für Bürger:innen", "Für Bürger:innen"])
        self.assertEqual(linktexte(html, "/work/"), ["Anmelden", "Anmelden"])

    def test_produkte_knopf_zeigt_aktuellen_bereich(self):
        knopf = re.compile(r'<button[^>]*aria-controls="produkte-menue"[^>]*>', re.S)
        self.assertIn('data-aktiv="true"', knopf.search(kopfzeile("/kommunen/")).group(0))
        self.assertIn('data-aktiv="true"', knopf.search(kopfzeile("/roadmap/")).group(0))
        self.assertNotIn("data-aktiv", knopf.search(kopfzeile("/preise/")).group(0))

    def test_slide_menue_ist_beschrifteter_modaler_dialog(self):
        html = kopfzeile("/")
        knopf = re.search(r'<button[^>]*aria-controls="mobilmenue"[^>]*>', html, re.S).group(0)
        self.assertIn('aria-expanded="false"', knopf)
        dialog = re.search(r'<div id="mobilmenue"[^>]*>', html, re.S).group(0)
        self.assertIn('role="dialog"', dialog)
        self.assertIn('aria-modal="true"', dialog)
        self.assertIn('aria-label="Menü"', dialog)


class AbstandZurKopfzeileTests(SimpleTestCase):
    def test_scroll_margin_im_inhalt_statt_scroll_padding_am_html(self):
        # Mit scroll-padding am html hält Chrome die haftende Kopfzeile für verdeckt und scrollt bei jedem
        # Fokus darin (Tab, Pfeiltasten im Produkte-Menü) die Seite nach oben.
        quelle = (settings.BASE_DIR / "templates" / "base.html").read_text(encoding="utf-8")
        html_tag = re.search(r"<html[^>]*>", quelle, re.S).group(0)
        self.assertNotIn("scroll-p", html_tag)
        self.assertIn("main, main *, footer * { scroll-margin-top: 5rem; }", quelle)
