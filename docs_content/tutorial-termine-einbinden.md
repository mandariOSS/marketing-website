# Tutorial: Termine auf der Fraktions-Webseite

In 10 Minuten zeigt eure Webseite automatisch die nächsten öffentlichen
Fraktionssitzungen — ohne Plugins, ohne Backend, mit einem kleinen
JavaScript-Snippet.

## Schritt 1: API aktivieren

Im Work-Portal unter **Organisation → Reiter „API"** die öffentliche API
aktivieren und die **Basis-URL** kopieren (sie enthält euer Zugangs-Token).

> Tipp: Beschränkt dort die „Erlaubten Origins" auf eure Webseiten-Domain —
> dann kann kein anderer die Daten per Browser einbetten.

## Schritt 2: Snippet einbauen

Diesen Block an die gewünschte Stelle eurer Webseite einfügen und
`DEINE_BASIS_URL` durch die kopierte URL ersetzen (der API-Reiter erzeugt
das Snippet auch fertig ausgefüllt zum Kopieren):

```html
<div id="fraktions-termine">Termine werden geladen…</div>
<script>
fetch("DEINE_BASIS_URLsitzungen/")
  .then(r => r.json())
  .then(data => {
    const el = document.getElementById("fraktions-termine");
    const kommende = data.meetings.filter(m => new Date(m.start) >= new Date() && !m.cancelled);
    if (!kommende.length) { el.textContent = "Aktuell keine öffentlichen Termine."; return; }
    el.innerHTML = kommende.map(m =>
      "<p><strong>" + new Date(m.start).toLocaleString("de-DE", {dateStyle: "medium", timeStyle: "short"}) +
      "</strong> — " + m.title + (m.location ? " (" + m.location + ")" : "") + "</p>"
    ).join("");
  })
  .catch(() => { document.getElementById("fraktions-termine").textContent = "Termine derzeit nicht verfügbar."; });
</script>
```

## Schritt 3: Prüfen

Seite neu laden — die kommenden Termine erscheinen. Falls nicht:

- **„Termine derzeit nicht verfügbar"**: Basis-URL prüfen (endet auf `/`),
  API im Work-Portal wirklich aktiviert?
- **Leere Liste**: Es gibt aktuell keine geplanten öffentlichen Sitzungen —
  Entwürfe und nicht-öffentliche Termine erscheinen nie.
- **CORS-Fehler in der Browser-Konsole**: Eure Domain unter „Erlaubte
  Origins" eintragen (oder das Feld leeren für alle).

## WordPress & Co.

Das Snippet funktioniert überall, wo ihr HTML einfügen könnt — bei
WordPress z. B. über einen „Custom HTML"-Block. Für Systeme, die kein
JavaScript erlauben, könnt ihr die JSON-Daten auch serverseitig abrufen
(Details in der [API-Referenz](/docs/fraktions-api/)).
