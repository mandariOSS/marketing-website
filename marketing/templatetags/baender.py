"""
Hintergrundbänder und Produktfarben.

Jeder Abschnitt einer Seite liegt auf einem vollbreiten Band mit eigenem Hintergrund, damit sich Bereiche
auch am Handy klar voneinander abheben. ``baender`` legt die Bänder für StreamField-Seiten nach der
Reihenfolge der Blöcke fest – ohne dass Redaktion oder Seeds etwas einstellen müssen:

* Hero hell (auf den Produktseiten in der Fläche des Produkts),
* danach abwechselnd Hellgrau und Weiß, nie zwei gleiche Bänder nebeneinander – auch die nummerierten
  Artikel im Trust Center, damit lange Seiten am Handy nicht zu einer Textwand werden,
* eine Einladung mitten auf der Seite auf der zarten Markenfläche, die abschließende Einladung dunkel,
* kleine Zusätze (Eckdaten, Hinweis, Warrant Canary) bleiben auf dem Band davor,
* Rechtstexte ruhig: Titel auf Hellgrau, der Text durchgehend auf Weiß.

Die Farben selbst stehen in ``static/css/input.css`` (Klassen ``band-*`` und ``produkt-*``, hell und dunkel).

Produktfarben (aus den Anwendungen abgeleitet): Session trägt ein Petrol, abgeleitet vom Blau des
Sitzungsdienstes (Standardfarbe der Kommune in Session) und so weit ins Petrol geschoben, dass es sich
am Handy klar vom Indigo abhebt; Work das Indigo des Fraktionsbereichs (Standardfarbe der Organisation
in Work), Insight ein ruhiges Grün, wie bisher auf der Preisseite.
"""

import re

from django import template
from django.templatetags.static import static
from django.utils.safestring import mark_safe

register = template.Library()

HELL, GRAU, MARKE, TINTE = "hell", "grau", "marke", "tinte"

# Gehören zum Abschnitt davor und bekommen kein eigenes Band.
ANGEHAENGT = {"trust_banner", "disclaimer_box", "warrant_canary"}

# Seiten, die ganz einem Produkt gehören: Hero in der Fläche des Produkts.
PRODUKT_JE_SEITE = {"fraktionen": "work", "kommunen": "session"}

PRODUKTE = {
    "session": {
        "name": "mandari Session",
        "bild": None,
    },
    "work": {
        "name": "mandari Work",
        "bild": None,
    },
    "insight": {
        "name": "mandari Insight",
        # Echter Screenshot des Bürgerportals (Münster), dasselbe Bild wie im Hero der Startseite
        "bild": {
            "src": "images/startseite/insight-muenster-1280.webp",
            "breite": 1280,
            "hoehe": 800,
            "alt": "mandari Insight für Münster: Suche in den Ratsinformationen und kommende Sitzungen",
        },
    },
}

_PRODUKT_MUSTER = {
    "session": re.compile(r"\bSession\b"),
    "work": re.compile(r"\bWork\b"),
    "insight": re.compile(r"\bInsight\b|Bürgerportal"),
}


def band_folge(typen, produkt=None, ruhig=False):
    """Bänder für eine Folge von Block-Typen.

    Gibt je Block ein Band zurück (``hell``, ``grau``, ``marke``, ``tinte`` oder den Schlüssel eines
    Produkts). ``produkt`` färbt Hero und Markenfläche in der Fläche des Produkts, ``ruhig`` setzt
    Rechtstexte ohne Wechsel: Titel hellgrau, alles danach weiß.
    """
    baender = []
    # Nach einem hellen Hero beginnt der Wechsel mit Grau, nach einer getönten Fläche mit Weiß.
    zuletzt_neutral = GRAU if produkt else HELL
    for index, typ in enumerate(typen):
        vorher = baender[-1] if baender else None
        letzter = index == len(typen) - 1
        if index == 0 and typ == "hero":
            band = GRAU if ruhig else (produkt or HELL)
        elif vorher and typ in ANGEHAENGT:
            band = vorher
        elif typ == "gradient_cta" and letzter:
            band = TINTE
        elif typ == "gradient_cta":
            band = produkt or MARKE
        elif ruhig:
            band = HELL
        else:
            band = HELL if zuletzt_neutral == GRAU else GRAU
            if band == vorher:
                band = GRAU if band == HELL else HELL
            zuletzt_neutral = band
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
    page = context.get("page")
    produkt = PRODUKT_JE_SEITE.get(getattr(page, "slug", ""))
    return _abschnitte(eintraege, band_folge(typen, produkt=produkt, ruhig=ruhig))


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
    """Screenshot eines Produkts (nur, wo ein echter vorliegt) mit fertiger ``src``."""
    bild = (PRODUKTE.get(key) or {}).get("bild")
    if not bild:
        return None
    return {**bild, "url": static(bild["src"])}


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
