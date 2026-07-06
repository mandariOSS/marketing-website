"""
Management Command: Erstellt den initialen Wagtail Page-Tree.

Idempotent — kann beliebig oft ausgeführt werden.
Erstellt nur Seiten, die noch nicht existieren.

Usage:
    python manage.py setup_initial_pages
"""

from django.core.management.base import BaseCommand
from django.template import TemplateDoesNotExist
from django.template.loader import get_template as load_template
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = "Erstellt die initiale Seitenstruktur für die Marketing-Website"

    def handle(self, *args, **options):
        from blog.models import BlogIndexPage, ReleaseIndexPage
        from marketing.legal_content import load_legal_content
        from marketing.models import ContactPage, HomePage, LegalPage, MarketingPage

        # Wagtail Root Page holen
        root = Page.objects.filter(depth=1).first()
        if not root:
            self.stderr.write(self.style.ERROR("Keine Wagtail Root Page gefunden. Wurden Migrationen ausgeführt?"))
            return

        # Default "Welcome to your new Wagtail site!" entfernen
        welcome = Page.objects.filter(depth=2, title="Welcome to your new Wagtail site!").first()

        # HomePage erstellen (oder finden)
        home = HomePage.objects.first()
        if not home:
            home = HomePage(
                title="Mandari",
                slug="mandari",
                subtitle="Kommunalpolitische Transparenz für Deutschland",
                seo_title="Mandari – Kommunalpolitische Transparenz für Deutschland",
                search_description=(
                    "Mandari macht kommunalpolitische Entscheidungen transparent und zugänglich. "
                    "Open Source unter AGPL-3.0."
                ),
                show_in_menus=True,
            )
            root.add_child(instance=home)
            home.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  Startseite erstellt"))
        else:
            self.stdout.write("  Startseite existiert bereits")

        # Site-Konfiguration: HomePage als Root setzen
        site = Site.objects.filter(is_default_site=True).first()
        if site:
            if site.root_page_id != home.pk:
                site.root_page = home
                site.save()
                self.stdout.write(self.style.SUCCESS("  Site Root → Startseite"))
        else:
            Site.objects.create(
                hostname="localhost",
                root_page=home,
                is_default_site=True,
                site_name="Mandari",
            )
            self.stdout.write(self.style.SUCCESS("  Site erstellt"))

        # Welcome-Page entfernen (nach Site-Umstellung)
        if welcome:
            welcome.delete()
            self.stdout.write(self.style.SUCCESS("  Welcome-Page entfernt"))

        # ── Marketing-Seiten ──────────────────────────────────────────────

        marketing_pages = [
            # ── Produkt ───────────────────────────────────────────────────
            {
                "title": "Produkt",
                "slug": "produkt",
                "seo_title": "Produkt – Mandari",
                "search_description": "Drei Module für kommunalpolitische Transparenz: Insight, Work und Session.",
            },
            {
                "title": "Preise",
                "slug": "preise",
                "seo_title": "Preise – Mandari",
                "search_description": "Transparente Preisgestaltung. Insight ist kostenlos, Work ab 39,90€/Monat.",
            },
            {
                "title": "Kommunen",
                "slug": "kommunen",
                "seo_title": "Verfügbare Kommunen – Mandari",
                "search_description": "Kommunen, deren Ratsinformationen über Mandari verfügbar sind.",
            },
            {
                "title": "Migration",
                "slug": "migration",
                "seo_title": "Migration vom Alt-RIS – Mandari",
                "search_description": "Wechsel von ALLRIS, regisafe oder Somacos zu Mandari Session. Vier-Schritte-Plan, was mitkommt, Pilot-Konditionen.",
            },
            {
                "title": "Roadmap",
                "slug": "roadmap",
                "seo_title": "Roadmap – Mandari",
                "search_description": "Öffentliche Roadmap und geplante Features.",
            },

            # ── Vertrauen ★ NEU ──────────────────────────────────────────
            # /sicherheit/ wurde in /trust/ integriert (komplette Doppelung)
            {
                "title": "Trust Center",
                "slug": "trust",
                "seo_title": "Trust Center – Sicherheit, DPA, Subprocessoren",
                "search_description": "Komplette Sicherheits- & Vertrauensübersicht: DPA-Download, Subprocessor-Liste, Hosting-Stack, Backup, SLA, Audits.",
            },
            {
                "title": "Transparenzbericht",
                "slug": "transparenz",
                "seo_title": "Transparenzbericht 2026 – Mandari",
                "search_description": "Behördenanfragen, Sicherheitsvorfälle, aktive Kommunen, Finanztransparenz vom Solo-Founder, Open-Source-Beiträge.",
            },
            {
                "title": "Barrierefreiheit",
                "slug": "barrierefreiheit",
                "seo_title": "Erklärung zur Barrierefreiheit – Mandari",
                "search_description": "Pflichterklärung nach BFSG, BITV 2.0, EN 301 549. Konformitätsstand, Feedback, Schlichtungsstelle.",
            },
            {
                "title": "Missbrauch melden",
                "slug": "abuse",
                "seo_title": "Missbrauch melden – Abuse-Kontakte",
                "search_description": "Abuse-Meldestelle für Spam, illegalen Content, Datenschutz, Urheberrecht, Belästigung. DSA- und NetzDG-konform.",
            },

            # ── Community ────────────────────────────────────────────────
            {
                "title": "Open Source",
                "slug": "open-source",
                "seo_title": "Open Source – Mandari",
                "search_description": "Mandari ist Open Source unter AGPL-3.0. Selbst-Hosting möglich.",
            },
            {
                "title": "Mitmachen",
                "slug": "mitmachen",
                "seo_title": "Mitmachen – Mandari",
                "search_description": "Werde Teil der Mandari-Community. Entwicklung, Dokumentation, Übersetzung.",
            },

            # ── Über uns ─────────────────────────────────────────────────
            {
                "title": "Über uns",
                "slug": "ueber-uns",
                "seo_title": "Über uns – Mission, Founder, Werte",
                "search_description": "Mandari ist ein Solo-Projekt von Sven Konopka — Mission, Founder, Werte an einem Ort.",
            },
            {
                "title": "Partner",
                "slug": "partner",
                "seo_title": "Partner – Mandari",
                "search_description": "Partnerschaften mit Kommunen, Fraktionen und zivilgesellschaftlichen Organisationen.",
            },
            {
                "title": "Presse",
                "slug": "presse",
                "seo_title": "Presse – Mandari",
                "search_description": "Pressematerial und Kontakt für Journalist:innen.",
            },
            # /faq/ wurde aufgelöst — Page-spezifische FAQs sind direkt in
            # /preise/, /kontakt/, /migration/ integriert

            # Note: /status/ und /sicherheit/disclosure/ sind KEINE Wagtail-Pages —
            # sie werden von Django-Views (`status_view`, `security_disclosure_view`)
            # in website/urls.py BEFORE dem Wagtail catch-all gerendert.
            # Note: /loesungen/, /team/, /danksagungen/ wurden in Produkt /
            # Über-uns / Open-Source konsolidiert — werden via Django-Redirects
            # in website/urls.py auf die neuen URLs umgeleitet.
        ]

        # ── Konsolidierung: gemergte Pages aus DB entfernen ────────────────
        # Phase 1 (vorher): loesungen → produkt, team → ueber-uns, danksagungen → open-source
        # Phase 2 (jetzt):  sicherheit → trust, faq → kontakt
        consolidated_slugs = ["loesungen", "team", "danksagungen", "sicherheit", "faq"]
        for slug in consolidated_slugs:
            page = MarketingPage.objects.filter(slug=slug).first()
            if page:
                page.delete()
                self.stdout.write(self.style.WARNING(f"  {slug}/ entfernt (konsolidiert)"))

        # Note: custom_template wird bewusst NICHT mehr geseedet — die alten
        # Spezial-Templates (marketing/produkt.html, …) existieren in diesem
        # Repo nicht. Inhalte kommen aus dem StreamField-Seed
        # (`migrate_pages_to_streamfield`), gerendert über marketing_page.html.
        for page_data in marketing_pages:
            slug = page_data.pop("slug")
            show_in_menus = page_data.pop("show_in_menus", True)

            if MarketingPage.objects.filter(slug=slug).exists():
                self.stdout.write(f"  {page_data['title']} existiert bereits")
                continue

            page = MarketingPage(
                slug=slug,
                show_in_menus=show_in_menus,
                **page_data,
            )
            home.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  {page_data['title']} erstellt"))

        # ── Kontaktseite ──────────────────────────────────────────────────

        if not ContactPage.objects.exists():
            contact = ContactPage(
                title="Kontakt",
                slug="kontakt",
                seo_title="Kontakt – Mandari",
                search_description="Kontaktformular und Ansprechpartner.",
                intro="<p>Wir freuen uns über Ihre Nachricht.</p>",
                thank_you_text="<p>Vielen Dank für Ihre Nachricht! Wir melden uns so schnell wie möglich.</p>",
                show_in_menus=True,
            )
            home.add_child(instance=contact)
            contact.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  Kontakt erstellt"))
        else:
            self.stdout.write("  Kontakt existiert bereits")

        # ── Rechtliche Seiten ─────────────────────────────────────────────
        # Impressum / Datenschutz / AGB: Inhalte kommen aus .legal-content/
        # (via marketing/legal_content.py) und landen im RichText-Feld `body`.
        # Gerendert wird über das generische marketing/legal_page.html —
        # kein custom_template, kein hardcodierter Rechtstext in Templates.
        legal_content = load_legal_content()

        legal_pages = [
            {
                "title": "Impressum",
                "slug": "impressum",
                "body": legal_content["impressum"],
            },
            {
                "title": "Datenschutz",
                "slug": "datenschutz",
                "body": legal_content["datenschutz"],
            },
            {
                "title": "AGB",
                "slug": "agb",
                "body": legal_content["agb"],
            },
            {
                "title": "Quellennachweise",
                "slug": "quellen",
                # Inhalt kommt als StreamField-Blöcke aus
                # `migrate_pages_to_streamfield` (body_stream).
                "body": "<p>Quellennachweise und OParl-Quellenverzeichnis.</p>",
            },
        ]

        # Marker der alten Seed-Platzhalter — nur solche Inhalte werden bei
        # bestehenden Seiten überschrieben. Im Wagtail-Admin gepflegte Texte
        # bleiben unangetastet.
        placeholder_marker = "bitte im Wagtail-Admin vervollständigen"

        for page_data in legal_pages:
            slug = page_data.pop("slug")

            existing = LegalPage.objects.filter(slug=slug).first()
            if existing:
                new_body = page_data.get("body", "")
                if new_body and (not existing.body or placeholder_marker in existing.body):
                    existing.body = new_body
                    existing.save()
                    existing.save_revision().publish()
                    self.stdout.write(self.style.SUCCESS(f"  {page_data['title']}: Platzhalter durch Inhalt ersetzt"))
                else:
                    self.stdout.write(f"  {page_data['title']} existiert bereits")
                continue

            page = LegalPage(
                slug=slug,
                show_in_menus=False,
                **page_data,
            )
            home.add_child(instance=page)
            page.save_revision().publish()
            self.stdout.write(self.style.SUCCESS(f"  {page_data['title']} erstellt"))

        # ── Blog ──────────────────────────────────────────────────────────

        if not BlogIndexPage.objects.exists():
            blog = BlogIndexPage(
                title="Blog",
                slug="blog",
                seo_title="Blog – Mandari",
                search_description="Neuigkeiten, Tutorials und Community-Beiträge rund um Mandari.",
                intro="<p>Neuigkeiten und Einblicke aus der Entwicklung von Mandari.</p>",
                show_in_menus=True,
            )
            home.add_child(instance=blog)
            blog.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  Blog erstellt"))
        else:
            self.stdout.write("  Blog existiert bereits")

        # ── Releases ──────────────────────────────────────────────────────

        if not ReleaseIndexPage.objects.exists():
            releases = ReleaseIndexPage(
                title="Releases",
                slug="releases",
                seo_title="Releases – Mandari",
                search_description="Versionshistorie und Changelogs.",
                intro="<p>Alle Mandari-Releases mit Changelogs und Release-Notes.</p>",
                show_in_menus=True,
            )
            home.add_child(instance=releases)
            releases.save_revision().publish()
            self.stdout.write(self.style.SUCCESS("  Releases erstellt"))
        else:
            self.stdout.write("  Releases existiert bereits")

        # ── Reparatur: verwaiste custom_template-Verweise entfernen ──────
        # Ältere Seed-Versionen setzten custom_template auf Spezial-Templates
        # (z.B. marketing/impressum.html), die in diesem Repo nicht existieren.
        # Solche Seiten würden beim Rendern mit TemplateDoesNotExist crashen —
        # deshalb wird der Verweis idempotent entfernt, wenn das Template
        # nicht auflösbar ist. Danach greifen die Standard-Templates
        # (marketing_page.html / legal_page.html / legal_streamfield_page.html).
        for model in (MarketingPage, LegalPage):
            for page in model.objects.exclude(custom_template=""):
                try:
                    load_template(page.custom_template)
                except TemplateDoesNotExist:
                    self.stdout.write(self.style.WARNING(
                        f"  {page.slug}/: custom_template '{page.custom_template}' fehlt → entfernt"
                    ))
                    page.custom_template = ""
                    page.save()
                    page.save_revision().publish()

        # ── Zusammenfassung ───────────────────────────────────────────────

        total = Page.objects.descendant_of(home).live().count()
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Seitenstruktur fertig: {total} Seiten unter /{home.slug}/"))
