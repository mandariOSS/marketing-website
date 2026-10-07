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
    python manage.py refresh_seeded_page <slug> --nur-meta # nur Titel und SEO-Felder, Inhalt bleibt
    python manage.py refresh_seeded_page <slug> --nur-meta --probelauf  # zeigt alt → neu, speichert nichts

`--force` ersetzt den ganzen Inhalt der Seite durch die Seed-Definition (im CMS
geänderte Blöcke gehen dabei verloren). Sollen nur Titel, SEO-Titel und
Meta-Description nachgezogen werden (z. B. nach Änderungen in
`marketing/seo_texte.py`), genügt `--nur-meta`: Der Befehl setzt `title`,
`seo_title` und `search_description` aus dem Seed, lässt Inhalt und Vorlage
unangetastet und veröffentlicht das als neue Revision. Seiten mit einem
unveröffentlichten Entwurf im CMS überspringt er mit einer Warnung, damit der
Entwurf nicht verdeckt wird. Die Ausgabe nennt je geändertem Feld den alten und
den neuen Wert; `--probelauf` (auch `--dry-run`) zeigt das vorab, ohne zu
speichern. So fällt auf, wenn etwa ein im CMS umbenannter Seitentitel auf den
Seed-Stand zurückginge.

Beispiele:
    python manage.py refresh_seeded_page trust --force       # Trust Center neu seeden
    python manage.py refresh_seeded_page avv --force         # AVV-Text aus .legal-content/
    python manage.py refresh_seeded_page startseite --force  # Titel/SEO der Startseite

Die Startseite (`startseite`) hat keine StreamField-Inhalte (Template
`marketing/landing.html`); der Befehl zieht dort nur Titel und SEO-Felder aus
`setup_initial_pages.HOME_PAGE_META` nach.
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
        parser.add_argument(
            "--nur-meta",
            action="store_true",
            dest="nur_meta",
            help="Nur Titel, SEO-Titel und Meta-Description aus dem Seed übernehmen; der Inhalt bleibt unverändert",
        )
        parser.add_argument(
            "--probelauf",
            "--dry-run",
            action="store_true",
            dest="probelauf",
            help="Nur mit --nur-meta: zeigt je Feld den alten und den neuen Wert, speichert nichts",
        )

    def handle(self, *args, **options):
        from marketing.blocks import MarketingStreamBlock
        from marketing.legal_content import LEGAL_FILES, load_legal_content
        from marketing.management.commands.migrate_pages_to_streamfield import (
            get_legal_definitions,
            get_marketing_definitions,
            get_release_definitions,
        )
        from marketing.models import LegalPage, MarketingPage

        slug = options["slug"].strip().strip("/")
        force = options["force"]

        if options["probelauf"] and not options["nur_meta"]:
            raise CommandError("--probelauf gibt es nur zusammen mit --nur-meta.")
        if options["nur_meta"]:
            if force:
                raise CommandError("--nur-meta und --force schließen sich aus.")
            self._refresh_meta_only(slug, probelauf=options["probelauf"])
            return

        # Kontaktseite (eigener Seitentyp ohne StreamField): nur Titel und SEO-Felder
        if slug == "kontakt":
            self._refresh_contact_meta(force)
            return

        marketing_defs = get_marketing_definitions()
        legal_defs = get_legal_definitions()
        release_defs = get_release_definitions()

        if slug == "startseite":
            self._refresh_home(force)
        elif slug in marketing_defs:
            self._refresh_streamfield(
                slug, marketing_defs[slug], MarketingPage, "body",
                MarketingStreamBlock(), force,
            )
        elif slug in legal_defs:
            self._refresh_streamfield(
                slug, legal_defs[slug], LegalPage, "body_stream",
                MarketingStreamBlock(), force,
            )
        elif slug in release_defs:
            self._refresh_release(slug, release_defs[slug], force)
        elif slug in LEGAL_FILES:
            self._refresh_legal_richtext(slug, load_legal_content()[slug], LegalPage, force)
        else:
            known = sorted(
                set(marketing_defs) | set(legal_defs) | set(release_defs) | set(LEGAL_FILES) | {"startseite"}
            )
            raise CommandError(
                f"Keine Seed-Definition für Slug '{slug}' gefunden.\n"
                f"Verfügbare Slugs: {', '.join(known)}"
            )

    # ── Nur Titel und SEO-Felder (--nur-meta) ───────────────────────────

    META_FELDER = ("title", "seo_title", "search_description")

    def _refresh_meta_only(self, slug, probelauf=False):
        """Titel und SEO-Felder aus dem Seed übernehmen, ohne Inhalt, Vorlage oder Entwürfe anzurühren.

        Mit ``probelauf`` nur anzeigen, was sich ändern würde (alter und neuer Wert je Feld).
        """
        from marketing.management.commands.setup_initial_pages import (
            CONTACT_PAGE_META,
            HOME_PAGE_META,
            MARKETING_PAGE_META,
        )
        from marketing.models import ContactPage, HomePage, MarketingPage

        if slug == "startseite":
            page, meta = HomePage.objects.first(), HOME_PAGE_META
        elif slug == "kontakt":
            page, meta = ContactPage.objects.first(), CONTACT_PAGE_META
        else:
            meta = next((m for m in MARKETING_PAGE_META if m["slug"] == slug), None)
            if meta is None:
                known = sorted({m["slug"] for m in MARKETING_PAGE_META} | {"startseite", "kontakt"})
                raise CommandError(
                    f"Keine Metadaten für Slug '{slug}' im Seed (--nur-meta).\n"
                    f"Verfügbare Slugs: {', '.join(known)}"
                )
            page = MarketingPage.objects.filter(slug=slug).first()
        if page is None:
            raise CommandError(
                f"Seite '{slug}' existiert nicht in der DB — zuerst `python manage.py setup_initial_pages` ausführen."
            )

        changed = {
            field: meta[field]
            for field in self.META_FELDER
            if field in meta and getattr(page, field) != meta[field]
        }
        if not changed:
            self.stdout.write(f"  ◯ {slug}/: Titel und SEO-Felder sind bereits auf dem Stand des Seeds.")
            return
        # Je Feld „alt → neu“: Ein im CMS umbenannter Seitentitel fällt so vor bzw. nach dem Lauf auf.
        aenderungen = "\n".join(
            f"      {field}: „{getattr(page, field)}“ → „{changed[field]}“" for field in sorted(changed)
        )
        if page.has_unpublished_changes:
            self.stdout.write(self.style.WARNING(
                f"  ◯ {slug}/ hat einen unveröffentlichten Entwurf — übersprungen, damit er erhalten bleibt. "
                f"Felder im CMS anpassen: {', '.join(sorted(changed))}"
            ))
            self.stdout.write(aenderungen)
            return
        if probelauf:
            self.stdout.write(self.style.WARNING(
                f"  ◯ {slug}/ (Probelauf, nichts gespeichert): würde {', '.join(sorted(changed))} setzen"
            ))
            self.stdout.write(aenderungen)
            return

        for field, value in changed.items():
            setattr(page, field, value)
        page.save()
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ {slug}/: {', '.join(sorted(changed))} aktualisiert, Inhalt unverändert (veröffentlicht)"
        ))
        self.stdout.write(aenderungen)

    # ── Startseite (HomePage — nur Titel und SEO-Felder) ────────────────

    def _refresh_home(self, force):
        from marketing.management.commands.setup_initial_pages import HOME_PAGE_META
        from marketing.models import HomePage

        home = HomePage.objects.first()
        if not home:
            raise CommandError("Keine Startseite in der DB — zuerst `python manage.py setup_initial_pages` ausführen.")

        changed = {k: v for k, v in HOME_PAGE_META.items() if getattr(home, k) != v}
        if not changed:
            self.stdout.write("  ◯ Startseite ist bereits auf dem Stand der Seed-Definition.")
            return
        if not force:
            self.stdout.write(self.style.WARNING(
                f"  ◯ Startseite weicht ab ({', '.join(sorted(changed))}) — nutze --force, um sie zu überschreiben."
            ))
            return

        for field, value in changed.items():
            setattr(home, field, value)
        home.save()
        home.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ Startseite aktualisiert ({', '.join(sorted(changed))}, veröffentlicht)"
        ))

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

        from marketing.management.commands.setup_initial_pages import (
            MARKETING_PAGE_META,
            seeded_custom_template,
        )

        setattr(page, body_field, StreamValue(stream_block, blocks_data, is_lazy=False))
        # Seed-Definitionen werden über die Standard-Templates gerendert – außer der
        # Seed nennt ein eigenes (z. B. company/unternehmen.html); ein anderes, früher
        # gesetztes custom_template würde sie verdecken.
        page.custom_template = seeded_custom_template(slug)

        # Titel / SEO-Metadaten aus dem Seed mitziehen (Slug bleibt stabil) —
        # sonst behalten Live-Seiten nach Umbenennungen den alten Titel.
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

    # ── Kontaktseite (ContactPage — nur Titel und SEO-Felder) ───────────

    def _refresh_contact_meta(self, force):
        """`refresh_seeded_page kontakt --force`: Titel und SEO-Felder aus CONTACT_PAGE_META."""
        from marketing.management.commands.setup_initial_pages import CONTACT_PAGE_META
        from marketing.models import ContactPage

        page = ContactPage.objects.first()
        if not page:
            raise CommandError(
                "Keine Kontaktseite in der DB — zuerst `python manage.py setup_initial_pages` ausführen."
            )
        if not force:
            self.stdout.write(self.style.WARNING(
                "  ◯ kontakt/ existiert — nutze --force, um Titel und SEO-Felder aus dem Seed zu übernehmen."
            ))
            return
        for field in ("title", "seo_title", "search_description"):
            setattr(page, field, CONTACT_PAGE_META[field])
        page.save()
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS("  ✓ kontakt/ Titel und SEO-Felder aktualisiert (veröffentlicht)"))

    # ── Release-Seiten (blog.ReleasePage — Meta + body) ─────────────────

    def _refresh_release(self, slug, definition, force):
        from datetime import date

        from wagtail.blocks import StreamValue

        from blog.models import ReleasePage
        from marketing.blocks import MarketingStreamBlock

        page = ReleasePage.objects.filter(slug=slug).first()
        if not page:
            raise CommandError(
                f"ReleasePage mit Slug '{slug}' existiert nicht in der DB — "
                "zuerst `python manage.py setup_initial_pages` ausführen."
            )

        if page.body and len(list(page.body)) > 0 and not force:
            self.stdout.write(self.style.WARNING(
                f"  ◯ {slug}/ hat bereits {len(list(page.body))} Blöcke — "
                "nutze --force, um die Seed-Definition erneut anzuwenden."
            ))
            return

        meta = dict(definition["meta"])
        page.release_date = date.fromisoformat(meta.pop("release_date"))
        for field, value in meta.items():
            setattr(page, field, value)
        page.body = StreamValue(MarketingStreamBlock(), definition["blocks"], is_lazy=False)
        page.save()
        page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS(
            f"  ✓ Release {slug}/ neu geseedet ({len(definition['blocks'])} Blöcke, veröffentlicht)"
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
