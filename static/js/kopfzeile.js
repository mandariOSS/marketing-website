// SPDX-License-Identifier: AGPL-3.0-or-later
//
// Kopfzeile von mandari.de (templates/components/navbar.html):
// * kopfzeile    – Schatten beim Scrollen, Schalter für den dunklen Modus und das Slide-Menü für schmale
//                  Bildschirme (Dialog mit Fokusfalle, gesperrtem Seiten-Scroll, Escape und Klick auf den Hintergrund)
// * produkteMenue – Aufklappmenü „Produkte“ auf breiten Bildschirmen (Klick, Enter/Leertaste, Pfeiltasten)
//
// Wird vor Alpine geladen (beide mit defer, die Reihenfolge in base.html zählt).
//
// Fokus in der Kopfzeile immer mit preventScroll: Sie haftet oben und ist immer sichtbar, die Seite soll dabei
// nicht springen (der Abstand für Anker und Fokus im Inhalt steht als scroll-margin in base.html).

document.addEventListener("alpine:init", () => {
  const FOKUSSIERBAR = 'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])';
  const DESKTOP = window.matchMedia("(min-width: 1024px)");
  const OHNE_SCROLL = { preventScroll: true };

  // Ein Link auf die aktuelle Seite verschwindet mit dem Menü. Der Fokus geht auf das Ziel des Ankers
  // (das der Browser gleich anspringt) oder, ohne Anker, auf den Knopf, der das Menü geöffnet hat.
  const fokusNachAuswahl = (link, knopf) => {
    const ziel = link.hash && document.getElementById(decodeURIComponent(link.hash.slice(1)));
    if (!ziel) {
      knopf.focus(OHNE_SCROLL);
      return;
    }
    if (!ziel.hasAttribute("tabindex")) ziel.setAttribute("tabindex", "-1");
    ziel.focus(OHNE_SCROLL);
  };

  window.Alpine.data("kopfzeile", () => ({
    gescrollt: false,
    menueOffen: false,
    gesperrt: [],
    // Gesetzt hat die Klasse schon das Skript im Kopf von base.html; hier nur der Schalter und das Merken.
    darkMode: document.documentElement.classList.contains("dark"),

    init() {
      this.$watch("darkMode", (dunkel) => {
        document.documentElement.classList.toggle("dark", dunkel);
        try {
          localStorage.setItem("darkMode", dunkel);
        } catch (e) {
          // ohne Speicher gilt der Modus nur für diese Seite
        }
      });
      const pruefen = () => {
        this.gescrollt = window.scrollY > 4;
      };
      // Erst im nächsten Bild: scrollY verlangt ein fertiges Layout und würde es sonst mitten im Start von Alpine
      // erzwingen – eine lange Aufgabe, die das erste Antworten der Seite verzögert.
      requestAnimationFrame(pruefen);
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
      if (!link || link.pathname !== window.location.pathname) return;
      this.schliessen(false);
      fokusNachAuswahl(link, this.$refs.menueKnopf);
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
      this.$nextTick(() => this.$refs.schliessenKnopf.focus(OHNE_SCROLL));
    },

    schliessen(fokusZurueck = true) {
      if (!this.menueOffen) return;
      this.menueOffen = false;
      this.gesperrt.forEach((el) => el.removeAttribute("inert"));
      this.gesperrt = [];
      const html = document.documentElement;
      html.style.overflow = "";
      html.style.paddingRight = "";
      if (fokusZurueck) this.$refs.menueKnopf.focus(OHNE_SCROLL);
    },

    // Tab und Umschalt+Tab laufen im Menü im Kreis. Ohne preventScroll, damit ein hohes Menü
    // (Querformat) den Eintrag in seinem eigenen Bereich sichtbar scrollt.
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

    // Index wie bei Array.at: 0 ist der erste, -1 der letzte Eintrag.
    fokussieren(index) {
      this.eintraege().at(index)?.focus(OHNE_SCROLL);
    },

    umschalten() {
      this.offen = !this.offen;
    },

    // Pfeil runter öffnet und springt auf den ersten Eintrag, Pfeil hoch auf den letzten.
    oeffnenBei(index) {
      this.offen = true;
      this.$nextTick(() => this.fokussieren(index));
    },

    bewegen(schritt) {
      const eintraege = this.eintraege();
      const aktuell = eintraege.indexOf(document.activeElement);
      this.fokussieren(aktuell === -1 ? (schritt > 0 ? 0 : -1) : (aktuell + schritt) % eintraege.length);
    },

    linkGewaehlt(event) {
      const link = event.target.closest("a[href]");
      if (!link) return;
      this.schliessen();
      if (link.pathname === window.location.pathname) fokusNachAuswahl(link, this.$refs.knopf);
    },

    schliessen(fokusZurueck = false) {
      if (!this.offen) return;
      this.offen = false;
      if (fokusZurueck) this.$refs.knopf.focus(OHNE_SCROLL);
    },
  }));
});
