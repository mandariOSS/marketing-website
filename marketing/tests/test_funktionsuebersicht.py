"""Funktionsübersicht (feature_matrix): „nicht vorgesehen“ bleibt ruhig, aber erkennbar."""

import re
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

MINUS = re.compile(r'<span class="([^"]*)"><i data-lucide="minus" class="w-4 h-4 flex-none"')


class NichtVorgesehenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def test_minus_mit_ausreichendem_kontrast(self):
        # Grau 500 auf Weiß 4,8:1, Grau 400 auf Grau 800 (dunkel) 5,8:1; Grau 400 hell hatte nur 2,5:1.
        html = self.client.get("/produkte/").content.decode("utf-8")
        klassen = MINUS.findall(html)
        self.assertTrue(klassen)
        for k in klassen:
            self.assertIn("text-gray-500", k.split())
            self.assertIn("dark:text-gray-400", k.split())
            self.assertNotIn("text-gray-400", k.split())
