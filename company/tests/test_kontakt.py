"""Kontaktformulare auf /kontakt/: Spamschutz, Prüfung, Zustellung und Rückmeldung."""

import base64
import datetime
import hashlib
import json
import os
from io import StringIO
from unittest import mock

from django.conf import settings
from django.core import mail
from django.core.cache import caches
from django.core.management import call_command
from django.test import RequestFactory, SimpleTestCase, TestCase, override_settings
from django.utils import timezone

from marketing import contact

LOCMEM = "django.core.mail.backends.locmem.EmailBackend"


def next_weekday(days=7):
    day = timezone.localdate() + datetime.timedelta(days=days)
    while day.weekday() >= 5:
        day += datetime.timedelta(days=1)
    return day


@override_settings(EMAIL_BACKEND=LOCMEM, ALTCHA_MAX_NUMBER=500)
class KontaktformularTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())

    def setUp(self):
        caches[contact.CACHE_ALIAS].clear()

    def solve_altcha(self):
        challenge = self.client.get("/altcha/challenge/").json()
        number = next(
            n for n in range(challenge["maxnumber"] + 1)
            if hashlib.sha256(f"{challenge['salt']}{n}".encode()).hexdigest() == challenge["challenge"]
        )
        payload = {"algorithm": "SHA-256", "challenge": challenge["challenge"], "number": number,
                   "salt": challenge["salt"], "signature": challenge["signature"]}
        return base64.b64encode(json.dumps(payload).encode()).decode()

    def post_from(self, data, forwarded_for, remote="10.0.0.1"):
        return self.client.post("/kontakt/", data, HTTP_X_FORWARDED_FOR=forwarded_for, REMOTE_ADDR=remote)

    def termin(self, **overrides):
        data = {
            "art": "termin", "datum": next_weekday().isoformat(), "zeitfenster": "11-13", "format": "telefon",
            "thema": "verwaltung", "name": "Erika Muster", "email": "erika@example.org",
            "organisation": "Stadt Musterstadt", "telefon": "0251 123456", "nachricht": "Umstieg 2027",
            "datenschutz": "on", "anlass": "Session-Angebot", "website": "", "altcha": self.solve_altcha(),
        }
        data.update(overrides)
        return data

    def nachricht(self, **overrides):
        data = {
            "art": "nachricht", "thema": "presse", "name": "Max Presse", "email": "max@example.org",
            "nachricht": "Wir planen einen Bericht über offene Ratsdaten.", "datenschutz": "on",
            "website": "", "altcha": self.solve_altcha(),
        }
        data.update(overrides)
        return data

    def test_subject_waehlt_thema_vor(self):
        body = self.client.get("/kontakt/?subject=Session-Angebot").content.decode("utf-8")
        self.assertIn('<option value="verwaltung" selected>', body)
        self.assertIn('value="Session-Angebot"', body)

    def test_terminanfrage_wird_zugestellt(self):
        response = self.client.post("/kontakt/", self.termin())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response["Location"], "/kontakt/?gesendet=termin#termin")
        self.assertEqual(len(mail.outbox), 1)
        message = mail.outbox[0]
        self.assertTrue(message.subject.startswith("Terminanfrage: Demo für unsere Verwaltung"))
        self.assertEqual(message.to, ["hello@mandari.de"])
        self.assertEqual(message.reply_to, ["erika@example.org"])
        self.assertIn("Gesprächsform: Am Telefon", message.body)
        self.assertIn("Aufgerufen über: Session-Angebot", message.body)
        self.assertTrue(message.extra_headers["Message-ID"].endswith("@mandari.de>"))

        confirmation = self.client.get(response["Location"]).content.decode("utf-8")
        self.assertIn("Danke, Ihre Terminanfrage ist bei uns.", confirmation)

    def test_nachricht_wird_zugestellt(self):
        response = self.client.post("/kontakt/", self.nachricht())
        self.assertEqual(response.status_code, 302)
        self.assertEqual(len(mail.outbox), 1)
        self.assertTrue(mail.outbox[0].subject.startswith("Nachricht: Presse und Medien"))

    def test_ohne_spamschutz_keine_zustellung(self):
        response = self.client.post("/kontakt/", self.nachricht(altcha=""))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Der Spamschutz konnte Ihre Anfrage nicht bestätigen.")
        self.assertEqual(mail.outbox, [])

    @override_settings(ALTCHA_EXPIRES_SECONDS=-1)
    def test_abgelaufene_aufgabe_gilt_nicht(self):
        response = self.client.post("/kontakt/", self.nachricht())
        self.assertContains(response, "Der Spamschutz konnte Ihre Anfrage nicht bestätigen.")
        self.assertContains(response, "Ihre Eingaben sind erhalten.")
        self.assertContains(response, "Wir planen einen Bericht über offene Ratsdaten.")
        self.assertEqual(mail.outbox, [])

    def test_aufgabe_ohne_ablaufzeit_gilt_nicht(self):
        import hmac

        salt, number = "ohne-ablauf", 7
        challenge = hashlib.sha256(f"{salt}{number}".encode()).hexdigest()
        signature = hmac.new(settings.ALTCHA_HMAC_KEY.encode(), challenge.encode(), hashlib.sha256).hexdigest()
        payload = {"algorithm": "SHA-256", "challenge": challenge, "number": number, "salt": salt,
                   "signature": signature}
        altcha = base64.b64encode(json.dumps(payload).encode()).decode()
        response = self.client.post("/kontakt/", self.nachricht(altcha=altcha))
        self.assertContains(response, "Der Spamschutz konnte Ihre Anfrage nicht bestätigen.")
        self.assertEqual(mail.outbox, [])

    def test_geloeste_aufgabe_gilt_nur_einmal(self):
        data = self.nachricht()
        self.assertEqual(self.client.post("/kontakt/", data).status_code, 302)
        response = self.client.post("/kontakt/", data)
        self.assertContains(response, "Der Spamschutz konnte Ihre Anfrage nicht bestätigen.")
        self.assertEqual(len(mail.outbox), 1)

    def test_honigtopf(self):
        self.client.post("/kontakt/", self.nachricht(website="https://spam.example"))
        self.assertEqual(mail.outbox, [])

    def test_pflichtfelder_und_werktag(self):
        saturday = timezone.localdate() + datetime.timedelta(days=(5 - timezone.localdate().weekday()) % 7 or 7)
        response = self.client.post("/kontakt/", self.termin(datum=saturday.isoformat(), name="", datenschutz=""))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Bitte prüfen Sie die markierten Felder.")
        self.assertContains(response, "Bitte wählen Sie einen Tag von Montag bis Freitag.")
        self.assertContains(response, "Bitte bestätigen Sie die Datenschutzerklärung.")
        self.assertContains(response, 'value="Stadt Musterstadt"')  # Eingaben bleiben erhalten
        self.assertEqual(mail.outbox, [])

    def test_einmal_pruefung_im_gemeinsamen_zwischenspeicher(self):
        """Beide gunicorn-Worker müssen dieselbe Einmal-Prüfung sehen – also kein Speicher je Prozess."""
        self.assertEqual(settings.CACHES[contact.CACHE_ALIAS]["BACKEND"],
                         "django.core.cache.backends.db.DatabaseCache")
        self.assertEqual(self.client.post("/kontakt/", self.nachricht()).status_code, 302)
        from django.db import connection

        table = connection.ops.quote_name(settings.CACHES[contact.CACHE_ALIAS]["LOCATION"])
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT cache_key FROM {table}")
            keys = [row[0] for row in cursor.fetchall()]
        self.assertTrue(any("kontakt:altcha:" in key for key in keys), keys)

    def test_grenze_je_adresse(self):
        for _ in range(5):
            self.assertEqual(self.client.post("/kontakt/", self.nachricht()).status_code, 302)
        response = self.client.post("/kontakt/", self.nachricht())
        self.assertContains(response, "schon mehrere Anfragen")
        self.assertEqual(len(mail.outbox), 5)

    def test_wechselnder_forwarded_for_umgeht_die_grenze_nicht(self):
        """Selbst gesetzte X-Forwarded-For-Einträge zählen nicht, nur der des eigenen Proxys (der letzte)."""
        for i in range(5):
            response = self.post_from(self.nachricht(), f"198.51.100.{i}, 203.0.113.7")
            self.assertEqual(response.status_code, 302)
        response = self.post_from(self.nachricht(), "198.51.100.99, 203.0.113.7")
        self.assertContains(response, "schon mehrere Anfragen")
        # Eine andere Besucherin hinter demselben Proxy ist nicht betroffen.
        self.assertEqual(self.post_from(self.nachricht(), "203.0.113.8").status_code, 302)
        self.assertEqual(len(mail.outbox), 6)

    @mock.patch.dict(os.environ, {"CONTACT_TRUSTED_PROXIES": "0"})
    def test_ohne_proxy_zaehlt_die_verbindung(self):
        for i in range(5):
            self.assertEqual(self.post_from(self.nachricht(), f"198.51.100.{i}").status_code, 302)
        response = self.post_from(self.nachricht(), "198.51.100.99")
        self.assertContains(response, "schon mehrere Anfragen")

    @mock.patch.object(contact, "TOTAL_PER_HOUR", 2)
    def test_gesamtgrenze_mit_neutraler_meldung(self):
        for i in range(2):
            self.assertEqual(self.post_from(self.nachricht(), f"203.0.113.{i}").status_code, 302)
        response = self.post_from(self.nachricht(), "203.0.113.50")
        self.assertContains(response, "Das Formular nimmt gerade keine weiteren Anfragen an.")
        self.assertNotContains(response, "Von Ihrem Anschluss")
        self.assertEqual(len(mail.outbox), 2)

    @override_settings(DEBUG=False, EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    def test_ohne_zustellweg_mailadresse_statt_formular(self):
        body = self.client.get("/kontakt/").content.decode("utf-8")
        self.assertNotIn("<form", body)
        self.assertNotIn("altcha", body)
        self.assertIn('href="mailto:hello@mandari.de?subject=Erstgespr%C3%A4ch"', body)
        self.assertIn('id="termin"', body)
        self.assertIn('id="nachricht"', body)

    @override_settings(DEBUG=False, EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    def test_ohne_zustellweg_ehrliche_rueckmeldung(self):
        response = self.client.post("/kontakt/", self.nachricht())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ihre Anfrage konnte gerade nicht zugestellt werden.")


class AnschlussTests(SimpleTestCase):
    """Welcher Anschluss für die Begrenzung zählt."""

    def address(self, forwarded="", remote="10.0.0.1", proxies="1"):
        request = RequestFactory().post("/kontakt/", REMOTE_ADDR=remote)
        if forwarded:
            request.META["HTTP_X_FORWARDED_FOR"] = forwarded
        with mock.patch.dict(os.environ, {"CONTACT_TRUSTED_PROXIES": proxies}):
            return contact._client_address(request)

    def test_letzter_eintrag_des_eigenen_proxys(self):
        self.assertEqual(self.address("1.2.3.4, 203.0.113.7"), "203.0.113.7")

    def test_zwei_eigene_proxys(self):
        self.assertEqual(self.address("1.2.3.4, 203.0.113.7, 10.0.0.2", proxies="2"), "203.0.113.7")

    def test_ohne_header_zaehlt_die_verbindung(self):
        self.assertEqual(self.address(), "10.0.0.1")

    def test_unsinn_im_header(self):
        self.assertEqual(self.address("kein-ip"), "10.0.0.1")

    def test_ipv6_zaehlt_je_64er_netz(self):
        self.assertEqual(self.address("2001:db8:1:2:aaaa::1"), "2001:db8:1:2::/64")
        self.assertEqual(self.address("2001:db8:1:2:bbbb::9"), "2001:db8:1:2::/64")
