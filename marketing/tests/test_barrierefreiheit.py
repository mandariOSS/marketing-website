"""Barrierefreiheit aus den SEO-Prüfungen (Issue mandariOSS/mandari#914, Nachtrag): kein Link in einem Label,
Inline-SVGs ohne Namen ausgeblendet, Hinweis bei Links in neuem Tab, aria-current in der Navigation und
unterscheidbare Aufrufe mit gleichem Text."""

import re
from collections import defaultdict
from html.parser import HTMLParser
from io import StringIO
from types import SimpleNamespace

from django.core.management import call_command
from django.template import Context, Template
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase, override_settings
from wagtail.models import Page

from marketing.templatetags.zugang import aufruf_name, neuer_tab_hinweis

LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


class Links(HTMLParser):
    """Links (Ziel, Name, target, Klassen) sowie interaktive Elemente in Labels und SVGs ohne Namen."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.in_label = 0
        self.interaktiv_im_label = []
        self.svg_ohne_namen = []
        self._link = None
        self._versteckt = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "label":
            self.in_label += 1
        elif self.in_label and tag in ("a", "button", "select", "textarea"):
            self.interaktiv_im_label.append(self.get_starttag_text())
        if tag == "svg" and a.get("aria-hidden") != "true" and not (a.get("aria-label") or a.get("role") == "img"):
            self.svg_ohne_namen.append(self.get_starttag_text())
        if tag == "a" and "href" in a:
            self._link = {
                "href": a["href"],
                "label": a.get("aria-label"),
                "target": a.get("target"),
                "klasse": a.get("class") or "",
                "text": [],
            }

    def handle_endtag(self, tag):
        if tag == "label":
            self.in_label -= 1
        if tag == "a" and self._link is not None:
            self._link["text"] = " ".join("".join(self._link["text"]).split())
            self.links.append(self._link)
            self._link = None

    def handle_data(self, data):
        if self._link is not None:
            self._link["text"].append(data)


def lesen(html):
    parser = Links()
    parser.feed(html)
    return parser


@override_settings(EMAIL_BACKEND=LOCMEM, SITE_URL="https://mandari.de")
class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def html(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def alle_seiten(self):
        urls = {p.url for p in Page.objects.live().specific() if p.url}
        return sorted(urls | {"/sicherheit/disclosure/", "/crawler/"})

    def test_kontakt_link_nicht_im_label_und_kaestchen_beschrieben(self):
        html = self.html("/kontakt/")
        seite = lesen(html)
        self.assertEqual([t for t in seite.interaktiv_im_label if "<a " in t], [])
        for kennung in ("t-datenschutz", "n-datenschutz"):
            kaestchen = re.search(rf'<input id="{kennung}"[^>]*>', html, re.S).group(0)
            self.assertIn(f'aria-describedby="{kennung}-hinweis"', kaestchen)
            self.assertRegex(html, rf'<label for="{kennung}">Ich habe die Datenschutzerklärung gelesen[^<]*</label>')
            hinweis = re.search(rf'<p id="{kennung}-hinweis"[^>]*>(.*?)</p>', html, re.S).group(1)
            self.assertIn('href="/datenschutz/#formular"', hinweis)

    def test_svgs_ohne_namen_sind_ausgeblendet(self):
        for url in self.alle_seiten():
            self.assertEqual(lesen(self.html(url)).svg_ohne_namen, [], url)

    def test_links_in_neuem_tab_mit_hinweis(self):
        gefunden = 0
        for url in self.alle_seiten():
            for link in lesen(self.html(url)).links:
                if link["target"] == "_blank":
                    gefunden += 1
                    self.assertIn("(öffnet in neuem Tab)", link["text"], f"{url}: {link['href']}")
        self.assertGreater(gefunden, 0)  # Rechtstexte und Quellen öffnen externe Seiten in neuem Tab

    def test_gleicher_aufruftext_fuehrt_nicht_zu_verschiedenen_zielen(self):
        # Gefüllte Aufrufe (btn-primary) mit gleichem zugänglichem Namen müssen dasselbe Ziel haben
        for url in self.alle_seiten():
            ziele = defaultdict(set)
            for link in lesen(self.html(url)).links:
                if "btn-primary" in link["klasse"]:
                    ziele[link["label"] or link["text"]].add(link["href"])
            mehrdeutig = {name: z for name, z in ziele.items() if len(z) > 1}
            self.assertEqual(mehrdeutig, {}, url)

    def test_kommunen_aufrufe_mit_anlass(self):
        links = [link for link in lesen(self.html("/kommunen/")).links if link["text"] == "Erstgespräch vereinbaren"]
        self.assertEqual(
            {(link["href"], link["label"]) for link in links},
            {
                ("/kontakt/?subject=Kommune-anbinden#termin", "Erstgespräch vereinbaren: Kommune anbinden"),
                ("/kontakt/?subject=Pilot-Kommune#termin", "Erstgespräch vereinbaren: Pilotkommune werden"),
            },
        )

    def test_fusszeile_markiert_aktuelle_seite(self):
        for url in ("/roadmap/", "/partner/", "/impressum/"):
            html = self.html(url)
            fuss = html[html.find('role="contentinfo"') :]
            self.assertEqual(re.findall(r'<a href="([^"]+)" aria-current="page"', fuss), [url], url)
        # Unterseiten sind nicht die Seite selbst
        fuss = self.html("/vergleich/mandari-vs-allris/")
        self.assertNotIn('aria-current="page"', fuss[fuss.find('role="contentinfo"') :])

    def test_kopfzeile_markiert_aktuelle_seite_desktop_und_mobil(self):
        html = self.html("/preise/")
        kopf = html[html.find('role="banner"') : html.find('role="main"')]
        self.assertEqual(re.findall(r'<a href="([^"]+)" aria-current="page"', kopf), ["/preise/", "/preise/"])

    def test_anmelden_direkt_zur_anmeldeseite(self):
        html = self.html("/")
        anmelden = re.findall(r'<a href="([^"]+)" rel="nofollow"[^>]*>\s*Anmelden\s*</a>', html)
        self.assertEqual(anmelden, ["/accounts/login/?next=/work/"] * 2)
        self.assertNotIn('href="/work/"', html)


class EinwilligungTests(SimpleTestCase):
    def test_fehler_bleibt_beschrieben(self):
        fehler = ["Bitte bestätigen Sie die Datenschutzerklärung."]
        feld = SimpleNamespace(html_name="datenschutz", value=None, errors=fehler)
        html = render_to_string("marketing/_kontakt_einwilligung.html", {"field": feld, "id": "t-datenschutz"})
        kaestchen = re.search(r'<input id="t-datenschutz"[^>]*>', html, re.S).group(0)
        self.assertIn('aria-describedby="t-datenschutz-hinweis t-datenschutz-fehler"', kaestchen)
        self.assertIn('aria-invalid="true"', kaestchen)
        self.assertIn('<p id="t-datenschutz-fehler"', html)


class FilterTests(SimpleTestCase):
    def test_neuer_tab_hinweis_einmal(self):
        html = '<a href="https://oparl.org/" target="_blank" rel="noopener">OParl</a> und <a href="/x/">X</a>'
        neu = neuer_tab_hinweis(html)
        self.assertEqual(
            neu,
            '<a href="https://oparl.org/" target="_blank" rel="noopener">OParl'
            '<span class="sr-only"> (öffnet in neuem Tab)</span></a> und <a href="/x/">X</a>',
        )
        self.assertEqual(neuer_tab_hinweis(neu), neu)

    def test_neuer_tab_maskiert_unsicheren_text(self):
        html = Template("{% load zugang %}{{ wert|neuer_tab }}").render(Context({"wert": "<script>x</script>"}))
        self.assertEqual(html, "&lt;script&gt;x&lt;/script&gt;")

    def test_aufruf_name(self):
        self.assertEqual(
            aufruf_name("Erstgespräch vereinbaren", "/kontakt/?subject=Pilot-Kommune#termin"),
            ' aria-label="Erstgespräch vereinbaren: Pilotkommune werden"',
        )
        # Nennt der Text den Anlass schon oder ist keiner eingetragen, bleibt es beim Text
        self.assertEqual(aufruf_name("Pilot-Kommune werden", "/kontakt/?subject=Pilot-Kommune"), "")
        self.assertEqual(aufruf_name("Demo anfragen", "/kontakt/?subject=Demo"), "")
        self.assertEqual(aufruf_name("Preise", "/preise/"), "")
