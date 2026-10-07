from django.contrib.staticfiles.apps import StaticFilesConfig


class StatischeDateienConfig(StaticFilesConfig):
    """``django.contrib.staticfiles`` ohne die Quelle des Stylesheets.

    ``static/css/input.css`` bindet Tailwind mit ``@import "tailwindcss"`` ein. ``collectstatic`` hielte das für eine
    Datei neben input.css und bräche mit dem Manifest-Speicher (``DEBUG`` aus, Docker-Start, CI) ab. Ausgeliefert
    werden nur die gebauten ``styles.css`` und ``kritisch.css``; die Quelle braucht im Betrieb niemand.
    """

    ignore_patterns = [*StaticFilesConfig.ignore_patterns, "input.css"]
