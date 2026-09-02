# OParl-API (Bürgerportal)

mandari Insight stellt alle öffentlichen Ratsinformationen über
**[OParl 1.1](https://oparl.org)** bereit — den deutschen Standard für
offene Ratsinformationssysteme. Die API ist anonym, lesend und kostenlos.

## Einstiegspunkt

```
https://mandari.de/oparl/v1/system
```

Von dort hangelst du dich über die verlinkten Objekte durch alle Daten:

```
System → Bodies (Kommunen) → Organizations, Persons, Meetings, Papers
```

## Die wichtigsten Objekte

| OParl-Objekt | Bedeutung |
|--------------|-----------|
| `Body` | Kommune (Stadt, Kreis, Gemeinde) |
| `Organization` | Gremium: Rat, Ausschuss, Fraktion |
| `Meeting` | Sitzung mit Tagesordnung |
| `AgendaItem` | Tagesordnungspunkt |
| `Paper` | Vorlage/Drucksache mit Dateien |
| `Consultation` | Beratung: verbindet Vorlage ↔ TOP ↔ Sitzung |
| `Person` / `Membership` | Mandatsträger und Gremienzugehörigkeit |

## Beispiel: Kommunen abrufen

```bash
curl https://mandari.de/oparl/v1/bodies
```

Alle Listen sind paginiert (`links.next`). Zeitfilter laufen über
`modified_since` — ideal für inkrementelle Synchronisation:

```bash
curl "https://mandari.de/oparl/v1/papers?modified_since=2026-01-01T00:00:00Z"
```

## Fair Use

- Bitte inkrementell synchronisieren statt Vollabzüge zu wiederholen.
- Setze einen aussagekräftigen `User-Agent` mit Kontaktmöglichkeit.
- Fragen zur Anbindung: [Kontakt](/kontakt/).
