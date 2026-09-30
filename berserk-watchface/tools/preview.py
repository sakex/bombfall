#!/usr/bin/env python3
"""Approximate mock-up of the face with sample data (system fonts differ
slightly from Garmin's; use the Connect IQ simulator for the real thing).

    python3 tools/preview.py [out.png]
"""
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRAW = os.path.join(ROOT, "resources", "drawables")
BONE, ASH, BLOOD, EMBER, GOLD, STEEL, TRACK = (
    (232, 220, 196), (154, 142, 132), (224, 24, 44), (255, 90, 50), (214, 170, 60), (120, 160, 200), (42, 28, 28))
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
F = {"xtiny": ImageFont.truetype(BOLD, 21), "tiny": ImageFont.truetype(BOLD, 25),
     "small": ImageFont.truetype(BOLD, 30), "hot": ImageFont.truetype(BOLD, 118)}
CX = CY = 227


def ic(name):
    return Image.open(os.path.join(DRAW, f"icon_{name}.png")).convert("RGBA")


def text(d, x, y, s, font, col, anchor, halo=1):
    for dx, dy in ((-halo, -halo), (halo, -halo), (-halo, halo), (halo, halo)):
        d.text((x + dx, y + dy), s, font=font, fill=(0, 0, 0), anchor=anchor)
    d.text((x, y), s, font=font, fill=col, anchor=anchor)


def cell(img, d, x, y, icon, s, col, font):
    im = ic(icon)
    tw = d.textlength(s, font=font) if s else 0
    w = im.width + (5 + tw if s else 0)
    left = int(x - w / 2)
    img.paste(im, (left, int(y - im.height / 2)), im)
    if s:
        text(d, left + im.width + 5, y, s, font, col, "lm")
    return w


def arc(d, start, span, cw, frac, col, r=204, pen=8):
    box = [CX - r, CY - r, CX + r, CY + r]
    # PIL angles are clockwise from 3 o'clock; Garmin's are counter-clockwise
    def pil(a):
        return (-a) % 360
    a0, a1 = (start - span, start) if cw else (start, start + span)
    d.arc(box, pil(a1), pil(a0), fill=TRACK, width=pen)
    if frac > 0:
        f = min(frac, 1) * span
        b0, b1 = (start - f, start) if cw else (start, start + f)
        d.arc(box, pil(b1), pil(b0), fill=col, width=pen)


def main(out, bleed):
    bg = Image.open(os.path.join(ROOT, "resources-round-454x454", "drawables",
                                 "bg_bleed.png" if bleed else "bg_calm.png")).convert("RGB")
    img = bg.copy()
    d = ImageDraw.Draw(img)
    arc(d, 215, 70, True, 0.76, GOLD)
    arc(d, 325, 70, False, 0.62, BLOOD)
    for name, deg in (("bolt", 223), ("steps", 317)):
        x = CX + 204 * math.cos(math.radians(deg))
        y = CY - 204 * math.sin(math.radians(deg))
        im = ic(name)
        img.paste(im, (int(x - im.width / 2), int(y - im.height / 2)), im)

    # status row
    items = [("bt", "", STEEL), ("bell", "3", BONE), ("alarm", "", BONE), ("battery", "78% 11d", BONE)]
    widths = [ic(n).width + ((5 + d.textlength(s, font=F["xtiny"])) if s else 0) for n, s, _ in items]
    x = CX - (sum(widths) + 10 * (len(items) - 1)) / 2
    for (n, s, c), w in zip(items, widths):
        cell(img, d, x + w / 2, 46, n, s, c, F["xtiny"])
        x += w + 10
    text(d, CX, 80, "WED 30 SEP", F["small"], BONE, "mm", 2)
    cell(img, d, CX - 104, 114, "mountain", "432m", ASH, F["xtiny"])
    cell(img, d, CX, 114, "drop", "97%", STEEL, F["xtiny"])
    cell(img, d, CX + 104, 114, "hourglass", "18h", ASH, F["xtiny"])

    t = "21:47"
    text(d, CX, 194, t, F["hot"], BONE, "mm", 3)
    tw = d.textlength(t, font=F["hot"])
    text(d, CX + tw / 2 + 4, 218, "32", F["tiny"], BLOOD, "lm", 2)

    cell(img, d, CX - 116, 280, "heart", "58", BONE, F["tiny"])
    cell(img, d, CX, 280, "bolt", "76", GOLD, F["tiny"])
    cell(img, d, CX + 116, 280, "stress", "24", BONE, F["tiny"])
    cell(img, d, CX - 116, 318, "steps", "6,214", BONE, F["tiny"])
    cell(img, d, CX, 318, "flame", "1840", BONE, F["tiny"])
    cell(img, d, CX + 116, 318, "stairs", "9", BONE, F["tiny"])
    cell(img, d, CX - 72, 356, "temp", "14° 19°/8°", BONE, F["xtiny"])
    cell(img, d, CX + 78, 356, "sunrise" if bleed else "sunset", "07:31" if bleed else "19:12",
         GOLD if bleed else EMBER, F["xtiny"])
    cell(img, d, CX - 64, 392, "sword", "145", BONE, F["xtiny"])
    cell(img, d, CX + 64, 392, "distance", "4.8km", BONE, F["xtiny"])
    img.save(out)


if __name__ == "__main__":
    base = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "preview.png")
    stem, ext = os.path.splitext(base)  # writes <stem>_day / <stem>_night
    main(stem + "_day" + ext, False)
    main(stem + "_night" + ext, True)
    print("wrote", stem + "_day" + ext, stem + "_night" + ext)
