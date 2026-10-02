"""Gestaltungssystem: Bänder, Abstände, Seitenkopf, Produktfarben und -reihenfolge, Darstellung der Seiten."""

import re
from io import StringIO

from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.utils.safestring import mark_safe

from marketing.templatetags.baender import abschnitt, band_folge, kernsatz_html, produkt_aus, produkt_ordnung

BAND = re.compile(r'<(?:section|div|nav|article)[^>]*class="[^"]*\bband-([a-z]+)\b')


def baender_der_seite(html):
    """Bänder in der Reihenfolge des Hauptbereichs (ohne Fußzeile)."""
    haupt = html[html.find('role="main"'):html.find('role="contentinfo"')]
    return BAND.findall(haupt)


class BandFolgeTests(SimpleTestCase):
    def test_hero_hell_wechsel_einladung_dunkel(self):
        typen = ["hero", "mandari_cards", "split_rows", "feature_matrix", "gradient_cta"]
        self.assertEqual(band_folge(typen), ["hell", "grau", "hell", "grau", "tinte"])

    def test_nie_zwei_gleiche_baender_nebeneinander(self):
        typen = ["hero", "pricing_table", "mandari_cards", "gradient_cta", "feature_matrix",
                 "two_column_use_case", "mandari_cards", "accordion_faq", "gradient_cta"]
        baender = band_folge(typen)
        self.assertEqual(baender[3], "marke")  # Einladung mitten auf der Seite
        self.assertEqual(baender[-1], "tinte")
        for links, rechts in zip(baender, baender[1:]):
            self.assertNotEqual(links, rechts)

    def test_zusaetze_bleiben_auf_dem_band_artikel_wechseln(self):
        typen = ["hero", "trust_banner", "mandari_cards", "numbered_article", "disclaimer_box",
                 "numbered_article", "numbered_article", "gradient_cta"]
        self.assertEqual(band_folge(typen), ["hell", "hell", "grau", "hell", "hell", "grau", "hell", "tinte"])

    def test_dokumente_durchgehend_weiss(self):
        # Rechtstexte und Quellen: Kopf und Text auf demselben weißen Band, wie ein gedrucktes Dokument
        typen = ["hero", "table_of_contents", "numbered_article", "numbered_article", "disclaimer_box"]
        self.assertEqual(band_folge(typen, ruhig=True), ["hell"] * 5)
        typen = ["hero", "richtext_section", "richtext_section", "disclaimer_box"]
        self.assertEqual(band_folge(typen, ruhig=True), ["hell"] * 4)

    def test_hero_immer_hell(self):
        # Ein Seitenkopf für alle Seiten: keine Produktfläche im Hero, die Kennfarbe steht nur im Bild und im Namen
        typen = ["hero", "mandari_cards", "two_column_use_case", "gradient_cta"]
        self.assertEqual(band_folge(typen), ["hell", "grau", "hell", "tinte"])

    def test_einladung_mitten_nie_neben_hellgrau(self):
        # Nach Weiß auf der Markenfläche, nach Hellgrau auf Weiß – Markenfläche und Hellgrau nie nebeneinander
        self.assertEqual(band_folge(["hero", "gradient_cta", "mandari_cards", "gradient_cta"]),
                         ["hell", "marke", "hell", "tinte"])
        baender = band_folge(["hero", "mandari_cards", "gradient_cta", "mandari_cards", "gradient_cta"])
        self.assertEqual(baender, ["hell", "grau", "hell", "grau", "tinte"])


class AbschnittTests(SimpleTestCase):
    def test_eine_abstandsskala(self):
        self.assertEqual(abschnitt("grau", True, True), "band-grau abschnitt")
        self.assertEqual(abschnitt("", "", "", standard="grau"), "band-grau abschnitt")
        self.assertEqual(abschnitt("hell", True, True, art="kompakt"), "band-hell abschnitt-kompakt")
        self.assertEqual(abschnitt(None, art="hero"), "band-hell hero")

    def test_fortsetzung_auf_demselben_band(self):
        # Kein doppelter Abschnittsabstand, wenn ein Block das Band seines Vorgängers fortsetzt
        self.assertEqual(abschnitt("hell", False, False), "band-hell abschnitt fortsetzung fortgesetzt")
        self.assertEqual(abschnitt("hell", True, False, art="hero"), "band-hell hero fortgesetzt")


class ProduktReihenfolgeTests(SimpleTestCase):
    def test_session_work_insight(self):
        spalten = ["Insight (Bürgerportal)", "Work (Fraktionen)", "Session (Verwaltung)"]
        self.assertEqual(produkt_ordnung(spalten), [2, 1, 0])
        self.assertEqual(produkt_ordnung(["mandari Insight", "mandari Work", "mandari Session"]), [2, 1, 0])

    def test_ohne_produktspalten_bleibt_die_reihenfolge(self):
        spalten = ["Selbst-Hosting", "Managed Hosting", "On-Premises mit Support"]
        self.assertEqual(produkt_ordnung(spalten), [0, 1, 2])
        self.assertEqual(produkt_ordnung(["Session", "Kosten"]), [0, 1])


class ProduktTests(SimpleTestCase):
    def test_eindeutiger_bezug(self):
        self.assertEqual(produkt_aus("Bürgerportal mandari Insight"), "insight")
        self.assertEqual(produkt_aus("Verwaltungs-RIS mandari Session"), "session")
        self.assertEqual(produkt_aus("Work (Fraktionen)"), "work")

    def test_mehrere_oder_keins(self):
        self.assertEqual(produkt_aus("Session · Work · Insight"), "")
        self.assertEqual(produkt_aus("Ein Datenbestand"), "")
        self.assertEqual(produkt_aus("Workshop für Ihre Fraktion"), "")

    def test_kernsatz_nur_bei_gerendertem_text(self):
        html = mark_safe(
            "<p>Sitzungsdienst ohne Medienbrüche. Das Ratsinformationssystem führt Ihren Sitzungsdienst von der "
            "Tagesordnung bis zur freigegebenen Niederschrift.</p>"
        )
        self.assertIn('<span class="kernsatz">Sitzungsdienst ohne Medienbrüche.</span> Das', kernsatz_html(html))
        self.assertEqual(kernsatz_html("<p>Nicht maskiert. " + "x" * 200 + "</p>"), "<p>Nicht maskiert. " + "x" * 200 + "</p>")


class SeitenTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        call_command("setup_initial_pages", stdout=StringIO())
        call_command("migrate_pages_to_streamfield", stdout=StringIO())

    def seite(self, url):
        antwort = self.client.get(url)
        self.assertEqual(antwort.status_code, 200, url)
        return antwort.content.decode("utf-8")

    def test_benachbarte_baender_unterscheiden_sich(self):
        for url in ["/", "/produkte/", "/fraktionen/", "/kommunen/", "/preise/", "/unternehmen/", "/presse/",
                    "/roadmap/", "/vergabe/", "/open-source/", "/karriere/"]:
            baender = baender_der_seite(self.seite(url))
            self.assertGreater(len(baender), 2, url)
            for links, rechts in zip(baender, baender[1:]):
                self.assertNotEqual(links, rechts, f"{url}: zweimal {links} nebeneinander ({baender})")

    def test_startseite_und_produkte_zeigen_drei_produktflaechen(self):
        for url in ["/", "/produkte/"]:
            html = self.seite(url)
            for produkt in ["session", "work", "insight"]:
                self.assertEqual(html.count(f'class="produkt produkt-{produkt} '), 1, f"{url}: {produkt}")
            # Alle drei Flächen gleich gebaut: die Bildschirme stehen im Hero, keine Fläche trägt ein eigenes Bild
            flaechen = html[html.find('class="produkt produkt-session'):]
            flaechen = flaechen[:flaechen.find("</section>")]
            self.assertNotIn("<img", flaechen, url)
            self.assertLess(html.find("produkt-session "), html.find("produkt-work "), url)
            self.assertLess(html.find("produkt-work "), html.find("produkt-insight "), url)

    def test_trust_center_keine_textwand(self):
        # Zusätze (Leiste unter dem Hero, Hinweis nach Artikel 1) setzen das Band davor fort; jeder
        # nummerierte Artikel bekommt im Wechsel ein eigenes Band.
        baender = baender_der_seite(self.seite("/trust/"))
        zusammengefasst = [b for i, b in enumerate(baender) if i == 0 or baender[i - 1] != b]
        self.assertEqual(zusammengefasst, ["hell", "grau", "hell", "grau", "hell", "grau", "hell", "grau", "tinte"])

    def test_ein_seitenkopf_fuer_alle_seiten(self):
        # Weiß, dieselbe Schriftstufe; Produktseiten zeigen rechts ein echtes Bild ihres Produkts
        bilder = {"/produkte/": ["hero-session-800", "hero-work-800", "hero-insight-muenster-800"],
                  "/kommunen/": ["hero-session-800"], "/fraktionen/": ["hero-work-800"]}
        for url in ["/produkte/", "/kommunen/", "/fraktionen/", "/preise/", "/unternehmen/", "/presse/",
                    "/trust/", "/vergleich/", "/kontakt/", "/quellen/", "/impressum/", "/releases/"]:
            html = self.seite(url)
            self.assertEqual(baender_der_seite(html)[0], "hell", url)
            kopf = html[html.find('role="main"'):]
            kopf = kopf[:kopf.find("</h1>")]
            self.assertIn('class="t-h1 ', kopf, url)
            hero = html[html.find('role="main"'):]
            hero = hero[:hero.find("</section>")]
            for bild in bilder.get(url, []):
                self.assertIn(bild, hero, url)
            if url not in bilder:
                self.assertNotIn("<figure", hero, url)

    def test_keine_ankuendigung_kuenftiger_werkzeuge(self):
        # Weitere Werkzeuge stehen nur in der Roadmap, nicht auf Produkt-, Presse- und Unternehmensseiten
        for url in ["/", "/produkte/", "/presse/", "/unternehmen/"]:
            html = self.seite(url)
            for wort in ["Als Nächstes", "mandari Data", "mandari App", "Wahlergebnisse", "weitere in Entwicklung",
                         "Weitere Werkzeuge"]:
                self.assertNotIn(wort, html, f"{url}: {wort}")
        self.assertIn('href="/roadmap/"', self.seite("/produkte/"))
        self.assertIn("mandari Data", self.seite("/roadmap/"))

    def test_eintraege_titel_ueber_dem_text(self):
        # Kein Muster „Überschrift links, Text rechts“ mehr: Wertekompass im Raster, Wegmarken als Zeitleiste,
        # Mission und Vision in der Randspalte neben „Warum wir das tun“
        html = self.seite("/unternehmen/")
        self.assertNotIn("lg:col-span-7 lg:col-start-6", html)
        werte = html[html.find('id="werte"'):]
        werte = werte[:werte.find("</section>")]
        self.assertIn("md:grid-cols-2", werte)
        self.assertNotIn("lg:col-span-4", werte)
        wegmarken = html[html.find('id="wegmarken"'):]
        self.assertIn("<ol", wegmarken[:wegmarken.find("</section>")])
        warum = html[html.find('id="warum"'):]
        warum = warum[:warum.find("</section>")]
        self.assertIn("<aside", warum)
        self.assertIn("Unsere Mission", warum)
        self.assertIn("Unsere Vision", warum)

    def test_funktionsuebersicht_in_produktreihenfolge(self):
        html = self.seite("/produkte/")
        tabelle = html[html.find('id="funktionen"'):]
        self.assertLess(tabelle.find("Session (Verwaltung)"), tabelle.find("Work (Fraktionen)"))
        self.assertLess(tabelle.find("Work (Fraktionen)"), tabelle.find("Insight (Bürgerportal)"))
        preise = self.seite("/preise/")
        self.assertLess(preise.find(">mandari Session</h3>"), preise.find(">mandari Work</h3>"))
        self.assertLess(preise.find(">mandari Work</h3>"), preise.find(">mandari Insight</h3>"))

    def test_einladung_am_ende_dunkel(self):
        for url in ["/produkte/", "/preise/", "/unternehmen/"]:
            self.assertEqual(baender_der_seite(self.seite(url))[-1], "tinte", url)

    def test_kontakt_hat_ueberschrift(self):
        self.assertIn(">Sprechen wir über Ihre Verwaltung.</h1>", self.seite("/kontakt/"))

    def test_kontakt_hilfetexte_lesbar_auf_hellgrau(self):
        # Das Formular liegt auf Hellgrau; Grau 500 erreicht dort nur 4,2:1, Grau 600 erreicht 6,6:1.
        html = self.seite("/kontakt/")
        formular = html[html.find('id="termin"'):html.find("Direkt zur richtigen Stelle")]
        self.assertIn("(optional)", formular)
        self.assertNotIn("text-gray-500", formular)

    def test_kuendigungsbutton_ist_ein_aufruf(self):
        # § 312k BGB: der Knopf muss lesbar sein – die Linkgestalt des Fließtexts darf ihn nicht überschreiben
        html = self.seite("/kuendigung/")
        self.assertIn('class="btn-primary">Jetzt Vertrag kündigen</a>', html)
        self.assertNotIn("text-align:center", html)

    def test_kontakt_ein_formularsystem(self):
        # Beide Formulare: gleiche Felder (Klasse feld, 48 px), gleicher Aufruf, Umschalter Termin | Nachricht
        html = self.seite("/kontakt/")
        self.assertEqual(html.count('<button type="submit" class="btn-primary">'), 2)
        self.assertIn('role="tablist"', html)
        self.assertEqual(html.count('role="tabpanel"'), 2)
        self.assertEqual(html.count('rows="5"'), 2)
        self.assertGreaterEqual(html.count('class="feld"'), 14)

    def test_eintrag_mit_produktbezug_traegt_die_kennfarbe(self):
        html = self.seite("/kommunen/")
        self.assertRegex(html, r'class="flex flex-col produkt-insight"')
