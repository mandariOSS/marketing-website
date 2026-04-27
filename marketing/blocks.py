"""
Mandari Design System Blocks for Wagtail StreamField.

Each block matches a recurring pattern from the Mandari Design System,
allowing CMS editors to assemble complete pages without touching code.

Color palette (used by ChoiceBlock fields throughout):
    primary  = Indigo  (Mandari brand color)
    green    = Insight & open / cost-free
    blue     = Session / official
    amber    = Beta / warning / community
    rose     = Reseller / design / urgent
    teal     = Strategic / advisory
    gray     = Neutral / default
"""

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    IntegerBlock,
    ListBlock,
    PageChooserBlock,
    RichTextBlock,
    StreamBlock,
    StructBlock,
    TextBlock,
    URLBlock,
)
from wagtail.images.blocks import ImageChooserBlock


# ─────────────────────────── Color choices ────────────────────────────
COLOR_CHOICES = [
    ("primary", "Primary (Indigo)"),
    ("green", "Grün"),
    ("blue", "Blau"),
    ("amber", "Amber / Gelb"),
    ("rose", "Rose / Rot"),
    ("teal", "Teal"),
    ("gray", "Grau / Neutral"),
]


# ──────────────────────── Reusable atom blocks ────────────────────────


class CTAButtonBlock(StructBlock):
    """Single CTA button — used inside HeroBlock and GradientCTABlock."""

    label = CharBlock(required=True, help_text="Button-Text")
    url = CharBlock(
        required=True,
        help_text="URL oder Anchor (z.B. /kontakt/ oder #faq)",
    )
    icon = CharBlock(
        required=False,
        help_text="Lucide-Icon-Name (z.B. 'mail', 'github', 'arrow-right')",
    )
    style = ChoiceBlock(
        choices=[
            ("primary", "Primary (gefüllt)"),
            ("secondary", "Sekundär (grau gefüllt)"),
            ("outline", "Outline (Rahmen)"),
        ],
        default="primary",
    )

    class Meta:
        icon = "link"
        label = "CTA-Button"


class TrustBannerItemBlock(StructBlock):
    """One item inside the 4-icon trust banner."""

    icon = CharBlock(required=True, help_text="Lucide-Icon-Name")
    label_bold = CharBlock(required=True, help_text="Fett gedruckter Teil (z.B. 'AGPL-3.0')")
    label_normal = CharBlock(required=False, help_text="Normaler Teil (z.B. 'Code offen')")

    class Meta:
        icon = "tick"
        label = "Trust-Item"


class CardBulletBlock(StructBlock):
    """Single bullet inside a Mandari card."""

    icon = CharBlock(required=False, default="check", help_text="Lucide-Icon (default: check)")
    text = CharBlock(required=True)

    class Meta:
        icon = "tick"


class MandariCardBlock(StructBlock):
    """One card in a 3- or 6-column Mandari card grid."""

    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary", help_text="Card-Akzentfarbe")
    icon = CharBlock(required=True, help_text="Lucide-Icon im Header")
    badge = CharBlock(required=False, help_text="Optionales Badge oben links (z.B. 'Top-Priorität')")
    title = CharBlock(required=True)
    subtitle = CharBlock(required=False, help_text="Kleiner farbiger Text unter dem Titel")
    description = TextBlock(required=False)
    bullets = ListBlock(CardBulletBlock(), required=False, default=[])
    cta_label = CharBlock(required=False)
    cta_url = CharBlock(required=False)
    cta_icon = CharBlock(required=False, default="arrow-right")

    class Meta:
        icon = "placeholder"
        label = "Mandari-Card"


class StepBlock(StructBlock):
    """One step in a numbered process."""

    number = CharBlock(required=True, help_text="z.B. '01', '02'")
    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")
    icon = CharBlock(required=True, help_text="Lucide-Icon")
    title = CharBlock(required=True)
    description = TextBlock(required=True)
    duration = CharBlock(required=False, help_text="z.B. '≤ 24 h' oder '1–2 Wochen'")

    class Meta:
        icon = "ordered-list"


class StatsItemBlock(StructBlock):
    """One large-number stat in a stats grid."""

    value = CharBlock(required=True, help_text="Große Zahl, z.B. '0' oder '~3 k'")
    label = CharBlock(required=True, help_text="Kleiner Text darunter")
    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")

    class Meta:
        icon = "snippet"


class FAQItemBlock(StructBlock):
    """Single Q&A entry."""

    question = CharBlock(required=True)
    answer = RichTextBlock(required=True, features=["bold", "italic", "link", "ol", "ul"])

    class Meta:
        icon = "help"


class TechPartnerBlock(StructBlock):
    """One tech partner in the 8-card grid."""

    name = CharBlock(required=True, help_text="z.B. 'Django'")
    icon = CharBlock(required=True, help_text="Lucide-Icon")
    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")
    description = CharBlock(required=False, help_text="Kurzbeschreibung, z.B. 'Web-Framework'")
    url = URLBlock(required=False)

    class Meta:
        icon = "site"


class EmailEntryBlock(StructBlock):
    """One row in the email-directory table."""

    address = CharBlock(required=True, help_text="z.B. 'security@mandari.de'")
    purpose = CharBlock(required=True)
    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")

    class Meta:
        icon = "mail"


# ──────────────────────────── Section blocks ───────────────────────────


class HeroBlock(StructBlock):
    """Linksbündige Hero-Sektion mit Badge, H1, Subline, CTAs."""

    badge_text = CharBlock(required=False, help_text="Pill über dem Titel")
    badge_icon = CharBlock(required=False, help_text="Lucide-Icon")
    badge_color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")
    title = CharBlock(required=True, help_text="H1 — kann <span>highlight</span> enthalten")
    title_highlight = CharBlock(
        required=False,
        help_text="Text der farbig hervorgehoben wird (am Ende des Titels)",
    )
    subline = TextBlock(required=False, help_text="Erste Subline (text-xl)")
    subline_secondary = TextBlock(required=False, help_text="Optionale zweite Subline (text-lg, ausgegraut)")
    ctas = ListBlock(CTAButtonBlock(), required=False, default=[])
    background_color = ChoiceBlock(
        choices=COLOR_CHOICES,
        default="primary",
        help_text="Gradient-Farbe oben links (Default: primary)",
    )

    class Meta:
        template = "marketing/blocks/hero.html"
        icon = "image"
        label = "Hero (linksbündig)"


class TrustBannerBlock(StructBlock):
    """Horizontaler Trust-Banner mit 3-4 Icon+Label-Items."""

    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary", help_text="Hintergrundfarbe")
    items = ListBlock(TrustBannerItemBlock(), min_num=2, max_num=5)

    class Meta:
        template = "marketing/blocks/trust_banner.html"
        icon = "tick-inverse"
        label = "Trust-Banner"


class SectionHeaderBlock(StructBlock):
    """Wiederverwendbarer Sektions-Header (Badge + H2 + Subline)."""

    badge_text = CharBlock(required=False)
    badge_icon = CharBlock(required=False)
    badge_color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")
    title = CharBlock(required=True, help_text="H2")
    subline = TextBlock(required=False)
    align = ChoiceBlock(
        choices=[("left", "Linksbündig"), ("center", "Zentriert")],
        default="left",
    )

    class Meta:
        template = "marketing/blocks/section_header.html"
        icon = "title"
        label = "Sektions-Header"


class MandariCardsBlock(StructBlock):
    """Grid von 3 oder 6 Mandari-Cards (border-2 + Decorative Corner Circle)."""

    header = SectionHeaderBlock(required=False)
    columns = ChoiceBlock(
        choices=[("3", "3 Spalten"), ("4", "4 Spalten"), ("6", "6 Spalten (2×3)")],
        default="3",
    )
    cards = ListBlock(MandariCardBlock(), min_num=2, max_num=6)
    background = ChoiceBlock(
        choices=[("white", "Weiß"), ("gray", "Hellgrau (gray-50)")],
        default="white",
    )

    class Meta:
        template = "marketing/blocks/mandari_cards.html"
        icon = "grip"
        label = "Mandari-Cards (3/6 Spalten)"


class TwoColumnUseCaseBlock(StructBlock):
    """2-Spalten Use-Case-Sektion (auf bg-gray-50)."""

    header = SectionHeaderBlock(required=False)
    left_card = MandariCardBlock()
    right_card = MandariCardBlock()

    class Meta:
        template = "marketing/blocks/two_column_use_case.html"
        icon = "duplicate"
        label = "2-Spalten Use-Case"


class StepProcessBlock(StructBlock):
    """Numerierte 3- oder 4-Schritte-Sektion (z.B. So-läufts)."""

    header = SectionHeaderBlock(required=False)
    columns = ChoiceBlock(
        choices=[("3", "3 Schritte"), ("4", "4 Schritte")],
        default="4",
    )
    steps = ListBlock(StepBlock(), min_num=2, max_num=5)
    background = ChoiceBlock(
        choices=[("white", "Weiß"), ("gray", "Hellgrau (gray-50)")],
        default="gray",
    )

    class Meta:
        template = "marketing/blocks/step_process.html"
        icon = "ordered-list"
        label = "Schritt-Prozess (numerisch)"


class StatsGridBlock(StructBlock):
    """Grid mit großen Zahlen (z.B. Transparenzbericht-Sektionen)."""

    header = SectionHeaderBlock(required=False)
    columns = ChoiceBlock(
        choices=[("2", "2 Spalten"), ("3", "3 Spalten"), ("4", "4 Spalten")],
        default="4",
    )
    items = ListBlock(StatsItemBlock(), min_num=2, max_num=8)
    border_color = ChoiceBlock(
        choices=COLOR_CHOICES,
        default="primary",
        help_text="Border-Farbe der Karten",
    )

    class Meta:
        template = "marketing/blocks/stats_grid.html"
        icon = "snippet"
        label = "Stats-Grid (große Zahlen)"


class GradientCTABlock(StructBlock):
    """Final CTA mit Gradient-Background."""

    title = CharBlock(required=True)
    subline = TextBlock(required=False)
    ctas = ListBlock(CTAButtonBlock(), min_num=1, max_num=4)
    gradient_from = ChoiceBlock(choices=COLOR_CHOICES, default="primary")

    class Meta:
        template = "marketing/blocks/gradient_cta.html"
        icon = "pick"
        label = "Final CTA (gradient)"


class AccordionFAQBlock(StructBlock):
    """Akkordeon-FAQ mit Alpine.js."""

    header = SectionHeaderBlock(required=False)
    items = ListBlock(FAQItemBlock(), min_num=1)
    anchor_id = CharBlock(
        required=False,
        default="faq",
        help_text="HTML-id für Anker-Links (default: 'faq')",
    )
    background = ChoiceBlock(
        choices=[("white", "Weiß"), ("gray", "Hellgrau (gray-50)")],
        default="gray",
    )

    class Meta:
        template = "marketing/blocks/accordion_faq.html"
        icon = "help"
        label = "FAQ-Akkordeon"


class TableOfContentsBlock(StructBlock):
    """Inhaltsverzeichnis-Card mit Sprungmarken (Legal-Pages)."""

    title = CharBlock(default="Inhalt", required=True)
    items = ListBlock(
        StructBlock([
            ("number", CharBlock(required=True, help_text="z.B. '1.'")),
            ("text", CharBlock(required=True)),
            ("anchor", CharBlock(required=True, help_text="Anker ohne #, z.B. 'auf-einen-blick'")),
        ]),
        min_num=2,
    )

    class Meta:
        template = "marketing/blocks/table_of_contents.html"
        icon = "list-ul"
        label = "Inhaltsverzeichnis (Schnell-Nav)"


class NumberedArticleBlock(StructBlock):
    """Nummerierte Artikel-Sektion mit RichText (Legal-Pages, Transparenzbericht)."""

    number = CharBlock(required=True, help_text="z.B. '1', '2.1'")
    anchor = CharBlock(required=True, help_text="HTML-id für Sprungmarke")
    title = CharBlock(required=True)
    body = RichTextBlock(features=["bold", "italic", "link", "ol", "ul", "h3", "h4"])

    class Meta:
        template = "marketing/blocks/numbered_article.html"
        icon = "doc-full"
        label = "Nummerierter Artikel"


class DisclaimerBoxBlock(StructBlock):
    """Hinweis-Box (rounded, mit Icon, gray oder farbig)."""

    icon = CharBlock(required=True, default="info")
    color = ChoiceBlock(choices=COLOR_CHOICES, default="gray")
    body = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        template = "marketing/blocks/disclaimer_box.html"
        icon = "warning"
        label = "Hinweis-Box"


class TechPartnerGridBlock(StructBlock):
    """Grid mit Tech-Partner-Logos (8-Kachel-Layout)."""

    header = SectionHeaderBlock(required=False)
    partners = ListBlock(TechPartnerBlock(), min_num=4, max_num=12)

    class Meta:
        template = "marketing/blocks/tech_partner_grid.html"
        icon = "package"
        label = "Tech-Partner-Grid"


class EmailDirectoryBlock(StructBlock):
    """Tabelle mit E-Mail-Adressen (RFC 2142 Style)."""

    header = SectionHeaderBlock(required=False)
    entries = ListBlock(EmailEntryBlock(), min_num=2)

    class Meta:
        template = "marketing/blocks/email_directory.html"
        icon = "mail"
        label = "E-Mail-Verzeichnis"


class WarrantCanaryBlock(StructBlock):
    """Warrant-Canary-Block für Transparenzbericht."""

    date = CharBlock(required=True, help_text="Stand-Datum (z.B. '26.04.2026')")
    body = RichTextBlock(features=["bold", "italic", "link"])

    class Meta:
        template = "marketing/blocks/warrant_canary.html"
        icon = "warning"
        label = "Warrant Canary"


class RichTextSectionBlock(StructBlock):
    """Freie Rich-Text-Sektion mit optionalem Header."""

    header = SectionHeaderBlock(required=False)
    body = RichTextBlock(features=["bold", "italic", "link", "ol", "ul", "h2", "h3", "h4", "blockquote"])
    background = ChoiceBlock(
        choices=[("white", "Weiß"), ("gray", "Hellgrau (gray-50)")],
        default="white",
    )

    class Meta:
        template = "marketing/blocks/richtext_section.html"
        icon = "doc-full"
        label = "Richtext-Sektion"


class PricingTierBlock(StructBlock):
    """One pricing tier card (Insight / Work / Session pattern)."""

    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")
    name = CharBlock(required=True)
    subtitle = CharBlock(required=False)
    badge = CharBlock(required=False, help_text="z.B. 'Beta-Phase' oder 'Immer kostenlos'")
    price_main = CharBlock(required=True, help_text="Hauptpreis, z.B. '39,90 €' oder '0 €'")
    price_unit = CharBlock(required=False, help_text="z.B. '/Monat' oder 'für immer'")
    price_note = CharBlock(required=False, help_text="Kleiner Hinweis unter dem Preis")
    description = TextBlock(required=False)
    features = ListBlock(CardBulletBlock(), required=False)
    is_highlighted = BooleanBlock(required=False, help_text="Mit Empfohlen-Sticker + shadow")
    cta_label = CharBlock(required=False)
    cta_url = CharBlock(required=False)

    class Meta:
        icon = "tag"


class PricingTableBlock(StructBlock):
    """3-Card-Pricing-Tabelle (für Preise-Page)."""

    header = SectionHeaderBlock(required=False)
    tiers = ListBlock(PricingTierBlock(), min_num=2, max_num=4)

    class Meta:
        template = "marketing/blocks/pricing_table.html"
        icon = "tag"
        label = "Pricing-Tabelle (3 Cards)"


# ─────────────────────── Composite block container ──────────────────────


class MarketingStreamBlock(StreamBlock):
    """Available blocks for marketing pages — order matters in the picker UI."""

    # Page-Layout-Bausteine (häufigste oben)
    hero = HeroBlock()
    trust_banner = TrustBannerBlock()
    mandari_cards = MandariCardsBlock()
    two_column_use_case = TwoColumnUseCaseBlock()
    step_process = StepProcessBlock()
    stats_grid = StatsGridBlock()
    pricing_table = PricingTableBlock()
    accordion_faq = AccordionFAQBlock()
    gradient_cta = GradientCTABlock()

    # Spezialisierte Blöcke
    tech_partner_grid = TechPartnerGridBlock()
    email_directory = EmailDirectoryBlock()
    warrant_canary = WarrantCanaryBlock()

    # Legal / Prosa
    table_of_contents = TableOfContentsBlock()
    numbered_article = NumberedArticleBlock()
    richtext_section = RichTextSectionBlock()
    disclaimer_box = DisclaimerBoxBlock()

    class Meta:
        block_counts = {}  # No max-restrictions
