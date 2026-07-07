# Mandari Marketing Website

[![License: AGPL v3](https://img.shields.io/badge/License-AGPL_v3-blue.svg)](https://www.gnu.org/licenses/agpl-3.0)
[![Python 3.12+](https://img.shields.io/badge/python-3.12+-blue.svg)](https://www.python.org/downloads/)
[![Django 6.0](https://img.shields.io/badge/django-6.0-green.svg)](https://www.djangoproject.com/)
[![Wagtail 7](https://img.shields.io/badge/wagtail-7-teal.svg)](https://wagtail.org/)

Die öffentliche Marketing-Website von [Mandari](https://mandari.de) — dem
Open-Source-Ratsinformationssystem für deutsche Kommunen.

Diese Website ist **eigenständig** vom Hauptprojekt
[`mandariOSS/mandari`](https://github.com/mandariOSS/mandari) und kann
separat gehostet und entwickelt werden.

## ✨ Was enthält dieses Repo?

- **Marketing-Pages** — Startseite, Produkt, Preise, Kommunen, Migration,
  Roadmap, Trust Center, Transparenzbericht, Barrierefreiheit, Abuse,
  Open Source, Mitmachen, Partner, Über uns, Presse, Kontakt, Blog, Releases
- **Rechtliche Seiten** — Impressum, Datenschutz, AGB, AVV (Muster-Auftrags-
  verarbeitungsvertrag nach Art. 28 DSGVO), Quellennachweise — Texte liegen
  versioniert in `.legal-content/` (siehe unten)
- **Django-Views** außerhalb von Wagtail — `/status/` (Live-Status via Kener-API)
  und `/sicherheit/disclosure/` (Responsible Disclosure)
- **Wagtail 7 CMS** für inhaltliche Pflege durch Nicht-Entwickler:innen —
  alle Seiten bestehen aus **StreamField-Blöcken** des Mandari Design Systems
  (`marketing/blocks.py`: Hero, Trust-Banner, Mandari-Cards, Pricing-Tabelle,
  Schritt-Prozess, FAQ-Akkordeon, Stats-Grid, Gradient-CTA u. v. m.)
- **Mandari Design System** — konsistentes UI mit Tailwind CSS, Hero-Banner,
  Trust-Banner, Border-2-Cards mit Decorative Corner Circles
- **Discoverability** — `robots.txt`, `sitemap.xml`, RFC 8288 Link-Header,
  `.well-known/security.txt`
- **Compliance** — DSGVO, BFSG, DSA, NetzDG, RFC 9116 (Responsible Disclosure)
- **Status Page** via [Kener](https://github.com/rajnandan1/kener) — produktiv
  unter <https://status.mandari.de>, lokal im Compose-Stack enthalten
- **DSGVO-konformer Spam-Schutz** via [Altcha](https://altcha.org)
  (selbst-gehostet, kein Captcha, kein Tracking)

## 📝 Content-Architektur: Seeds & Rechtstexte

Die Website deployt gegen eine Datenbank, in der Seiten bereits existieren —
alle Seeds sind deshalb **idempotent**:

| Command | Zweck |
|---|---|
| `setup_initial_pages` | Erstellt den Wagtail-Page-Tree (überspringt vorhandene Seiten), seedet Rechtstexte aus `.legal-content/` |
| `migrate_pages_to_streamfield` | Seedet die StreamField-Inhalte aller Marketing-/Legal-Pages (überspringt Seiten, die bereits Blöcke haben; `--force` überschreibt) |
| `refresh_seeded_page <slug> [--force]` | Wendet die Seed-Definition **einer** Seite erneut an — für Live-Updates nach Deploys, z. B. `refresh_seeded_page trust --force` |

**Rechtstexte** (Impressum, Datenschutz, AGB, AVV) werden **nicht** in
Templates oder im Code gepflegt: Die authoritative Fassung liegt als HTML in
`.legal-content/*.html`, wird über `marketing/legal_content.py` geladen und in
das RichText-Feld `LegalPage.body` geseedet (gerendert via
`marketing/legal_page.html`). Änderungen an Rechtstexten gehören in
`.legal-content/` und werden auf laufenden Instanzen mit
`refresh_seeded_page <slug> --force` ausgerollt.

## 🚀 Quickstart (Docker, empfohlen)

```bash
# 1. Repo klonen
git clone https://github.com/mandariOSS/marketing-website.git
cd marketing-website

# 2. Optional: Eigene .env anlegen (Defaults reichen für lokal)
cp .env.example .env

# 3. Stack starten (Postgres + Wagtail + Kener)
docker compose up -d --build

# 4. Initiale Wagtail-Seitenstruktur anlegen + Inhalte seeden
docker compose exec website python manage.py setup_initial_pages
docker compose exec website python manage.py migrate_pages_to_streamfield

# 5. Admin-Account erstellen
docker compose exec website python manage.py createsuperuser
```

Anschließend:

| URL | Beschreibung |
|---|---|
| <http://localhost:6500/> | Marketing-Website |
| <http://localhost:6500/cms-admin/> | Wagtail-Admin (CMS) |
| <http://localhost:6500/admin/> | Django-Admin |
| <http://localhost:6501/> | Kener Status-Page |

## 🛠 Lokale Entwicklung (ohne Docker)

```bash
# Python 3.12+ und Node 20+ vorausgesetzt
pip install -e .
npm install

# Tailwind im Watch-Mode
npm run dev   # build → dist
# oder direkt:
npx tailwindcss -i static/css/input.css -o static/css/styles.css --watch

# Postgres läuft separat — DATABASE_URL anpassen in .env
python manage.py migrate
python manage.py setup_initial_pages
python manage.py migrate_pages_to_streamfield
python manage.py runserver 8001
```

## 🏗 Tech-Stack

| Bereich | Technologie | Lizenz |
|---|---|---|
| Backend | Django 6, Wagtail 7 | BSD-3 |
| Datenbank | PostgreSQL 16 | PostgreSQL |
| Frontend | HTMX + Alpine.js + Tailwind CSS 3 | MIT / BSD |
| Icons | [Lucide](https://lucide.dev) | ISC |
| Suche | Wagtail-Builtin | BSD-3 |
| Status | [Kener](https://github.com/rajnandan1/kener) | MIT |
| Spam-Schutz | [Altcha](https://altcha.org) v2 | MIT |
| Deployment | Docker Compose, Gunicorn, WhiteNoise | Apache-2.0 |

## 📁 Projekt-Struktur

```
marketing-website/
├── website/                  # Django-Projekt (Settings, URLs, WSGI)
├── marketing/                # App: Marketing-Pages (Wagtail-Models, Views, Middleware)
│   ├── models.py             # HomePage, MarketingPage, ContactPage, LegalPage
│   ├── blocks.py             # StreamField-Blöcke des Mandari Design Systems
│   ├── legal_content.py      # Lädt Rechtstexte aus .legal-content/
│   ├── views.py              # status_view, security_txt, robots_txt, altcha
│   ├── middleware.py         # LinkHeaderMiddleware (RFC 8288)
│   └── management/commands/
│       ├── setup_initial_pages.py          # Idempotenter Page-Tree + Legal-Seeds
│       ├── migrate_pages_to_streamfield.py # StreamField-Inhalte aller Seiten
│       └── refresh_seeded_page.py          # Re-Seed einer Seite (Live-Update)
├── blog/                     # App: Blog + Releases (Wagtail BlogIndex)
├── .legal-content/           # Authoritative Rechtstexte (impressum, datenschutz, agb, avv)
├── templates/
│   ├── base.html             # Globales Layout
│   ├── components/           # navbar, footer
│   └── marketing/            # Page-Templates + blocks/ (StreamField-Block-Templates)
├── static/
│   ├── css/                  # Tailwind input + compiled output
│   ├── vendor/               # alpine, lucide, altcha (lokal gehostet)
│   └── security/             # PGP-Key
├── scripts/                  # Kener-Bootstrap & Utilities
├── .github/workflows/        # CI: Release-Build → ghcr.io/mandarioss/website
├── docker-compose.yml        # Lokaler Stack: Wagtail + Postgres + Kener + Redis
├── Dockerfile
└── tailwind.config.js
```

## 🚢 CI & Deployment

- **CI**: Jeder Push auf `main`/`dev` baut das Docker-Image und pusht es nach
  **`ghcr.io/mandarioss/website`** (Tags: `<branch>` und `<branch>-<shortsha>`,
  siehe `.github/workflows/release.yml`).
- **Produktion**: Die Website läuft als `website`-Service im
  Docker-Compose-Stack des Hauptrepos
  [`mandariOSS/mandari`](https://github.com/mandariOSS/mandari) auf dem
  Mandari-Server. Caddy routet dort auf **einer Domain**: `/insight/`, `/work/`,
  `/session/`, `/api/`, … → Django-App; alles andere (inkl. `/`) → diese
  Wagtail-Website. Die Statuspage läuft unter <https://status.mandari.de>.
- **Deploys gegen bestehende DB**: Migrationen + idempotente Seeds laufen beim
  Start; gezielte Inhalts-Updates per `refresh_seeded_page <slug> --force`.

### Wichtige Umgebungsvariablen

| Variable | Default | Zweck |
|---|---|---|
| `WEBSITE_SECRET_KEY` / `SECRET_KEY` | dev-Wert | Django Secret Key |
| `DEBUG` | `True` | Debug-Modus (Production: `False`) |
| `SITE_URL` | `http://localhost:8001` | Öffentliche Basis-URL (robots.txt, security.txt, CSRF) |
| `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` | localhost | Host-/Origin-Whitelist |
| `WEBSITE_DATABASE_URL` / `DATABASE_URL` | lokaler Postgres | PostgreSQL-Verbindung |
| `STATUS_PAGE_URL` | `https://status.mandari.de` | Öffentlicher Link zur Statuspage |
| `KENER_INTERNAL_URL` | `http://kener:3000` | Interne Kener-API (für /status/) |
| `KENER_API_TOKEN` | – | Token für die Kener-API (ohne: Fallback-Link) |
| `MANDARI_API_URL` | `http://mandari:8000/api` | Stats-API der Haupt-App (Startseite) |
| `BOOKING_URL` | `/kontakt/#termin-buchen` | Ziel der „Call buchen"-CTAs |
| `ALTCHA_HMAC_KEY` | dev-Wert | HMAC-Secret für Altcha-Challenges |
| `TZ` | `Europe/Berlin` | Zeitzone |

## 🎨 Mandari Design System

Alle Pages folgen demselben visuellen Vokabular:

- **Hero linksbündig** mit Badge + H1 + highlighted span + Subline + CTAs
- **Trust-Banner** mit 4 Eckdaten (Icon + Bold-Label + Erklärung)
- **3- oder 6-Spalten-Cards** mit `border-2 border-{color}-200` + Decorative
  Corner Circle (`absolute top-0 right-0 w-32 h-32 rounded-bl-full -mr-8 -mt-8`)
- **Color-System**: green / primary (Indigo) / blue als Trio, plus amber, rose,
  teal als sekundäre Akzente
- **Final CTA** mit `bg-gradient-to-br from-primary-600 to-primary-800`
- Standard-Tailwind-Klassen (lg:, md:, sm:) — keine xl: oder col-span-N-Tricks

## 🤝 Mitmachen

Issues und Pull Requests willkommen — siehe
[CONTRIBUTING.md](CONTRIBUTING.md) und unsere
[Mitmachen-Seite](https://mandari.de/mitmachen/).

Du kannst Mandari auch finanziell unterstützen:

- [GitHub Sponsors](https://github.com/sponsors/mandariOSS)
- [Ko-fi](https://ko-fi.com/mandari)
- [Buy Me a Coffee](https://buymeacoffee.com/mandari)
- Oder über die [Transparenz-Seite](https://mandari.de/transparenz/#unterstuetzen)

## 📜 Lizenz

Mandari ist [AGPL-3.0](LICENSE) lizenziert — siehe Datei `LICENSE` und
<https://mandari.de/open-source/>.

## 🛡 Sicherheit

Sicherheitslücken bitte gemäß unserer
[Responsible-Disclosure-Policy](https://mandari.de/sicherheit/disclosure/)
melden — siehe auch [`security.txt`](https://mandari.de/.well-known/security.txt)
und [SECURITY.md](SECURITY.md).

## 📞 Kontakt

- **Allgemein**: [hi@mandari.de](mailto:hi@mandari.de)
- **Sicherheit**: [security@mandari.de](mailto:security@mandari.de)
- **Datenschutz**: [privacy@mandari.de](mailto:privacy@mandari.de)
- **Missbrauch**: [abuse@mandari.de](mailto:abuse@mandari.de)
- **Founder**: Sven Konopka, [topixmedia.de](https://topixmedia.de), Münster

---

Made with ❤ for transparent local democracy.
