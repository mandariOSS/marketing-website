"""
„Offene Daten“ auf der Website (mandariOSS/mandari#1309): Übersicht und eine Seite je Kommune aus der Übersicht der
OParl-Schnittstelle, mit Kurzadressen, Zwischenspeicher und Rückfall.
"""

import json
from unittest import mock

from django.core.cache import cache
from django.test import SimpleTestCase, TestCase, override_settings

from marketing import offene_daten

OPARL = "https://oparl.mandari.example/oparl"
KENNUNG = "3ae1b038-cf57-5305-a49b-83108c0d6b96"
UEBERSICHT = {
    "system": f"{OPARL}/v1/system",
    "bodyIndex": [
        {
            "name": "Stadt Köln",
            "displayName": "Köln",
            "slug": "koeln",
            "ags": "05315000",
            "body": f"{OPARL}/v1/body/11111111-1111-5111-8111-111111111111",
            "paper": f"{OPARL}/v1/body/11111111-1111-5111-8111-111111111111/papers",
            "meeting": f"{OPARL}/v1/body/11111111-1111-5111-8111-111111111111/meetings",
            "web": "https://mandari.example/insight/k/koeln/",
            "license": "https://dl-de.example/by",
        },
        {
            "name": "Stadt Münster",
            "displayName": "Münster",
            "slug": "muenster",
            "ags": "05515000",
            "body": f"{OPARL}/v1/body/{KENNUNG}",
            "paper": f"{OPARL}/v1/body/{KENNUNG}/papers",
            "meeting": f"{OPARL}/v1/body/{KENNUNG}/meetings",
            "organization": f"{OPARL}/v1/body/{KENNUNG}/organizations",
            "person": f"{OPARL}/v1/body/{KENNUNG}/people",
            "web": "https://mandari.example/insight/k/muenster/",
        },
        # Ohne Slug: keine eigene Seite, die Adressen bleiben die gültigen
        {"name": "Gemeinde Ohne", "body": f"{OPARL}/v1/body/22222222-2222-5222-8222-222222222222"},
        # Unbrauchbar: fällt heraus
        {"name": "Kaputt", "body": "javascript:alert(1)"},
        {"body": f"{OPARL}/v1/body/33333333-3333-5333-8333-333333333333"},
    ],
}


class _Antwort:
    def __init__(self, daten):
        self._roh = json.dumps(daten).encode("utf-8")

    def read(self, _menge=None):
        return self._roh

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


def _abruf(daten=UEBERSICHT):
    return mock.patch("marketing.offene_daten.urllib.request.urlopen", return_value=_Antwort(daten))


class AuswertenTests(SimpleTestCase):
    def test_kurzadressen_mit_dem_namen_der_kommune(self):
        verzeichnis = offene_daten.auswerten(UEBERSICHT, f"{OPARL}/")
        muenster = verzeichnis.kommune("muenster")

        self.assertEqual(muenster.adresse, f"{OPARL}/v1/body/muenster")
        self.assertEqual(muenster.kennung, f"{OPARL}/v1/body/{KENNUNG}")
        self.assertEqual(muenster.liste("paper").adresse, f"{OPARL}/v1/body/muenster/papers")
        self.assertEqual(muenster.liste("paper").kennung, f"{OPARL}/v1/body/{KENNUNG}/papers")
        self.assertEqual([liste.feld for liste in muenster.listen], ["paper", "meeting", "organization", "person"])
        self.assertEqual(verzeichnis.system, f"{OPARL}/v1/system")

    def test_ohne_slug_bleiben_die_gueltigen_adressen_und_unbrauchbares_faellt_heraus(self):
        verzeichnis = offene_daten.auswerten(UEBERSICHT, f"{OPARL}/")

        self.assertEqual([k.anzeige for k in verzeichnis.kommunen], ["Köln", "Münster", "Gemeinde Ohne"])
        ohne = verzeichnis.kommunen[2]
        self.assertEqual((ohne.slug, ohne.adresse), ("", ohne.kennung))

    def test_antwort_ohne_bodyindex_ist_kein_verzeichnis(self):
        self.assertIsNone(offene_daten.auswerten({"name": "etwas"}, f"{OPARL}/"))
        self.assertIsNone(offene_daten.auswerten(["liste"], f"{OPARL}/"))


@override_settings(OPARL_UEBERSICHT_URL=f"{OPARL}/", SITE_URL="https://mandari.de")
class AbrufTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def test_ein_abruf_fuer_viele_seiten(self):
        with _abruf() as urlopen:
            erste = offene_daten.verzeichnis()
            zweite = offene_daten.verzeichnis()

        self.assertEqual(urlopen.call_count, 1)
        self.assertEqual(erste, zweite)
        anfrage = urlopen.call_args.args[0]
        self.assertEqual(anfrage.full_url, f"{OPARL}/")
        self.assertEqual(urlopen.call_args.kwargs["timeout"], offene_daten.ZEITGRENZE_SEKUNDEN)

    def test_faellt_der_abruf_aus_gilt_der_letzte_bekannte_stand(self):
        with _abruf():
            offene_daten.verzeichnis()
        cache.delete("offene-daten:frisch")

        with mock.patch("marketing.offene_daten.urllib.request.urlopen", side_effect=OSError("weg")):
            stand = offene_daten.verzeichnis()

        self.assertEqual([k.slug for k in stand.kommunen], ["koeln", "muenster", ""])

    def test_ohne_gelungenen_abruf_gibt_es_kein_verzeichnis(self):
        with mock.patch("marketing.offene_daten.urllib.request.urlopen", side_effect=OSError("weg")):
            self.assertIsNone(offene_daten.verzeichnis())

    def test_gescheiterter_abruf_wird_nicht_bei_jeder_anfrage_wiederholt(self):
        """Auch ohne letzten Stand: Sonst hängt jede Anfrage bis zur Zeitgrenze an der Schnittstelle."""
        with mock.patch("marketing.offene_daten.urllib.request.urlopen", side_effect=OSError("weg")) as urlopen:
            self.assertIsNone(offene_daten.verzeichnis())
            self.assertIsNone(offene_daten.verzeichnis())
            self.assertIsNone(offene_daten.verzeichnis())
        self.assertEqual(urlopen.call_count, 1)

    def test_abgeschnittene_antwort_zaehlt_als_ausfall(self):
        import http.client

        with mock.patch(
            "marketing.offene_daten.urllib.request.urlopen", side_effect=http.client.IncompleteRead(b"{")
        ):
            self.assertIsNone(offene_daten.verzeichnis())

    @override_settings(OPARL_UEBERSICHT_URL="")
    def test_abgeschaltet_ruft_nichts_ab(self):
        with _abruf() as urlopen:
            self.assertIsNone(offene_daten.verzeichnis())
        urlopen.assert_not_called()


@override_settings(
    OPARL_UEBERSICHT_URL=f"{OPARL}/", SITE_URL="https://mandari.de", ALLOWED_HOSTS=["testserver"]
)
class SeitenTests(TestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)

    def seite(self, pfad):
        with _abruf():
            antwort = self.client.get(pfad)
        return antwort, antwort.content.decode("utf-8")

    def test_uebersicht_nennt_einstieg_und_jede_kommune_mit_kurzadresse(self):
        antwort, html = self.seite("/offene-daten/")

        self.assertEqual(antwort.status_code, 200)
        self.assertIn("<title>Offene Daten: OParl-Schnittstelle und Adressen je Kommune | mandari</title>", html)
        # Adressen als sichtbarer Text, nicht nur im Link
        self.assertIn(f">{OPARL}/v1/system</a>", html)
        self.assertIn(f">{OPARL}/v1/body/muenster</a>", html)
        self.assertIn(f'href="{OPARL}/v1/body/muenster/papers"', html)
        self.assertIn(f">{OPARL}/v1/body/muenster/papers?modified_since=", html)
        self.assertIn('href="/offene-daten/muenster/"', html)
        self.assertIn('href="/offene-daten/koeln/"', html)
        self.assertNotIn("Kaputt", html)
        self.assertNotIn("javascript:", html)

    def test_uebersicht_traegt_den_datenkatalog(self):
        _, html = self.seite("/offene-daten/")
        daten = json.loads(html.split('<script type="application/ld+json">')[1].split("</script>")[0])
        katalog = next(knoten for knoten in daten["@graph"] if knoten["@type"] == "DataCatalog")

        self.assertEqual(katalog["sameAs"], f"{OPARL}/v1/system")
        namen = {d["name"]: d for d in katalog["dataset"]}
        self.assertEqual(namen["Ratsinformationen Münster"]["url"], "https://mandari.de/offene-daten/muenster/")
        self.assertEqual(namen["Ratsinformationen Münster"]["identifier"], "05515000")
        # Die Kennung, nicht die Kurzadresse, steht in den Daten für Maschinen
        self.assertEqual(
            namen["Ratsinformationen Münster"]["distribution"][0]["contentUrl"], f"{OPARL}/v1/body/{KENNUNG}"
        )
        self.assertEqual(namen["Ratsinformationen Köln"]["license"], "https://dl-de.example/by")
        self.assertNotIn("license", namen["Ratsinformationen Münster"])

    def test_seite_der_kommune(self):
        antwort, html = self.seite("/offene-daten/muenster/")

        self.assertEqual(antwort.status_code, 200)
        self.assertIn("<title>OParl-Schnittstelle Münster: offene Ratsdaten | mandari</title>", html)
        self.assertIn("Offene Daten Münster</h1>", html)
        for adresse in ("", "/papers", "/meetings", "/organizations", "/people"):
            self.assertIn(f">{OPARL}/v1/body/muenster{adresse}</a>", html, adresse)
        # Die Kennung steht als Text daneben
        self.assertIn(f"{OPARL}/v1/body/{KENNUNG}", html)
        self.assertIn(f">{OPARL}/v1/system</a>", html)
        self.assertIn("05515000", html)
        self.assertNotIn("Köln", html)
        daten = json.loads(html.split('<script type="application/ld+json">')[1].split("</script>")[0])
        datensatz = next(knoten for knoten in daten["@graph"] if knoten["@type"] == "Dataset")
        self.assertEqual(datensatz["url"], "https://mandari.de/offene-daten/muenster/")

    def test_unbekannte_kommune_ist_404(self):
        antwort, _ = self.seite("/offene-daten/gibt-es-nicht/")
        self.assertEqual(antwort.status_code, 404)

    def test_ohne_abruf_nennt_die_uebersicht_den_einstieg_und_die_seite_der_kommune_fehlt(self):
        with mock.patch("marketing.offene_daten.urllib.request.urlopen", side_effect=OSError("weg")):
            uebersicht = self.client.get("/offene-daten/")
            kommune = self.client.get("/offene-daten/muenster/")

        self.assertEqual(uebersicht.status_code, 200)
        html = uebersicht.content.decode("utf-8")
        self.assertIn(f">{OPARL}/v1/system</a>", html)
        self.assertIn("gerade nicht abrufbar", html)
        self.assertEqual(kommune.status_code, 404)

    def test_sitemap_nennt_uebersicht_und_kommunen(self):
        _, sitemap = self.seite("/sitemap.xml")

        self.assertIn("<loc>https://mandari.de/offene-daten/</loc>", sitemap)
        self.assertIn("<loc>https://mandari.de/offene-daten/muenster/</loc>", sitemap)
        self.assertIn("<loc>https://mandari.de/offene-daten/koeln/</loc>", sitemap)

    def test_fusszeile_verlinkt_die_seite(self):
        _, html = self.seite("/offene-daten/")
        self.assertIn('<a href="/offene-daten/" aria-current="page">Offene Daten</a>', html)
