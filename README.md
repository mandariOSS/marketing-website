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

- **Marketing-Pages** — Startseite, Produkte, Für Fraktionen, Preise, Kommunen, Migration,
  Roadmap, Trust Center, Transparenzbericht, Barrierefreiheit, Abuse,
  Open Source, Mitmachen, Partner, Über uns, Presse, Kontakt, Releases
  (der Blog ruht, siehe [Blog reaktivieren](#blog-reaktivieren))
- **Rechtliche Seiten** — Impressum, Datenschutz, AGB, AVV (Muster-Auftrags-
  verarbeitungsvertrag nach Art. 28 DSGVO), Quellennachweise — Texte liegen
  versioniert in `.legal-content/` (siehe unten)
- **Django-Views** außerhalb von Wagtail — `/sicherheit/disclosure/`
  (Responsible Disclosure) und `/crawler/` (Infoseite zum Crawler);
  `/status/` leitet dauerhaft auf <https://status.mandari.de/>
- **Wagtail 7 CMS** für inhaltliche Pflege durch Nicht-Entwickler:innen —
  alle Seiten bestehen aus **StreamField-Blöcken** des Mandari Design Systems
  (`marketing/blocks.py`: Hero, Trust-Banner, Mandari-Cards, Pricing-Tabelle,
  Schritt-Prozess, FAQ-Akkordeon, Stats-Grid, Zeilen, Einladung u. v. m.)
- **Ruhige Gestaltung** mit Tailwind CSS — Schriftstufen, ein Button-Stil und
  Textlinks als Komponenten, Inhalte offen auf der Fläche (siehe [Gestaltung](#-gestaltung))
- **Discoverability** — `robots.txt`, `sitemap.xml` (Adressen und `lastmod` aus
  `SITE_URL`), Canonical/og:url aus `SITE_URL`, Meta-Description aus
  `search_description`, RFC 8288 Link-Header, `.well-known/security.txt`
- **Compliance** — DSGVO, BFSG, DSA, NetzDG, RFC 9116 (Responsible Disclosure)
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
| `retire_page <pfad\|slug> --redirect <ziel> [--dry-run]` | Zieht eine Seite samt Unterseiten zurück (unpublish, bleibt im CMS) und legt eine dauerhafte Weiterleitung an bzw. korrigiert sie; prüft danach per Anfrage, dass der alte Pfad mit 301 auf das Ziel zeigt. Idempotent, z. B. `retire_page /blog/ --redirect /releases/` |

**Seiten zurückziehen:** Fällt eine Seite bei einem Umbau weg, zuerst die
Zielseite anlegen (`setup_initial_pages`), dann `retire_page` ausführen. Interne
Ziele müssen existieren, sonst bricht der Befehl ab, bevor er etwas ändert. Ziele
mit Anker (`/kontakt/#termin`) und externe Adressen sind erlaubt. Zurückgezogene
Seiten verschwinden aus Sitemap und Struktur-Test; über den Wagtail-Admin lassen
sie sich jederzeit wieder veröffentlichen.

### Blog reaktivieren

Der Blog ruht, solange es keine Beiträge gibt: `/blog/` und `/blog/feed/` leiten
dauerhaft auf `/releases/` (`website/urls.py`), ein vorhandener Blog-Index wird
mit `retire_page /blog/ --redirect /releases/` zurückgezogen. Der Code bleibt
vollständig erhalten (`blog/models.py`, `blog/feeds.py`, `templates/blog/`).
Zum Reaktivieren:

1. In `website/urls.py` die beiden Weiterleitungen für `blog/` und `blog/feed/`
   entfernen und den Feed wieder eintragen:
   `path("blog/feed/", BlogFeed(), name="blog_feed")` (Import `from blog.feeds import BlogFeed`).
2. Die Wagtail-Weiterleitung `/blog` im Admin unter *Einstellungen → Weiterleitungen* löschen.
3. Den Blog-Index im Admin wieder veröffentlichen – oder auf neuen Datenbanken
   `BLOG_ENABLED = True` in `marketing/management/commands/setup_initial_pages.py`
   setzen und `setup_initial_pages` ausführen.
4. Den Blog in Fußzeile (`templates/components/footer.html`) und Struktur-Test
   (`scripts/check_site_structure.py`, Liste `FUSSZEILE`) aufnehmen; optional
   `<link rel="alternate" type="application/rss+xml" href="/blog/feed/">` in `templates/base.html`.

### Struktur-Test

`scripts/check_site_structure.py` verfolgt ausgehend von `/` alle internen Links
mit dem Django-Test-Client und prüft: keine internen Links auf 404, jede
veröffentlichte Seite verlinkt (Unterseiten von ihrer Elternseite), eindeutige
Titel der Form „<Titel> | mandari“, eindeutige Meta-Descriptions, Canonical aus
`SITE_URL`, Kopf- und Fußzeile genau nach Zielstruktur. Die CI führt ihn nach den
Seeds aus; lokal:

```bash
SITE_URL=https://mandari.de python scripts/check_site_structure.py   # --strict: ausstehende Ziele als Fehler
python manage.py test --buffer                                         # Unit-Tests (retire_page, SEO, Weiterleitungen)
```

**Rechtstexte** (Impressum, Datenschutz, AGB, AVV) werden **nicht** in
Templates oder im Code gepflegt: Die authoritative Fassung liegt als HTML in
`.legal-content/*.html`, wird über `marketing/legal_content.py` geladen und in
das RichText-Feld `LegalPage.body` geseedet (gerendert via
`marketing/legal_page.html`). Änderungen an Rechtstexten gehören in
`.legal-content/` und werden auf laufenden Instanzen mit
`refresh_seeded_page <slug> --force` ausgerollt.

## Unternehmensangaben, Unternehmensseiten und Kontakt

- **Stufenschalter Vorgründung / Gesellschaft:** Wagtail-Admin → *Einstellungen →
  Unternehmensangaben* (App `company`). Standard ist die Vorgründung (Rechtsträger
  topixmedia, Inhaber Sven Konopka). Nach der Eintragung der Gesellschaft Firma,
  Geschäftsführung, Anschrift und Register eintragen und die Stufe umstellen – die
  *Angaben zum Unternehmen* auf `/unternehmen/` und die Anschrift auf `/kontakt/`
  ziehen sofort nach. Ohne Pflichtangaben lässt sich die Stufe nicht speichern.
  Die Rechtstexte in `.legal-content/` schalten **nicht** automatisch um: Sie werden
  geprüft, angepasst und mit `refresh_seeded_page <slug> --force` ausgerollt.
- **Inhalte** von `/unternehmen/`, `/karriere/`, `/presse/`, `/partner/` und
  `/open-source/` stehen in `marketing/seeds_unternehmen.py`, die Kennzahlen der
  Presseseite dort mit Stand. Das Logo-Paket (`/presse/mandari-logopaket.zip`) wird
  aus `static/brand/` gebaut.
- **Kontaktformulare** (`/kontakt/#termin`, `/kontakt/#nachricht`): Altcha-Spamschutz,
  Prüfung in `marketing/contact.py`, Zustellung per SMTP an `CONTACT_TO`
  (Umgebungsvariablen `CONTACT_*`, siehe `.env.example`). `?subject=…` wählt das
  Thema vor. Einmal-Prüfung des Spamschutzes und Begrenzung (fünf Anfragen je Stunde
  und Anschluss, 60 insgesamt) liegen im Datenbank-Zwischenspeicher `formulare`;
  die Tabelle legt `python manage.py createcachetable` an (läuft beim Container-Start).
  Ohne Zustellweg zeigt `/kontakt/` statt der Formulare die Mailadresse.

## 🚀 Quickstart (Docker, empfohlen)

```bash
# 1. Repo klonen
git clone https://github.com/mandariOSS/marketing-website.git
cd marketing-website

# 2. Optional: Eigene .env anlegen (Defaults reichen für lokal)
cp .env.example .env

# 3. Stack starten (Postgres + Wagtail)
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
│   ├── views.py              # security_txt, robots_txt, altcha, Disclosure, Crawler
│   ├── seo.py                # Titel, Meta-Description, Canonical aus SITE_URL
│   ├── sitemaps.py           # Sitemap mit SITE_URL-Adressen und plausiblem lastmod
│   ├── middleware.py         # LinkHeaderMiddleware (RFC 8288)
│   └── management/commands/
│       ├── setup_initial_pages.py          # Idempotenter Page-Tree + Legal-Seeds
│       ├── migrate_pages_to_streamfield.py # StreamField-Inhalte aller Seiten
│       ├── refresh_seeded_page.py          # Re-Seed einer Seite (Live-Update)
│       └── retire_page.py                  # Seite zurückziehen + 301-Weiterleitung
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
├── scripts/                  # Prüfskripte (Struktur-Test, Template-Kommentare) & Utilities
├── .github/workflows/        # CI: Release-Build → ghcr.io/mandarioss/website
├── docker-compose.yml        # Lokaler Stack: Wagtail + Postgres
├── Dockerfile
└── tailwind.config.js
```

## 🚢 CI & Deployment

- **CI**: Jeder Push auf `main`/`dev` baut das Docker-Image und pusht es nach
  **`ghcr.io/mandarioss/website`** (`main`: Tags `main`, `latest` und `main-<shortsha>`;
  `dev`: `dev-<shortsha>`, siehe `.github/workflows/release.yml`). Release-Versionen
  (`v0.11.0`), `dev` und die Commit-Tags der Installation setzt der Release-Workflow von
  [`mandariOSS/mandari`](https://github.com/mandariOSS/mandari) als Kopie von `main`, weil die
  Installation alle drei Images mit einem Tag zieht.
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
| `SITE_URL` | `http://localhost:8001` | Öffentliche Basis-URL: Canonical, og:url, Sitemap, robots.txt, security.txt, CSRF (Produktion: `https://mandari.de`) |
| `ALLOWED_HOSTS` / `CSRF_TRUSTED_ORIGINS` | localhost | Host-/Origin-Whitelist |
| `WEBSITE_DATABASE_URL` / `DATABASE_URL` | lokaler Postgres | PostgreSQL-Verbindung |
| `STATUS_PAGE_URL` | `https://status.mandari.de/` | Öffentliche Statusseite: Ziel von `/status/` und Link in der Fußzeile |
| `BOOKING_URL` | `/kontakt/#termin-buchen` | Ziel der „Call buchen"-CTAs |
| `ALTCHA_HMAC_KEY` | dev-Wert | HMAC-Secret für Altcha-Challenges |
| `CONTACT_SMTP_HOST` / `_PORT` / `_USER` / `_PASSWORD` | – / 465 | SMTP-Zugang für die Kontaktformulare (ohne Host: Mailadresse statt Formular) |
| `CONTACT_FROM` / `CONTACT_TO` | `hello@mandari.de` | Absender und Empfänger der Formular-Mails |
| `CONTACT_TRUSTED_PROXIES` | `1` | Eigene Reverse Proxys vor der Website; bestimmt, welcher `X-Forwarded-For`-Eintrag als Anschluss zählt |
| `TZ` | `Europe/Berlin` | Zeitzone |

## 🎨 Gestaltung

Weniger ist mehr: Typografie trägt die Seite, nicht Effekte.

- **Flächen:** Weiß als Grund, eine ruhige helle Fläche (`bg-mist`) für
  Abschnitte, Tinte `#111827` für die Einladung am Seitenende. Keine Verläufe.
- **Akzent:** Indigo nur für den einen gefüllten Button (`btn-primary`),
  Textlinks (`textlink`) und den Punkt der Wortmarke (`punkt`).
- **Schrift:** Inter, Stufen `t-display`, `t-h1`, `t-h2`, `t-h3`, `t-lead`,
  `t-body` (Komponenten in `static/css/input.css`), linksbündig.
- **Hero:** Überschrift, ein erklärender Satz, ein Button, höchstens ein
  Textlink. Keine Pillen, keine Zähler-Leiste.
- **Inhalte offen auf der Fläche** statt in Karten; Status als leiser Text,
  Gruppierung über Abstand. Linien nur, wo sie Tabellen und Listen lesbarer machen.
- **Zustände** ändern Farbe oder Unterstreichung, nie die Position
  (die CI prüft alle Templates außer dem ruhenden Blog: kein Hover mit
  `translate-y`, keine Verläufe, keine Pillen-Etiketten, keine Deko-Viertelkreise).

Die StreamField-Blocktypen bleiben aus Kompatibilitätsgründen definiert, auch
wenn einzelne Felder (z. B. `badge_text`, `gradient_from`) nicht mehr angezeigt
werden.

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
