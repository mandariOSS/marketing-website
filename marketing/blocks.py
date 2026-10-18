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

import re

from wagtail.blocks import (
    BooleanBlock,
    CharBlock,
    ChoiceBlock,
    FloatBlock,
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


class StatusBadgeBlock(StructBlock):
    """Small status pill displayed at the top of a Mandari card."""

    text = CharBlock(required=True, help_text="Badge-Text, z.B. 'Offen ab sofort'")
    icon = CharBlock(required=False, help_text="Optionales Lucide-Icon (z.B. 'rocket')")
    color = ChoiceBlock(
        choices=COLOR_CHOICES + [("auto", "Wie Card-Farbe (auto)")],
        default="auto",
        help_text="Badge-Farbe — 'auto' folgt der Card-Akzentfarbe",
    )

    class Meta:
        icon = "tag"
        label = "Status-Badge"


class MandariCardBlock(StructBlock):
    """One card in a 3- or 6-column Mandari card grid."""

    color = ChoiceBlock(choices=COLOR_CHOICES, default="primary", help_text="Card-Akzentfarbe")
    icon = CharBlock(required=True, help_text="Lucide-Icon im Header")
    badge = CharBlock(required=False, help_text="DEPRECATED: nutze status_badges statt dessen")
    status_badges = ListBlock(
        StatusBadgeBlock(),
        required=False,
        default=[],
        help_text="0-3 kleine Status-Pills oben (z.B. 'Offen ab sofort', 'Pilot-Konditionen')",
    )
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
    meta_text = CharBlock(
        required=False,
        help_text="Optionale Zusatzzeile unter Beschreibung (z.B. 'kostenlos · unverbindlich')",
    )

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


def hero_title(title, highlight=""):
    """Setzt Titel und title_highlight zur Überschrift zusammen.

    Normalfall: mit Leerzeichen anhängen („mandari“ + „Roadmap“ → „mandari Roadmap“).
    Endet der Titel auf Bindestrich, ist er ein Wortanfang: Beginnt die Ergänzung klein, entsteht
    ein Wort („Quellen-“ + „nachweise“ → „Quellennachweise“); beginnt sie groß, bleibt der
    Bindestrich („Presse-“ + „Material“ → „Presse-Material“).
    """
    title = title or ""
    if not highlight:
        return title
    if title.endswith("-"):
        if highlight[0].islower():
            return title[:-1] + highlight
        return title + highlight
    return f"{title} {highlight}" if title else highlight


# Neben einem Produktbild ist die Überschrift höchstens 15 Zeichen breit. Längere Wörter
# (Ratsinformationssystem) passen bei 56 px nicht einmal in die halbe Rasterbreite: Dann bekommt der Text
# sieben, das Bild fünf Spalten (hero.html).
LANGES_WORT = 16


def langes_wort(text):
    """Enthält die Überschrift ein Wort, das neben einem Produktbild nicht in eine Zeile passt?"""
    return any(len(wort) >= LANGES_WORT for wort in re.findall(r"\w+", str(text or "")))


class HeroBlock(StructBlock):
    """Linksbündiger Hero: H1, ein erklärender Satz, ein gefüllter Aufruf und höchstens ein Textlink.

    Badge-Felder und Hintergrundfarbe bleiben für bestehende Inhalte definiert, werden aber nicht mehr
    angezeigt (keine Pillen, keine Verläufe).
    """

    badge_text = CharBlock(required=False, help_text="Wird nicht angezeigt (Hero ohne Pille)")
    badge_icon = CharBlock(required=False, help_text="Lucide-Icon")
    badge_color = ChoiceBlock(choices=COLOR_CHOICES, default="primary")
    title = CharBlock(required=True, help_text="H1 — kann <span>highlight</span> enthalten")
    title_highlight = CharBlock(
        required=False,
        help_text="Wird ohne eigene Farbe an den Titel angehängt",
    )
    subline = TextBlock(required=False, help_text="Erste Subline (text-xl)")
    subline_secondary = TextBlock(required=False, help_text="Optionale zweite Subline (text-lg, ausgegraut)")
    ctas = ListBlock(
        CTAButtonBlock(),
        required=False,
        default=[],
        help_text="Erster Eintrag = gefüllter Button, zweiter = Textlink; weitere werden nicht angezeigt",
    )
    background_color = ChoiceBlock(
        choices=COLOR_CHOICES,
        default="primary",
        help_text="Ohne Wirkung (Hero ohne Verlauf)",
    )

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        context["heading"] = hero_title(value.get("title"), value.get("title_highlight"))
        context["langes_wort"] = langes_wort(context["heading"])
        return context

    class Meta:
        template = "marketing/blocks/hero.html"
        icon = "image"
        label = "Hero (linksbündig, ein Aufruf)"


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
    anchor_id = CharBlock(
        required=False,
        help_text="Optionale HTML-id für Anker-Links (ohne #, z.B. 'founder')",
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
    note_html = RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Optionaler Hinweis unter den Schritten (z.B. Solo-Founder-Realität)",
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
    """Einladung am Seitenende auf ruhiger dunkler Fläche (ohne Verlauf).

    Der Name bleibt für bestehende Inhalte erhalten; `gradient_from` hat keine Wirkung mehr.
    """

    title = CharBlock(required=True)
    subline = TextBlock(required=False)
    ctas = ListBlock(
        CTAButtonBlock(),
        min_num=1,
        max_num=4,
        help_text="Erster Eintrag = gefüllter Button, zweiter = Textlink; weitere werden nicht angezeigt",
    )
    gradient_from = ChoiceBlock(choices=COLOR_CHOICES, default="primary", help_text="Ohne Wirkung (flache Fläche)")
    wege = ListBlock(
        StructBlock([
            ("label", CharBlock(help_text="Kleine Zeile, z. B. 'E-Mail' oder 'Für Vergabestellen'")),
            ("wert", CharBlock(help_text="Adresse, Angabe oder Linktext")),
            ("url", CharBlock(required=False, help_text="Optionaler Link; E-Mail-Adressen werden automatisch verlinkt")),
        ]),
        required=False,
        default=[],
        help_text="Direkte Wege rechts neben der Einladung (Muster 5c). Leer: E-Mail und Gesprächsform als Standard.",
    )

    class Meta:
        template = "marketing/blocks/gradient_cta.html"
        icon = "pick"
        label = "Einladung (Seitenende)"


class SplitRowBlock(StructBlock):
    """Eine Zeile: Titel links (mit Etikett und Status), Text und ein Textlink rechts."""

    title = CharBlock(required=True, help_text="Überschrift der Zeile, z. B. 'mandari Session' oder 'Verwaltung'")
    label = CharBlock(required=False, help_text="Kleine Zeile unter dem Titel, z. B. 'Für Verwaltungen'")
    status = CharBlock(
        required=False,
        help_text="Leiser Status unter dem Etikett, z. B. 'Offene Beta' oder 'Geplant 2027'",
    )
    text = RichTextBlock(required=True, features=["bold", "italic", "link"])
    link_label = CharBlock(required=False, help_text="Text des einen Links, sagt, was passiert")
    link_url = CharBlock(required=False, help_text="Ziel des Links, z. B. /kommunen/")
    anchor_id = CharBlock(required=False, help_text="Optionale HTML-id für Sprungmarken (ohne #, z. B. 'insight')")

    class Meta:
        icon = "list-ul"
        label = "Zeile"


class SplitRowsBlock(StructBlock):
    """Einträge ohne Karten: Titel über dem Text, im Raster oder als Zeitleiste.

    Einträge zu mandari Session, Work und Insight werden Produktflächen in der Kennfarbe. Der Typname
    bleibt aus Kompatibilitätsgründen ``split_rows``.
    """

    header = SectionHeaderBlock(required=False)
    layout = ChoiceBlock(
        choices=[
            ("raster", "Raster: Titel über dem Text, zwei Spalten (drei bei genau drei Einträgen)"),
            ("zeitleiste", "Zeitleiste: Datum (Titel) links, Ereignis (Zeile darunter) und Text rechts"),
        ],
        default="raster",
        required=False,
        help_text="Zeitleiste nur für Daten in zeitlicher Folge",
    )
    rows = ListBlock(SplitRowBlock(), min_num=1, max_num=8)
    note = RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Optionaler Absatz unter den Zeilen (z. B. Ausblick mit Link zur Roadmap)",
    )
    background = ChoiceBlock(
        choices=[("white", "Weiß"), ("gray", "Hell (ruhige Fläche)")],
        default="white",
    )

    class Meta:
        template = "marketing/blocks/split_rows.html"
        icon = "list-ul"
        label = "Einträge (Raster oder Zeitleiste)"


# ── Randspalte (Muster 5a), auch in Häufigen Fragen und Dokumentseiten ──

LINK_FEATURES = ["bold", "italic", "link"]
PRODUKT_CHOICES = [("session", "mandari Session"), ("work", "mandari Work"), ("insight", "mandari Insight")]


class LinkBlock(StructBlock):
    label = CharBlock()
    url = CharBlock()

    class Meta:
        icon = "link"
        label = "Link"


class BegriffWertBlock(StructBlock):
    begriff = CharBlock()
    wert = CharBlock()

    class Meta:
        icon = "list-ul"
        label = "Angabe"


class RandAblaufBlock(StructBlock):
    titel = CharBlock()
    schritte = ListBlock(StructBlock([("marke", CharBlock()), ("text", CharBlock())]))

    class Meta:
        icon = "time"
        label = "Kleiner Ablauf"


class RandLinksBlock(StructBlock):
    titel = CharBlock()
    links = ListBlock(LinkBlock())

    class Meta:
        icon = "link"
        label = "Links"


class RandFaktenBlock(StructBlock):
    titel = CharBlock(required=False)
    fakten = ListBlock(BegriffWertBlock())

    class Meta:
        icon = "list-ul"
        label = "Fakten"


class RandStreamBlock(StreamBlock):
    ablauf = RandAblaufBlock()
    links = RandLinksBlock()
    fakten = RandFaktenBlock()
    text = RichTextBlock(features=LINK_FEATURES + ["ul"])


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
    rand = RandStreamBlock(required=False, help_text="Optionale Randspalte rechts (Kontakt, Links zum Nachlesen)")

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
    aside = RichTextBlock(
        required=False,
        features=["bold", "italic", "link", "ul", "h3"],
        help_text="Randspalte rechts neben dem Text (am Handy darunter): kurze Ergänzung wie Kernsätze, "
                  "Kennzahlen mit Stand oder ein Kontakt. Leer lassen, wenn es nichts Eigenes zu sagen gibt.",
    )
    background = ChoiceBlock(
        choices=[("white", "Weiß"), ("gray", "Hellgrau (gray-50)")],
        default="white",
    )
    zweispaltig = BooleanBlock(
        required=False, help_text="Lange Listen (Quellen) über die volle Breite in zwei Spalten"
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
    price_net = CharBlock(required=False, help_text="Nettoausweis für Vergabevergleiche, z. B. '33,53 € netto zzgl. 19 % USt'")
    price_alt = CharBlock(required=False, help_text="Alternative Zahlweise, z. B. 'oder 399 €/Jahr – zwei Monate gespart'")
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


# ─────────────────── Vergleichstabelle (mandari vs. X) ───────────────────


class ComparisonCellBlock(StructBlock):
    """Eine Zelle der Vergleichstabelle (mandari- oder Anbieter-Spalte)."""

    status = ChoiceBlock(
        choices=[
            ("yes", "✓ Ja (grün)"),
            ("partial", "◐ Teilweise / eingeschränkt"),
            ("open", "○ Noch nicht verfügbar (nur mandari, Roadmap-Stufe im Zusatztext)"),
            ("no", "– Nein / nicht vorhanden (neutral)"),
            ("unknown", "keine öffentliche Angabe (neutral, mit Fußnote)"),
        ],
        default="yes",
    )
    note = CharBlock(
        required=False,
        help_text="Optionaler kurzer Zusatztext unter dem Status (z. B. Produktname, Eigenangabe-Kennzeichnung)",
    )

    class Meta:
        icon = "tick"
        label = "Vergleichs-Zelle"


class ComparisonRowBlock(StructBlock):
    """Eine Zeile der Vergleichstabelle: Kriterium + zwei Zellen."""

    label = CharBlock(required=True, help_text="Funktion/Kriterium, z. B. 'Open Source'")
    mandari = ComparisonCellBlock(help_text="mandari-Spalte")
    competitor = ComparisonCellBlock(help_text="Anbieter-Spalte")

    class Meta:
        icon = "list-ul"
        label = "Vergleichs-Zeile"


class ComparisonGroupBlock(StructBlock):
    """Gruppe von Vergleichszeilen (z. B. 'Grundlagen', 'Betrieb')."""

    title = CharBlock(required=True, help_text="Gruppen-Überschrift, z. B. 'Grundlagen'")
    rows = ListBlock(ComparisonRowBlock(), min_num=1)

    class Meta:
        icon = "folder-open-1"
        label = "Kriterien-Gruppe"


class ComparisonTableBlock(StructBlock):
    """Funktionstabelle mandari vs. Anbieter — Zeilen = Kriterien, Spalten = Systeme."""

    header = SectionHeaderBlock(required=False)
    competitor_label = CharBlock(required=True, help_text="Spaltentitel des Anbieters, z. B. 'ALLRIS (CC e-gov)'")
    groups = ListBlock(ComparisonGroupBlock(), min_num=1)
    footnote = RichTextBlock(
        required=False,
        features=["bold", "italic", "link"],
        help_text="Fußnote unter der Tabelle (z. B. Erläuterung zu 'keine öffentliche Angabe')",
    )

    class Meta:
        template = "marketing/blocks/comparison_table.html"
        icon = "table"
        label = "Vergleichstabelle (mandari vs. Anbieter)"


# ─────────────────── Feature-Matrix (Zeilen = Funktionen, Spalten = Module/Modelle) ───────────────────


class FeatureCellBlock(StructBlock):
    """Eine Zelle der Feature-Matrix."""

    status = ChoiceBlock(
        choices=[
            ("yes", "✓ verfügbar"),
            ("partial", "◐ teilweise / Basis"),
            ("planned", "○ geplant"),
            ("review", "in Prüfung (ohne Termin)"),
            ("no", "– nicht vorgesehen"),
            ("info", "nur Text (z. B. Zuständigkeit)"),
        ],
        default="yes",
    )
    note = CharBlock(required=False, help_text="Kurzer Zusatz, z. B. 'Q4/2026' oder 'Kommune'")

    class Meta:
        icon = "tick"
        label = "Matrix-Zelle"


class FeatureRowBlock(StructBlock):
    """Eine Zeile: Funktion plus eine Zelle je Spalte (Reihenfolge wie `columns`)."""

    label = CharBlock(required=True, help_text="Funktion oder Kriterium")
    description = CharBlock(required=False, help_text="Optionale Erläuterung unter dem Namen")
    cells = ListBlock(FeatureCellBlock(), min_num=2, max_num=4)

    class Meta:
        icon = "list-ul"
        label = "Matrix-Zeile"


class FeatureGroupBlock(StructBlock):
    title = CharBlock(required=True, help_text="Gruppen-Überschrift, z. B. 'Sitzungsdienst'")
    rows = ListBlock(FeatureRowBlock(), min_num=1)

    class Meta:
        icon = "folder-open-1"
        label = "Funktionsgruppe"


class FeatureMatrixBlock(StructBlock):
    """Funktionsmatrix: Spalten frei benennbar (Insight/Work/Session oder Betriebsmodelle)."""

    header = SectionHeaderBlock(required=False)
    columns = ListBlock(CharBlock(), min_num=2, max_num=4, help_text="Spaltentitel in Reihenfolge der Zellen")
    groups = ListBlock(FeatureGroupBlock(), min_num=1)
    show_legend = BooleanBlock(required=False, default=True, help_text="Legende der Symbole anzeigen")
    footnote = RichTextBlock(required=False, features=["bold", "italic", "link"])

    class Meta:
        template = "marketing/blocks/feature_matrix.html"
        icon = "table"
        label = "Feature-Matrix"


# ─────────────── Marktübersicht (mandari und mehrere Anbieter, nur Status) ───────────────


class MarketMatrixColumnBlock(StructBlock):
    """Spaltenkopf der Marktübersicht, optional mit Link auf den Einzelvergleich."""

    name = CharBlock(required=True, help_text="z. B. 'mandari' oder 'Somacos'")
    url = CharBlock(required=False, help_text="Optionaler Link, z. B. /vergleich/mandari-vs-somacos/")

    class Meta:
        icon = "link"
        label = "Spalte"


class MarketMatrixRowBlock(StructBlock):
    """Eine Zeile: Funktion plus eine Zelle je Spalte (Reihenfolge wie `columns`)."""

    label = CharBlock(required=True, help_text="Funktion")
    cells = ListBlock(ComparisonCellBlock(), min_num=2, max_num=6)

    class Meta:
        icon = "list-ul"
        label = "Zeile"


class MarketMatrixGroupBlock(StructBlock):
    title = CharBlock(required=True, help_text="Bereich, z. B. 'Sitzungsdienst'")
    rows = ListBlock(MarketMatrixRowBlock(), min_num=1)

    class Meta:
        icon = "folder-open-1"
        label = "Bereich"


class MarketMatrixBlock(StructBlock):
    """Marktübersicht: Zeilen = Funktionen, Spalten = mandari und Anbieter; nur Status, kurze Zusätze."""

    header = SectionHeaderBlock(required=False)
    columns = ListBlock(MarketMatrixColumnBlock(), min_num=2, max_num=6)
    groups = ListBlock(MarketMatrixGroupBlock(), min_num=1)
    footnote = RichTextBlock(required=False, features=["bold", "italic", "link"])

    class Meta:
        template = "marketing/blocks/market_matrix.html"
        icon = "table"
        label = "Marktübersicht (mandari und Anbieter)"


# ═════════════════════ Musterkatalog: Abschnitte nach Inhaltsart ═════════════════════
# Jedes Muster hat seine Form aus dem Inhalt (Ablauf mit Fristen → Zeitskala, Sammlung → Register,
# Zusage → große Aussage …). Templates: templates/marketing/blocks/<muster>.html, Geometrie:
# marketing/templatetags/muster.py. Die älteren Bausteine oben bleiben definiert, damit bestehende
# Inhalte weiter laden.

STRECKE_CHOICES = [("1", "erste Strecke (maßstäblich)"), ("2", "nach dem Achsenbruch")]


# ── M1a Zeitskala ─────────────────────────────────────────────────────────


class ZeitMarkeBlock(StructBlock):
    tag = FloatBlock(help_text="Zeitpunkt in Tagen ab Beginn der Strecke (5 Werktage ≈ 7)")
    strecke = ChoiceBlock(choices=STRECKE_CHOICES, default="1")
    frist = CharBlock(help_text="Groß über der Achse, z. B. '3 Werktage'")
    notiz = CharBlock(required=False, help_text="Halbsatz darunter, z. B. 'Eingangsbestätigung'")
    offen = BooleanBlock(required=False, help_text="Zeitpunkt offen (hohle Raute)")

    class Meta:
        icon = "time"
        label = "Marke"


class ZeitBalkenBlock(StructBlock):
    label = CharBlock(help_text="z. B. 'kritisch'")
    wert = CharBlock(help_text="z. B. '72 Stunden'")
    tage = FloatBlock(help_text="Länge in Tagen, im Maßstab der ersten Strecke")

    class Meta:
        icon = "minus"
        label = "Balken"


class ZeitSkalaPunktBlock(StructBlock):
    tag = FloatBlock()
    strecke = ChoiceBlock(choices=STRECKE_CHOICES, default="1")
    label = CharBlock()

    class Meta:
        icon = "minus"
        label = "Skalenpunkt"


class ZeitSchrittBlock(StructBlock):
    frist = CharBlock()
    frist_zusatz = CharBlock(required=False)
    titel = CharBlock()
    text = TextBlock()
    details = ListBlock(BegriffWertBlock(), required=False, default=[])

    class Meta:
        icon = "ordered-list"
        label = "Schritt"


class ZeitskalaBlock(StructBlock):
    """M1a: Ablauf mit Fristen als maßstäbliche Zeitachse; am Handy und für Screenreader als Liste."""

    header = SectionHeaderBlock(required=False)
    strecke1_tage = FloatBlock(default=30, help_text="Länge der ersten Strecke in Tagen")
    strecke2_label = CharBlock(
        required=False, help_text="Gibt es eine zweite Strecke nach einem offenen Zeitpunkt (z. B. 'Fix')?"
    )
    strecke2_tage = FloatBlock(required=False, help_text="Länge der zweiten Strecke in Tagen (leer: nach Marken)")
    marken = ListBlock(ZeitMarkeBlock(), min_num=2, max_num=8)
    balken_titel = CharBlock(required=False)
    balken = ListBlock(ZeitBalkenBlock(), required=False, default=[])
    fenster = TextBlock(required=False, help_text="Ein Satz als helle Fläche über der zweiten Strecke")
    skala = ListBlock(ZeitSkalaPunktBlock(), required=False, default=[])
    schritte = ListBlock(ZeitSchrittBlock(), min_num=2, max_num=6, help_text="Dieselben Daten als Liste")
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/zeitskala.html"
        icon = "time"
        label = "Zeitskala mit Fristen (M1a)"


# ── M1b Dauerbalken ───────────────────────────────────────────────────────


class DauerZeileBlock(StructBlock):
    titel = CharBlock()
    dauer = CharBlock(help_text="z. B. '2–4 Wochen'")
    text = CharBlock(required=False)
    art = ChoiceBlock(
        choices=[("balken", "Schritt mit Dauer"), ("meilenstein", "fester Tag (Raute)")], default="balken"
    )
    dauer_min = FloatBlock(required=False, default=0)
    dauer_max = FloatBlock(required=False, default=0)

    class Meta:
        icon = "minus"
        label = "Schritt"


class DauerbalkenBlock(StructBlock):
    """M1b: aufeinanderfolgende Schritte mit Mindest- und Höchstdauer auf einer Wochenachse."""

    header = SectionHeaderBlock(required=False)
    einheit = CharBlock(default="Wochen")
    gesamt = FloatBlock(default=14)
    teilung = FloatBlock(default=2)
    zeilen = ListBlock(DauerZeileBlock(), min_num=2, max_num=6)
    legende_meilenstein = CharBlock(required=False, default="Umstellung")

    class Meta:
        template = "marketing/blocks/dauerbalken.html"
        icon = "time"
        label = "Dauerbalken (M1b)"


# ── M1a Variante Quartalsachse ────────────────────────────────────────────


class AchsenEintragBlock(StructBlock):
    titel = CharBlock()
    produkt = ChoiceBlock(choices=[("", "Plattform")] + PRODUKT_CHOICES, required=False, default="")
    status = CharBlock(required=False, help_text="'Zugesagt', 'Geplant' oder 'In Prüfung'")
    text = TextBlock(required=False)
    link_label = CharBlock(required=False)
    link_url = CharBlock(required=False)

    class Meta:
        icon = "list-ul"
        label = "Vorhaben"


class AchsenPunktBlock(StructBlock):
    zeitpunkt = CharBlock(help_text="z. B. 'Q4/2026' oder 'Version 1.0'")
    satz = CharBlock(required=False)
    eintraege = ListBlock(AchsenEintragBlock())

    class Meta:
        icon = "date"
        label = "Zeitpunkt"


class QuartalsachseBlock(StructBlock):
    """M1a als Quartalsachse: Spalten sind Zeitpunkte, darunter die Vorhaben mit Kennfarbe und Stufe."""

    header = SectionHeaderBlock(required=False)
    punkte = ListBlock(AchsenPunktBlock(), min_num=2, max_num=5)
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/quartalsachse.html"
        icon = "date"
        label = "Quartalsachse (Roadmap)"


# ── M2 Schrittfolge ───────────────────────────────────────────────────────


class FolgeSchrittBlock(StructBlock):
    titel = CharBlock()
    text = TextBlock()
    notiz = CharBlock(required=False)

    class Meta:
        icon = "ordered-list"
        label = "Schritt"


class SchrittfolgeBlock(StructBlock):
    """M2: kurze Folge ohne Fristen in einer Zeile; die letzte Zelle zeigt das Ergebnis."""

    header = SectionHeaderBlock(required=False)
    schritte = ListBlock(FolgeSchrittBlock(), min_num=2, max_num=4)
    ergebnis_titel = CharBlock(required=False)
    ergebnis_text = TextBlock(required=False)
    ergebnis_link_label = CharBlock(required=False)
    ergebnis_link_url = CharBlock(required=False)
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/schrittfolge.html"
        icon = "ordered-list"
        label = "Schrittfolge kompakt (M2)"


# ── M3 Register ───────────────────────────────────────────────────────────


class RegisterZeileBlock(StructBlock):
    titel = CharBlock()
    url = CharBlock(required=False)
    ort = CharBlock(required=False, help_text="Klein unter dem Titel, z. B. 'im Trust Center'")
    text = RichTextBlock(required=False, features=LINK_FEATURES)
    zusatz = RichTextBlock(required=False, features=LINK_FEATURES, help_text="Dritte Spalte bei vier Spalten")
    stand = CharBlock(required=False)
    status = ChoiceBlock(
        choices=[
            ("da", "verfügbar (gefüllter Punkt)"),
            ("offen", "in Arbeit oder geplant (leerer Kreis)"),
            ("text", "nur Text"),
            ("zahl", "Zahl oder Betrag (rechtsbündig)"),
        ],
        default="text",
    )

    class Meta:
        icon = "list-ul"
        label = "Zeile"


class RegisterGruppeBlock(StructBlock):
    titel = CharBlock(required=False)
    zeilen = ListBlock(RegisterZeileBlock())
    summe_label = CharBlock(required=False)
    summe = CharBlock(required=False)

    class Meta:
        icon = "folder-open-1"
        label = "Gruppe"


class RegisterBlock(StructBlock):
    """M3: Sammlung gleichartiger Einträge als eine Tabelle mit Gruppen und Stand (auch Wegweiser, Kontenblatt)."""

    header = SectionHeaderBlock(required=False)
    kopf = ChoiceBlock(
        choices=[("rand", "Randkopf (links neben der Tabelle)"), ("ueber", "Überkopf")], default="rand"
    )
    spalten = ListBlock(CharBlock(), min_num=2, max_num=4, help_text="Titel, Text, [Zusatz], Stand")
    gruppen = ListBlock(RegisterGruppeBlock(), min_num=1)
    bestand_satz = CharBlock(
        required=False, help_text="z. B. '{da} von {gesamt} liegen vor, {offen} sind in Arbeit.'"
    )
    stand = CharBlock(required=False, help_text="z. B. 'Stand 4. Oktober 2026'")
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/register.html"
        icon = "table"
        label = "Register (M3)"


# ── M5a Randspalte ────────────────────────────────────────────────────────


class RandspalteBlock(StructBlock):
    """M5a: Text in Lesebreite (Stichwort am Absatzanfang) und eine Randspalte mit eigener Aufgabe."""

    header = SectionHeaderBlock(required=False)
    body = RichTextBlock(features=LINK_FEATURES + ["ul", "ol", "h3"])
    rand = RandStreamBlock(help_text="Was der Text nicht hat: Ablauf, Dateien, Ansprechpartner")

    class Meta:
        template = "marketing/blocks/randspalte.html"
        icon = "doc-full"
        label = "Text mit Randspalte (M5a)"


# ── M5b Begriffe in der Marginalie ────────────────────────────────────────


class BegriffBlock(StructBlock):
    begriff = CharBlock()
    marke = CharBlock(required=False, help_text="Kleine Zeile unter dem Begriff, z. B. Datum oder Status")
    text = RichTextBlock(features=LINK_FEATURES + ["ul"])
    link_label = CharBlock(required=False)
    link_url = CharBlock(required=False)
    anchor_id = CharBlock(required=False)

    class Meta:
        icon = "list-ul"
        label = "Begriff"


class BegriffeBlock(StructBlock):
    """M5b: Begriff links groß, Erklärung rechts, Linie zwischen den Zeilen."""

    header = SectionHeaderBlock(required=False)
    eintraege = ListBlock(BegriffBlock(), min_num=2)
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/begriffe.html"
        icon = "list-ul"
        label = "Begriffe in der Marginalie (M5b)"


# ── M6 Große Aussage ──────────────────────────────────────────────────────


class NebenzusageBlock(StructBlock):
    stichwort = CharBlock()
    text = CharBlock()

    class Meta:
        icon = "tick"
        label = "Nebenzusage"


class ZusageBlock(StructBlock):
    """M6a: eine Zusage als großer Satz, rechts die Bedingungen, darunter Nebenzusagen."""

    aussage = TextBlock()
    grundlage = RichTextBlock(required=False, features=LINK_FEATURES)
    bedingungen_titel = CharBlock(required=False)
    bedingungen = ListBlock(CharBlock(), required=False, default=[])
    geltung = RichTextBlock(required=False, features=LINK_FEATURES)
    neben = ListBlock(NebenzusageBlock(), required=False, default=[])
    anchor_id = CharBlock(required=False)

    class Meta:
        template = "marketing/blocks/zusage.html"
        icon = "pick"
        label = "Zusage (M6a)"


class LeitsatzBlock(StructBlock):
    """M6b: Leitsatz über die ganze Breite, Begründung rechts versetzt darunter."""

    satz = TextBlock(help_text="Zeilenumbrüche bleiben erhalten")
    text = RichTextBlock(features=LINK_FEATURES)
    links = ListBlock(LinkBlock(), required=False, default=[])
    anchor_id = CharBlock(required=False)

    class Meta:
        template = "marketing/blocks/leitsatz.html"
        icon = "openquote"
        label = "Leitsatz (M6b)"


# ── M7 Produktbild angeschnitten ──────────────────────────────────────────


class ProduktbildBlock(StructBlock):
    produkt = ChoiceBlock(choices=PRODUKT_CHOICES)
    titel = CharBlock()
    text = TextBlock()
    fakten = ListBlock(BegriffWertBlock(), required=False, default=[])
    link_label = CharBlock(required=False)
    link_url = CharBlock(required=False)
    anchor_id = CharBlock(required=False)

    class Meta:
        icon = "image"
        label = "Produkt"


class ProduktbilderBlock(StructBlock):
    """M7: Text im Raster, echter Bildschirm bis an den Fensterrand, im Wechsel rechts und links."""

    header = SectionHeaderBlock(required=False)
    eintraege = ListBlock(ProduktbildBlock(), min_num=1, max_num=3)
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/produktbilder.html"
        icon = "image"
        label = "Produktbilder angeschnitten (M7)"


# ── M8 Vergleichstabelle ──────────────────────────────────────────────────


class VergleichOptionBlock(StructBlock):
    name = CharBlock()
    satz = CharBlock(required=False)

    class Meta:
        icon = "list-ul"
        label = "Option"


class VergleichKriteriumBlock(StructBlock):
    kriterium = CharBlock()
    werte = ListBlock(RichTextBlock(features=LINK_FEATURES), min_num=2, max_num=4)

    class Meta:
        icon = "list-ul"
        label = "Kriterium"


class VergleichBlock(StructBlock):
    """M8: zwei bis vier Optionen nach denselben Kriterien."""

    header = SectionHeaderBlock(required=False)
    optionen = ListBlock(VergleichOptionBlock(), min_num=2, max_num=4)
    kriterien = ListBlock(VergleichKriteriumBlock(), min_num=1)
    note = RichTextBlock(required=False, features=LINK_FEATURES)

    class Meta:
        template = "marketing/blocks/vergleich.html"
        icon = "table"
        label = "Vergleichstabelle (M8)"


# ── M9 Kennzahl im Kontext ────────────────────────────────────────────────


class ZahlensatzBlock(StructBlock):
    """M9a: Zahlen in einem Satz (fett), rechts klein, wie gezählt wird."""

    titel = CharBlock()
    satz = RichTextBlock(features=["bold"])
    rand = RichTextBlock(required=False, features=LINK_FEATURES)
    anchor_id = CharBlock(required=False)

    class Meta:
        template = "marketing/blocks/zahlensatz.html"
        icon = "snippet"
        label = "Zahl im Satz (M9a)"


class NullenZeileBlock(StructBlock):
    art = CharBlock()
    was = CharBlock()
    wert = CharBlock()

    class Meta:
        icon = "list-ul"
        label = "Zeile"


class NullenGruppeBlock(StructBlock):
    titel = CharBlock()
    zeilen = ListBlock(NullenZeileBlock())

    class Meta:
        icon = "folder-open-1"
        label = "Gruppe"


class NullenBlock(StructBlock):
    """M9b: Summen groß, daneben eine Tabelle, die sie aufschlüsselt."""

    summen = ListBlock(BegriffWertBlock(), min_num=1, max_num=3, help_text="begriff = Bezeichnung, wert = Zahl")
    titel = CharBlock()
    text = RichTextBlock(required=False, features=LINK_FEATURES)
    spalten = ListBlock(CharBlock(), min_num=3, max_num=3)
    gruppen = ListBlock(NullenGruppeBlock())
    anchor_id = CharBlock(required=False)

    class Meta:
        template = "marketing/blocks/nullen.html"
        icon = "snippet"
        label = "Kennzahl mit Aufschlüsselung (M9b)"


# ── M10 Download-Leiste ───────────────────────────────────────────────────


class DownloadsBlock(StructBlock):
    """M10: Titel links, ein Paket oder eine Datei als Button rechts (mit Format), optional Dateizeilen."""

    header = SectionHeaderBlock(required=False)
    label = CharBlock()
    url = CharBlock()
    hinweis = CharBlock(required=False, help_text="Format und Inhalt, z. B. 'Webseite im Kundenportal, tagesaktuell'")
    dateien = ListBlock(LinkBlock(), required=False, default=[])

    class Meta:
        template = "marketing/blocks/downloads.html"
        icon = "download"
        label = "Download-Leiste (M10)"


# ─────────────────────── Composite block container ──────────────────────


class MarketingStreamBlock(StreamBlock):
    """Available blocks for marketing pages — order matters in the picker UI."""

    # Page-Layout-Bausteine (häufigste oben)
    hero = HeroBlock()
    trust_banner = TrustBannerBlock()
    split_rows = SplitRowsBlock()
    mandari_cards = MandariCardsBlock()
    two_column_use_case = TwoColumnUseCaseBlock()
    step_process = StepProcessBlock()
    stats_grid = StatsGridBlock()
    pricing_table = PricingTableBlock()
    comparison_table = ComparisonTableBlock()
    market_matrix = MarketMatrixBlock()
    feature_matrix = FeatureMatrixBlock()
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

    # Musterkatalog (Form folgt Inhalt)
    zeitskala = ZeitskalaBlock()
    dauerbalken = DauerbalkenBlock()
    quartalsachse = QuartalsachseBlock()
    schrittfolge = SchrittfolgeBlock()
    register = RegisterBlock()
    randspalte = RandspalteBlock()
    begriffe = BegriffeBlock()
    zusage = ZusageBlock()
    leitsatz = LeitsatzBlock()
    produktbilder = ProduktbilderBlock()
    vergleich = VergleichBlock()
    zahlensatz = ZahlensatzBlock()
    nullen = NullenBlock()
    downloads = DownloadsBlock()

    class Meta:
        block_counts = {}  # No max-restrictions
