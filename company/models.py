"""
Unternehmensangaben mit Stufenschalter Vorgründung / Gesellschaft.

Solange die eigene Gesellschaft nicht eingetragen ist, ist topixmedia (Inhaber Sven Konopka)
Rechtsträger von mandari. Diese Angaben stehen hier fest im Code, wortgleich mit dem Impressum.
Nach der Eintragung trägt die Redaktion die Daten der Gesellschaft im Wagtail-Admin unter
„Einstellungen → Unternehmensangaben“ ein und stellt die Stufe um. Die Angaben zum Unternehmen
auf /unternehmen/ und die Anschrift auf /kontakt/ ziehen sofort nach.

Die Rechtstexte in .legal-content/ (Impressum, Datenschutz, AGB, AVV) schalten bewusst NICHT
automatisch um: Sie werden nach der Gründung geprüft, angepasst und mit
`python manage.py refresh_seeded_page <slug> --force` ausgerollt.
"""

from dataclasses import dataclass

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.contrib.settings.models import BaseGenericSetting, register_setting

STAGE_PRE_FOUNDING = "vorgruendung"
STAGE_COMPANY = "gesellschaft"


@dataclass(frozen=True)
class LegalEntity:
    """Der Rechtsträger, so wie ihn die Seiten anzeigen."""

    name: str
    addition: str
    legal_form: str
    representation_label: str
    representation: str
    street: str
    postal_city: str
    phone: str = ""
    vat_id: str = ""
    register: str = ""
    founded: str = ""
    liability_insurance: str = ""

    @property
    def display_name(self) -> str:
        return f"{self.name}, {self.addition}" if self.addition else self.name

    @property
    def address(self) -> str:
        return ", ".join(part for part in (self.street, self.postal_city) if part)

    @property
    def rows(self) -> list[tuple[str, str]]:
        """Zeilen für „Angaben zum Unternehmen“ – leere Angaben entfallen."""
        rows = [
            ("Firmierung", self.display_name),
            ("Rechtsform", self.legal_form),
            (self.representation_label, self.representation),
            ("Anschrift", self.address),
            ("Registereintrag", self.register),
            ("Gründung", self.founded),
            ("Umsatzsteuer-ID", self.vat_id),
            ("Haftpflicht", self.liability_insurance),
        ]
        return [(label, value) for label, value in rows if value]


# Heutiger Rechtsträger (bis zur Eintragung der Gesellschaft) – wie im Impressum.
PRE_FOUNDING = LegalEntity(
    name="topixmedia",
    addition="Inhaber Sven Konopka",
    legal_form="Einzelunternehmen",
    representation_label="Vertreten durch",
    representation="Sven Konopka",
    street="Aegidiistraße 61/62",
    postal_city="48143 Münster",
    phone="0251 37989915",
    vat_id="DE353231778",
)


@register_setting(icon="home")
class CompanySettings(BaseGenericSetting):
    """Stufenschalter und Angaben der künftigen Gesellschaft."""

    STAGE_CHOICES = [
        (STAGE_PRE_FOUNDING, "Vorgründung (Rechtsträger: topixmedia, Inhaber Sven Konopka)"),
        (STAGE_COMPANY, "Gesellschaft (Angaben unten)"),
    ]

    stage = models.CharField(
        "Stufe",
        max_length=20,
        choices=STAGE_CHOICES,
        default=STAGE_PRE_FOUNDING,
        help_text=(
            "Bestimmt, welcher Rechtsträger auf /unternehmen/ und /kontakt/ erscheint. "
            "Impressum, Datenschutz, AGB und AVV schalten nicht automatisch um."
        ),
    )
    announce_founding = models.BooleanField(
        "Hinweis auf die geplante Gesellschaft zeigen",
        default=True,
        help_text="Nur in der Vorgründung: kurzer Hinweis unter den Angaben zum Unternehmen.",
    )

    company_name = models.CharField("Firma", max_length=200, blank=True, default="mandari UG (haftungsbeschränkt)")
    legal_form = models.CharField(
        "Rechtsform", max_length=200, blank=True, default="Unternehmergesellschaft (haftungsbeschränkt)"
    )
    managing_directors = models.CharField("Geschäftsführung", max_length=200, blank=True)
    street = models.CharField("Straße und Hausnummer", max_length=200, blank=True)
    postal_city = models.CharField("PLZ und Ort", max_length=200, blank=True)
    phone = models.CharField("Telefon", max_length=50, blank=True)
    register_court = models.CharField(
        "Registergericht", max_length=200, blank=True, help_text="z. B. Amtsgericht Münster"
    )
    register_number = models.CharField("Registernummer", max_length=50, blank=True, help_text="z. B. HRB 00000")
    vat_id = models.CharField("Umsatzsteuer-Identifikationsnummer", max_length=50, blank=True)
    founded = models.CharField("Gründung", max_length=50, blank=True, help_text="z. B. 2026")
    liability_insurance = models.CharField(
        "Haftpflicht",
        max_length=255,
        blank=True,
        help_text="z. B. Betriebs- und Vermögensschadenhaftpflicht, Deckungssumme auf Anfrage",
    )

    panels = [
        FieldPanel("stage"),
        FieldPanel("announce_founding"),
        MultiFieldPanel(
            [
                FieldPanel("company_name"),
                FieldPanel("legal_form"),
                FieldPanel("managing_directors"),
                FieldPanel("street"),
                FieldPanel("postal_city"),
                FieldPanel("phone"),
                FieldPanel("register_court"),
                FieldPanel("register_number"),
                FieldPanel("vat_id"),
                FieldPanel("founded"),
                FieldPanel("liability_insurance"),
            ],
            heading="Gesellschaft (gilt ab Stufe „Gesellschaft“)",
        ),
    ]

    # Ohne diese Angaben geht keine Gesellschaft online – ein halbes Impressum verhindert die Prüfung.
    REQUIRED_FOR_COMPANY = (
        "company_name",
        "legal_form",
        "managing_directors",
        "street",
        "postal_city",
        "register_court",
        "register_number",
    )

    class Meta:
        verbose_name = "Unternehmensangaben"

    def clean(self):
        super().clean()
        if self.stage == STAGE_COMPANY:
            missing = {
                field: "Pflichtangabe für die Stufe „Gesellschaft“."
                for field in self.REQUIRED_FOR_COMPANY
                if not (getattr(self, field) or "").strip()
            }
            if missing:
                raise ValidationError(missing)

    @property
    def is_company(self) -> bool:
        return self.stage == STAGE_COMPANY

    @property
    def show_founding_notice(self) -> bool:
        return not self.is_company and self.announce_founding

    def entity(self) -> LegalEntity:
        if not self.is_company:
            return PRE_FOUNDING
        register = ", ".join(p for p in (self.register_court.strip(), self.register_number.strip()) if p)
        return LegalEntity(
            name=self.company_name.strip(),
            addition="",
            legal_form=self.legal_form.strip(),
            representation_label="Geschäftsführung",
            representation=self.managing_directors.strip(),
            street=self.street.strip(),
            postal_city=self.postal_city.strip(),
            phone=self.phone.strip(),
            vat_id=self.vat_id.strip(),
            register=register,
            founded=self.founded.strip(),
            liability_insurance=self.liability_insurance.strip(),
        )
