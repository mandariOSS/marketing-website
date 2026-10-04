"""
Bausteine der Abschnittsmuster für die Seeds (Musterkatalog, marketing/blocks.py).

Jede Funktion liefert ein ``(typ, wert)``-Paar in derselben Form wie die übrigen Seed-Helfer in
``migrate_pages_to_streamfield``. Rich Text wird als HTML übergeben.
"""

from __future__ import annotations


def kopf(title="", subline="", anchor=""):
    return {"badge_text": "", "badge_icon": "", "badge_color": "primary", "title": title,
            "subline": subline, "align": "left", "anchor_id": anchor}


def _p(text):
    """Text ohne eigenes Absatz-Tag in einen Absatz setzen."""
    if not text:
        return ""
    return text if text.lstrip().startswith("<") else f"<p>{text}</p>"


# ── M1 ──────────────────────────────────────────────────────────────────────

def marke(tag, frist, notiz="", *, strecke="1", offen=False):
    return {"tag": tag, "strecke": strecke, "frist": frist, "notiz": notiz, "offen": offen}


def skalenpunkt(tag, label, strecke="1"):
    return {"tag": tag, "strecke": strecke, "label": label}


def schritt(frist, titel, text, *, zusatz="", details=None):
    return {"frist": frist, "frist_zusatz": zusatz, "titel": titel, "text": text,
            "details": [{"begriff": b, "wert": w} for b, w in (details or [])]}


def zeitskala(title, *, subline="", anchor="", tage=30, zweite="", tage2=None, marken, schritte, balken=None,
              balken_titel="", fenster="", skala=None, note=""):
    return ("zeitskala", {
        "header": kopf(title, subline, anchor), "strecke1_tage": tage, "strecke2_label": zweite,
        "strecke2_tage": tage2, "marken": marken, "balken_titel": balken_titel,
        "balken": [{"label": l, "wert": w, "tage": t} for l, w, t in (balken or [])],
        "fenster": fenster, "skala": skala or [], "schritte": schritte, "note": note,
    })


def dauerbalken(title, zeilen, *, subline="", anchor="", gesamt=14, teilung=2, einheit="Wochen",
                meilenstein="Umstellung"):
    return ("dauerbalken", {
        "header": kopf(title, subline, anchor), "einheit": einheit, "gesamt": gesamt, "teilung": teilung,
        "zeilen": zeilen, "legende_meilenstein": meilenstein,
    })


def dauer(titel, dauer_text, text="", *, von=0, bis=0, meilenstein=False):
    return {"titel": titel, "dauer": dauer_text, "text": text, "art": "meilenstein" if meilenstein else "balken",
            "dauer_min": von, "dauer_max": bis}


def quartalsachse(title, punkte, *, subline="", anchor="", note=""):
    return ("quartalsachse", {"header": kopf(title, subline, anchor), "punkte": punkte, "note": note})


def zeitpunkt(zeit, *eintraege, satz=""):
    return {"zeitpunkt": zeit, "satz": satz, "eintraege": list(eintraege)}


def vorhaben(titel, *, produkt="", status="", text="", link_label="", link_url=""):
    return {"titel": titel, "produkt": produkt, "status": status, "text": text,
            "link_label": link_label, "link_url": link_url}


# ── M2 ──────────────────────────────────────────────────────────────────────

def schrittfolge(title, schritte, *, subline="", anchor="", ergebnis=None, note=""):
    ergebnis = ergebnis or {}
    return ("schrittfolge", {
        "header": kopf(title, subline, anchor),
        "schritte": [{"titel": t, "text": x, "notiz": n} for t, x, n in schritte],
        "ergebnis_titel": ergebnis.get("titel", ""), "ergebnis_text": ergebnis.get("text", ""),
        "ergebnis_link_label": ergebnis.get("link_label", ""), "ergebnis_link_url": ergebnis.get("link_url", ""),
        "note": note,
    })


# ── M3 ──────────────────────────────────────────────────────────────────────

def zeile(titel, text="", *, url="", ort="", zusatz="", stand="", status="text"):
    return {"titel": titel, "url": url, "ort": ort, "text": _p(text), "zusatz": _p(zusatz), "stand": stand,
            "status": status}


def gruppe(titel, *zeilen, summe_label="", summe=""):
    return {"titel": titel, "zeilen": list(zeilen), "summe_label": summe_label, "summe": summe}


def register(title, gruppen, *, spalten, subline="", anchor="", kopfart="rand", bestand="", stand="", note=""):
    return ("register", {
        "header": kopf(title, subline, anchor), "kopf": kopfart, "spalten": list(spalten),
        "gruppen": list(gruppen), "bestand_satz": bestand, "stand": stand, "note": note,
    })


# ── M5 ──────────────────────────────────────────────────────────────────────

def rand_ablauf(titel, *schritte):
    return {"type": "ablauf", "value": {"titel": titel,
                                        "schritte": [{"marke": m, "text": t} for m, t in schritte]}}


def rand_links(titel, *links):
    return {"type": "links", "value": {"titel": titel, "links": [{"label": l, "url": u} for l, u in links]}}


def rand_fakten(titel, *fakten):
    return {"type": "fakten", "value": {"titel": titel,
                                        "fakten": [{"begriff": b, "wert": w} for b, w in fakten]}}


def rand_text(html):
    return {"type": "text", "value": html}


def randspalte(title, body, rand, *, subline="", anchor=""):
    return ("randspalte", {"header": kopf(title, subline, anchor), "body": body, "rand": list(rand)})


def begriff(name, text, *, marke="", link_label="", link_url="", anchor=""):
    return {"begriff": name, "marke": marke, "text": _p(text), "link_label": link_label, "link_url": link_url,
            "anchor_id": anchor}


def begriffe(title, eintraege, *, subline="", anchor="", note=""):
    return ("begriffe", {"header": kopf(title, subline, anchor), "eintraege": list(eintraege), "note": note})


def einladung(title, subline, cta_label, cta_url, *, wege=None, link_label="", link_url=""):
    ctas = [{"label": cta_label, "url": cta_url, "icon": "", "style": "primary"}]
    if link_label:
        ctas.append({"label": link_label, "url": link_url, "icon": "", "style": "outline"})
    return ("gradient_cta", {
        "title": title, "subline": subline, "ctas": ctas, "gradient_from": "primary",
        "wege": [{"label": l, "wert": w, "url": u} for l, w, u in (wege or [])],
    })


# ── M6 ──────────────────────────────────────────────────────────────────────

def zusage(aussage, *, grundlage="", bedingungen_titel="", bedingungen=None, geltung="", neben=None, anchor=""):
    return ("zusage", {
        "aussage": aussage, "grundlage": _p(grundlage), "bedingungen_titel": bedingungen_titel,
        "bedingungen": list(bedingungen or []), "geltung": _p(geltung),
        "neben": [{"stichwort": s, "text": t} for s, t in (neben or [])], "anchor_id": anchor,
    })


def leitsatz(satz, text, *, links=None, anchor=""):
    return ("leitsatz", {"satz": satz, "text": text, "anchor_id": anchor,
                         "links": [{"label": l, "url": u} for l, u in (links or [])]})


# ── M7–M10 ──────────────────────────────────────────────────────────────────

def produktbild(produkt, titel, text, *, fakten=None, link_label="", link_url="", anchor=""):
    return {"produkt": produkt, "titel": titel, "text": text, "link_label": link_label, "link_url": link_url,
            "fakten": [{"begriff": b, "wert": w} for b, w in (fakten or [])], "anchor_id": anchor}


def produktbilder(title, eintraege, *, subline="", anchor="", note=""):
    return ("produktbilder", {"header": kopf(title, subline, anchor), "eintraege": list(eintraege), "note": note})


def vergleich(title, optionen, kriterien, *, subline="", anchor="", note=""):
    return ("vergleich", {
        "header": kopf(title, subline, anchor),
        "optionen": [{"name": n, "satz": s} for n, s in optionen],
        "kriterien": [{"kriterium": k, "werte": [_p(w) for w in werte]} for k, werte in kriterien],
        "note": note,
    })


def zahlensatz(titel, satz, *, rand="", anchor=""):
    return ("zahlensatz", {"titel": titel, "satz": _p(satz), "rand": rand, "anchor_id": anchor})


def nullen(titel, summen, gruppen, *, text="", spalten=("Art", "Was dazu zählt", "Anzahl"), anchor=""):
    return ("nullen", {
        "summen": [{"begriff": b, "wert": w} for b, w in summen], "titel": titel, "text": _p(text),
        "spalten": list(spalten), "anchor_id": anchor,
        "gruppen": [{"titel": g, "zeilen": [{"art": a, "was": w, "wert": z} for a, w, z in zeilen]}
                    for g, zeilen in gruppen],
    })


def downloads(title, label, url, *, subline="", hinweis="", anchor="", dateien=None):
    return ("downloads", {"header": kopf(title, subline, anchor), "label": label, "url": url, "hinweis": hinweis,
                          "dateien": [{"label": l, "url": u} for l, u in (dateien or [])]})


def begriffe_aus_html(title, html, *, subline="", anchor=""):
    """Rich Text mit h3-Zwischenüberschriften als Begriffe (Überschrift links, Inhalt rechts)."""
    import re

    teile = re.split(r"<h3>(.*?)</h3>", html)
    eintraege = [begriff(teile[i], teile[i + 1].strip()) for i in range(1, len(teile) - 1, 2)]
    return begriffe(title, eintraege, subline=subline, anchor=anchor)
