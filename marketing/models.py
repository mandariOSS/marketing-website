"""
Wagtail Page Models for Mandari Marketing Website.

Each page type corresponds to a category of marketing content.
The initial content is loaded from the migrated Django templates.
"""

from django.db import models

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.fields import RichTextField, StreamField
from wagtail.models import Page

from .blocks import MarketingStreamBlock


class HomePage(Page):
    """Landing page - holt Stats via API von Mandari."""

    subtitle = models.CharField(max_length=255, blank=True)
    body = StreamField(MarketingStreamBlock(), blank=True, use_json_field=True)

    content_panels = Page.content_panels + [
        FieldPanel("subtitle"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels

    template = "marketing/landing.html"
    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["MarketingPage", "ContactPage", "LegalPage", "blog.BlogIndexPage", "blog.ReleaseIndexPage"]

    class Meta:
        verbose_name = "Startseite"


class MarketingPage(Page):
    """
    Generische Marketing-Seite.

    Used for: Produkt, Lösungen, Sicherheit, Open Source, Preise,
    Mitmachen, Team, FAQ, Partner, Über uns, Kommunen, Roadmap,
    Presse, Danksagungen.
    """

    body = StreamField(MarketingStreamBlock(), blank=True, use_json_field=True)

    # Allow a custom template override per page
    custom_template = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optionaler Template-Pfad (z.B. 'marketing/produkt.html'). Leer = Standard-Template.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [FieldPanel("custom_template")],
            heading="Template-Konfiguration",
        ),
    ]

    # MarketingPage darf MarketingPage-Kinder haben — genutzt für die
    # Vergleichsseiten unter /vergleich/mandari-vs-<anbieter>/.
    parent_page_types = ["HomePage", "MarketingPage"]
    subpage_types = ["MarketingPage"]

    def get_template(self, request, *args, **kwargs):
        if self.custom_template:
            return self.custom_template
        return "marketing/marketing_page.html"

    class Meta:
        verbose_name = "Marketing-Seite"
        verbose_name_plural = "Marketing-Seiten"


class ContactPage(Page):
    """Kontaktseite mit Formular."""

    intro = RichTextField(blank=True)
    thank_you_text = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel("intro"),
        FieldPanel("thank_you_text"),
    ]

    template = "marketing/kontakt.html"
    max_count = 1
    parent_page_types = ["HomePage"]
    subpage_types = []

    class Meta:
        verbose_name = "Kontaktseite"


class LegalPage(Page):
    """Impressum, Datenschutz, AGB, Quellen — StreamField-basiert."""

    # Legacy RichText (vorher das einzige Feld). Nur noch für Rückwärts-
    # Kompatibilität — neue Inhalte gehören in body_stream.
    body = RichTextField(blank=True, help_text="Legacy-Feld, nutze body_stream für neue Inhalte.")

    # Neuer StreamField — gleiches Block-Set wie MarketingPage
    body_stream = StreamField(
        MarketingStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text="Strukturierter Inhalt aus Mandari-Design-System-Blöcken",
    )

    # Allow a custom template override per page
    custom_template = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optionaler Template-Pfad (z.B. 'marketing/impressum.html'). Leer = Standard-Template.",
    )

    content_panels = Page.content_panels + [
        FieldPanel("body_stream"),
        FieldPanel("body"),
    ]

    promote_panels = Page.promote_panels + [
        MultiFieldPanel(
            [FieldPanel("custom_template")],
            heading="Template-Konfiguration",
        ),
    ]

    parent_page_types = ["HomePage"]
    subpage_types = []

    def get_template(self, request, *args, **kwargs):
        if self.custom_template:
            return self.custom_template
        # If body_stream has content, use the universal streamfield template
        if self.body_stream:
            return "marketing/legal_streamfield_page.html"
        return "marketing/legal_page.html"

    class Meta:
        verbose_name = "Rechtliche Seite"
        verbose_name_plural = "Rechtliche Seiten"
