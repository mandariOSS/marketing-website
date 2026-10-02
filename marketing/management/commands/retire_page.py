"""
Management Command: Zieht eine Seite idempotent zurück.

Für Seiten, die bei einem Umbau wegfallen (z. B. /blog/ → /releases/,
/ueber-uns/ → /unternehmen/). Der Befehl

1. zieht die Seite und alle ihre Unterseiten zurück (unpublish – die Seite
   bleibt im CMS erhalten und lässt sich jederzeit wieder veröffentlichen),
2. legt eine dauerhafte Weiterleitung (301) vom alten Pfad auf das Ziel an
   oder korrigiert eine vorhandene,
3. prüft per Anfrage an die Anwendung, dass der alte Pfad wirklich mit 301 auf
   das Ziel zeigt.

Mehrfaches Ausführen ändert nichts mehr („unverändert“). Interne Ziele müssen
existieren (Wagtail-Seite oder Django-Route) – sonst bricht der Befehl ab, bevor
er etwas verändert. Neue Zielseiten deshalb vorher mit `setup_initial_pages`
anlegen.

Usage:
    python manage.py retire_page /blog/ --redirect /releases/
    python manage.py retire_page ueber-uns --redirect /unternehmen/
    python manage.py retire_page /altes-angebot/ --redirect https://example.org/ --dry-run
"""

from __future__ import annotations

from urllib.parse import urlsplit

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from django.urls import Resolver404, resolve
from wagtail.contrib.redirects.models import Redirect
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = (
        "Zieht eine Seite samt Unterseiten zurück (unpublish) und legt eine dauerhafte "
        "Weiterleitung auf das Ziel an. Idempotent."
    )

    def add_arguments(self, parser):
        parser.add_argument("page", help="Pfad ('/blog/') oder Slug ('blog') der zurückzuziehenden Seite")
        parser.add_argument(
            "--redirect",
            required=True,
            help="Ziel der Weiterleitung: Pfad ('/releases/') oder absolute URL ('https://…')",
        )
        parser.add_argument("--dry-run", action="store_true", help="Nur anzeigen, was passieren würde")

    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        site = Site.objects.select_related("root_page").filter(is_default_site=True).first()
        if site is None:
            raise CommandError("Keine Standard-Site gefunden – zuerst `setup_initial_pages` ausführen.")
        home = site.root_page

        page, old_path = self._find_page(home, options["page"])
        target_page, target = self._resolve_target(home, options["redirect"])

        if page is not None and page.pk == home.pk:
            raise CommandError("Die Startseite kann nicht zurückgezogen werden.")
        if Redirect.normalise_path(old_path) == Redirect.normalise_path(urlsplit(target).path) and not urlsplit(
            target
        ).netloc:
            raise CommandError(f"Weiterleitung {old_path} → {target} würde auf sich selbst zeigen.")
        if page is not None and target_page is not None and target_page.path.startswith(page.path):
            raise CommandError(f"Ziel {target} liegt unterhalb der zurückzuziehenden Seite {old_path}.")

        prefix = "[Probelauf] " if dry_run else ""
        self.stdout.write(f"{prefix}Seite {old_path} zurückziehen, Weiterleitung → {target}")

        self._unpublish(home, page, old_path, dry_run, prefix)
        self._ensure_redirect(old_path, target_page, target, dry_run, prefix)

        if dry_run:
            self.stdout.write(f"{prefix}Keine Änderung geschrieben.")
            return
        self._verify(old_path, target)

    # ── Seite finden ────────────────────────────────────────────────────

    def _find_page(self, home, identifier):
        identifier = identifier.strip()
        if identifier.startswith("/"):
            if not identifier.strip("/"):
                return home.specific, "/"
            path = "/" + identifier.strip("/") + "/"
            url_path = home.url_path + path.lstrip("/")
            page = Page.objects.filter(url_path=url_path).first()
            return (page.specific if page else None), path

        slug = identifier.strip("/")
        matches = list(Page.objects.descendant_of(home).filter(slug=slug))
        if len(matches) > 1:
            paths = ", ".join(self._relative_path(home, match) for match in matches)
            raise CommandError(f"Slug '{slug}' ist mehrdeutig ({paths}) – bitte den Pfad angeben.")
        if matches:
            return matches[0].specific, self._relative_path(home, matches[0])
        # Seite existiert nicht (mehr): nur die Weiterleitung auf Seitenebene sicherstellen.
        return None, f"/{slug}/"

    @staticmethod
    def _relative_path(home, page):
        return "/" + page.url_path[len(home.url_path):]

    # ── Ziel prüfen ─────────────────────────────────────────────────────

    def _resolve_target(self, home, target):
        target = target.strip()
        parts = urlsplit(target)
        if parts.scheme in ("http", "https") and parts.netloc:
            return None, target
        if not target.startswith("/"):
            raise CommandError(f"Ziel '{target}' muss ein Pfad (/…/) oder eine absolute URL sein.")

        path = parts.path if parts.path.endswith("/") else parts.path + "/"
        url_path = home.url_path + path.lstrip("/")
        page = Page.objects.filter(url_path=url_path).first()
        if page is not None:
            if not page.live:
                raise CommandError(f"Zielseite {path} ist nicht veröffentlicht.")
            if parts.fragment:
                # Wagtail-Weiterleitungen auf Seiten verwerfen Anker – mit Anker als Link speichern.
                return None, f"{path}#{parts.fragment}"
            return page.specific, path

        try:
            match = resolve(path)
        except Resolver404:
            match = None
        if match is not None and match.url_name != "wagtail_serve":
            return None, target
        raise CommandError(
            f"Ziel {path} existiert nicht (weder Wagtail-Seite noch Django-Route) – "
            "zuerst `python manage.py setup_initial_pages` ausführen."
        )

    # ── Zurückziehen ────────────────────────────────────────────────────

    def _unpublish(self, home, page, old_path, dry_run, prefix):
        if page is None:
            self.stdout.write(f"  {prefix}Seite {old_path} existiert nicht – nur die Weiterleitung wird geprüft.")
            return
        live = [page] if page.live else []
        live += list(page.get_descendants().live().specific())
        if not live:
            self.stdout.write(f"  {prefix}{old_path} ist bereits zurückgezogen – unverändert.")
            return
        for item in live:
            if not dry_run:
                item.unpublish()
            self.stdout.write(self.style.SUCCESS(
                f"  {prefix}zurückgezogen: {item.title} ({self._relative_path(home, item)})"
            ))

    # ── Weiterleitung ───────────────────────────────────────────────────

    def _ensure_redirect(self, old_path, target_page, target, dry_run, prefix):
        normalised = Redirect.normalise_path(old_path)
        existing = Redirect.objects.filter(old_path=normalised, site__isnull=True).first()
        wanted_link = "" if target_page is not None else target

        if existing is not None:
            same_target = (
                existing.redirect_page_id == (target_page.pk if target_page else None)
                and (existing.redirect_link or "") == wanted_link
                and existing.is_permanent
            )
            if same_target:
                self.stdout.write(f"  {prefix}Weiterleitung {old_path} → {target} vorhanden – unverändert.")
                return
            self.stdout.write(self.style.WARNING(
                f"  {prefix}Weiterleitung {old_path} zeigte auf {existing.link} – wird auf {target} gesetzt."
            ))
        else:
            self.stdout.write(self.style.SUCCESS(f"  {prefix}Weiterleitung {old_path} → {target} angelegt."))
            existing = Redirect(old_path=normalised, site=None)

        if dry_run:
            return
        existing.redirect_page = target_page
        existing.redirect_link = wanted_link
        existing.is_permanent = True
        existing.save()

    # ── Prüfung ─────────────────────────────────────────────────────────

    def _verify(self, old_path, target):
        site_url = urlsplit(getattr(settings, "SITE_URL", "") or "")
        host = site_url.netloc or "localhost"
        response = Client(HTTP_HOST=host).get(old_path, secure=site_url.scheme == "https")
        location = response.get("Location", "")
        expected = self._comparable(target)
        if response.status_code != 301 or self._comparable(location) != expected:
            raise CommandError(
                f"Prüfung fehlgeschlagen: {old_path} liefert HTTP {response.status_code}"
                f"{' → ' + location if location else ''}, erwartet 301 → {target}."
            )
        self.stdout.write(self.style.SUCCESS(f"  geprüft: {old_path} → 301 {location}"))

    @staticmethod
    def _comparable(url):
        """Interne Ziele relativ vergleichen (mit oder ohne Host), externe vollständig."""
        parts = urlsplit(url)
        site = urlsplit(getattr(settings, "SITE_URL", "") or "")
        internal = not parts.netloc or parts.netloc == site.netloc
        fragment = f"#{parts.fragment}" if parts.fragment else ""
        if internal:
            return (parts.path or "/") + fragment
        return url
