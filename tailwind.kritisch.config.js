/** @type {import('tailwindcss').Config} */

// ── Kritisches CSS: nur die erste Ansicht ────────────────────────────────
// Eine zweite, kleine Tailwind-Ausgabe (static/css/kritisch.css), die base.html inline in den Kopf schreibt
// ({% stile %} in marketing/templatetags/stile.py). Sie gestaltet, was beim ersten Aufruf sichtbar ist:
// Grundgerüst, Kopfzeile mit Slide-Menü und Produkte-Menü im Grundzustand (geschlossen) und den Seitenkopf aller
// Seitentypen. Das vollständige styles.css lädt danach, ohne das erste Zeichnen aufzuhalten; bis dahin
// bleibt alles unterhalb des Seitenkopfs unsichtbar (static/css/erste-ansicht.css).
//
// Gleiche Konfiguration wie tailwind.config.js, nur andere Vorlagen. Eigene Klassen aus static/css/input.css
// (Bänder, Hero-Bilder, Schriftstufen …) übernimmt scripts/kritisches_css.js nur, wenn eine dieser Vorlagen
// sie verwendet. Wer einen Seitenkopf in einer weiteren Vorlage baut, trägt sie hier ein;
// scripts/check_kritisches_css.py meldet in der CI jede Klasse aus Kopfzeile und Seitenkopf, die fehlt.
const basis = require('./tailwind.config.js');

const ersteAnsicht = [
  './templates/base.html',
  // Seitenkopf als Baustein (StreamField-Seiten, /kontakt/) und die Bilder darin
  './templates/marketing/blocks/hero.html',
  './templates/marketing/_hero_stapel.html',
  './templates/marketing/_hero_einzel.html',
];

// Vorlagen mit eigenem Seitenkopf im Template: Nur der Seitenkopf zählt (das erste Element mit der Klasse
// „hero“ bis zu seinem schließenden Tag, bei Dokumentseiten bis zum Ende ihres <header>), sonst käme der ganze
// Seiteninhalt ins kritische CSS.
const mitEigenemSeitenkopf = [
  './templates/marketing/landing.html',
  './templates/marketing/dokument.html',
  './templates/marketing/crawler.html',
  './templates/marketing/sicherheit_disclosure.html',
  './templates/blog/release.html',
  './templates/blog/release_index.html',
  './templates/404.html',
];

const { ohne, seitenkopf } = require('./scripts/kritisches_css.js');

module.exports = {
  ...basis,
  content: [
    ...ersteAnsicht,
    ...mitEigenemSeitenkopf.map((datei) => ({ raw: seitenkopf(datei), extension: 'html' })),
    // Kopfzeile ohne das Innere der geschlossenen Menüs: Sie öffnen sich erst auf Klick, bis dahin ist styles.css da
    // (sonst bleiben sie unsichtbar, static/css/erste-ansicht.css).
    { raw: ohne('./templates/components/navbar.html', 'produkte-menue', 'mobilmenue'), extension: 'html' },
  ],
  // Fließtext im Seitenkopf bleibt bis zum vollständigen Stylesheet unsichtbar
  blocklist: ['prose', 'prose-lg', 'dark:prose-invert'],
  safelist: [],
};
