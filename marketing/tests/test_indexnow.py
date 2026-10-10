"""IndexNow: Schlüsseldatei, Meldungen an die Suchmaschine, Meldung beim Veröffentlichen und der Befehl."""

import json
import urllib.error
from io import StringIO
from unittest import mock

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import SimpleTestCase, TestCase, override_settings
from wagtail.models import Page

from marketing import indexnow
from marketing.models import MarketingPage

SCHLUESSEL = "3f8a1c2e9b7d4a6f8e0c1b2a3d4e5f60"
ENDPUNKT = "https://api.indexnow.org/indexnow"
MIT_SCHLUESSEL = override_settings(
    SITE_URL="https://mandari.de",
    INDEXNOW_KEY=SCHLUESSEL,
    INDEXNOW_ENDPOINT=ENDPUNKT,
    ALLOWED_HOSTS=["mandari.de", "testserver"],
)


class Antwort:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def gesendet(urlopen):
    """Die gemeldeten Daten je Aufruf von ``urlopen``."""
    return [json.loads(aufruf.args[0].data) for aufruf in urlopen.call_args_list]


@MIT_SCHLUESSEL
class SchluesseldateiTests(TestCase):  # 404-Seite liest Navigation aus der Datenbank
    def test_liefert_den_schluessel_als_text(self):
        antwort = self.client.get(f"/{SCHLUESSEL}.txt", HTTP_HOST="mandari.de")
        self.assertEqual(antwort.status_code, 200)
        self.assertEqual(antwort["Content-Type"], "text/plain; charset=utf-8")
        self.assertEqual(antwort.content.decode(), SCHLUESSEL)

    def test_head_fuer_pruefwerkzeuge(self):
        self.assertEqual(self.client.head(f"/{SCHLUESSEL}.txt", HTTP_HOST="mandari.de").status_code, 200)

    def test_anderer_name_404(self):
        self.assertEqual(self.client.get("/0123456789abcdef.txt", HTTP_HOST="mandari.de").status_code, 404)

    @override_settings(INDEXNOW_KEY="")
    def test_ohne_schluessel_404(self):
        self.assertEqual(self.client.get(f"/{SCHLUESSEL}.txt", HTTP_HOST="mandari.de").status_code, 404)

    @override_settings(INDEXNOW_KEY="kurz")
    def test_schluessel_ausserhalb_des_protokolls_gilt_nicht(self):
        self.assertEqual(indexnow.schluessel(), "")
        self.assertEqual(self.client.get("/kurz.txt", HTTP_HOST="mandari.de").status_code, 404)

    def test_robots_txt_bleibt_unberuehrt(self):
        antwort = self.client.get("/robots.txt", HTTP_HOST="mandari.de")
        self.assertEqual(antwort.status_code, 200)
        self.assertIn("Sitemap:", antwort.content.decode())


@MIT_SCHLUESSEL
class MeldenTests(SimpleTestCase):
    @mock.patch("marketing.indexnow.urllib.request.urlopen", return_value=Antwort(200))
    def test_meldet_eigene_adressen_einmal(self, urlopen):
        angenommen = indexnow.melden(
            [
                "https://mandari.de/kommunen/",
                "https://mandari.de/kommunen/",
                "https://example.org/fremd/",
                "/relativ/",
                "https://mandari.de/ratsinformationssystem/",
            ]
        )

        self.assertEqual(angenommen, 2)
        anfrage = urlopen.call_args.args[0]
        self.assertEqual(anfrage.full_url, ENDPUNKT)
        self.assertEqual(anfrage.get_method(), "POST")
        self.assertEqual(anfrage.get_header("Content-type"), "application/json; charset=utf-8")
        self.assertEqual(
            gesendet(urlopen),
            [
                {
                    "host": "mandari.de",
                    "key": SCHLUESSEL,
                    "keyLocation": f"https://mandari.de/{SCHLUESSEL}.txt",
                    "urlList": ["https://mandari.de/kommunen/", "https://mandari.de/ratsinformationssystem/"],
                }
            ],
        )
        self.assertEqual(urlopen.call_args.kwargs["timeout"], indexnow.WARTEZEIT_SEKUNDEN)

    @mock.patch("marketing.indexnow.ADRESSEN_JE_MELDUNG", 2)
    @mock.patch("marketing.indexnow.urllib.request.urlopen", return_value=Antwort(202))
    def test_teilt_in_meldungen_nach_der_grenze(self, urlopen):
        adressen = [f"https://mandari.de/seite-{n}/" for n in range(5)]

        self.assertEqual(indexnow.melden(adressen), 5)
        self.assertEqual([len(daten["urlList"]) for daten in gesendet(urlopen)], [2, 2, 1])

    @mock.patch(
        "marketing.indexnow.urllib.request.urlopen",
        side_effect=urllib.error.HTTPError(ENDPUNKT, 403, "Forbidden", {}, None),
    )
    def test_abgelehnte_meldung_wirft_nicht(self, urlopen):
        with self.assertLogs("marketing.indexnow", "WARNING") as protokoll:
            self.assertEqual(indexnow.melden(["https://mandari.de/kommunen/"]), 0)
        self.assertIn("Antwort 403", protokoll.output[0])

    @mock.patch("marketing.indexnow.urllib.request.urlopen", side_effect=urllib.error.URLError("timed out"))
    def test_nicht_erreichbar_wirft_nicht(self, urlopen):
        with self.assertLogs("marketing.indexnow", "WARNING"):
            self.assertEqual(indexnow.melden(["https://mandari.de/kommunen/"]), 0)

    @override_settings(INDEXNOW_KEY="")
    @mock.patch("marketing.indexnow.urllib.request.urlopen")
    def test_ohne_schluessel_keine_meldung(self, urlopen):
        self.assertEqual(indexnow.melden(["https://mandari.de/kommunen/"]), 0)
        urlopen.assert_not_called()


@MIT_SCHLUESSEL
class VeroeffentlichenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        cls.home = Page.objects.get(depth=2).specific
        cls.eltern = MarketingPage(title="Übersicht", slug="uebersicht")
        cls.home.add_child(instance=cls.eltern)
        cls.eltern.save_revision().publish()

    def _neue_seite(self):
        seite = MarketingPage(title="Neu", slug="neu")
        self.eltern.add_child(instance=seite)
        return seite

    @mock.patch("marketing.indexnow.melden")
    def test_veroeffentlichen_meldet_seite_und_elternseite(self, melden):
        seite = self._neue_seite()
        with self.captureOnCommitCallbacks(execute=True):
            seite.save_revision().publish()

        melden.assert_called_once_with(["https://mandari.de/uebersicht/neu/", "https://mandari.de/uebersicht/"])

    @mock.patch("marketing.indexnow.melden")
    def test_zurueckziehen_meldet_die_entfallene_adresse(self, melden):
        seite = self._neue_seite()
        seite.save_revision().publish()
        melden.reset_mock()

        with self.captureOnCommitCallbacks(execute=True):
            seite.unpublish()

        melden.assert_called_once_with(["https://mandari.de/uebersicht/neu/", "https://mandari.de/uebersicht/"])

    @override_settings(INDEXNOW_KEY="")
    @mock.patch("marketing.indexnow.melden")
    def test_ohne_schluessel_keine_meldung(self, melden):
        seite = self._neue_seite()
        with self.captureOnCommitCallbacks(execute=True):
            seite.save_revision().publish()

        melden.assert_not_called()


@MIT_SCHLUESSEL
class BefehlTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())

    def test_probelauf_zeigt_alle_adressen_der_sitemap(self):
        out = StringIO()
        call_command("indexnow_melden", "--alle", "--probelauf", stdout=out)

        zeilen = out.getvalue().splitlines()
        self.assertIn("https://mandari.de/", zeilen)
        self.assertIn("https://mandari.de/kontakt/", zeilen)
        self.assertTrue(zeilen[-1].startswith("[Probelauf]"))

    @mock.patch("marketing.indexnow.melden", side_effect=lambda adressen: len(adressen))
    def test_meldet_pfade_als_adressen(self, melden):
        call_command("indexnow_melden", "/kommunen/", "https://mandari.de/preise/", stdout=StringIO())

        melden.assert_called_once_with(["https://mandari.de/kommunen/", "https://mandari.de/preise/"])

    @override_settings(INDEXNOW_KEY="")
    def test_ohne_schluessel_fehler(self):
        with self.assertRaises(CommandError):
            call_command("indexnow_melden", "--alle", stdout=StringIO())
