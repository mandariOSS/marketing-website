"""Kontaktformulare auf /kontakt/: Spamschutz, Prüfung, Zustellung und Rückmeldung."""

import base64
import datetime
import hashlib
import json
from io import StringIO

from django.core import mail
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase, override_settings
from django.utils import timezone

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
        cache.clear()

    def solve_altcha(self):
        challenge = self.client.get("/altcha/challenge/").json()
        number = next(
            n for n in range(challenge["maxnumber"] + 1)
            if hashlib.sha256(f"{challenge['salt']}{n}".encode()).hexdigest() == challenge["challenge"]
        )
        payload = {"algorithm": "SHA-256", "challenge": challenge["challenge"], "number": number,
                   "salt": challenge["salt"], "signature": challenge["signature"]}
        return base64.b64encode(json.dumps(payload).encode()).decode()

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

    def test_grenze_je_adresse(self):
        for _ in range(5):
            self.assertEqual(self.client.post("/kontakt/", self.nachricht()).status_code, 302)
        response = self.client.post("/kontakt/", self.nachricht())
        self.assertContains(response, "schon mehrere Anfragen")
        self.assertEqual(len(mail.outbox), 5)

    @override_settings(DEBUG=False, EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend")
    def test_ohne_zustellweg_ehrliche_rueckmeldung(self):
        response = self.client.post("/kontakt/", self.nachricht())
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Ihre Anfrage konnte gerade nicht zugestellt werden.")
