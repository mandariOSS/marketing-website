"""
Management Command: Wendet die Seed-Definition für EINEN Slug erneut an.

Gedacht für Deployments gegen eine bestehende Datenbank: `setup_initial_pages`
und `migrate_pages_to_streamfield` überspringen Seiten, die bereits Inhalt
haben — dieses Command aktualisiert gezielt eine einzelne Live-Seite auf den
aktuellen Stand der Seed-Definition im Repo.

Quellen (in dieser Reihenfolge geprüft):
  1. StreamField-Definitionen aus `migrate_pages_to_streamfield`
     (MarketingPage.body bzw. LegalPage.body_stream)
  2. Rechtstexte aus `.legal-content/*.html` via `marketing.legal_content`
     (LegalPage.body, RichText)

Usage:
    python manage.py refresh_seeded_page <slug>            # nur wenn leer
    python manage.py refresh_seeded_page <slug> --force    # überschreibt Live-Inhalt

Beispiele:
    python manage.py refresh_seeded_page trust --force     # Trust Center neu seeden
    python manage.py refresh_seeded_page avv --force       # AVV-Text aus .legal-content/
"""

from __future__ import annotations

from django.core.management.base import BaseCommand, CommandError
from wagtail.blocks import StreamValue


class Command(BaseCommand):
    help = "Wendet die Seed-Definition für einen einzelnen Page-Slug erneut an (Live-Update nach Deploys)."

    def add_arguments(self, parser):
        parser.add_argument("slug", type=str, help="Slug der Seite, z.B. 'trust' oder 'avv'")
        parser.add_argument(
            "--force",
            action="store_true",
            help="Überschreibt vorhandenen Inhalt (ohne --force werden nur leere Seiten befüllt)",
        )

    def handle(self, *args, **options):
        from marketing.blocks import MarketingStreamBlock
        from marketing.legal_content import LEGAL_FILES, load_legal_content
        from marketing.management.commands.migrate_pages_to_streamfield import (
            get_legal_definitions,
            get_marketing_definitions,
        )
        from marketing.models import LegalPage, MarketingPage

        slug = options["slug"].strip().strip("/")
        force = options["force"]

        marketing_defs = get_marketing_definitions()
        legal_defs = get_legal_definitions()

        if slug in marketing_defs:
            self._refresh_streamfield(
                slug, marketing_defs[slug], MarketingPage, "body",
                MarketingStreamBlock(), force,
            )
        elif slug in legal_defs:
            self._refresh_streamfield(
                slug, legal_defs[slug], LegalPage, "body_stream",
                MarketingStreamBlock(), force,
            )
        elif slug in LEGAL_FILES:
            self._refresh_legal_richtext(slug, load_legal_content()[slug], LegalPage, force)
        else:
            known = sorted(set(marketing_defs) | set(legal_defs) | set(LEGAL_FILES))
            raise CommandError(
                f"Keine Seed-Definition für Slug '{slug}' gefunden.\n"
                f"Verfügbare Slugs: {', '.join(known)}"
            )

    # ── StreamField-Seiten (MarketingPage.body / LegalPage.body_stream) ──

    def _refresh_streamfield(self, slug, blocks_data, page_class, body_field, stream_block, force):
        page = page_class.objects.filter(slug=slug).first()
        if not page:
            raise CommandError(
                f"{page_class.__name__} mit Slug '{slug}' existiert nicht in der DB — "
                "zuerst `python manage.py setup_initial_pages` ausführen."
            )

        existing = getattr(page, body_field)
        if existing and len(list(existing)) > 0 and not force:
            self.stdout.write(self.style.WARNING(
                f"  ◯ {slug}/ hat bereits {len(list(existing))} Blöcke — "
                "nutze --force, um die Seed-Definition erneut anzuwenden."
            ))
            return

        setattr(page, body_field, StreamValue(stream_block, blocks_data, is_lazy=False))
        # Seed-Definitionen werden über die Standard-Templates gerendert —
        # ein evtl. gesetztes custom_template würde sie verdecken.
        page.custom_template = ""

        # Titel / SEO-Metadaten aus dem Seed mitziehen (Slug bleibt stabil) —
        # sonst behalten Live-Seiten nach Umbenennungen den alten Titel.
        from marketing.management.commands.setup_initial_pages import MARKETING_PAGE_META

        meta = next((m for m in MARKETING_PAGE_META if m["slug"] == slug), None)
        if meta:
            page.title = meta.get("title", page.title)
            page.seo_title = meta.get("seo_title", page.seo_title)
            page.search_description = meta.get("search_description", page.search_description)

        page.save()
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {slug}/ neu geseedet ({len(blocks_data)} Blöcke, veröffentlicht)"
        ))

    # ── Rechtstexte aus .legal-content/ (LegalPage.body, RichText) ──────

    def _refresh_legal_richtext(self, slug, html, page_class, force):
        page = page_class.objects.filter(slug=slug).first()
        if not page:
            raise CommandError(
                f"LegalPage mit Slug '{slug}' existiert nicht in der DB — "
                "zuerst `python manage.py setup_initial_pages` ausführen."
            )

        if page.body and not force:
            self.stdout.write(self.style.WARNING(
                f"  ◯ {slug}/ hat bereits Inhalt — "
                "nutze --force, um den Text aus .legal-content/ erneut anzuwenden."
            ))
            return

        page.body = html
        # Rechtstexte aus .legal-content/ werden über legal_page.html
        # gerendert; body_stream würde das Template umschalten und den
        # authoritative Text verdecken (siehe migrate_pages_to_streamfield).
        page.save()
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {slug}/ aus .legal-content/{slug}.html aktualisiert (veröffentlicht)"
        ))
