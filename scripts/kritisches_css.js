// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Kritisches CSS (static/css/kritisch.css) – PostCSS-Schritt nach Tailwind, eingebunden über
// postcss.kritisch.config.js (npm run build:css).
//
// Tailwind erzeugt Grundstile und Utilities nur für die Vorlagen der ersten Ansicht (tailwind.kritisch.config.js).
// Eigene Regeln aus static/css/input.css übernimmt Tailwind aber immer. Dieser Schritt entfernt die eigenen Regeln,
// deren Klassen in keiner Vorlage der ersten Ansicht vorkommen (Produktflächen, Prosa-Links, Abschnittsmuster …),
// und hängt static/css/erste-ansicht.css an: Bis das vollständige Stylesheet geladen ist, bleibt alles unterhalb
// des Seitenkopfs unsichtbar.

const fs = require('fs');
const path = require('path');

const WURZEL = path.join(__dirname, '..');
const EINGABE = path.join(WURZEL, 'static/css/input.css');
const ZUSATZ = path.join(WURZEL, 'static/css/erste-ansicht.css');

// Klassen, die nicht im Template-Text stehen: {% abschnitt %} (marketing/templatetags/baender.py) setzt Band
// und Abstand des Seitenkopfs, base.html und static/js/kopfzeile.js den dunklen Modus, {% stile %} „vorab“.
const IMMER = ['dark', 'vorab', 'band-hell', 'hero', 'fortsetzung', 'fortgesetzt'];

/** Ende des Elements, das bei `start` beginnt (Index nach seinem schließenden Tag). */
function elementEnde(text, start) {
  const tag = /^<([a-z]+)/.exec(text.slice(start))[1];
  const muster = new RegExp('<(/?)' + tag + '\\b', 'g');
  muster.lastIndex = start;
  let tiefe = 0;
  let treffer;
  while ((treffer = muster.exec(text))) {
    tiefe += treffer[1] ? -1 : 1;
    if (tiefe === 0) return text.indexOf('>', treffer.index) + 1;
  }
  return text.length;
}

/** Text einer Vorlage ohne Kommentare und Ausgaben ({{ … }}): Dort stehen Wörter, aber keine Klassen. */
function vorlage(datei) {
  return fs
    .readFileSync(path.resolve(WURZEL, datei), 'utf8')
    .replace(/{% comment %}[\s\S]*?{% endcomment %}|{#[\s\S]*?#}|{{[\s\S]*?}}/g, ' ');
}

/** Seitenkopf einer Vorlage: vom ersten Element mit der Klasse „hero“ bis zu seinem schließenden Tag. Enthält er
 *  einen <header> (Dokumentseite: Titel, darunter Randspalte, Inhalt und Text), endet er mit diesem: Was danach
 *  kommt, bleibt bis zum vollständigen Stylesheet unsichtbar (static/css/erste-ansicht.css). */
function seitenkopf(datei) {
  const text = vorlage(datei);
  const start = text.search(/<[a-z]+\b[^>]*\bclass="[^"]*\bhero\b/);
  if (start < 0) {
    console.warn(`kritisches CSS: kein Seitenkopf (class="… hero …") in ${datei}, die ganze Vorlage zählt`);
    return text;
  }
  const kopf = text.slice(start, elementEnde(text, start));
  const header = kopf.search(/<header\b/);
  return header < 0 ? kopf : kopf.slice(0, elementEnde(kopf, header));
}

/** Vorlage ohne die Elemente mit diesen ids (geschlossene Menüs: Sie öffnen sich erst auf Klick). */
function ohne(datei, ...ids) {
  let text = vorlage(datei);
  for (const id of ids) {
    const start = text.search(new RegExp('<[a-z]+\\b[^>]*\\bid="' + id + '"'));
    if (start < 0) throw new Error(`kritisches CSS: kein Element mit id="${id}" in ${datei}`);
    text = text.slice(0, start) + text.slice(elementEnde(text, start));
  }
  return text;
}

// Zustände, die erst durch Bedienen eintreten (Zeiger, Fokus, geöffnetes Menü): Ihre Regeln braucht das erste
// Zeichnen nicht, sie kommen mit styles.css. Zustände ändern nur Farbe oder Unterstreichung (Gestaltungsregeln),
// nie die Position.
const ZUSTAND = /:hover|:focus|:active|::backdrop|\[aria-expanded=true\]/;
const INLINE = ['a', 'abbr', 'b', 'br', 'code', 'em', 'i', 'img', 'li', 'ol', 'p', 'small', 'span', 'strong', 'sub', 'sup', 'svg', 'ul'];

/** Grundstile (Selektor ohne Klassen) nur für Elemente, die in der ersten Ansicht vorkommen. */
function elementeVorhanden(selektor, elemente) {
  if (selektor.includes('.')) return true;
  const namen = selektor
    .replace(/\[[^\]]*\]/g, '')
    .replace(/::?[a-z-]+(\([^)]*\))?/g, '')
    .match(/[a-z][a-z0-9]*/g);
  return !namen || namen.some((name) => elemente.has(name));
}

const KLASSE = /\.((?:\\.|[A-Za-z0-9_-])+)/g;
const klassenIn = (selektor) => [...selektor.matchAll(KLASSE)].map((m) => m[1].replace(/\\(.)/g, '$1'));

/** Steht ein Selektor nur aus Klassen, die die erste Ansicht verwendet? Klassen in :not() zählen nicht, von den
 *  Alternativen in :is()/:where() genügt eine. Nur eigene Klassen aus input.css werden geprüft. */
function erlaubt(selektor, eigene, vorhanden) {
  const fehlt = (klasse) => eigene.has(klasse) && !vorhanden.has(klasse);
  let ok = true;
  const rest = selektor
    .replace(/:not\([^)]*\)/g, '')
    .replace(/:(?:is|where)\(([^)]*)\)/g, (_, liste) => {
      if (!liste.split(',').some((alt) => !klassenIn(alt).some(fehlt))) ok = false;
      return '';
    });
  return ok && !klassenIn(rest).some(fehlt);
}

const plugin = () => ({
  postcssPlugin: 'kritisches-css',
  OnceExit(root, { postcss, result }) {
    const config = require(path.join(WURZEL, 'tailwind.kritisch.config.js'));

    // Eigene Klassen: alle Klassen in Selektoren von input.css (Tailwind-Utilities stehen dort nicht)
    const eigene = new Set();
    postcss.parse(fs.readFileSync(EINGABE, 'utf8')).walkRules((rule) => {
      rule.selectors.forEach((sel) => klassenIn(sel).forEach((k) => eigene.add(k)));
    });

    // Wörter der Vorlagen der ersten Ansicht (wie Tailwind sie liest), ohne die gesperrten Klassen
    const text = config.content.map((e) => (typeof e === 'string' ? vorlage(e) : e.raw)).join('\n');
    const vorhanden = new Set([...(text.match(/[A-Za-z0-9_-]+/g) || []), ...IMMER]);
    (config.blocklist || []).forEach((klasse) => vorhanden.delete(klasse));

    // Elemente der ersten Ansicht (für die Grundstile) und Inline-Elemente, die Rich Text im Seitenkopf mitbringt
    const elemente = new Set([...text.matchAll(/<([a-z][a-z0-9]*)/g)].map((m) => m[1]).concat(INLINE));

    root.walkComments((kommentar) => kommentar.remove()); // Lizenzhinweis steht in styles.css
    root.walkRules((rule) => {
      if (rule.parent.type === 'atrule' && /keyframes$/.test(rule.parent.name)) return;
      // Übergänge und Animationen: Beim ersten Zeichnen ändert sich nichts, styles.css bringt sie mit
      if (rule.nodes.every((d) => d.type !== 'decl' || /^(transition|animation)/.test(d.prop))) {
        rule.remove();
        return;
      }
      const bleiben = rule.selectors.filter(
        (sel) =>
          !ZUSTAND.test(sel) && erlaubt(sel, eigene, vorhanden) && elementeVorhanden(sel, elemente),
      );
      if (!bleiben.length) rule.remove();
      else if (bleiben.length < rule.selectors.length) rule.selectors = bleiben;
    });
    // Leere @media-Blöcke entfernen (auch verschachtelte)
    let leer;
    do {
      leer = [];
      root.walkAtRules((at) => {
        if (at.nodes && at.nodes.length === 0) leer.push(at);
      });
      leer.forEach((at) => at.remove());
    } while (leer.length);

    root.append(postcss.parse(fs.readFileSync(ZUSATZ, 'utf8'), { from: ZUSATZ }).nodes);
    result.messages.push({ type: 'dependency', plugin: 'kritisches-css', file: ZUSATZ, parent: result.opts.from });
  },
});
plugin.postcss = true;

module.exports = plugin;
module.exports.seitenkopf = seitenkopf;
module.exports.ohne = ohne;
