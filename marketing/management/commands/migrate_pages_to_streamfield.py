"""
Management Command: Migriert Marketing-Pages auf das StreamField-System.

Übernimmt die Inhalte aus den hardcoded HTML-Templates und übersetzt sie in
strukturierte StreamField-Blöcke, die im Wagtail-Admin pflegbar sind.

Idempotent: kann mehrfach laufen, überschreibt aber bestehende body-Inhalte
nur mit --force.

Usage:
    python manage.py migrate_pages_to_streamfield                  # alle Pages
    python manage.py migrate_pages_to_streamfield --pages transparenz kontakt
    python manage.py migrate_pages_to_streamfield --force          # überschreibt
"""

from __future__ import annotations

import json

from django.core.management.base import BaseCommand
from wagtail.blocks import StreamValue


# ─────────────────────────── Page-Definitionen ─────────────────────────


def get_page_definitions() -> dict:
    """Maps slug → list of (block_type, value_dict) tuples to be set as body."""

    return {
        # ──────────────────────────────────────────────────────────────
        # /transparenz/ — Quartals-Update-Bericht
        # ──────────────────────────────────────────────────────────────
        "transparenz": [
            ("hero", {
                "badge_text": "Transparenzbericht · jährlich",
                "badge_icon": "eye",
                "badge_color": "primary",
                "title": "Transparenzbericht",
                "title_highlight": "2026",
                "subline": "Was andere SaaS gerne verstecken, legen wir offen: Behördenanfragen, Sicherheitsvorfälle, Finanzlage, Hosting-Realität, Open-Source-Beiträge.",
                "subline_secondary": "Berichtszeitraum: 1. Januar bis 31. Dezember 2026 · Veröffentlicht: 26. April 2026 · Nächste Aktualisierung: Juli 2026",
                "ctas": [],
                "background_color": "primary",
            }),
            ("trust_banner", {
                "color": "primary",
                "items": [
                    {"icon": "gavel", "label_bold": "0", "label_normal": "Behörden­anfragen"},
                    {"icon": "shield-check", "label_bold": "0", "label_normal": "Sicherheits­vorfälle"},
                    {"icon": "user", "label_bold": "1", "label_normal": "Solo-Founder"},
                    {"icon": "git-pull-request", "label_bold": "100 %", "label_normal": "Code offen"},
                ],
            }),
            ("stats_grid", {
                "header": {
                    "badge_text": "01 · Behördenanfragen",
                    "badge_icon": "gavel",
                    "badge_color": "blue",
                    "title": "Behördenanfragen",
                    "subline": "Auskunfts­ersuchen, Beschlagnahmungen, Auskunfts­anordnungen, alles, was rechtlich an uns herangetragen wurde.",
                    "align": "left",
                },
                "columns": "4",
                "border_color": "blue",
                "items": [
                    {"value": "0", "label": "Strafverfolgung", "color": "blue"},
                    {"value": "0", "label": "Geheimdienste", "color": "blue"},
                    {"value": "0", "label": "Zivilrechtlich", "color": "blue"},
                    {"value": "0", "label": "Datenherausgaben", "color": "blue"},
                ],
            }),
            ("warrant_canary", {
                "date": "26.04.2026",
                "body": "<p>Mandari wurde nicht durch eine Geheim­halte­anordnung (z.&nbsp;B. nach § 95 GWB oder § 100b StPO) verpflichtet, Auskünfte unter Geheimhaltung zu erteilen.</p><p>Diese Erklärung wird vierteljährlich aktualisiert. Sollte sie verschwinden oder veralten, interpretiere das entsprechend.</p>",
            }),
            ("stats_grid", {
                "header": {
                    "badge_text": "02 · Sicherheitsvorfälle",
                    "badge_icon": "shield-alert",
                    "badge_color": "rose",
                    "title": "Sicherheitsvorfälle",
                    "subline": "Datenschutz­vorfälle, Sicherheits­lücken, Downtime mit Datenrelevanz.",
                    "align": "left",
                },
                "columns": "3",
                "border_color": "green",
                "items": [
                    {"value": "0", "label": "Datenschutz­vorfälle", "color": "green"},
                    {"value": "0", "label": "Gemeldete CVEs", "color": "green"},
                    {"value": "0", "label": "DSGVO-Meldungen", "color": "green"},
                ],
            }),
            ("stats_grid", {
                "header": {
                    "badge_text": "03 · Nutzung & Reichweite",
                    "badge_icon": "bar-chart-3",
                    "badge_color": "green",
                    "title": "Nutzung & Reichweite",
                    "subline": "Anonymisierte Aggregate, keine individuellen Profile, keine Tracker.",
                    "align": "left",
                },
                "columns": "4",
                "border_color": "primary",
                "items": [
                    {"value": "0", "label": "Pilot-Kommunen live", "color": "green"},
                    {"value": "~12", "label": "Erstgespräche geführt", "color": "amber"},
                    {"value": "~3 k", "label": "Insight-Aufrufe / Mon", "color": "primary"},
                    {"value": "2", "label": "OParl-Quellen indiziert", "color": "blue"},
                ],
            }),
            ("disclaimer_box", {
                "icon": "info",
                "color": "amber",
                "body": "<p><strong>Reality Check:</strong> Wir sind in der Beta-Phase. Diese Zahlen sind klein, und genau deshalb veröffentlichen wir sie. Wir gewinnen nichts, indem wir uns größer machen, als wir sind.</p>",
            }),
            ("two_column_use_case", {
                "header": {
                    "badge_text": "04 · Finanztransparenz",
                    "badge_icon": "banknote",
                    "badge_color": "teal",
                    "title": "Finanztransparenz",
                    "subline": "Solo-Founder-Vorteil: ich kann offen zeigen, wie das Geld fließt.",
                    "align": "left",
                },
                "left_card": {
                    "color": "green",
                    "icon": "trending-up",
                    "title": "Einnahmen 2026",
                    "subtitle": "~ 0 € · Beta-Phase",
                    "description": "Beta-Phase, noch keine Lizenzeinnahmen.",
                    "bullets": [
                        {"icon": "circle-dot", "text": "Work-Lizenzen: noch nicht aktiv"},
                        {"icon": "circle-dot", "text": "Spenden: 0 € (Konzept in Vorbereitung)"},
                        {"icon": "circle-dot", "text": "Fördermittel: in Beantragung"},
                    ],
                    "cta_label": "",
                    "cta_url": "",
                    "cta_icon": "",
                    "badge": "",
                },
                "right_card": {
                    "color": "rose",
                    "icon": "trending-down",
                    "title": "Ausgaben 2026",
                    "subtitle": "~ 1.200 € hochgerechnet",
                    "description": "Hochgerechnet auf das Jahr (laufende Kosten).",
                    "bullets": [
                        {"icon": "server", "text": "Hosting (Hetzner): ~ 60 €/Mon"},
                        {"icon": "globe", "text": "Domain & DNS: ~ 30 €/Jahr"},
                        {"icon": "briefcase", "text": "Tools & Buchhaltung: ~ 40 €/Mon"},
                        {"icon": "brain", "text": "KI-Inferenz Tests: ~ 20 €/Mon"},
                    ],
                    "cta_label": "",
                    "cta_url": "",
                    "cta_icon": "",
                    "badge": "",
                },
            }),
            ("mandari_cards", {
                "header": {
                    "badge_text": "07 · So kannst du beitragen",
                    "badge_icon": "hand-heart",
                    "badge_color": "green",
                    "title": "So kannst du beitragen",
                    "subline": "Wenn dir Mandari etwas wert ist: vier Wege, das Projekt finanziell mitzutragen.",
                    "align": "left",
                },
                "columns": "4",
                "background": "white",
                "cards": [
                    {
                        "color": "primary",
                        "icon": "github",
                        "title": "GitHub Sponsors",
                        "subtitle": "0 % Plattformgebühr",
                        "description": "Für Devs und Tech-Community. Monatlich oder einmalig.",
                        "bullets": [],
                        "cta_label": "Öffnen",
                        "cta_url": "https://github.com/sponsors/mandariOSS",
                        "cta_icon": "external-link",
                        "badge": "",
                    },
                    {
                        "color": "amber",
                        "icon": "coffee",
                        "title": "Ko-fi",
                        "subtitle": "3 € reicht schon",
                        "description": "Niedrigschwellig. „Spendier dem Founder einen Kaffee.\"",
                        "bullets": [],
                        "cta_label": "Öffnen",
                        "cta_url": "https://ko-fi.com/mandari",
                        "cta_icon": "external-link",
                        "badge": "",
                    },
                    {
                        "color": "rose",
                        "icon": "cookie",
                        "title": "Buy Me a Coffee",
                        "subtitle": "Ein-Klick-Tip",
                        "description": "Ohne Account, ohne Hürde. PayPal oder Karte.",
                        "bullets": [],
                        "cta_label": "Öffnen",
                        "cta_url": "https://buymeacoffee.com/mandari",
                        "cta_icon": "external-link",
                        "badge": "",
                    },
                    {
                        "color": "green",
                        "icon": "banknote",
                        "title": "SEPA-Direkt",
                        "subtitle": "0 % Gebühren",
                        "description": "Für Kommunen, Stiftungen, Großspender. Bankdaten auf Anfrage.",
                        "bullets": [],
                        "cta_label": "Anfragen",
                        "cta_url": "/kontakt/?subject=SEPA-Spende-Bankdaten",
                        "cta_icon": "mail",
                        "badge": "",
                    },
                ],
            }),
            ("disclaimer_box", {
                "icon": "info",
                "color": "gray",
                "body": "<p><strong>Ehrlich gesagt:</strong> Spenden sind aktuell <em>nicht</em> steuerlich absetzbar, da Mandari als Einzelunternehmen aufgestellt ist. Eine Überführung in eine <strong>gemeinwohlorientierte Trägerstruktur</strong> (z.&nbsp;B. e.&nbsp;V., Genossenschaft, gGmbH oder Verantwortungseigentum) prüfen wir für 2027, sobald die Pilot-Phase Fahrt aufnimmt.</p>",
            }),
            ("gradient_cta", {
                "title": "Vermisst du eine Zahl?",
                "subline": "Wenn du etwas spezifisches sehen möchtest, Energie­verbrauch, CO₂-Bilanz, Code-Qualitäts­metriken, sag Bescheid. Wir nehmen es auf.",
                "ctas": [
                    {"label": "Vorschlag einreichen", "url": "/kontakt/?subject=Transparenzbericht-Vorschlag", "icon": "message-square", "style": "primary"},
                    {"label": "Updates abonnieren", "url": "/blog/feed/", "icon": "rss", "style": "outline"},
                ],
                "gradient_from": "primary",
            }),
        ],
    }


# ─────────────────────────── Command-Klasse ────────────────────────────


class Command(BaseCommand):
    help = "Migriert Marketing-Pages auf das StreamField-System."

    def add_arguments(self, parser):
        parser.add_argument(
            "--pages",
            nargs="+",
            type=str,
            default=None,
            help="Optionale Liste von Slugs (Default: alle definierten Pages)",
        )
        parser.add_argument(
            "--force",
            action="store_true",
            help="Überschreibt bestehende body-Inhalte",
        )

    def handle(self, *args, **options):
        from marketing.models import MarketingPage
        from marketing.blocks import MarketingStreamBlock

        definitions = get_page_definitions()
        slugs = options["pages"] or list(definitions.keys())
        force = options["force"]

        stream_block = MarketingStreamBlock()

        for slug in slugs:
            if slug not in definitions:
                self.stdout.write(self.style.WARNING(f"  {slug}/ - keine Definition gefunden, übersprungen"))
                continue

            page = MarketingPage.objects.filter(slug=slug).first()
            if not page:
                self.stdout.write(self.style.ERROR(f"  {slug}/ - Page nicht in DB, übersprungen"))
                continue

            # Body bereits gefüllt?
            existing_body = page.body
            if existing_body and len(list(existing_body)) > 0 and not force:
                self.stdout.write(self.style.WARNING(
                    f"  {slug}/ - body bereits gefüllt ({len(list(existing_body))} Blöcke), --force zum Überschreiben"
                ))
                continue

            # Body als StreamValue setzen (tuple-format with is_lazy=False)
            blocks_data = definitions[slug]
            page.body = StreamValue(stream_block, blocks_data, is_lazy=False)

            # custom_template leeren — Page rendert über das Universal-Template
            old_template = page.custom_template
            page.custom_template = ""

            # Speichern + neue Revision
            page.save()
            page.save_revision().publish()

            self.stdout.write(self.style.SUCCESS(
                f"  ✓ {slug}/ - {len(blocks_data)} Blöcke gesetzt (custom_template '{old_template}' → leer)"
            ))

        self.stdout.write("")
        self.stdout.write(self.style.SUCCESS("Migration fertig."))
