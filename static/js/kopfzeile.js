// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Kopfzeile von mandari.de (templates/components/navbar.html):
// * kopfzeile    – Schatten beim Scrollen und das Slide-Menü für schmale Bildschirme
//                  (Dialog mit Fokusfalle, gesperrtem Seiten-Scroll, Escape und Klick auf den Hintergrund)
// * produkteMenue – Aufklappmenü „Produkte“ auf breiten Bildschirmen (Klick, Enter/Leertaste, Pfeiltasten)
//
// Wird vor Alpine geladen (beide mit defer, die Reihenfolge in base.html zählt).

document.addEventListener("alpine:init", () => {
  const FOKUSSIERBAR = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const DESKTOP = window.matchMedia("(min-width: 1024px)");

  window.Alpine.data("kopfzeile", () => ({
    gescrollt: false,
    menueOffen: false,
    gesperrt: [],

    init() {
      const pruefen = () => {
        this.gescrollt = window.scrollY > 4;
      };
      pruefen();
      window.addEventListener("scroll", pruefen, { passive: true });
      // Wird das Fenster breit genug für das Desktop-Menü, schließt das Slide-Menü.
      DESKTOP.addEventListener("change", (event) => {
        if (event.matches) this.schliessen(false);
      });
      // Zurück-Taste: Seiten aus dem Verlaufs-Cache kommen mit geschlossenem Menü wieder.
      window.addEventListener("pageshow", (event) => {
        if (event.persisted) this.schliessen(false);
      });
    },

    // Ein Anker auf derselben Seite lädt nichts neu – dann schließt das Menü selbst.
    linkGewaehlt(event) {
      const link = event.target.closest("a[href]");
      if (link && link.pathname === window.location.pathname) this.schliessen(false);
    },

    oeffnen() {
      if (this.menueOffen) return;
      const html = document.documentElement;
      const scrollleiste = window.innerWidth - html.clientWidth;
      html.style.overflow = "hidden";
      if (scrollleiste > 0) html.style.paddingRight = `${scrollleiste}px`;
      // Alles außer dem Menü ist währenddessen weder per Tastatur noch per Screenreader erreichbar.
      this.gesperrt = [...document.body.children]
        .filter((el) => !el.contains(this.$root) && el.tagName !== "SCRIPT")
        .concat(this.$refs.leiste);
      this.gesperrt.forEach((el) => el.setAttribute("inert", ""));
      this.menueOffen = true;
      this.$nextTick(() => this.$refs.schliessenKnopf.focus({ preventScroll: true }));
    },

    schliessen(fokusZurueck = true) {
      if (!this.menueOffen) return;
      this.menueOffen = false;
      this.gesperrt.forEach((el) => el.removeAttribute("inert"));
      this.gesperrt = [];
      const html = document.documentElement;
      html.style.overflow = "";
      html.style.paddingRight = "";
      if (fokusZurueck) this.$refs.menueKnopf.focus({ preventScroll: true });
    },

    // Tab und Umschalt+Tab laufen im Menü im Kreis.
    fokusHalten(event) {
      const elemente = [...this.$refs.panel.querySelectorAll(FOKUSSIERBAR)].filter(
        (el) => el.getClientRects().length > 0,
      );
      if (!elemente.length) return;
      const erstes = elemente[0];
      const letztes = elemente[elemente.length - 1];
      if (event.shiftKey && document.activeElement === erstes) {
        event.preventDefault();
        letztes.focus();
      } else if (!event.shiftKey && document.activeElement === letztes) {
        event.preventDefault();
        erstes.focus();
      }
    },
  }));

  window.Alpine.data("produkteMenue", () => ({
    offen: false,

    init() {
      window.addEventListener("pageshow", (event) => {
        if (event.persisted) this.offen = false;
      });
    },

    eintraege() {
      return [...this.$refs.liste.querySelectorAll("a")];
    },

    umschalten() {
      this.offen = !this.offen;
    },

    // Pfeil runter öffnet und springt auf den ersten Eintrag, Pfeil hoch auf den letzten.
    oeffnenBei(index) {
      this.offen = true;
      this.$nextTick(() => this.eintraege().at(index)?.focus());
    },

    bewegen(schritt) {
      const eintraege = this.eintraege();
      const aktuell = eintraege.indexOf(document.activeElement);
      const ziel = aktuell === -1 ? (schritt > 0 ? 0 : -1) : (aktuell + schritt) % eintraege.length;
      eintraege.at(ziel).focus();
    },

    schliessen(fokusZurueck = false) {
      if (!this.offen) return;
      this.offen = false;
      if (fokusZurueck) this.$refs.knopf.focus();
    },
  }));
});
