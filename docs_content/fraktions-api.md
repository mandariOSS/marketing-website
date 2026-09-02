# Öffentliche Fraktions-API v1

Mit der Fraktions-API bindet ihr die **öffentlichen** Termine und
Tagesordnungen eurer Fraktionssitzungen automatisch auf eurer Webseite ein —
als einfaches JSON, read-only, mit CORS für den direkten Browser-Zugriff.

## Aktivierung

Die API ist standardmäßig **deaktiviert** (bewusstes Opt-in):

1. Work-Portal → **Organisation → Reiter „API"**
2. „Öffentliche API aktivieren" anhaken und speichern
3. Die persönliche Basis-URL (mit eurem Zugangs-Token) kopieren

Im API-Reiter konfiguriert ihr außerdem: Zeitfenster für vergangene und
kommende Sitzungen, ob Sitzungsort und Tagesordnung ausgeliefert werden,
erlaubte CORS-Origins und die Cache-Dauer. Dazu gibt es eine
Nutzungsstatistik und ein fertiges Einbindungs-Snippet.

## Endpunkte

Basis: `https://mandari.de/api/public/v1`

| Methode | Pfad | Beschreibung |
|---------|------|--------------|
| GET | `/openapi.json` | OpenAPI-3.0-Schema |
| GET | `/fraktionen/<token>/` | Zugangs-Info + Endpunkte |
| GET | `/fraktionen/<token>/sitzungen/` | Terminliste |
| GET | `/fraktionen/<token>/sitzungen/<id>/` | Detail mit öffentlicher Tagesordnung |

## Sicherheit & Datenschutz

- Zugriff über ein **opakes Token** — Organisationen sind nicht enumerierbar.
  Das Token ist jederzeit erneuerbar (alte URLs werden sofort ungültig).
- Ausgeliefert werden **ausschließlich öffentliche** Inhalte. Niemals:
  nicht-öffentliche TOPs, Protokolle, Beschlüsse, Teilnehmerdaten.
- Unbekannte oder deaktivierte Zugänge antworten einheitlich mit `404`.

## Beispiel-Antwort

```json
{
  "api_version": "1.0",
  "organization": {"name": "Fraktion Beispiel"},
  "count": 1,
  "meetings": [
    {
      "id": "…",
      "title": "Fraktionssitzung",
      "start": "2026-09-15T18:00:00+02:00",
      "location": "Rathaus, Raum 1",
      "status": "invited",
      "cancelled": false
    }
  ]
}
```

Zur fertigen Einbindung siehe das
[Tutorial: Termine auf der Fraktions-Webseite](/docs/tutorial-termine-einbinden/).
