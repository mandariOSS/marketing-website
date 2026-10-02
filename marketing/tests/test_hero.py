"""Hero-Überschrift und Zahl der Aufrufe in Hero und Einladung."""

from django.test import SimpleTestCase

from marketing.blocks import GradientCTABlock, HeroBlock, hero_title


class HeroTitleTests(SimpleTestCase):
    def test_haengt_ergaenzung_mit_leerzeichen_an(self):
        self.assertEqual(hero_title("mandari", "Roadmap"), "mandari Roadmap")

    def test_ohne_ergaenzung_bleibt_titel(self):
        self.assertEqual(hero_title("Kontakt", ""), "Kontakt")
        self.assertEqual(hero_title("Kontakt", None), "Kontakt")

    def test_bindestrich_mit_kleinbuchstabe_wird_ein_wort(self):
        self.assertEqual(hero_title("Quellen-", "nachweise"), "Quellennachweise")

    def test_bindestrich_mit_grossbuchstabe_bleibt(self):
        self.assertEqual(hero_title("Presse-", "Material"), "Presse-Material")

    def test_nur_ergaenzung(self):
        self.assertEqual(hero_title("", "Roadmap"), "Roadmap")


class AufrufeTests(SimpleTestCase):
    ctas = [
        {"label": "Erstgespräch vereinbaren", "url": "/kontakt/#termin", "icon": "", "style": "primary"},
        {"label": "Bürgerportal ansehen", "url": "/insight/", "icon": "", "style": "outline"},
        {"label": "Dritter Weg", "url": "/dritter/", "icon": "", "style": "outline"},
    ]

    def test_hero_rendert_ueberschrift_und_hoechstens_einen_textlink(self):
        block = HeroBlock()
        html = block.render(block.to_python({"title": "Quellen-", "title_highlight": "nachweise", "ctas": self.ctas}))
        self.assertIn(">Quellennachweise</h1>", html)
        self.assertEqual(html.count('class="btn-primary"'), 1)
        self.assertEqual(html.count('class="textlink"'), 1)
        self.assertNotIn("Dritter Weg", html)

    def test_einladung_rendert_hoechstens_einen_textlink(self):
        block = GradientCTABlock()
        html = block.render(block.to_python({"title": "Fragen?", "ctas": self.ctas}))
        self.assertEqual(html.count('class="btn-primary"'), 1)
        self.assertEqual(html.count('class="textlink"'), 1)
        self.assertNotIn("Dritter Weg", html)
