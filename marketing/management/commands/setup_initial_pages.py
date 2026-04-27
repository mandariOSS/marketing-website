"""
Management Command: Erstellt den initialen Wagtail Page-Tree.

Idempotent — kann beliebig oft ausgeführt werden.
Erstellt nur Seiten, die noch nicht existieren.

Usage:
    python manage.py setup_initial_pages
"""

from django.core.management.base import BaseCommand
from wagtail.models import Page, Site


class Command(BaseCommand):
    help = "Erstellt die initiale Seitenstruktur für die Marketing-Website"

    def handle(self, *args, **options):
        from blog.models import BlogIndexPage, ReleaseIndexPage
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
                "custom_template": "marketing/produkt.html",
                "seo_title": "Produkt – Mandari",
                "search_description": "Drei Module für kommunalpolitische Transparenz: Insight, Work und Session.",
            },
            {
                "title": "Preise",
                "slug": "preise",
                "custom_template": "marketing/preise.html",
                "seo_title": "Preise – Mandari",
                "search_description": "Transparente Preisgestaltung. Insight ist kostenlos, Work ab 39,90€/Monat.",
            },
            {
                "title": "Kommunen",
                "slug": "kommunen",
                "custom_template": "marketing/kommunen.html",
                "seo_title": "Verfügbare Kommunen – Mandari",
                "search_description": "Kommunen, deren Ratsinformationen über Mandari verfügbar sind.",
            },
            {
                "title": "Migration",
                "slug": "migration",
                "custom_template": "marketing/migration.html",
                "seo_title": "Migration vom Alt-RIS – Mandari",
                "search_description": "Wechsel von ALLRIS, regisafe oder Somacos zu Mandari Session. Vier-Schritte-Plan, was mitkommt, Pilot-Konditionen.",
            },
            {
                "title": "Roadmap",
                "slug": "roadmap",
                "custom_template": "marketing/roadmap.html",
                "seo_title": "Roadmap – Mandari",
                "search_description": "Öffentliche Roadmap und geplante Features.",
            },

            # ── Vertrauen ★ NEU ──────────────────────────────────────────
            # /sicherheit/ wurde in /trust/ integriert (komplette Doppelung)
            {
                "title": "Trust Center",
                "slug": "trust",
                "custom_template": "marketing/trust.html",
                "seo_title": "Trust Center – Sicherheit, DPA, Subprocessoren",
                "search_description": "Komplette Sicherheits- & Vertrauensübersicht: DPA-Download, Subprocessor-Liste, Hosting-Stack, Backup, SLA, Audits.",
            },
            {
                "title": "Transparenzbericht",
                "slug": "transparenz",
                "custom_template": "marketing/transparenz.html",
                "seo_title": "Transparenzbericht 2026 – Mandari",
                "search_description": "Behördenanfragen, Sicherheitsvorfälle, aktive Kommunen, Finanztransparenz vom Solo-Founder, Open-Source-Beiträge.",
            },
            {
                "title": "Barrierefreiheit",
                "slug": "barrierefreiheit",
                "custom_template": "marketing/barrierefreiheit.html",
                "seo_title": "Erklärung zur Barrierefreiheit – Mandari",
                "search_description": "Pflichterklärung nach BFSG, BITV 2.0, EN 301 549. Konformitätsstand, Feedback, Schlichtungsstelle.",
            },
            {
                "title": "Missbrauch melden",
                "slug": "abuse",
                "custom_template": "marketing/abuse.html",
                "seo_title": "Missbrauch melden – Abuse-Kontakte",
                "search_description": "Abuse-Meldestelle für Spam, illegalen Content, Datenschutz, Urheberrecht, Belästigung. DSA- und NetzDG-konform.",
            },

            # ── Community ────────────────────────────────────────────────
            {
                "title": "Open Source",
                "slug": "open-source",
                "custom_template": "marketing/open-source.html",
                "seo_title": "Open Source – Mandari",
                "search_description": "Mandari ist Open Source unter AGPL-3.0. Selbst-Hosting möglich.",
            },
            {
                "title": "Mitmachen",
                "slug": "mitmachen",
                "custom_template": "marketing/mitmachen.html",
                "seo_title": "Mitmachen – Mandari",
                "search_description": "Werde Teil der Mandari-Community. Entwicklung, Dokumentation, Übersetzung.",
            },

            # ── Über uns ─────────────────────────────────────────────────
            {
                "title": "Über uns",
                "slug": "ueber-uns",
                "custom_template": "marketing/ueber-uns.html",
                "seo_title": "Über uns – Mission, Founder, Werte",
                "search_description": "Mandari ist ein Solo-Projekt von Sven Konopka — Mission, Founder, Werte an einem Ort.",
            },
            {
                "title": "Partner",
                "slug": "partner",
                "custom_template": "marketing/partner.html",
                "seo_title": "Partner – Mandari",
                "search_description": "Partnerschaften mit Kommunen, Fraktionen und zivilgesellschaftlichen Organisationen.",
            },
            {
                "title": "Presse",
                "slug": "presse",
                "custom_template": "marketing/presse.html",
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

        for page_data in marketing_pages:
            slug = page_data.pop("slug")
            custom_template = page_data.pop("custom_template")
            show_in_menus = page_data.pop("show_in_menus", True)

            if MarketingPage.objects.filter(slug=slug).exists():
                self.stdout.write(f"  {page_data['title']} existiert bereits")
                continue

            page = MarketingPage(
                slug=slug,
                custom_template=custom_template,
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

        legal_pages = [
            {
                "title": "Impressum",
                "slug": "impressum",
                "custom_template": "marketing/impressum.html",
                "body": "<p>Angaben gemäß § 5 TMG — bitte im Wagtail-Admin vervollständigen.</p>",
            },
            {
                "title": "Datenschutz",
                "slug": "datenschutz",
                "custom_template": "marketing/datenschutz.html",
                "body": "<p>Datenschutzerklärung — bitte im Wagtail-Admin vervollständigen.</p>",
            },
            {
                "title": "AGB",
                "slug": "agb",
                "custom_template": "marketing/agb.html",
                "body": "<p>Allgemeine Geschäftsbedingungen — bitte im Wagtail-Admin vervollständigen.</p>",
            },
            {
                "title": "Quellennachweise",
                "slug": "quellen",
                "custom_template": "marketing/quellen.html",
                "body": "<p>Quellennachweise und OParl-Quellenverzeichnis — Inhalt wird über das Template gerendert.</p>",
            },
        ]

        for page_data in legal_pages:
            slug = page_data.pop("slug")
            custom_template = page_data.pop("custom_template")

            if LegalPage.objects.filter(slug=slug).exists():
                self.stdout.write(f"  {page_data['title']} existiert bereits")
                continue

            page = LegalPage(
                slug=slug,
                custom_template=custom_template,
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

        # ── Zusammenfassung ───────────────────────────────────────────────

        total = Page.objects.descendant_of(home).live().count()
        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS(f"Seitenstruktur fertig: {total} Seiten unter /{home.slug}/"))
