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

- **24 Marketing-Pages** — Produkt, Preise, Kommunen, Migration, Trust Center,
  Transparenzbericht, Barrierefreiheit, Abuse, Open Source, Mitmachen, Partner,
  Über uns, Presse, Kontakt, FAQ, Blog, Releases, Impressum, Datenschutz, AGB,
  Quellen + 2 Sub-Pages (Status, Disclosure)
- **Wagtail 7 CMS** für inhaltliche Pflege durch Nicht-Entwickler:innen
- **Mandari Design System** — konsistentes UI mit Tailwind CSS, Hero-Banner,
  Trust-Banner, Border-2-Cards mit Decorative Corner Circles
- **Discoverability** — `robots.txt`, `sitemap.xml`, RFC 8288 Link-Header,
  `.well-known/security.txt`
- **Compliance** — DSGVO, BFSG, DSA, NetzDG, RFC 9116 (Responsible Disclosure)
- **Status Page** via [Kener](https://github.com/rajnandan1/kener) (eingebunden)
- **DSGVO-konformer Spam-Schutz** via [Altcha](https://altcha.org)
  (selbst-gehostet, kein Captcha, kein Tracking)

## 🚀 Quickstart (Docker, empfohlen)

```bash
# 1. Repo klonen
git clone https://github.com/mandariOSS/marketing-website.git
cd marketing-website

# 2. Optional: Eigene .env anlegen (Defaults reichen für lokal)
cp .env.example .env

# 3. Stack starten (Postgres + Wagtail + Kener)
docker compose up -d --build

# 4. Initiale Wagtail-Seitenstruktur anlegen
docker compose exec website python manage.py setup_initial_pages

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
├── website/                  # Django-Projekt (Settings, URLs, ASGI/WSGI)
├── marketing/                # App: Marketing-Pages (Wagtail-Models, Views, Middleware)
│   ├── models.py             # MarketingPage, ContactPage, LegalPage, HomePage
│   ├── views.py              # status_view, security_txt, robots_txt, altcha
│   ├── middleware.py         # LinkHeaderMiddleware (RFC 8288)
│   └── management/commands/
│       └── setup_initial_pages.py   # Idempotente Seitenstruktur
├── blog/                     # App: Blog + Releases (Wagtail BlogIndex)
├── templates/
│   ├── base.html             # Globales Layout
│   ├── components/           # navbar, footer
│   └── marketing/            # Page-Templates (produkt, preise, trust, ...)
├── static/
│   ├── css/                  # Tailwind input + compiled output
│   ├── vendor/               # alpine, lucide, altcha (lokal gehostet)
│   └── security/             # PGP-Key-Placeholder
├── scripts/                  # Kener-Bootstrap & Utilities
├── docker-compose.yml        # Wagtail + Postgres + Kener + Redis
├── Dockerfile
└── tailwind.config.js
```

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
