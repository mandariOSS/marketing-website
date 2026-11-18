"""Kennzahlen des Bürgerportals (marketing/kennzahlen.py, mandariOSS/mandari#1481)."""

import json
from datetime import date
from unittest import mock

from django.core.cache import cache
from django.template import Context, Template
from django.test import SimpleTestCase, override_settings
from django.utils.safestring import SafeData, mark_safe

from marketing import kennzahlen as kz

ANTWORT = {"bodies": 41, "organizations": 3100, "persons": 18400, "meetings": 62000, "papers": 1234567}


class _Antwort:
    def __init__(self, daten):
        self.daten = json.dumps(daten).encode()

    def read(self, _hoechstens):
        return self.daten

    def __enter__(self):
        return self

    def __exit__(self, *_):
        return False


class KennzahlenTests(SimpleTestCase):
    def setUp(self):
        cache.clear()
        self.addCleanup(cache.clear)
        # Der Abruf läuft im Betrieb im Hintergrund; im Test sofort, damit das Ergebnis feststeht
        ersatz = mock.patch.object(kz, "_starten", lambda funktion, *argumente: funktion(*argumente))
        ersatz.start()
        self.addCleanup(ersatz.stop)

    def test_ohne_adresse_gilt_der_stand_im_code(self):
        with override_settings(KENNZAHLEN_URL=""), mock.patch("urllib.request.urlopen") as abruf:
            self.assertEqual(kz.kennzahlen(), kz.RUECKFALL)
            abruf.assert_not_called()

    def test_auswerten_verlangt_alle_felder_als_positive_ganze_zahl(self):
        heute = date(2026, 12, 1)
        gut = kz.auswerten(ANTWORT, heute)
        self.assertEqual((gut.kommunen, gut.vorgaenge, gut.sitzungen, gut.stand), (41, 1234567, 62000, heute))
        for kaputt in (None, [], {}, {**ANTWORT, "bodies": 0}, {**ANTWORT, "papers": "viele"},
                       {**ANTWORT, "meetings": True}, {k: v for k, v in ANTWORT.items() if k != "persons"}):
            self.assertIsNone(kz.auswerten(kaputt, heute), kaputt)

    def test_platzhalter_mit_tausenderpunkt_und_stand(self):
        werte = kz.auswerten(ANTWORT, date(2026, 12, 1)).platzhalter()
        self.assertEqual(werte["vorgaenge"], "1.234.567")
        self.assertEqual(werte["kommunen"], "41")
        self.assertEqual(werte["kennzahlen-stand"], "1. Dezember 2026")

    @override_settings(KENNZAHLEN_URL="https://beispiel.invalid/api/stats/")
    def test_erster_aufruf_wartet_nicht_und_erneuert_im_hintergrund(self):
        with mock.patch("urllib.request.urlopen", return_value=_Antwort(ANTWORT)) as abruf:
            # Der erste Aufruf liefert sofort den Stand aus dem Code und stößt den Abruf an
            self.assertEqual(kz.kennzahlen(), kz.RUECKFALL)
            self.assertEqual(kz.kennzahlen().kommunen, 41)
            self.assertEqual(kz.kennzahlen().kommunen, 41)
            self.assertEqual(abruf.call_count, 1)

    @override_settings(KENNZAHLEN_URL="https://beispiel.invalid/api/stats/")
    def test_seite_wartet_nie_auf_die_statistik(self):
        gestartet = []
        with mock.patch.object(kz, "_starten", lambda funktion, *argumente: gestartet.append(funktion)),                 mock.patch("urllib.request.urlopen") as abruf:
            self.assertEqual(kz.kennzahlen(), kz.RUECKFALL)
            # Solange der Hintergrundlauf aussteht, startet kein zweiter
            self.assertEqual(kz.kennzahlen(), kz.RUECKFALL)
            abruf.assert_not_called()
        self.assertEqual(gestartet, [kz._erneuern])

    @override_settings(KENNZAHLEN_URL="https://beispiel.invalid/api/stats/")
    def test_ausfall_zeigt_letzten_stand_sonst_den_rueckfall(self):
        with mock.patch("urllib.request.urlopen", side_effect=OSError("aus")) as abruf:
            self.assertEqual(kz.kennzahlen(), kz.RUECKFALL)
            # Während der Pause nach einem Fehler fragt keine Seite erneut
            self.assertEqual(kz.kennzahlen(), kz.RUECKFALL)
            self.assertEqual(abruf.call_count, 1)
        cache.clear()
        with mock.patch("urllib.request.urlopen", return_value=_Antwort(ANTWORT)):
            kz.kennzahlen()
            self.assertEqual(kz.kennzahlen().kommunen, 41)
        cache.delete(kz._CACHE_FRISCH)
        with mock.patch("urllib.request.urlopen", side_effect=OSError("aus")):
            self.assertEqual(kz.kennzahlen().kommunen, 41)
            self.assertEqual(kz.kennzahlen().kommunen, 41)

    @override_settings(KENNZAHLEN_URL="")
    def test_filter_setzt_ein_und_bleibt_sicher(self):
        vorlage = Template("{% load kennzahlen %}{{ text|kennzahlen }}")
        html = vorlage.render(Context({"text": mark_safe("<b>[kommunen]</b> Kommunen, Stand [kennzahlen-stand]")}))
        self.assertEqual(html, f"<b>{kz.RUECKFALL.kommunen}</b> Kommunen, Stand {kz.RUECKFALL.stand_text()}")
        # Nicht als sicher markierter Text wird weiter maskiert
        html = vorlage.render(Context({"text": "<i>[kommunen]</i>"}))
        self.assertEqual(html, f"&lt;i&gt;{kz.RUECKFALL.kommunen}&lt;/i&gt;")
        self.assertNotIsInstance(kz.einsetzen("[kommunen]"), SafeData)

    @override_settings(KENNZAHLEN_URL="")
    def test_filter_nach_richtext_von_wagtail(self):
        # So steht es in der Vorlage: {{ self.satz|richtext|kennzahlen }}; richtext liefert ein RichText-Objekt
        vorlage = Template("{% load wagtailcore_tags kennzahlen %}{{ text|richtext|kennzahlen }}")
        html = vorlage.render(Context({"text": "<p>Aus <b>[kommunen]</b> Kommunen</p>"}))
        self.assertIn(f"<b>{kz.RUECKFALL.kommunen}</b> Kommunen", html)
        self.assertNotIn("[kommunen]", html)

    def test_text_ohne_platzhalter_bleibt_gleich(self):
        with mock.patch.object(kz, "kennzahlen") as lesen:
            self.assertEqual(kz.einsetzen("Kein Platzhalter"), "Kein Platzhalter")
            lesen.assert_not_called()
