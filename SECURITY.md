# Security Policy

## Reporting a Vulnerability

Mandari nimmt jede gutgläubige Sicherheitsmeldung ernst — wir antworten **binnen
48 Stunden** und behandeln dich mit Respekt: keine Anwälte, keine Drohungen,
kein Hacker-Paragraph-202c-Brief.

### Wie melden?

Bevorzugte Wege (nach Reihenfolge):

1. **GitHub Security Advisory** (verschlüsselt, privat)
   → <https://github.com/mandariOSS/marketing-website/security/advisories/new>

2. **E-Mail** an [security@mandari.de](mailto:security@mandari.de)
   (PGP-Key in Vorbereitung — siehe `static/security/mandari-pgp-key.asc`)

3. **`/.well-known/security.txt`** für maschinenlesbaren Kontakt
   → <https://mandari.de/.well-known/security.txt>

Vollständige Policy: <https://mandari.de/sicherheit/disclosure/>

### Was rein gehört

- **URL** der betroffenen Seite oder Beschreibung des Codes
- **Beschreibung** der Schwachstelle und ihrer Auswirkung
- **Proof of Concept** (kein echter User-Account, bitte!)
- **CVSS-Bewertung** falls möglich (3.1)
- Wie wir dich erreichen können (E-Mail, Matrix, …)

### Was du erwarten kannst

- **≤ 48 h**: Eingangsbestätigung durch den Founder persönlich
- **1–7 Tage**: Triage und Schwere-Einstufung nach CVSS 3.1
- **≤ 90 Tage**: Patch + Disclosure (kürzer bei kritischen Lücken)
- **+14 Tage**: Security Advisory mit CVE, Erwähnung in der Hall of Fame

### Safe Harbor

Solange du dich an unsere
[Responsible-Disclosure-Policy](https://mandari.de/sicherheit/disclosure/) hältst,
verzichten wir auf zivil- oder strafrechtliche Verfolgung.

## Scope

### In Scope

- `mandari.de` und alle Subdomains
- Source-Code in `mandariOSS/marketing-website` und `mandariOSS/mandari`
- Selbst gehostete Mandari-Instanzen (mit Erlaubnis der Betreiber)

### Out of Scope

- DoS / DDoS jeglicher Art
- Social Engineering gegen Founder oder Nutzer:innen
- OParl-Quellsysteme der Kommunen (sind nicht unser System)
- Drittanbieter-Dienste (Hetzner, Postmark, …)

## Bekannte Sicherheits-Eigenschaften

- TLS 1.3, HSTS preload, strikte CSP
- AES-256 at rest (LUKS auf Hetzner-Servern in Deutschland)
- Altcha (Proof-of-Work) als DSGVO-konformer Spam-Schutz
- AGPL-3.0 — kompletter Quellcode öffentlich begutachtbar
- Keine Tracker, kein Google Analytics, kein Facebook Pixel

## Supported Versions

Wir patchen sicherheitsrelevante Updates nur in der `main`-Branch.
Forks und ältere Versionen werden nicht supportet — wir empfehlen,
immer von `main` zu pullen.

| Version | Supported          |
|---------|--------------------|
| `main`  | :white_check_mark: |
| Forks   | :x:                |
