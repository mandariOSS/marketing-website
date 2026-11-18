# Sprachregel und Glossar

Gilt für alle Texte dieser Website außer den Rechtstexten in `.legal-content/`. Der Test
`marketing/tests/test_sprache.py` prüft die Seeds und Vorlagen gegen die Regeln, die sich prüfen lassen.

## Ton

- Selbstbewusst, klar, im Präsens. Wir sagen, was mandari kann und was als Nächstes kommt.
- Keine Verteidigung und keine Abgrenzung gegen andere („Andere SaaS …“, „keine Marketing-Übertreibung“,
  „ehrliche Antwort statt …“). Was noch fehlt, steht sachlich mit Zeitraum in der Roadmap und in den Tabellen.
- Nichts erfinden: keine Kunden, Zahlen oder Nachweise, die es nicht gibt. Zahlen tragen ihren Stand.
- Sie-Form. Du nur auf `/mitmachen/` und `/karriere/`.

## Schreibweise

- Gedankenstrich ist der Halbgeviertstrich mit Leerzeichen ( – ), sparsam. Nie der Geviertstrich (—).
- „und“ statt „&“.
- Deutsch vor Englisch, wo es ein gängiges deutsches Wort gibt (siehe Glossar).
- Produktnamen: mandari Session, mandari Work, mandari Insight. „mandari“ immer klein, die Produktnamen groß.

## Glossar

| Sache | So schreiben wir | Nicht |
|---|---|---|
| Insight als Gattung | Bürgerportal | Bürger:innen-Portal, Informationsportal |
| Insight als Suchbegriff | Bürgerinformationssystem, nur auf der Sachseite und in Verweisen dorthin | als Wechselwort für Bürgerportal |
| Arbeit der Verwaltung rund um die Sitzung | Sitzungsdienst | Verwaltungs-RIS |
| Suchbegriff dazu | Sitzungsmanagement, nur auf der Sachseite und in Verweisen dorthin | als Wechselwort für Sitzungsdienst |
| Kommune betreibt mandari selbst | Selbstbetrieb, mit Vertrag: Selbstbetrieb mit Betreuungsvertrag | Self-Hosting, Selbst-Hosting, Eigenbetrieb, On-Premises |
| Wir betreiben mandari | Betrieb durch mandari, als Dienst | Managed Hosting, Managed Service |
| Art. 28 DSGVO | Unterauftragsverarbeiter | Subprocessoren, Subprozessoren, Subunternehmer, Unterauftragnehmer |
| Bindung an einen Hersteller | Anbieterbindung | Lock-in, Vendor-Lock-in |
| Das abzulösende System | bisheriges RIS, bisheriges System | Alt-RIS |
| Datensicherung | Sicherung | Backup (außer in festen Produktnamen) |
| Menschen in der Kommune | Bürger:innen | Bürgerinnen und Bürger |
| Preis von mandari Work | Tarif, Preis | Lizenz (nur für die AGPL) |

## Stand der Produkte

| Produkt | Bezeichnung |
|---|---|
| mandari Session | Pilotphase (mit Zeitangabe: Pilotbetrieb ab 2027) |
| mandari Work | Offene Beta |
| mandari Insight | Im Einsatz |

Nicht: Beta-Phase, Pilot-Phase, General Availability.

## Aufrufe

- Verwaltungen: **Erstgespräch vereinbaren** (`/kontakt/#termin`).
- Fraktionen: der Aufruf aus `WORK_AUFRUF` in `marketing/management/commands/migrate_pages_to_streamfield.py`.
- Schriftliche Anfrage: **Nachricht schreiben** (`/kontakt/#nachricht`).
- Presse: **Presseanfrage stellen**. Partner: **Partnergespräch vereinbaren**.
- Textlinks nennen ihr Ziel („Bürgerportal öffnen“, „Roadmap ansehen“).

## Überschriften

- Angebotsseiten: eine Aussage mit Punkt („Sitzungsdienst ohne Medienbrüche.“).
- Nachschlageseiten (Roadmap, Releases, Trust Center, Quellen, Offene Daten, Meldewege): ein Etikett ohne Punkt.
- Keine Frage mit angehängter Antwort.

## Geschäftsmodell in einem Satz

Der Code der Plattform (mandari Session, Work, Insight) steht unter AGPL-3.0. Bezahlt wird Leistung: Betrieb,
Betreuung, Einführung und Schulung. Aussagen wie „jede Zeile“, „alles, was wir bauen“ oder „nie“ vermeiden wir,
wenn sie über die Plattform hinausgreifen.
