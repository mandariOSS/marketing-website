"""Statische Dateien: collectstatic läuft mit dem Manifest-Speicher wie im Betrieb (DEBUG aus, Start des Containers,
CI) und liefert die Quelle des Stylesheets nicht aus.

static/css/input.css bindet Tailwind CSS 4 mit ``@import "tailwindcss"`` ein. Der Manifest-Speicher hielte das für
eine Datei neben input.css und bräche ab; deshalb übergeht ``website.apps.StatischeDateienConfig`` die Quelle."""

import json
import tempfile
from io import StringIO
from pathlib import Path

from django.apps import apps
from django.conf import settings
from django.core.management import call_command
from django.test import SimpleTestCase, override_settings

MANIFEST = "django.contrib.staticfiles.storage.ManifestStaticFilesStorage"


class CollectstaticTests(SimpleTestCase):
    def test_quelle_bindet_tailwind_per_import_ein(self):
        quelle = (Path(settings.BASE_DIR) / "static/css/input.css").read_text(encoding="utf-8")
        self.assertIn('@import "tailwindcss"', quelle)

    def test_manifest_ohne_quelle_des_stylesheets(self):
        with (
            tempfile.TemporaryDirectory() as ziel,
            override_settings(
                STATIC_ROOT=ziel,
                STATICFILES_FINDERS=["django.contrib.staticfiles.finders.FileSystemFinder"],
                STORAGES={**settings.STORAGES, "staticfiles": {"BACKEND": MANIFEST}},
            ),
        ):
            call_command("collectstatic", interactive=False, verbosity=0, stdout=StringIO())
            pfade = json.loads((Path(ziel) / "staticfiles.json").read_text(encoding="utf-8"))["paths"]
        self.assertNotIn("css/input.css", pfade)
        self.assertIn("css/erste-ansicht.css", pfade)
        self.assertIn("fonts/inter-latin.woff2", pfade)

    def test_staticfiles_mit_eigenen_ausnahmen(self):
        config = apps.get_app_config("staticfiles")
        self.assertEqual(type(config).__name__, "StatischeDateienConfig")
        self.assertIn("input.css", config.ignore_patterns)
        self.assertIn("CVS", config.ignore_patterns)  # Standardausnahmen von Django bleiben
