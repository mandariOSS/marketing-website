# SPDX-License-Identifier: AGPL-3.0-or-later
"""
Erzeugt die PDF-Fassung des Service Level Agreement reproduzierbar aus der
zentralen Quelle `marketing/sla_content.py` (dieselbe Quelle wie /sla/ und
/sla/druck/).

Ablauf: Django-Template `marketing/sla_print.html` rendern → temporäre
HTML-Datei → Chromium-basierter Browser (Chrome/Edge/Chromium) im Headless-
Modus druckt nach PDF. Es wird bewusst keine zusätzliche Python-Abhängigkeit
(WeasyPrint, ReportLab, …) eingeführt; ein Browser ist auf Entwicklungs-
rechnern ohnehin vorhanden.

Aufruf (aus dem Repo-Root, ohne laufende Datenbank):

    python scripts/build_sla_pdf.py                  # → static/downloads/mandari-sla-v<version>.pdf
    python scripts/build_sla_pdf.py --out /tmp/x.pdf
    python scripts/build_sla_pdf.py --browser "C:/Program Files/Google/Chrome/Application/chrome.exe"
    python scripts/build_sla_pdf.py --html-only      # nur HTML schreiben (Debug)

Bei Änderungen am SLA: Version/Datum in marketing/sla_content.py anheben,
Skript ausführen, neue PDF zusammen mit dem Seed committen.
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent

BROWSER_CANDIDATES = [
    # Umgebungsvariable hat Vorrang
    os.environ.get("SLA_PDF_BROWSER", ""),
    # Windows
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    # Linux / macOS
    "google-chrome",
    "google-chrome-stable",
    "chromium",
    "chromium-browser",
    "microsoft-edge",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
]


def find_browser(explicit: str | None) -> str | None:
    for candidate in ([explicit] if explicit else []) + BROWSER_CANDIDATES:
        if not candidate:
            continue
        if Path(candidate).is_file():
            return candidate
        found = shutil.which(candidate)
        if found:
            return found
    return None


def render_html() -> tuple[str, str]:
    """Rendert das Druck-Template über Django (ohne Datenbankzugriff)."""
    sys.path.insert(0, str(REPO_ROOT))
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "website.settings")
    # Keine Datenbank nötig — aber settings.py parst die URL; SQLite-Dummy
    # verhindert, dass ein fehlender Postgres den Import stört.
    os.environ.setdefault("WEBSITE_DATABASE_URL", "sqlite:///:memory:")
    os.environ.setdefault("DEBUG", "true")
    # Links im PDF müssen auf die öffentliche Site zeigen, nicht auf localhost.
    os.environ.setdefault("SITE_URL", "https://mandari.de")

    import django

    django.setup()

    from django.template.loader import render_to_string

    from marketing.sla_content import SLA_VERSION
    from marketing.views import sla_print_context

    logo = (REPO_ROOT / "static" / "brand" / "mandari-logo-print.png").resolve()
    context = sla_print_context(logo_url=logo.as_uri())
    return render_to_string("marketing/sla_print.html", context), SLA_VERSION


def main() -> int:
    parser = argparse.ArgumentParser(description="PDF-Fassung des SLA erzeugen")
    parser.add_argument(
        "--out", type=Path, help="Zielpfad der PDF (Default: static/downloads/mandari-sla-v<version>.pdf)"
    )
    parser.add_argument("--browser", help="Pfad zu Chrome/Edge/Chromium (Default: automatisch suchen)")
    parser.add_argument("--html-only", action="store_true", help="Nur die HTML-Datei neben die PDF schreiben")
    args = parser.parse_args()

    html, version = render_html()

    out = args.out or (REPO_ROOT / "static" / "downloads" / f"mandari-sla-v{version}.pdf")
    out.parent.mkdir(parents=True, exist_ok=True)

    if args.html_only:
        html_path = out.with_suffix(".html")
        html_path.write_text(html, encoding="utf-8")
        print(f"HTML geschrieben: {html_path}")
        return 0

    browser = find_browser(args.browser)
    if not browser:
        print(
            "Kein Chromium-basierter Browser gefunden. Pfad per --browser oder "
            "SLA_PDF_BROWSER angeben — oder /sla/druck/ im Browser öffnen und "
            "manuell als PDF speichern.",
            file=sys.stderr,
        )
        return 2

    with tempfile.TemporaryDirectory() as tmp:
        html_path = Path(tmp) / "sla.html"
        html_path.write_text(html, encoding="utf-8")
        cmd = [
            browser,
            "--headless=new",
            "--disable-gpu",
            "--no-sandbox",
            "--no-pdf-header-footer",
            "--allow-file-access-from-files",
            f"--user-data-dir={Path(tmp) / 'profile'}",
            f"--print-to-pdf={out}",
            html_path.as_uri(),
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
        if result.returncode != 0 or not out.exists():
            print(result.stdout, result.stderr, file=sys.stderr)
            print(f"PDF-Erzeugung fehlgeschlagen (Exit {result.returncode})", file=sys.stderr)
            return 1

    print(f"PDF geschrieben: {out} ({out.stat().st_size // 1024} KB, Version {version})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
