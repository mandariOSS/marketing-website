"""
Rechenhilfen der Abschnittsmuster (Musterkatalog, templates/marketing/muster/).

Die Muster bekommen ihre Daten als StreamField-Wert (StructValue) oder als einfaches dict aus einem
festen Template (Disclosure, Startseite); beide werden hier gleich gelesen (``_get``). Die Tags rechnen
nur Geometrie und Zählungen, keine Texte: Wo eine Marke auf der Zeitachse steht, wie lang ein
Dauerbalken ist, wie viele Unterlagen eines Registers vorliegen.
"""

from __future__ import annotations

import re

from django import template
from django.templatetags.static import static
from django.utils.html import format_html, format_html_join
from django.utils.safestring import mark_safe

register = template.Library()


def _get(obj, key, default=None):
    if obj is None:
        return default
    try:
        value = obj.get(key, default)
    except AttributeError:
        value = getattr(obj, key, default)
    return default if value is None else value


def _zahl(value, default=0.0):
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _prozent(value):
    return f"{value:.3f}".rstrip("0").rstrip(".") + "%"


# ── M1a Zeitskala ────────────────────────────────────────────────────────────
# Strecke 1 ist linear in Tagen. Gibt es eine zweite Strecke (nach einem Ereignis mit offenem Zeitpunkt,
# z. B. „Fix“), endet Strecke 1 bei 61 %, der Achsenbruch steht bei 62,5 %, Strecke 2 läuft von 64 bis 100 %.
STRECKE1_ALLEIN = 100.0
STRECKE1_ENDE = 61.0
BRUCH = 62.5
STRECKE2_ANFANG = 64.0
RASTER_PX = 1216  # Inhaltsbreite bei 1440 px (max-w-7xl abzüglich Rand)
HOEHE_STUFE_REM = 4.5
HOEHE_BASIS_REM = 4.75


def _breite_prozent(frist, notiz):
    """Geschätzte Breite einer Marke (Frist 28 px halbfett, Notiz 14 px, höchstens 12 rem) in % der Achse."""
    frist_px = len(frist or "") * 15.6
    notiz_px = min(len(notiz or "") * 7.3, 180)
    return (max(frist_px, notiz_px) + 14) / RASTER_PX * 100


def _ende(marke):
    return marke["pos"] if marke["rechts"] else marke["pos"] + marke["breite"]


def zeitskala_plan(value):
    """Lage aller Marken, Balken und Skalenpunkte einer Zeitskala (M1a).

    Marken, deren Beschriftung über die nächste Leitlinie reichen würde, stehen treppenförmig tiefer
    (frühere Marke höher, höchstens vier Höhen), damit keine Leitlinie durch einen Text läuft. Eine Marke
    am rechten Ende steht links von ihrer Linie.
    """
    t1 = _zahl(_get(value, "strecke1_tage"), 30.0) or 30.0
    zweite = bool(_get(value, "strecke2_label"))
    marken_roh = list(_get(value, "marken", []) or [])
    t2 = _zahl(_get(value, "strecke2_tage"), 0.0)
    if zweite and not t2:
        t2 = max([_zahl(_get(m, "tag")) for m in marken_roh if str(_get(m, "strecke", "1")) == "2"] or [1.0]) or 1.0
    ende1 = STRECKE1_ENDE if zweite else STRECKE1_ALLEIN

    def lage(tag, strecke):
        if zweite and str(strecke) == "2":
            return STRECKE2_ANFANG + min(_zahl(tag) / t2, 1.0) * (100.0 - STRECKE2_ANFANG)
        return min(_zahl(tag) / t1, 1.0) * ende1

    marken = []
    for roh in marken_roh:
        frist, notiz = _get(roh, "frist", ""), _get(roh, "notiz", "")
        pos = lage(_get(roh, "tag", 0), _get(roh, "strecke", "1"))
        breite = _breite_prozent(frist, notiz)
        marken.append({"frist": frist, "notiz": notiz, "pos": pos, "breite": breite,
                       "offen": bool(_get(roh, "offen", False)), "rechts": pos + breite > 100.5})
    marken.sort(key=lambda m: m["pos"])
    for i, marke in enumerate(marken):
        frueher = marken[:i]
        if marke["rechts"]:
            # Beschriftung links der Linie: frühere Linien darunter müssen kürzer sein, die Marke steht höher
            links = marke["pos"] - marke["breite"] - 0.4
            treffer = [m["stufe"] for m in frueher if m["pos"] >= links or _ende(m) > links]
            marke["stufe"] = max(1, min(treffer) - 1) if treffer else 1
        else:
            # Beschriftung rechts der Linie: reicht eine frühere Beschriftung bis hierher, steht diese Marke tiefer
            treffer = [m["stufe"] for m in frueher if _ende(m) > marke["pos"] - 0.4]
            marke["stufe"] = min(max(treffer) + 1, 4) if treffer else 1
    hoechste = max([m["stufe"] for m in marken] or [1])
    for marke in marken:
        marke["hoehe"] = f"{HOEHE_BASIS_REM + (hoechste - marke['stufe']) * HOEHE_STUFE_REM:g}rem"
        marke["links"] = _prozent(marke["pos"])

    balken = []
    for i, roh in enumerate(_get(value, "balken", []) or []):
        balken.append({"label": _get(roh, "label", ""), "wert": _get(roh, "wert", ""),
                       "breite": _prozent(lage(_get(roh, "tage", 0), "1")), "oben": f"{1.6 + i * 2.3:g}rem"})
    skala = []
    for roh in _get(value, "skala", []) or []:
        pos = lage(_get(roh, "tag", 0), _get(roh, "strecke", "1"))
        skala.append({"label": _get(roh, "label", ""), "links": _prozent(pos),
                      "klasse": "zk-l" if pos < 0.5 else ("zk-r" if pos > 99.5 else "")})
    return {
        "marken": marken,
        "hoehe": f"{HOEHE_BASIS_REM + (hoechste - 1) * HOEHE_STUFE_REM:g}rem",
        "zweite": zweite,
        "seg1": _prozent(ende1),
        "bruch": _prozent(BRUCH),
        "seg2_links": _prozent(STRECKE2_ANFANG - 0.5),
        "seg2_breite": _prozent(100.0 - STRECKE2_ANFANG + 0.5),
        "fenster_links": _prozent(STRECKE2_ANFANG),
        "balken": balken,
        "spuren_hoehe": f"{max(1.6 + len(balken) * 2.3 + 0.4, 6.5 if _get(value, 'fenster') else 0):g}rem",
    }


register.simple_tag(zeitskala_plan)


# ── M1b Dauerbalken ──────────────────────────────────────────────────────────


def dauer_plan(value):
    """Balken aufeinanderfolgender Schritte: frühestmöglich (Summe der Mindestdauern) und spätestens
    (Summe der Höchstdauern). Ein Meilenstein steht frühestens/spätestens am Ende der Schritte davor."""
    gesamt = _zahl(_get(value, "gesamt"), 14.0) or 14.0
    teilung = _zahl(_get(value, "teilung"), 2.0) or 2.0
    einheit = _get(value, "einheit", "Wochen")
    frueh = spaet = 0.0
    zeilen = []
    for nr, roh in enumerate(_get(value, "zeilen", []) or [], start=1):
        dmin, dmax = _zahl(_get(roh, "dauer_min")), _zahl(_get(roh, "dauer_max"))
        art = _get(roh, "art", "balken")
        zeile = {"nr": nr, "titel": _get(roh, "titel", ""), "dauer": _get(roh, "dauer", ""),
                 "text": _get(roh, "text", ""), "art": art}
        if art == "meilenstein":
            zeile.update(frueh=_prozent(frueh / gesamt * 100), spaet=_prozent(spaet / gesamt * 100),
                         linie=_prozent((spaet - frueh) / gesamt * 100))
        else:
            zeile.update(start=_prozent(frueh / gesamt * 100), frueh_breite=_prozent(dmin / gesamt * 100),
                         spiel_start=_prozent((frueh + dmin) / gesamt * 100),
                         spiel_breite=_prozent(max(spaet + dmax - frueh - dmin, 0) / gesamt * 100))
            frueh, spaet = frueh + dmin, spaet + dmax
        zeilen.append(zeile)
    skala = []
    schritte = int(gesamt // teilung)
    for i in range(schritte + 1):
        wert = i * teilung
        label = f"{wert:g}" + (f" {einheit}" if i == schritte else "")
        skala.append({"label": label, "links": _prozent(wert / gesamt * 100)})
    return {"zeilen": zeilen, "skala": skala, "raster": _prozent(teilung / gesamt * 100)}


register.simple_tag(dauer_plan)


# ── M3 Register ──────────────────────────────────────────────────────────────


def register_plan(value):
    """Spalten und Bestand eines Registers: ``spalten`` (Überschriften), ``vierte`` (gibt es eine
    Zusatzspalte), ``da``/``offen``/``gesamt`` und die Segmente der Bestandsleiste."""
    spalten = [s for s in (_get(value, "spalten", []) or []) if s]
    da = offen = 0
    segmente = []
    for gruppe in _get(value, "gruppen", []) or []:
        for zeile in _get(gruppe, "zeilen", []) or []:
            status = _get(zeile, "status", "text")
            if status == "da":
                da += 1
                segmente.append(True)
            elif status == "offen":
                offen += 1
                segmente.append(False)
    segmente.sort(key=lambda s: not s)
    satz = _get(value, "bestand_satz", "") or ""
    if satz:
        satz = satz.format(da=da, offen=offen, gesamt=da + offen)
    return {"spalten": spalten, "vierte": len(spalten) >= 4, "drei": len(spalten) >= 3, "da": da,
            "offen": offen, "gesamt": da + offen, "segmente": segmente, "satz": satz}


register.simple_tag(register_plan)


# ── M4 Dokumentseite ─────────────────────────────────────────────────────────

_UEBERSCHRIFT = re.compile(r"<h2(?P<attrs>[^>]*)>(?P<text>.*?)</h2>", re.S)
_ID = re.compile(r'\sid="([^"]+)"')


def anker_aus(text):
    """Sprungmarke aus einer Überschrift: „1. Gegenstand und Dauer“ → ``gegenstand-und-dauer``."""
    text = re.sub(r"<[^>]+>", "", text)
    text = re.sub(r"^\s*\d+(\.\d+)*\.?\s*", "", text).lower()
    for alt, neu in (("ä", "ae"), ("ö", "oe"), ("ü", "ue"), ("ß", "ss")):
        text = text.replace(alt, neu)
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return "-".join(text.split("-")[:5]) or "abschnitt"


@register.simple_tag
def dokument_gliederung(html):
    """Rechtstext mit Sprungmarken an jeder h2 und das Inhaltsverzeichnis dazu.

    ``{% dokument_gliederung page.body|richtext as dok %}`` → ``dok.html`` (Text mit ids), ``dok.inhalt``
    (Liste aus ``anker`` und ``titel``). Vorhandene ids bleiben, doppelte Marken werden durchnummeriert.
    """
    text = str(html.__html__() if hasattr(html, "__html__") else html or "")
    inhalt, vergeben = [], set()

    def ersetzen(treffer):
        attrs, titel = treffer.group("attrs"), treffer.group("text")
        vorhanden = _ID.search(attrs)
        anker = vorhanden.group(1) if vorhanden else anker_aus(titel)
        basis, n = anker, 2
        while anker in vergeben:
            anker, n = f"{basis}-{n}", n + 1
        vergeben.add(anker)
        inhalt.append({"anker": anker, "titel": re.sub(r"<[^>]+>", "", titel).strip()})
        if vorhanden:
            return treffer.group(0)
        return f'<h2{attrs} id="{anker}">{titel}</h2>'

    neu = _UEBERSCHRIFT.sub(ersetzen, text)
    return {"html": mark_safe(neu), "inhalt": inhalt}  # noqa: S308 – Eingabe ist gerenderter Rich Text


_STAND = re.compile(r"Stand:?\s*(?:</?strong>\s*)*([0-9]{1,2}\.\s*[A-Za-zä]+\s+20\d\d|[A-Za-zä]+\s+20\d\d)")


@register.simple_tag
def dokument_stand(html):
    """„Stand: Juli 2026“ aus einem Rechtstext lesen (sonst leer)."""
    treffer = _STAND.search(str(html or ""))
    return treffer.group(1) if treffer else ""


# ── M7 Produktbild ───────────────────────────────────────────────────────────


@register.simple_tag
def produkt_ausschnitt(key):
    """Bildschirm eines Produkts für den angeschnittenen Ausschnitt (groß für Desktop, klein fürs Handy)."""
    from .baender import PRODUKTE

    bild = (PRODUKTE.get(key) or {}).get("bild")
    if not bild:
        return None
    return {"url": static(bild["src_gross"]), "url_klein": static(bild["src"]), "alt": bild["alt"]}


# ── Kleinkram ────────────────────────────────────────────────────────────────


@register.filter
def zeilen(text):
    """Mehrzeiligen Text mit Zeilenumbrüchen ausgeben (Leitsatz in zwei Zeilen)."""
    teile = [t.strip() for t in str(text or "").splitlines() if t.strip()]
    return format_html_join(mark_safe("<br>"), "{}", ((t,) for t in teile))


@register.simple_tag
def wert_oder(*werte):
    """Erster nicht leerer Wert."""
    for wert in werte:
        if wert:
            return wert
    return ""


@register.filter
def kontaktwert(wert):
    """E-Mail-Adresse als mailto-Link, sonst Text."""
    wert = str(wert or "")
    if re.fullmatch(r"[^@\s]+@[^@\s]+\.[a-z]{2,}", wert):
        return format_html('<a class="textlink" href="mailto:{}">{}</a>', wert, wert)
    return wert


# ── Daten fester Seiten (marketing/muster_daten.py) ──────────────────────────


@register.simple_tag
def einladung_wege(wege=None, seite=""):
    """Wege rechts im Einladungsband: die des Blocks, sonst die der Seite, sonst E-Mail und Gesprächsform."""
    from marketing import muster_daten

    eigene = [w for w in (wege or []) if _get(w, "wert")]
    if eigene:
        return eigene
    return muster_daten.WEGE.get(seite) or muster_daten.STANDARD_WEGE


@register.simple_tag
def muster_daten(name):
    from marketing import muster_daten as daten

    return daten.DATEN[name]


@register.simple_tag
def dokument_rand(slug):
    from marketing import muster_daten

    return muster_daten.DOKUMENTE.get(slug, {"kontakt": "hello@mandari.de", "verweise": []})


# ── M4: Aufbau einer Dokumentseite aus Rechtstext oder Blöcken ───────────────

DOKUMENT_ABSCHNITT = {"richtext_section", "numbered_article"}
DOKUMENT_DANACH = {"gradient_cta"}


@register.simple_tag(takes_context=True)
def dokument_aufbau(context, page=None):
    """Alles, was die Dokumentseite (templates/marketing/dokument.html) braucht.

    Rechtstexte (LegalPage.body): Text mit Sprungmarken je h2. Seiten aus Blöcken (Quellen, Trust Center):
    der Hero wird Kopf, Fließtext-Abschnitte und nummerierte Artikel werden Abschnitte mit Sprungmarke,
    Tabellen und Kennzahlen (register, zahlensatz) hängen am Abschnitt davor, Eckdaten (trust_banner)
    gehen in die Randspalte, Hinweise (disclaimer_box) stehen leise unter dem Abschnitt, die Einladung
    folgt nach dem Dokument.
    """
    page = page or context.get("page")
    rand = dict(dokument_rand(getattr(page, "slug", "")))
    aufbau = {"titel": page.title, "satz": "", "html": "", "inhalt": [], "abschnitte": [], "danach": [],
              "eckdaten": [], "rand": rand, "stand": "", "ctas": []}
    stream = getattr(page, "body_stream", None) or (getattr(page, "body", None) if not hasattr(page, "body_stream") else None)
    if hasattr(page, "body_stream") and not page.body_stream:
        # Rechtstext als Rich Text
        from wagtail.rich_text import expand_db_html

        html = expand_db_html(page.body or "")
        gliederung = dokument_gliederung(html)
        aufbau.update(html=gliederung["html"], inhalt=gliederung["inhalt"], stand=dokument_stand(html))
        return aufbau

    vergeben = set()
    for block in stream or []:
        typ, wert = block.block_type, block.value
        if typ == "hero":
            from marketing.blocks import hero_title

            aufbau["titel"] = hero_title(wert.get("title"), wert.get("title_highlight"))
            aufbau["satz"] = wert.get("subline") or ""
            aufbau["ctas"] = list(wert.get("ctas") or [])[:2]
        elif typ in DOKUMENT_ABSCHNITT:
            if typ == "numbered_article":
                titel, anker = wert.get("title"), wert.get("anchor") or anker_aus(wert.get("title"))
                body = wert.get("body")
            else:
                kopf = wert.get("header") or {}
                titel = kopf.get("title") or ""
                anker = kopf.get("anchor_id") or anker_aus(titel)
                body = wert.get("body")
            basis, n = anker, 2
            while anker in vergeben:
                anker, n = f"{basis}-{n}", n + 1
            vergeben.add(anker)
            aufbau["abschnitte"].append({"titel": titel, "anker": anker, "body": body, "vorne": [], "bloecke": [],
                                         "hinweise": []})
            if titel:
                aufbau["inhalt"].append({"anker": anker, "titel": titel})
        elif typ == "trust_banner":
            aufbau["eckdaten"] += [{"begriff": i.get("label_bold"), "wert": i.get("label_normal")}
                                   for i in wert.get("items") or []]
        elif typ == "disclaimer_box":
            ziel = aufbau["abschnitte"][-1]["hinweise"] if aufbau["abschnitte"] else aufbau["danach"]
            ziel.append(wert.get("body"))
            if not aufbau["stand"]:
                aufbau["stand"] = dokument_stand(str(wert.get("body") or ""))
        elif typ in DOKUMENT_DANACH:
            aufbau["danach"].append(block)
        elif typ == "mandari_cards":
            continue  # Themenübersicht: ersetzt durch die Inhaltsleiste
        elif aufbau["abschnitte"]:
            # Kennzahl im Satz vor dem Text des Abschnitts (sie fasst ihn zusammen), Tabellen danach
            aufbau["abschnitte"][-1]["vorne" if typ == "zahlensatz" else "bloecke"].append(block)
        else:
            aufbau["danach"].append(block)
    return aufbau
