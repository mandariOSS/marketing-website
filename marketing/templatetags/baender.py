"""
Hintergrundbänder, Abstände und Produktfarben.

Jeder Abschnitt einer Seite liegt auf einem vollbreiten Band mit eigenem Hintergrund, damit sich Bereiche
auch am Handy klar voneinander abheben. ``baender`` legt die Bänder für StreamField-Seiten nach der
Reihenfolge der Blöcke fest – ohne dass Redaktion oder Seeds etwas einstellen müssen:

* der Hero immer hell (ein Seitenkopf für alle Seiten; Produktseiten zeigen rechts ein echtes Bild,
  siehe ``hero_bild``),
* danach abwechselnd Hellgrau und Weiß, nie zwei gleiche Bänder nebeneinander – auch die nummerierten
  Artikel im Trust Center, damit lange Seiten am Handy nicht zu einer Textwand werden,
* eine Einladung mitten auf der Seite auf der Markenfläche (nach Weiß) oder auf Weiß (nach Hellgrau),
  die abschließende Einladung dunkel,
* kleine Zusätze (Eckdaten, Hinweis, Warrant Canary) bleiben auf dem Band davor,
* Dokumente (Rechtstexte, Quellen) ruhig: Kopf und Text durchgehend auf Weiß, wie ein gedrucktes Dokument.

``abschnitt`` setzt Band und Innenabstand aus der einen Abstandsskala (static/css/input.css). Die Farben
selbst stehen dort ebenfalls (Klassen ``band-*`` und ``produkt-*``, hell und dunkel).

Produktfarben (aus den Anwendungen abgeleitet): Session trägt ein Petrol, abgeleitet vom Blau des
Sitzungsdienstes (Standardfarbe der Kommune in Session) und so weit ins Petrol geschoben, dass es sich
am Handy klar vom Indigo abhebt; Work das Indigo des Fraktionsbereichs (Standardfarbe der Organisation
in Work), Insight ein ruhiges Grün, wie bisher auf der Preisseite. Die Produkte stehen überall in derselben
Reihenfolge: Session, Work, Insight.
"""

import re

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

HELL, GRAU, MARKE, TINTE = "hell", "grau", "marke", "tinte"

# Gehören zum Abschnitt davor und bekommen kein eigenes Band.
ANGEHAENGT = {"trust_banner", "disclaimer_box", "warrant_canary"}

# Seiten mit einem echten Produktbild im Hero: der Stapel aus drei Bildschirmen wie auf der Startseite
# oder ein Bildschirm des Produkts, dem die Seite gehört.
HERO_BILD = {"produkte": "stapel", "kommunen": "session", "fraktionen": "work"}

# Feste Reihenfolge der Produkte in Tabellen, Preisen und Flächen
REIHENFOLGE = ("session", "work", "insight")

PRODUKTE = {
    "session": {
        "name": "mandari Session",
        "bild": {
            "src": "images/startseite/hero-session-800.webp",
            "src_gross": "images/startseite/hero-session-1600.webp",
            "alt": "mandari Session: Sitzungsübersicht der Stadtverwaltung mit kommenden Sitzungen von Rat und "
                   "Ausschüssen und ihrem Stand",
        },
    },
    "work": {
        "name": "mandari Work",
        "bild": {
            "src": "images/startseite/hero-work-800.webp",
            "src_gross": "images/startseite/hero-work-1600.webp",
            "alt": "mandari Work: Die Fraktion bereitet die Ratssitzung vor und legt zu jedem Tagesordnungspunkt "
                   "ihre Position fest",
        },
    },
    "insight": {
        "name": "mandari Insight",
        "bild": {
            "src": "images/startseite/hero-insight-muenster-800.webp",
            "src_gross": "images/startseite/hero-insight-muenster-1600.webp",
            "alt": "mandari Insight für Münster: Suche in den Ratsinformationen, kommende Sitzungen und neueste "
                   "Vorgänge der Stadt",
        },
    },
}

_PRODUKT_MUSTER = {
    "session": re.compile(r"\bSession\b"),
    "work": re.compile(r"\bWork\b"),
    "insight": re.compile(r"\bInsight\b|Bürgerportal"),
}


def band_folge(typen, ruhig=False):
    """Bänder für eine Folge von Block-Typen.

    Gibt je Block ein Band zurück (``hell``, ``grau``, ``marke`` oder ``tinte``). ``ruhig`` setzt Dokumente
    ohne Wechsel: Kopf und Text durchgehend weiß.
    """
    baender = []
    for index, typ in enumerate(typen):
        vorher = baender[-1] if baender else None
        letzter = index == len(typen) - 1
        if index == 0 and typ == "hero":
            band = HELL
        elif vorher and typ in ANGEHAENGT:
            band = vorher
        elif typ == "gradient_cta" and letzter:
            band = TINTE
        elif ruhig:
            band = HELL
        elif typ == "gradient_cta":
            # Mitten auf der Seite: Markenfläche nach Weiß, sonst Weiß – nie neben Hellgrau
            band = MARKE if vorher in (None, HELL) else HELL
        else:
            band = GRAU if vorher in (None, HELL) else HELL
        baender.append(band)
    return baender


def _abschnitte(eintraege, baender):
    abschnitte = []
    for index, (eintrag, band) in enumerate(zip(eintraege, baender)):
        abschnitte.append(
            {
                "block": eintrag,
                "einschub": eintrag is None,
                "band": band,
                "anfang": index == 0 or baender[index - 1] != band,
                "ende": index == len(baender) - 1 or baender[index + 1] != band,
                "letzter": index == len(baender) - 1,
            }
        )
    return abschnitte


@register.simple_tag(takes_context=True)
def baender(context, body, einschub_nach=None, ruhig=False):
    """Blöcke mit ihrem Band: ``{% baender page.body as abschnitte %}``.

    Jeder Eintrag hat ``block``, ``band``, ``anfang``/``ende`` (beginnt oder endet hier ein Band)
    und ``letzter``. Mit ``einschub_nach`` kommt an der Stelle von ``insert_position`` ein Eintrag mit
    ``einschub`` (fester Abschnitt wie die Angaben zum Unternehmen), der im Wechsel mitzählt.
    """
    bloecke = list(body or [])
    eintraege = list(bloecke)
    if einschub_nach is not None:
        from company.templatetags.company_tags import insert_position

        eintraege.insert(insert_position(body, einschub_nach), None)
    typen = ["einschub" if e is None else e.block_type for e in eintraege]
    return _abschnitte(eintraege, band_folge(typen, ruhig=ruhig))


@register.simple_tag
def abschnitt(band=None, anfang=True, ende=True, standard=HELL, art="abschnitt"):
    """Klassen eines Abschnitts: ``<section class="{% abschnitt band band_anfang band_ende %}">``.

    Band (``band-*``) und Innenabstand aus der einen Skala: ``abschnitt`` (96 px, am Handy 64), ``kompakt``
    (64/48) oder ``hero``. Setzt der Block das Band seines Vorgängers fort (``anfang`` ist False), entfällt
    der Abstand nach oben; geht das Band nach ihm weiter (``ende`` ist False), bleibt ein Unterabschnitt
    (48 px). Ohne Angaben (Block außerhalb von ``baender``) gilt der volle Abstand.
    """
    klassen = [f"band-{band or standard}", {"kompakt": "abschnitt-kompakt"}.get(art, art)]
    if anfang is False:
        klassen.append("fortsetzung")
    if ende is False:
        klassen.append("fortgesetzt")
    return " ".join(klassen)


@register.simple_tag(takes_context=True)
def hero_bild(context):
    """Bild im Hero der aktuellen Seite: ``stapel`` (drei Produkte), ein Produktschlüssel oder ``""``."""
    page = context.get("page")
    return HERO_BILD.get(getattr(page, "slug", ""), "")


def produkt_aus(*texte):
    """Schlüssel des Produkts, auf das sich ein Text eindeutig bezieht – sonst ``""``.

    „Bürgerportal mandari Insight“ → ``insight``; „Session · Work · Insight“ nennt mehrere → ``""``.
    """
    for text in texte:
        if not text:
            continue
        treffer = [key for key, muster in _PRODUKT_MUSTER.items() if muster.search(str(text))]
        if len(treffer) == 1:
            return treffer[0]
        if treffer:
            return ""
    return ""


@register.filter
def produkt(text):
    """``{{ card.subtitle|produkt }}`` → ``session``, ``work``, ``insight`` oder leer."""
    return produkt_aus(text)


@register.simple_tag
def produkt_zeile(row):
    """Produkt einer Zeile in „Heute im Einsatz“: über den Anker (``#session``) oder den Titel."""
    anker = (row.get("anchor_id") or "").strip()
    if anker in PRODUKTE:
        return anker
    titel = (row.get("title") or "").strip()
    for key, daten in PRODUKTE.items():
        if titel == daten["name"]:
            return key
    return ""


@register.simple_tag
def produkt_bild(key):
    """Bildschirm eines Produkts mit fertigen Adressen (``url``, ``url_gross``) und Alternativtext."""
    bild = (PRODUKTE.get(key) or {}).get("bild")
    if not bild:
        return None
    return {**bild, "url": static(bild["src"]), "url_gross": static(bild["src_gross"])}


def _rang(schluessel):
    return REIHENFOLGE.index(schluessel) if schluessel in REIHENFOLGE else len(REIHENFOLGE)


def produkt_ordnung(namen):
    """Indizes von ``namen`` in der festen Produktreihenfolge (Session, Work, Insight).

    Nur wenn jede Spalte eindeutig ein Produkt ist, wird umsortiert; sonst bleibt die Reihenfolge.
    """
    schluessel = [produkt_aus(name) for name in namen]
    if not schluessel or not all(schluessel) or len(set(schluessel)) != len(schluessel):
        return list(range(len(namen)))
    return sorted(range(len(namen)), key=lambda i: _rang(schluessel[i]))


@register.simple_tag
def produkt_matrix(value):
    """Funktionsübersicht in Produktreihenfolge: ``{% produkt_matrix self as m %}`` mit ``columns`` und
    ``groups`` (Zeilen mit ``label``, ``description``, ``cells``)."""
    spalten = list(value.get("columns") or [])
    ordnung = produkt_ordnung(spalten)
    gruppen = []
    for gruppe in value.get("groups") or []:
        zeilen = []
        for zeile in gruppe.get("rows") or []:
            zellen = list(zeile.get("cells") or [])
            zellen = [zellen[i] for i in ordnung if i < len(zellen)] + zellen[len(ordnung):]
            zeilen.append({"label": zeile.get("label"), "description": zeile.get("description"), "cells": zellen})
        gruppen.append({"title": gruppe.get("title"), "rows": zeilen})
    return {"columns": [spalten[i] for i in ordnung], "groups": gruppen}


@register.simple_tag
def produkt_stufen(tiers):
    """Preisstufen in Produktreihenfolge (Session, Work, Insight), wenn jede Stufe ein Produkt ist."""
    stufen = list(tiers or [])
    return [stufen[i] for i in produkt_ordnung([t.get("name") for t in stufen])]


# Abkürzungen, nach denen kein Satz endet
_ABKUERZUNGEN = {
    "z", "b", "d", "h", "u", "a", "s", "o", "ca", "bzw", "ggf", "inkl", "zzgl", "evtl", "vgl", "bspw",
    "usw", "etc", "nr", "abs", "mio", "mrd", "dr", "st", "str", "tel", "ff",
}
_SATZENDE = re.compile(r"[.!?](?=\s+[A-ZÄÖÜ„\"])")
KERNSATZ_AB = 120  # kürzere Texte bleiben ein Absatz in einem Ton


def kernsatz_teilen(text):
    """Ersten Satz und Rest trennen; ``(text, "")``, wenn es keinen sinnvollen Schnitt gibt."""
    text = (text or "").strip()
    if len(text) < KERNSATZ_AB:
        return text, ""
    for treffer in _SATZENDE.finditer(text):
        wort = re.search(r"([A-Za-zÄÖÜäöüß]+)$", text[: treffer.start()])
        if wort and (wort.group(1).lower() in _ABKUERZUNGEN or len(wort.group(1)) == 1):
            continue
        erster, rest = text[: treffer.end()], text[treffer.end():].strip()
        if rest and len(erster) <= 170:
            return erster, rest
        break
    return text, ""


_ERSTER_ABSATZ = re.compile(r"^\s*<p( [^>]*)?>([^<]*)")


@register.filter
def kernsatz_html(html):
    """Kernsatz einer Produktfläche: hebt den ersten Satz des ersten Absatzes von gerendertem Rich Text
    hervor (wenn er ohne Auszeichnung beginnt), damit der Text am Handy nicht als Wand wirkt.
    Sonst bleibt der Text unverändert."""
    if not hasattr(html, "__html__"):
        return html  # nur bereits gerenderter Rich Text (SafeString oder RichText)
    text = str(html.__html__())
    treffer = _ERSTER_ABSATZ.match(text)
    if not treffer:
        return html
    absatz_ende = text.find("</p>")
    absatz = text[treffer.start(2):absatz_ende if absatz_ende > 0 else len(text)]
    erster, rest = kernsatz_teilen(absatz)
    if not rest or "<" in erster or not treffer.group(2).startswith(erster):
        return html
    anfang = treffer.start(2)
    # Der Text stammt aus gerendertem Rich Text und ist bereits maskiert.
    return mark_safe(f'{text[:anfang]}<span class="kernsatz">{erster}</span>{text[anfang + len(erster):]}')
