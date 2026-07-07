#!/usr/bin/env python
"""Erzeugt die mandari-Brand-Assets (Wortmarke + Favicon) reproduzierbar.

Wortmarke: "mandari" in Inter Bold (tracking-tight ~ -0.025em) + Punkt "."
in Indigo — exakt wie die Text-Wortmarke in templates/components/navbar.html.

Erzeugt nach static/brand/:
  mandari-logo.svg          dunkle Variante  (Text #111827, Punkt #4F46E5)
  mandari-logo-white.svg    weisse Variante  (Text #FFFFFF, Punkt #818CF8)
  mandari-logo.png          2400px breit, transparent, dunkle Variante
  mandari-logo-white.png    2400px breit, transparent, weisse Variante
  mandari-logo-print.png    1200px breit, WEISSER Hintergrund (lexoffice-Briefpapier)
  favicon.svg               "m" + Indigo-Punkt, quadratische viewBox
  favicon-32.png / favicon-192.png / favicon-512.png   transparent
  apple-touch-icon.png      180px, weisser Hintergrund

Abhängigkeiten: fonttools, pillow, requests
Usage:  py scripts/generate_logo.py
"""

from __future__ import annotations

import io
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import requests
from fontTools.misc.transform import Transform
from fontTools.pens.boundsPen import BoundsPen
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from PIL import Image, ImageDraw, ImageFont

REPO_ROOT = Path(__file__).resolve().parent.parent
BRAND_DIR = REPO_ROOT / "static" / "brand"
CACHE_DIR = Path(__file__).resolve().parent / ".cache"
TTF_PATH = CACHE_DIR / "Inter-Bold-static.ttf"

# Markenfarben (Tailwind-Palette der Website)
GRAY_900 = "#111827"   # Text dunkel
WHITE = "#FFFFFF"      # Text auf dunklem Grund
PRIMARY_600 = "#4F46E5"  # Punkt (hell / Print / Favicon) — Indigo
PRIMARY_400 = "#818CF8"  # Punkt in der weissen (Darkmode-)Variante

TRACKING_EM = -0.025   # tracking-tight

FONT_SOURCES = [
    # Google Fonts: Inter Variable (opsz, wght) — klein & stabil erreichbar
    "https://github.com/google/fonts/raw/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
    # Fallback: rsms-Release-Mirror der Variable-TTF
    "https://raw.githubusercontent.com/google/fonts/main/ofl/inter/Inter%5Bopsz%2Cwght%5D.ttf",
]


def fetch_inter_bold() -> Path:
    """Lädt Inter herunter und instanziert eine statische Bold-TTF (wght=700)."""
    if TTF_PATH.exists():
        return TTF_PATH
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    last_err: Exception | None = None
    for url in FONT_SOURCES:
        try:
            print(f"  Lade Inter von {url} ...")
            resp = requests.get(url, timeout=120)
            resp.raise_for_status()
            font = TTFont(io.BytesIO(resp.content))
            if "fvar" in font:
                axes = {"wght": 700}
                if any(a.axisTag == "opsz" for a in font["fvar"].axes):
                    axes["opsz"] = 14  # Inter-Default (Text-Schnitt)
                instantiateVariableFont(font, axes, inplace=True)
            font.save(TTF_PATH)
            return TTF_PATH
        except Exception as exc:  # noqa: BLE001 — nächste Quelle probieren
            last_err = exc
            print(f"    fehlgeschlagen: {exc}")
    raise RuntimeError(f"Inter-Download fehlgeschlagen: {last_err}")


# ────────────────────────── SVG-Erzeugung ──────────────────────────


class Wordmark:
    """Layout der Glyphen von `text` in Font-Units, y-Achse bereits SVG-konform."""

    def __init__(self, font: TTFont, text: str):
        self.font = font
        self.upem = font["head"].unitsPerEm
        self.glyph_set = font.getGlyphSet()
        self.cmap = font.getBestCmap()
        tracking = TRACKING_EM * self.upem
        self.glyphs: list[tuple[str, float]] = []  # (glyph_name, x_offset)
        x = 0.0
        for ch in text:
            gname = self.cmap[ord(ch)]
            self.glyphs.append((gname, x))
            x += self.glyph_set[gname].width + tracking

    def glyph_path(self, gname: str, x: float) -> str:
        """SVG-Pfad (d-Attribut) der Glyphe, y-gespiegelt, an x positioniert."""
        pen = SVGPathPen(self.glyph_set)
        tpen = TransformPen(pen, Transform(1, 0, 0, -1, x, 0))
        self.glyph_set[gname].draw(tpen)
        return pen.getCommands()

    def path_d(self, indices: list[int]) -> str:
        return " ".join(self.glyph_path(*self.glyphs[i]) for i in indices)

    def ink_bounds(self, indices: list[int]) -> tuple[float, float, float, float]:
        """(xmin, ymin, xmax, ymax) in SVG-Koordinaten (y nach unten)."""
        xmin = ymin = float("inf")
        xmax = ymax = float("-inf")
        for i in indices:
            gname, x = self.glyphs[i]
            bp = BoundsPen(self.glyph_set)
            self.glyph_set[gname].draw(bp)
            if bp.bounds is None:
                continue
            gx0, gy0, gx1, gy1 = bp.bounds
            xmin = min(xmin, gx0 + x)
            xmax = max(xmax, gx1 + x)
            # y-Spiegelung: SVG-y = -font-y
            ymin = min(ymin, -gy1)
            ymax = max(ymax, -gy0)
        return xmin, ymin, xmax, ymax


def build_svg(wm: Wordmark, text_color: str, dot_color: str,
              text_idx: list[int], dot_idx: list[int],
              square: bool = False, pad_ratio: float = 0.06) -> str:
    all_idx = text_idx + dot_idx
    xmin, ymin, xmax, ymax = wm.ink_bounds(all_idx)
    w, h = xmax - xmin, ymax - ymin
    pad = max(w, h) * pad_ratio
    if square:
        # Quadratische viewBox, Inhalt zentriert, Glyphe füllt ~80 %
        side = max(w, h) / 0.80
        vx = xmin - (side - w) / 2
        vy = ymin - (side - h) / 2
        viewbox = (vx, vy, side, side)
    else:
        viewbox = (xmin - pad, ymin - pad, w + 2 * pad, h + 2 * pad)

    def fmt(v: float) -> str:
        return f"{v:.1f}".rstrip("0").rstrip(".")

    vb = " ".join(fmt(v) for v in viewbox)
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{vb}" '
        f'width="{fmt(viewbox[2])}" height="{fmt(viewbox[3])}" role="img" '
        f'aria-label="mandari.">',
    ]
    text_d = wm.path_d(text_idx)
    dot_d = wm.path_d(dot_idx)
    if text_d.strip():
        parts.append(f'  <path fill="{text_color}" d="{text_d}"/>')
    parts.append(f'  <path fill="{dot_color}" d="{dot_d}"/>')
    parts.append("</svg>")
    return "\n".join(parts)


# ────────────────────────── PNG-Erzeugung (Pillow) ──────────────────────────


def render_wordmark_png(ttf: Path, text_color: str, dot_color: str,
                        target_width: int, bg: str | None,
                        pad_ratio: float = 0.06) -> Image.Image:
    """Rendert "mandari" + "." char-weise mit Tracking, croppt auf Ink-Bounds."""
    fsize = 1000
    font = ImageFont.truetype(str(ttf), fsize)
    tracking = TRACKING_EM * fsize
    chars = [(c, text_color) for c in "mandari"] + [(".", dot_color)]

    canvas_w, canvas_h = fsize * 10, fsize * 3
    img = Image.new("RGBA", (canvas_w, canvas_h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x, y = fsize, fsize  # grosszügiger Rand
    for ch, color in chars:
        draw.text((x, y), ch, font=font, fill=color)
        x += font.getlength(ch) + tracking

    bbox = img.getbbox()  # Ink-Bounds über Alpha
    if bbox is None:
        raise RuntimeError("PNG-Rendering leer")
    img = img.crop(bbox)
    pad = int(max(img.size) * pad_ratio)
    padded = Image.new("RGBA", (img.width + 2 * pad, img.height + 2 * pad), (0, 0, 0, 0))
    padded.paste(img, (pad, pad), img)
    scale = target_width / padded.width
    out = padded.resize((target_width, max(1, round(padded.height * scale))),
                        Image.LANCZOS)
    if bg:
        out = Image.alpha_composite(Image.new("RGBA", out.size, bg), out)
    return out


def render_favicon_png(ttf: Path, size: int, bg: str | None) -> Image.Image:
    """Rendert "m." quadratisch (Glyphe ~80 % der Kantenlänge)."""
    fsize = 1000
    font = ImageFont.truetype(str(ttf), fsize)
    tracking = TRACKING_EM * fsize
    img = Image.new("RGBA", (fsize * 4, fsize * 3), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    x, y = fsize, fsize
    for ch, color in [("m", GRAY_900), (".", PRIMARY_600)]:
        draw.text((x, y), ch, font=font, fill=color)
        x += font.getlength(ch) + tracking
    bbox = img.getbbox()
    img = img.crop(bbox)
    side = int(max(img.size) / 0.80)
    square = Image.new("RGBA", (side, side), (0, 0, 0, 0))
    square.paste(img, ((side - img.width) // 2, (side - img.height) // 2), img)
    out = square.resize((size, size), Image.LANCZOS)
    if bg:
        out = Image.alpha_composite(Image.new("RGBA", out.size, bg), out)
    return out


# ────────────────────────── Verifikation ──────────────────────────


def verify_svg(path: Path) -> str:
    tree = ET.parse(path)  # wirft bei nicht wohlgeformtem XML
    root = tree.getroot()
    ns = {"svg": "http://www.w3.org/2000/svg"}
    paths = root.findall("svg:path", ns)
    assert paths, f"{path.name}: keine <path>-Elemente"
    for p in paths:
        assert p.get("d", "").strip(), f"{path.name}: leerer Pfad"
    assert root.get("viewBox"), f"{path.name}: keine viewBox"
    return root.get("viewBox")


def verify_png(path: Path, expect_w: int | None = None,
               expect_square: bool = False, expect_alpha: bool | None = None) -> str:
    with Image.open(path) as im:
        im.load()
        assert im.mode == "RGBA", f"{path.name}: mode {im.mode} != RGBA"
        if expect_w:
            assert im.width == expect_w, f"{path.name}: width {im.width} != {expect_w}"
        if expect_square:
            assert im.width == im.height, f"{path.name}: nicht quadratisch {im.size}"
        alpha_min = im.getchannel("A").getextrema()[0]
        if expect_alpha is True:
            assert alpha_min < 255, f"{path.name}: keine Transparenz vorhanden"
        if expect_alpha is False:
            assert alpha_min == 255, f"{path.name}: unerwartete Transparenz"
        return f"{im.width}x{im.height} {im.mode}"


def main() -> int:
    BRAND_DIR.mkdir(parents=True, exist_ok=True)
    ttf = fetch_inter_bold()
    font = TTFont(str(ttf))

    # ── SVGs: Wortmarke ──
    wm = Wordmark(font, "mandari.")
    text_idx, dot_idx = list(range(7)), [7]
    (BRAND_DIR / "mandari-logo.svg").write_text(
        build_svg(wm, GRAY_900, PRIMARY_600, text_idx, dot_idx), encoding="utf-8")
    (BRAND_DIR / "mandari-logo-white.svg").write_text(
        build_svg(wm, WHITE, PRIMARY_400, text_idx, dot_idx), encoding="utf-8")

    # ── SVG: Favicon "m." ──
    fm = Wordmark(font, "m.")
    (BRAND_DIR / "favicon.svg").write_text(
        build_svg(fm, GRAY_900, PRIMARY_600, [0], [1], square=True), encoding="utf-8")

    # ── PNGs: Wortmarke ──
    render_wordmark_png(ttf, GRAY_900, PRIMARY_600, 2400, None).save(
        BRAND_DIR / "mandari-logo.png")
    render_wordmark_png(ttf, WHITE, PRIMARY_400, 2400, None).save(
        BRAND_DIR / "mandari-logo-white.png")
    render_wordmark_png(ttf, GRAY_900, PRIMARY_600, 1200, WHITE, pad_ratio=0.10).save(
        BRAND_DIR / "mandari-logo-print.png")

    # ── PNGs: Favicon ──
    for size in (32, 192, 512):
        render_favicon_png(ttf, size, None).save(BRAND_DIR / f"favicon-{size}.png")
    render_favicon_png(ttf, 180, WHITE).save(BRAND_DIR / "apple-touch-icon.png")

    # ── Verifikation ──
    print("\nVerifikation:")
    for name in ("mandari-logo.svg", "mandari-logo-white.svg", "favicon.svg"):
        print(f"  {name}: viewBox {verify_svg(BRAND_DIR / name)}")
    print(f"  mandari-logo.png: {verify_png(BRAND_DIR / 'mandari-logo.png', 2400, expect_alpha=True)}")
    print(f"  mandari-logo-white.png: {verify_png(BRAND_DIR / 'mandari-logo-white.png', 2400, expect_alpha=True)}")
    print(f"  mandari-logo-print.png: {verify_png(BRAND_DIR / 'mandari-logo-print.png', 1200, expect_alpha=False)}")
    for size in (32, 192, 512):
        print(f"  favicon-{size}.png: {verify_png(BRAND_DIR / f'favicon-{size}.png', size, True, True)}")
    print(f"  apple-touch-icon.png: {verify_png(BRAND_DIR / 'apple-touch-icon.png', 180, True, False)}")
    print("\nOK — alle Assets erzeugt in", BRAND_DIR)
    return 0


if __name__ == "__main__":
    sys.exit(main())
