# Self-Hosting mit Docker

mandari ist Open Source (AGPL-3.0) und vollständig selbst betreibbar —
volle Datenhoheit auf eurer eigenen Infrastruktur.

## Voraussetzungen

- Linux-Server (2+ CPU-Kerne, 8 GB RAM empfohlen)
- Docker & Docker Compose
- Eine Domain mit TLS (z. B. über Caddy oder Traefik)

## Komponenten

| Container | Aufgabe |
|-----------|---------|
| `mandari` | Django-Anwendung (Insight, Work, Session) |
| `ingestor` | OParl-Synchronisation (Rust) |
| `ocr-worker` | Text-Extraktion für PDFs |
| `postgres` | Datenbank (PostgreSQL 16) |
| `elasticsearch` | Volltextsuche |
| `redis` | Cache & Echtzeit-Funktionen |

## Schnellstart

```bash
git clone https://github.com/mandariOSS/mandari.git
cd mandari
cp .env.example .env   # SECRET_KEY, DATABASE_URL, ENCRYPTION_MASTER_KEY setzen
docker compose up -d
docker compose exec mandari python manage.py migrate
docker compose exec mandari python manage.py createsuperuser
```

Wichtige Umgebungsvariablen und der komplette Aufbau sind im
[Repository](https://github.com/mandariOSS/mandari) dokumentiert
(`CLAUDE.md`/`docs/` im Quellcode).

## Regelmäßige Läufe (Cron)

```cron
0 7 * * * docker compose exec -T mandari python manage.py send_session_reminders
0 3 * * * docker compose exec -T mandari python manage.py session_privacy_purge
```

## Updates

Releases erscheinen auf [GitHub](https://github.com/mandariOSS/mandari/releases)
mit Release-Notes; Migrationen sind additiv angelegt und laufen per
`manage.py migrate`. Bitte vor Updates ein Datenbank-Backup erstellen.

## Support

Community-Support über GitHub-Issues; für Kommunen bieten wir
[betreutes Hosting und Support-Verträge](/kommunen/) an.
