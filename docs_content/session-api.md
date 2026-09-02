# Session-API (Verwaltung)

Kommunen, die **mandari Session** als Ratsinformationssystem nutzen,
veröffentlichen ihre öffentlichen Daten über eine eigene, OParl-konforme
Schnittstelle je Mandant — und speisen damit auch das Bürgerportal.

## OParl je Mandant

Jede Kommune hat ihren eigenen OParl-Einstiegspunkt:

```
https://mandari.de/session/<kommune>/oparl/v1/system
```

Ausgeliefert werden ausschließlich **öffentliche** Sitzungen, Vorlagen und
Anlagen — nicht-öffentliche Inhalte bleiben im geschützten Bereich. Die
Veröffentlichung ins Bürgerportal ist ein bewusster Schalter der Verwaltung
(Session → Einstellungen → Bürgerportal).

## Interne JSON-API

Für Fachverfahren und Integrationen gibt es zusätzlich eine
token-geschützte JSON-API je Mandant (Sitzungen, Vorlagen, Anträge sowie
das digitale Einreichen von Fraktionsanträgen). Die API-Dokumentation ist
im Session-Portal unter **Einstellungen → API** verlinkt; Zugriffstoken
verwaltet die Kommune selbst.

## Antragseinreichung aus mandari Work

Fraktionen, die mandari Work nutzen, reichen Anträge direkt digital bei
ihrer Verwaltung ein — inklusive Statusverfolgung (eingereicht → in
Prüfung → in Vorlage umgewandelt). Dafür ist keine eigene
API-Programmierung nötig.

## Fragen?

Für die Anbindung eurer Kommune: [Kontakt aufnehmen](/kontakt/) — wir
unterstützen bei Migration und Erstimport (auch aus Bestandssystemen).
