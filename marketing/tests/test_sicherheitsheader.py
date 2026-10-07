"""Sicherheits-Header: Permissions-Policy, Content-Security-Policy mit den Hashes des Inline-Codes und ETag."""

import base64
import hashlib
import re
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.template import Context, Template
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings

from marketing import sicherheit
from marketing.templatetags import stile

RO = "Content-Security-Policy-Report-Only"
SCHARF = "Content-Security-Policy"
INLINE = re.compile(r"<(script|style)\b([^>]*)>(.*?)</\1>", re.S)


def sha256(text):
    return "'sha256-" + base64.b64encode(hashlib.sha256(text.encode()).digest()).decode() + "'"


def inline_elemente(html):
    """Ausführbare Inline-Skripte und <style>-Elemente außerhalb von <noscript>."""
    ohne_noscript = re.sub(r"<noscript>.*?</noscript>", "", html, flags=re.S)
    for art, attribute, inhalt in INLINE.findall(ohne_noscript):
        if art == "script" and ("src=" in attribute or "application/ld+json" in attribute):
            continue
        yield art, inhalt


def richtlinie(antwort, header=RO):
    return dict(d.strip().split(" ", 1) for d in antwort[header].split(";"))


class PolicyTests(SimpleTestCase):
    def test_hash_wie_im_browser_auch_bei_crlf(self):
        self.assertEqual(sicherheit.quelle("a{}"), sha256("a{}"))
        self.assertEqual(sicherheit.quelle("a{\r\n}"), sha256("a{\n}"))

    def test_grundgeruest(self):
        teile = dict(d.split(" ", 1) for d in sicherheit.richtlinie().split("; "))
        self.assertEqual(teile["default-src"], "'self'")
        self.assertEqual(teile["object-src"], "'none'")
        self.assertEqual(teile["frame-ancestors"], "'self'")
        self.assertEqual(teile["report-uri"], "/csp-report/")
        # Kein pauschales Inline für Skripte und <style>; Alpine braucht eval, Altcha einen blob:-Worker
        self.assertNotIn("unsafe-inline", teile["script-src"])
        self.assertNotIn("unsafe-inline", teile["style-src"])
        self.assertIn("'unsafe-eval'", teile["script-src"])
        self.assertIn("blob:", teile["worker-src"])

    def test_stil_von_altcha_gefunden(self):
        # Altcha schreibt beim Laden einen festen Stil in den Kopf (/kontakt/); sein Hash muss dort in style-src stehen
        sicherheit.altcha_stil.cache_clear()
        quelle = sicherheit.altcha_stil()
        self.assertRegex(quelle, r"^'sha256-[A-Za-z0-9+/]{43}='$")
        anfrage = RequestFactory().get("/kontakt/")
        Template("{% load sicherheit %}{% csp_altcha %}").render(Context({"request": anfrage}))
        self.assertIn(quelle, sicherheit.richtlinie(anfrage._csp_inline))
        self.assertNotIn(quelle, sicherheit.richtlinie())

    def test_csp_inline_meldet_nur_ausfuehrbaren_code(self):
        anfrage = RequestFactory().get("/")
        html = Template(
            "{% load sicherheit %}{% csp_inline %}<script>eins()</script><style>p{}</style>"
            '<script src="/x.js"></script><script type="application/ld+json">{"a":1}</script>'
            '<script type="module">zwei()</script>{% endcsp_inline %}'
        ).render(Context({"request": anfrage}))
        self.assertIn("<script>eins()</script>", html)
        self.assertEqual(anfrage._csp_inline["script"], {sha256("eins()"), sha256("zwei()")})
        self.assertEqual(anfrage._csp_inline["style"], {sha256("p{}")})

    @override_settings(DEBUG=False)
    def test_stile_meldet_kritisches_css_und_ladeskript_an(self):
        anfrage = RequestFactory().get("/")
        with mock.patch.object(stile, "kritisches_css", return_value=".hero{}"):
            Template("{% load stile %}{% stile %}").render(Context({"request": anfrage}))
        self.assertEqual(anfrage._csp_inline["style"], {sha256(".hero{}")})
        self.assertEqual(anfrage._csp_inline["script"], {sha256(stile.LADER)})

    def test_unbekannter_modus_gilt_als_report(self):
        with override_settings(CSP_MODUS="an"), self.assertLogs("marketing.sicherheit", "WARNING"):
            sicherheit._gueltiger_modus.cache_clear()
            self.assertEqual(sicherheit.modus(), "report")


@override_settings(SITE_URL="https://mandari.de", DEBUG=False)
class HeaderTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def kritisch(self):
        # Wie im Betrieb: kritisches CSS inline (ohne gebautes kritisch.css in der Testumgebung ein Ersatz)
        return mock.patch.object(stile, "kritisches_css", return_value=".hero{padding-top:3.5rem}")

    def test_permissions_policy_restriktiv_auf_jeder_antwort(self):
        for url in ("/", "/preise/", "/robots.txt", "/gibt-es-nicht/"):
            wert = self.client.get(url)["Permissions-Policy"]
            for funktion in ("camera", "microphone", "geolocation", "payment", "usb"):
                self.assertIn(f"{funktion}=()", wert, url)
            self.assertNotRegex(wert, r"=\((?!\))", url)  # keine Funktion freigegeben

    def test_report_only_als_standard_mit_hashes_aller_inline_elemente(self):
        for url in ("/", "/preise/", "/kontakt/", "/impressum/", "/gibt-es-nicht/"):
            with self.kritisch():
                antwort = self.client.get(url)
            self.assertNotIn(SCHARF, antwort, url)
            teile = richtlinie(antwort)
            self.assertEqual(teile["report-uri"], "/csp-report/", url)
            html = antwort.content.decode("utf-8")
            elemente = list(inline_elemente(html))
            self.assertGreaterEqual(len(elemente), 4, url)  # Dunkelmodus, Ladeskript, Schriften, kritisches CSS …
            for art, inhalt in elemente:
                self.assertIn(sha256(inhalt), teile[f"{art}-src"], f"{url}: {art} ohne Hash: {inhalt[:60]}")

    def test_header_namen_sind_zeichenketten(self):
        # WSGI-Server (wsgiref, gunicorn) lehnen Header-Namen ab, die keine echten str sind (CSP ist ein StrEnum)
        for name, wert in self.client.get("/preise/").items():
            self.assertIs(type(name), str, name)
            self.assertIs(type(wert), str, name)

    @override_settings(CSP_MODUS="scharf")
    def test_scharf(self):
        antwort = self.client.get("/preise/")
        self.assertIn(SCHARF, antwort)
        self.assertNotIn(RO, antwort)

    @override_settings(CSP_MODUS="aus")
    def test_aus(self):
        antwort = self.client.get("/preise/")
        self.assertNotIn(SCHARF, antwort)
        self.assertNotIn(RO, antwort)
        self.assertIn("Permissions-Policy", antwort)

    @override_settings(EMAIL_BACKEND="django.core.mail.backends.locmem.EmailBackend")
    def test_altcha_nur_auf_der_kontaktseite(self):
        altcha = sicherheit.altcha_stil()
        self.assertIn(altcha, richtlinie(self.client.get("/kontakt/"))["style-src"])
        self.assertNotIn(altcha, richtlinie(self.client.get("/preise/"))["style-src"])

    def test_nicht_fuer_verwaltung_und_nicht_html(self):
        self.assertNotIn(RO, self.client.get("/cms-admin/login/"))
        self.assertNotIn(RO, self.client.get("/robots.txt"))

    def test_seiten_ohne_formular_bytegleich_mit_etag(self):
        for url in ("/", "/preise/", "/roadmap/"):
            with self.kritisch():
                erste, zweite = self.client.get(url), self.client.get(url)
            self.assertEqual(erste.content, zweite.content, url)
            self.assertTrue(erste.has_header("ETag"), url)
            self.assertEqual(erste["ETag"], zweite["ETag"], url)
            with self.kritisch():
                bedingt = self.client.get(url, HTTP_IF_NONE_MATCH=erste["ETag"])
            self.assertEqual(bedingt.status_code, 304, url)
