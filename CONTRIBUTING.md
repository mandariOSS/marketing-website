# Contributing zu Mandari Marketing Website

Schön, dass du beitragen möchtest! Hier ist alles, was du brauchst, um in unter
30 Minuten produktiv zu werden.

## Was wir suchen

| Art | Schwierigkeit | Zeitaufwand |
|---|---|---|
| Tippfehler / Doku-Verbesserungen | Erste Hilfe | 5 Min |
| Bug-Reports mit Screenshot | Erste Hilfe | 15 Min |
| Übersetzungen (EN, FR, NL, …) | Mittel | 2–10 Std |
| UI-Verbesserungen (mit Mandari Design System) | Mittel | 1–4 Std |
| Neue Wagtail-Page + Template | Mittel | 2–6 Std |
| Performance-Optimierungen | Mittel–Profi | 4 Std+ |
| WCAG-AA-Audit + Fixes | Profi | mehrtägig |

## Quickstart für Contributors

```bash
# 1. Fork + clone
git clone https://github.com/YOUR-USERNAME/marketing-website.git
cd marketing-website

# 2. Stack starten
docker compose up -d --build
docker compose exec website python manage.py setup_initial_pages
docker compose exec website python manage.py createsuperuser

# 3. Branch anlegen
git checkout -b fix/short-description
```

## Pull Request Workflow

1. **Issue zuerst** (für größere Änderungen): kurze Beschreibung + Akzeptanzkriterien
2. **Branch-Naming**: `fix/...`, `feat/...`, `docs/...`, `chore/...`
3. **Commits**: Conventional Commits empfohlen
   ```
   feat(transparenz): Quartals-Update Q1/2026 mit neuen Zahlen
   fix(navbar): Vertrauen-Dropdown auf Mobile verschoben
   docs(readme): Quickstart aktualisiert
   ```
4. **PR-Beschreibung**: was/warum, Screenshots bei UI-Änderungen
5. **Review**: Wir reviewen persönlich und zeitnah

## Mandari Design System einhalten

Alle neuen Pages folgen demselben visuellen Vokabular — siehe
[`templates/marketing/produkt.html`](templates/marketing/produkt.html) als
Referenz:

- **Hero linksbündig** (`pt-16 pb-10 lg:pt-24 lg:pb-12 bg-gradient-to-br from-primary-50 to-white`)
- **Trust-Banner** (`py-8 bg-{color}-50 border-y border-{color}-200`, 4 Items)
- **Border-2 Cards** mit Decorative Corner Circle
- **Color-Trio**: green / primary / blue + amber / rose / teal als Akzente
- **Final CTA**: `bg-gradient-to-br from-primary-600 to-primary-800`
- **Standard-Tailwind-Klassen** (lg:, md:, sm:) — KEINE xl: oder col-span-N

## Code-Stil

- **Python**: PEP 8, formatiert mit `ruff format`
- **HTML/Templates**: 4-Space-Indent, semantische Tags, ARIA-Labels
- **CSS**: nur Tailwind-Utility-Klassen, kein Custom-CSS außer in `base.html`
- **JS**: minimal — Alpine.js für Reaktivität, HTMX für Interaktionen

## Sprachregelung

- **Gendergerechte Sprache** mit Doppelpunkt: „Bürger:innen", „Mandatsträger:innen"
- **Du-Form** auf der ganzen Website
- Bei offiziellen Dokumenten (Quellen) Originalschreibweise übernehmen
- Em-Dashes „— " sparsam einsetzen, im Deutschen meist Komma oder Punkt

## Commit-Hooks (optional)

```bash
pip install pre-commit
pre-commit install
```

## Code of Conduct

Wir folgen dem
[Contributor Covenant 2.1](https://www.contributor-covenant.org/de/version/2/1/code_of_conduct/).
Verstöße bitte direkt an [conduct@mandari.de](mailto:conduct@mandari.de).

## Lizenz-Hinweis

Mit dem Einreichen einer PR stimmst du zu, dass dein Beitrag unter der
[AGPL-3.0](LICENSE) lizenziert wird.

## Fragen?

- [GitHub Discussions](https://github.com/mandariOSS/marketing-website/discussions)
- E-Mail: [hi@mandari.de](mailto:hi@mandari.de)
- Mitmachen-Übersicht: <https://mandari.de/mitmachen/>
