#!/usr/bin/env python3
"""Generates every bitmap used by the Berserk watch face.

    pip install pillow numpy
    python3 tools/gen_assets.py                       # uses art/brand.png if present
    python3 tools/gen_assets.py --brand my_brand.png  # any silhouette image

The brand artwork is traced from a reference image: dark strokes on a light
background, or opaque strokes on a transparent background. It is fitted into
the centre of the dial and then styled (glow, scar rim, hot core, blood).
Without a reference image a rough placeholder sigil is drawn instead.

Outputs:
  resources-round-<N>x<N>/drawables/bg_calm.png   brand dormant (day)
  resources-round-<N>x<N>/drawables/bg_bleed.png  brand bleeding (night)
  resources/drawables/icon_*.png                  22px data icons
  resources/drawables/aod_brand.png               thin brand for always-on mode
  resources/drawables/launcher_icon.png
"""
import argparse
import math
import os
import random

import numpy as np
from PIL import Image, ImageChops, ImageDraw, ImageFilter

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SS = 4  # supersampling factor
SIZES = [454, 416, 390, 360, 280, 260]

# ---------------------------------------------------------------------------
# Brand of Sacrifice geometry, in a 454px design space.
# Each stroke: (bezier control points, max width, taper-in, taper-out)
# ---------------------------------------------------------------------------
def _r(x, y):
    """Reference-sketch coords -> 454 design space."""
    return ((x - 286) * 0.98 + 227, (y - 45) * 0.98 + 72)


# Fallback outline of the Brand of Sacrifice, used only when art/brand.png is
# missing: stem with a flame tip, hooked arms crossing into an X that closes
# as a diamond at the bottom.
BRAND = [
    ([_r(286, 70), _r(288, 375)], 20, 0.02, 0.05),                 # stem
    ([_r(286, 45), _r(286, 80)], 16, 0.6, 0.0),                    # flame tip
    ([_r(268, 58), _r(280, 80)], 10, 0.5, 0.0),
    ([_r(304, 58), _r(292, 80)], 10, 0.5, 0.0),
    ([_r(222, 72), _r(206, 95), _r(212, 112)], 20, 0.1, 0.0),       # left hook
    ([_r(212, 108), _r(378, 272)], 22, 0.0, 0.0),                   # left arm -> right corner
    ([_r(378, 268), _r(288, 375)], 22, 0.0, 0.0),                   # right corner -> bottom
    ([_r(352, 72), _r(368, 95), _r(362, 112)], 20, 0.1, 0.0),       # right hook
    ([_r(362, 108), _r(196, 272)], 22, 0.0, 0.0),                   # right arm -> left corner
    ([_r(196, 268), _r(286, 375)], 22, 0.0, 0.0),                   # left corner -> bottom
]


def bezier(pts, t):
    n = len(pts) - 1
    x = y = 0.0
    for i, (px, py) in enumerate(pts):
        b = math.comb(n, i) * (t ** i) * ((1 - t) ** (n - i))
        x += b * px
        y += b * py
    return x, y


def stroke_polygon(pts, width, tin, tout, scale, jitter=0.0, rng=None):
    """Brush-like stroke: tapered at both ends with a slightly ragged edge."""
    steps = 90
    left, right = [], []
    for i in range(steps + 1):
        t = i / steps
        x, y = bezier(pts, t)
        x2, y2 = bezier(pts, min(1.0, t + 1e-3)) if t < 1 else bezier(pts, t)
        x1, y1 = bezier(pts, max(0.0, t - 1e-3))
        dx, dy = x2 - x1, y2 - y1
        ln = math.hypot(dx, dy) or 1.0
        nx, ny = -dy / ln, dx / ln
        # taper profile
        w = width
        if t < tin:
            w *= (t / tin) ** 0.7 if tin > 0 else 1
        elif t > 1 - tout:
            w *= ((1 - t) / tout) ** 0.8
        w = max(w, 0.3)
        j1 = (rng.uniform(-jitter, jitter) if rng else 0)
        j2 = (rng.uniform(-jitter, jitter) if rng else 0)
        left.append(((x + nx * (w / 2 + j1)) * scale, (y + ny * (w / 2 + j1)) * scale))
        right.append(((x - nx * (w / 2 + j2)) * scale, (y - ny * (w / 2 + j2)) * scale))
    return left + right[::-1]


BRAND_IMAGE = None  # set from --brand / art/brand.png
BRAND_BOX = (70, 72, 384, 400)  # x0, y0, x1, y1 in 454 space the brand is fitted into


def load_brand_image(path):
    """Reference image -> 'L' mask where 255 = brand stroke."""
    im = Image.open(path)
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        alpha = im.convert("RGBA").getchannel("A")
        lum = im.convert("L")
        # transparent background: strokes are the opaque pixels
        if alpha.getextrema()[0] < 128:
            return alpha
        im = lum
    lum = im.convert("L")
    arr = np.asarray(lum)
    # strokes are whichever side is the minority of pixels
    dark = arr < 128
    mask = dark if dark.mean() < 0.5 else ~dark
    return Image.fromarray((mask * 255).astype(np.uint8), "L")


def fit_mask(mask, size):
    """Crop to the strokes and fit into BRAND_BOX, at supersampled size."""
    bbox = mask.getbbox()
    mask = mask.crop(bbox)
    S = size * SS
    sc = S / 454.0
    bx0, by0, bx1, by1 = [v * sc for v in BRAND_BOX]
    bw, bh = bx1 - bx0, by1 - by0
    k = min(bw / mask.width, bh / mask.height)
    w, h = max(1, int(mask.width * k)), max(1, int(mask.height * k))
    mask = mask.resize((w, h), Image.LANCZOS)
    out = Image.new("L", (S, S), 0)
    out.paste(mask, (int(bx0 + (bw - w) / 2), int(by0 + (bh - h) / 2)))
    return out


def placeholder_mask(size, rng):
    s = size * SS
    scale = s / 454.0
    m = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(m)
    for pts, w, tin, tout in BRAND:
        d.polygon(stroke_polygon(pts, w, tin, tout, scale, 0.6, rng), fill=255)
    return m


_MASKS = {}


def brand_mask(size, width_mul=1.0, jitter=0.6, seed=7):
    """Brand mask at supersampled size, grown (>1) or thinned (<1)."""
    key = (size, width_mul)
    if key in _MASKS:
        return _MASKS[key]
    if BRAND_IMAGE is not None:
        base = fit_mask(BRAND_IMAGE, size)
    else:
        base = placeholder_mask(size, random.Random(11))
    m = base
    # grow / shrink by roughly (width_mul - 1) * half a stroke (~8px @454)
    px = int(round(abs(width_mul - 1.0) * 8 * size / 454.0 * SS))
    if px > 0:
        k = 2 * min(px, 60) + 1
        f = ImageFilter.MaxFilter if width_mul > 1 else ImageFilter.MinFilter
        # apply in small steps, large kernels are slow
        while k > 1:
            step = min(k, 9)
            m = m.filter(f(step))
            k -= step - 1
    _MASKS[key] = m
    return m


def drips(size, seed, count, strength):
    """Blood running down from points sampled on the brand strokes."""
    rng = random.Random(seed)
    s = size * SS
    scale = s / 454.0
    base = np.asarray(brand_mask(size, 1.0))
    ys, xs = np.nonzero(base > 200)
    m = Image.new("L", (s, s), 0)
    if len(xs) == 0:
        return m
    d = ImageDraw.Draw(m)
    low = int(np.argmax(ys))
    for n in range(count):
        i = low if n == 0 else rng.randrange(len(xs))
        x, y = xs[i] / scale, ys[i] / scale
        length = (48 if n == 0 else rng.uniform(12, 70)) * strength
        if n == 0:
            y -= 6
        dw = rng.uniform(2.0, 4.2)
        bot = y + length
        d.rounded_rectangle([(x - dw / 2) * scale, y * scale, (x + dw / 2) * scale, bot * scale],
                            radius=dw / 2 * scale, fill=255)
        r = dw * rng.uniform(0.9, 1.35)
        d.ellipse([(x - r) * scale, (bot - r) * scale, (x + r) * scale, (bot + r * 1.3) * scale], fill=255)
    return m


def distress(size, seed, count):
    rng = random.Random(seed)
    s = size * SS
    scale = s / 454.0
    m = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(m)
    for _ in range(count):
        x = rng.uniform(150, 304)
        y = rng.uniform(60, 410)
        rx = rng.uniform(0.3, 1.6)
        ry = rx * rng.uniform(0.4, 1.2)
        d.ellipse([(x - rx) * scale, (y - ry) * scale, (x + rx) * scale, (y + ry) * scale],
                  fill=rng.randint(120, 255))
    return m


def splatter(size, seed, count, spread):
    rng = random.Random(seed)
    s = size * SS
    scale = s / 454.0
    m = Image.new("L", (s, s), 0)
    d = ImageDraw.Draw(m)
    for _ in range(count):
        ang = rng.uniform(0, 2 * math.pi)
        dist = abs(rng.gauss(0, spread))
        cx = 227 + math.cos(ang) * dist
        cy = 235 + math.sin(ang) * dist * 1.1
        r = rng.uniform(0.6, 2.8) * (1.0 - min(dist, 200) / 260)
        a = rng.randint(90, 255)
        d.ellipse([(cx - r) * scale, (cy - r) * scale, (cx + r) * scale, (cy + r) * scale], fill=a)
    return m


def radial(size, inner, outer, power=1.6, center=(0.5, 0.47)):
    y, x = np.mgrid[0:size, 0:size].astype(np.float32)
    cx, cy = size * center[0], size * center[1]
    r = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / (size / 2)
    t = np.clip(r, 0, 1) ** power
    inner = np.array(inner, np.float32)
    outer = np.array(outer, np.float32)
    img = inner[None, None, :] * (1 - t[..., None]) + outer[None, None, :] * t[..., None]
    return img


def colorize(mask, rgb):
    layer = Image.new("RGB", mask.size, rgb)
    return layer, mask


def make_background(size, bleed):
    rng = np.random.default_rng(3 if bleed else 1)
    # base: warm near-black with a faint ember glow behind the brand
    base = radial(size,
                  (38, 6, 8) if bleed else (24, 12, 11),
                  (2, 1, 1), power=1.3)
    # grain (kept low so the PNG stays small and AMOLED blacks stay black)
    grain = rng.normal(0, 2.2, (size, size, 1)).astype(np.float32)
    base = np.clip(base + grain, 0, 255)
    img = Image.fromarray(base.astype(np.uint8), "RGB")

    # iron bezel ring + minute ticks
    big = img.resize((size * SS, size * SS), Image.BICUBIC)
    d = ImageDraw.Draw(big)
    S = size * SS
    c = S / 2
    sc = S / 454.0
    d.ellipse([c - 225 * sc, c - 225 * sc, c + 225 * sc, c + 225 * sc], outline=(58, 44, 40), width=int(2 * sc))
    for i in range(60):
        a = math.radians(i * 6)
        major = i % 5 == 0
        r1 = (226 if major else 226) * sc
        r0 = (212 if major else 219) * sc
        col = (120, 30, 32) if (major and bleed) else ((92, 80, 74) if major else (48, 40, 38))
        w = int((3 if major else 1.5) * sc)
        d.line([(c + math.sin(a) * r0, c - math.cos(a) * r0), (c + math.sin(a) * r1, c - math.cos(a) * r1)],
               fill=col, width=w)

    # brand glow
    mask = brand_mask(size, 1.0, seed=11)
    glow_mask = brand_mask(size, 1.8, jitter=0, seed=11).filter(ImageFilter.GaussianBlur(10 * SS))
    glow_col = (200, 10, 20) if bleed else (90, 8, 12)
    glow_amt = 0.6 if bleed else 0.35
    big = Image.composite(Image.new("RGB", big.size, glow_col), big,
                          glow_mask.point(lambda v: int(v * glow_amt)))

    # scar tissue: dark rim under the brand
    rim = brand_mask(size, 1.35, seed=11).filter(ImageFilter.GaussianBlur(2 * SS))
    big = Image.composite(Image.new("RGB", big.size, (20, 2, 3)), big, rim.point(lambda v: int(v * 0.8)))

    # the brand itself: gradient from dark crimson edge to hot core
    core_col = (214, 18, 30) if bleed else (122, 14, 20)
    edge_col = (120, 6, 12) if bleed else (70, 8, 12)
    big = Image.composite(Image.new("RGB", big.size, edge_col), big, mask)
    core = brand_mask(size, 0.8, jitter=0.2, seed=11).filter(ImageFilter.GaussianBlur(1 * SS))
    big = Image.composite(Image.new("RGB", big.size, core_col), big, core)
    if bleed:
        hot = brand_mask(size, 0.5, jitter=0, seed=11).filter(ImageFilter.GaussianBlur(3 * SS))
        big = Image.composite(Image.new("RGB", big.size, (255, 60, 50)), big, hot.point(lambda v: int(v * 0.35)))

    # distress: worn specks inside the strokes
    specks = distress(size, 21, 900 if bleed else 700)
    worn = ImageChops.multiply(specks, mask)
    big = Image.composite(Image.new("RGB", big.size, (40, 4, 6) if bleed else (24, 4, 5)), big, worn)

    # blood
    if bleed:
        dm = drips(size, 5, 22, 1.0)
        big = Image.composite(Image.new("RGB", big.size, (150, 6, 14)), big, dm)
        sp = splatter(size, 9, 260, 120)
        big = Image.composite(Image.new("RGB", big.size, (120, 4, 10)), big, sp)
    else:
        dm = drips(size, 5, 8, 0.45)
        big = Image.composite(Image.new("RGB", big.size, (70, 8, 12)), big, dm)
        sp = splatter(size, 9, 70, 130)
        big = Image.composite(Image.new("RGB", big.size, (52, 8, 10)), big, sp.point(lambda v: int(v * 0.7)))

    img = big.resize((size, size), Image.LANCZOS)

    # vignette to pure black at the rim (keeps round-bezel edge clean)
    vig = radial(size, (1.0, 1.0, 1.0), (0.0, 0.0, 0.0), power=6.0, center=(0.5, 0.5))
    arr = np.asarray(img).astype(np.float32) * (0.35 + 0.65 * vig)
    img = Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8), "RGB")
    # restore bezel ticks over vignette
    ring = Image.new("L", (size, size), 0)
    rd = ImageDraw.Draw(ring)
    rd.ellipse([0, 0, size - 1, size - 1], fill=255)
    img = Image.composite(img, Image.new("RGB", (size, size), (0, 0, 0)), ring)
    return img


# ---------------------------------------------------------------------------
# Icons (drawn at 8x then downsampled)
# ---------------------------------------------------------------------------
BONE = (232, 220, 196)
BLOOD = (214, 22, 40)
EMBER = (255, 90, 50)
GOLD = (214, 170, 60)
ASH = (150, 138, 128)
STEEL = (120, 160, 200)


def icon(draw_fn, px=22):
    k = 8
    s = px * k
    im = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    draw_fn(d, s)
    return im.resize((px, px), Image.LANCZOS)


def i_heart(d, s):
    r = s * 0.24
    d.ellipse([s * 0.08, s * 0.14, s * 0.08 + 2 * r, s * 0.14 + 2 * r], fill=BLOOD)
    d.ellipse([s * 0.92 - 2 * r, s * 0.14, s * 0.92, s * 0.14 + 2 * r], fill=BLOOD)
    d.polygon([(s * 0.1, s * 0.46), (s * 0.9, s * 0.46), (s * 0.5, s * 0.9)], fill=BLOOD)


def i_steps(d, s):
    d.ellipse([s * 0.14, s * 0.12, s * 0.42, s * 0.56], fill=BONE)
    d.ellipse([s * 0.18, s * 0.62, s * 0.40, s * 0.80], fill=BONE)
    d.ellipse([s * 0.56, s * 0.24, s * 0.84, s * 0.68], fill=BONE)
    d.ellipse([s * 0.60, s * 0.74, s * 0.82, s * 0.92], fill=BONE)


def i_flame(d, s):
    d.polygon([(s * 0.5, s * 0.04), (s * 0.82, s * 0.5), (s * 0.78, s * 0.8), (s * 0.5, s * 0.96),
               (s * 0.22, s * 0.8), (s * 0.18, s * 0.52), (s * 0.34, s * 0.34), (s * 0.4, s * 0.5)], fill=EMBER)
    d.polygon([(s * 0.52, s * 0.42), (s * 0.66, s * 0.66), (s * 0.6, s * 0.86), (s * 0.44, s * 0.86),
               (s * 0.38, s * 0.7)], fill=GOLD)


def i_stairs(d, s):
    w = s * 0.12
    pts = [(0.1, 0.9), (0.1, 0.7), (0.3, 0.7), (0.3, 0.5), (0.5, 0.5), (0.5, 0.3), (0.7, 0.3), (0.7, 0.1), (0.92, 0.1)]
    d.line([(x * s, y * s) for x, y in pts], fill=BONE, width=int(w), joint="curve")


def i_bolt(d, s):
    d.polygon([(s * 0.58, s * 0.02), (s * 0.16, s * 0.56), (s * 0.46, s * 0.56), (s * 0.38, s * 0.98),
               (s * 0.84, s * 0.40), (s * 0.54, s * 0.40)], fill=GOLD)


def i_stress(d, s):
    pts = [(0.04, 0.55), (0.24, 0.55), (0.34, 0.2), (0.5, 0.88), (0.64, 0.35), (0.72, 0.55), (0.96, 0.55)]
    d.line([(x * s, y * s) for x, y in pts], fill=EMBER, width=int(s * 0.11), joint="curve")


def i_intensity(d, s):
    # sword (Dragonslayer silhouette)
    d.polygon([(s * 0.44, s * 0.62), (s * 0.44, s * 0.14), (s * 0.5, s * 0.02), (s * 0.56, s * 0.14),
               (s * 0.56, s * 0.62)], fill=BONE)
    d.rectangle([s * 0.24, s * 0.62, s * 0.76, s * 0.70], fill=ASH)
    d.rectangle([s * 0.46, s * 0.70, s * 0.54, s * 0.92], fill=(120, 80, 60))
    d.ellipse([s * 0.43, s * 0.88, s * 0.57, s * 1.0], fill=ASH)


def i_drop(d, s):
    d.polygon([(s * 0.5, s * 0.04), (s * 0.78, s * 0.5), (s * 0.22, s * 0.5)], fill=STEEL)
    d.ellipse([s * 0.2, s * 0.34, s * 0.8, s * 0.94], fill=STEEL)


def i_mountain(d, s):
    d.polygon([(s * 0.02, s * 0.9), (s * 0.38, s * 0.22), (s * 0.56, s * 0.54), (s * 0.68, s * 0.38),
               (s * 0.98, s * 0.9)], fill=ASH)
    d.polygon([(s * 0.38, s * 0.22), (s * 0.48, s * 0.4), (s * 0.30, s * 0.38)], fill=BONE)


def i_hourglass(d, s):
    d.rectangle([s * 0.18, s * 0.04, s * 0.82, s * 0.12], fill=BONE)
    d.rectangle([s * 0.18, s * 0.88, s * 0.82, s * 0.96], fill=BONE)
    d.polygon([(s * 0.26, s * 0.12), (s * 0.74, s * 0.12), (s * 0.54, s * 0.5), (s * 0.74, s * 0.88),
               (s * 0.26, s * 0.88), (s * 0.46, s * 0.5)], fill=ASH)
    d.polygon([(s * 0.32, s * 0.88), (s * 0.68, s * 0.88), (s * 0.5, s * 0.64)], fill=GOLD)


def i_sun(d, s):
    c = s / 2
    for k in range(8):
        a = k * math.pi / 4
        d.line([(c + math.cos(a) * s * 0.3, c + math.sin(a) * s * 0.3),
                (c + math.cos(a) * s * 0.46, c + math.sin(a) * s * 0.46)], fill=GOLD, width=int(s * 0.08))
    d.ellipse([c - s * 0.22, c - s * 0.22, c + s * 0.22, c + s * 0.22], fill=GOLD)


def i_sunrise(d, s):
    c = s / 2
    d.pieslice([s * 0.16, s * 0.42, s * 0.84, s * 1.1], 180, 360, fill=GOLD)
    d.rectangle([0, s * 0.76, s, s * 0.84], fill=ASH)
    d.polygon([(c, s * 0.02), (c + s * 0.18, s * 0.26), (c - s * 0.18, s * 0.26)], fill=GOLD)


def i_sunset(d, s):
    c = s / 2
    d.pieslice([s * 0.16, s * 0.42, s * 0.84, s * 1.1], 180, 360, fill=EMBER)
    d.rectangle([0, s * 0.76, s, s * 0.84], fill=ASH)
    d.polygon([(c, s * 0.3), (c + s * 0.18, s * 0.06), (c - s * 0.18, s * 0.06)], fill=EMBER)


def i_moon(d, s):
    d.ellipse([s * 0.1, s * 0.1, s * 0.9, s * 0.9], fill=BONE)
    d.ellipse([s * 0.32, s * 0.02, s * 1.06, s * 0.76], fill=(0, 0, 0, 0))


def i_bell(d, s):
    d.pieslice([s * 0.18, s * 0.1, s * 0.82, s * 0.9], 180, 360, fill=BONE)
    d.rectangle([s * 0.18, s * 0.48, s * 0.82, s * 0.74], fill=BONE)
    d.rectangle([s * 0.08, s * 0.72, s * 0.92, s * 0.8], fill=BONE)
    d.ellipse([s * 0.4, s * 0.8, s * 0.6, s * 0.98], fill=BONE)


def i_bt(d, s):
    w = int(s * 0.09)
    pts = [(0.24, 0.3), (0.74, 0.7), (0.5, 0.9), (0.5, 0.1), (0.74, 0.3), (0.24, 0.7)]
    d.line([(x * s, y * s) for x, y in pts], fill=STEEL, width=w, joint="curve")


def i_alarm(d, s):
    d.ellipse([s * 0.14, s * 0.18, s * 0.86, s * 0.9], outline=BONE, width=int(s * 0.1))
    d.line([(s * 0.5, s * 0.54), (s * 0.5, s * 0.34)], fill=BONE, width=int(s * 0.08))
    d.line([(s * 0.5, s * 0.54), (s * 0.66, s * 0.62)], fill=BONE, width=int(s * 0.08))
    d.line([(s * 0.1, s * 0.22), (s * 0.28, s * 0.06)], fill=BONE, width=int(s * 0.1))
    d.line([(s * 0.9, s * 0.22), (s * 0.72, s * 0.06)], fill=BONE, width=int(s * 0.1))


def i_dnd(d, s):
    d.ellipse([s * 0.06, s * 0.06, s * 0.94, s * 0.94], fill=ASH)
    d.rectangle([s * 0.24, s * 0.44, s * 0.76, s * 0.56], fill=(0, 0, 0, 0))


def i_battery(d, s):
    d.rectangle([s * 0.02, s * 0.26, s * 0.86, s * 0.74], outline=BONE, width=int(s * 0.08))
    d.rectangle([s * 0.86, s * 0.40, s * 0.98, s * 0.60], fill=BONE)


def i_distance(d, s):
    d.line([(s * 0.14, s * 0.1), (s * 0.14, s * 0.96)], fill=BONE, width=int(s * 0.1))
    d.polygon([(s * 0.18, s * 0.1), (s * 0.88, s * 0.28), (s * 0.18, s * 0.46)], fill=BLOOD)


def i_temp(d, s):
    d.rounded_rectangle([s * 0.38, s * 0.04, s * 0.62, s * 0.66], radius=s * 0.12, outline=BONE, width=int(s * 0.07))
    d.ellipse([s * 0.26, s * 0.56, s * 0.74, s * 0.98], fill=BLOOD)
    d.rectangle([s * 0.46, s * 0.3, s * 0.54, s * 0.66], fill=BLOOD)


ICONS = {
    "heart": i_heart, "steps": i_steps, "flame": i_flame, "stairs": i_stairs, "bolt": i_bolt,
    "stress": i_stress, "sword": i_intensity, "drop": i_drop, "mountain": i_mountain,
    "hourglass": i_hourglass, "sun": i_sun, "sunrise": i_sunrise, "sunset": i_sunset, "moon": i_moon,
    "bell": i_bell, "bt": i_bt, "alarm": i_alarm, "dnd": i_dnd, "battery": i_battery,
    "distance": i_distance, "temp": i_temp,
}


def make_aod_brand(px=90):
    """Outline-only brand for always-on mode (few lit pixels)."""
    s = px * SS
    solid = brand_mask(454, 1.0).resize((s, s), Image.LANCZOS)
    inner = solid.filter(ImageFilter.MinFilter(9))
    outline = ImageChops.subtract(solid, inner)
    out = Image.new("RGBA", (s, s), (150, 16, 24, 0))
    out.putalpha(outline)
    return out.resize((px, px), Image.LANCZOS)


def make_launcher(px=70):
    bg = make_background(454, True).resize((px, px), Image.LANCZOS)
    m = Image.new("L", (px, px), 0)
    ImageDraw.Draw(m).ellipse([0, 0, px - 1, px - 1], fill=255)
    out = Image.new("RGBA", (px, px), (0, 0, 0, 0))
    out.paste(bg, (0, 0), m)
    return out


def main():
    global BRAND_IMAGE
    ap = argparse.ArgumentParser()
    ap.add_argument("--brand", help="reference image of the Brand of Sacrifice")
    args = ap.parse_args()
    path = args.brand or os.path.join(ROOT, "art", "brand.png")
    if os.path.exists(path):
        BRAND_IMAGE = load_brand_image(path)
        print(f"brand traced from {path}")
    else:
        print("no reference image found - drawing PLACEHOLDER sigil (see README)")
    for size in SIZES:
        out = os.path.join(ROOT, f"resources-round-{size}x{size}", "drawables")
        os.makedirs(out, exist_ok=True)
        make_background(size, False).save(os.path.join(out, "bg_calm.png"), optimize=True)
        make_background(size, True).save(os.path.join(out, "bg_bleed.png"), optimize=True)
    # default (fallback) backgrounds for any other round screen
    dflt = os.path.join(ROOT, "resources", "drawables")
    os.makedirs(dflt, exist_ok=True)
    make_background(454, False).save(os.path.join(dflt, "bg_calm.png"), optimize=True)
    make_background(454, True).save(os.path.join(dflt, "bg_bleed.png"), optimize=True)
    for name, fn in ICONS.items():
        icon(fn).save(os.path.join(dflt, f"icon_{name}.png"), optimize=True)
    make_aod_brand().save(os.path.join(dflt, "aod_brand.png"), optimize=True)
    make_launcher().save(os.path.join(dflt, "launcher_icon.png"), optimize=True)
    print("assets written")


if __name__ == "__main__":
    main()
