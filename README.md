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
- **Karriere ruht** (keine offenen Stellen): `/karriere/` ist mit
  `retire_page karriere --redirect /unternehmen/` zurückgezogen, Bewerbungen laufen über
  `bewerbung@mandari.de` (`/kontakt/`). Seed und Seite bleiben erhalten. Reaktivieren: die Seite im
  Wagtail-Admin wieder veröffentlichen, die Weiterleitung `/karriere` unter *Einstellungen →
  Weiterleitungen* löschen, den Link in Fußzeile (`templates/components/footer.html`), Struktur-Test
  (`scripts/check_site_structure.py`, `FUSSZEILE`) und Kontaktverzeichnis (`marketing/contact.py`)
  wieder aufnehmen und den Rückzug-Schritt in `.github/workflows/ci.yml` entfernen.
- **RIS-Vergleich** (`/vergleich/`, die vier Anbieterseiten und die Lücken auf `/roadmap/`): Funktionen,
  Zellen, Quellen und Lücken stehen in `marketing/seeds_vergleich.py`. Jede Angabe zu einem Anbieter trägt
  ein Quellenkürzel (z. B. `[ST2]`), über Anbieter steht nie „Nein“, sondern höchstens „keine öffentliche
  Angabe“; was mandari fehlt, steht als „Noch nicht verfügbar“ mit der Roadmap-Stufe. Die Tests in
  `marketing/tests/test_vergleich.py` prüfen das. Nach Änderungen `refresh_seeded_page vergleich --force`,
  `refresh_seeded_page mandari-vs-<anbieter> --force` und `refresh_seeded_page roadmap --force`.
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

# Tailwind im Watch-Mode (nur styles.css; mit DEBUG bindet base.html es wie gewohnt ein)
npm run watch:css
# styles.css und das kritische CSS (static/css/kritisch.css) bauen, wie im Docker-Build:
npm run build:css

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
| Icons | [Lucide](https://lucide.dev) als Inline-SVG (`marketing/templatetags/icons.py`), ohne JavaScript | ISC |
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
│   ├── fonts/                # Inter (latin, latin-ext), verkleinert mit scripts/schrift_teilmenge.py
│   ├── vendor/               # alpine, altcha (lokal gehostet)
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

### Ladezeit

- **Kritisches CSS.** `npm run build:css` baut neben `styles.css` das kleine `static/css/kritisch.css`:
  Grundgerüst, Kopfzeile und Seitenkopf aller Seitentypen (Vorlagen in `tailwind.kritisch.config.js`, eigene
  Klassen aus `input.css` filtert `scripts/kritisches_css.js`). `{% stile %}` (`marketing/templatetags/stile.py`)
  schreibt es inline in den Kopf und lädt `styles.css` mit `media="print"` nach, ohne das erste Zeichnen
  aufzuhalten. Bis es da und Alpine gestartet ist, bleibt alles unterhalb des Seitenkopfs ausgeblendet
  (`static/css/erste-ansicht.css`); danach meldet das Ereignis `stile:fertig`, dass die Seite vollständig steht.
  Seiten mit Produktbildern unter dem Seitenkopf (`BLOECKE_MIT_BILDERN` in `stile.py`, heute `/produkte/`) laden
  `styles.css` mit `fetchpriority="high"`. Sonst reiht Lighthouse es hinter diese Bilder und errechnet ein späteres
  LCP.
  Mit `DEBUG`, ohne gebautes `kritisch.css` oder mit der Umgebungsvariable `KRITISCHES_CSS=aus` bleibt es beim
  blockierenden Stylesheet. Wer einen Seitenkopf in
  einer weiteren Vorlage baut, trägt sie in `tailwind.kritisch.config.js` ein; die CI
  (`scripts/check_kritisches_css.py`) prüft die Größe (höchstens 6.000 Bytes gzip), dass jede Klasse aus
  Kopfzeile und Seitenkopf aller Seiten im kritischen CSS steht und dass das HTML von Startseite und `/kontakt/`
  mit dem kritischen CSS in die ersten TCP-Pakete passt (höchstens 13.800 Bytes gzip; darüber kommt das erste
  Bild am Handy rund 150 ms später). Kommentare im Kopf von `base.html` deshalb als Template-Kommentar.
- **Content-Security-Policy.** Das Ladeskript (`LADER` in `stile.py`) ist ein fester Text ohne Inline-Handler.
  Für eine CSP ohne `'unsafe-inline'` genügt sein Hash (dazu der des Skripts für den Dunkelmodus in `base.html`):
  `python -c "import base64, hashlib; from marketing.templatetags.stile import LADER; print('sha256-' + base64.b64encode(hashlib.sha256(LADER.encode()).digest()).decode())"`
- **Schrift.** Inter mit `font-display: swap`, davor im Schriftstapel `Inter Ersatz`: Arial bzw. Roboto, per
  `size-adjust` und `ascent-/descent-override` auf Inter angepasst (`base.html`, `tailwind.config.js`). Die Seite
  zeichnet vor `styles.css`; so verschiebt der Wechsel zu Inter den Text nicht (CLS), und Inter erscheint auch beim
  ersten Aufruf über das Mobilnetz. Wer die Schrift oder ihre Teilmenge ändert, rechnet die Werte neu.
- **Brotli.** Mit dem Paket `brotli` legt `collectstatic` neben `.gz` auch `.br` an, WhiteNoise liefert CSS, JS
  und SVG damit aus (Caddy reicht die fertige Kodierung durch). Prüfen:
  `curl -sI -H 'Accept-Encoding: br' https://mandari.de/wstatic/css/styles.<hash>.css` zeigt `content-encoding: br`.
- **Hero-Bilder** liegen je Breite als AVIF und WebP vor; vorgeladen wird das AVIF. Neue oder geänderte Bilder:
  WebP wie bisher ablegen, dann `python scripts/hero_avif.py` (Pillow mit AVIF, Vorlagen siehe Skript).
- **Spamschutz.** Altcha lädt erst, wenn jemand ein Kontaktformular betritt (`static/js/kontakt.js`).

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

Weniger ist mehr: Typografie trägt die Seite, nicht Effekte. Alle Seiten folgen einem
Gestaltungssystem (Kopfkommentar in `static/css/input.css`), damit Seitenwechsel ruhig wirken.

| | Stufen |
|---|---|
| **Schrift** | Inter, linksbündig: `t-h1` 56 px · `t-h2` 40 px (Dokumente `t-h2-dok` 28 px) · `t-h3` 22 px · `t-lead` 20 px · `t-body` 18 px · Sekundär 16 px · Klein 14 px. Am Handy `t-h1` 32 px, `t-h2` und große Aussage 28 px, Zahl im Satz 22 px. Unter 1280 px trennen Überschriften, Begriffe und Tabellenköpfe lange Wörter nach Silben (`hyphens: auto`, ab 12 Zeichen) und brechen sie notfalls am Rand, statt überzulaufen |
| **Abstand** | Abschnitt 96 px (Handy 64) · kompakt 64 px (48) für Hinweise · Unterabschnitt 48 px · Abschnittskopf → Inhalt 48 px, vor Fließtext 24 px |
| **Raster** | Inhalt 1216 px, 12 Spalten; Textspalte höchstens 45 rem (ca. 70 Zeichen); Einträge in zwei Spalten, bei genau drei Einträgen in drei |
| **Farbe** | Tinte `#111827`, Text `#4B5563`, Weiß, Hellgrau `#EEF0F4`; Indigo `#4F46E5` nur für den gefüllten Button, Textlinks und den Punkt der Wortmarke |

- **Ein Seitenkopf für alle Seiten** (`marketing/blocks/hero.html`): weiß, Überschrift,
  ein erklärender Satz, ein Button, höchstens ein Textlink, keine Pillen, keine Zähler-Leiste.
  Produktseiten zeigen rechts ein echtes Bild in derselben Rahmung wie die Startseite:
  `/produkte/` den Stapel aus Session, Work und Insight (`_hero_stapel.html`), `/kommunen/`
  Session und `/fraktionen/` Work (`_hero_einzel.html`, Zuordnung `HERO_BILD` in
  `marketing/templatetags/baender.py`). Alle anderen Seiten haben einen kompakten Kopf
  ohne Bild mit Mindesthöhe; Rechtstexte, Quellen und Releases sind Dokumente: Kopf und Text
  durchgehend auf Weiß.
- **Bänder:** Jeder Abschnitt liegt auf einem vollbreiten Band, benachbarte
  Bänder haben nie denselben Grund: Weiß, kühles Hellgrau, Markenfläche (Indigo, für
  eine Einladung mitten auf der Seite, nie neben Hellgrau), Tinte für die Einladung am
  Seitenende, die Fußzeile eine Stufe dunkler. Auf StreamField-Seiten legt
  `marketing/templatetags/baender.py` die Bänder nach der Reihenfolge der Blöcke fest, das
  Tag `{% abschnitt %}` setzt Band und Innenabstand aus der Skala (Zusätze wie Eckdaten oder
  Hinweise setzen das Band davor fort, ohne doppelten Abstand). Das Feld „Hintergrund“
  einzelner Blöcke wirkt nur noch ohne diese Automatik. Farben hell und dunkel als
  Variablen in `static/css/input.css`. Keine Verläufe.
- **Form folgt Inhalt (Musterkatalog):** Jeder Abschnitt bekommt die Form seiner Daten, nicht das
  eine Raster „fette Zeile + Absatz“. Die Muster sind StreamField-Bausteine (`marketing/blocks.py`,
  Templates `templates/marketing/blocks/<muster>.html`, Teile in `templates/marketing/muster/`,
  Geometrie in `marketing/templatetags/muster.py`, Seed-Helfer `marketing/seeds_muster.py`):

  | Inhalt | Muster | Baustein | Beispiel |
  |---|---|---|---|
  | Ablauf mit Fristen | Zeitskala, maßstäblich in Tagen, Achsenbruch für offene Zeitpunkte (Achse ab 1280 px, darunter Liste) | `zeitskala` | Disclosure, Abuse, Unternehmen |
  | Schritte mit Dauern | Dauerbalken (frühestens, Spielraum, fester Tag) | `dauerbalken` | Migration |
  | Vorhaben mit Zeitpunkt | Quartalsachse, Modul in Kennfarbe, Stufe als Text | `quartalsachse` | Roadmap |
  | Kurze Folge ohne Fristen | Schrittfolge in einer Zeile mit Ergebnis (ab 1280 px, darunter untereinander) | `schrittfolge` | Mitmachen, Partner |
  | Sammlung mit Stand | Register: eine Tabelle, Gruppen, Status als Punkt, Bestand im Randkopf | `register` | Vergabe, Lücken, Preisliste, Kontenblatt |
  | Lange Texte | Dokumentseite: Inhaltsleiste, Text, Randspalte (Stand, Verweise, Kontakt) | `marketing/dokument.html` | Rechtstexte, Quellen, Trust Center, Releases |
  | Text, der schmal bleibt | Text mit Randspalte (Ablauf, Dateien, Kontakt), Stichwort am Absatzanfang | `randspalte` | Vertragsgrundlagen, Kurzprofil |
  | Werte, Eigenschaften | Begriffe in der Marginalie | `begriffe` | Wertekompass, Fundament |
  | Einladung | Schlussband mit den direkten Wegen rechts | `gradient_cta` (Feld „Wege“) | jede Seite |
  | Zusage | große Aussage, rechts die Bedingungen (höchstens einmal je Seite) | `zusage`, `leitsatz` | Safe Harbor, Warrant Canary |
  | Produkte | Bildschirm in der Kennfläche des Produkts, rechts und unten angeschnitten bis an den Fensterrand; alle Produkte gleich (Text links, Bild rechts) | `produktbilder` | /produkte/ |
  | Optionen | Vergleichstabelle Kriterien × Optionen (mehr als zwei Optionen: Tabelle erst ab 1024 px) | `vergleich` | Selbst hosten, Anbindung, Partner |
  | Zahlen | Zahl im Satz, Null mit Aufschlüsselung | `zahlensatz`, `nullen` | Transparenz, Presse |
  | Dateien | Download-Leiste: ein Button rechts, Vorschauen nach Rang | `downloads`, `company/_logopaket.html` | Presse, Preisliste |

  Regeln: nie zweimal dasselbe Muster hintereinander, höchstens eine große Aussage je Seite, jede
  Seite mit mindestens einem Element, das kein Fließtext ist (`marketing/tests/test_muster.py`).
  **Keine leere rechte Hälfte:** Kein Abschnitt endet bei 1440 px vor 80 % der Rasterbreite;
  `scripts/check_fuellung.py` misst das im Browser (CI). Hinweise direkt nach dem Seitenkopf
  stehen in dessen Randspalte. Feste Seiten (Startseite, Disclosure, Crawler) holen ihre Daten
  aus `marketing/muster_daten.py`.
- **Produktfarben:** Session Petrol `#0F5E8C` (vom Blau in Session abgeleitet,
  bewusst vom Indigo abgesetzt), Work Indigo `#4F46E5` (Standardfarbe in Work),
  Insight Grün `#17703F`. Startseite und `/produkte/` zeigen jedes Produkt als eigene Fläche
  (`_produkt.html`): hell zart getönt, dunkel neutral mit Namen und Link in der Kennfarbe.
  Überall dieselbe Reihenfolge: Session, Work, Insight (auch Funktionsübersicht und Preise).
- **Formulare** (`/kontakt/`): ein Umschalter „Termin | Nachricht“, beide Formulare im selben
  Raster, alle Felder 48 px (Klasse `feld`), ein gefüllter Aufruf je Formular.
- **Links:** eine Gestalt für Textlinks und Links im Fließtext; Aufrufe im Rich Text
  (`<a class="btn-primary">`, z. B. der Kündigungsbutton) bleiben Aufrufe.
- **Weitere Werkzeuge** kündigen Produkt-, Presse- und Unternehmensseiten nicht an; was
  geplant ist, steht in der Roadmap (`/roadmap/`).
- **Versionsangaben** stehen nur in den Release-Notes (`/releases/`). Andere
  Seiten nennen den Stand ohne Nummer („Beta-Phase“) und verlinken dorthin,
  damit sie mit dem nächsten Release nicht veralten (die CI prüft das).
- **Zustände** ändern Farbe oder Unterstreichung, nie die Position
  (die CI prüft alle Templates außer dem ruhenden Blog: kein Hover mit
  `translate-y`, keine Verläufe, keine Pillen-Etiketten, keine Deko-Viertelkreise,
  Abstände nur aus der Skala).

Die StreamField-Blocktypen bleiben aus Kompatibilitätsgründen definiert, auch
wenn einzelne Felder (z. B. `badge_text`, `gradient_from`, `background_color`) nicht mehr angezeigt
werden.

## 🤝 Mitmachen

Issues und Pull Requests willkommen — siehe
[CONTRIBUTING.md](CONTRIBUTING.md) und unsere
[Mitmachen-Seite](https://mandari.de/mitmachen/).

Du kannst Mandari auch finanziell unterstützen:

- [GitHub Sponsors](https://github.com/sponsors/mandariOSS)
- [Ko-fi](https://ko-fi.com/mandari)
- [Buy Me a Coffee](https://buymeacoffee.com/mandari)

## 📜 Lizenz

Mandari ist [AGPL-3.0](LICENSE) lizenziert — siehe Datei `LICENSE` und
<https://mandari.de/open-source/>.

## 🛡 Sicherheit

Sicherheitslücken bitte gemäß unserer
[Responsible-Disclosure-Policy](https://mandari.de/sicherheit/disclosure/)
melden — siehe auch [`security.txt`](https://mandari.de/.well-known/security.txt)
und [SECURITY.md](SECURITY.md).

## 📞 Kontakt

- **Allgemein**: [hello@mandari.de](mailto:hello@mandari.de)
- **Sicherheit**: [security@mandari.de](mailto:security@mandari.de)
- **Datenschutz**: [datenschutz@mandari.de](mailto:datenschutz@mandari.de)
- **Missbrauch**: [abuse@mandari.de](mailto:abuse@mandari.de)
- **Founder**: Sven Konopka, [topixmedia.de](https://topixmedia.de), Münster

---

Made with ❤ for transparent local democracy.
