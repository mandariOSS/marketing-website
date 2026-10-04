// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Spamschutz der Kontaktformulare (templates/marketing/kontakt.html): Altcha (static/vendor/altcha) lädt erst,
// wenn jemand ein Formular betritt, nicht schon mit der Seite. Das spart beim Aufruf von /kontakt/ rund 24 KB und
// die Zeit, in der der Browser das Modul übersetzt und startet (Lighthouse: Total Blocking Time).
// Wie bisher (auto="onfocus") beginnt die Prüfung beim ersten Feld: Für das Feld, das den Fokus schon hat, holt
// verify() sie nach, danach übernimmt das Widget selbst.
(() => {
  const quelle = document.currentScript.dataset.altcha;
  let geladen = false;
  document.addEventListener("focusin", (event) => {
    const form = event.target.closest && event.target.closest("form");
    const widget = form && form.querySelector("altcha-widget");
    if (!widget) return;
    if (!geladen) {
      geladen = true;
      const skript = document.createElement("script");
      skript.type = "module";
      skript.src = quelle;
      document.head.append(skript);
    }
    // Das Widget stellt verify() erst kurz nach seiner Definition bereit.
    const pruefen = (versuche) => {
      if (typeof widget.verify !== "function") {
        if (versuche > 0) setTimeout(() => pruefen(versuche - 1), 25);
        return;
      }
      if (widget.getState() === "unverified") widget.verify();
    };
    customElements.whenDefined("altcha-widget").then(() => pruefen(80));
  });
})();
