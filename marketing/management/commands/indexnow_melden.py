"""
Adressen der Website an IndexNow melden (marketing/indexnow.py).

Das Veröffentlichen und Zurückziehen von Seiten meldet von selbst. Dieser Befehl ist für den Anfang (``--alle``:
alle Adressen der Sitemap einmal) und für einzelne Adressen:

    python manage.py indexnow_melden --alle --probelauf
    python manage.py indexnow_melden /ratsinformationssystem/ /kommunen/
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.core.management.base import BaseCommand, CommandError

from marketing import indexnow, seo
from marketing.sitemaps import FesteSeitenSitemap, MandariSitemap


class Command(BaseCommand):
    help = "Adressen der Website an IndexNow melden (--alle: alle Adressen der Sitemap)."

    def add_arguments(self, parser):
        parser.add_argument("adressen", nargs="*", help="Pfade (/kommunen/) oder Adressen auf SITE_URL")
        parser.add_argument("--alle", action="store_true", help="alle Adressen der Sitemap")
        parser.add_argument("--probelauf", action="store_true", help="nur anzeigen, nichts melden")

    def handle(self, *args, **options):
        adressen = [seo.absolute_url(a) if a.startswith("/") else a for a in options["adressen"]]
        if options["alle"]:
            adressen += self._sitemap()
        if not adressen:
            raise CommandError("Adressen oder --alle angeben.")
        if not indexnow.schluessel():
            raise CommandError("INDEXNOW_KEY fehlt oder genügt nicht dem Protokoll (8–128 Zeichen A–Z, a–z, 0–9, -).")

        eigene = indexnow.eigene(adressen)
        fremd = len(dict.fromkeys(adressen)) - len(eigene)
        if fremd:
            self.stdout.write(self.style.WARNING(f"{fremd} Adressen liegen nicht auf {seo.site_url()} und entfallen."))
        if options["probelauf"]:
            for adresse in eigene:
                self.stdout.write(adresse)
            self.stdout.write(f"[Probelauf] {len(eigene)} Adressen, nichts gemeldet.")
            return
        angenommen = indexnow.melden(eigene)
        self.stdout.write(f"{angenommen} von {len(eigene)} Adressen angenommen.")
        if angenommen < len(eigene):
            raise CommandError("Nicht alle Adressen angenommen, siehe Log (Schlüsseldatei erreichbar?).")

    @staticmethod
    def _sitemap():
        sitemap = MandariSitemap()
        seiten = [
            seo.absolute_url(urlsplit(info["location"]).path)
            for seite in sitemap.items()
            for info in seite.get_sitemap_urls(None)
        ]
        # Feste Django-Seiten aus der Sitemap (heute /ingestor/)
        feste = FesteSeitenSitemap()
        return seiten + [seo.absolute_url(feste.location(name)) for name in feste.items()]
