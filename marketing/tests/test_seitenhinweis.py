"""Seitenhinweis über der Kopfzeile, gesteuert über die Umgebung (SEITENHINWEIS)."""

from django.template.loader import render_to_string
from django.test import RequestFactory, SimpleTestCase, override_settings

from marketing.context_processors import site_context


class SeitenhinweisTests(SimpleTestCase):
    def _html(self):
        request = RequestFactory().get("/")
        return render_to_string("base.html", site_context(request), request=request)

    @override_settings(SEITENHINWEIS="")
    def test_ohne_hinweis_keine_leiste(self):
        self.assertNotIn('role="status"', self._html())

    @override_settings(SEITENHINWEIS="Viele Ratsinformationssysteme sind nicht erreichbar.")
    def test_hinweis_vor_der_kopfzeile_mit_link_zur_statusseite(self):
        html = self._html()
        self.assertIn("Viele Ratsinformationssysteme sind nicht erreichbar.", html)
        self.assertLess(html.index('role="status"'), html.index('role="banner"'))
        self.assertIn("Zur Statusseite", html)

    @override_settings(SEITENHINWEIS="<script>x</script>")
    def test_hinweis_wird_maskiert(self):
        self.assertNotIn("<script>x</script>", self._html())
