"""
Zentrale Quelle für die Inhalte der rechtlichen Seiten (Impressum,
Datenschutz, AGB).

Die authoritative Fassung liegt als reines HTML in `.legal-content/` im
Repo-Root (eine Datei pro Seite). Dieses Modul lädt die Dateien für das
Seed-Command `setup_initial_pages`, das die Texte in die
`LegalPage.body`-Felder (RichText) schreibt.

Inhalte NICHT hier oder in Templates hardcoden — Änderungen an den
Rechtstexten gehören in `.legal-content/*.html` (für neue Deployments)
bzw. in den Wagtail-Admin (für laufende Instanzen).
"""

from pathlib import Path

# Repo-Root = eine Ebene über dem marketing-Package
LEGAL_CONTENT_DIR = Path(__file__).resolve().parent.parent / ".legal-content"

# Slug der LegalPage → Dateiname in .legal-content/
LEGAL_FILES = {
    "impressum": "impressum.html",
    "datenschutz": "datenschutz.html",
    "agb": "agb.html",
}


def load_legal_content() -> dict:
    """Lädt alle Legal-HTML-Dateien.

    Returns:
        dict: Slug → HTML-Inhalt (str).

    Raises:
        FileNotFoundError: wenn eine der Dateien fehlt — das ist ein harter
        Fehler, denn ohne die Texte dürfen die Seiten nicht seeden.
    """
    content = {}
    for slug, filename in LEGAL_FILES.items():
        path = LEGAL_CONTENT_DIR / filename
        if not path.exists():
            raise FileNotFoundError(
                f"Legal-Content-Datei fehlt: {path} — "
                "das Verzeichnis .legal-content/ muss mit ausgeliefert werden."
            )
        content[slug] = path.read_text(encoding="utf-8").strip()
    return content
