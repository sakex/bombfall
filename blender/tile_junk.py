# One cell of the junkyard walls: a bale of compacted scrap, 1 x 1 x 2 m
# like tile_floor (front at -Y), centred. Crushed painted sheet metal and
# rust make up the block (a baked collage), with real pieces jutting out of
# the front: a split wooden crate, pipe ends, a hubcap, bent plates, a
# cable loop and a broken neon tube still glowing. Everything stays inside
# the cell so bales stack and line up; one mesh for the game's MultiMesh.
#   blender -b --python blender/tile_junk.py -- --preview blender/previews
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
F = -1.0


PAINTS = [((92, 50, 30), 5), ((58, 58, 66), 4), ((50, 76, 78), 2), ((104, 42, 36), 2), ((128, 104, 48), 1),
          ((88, 86, 84), 2), ((70, 40, 26), 3), ((62, 48, 72), 1)]


def _pick(rnd):
    tot = sum(w for _, w in PAINTS)
    x = rnd.uniform(0, tot)
    for c, w in PAINTS:
        x -= w
        if x <= 0:
            return c
    return PAINTS[0][0]


def draw_scrap(img, d, seed, label=True, emboss=False):
    """Crushed sheet metal pressed into strata: jagged horizontal layers of
    rust, bare steel and faded paint with dark creases between them. With
    `emboss` it draws the height instead (creases low, layers raised)."""
    rnd = random.Random(seed)
    w, h = img.size
    d.rectangle((0, 0, w, h), fill=(0, 0, 0, 0) if emboss else (40, 26, 20, 255))
    y = -4.0
    while y < h + 8:
        t = rnd.uniform(5, 18) * h / 256
        pts_top, pts_bot = [], []
        n = 9
        for i in range(n + 1):
            x = w * i / n
            pts_top.append((x, y + rnd.uniform(-3, 3) * h / 256))
            pts_bot.append((x, y + t + rnd.uniform(-3, 3) * h / 256))
        col = _pick(rnd)
        f = rnd.uniform(0.8, 1.1)
        fill = (255, 255, 255, 255) if emboss else (int(col[0] * f), int(col[1] * f), int(col[2] * f), 255)
        d.polygon(pts_top + pts_bot[::-1], fill=fill)
        if not emboss:
            d.line(pts_bot, fill=(16, 10, 10, 255), width=2)
            # rust blooms and paint chips on the layer
            for _ in range(int(w / 40)):
                cx, cy = rnd.uniform(0, w), y + rnd.uniform(0, t)
                r = rnd.uniform(1.5, 4.5)
                d.ellipse((cx - r * 1.6, cy - r * 0.6, cx + r * 1.6, cy + r * 0.6), fill=(110, 50, 22, 210))
        else:
            d.line(pts_bot, fill=(0, 0, 0, 0), width=3)
        y += t
    if label and not emboss:
        f = pil_font(int(h * 0.06))
        d.text((w * 0.74, h * 0.17), "FRAGILE", font=f, fill=(170, 46, 36, 255), anchor="mm")
        d.rectangle((w * 0.05, h * 0.87, w * 0.36, h * 0.93), fill=(190, 145, 24, 255))
        for i in range(5):
            x = w * (0.05 + i * 0.065)
            d.polygon([(x, h * 0.93), (x + w * 0.03, h * 0.93), (x + w * 0.05, h * 0.87), (x + w * 0.02, h * 0.87)],
                      fill=(20, 18, 20, 255))


def draw_front(img, d):
    draw_scrap(img, d, 3, True)


def draw_top(img, d):
    draw_scrap(img, d, 8, False)


def draw_side(img, d):
    draw_scrap(img, d, 13, False)


front = decal_image("junk_front", 256, 256, draw_front)
top = decal_image("junk_top", 256, 512, draw_top)
side = decal_image("junk_side", 512, 256, draw_side)
front_h = decal_image("junk_front_h", 256, 256, lambda i, d: draw_scrap(i, d, 3, False, True))
side_h = decal_image("junk_side_h", 512, 256, lambda i, d: draw_scrap(i, d, 13, False, True))

SCRAP = decal_pbr("paint", (0.2, 0.12, 0.08), [
    dict(image=front, origin=(0, F, 0), size=(1.0, 1.0), depth=0.02, facing=0.9, rough=0.7),
    dict(image=top, origin=(0, 0, 0.5), size=(1.0, 2.0), u=(1, 0, 0), v=(0, 1, 0), depth=0.02, facing=0.9,
         rough=0.7),
    dict(image=top, origin=(0, 0, -0.5), size=(1.0, 2.0), u=(1, 0, 0), v=(0, -1, 0), depth=0.02, facing=0.9,
         rough=0.7),
    dict(image=side, origin=(0.5, 0, 0), size=(2.0, 1.0), u=(0, 1, 0), v=(0, 0, 1), depth=0.02, facing=0.9,
         rough=0.7),
    dict(image=side, origin=(-0.5, 0, 0), size=(2.0, 1.0), u=(0, -1, 0), v=(0, 0, 1), depth=0.02, facing=0.9,
         rough=0.7),
    dict(image=front_h, origin=(0, F, 0), size=(1.0, 1.0), depth=0.02, facing=0.9, mode="none", emboss=1.0),
    dict(image=side_h, origin=(0.5, 0, 0), size=(2.0, 1.0), u=(0, 1, 0), v=(0, 0, 1), depth=0.02, facing=0.9,
         mode="none", emboss=1.0),
    dict(image=side_h, origin=(-0.5, 0, 0), size=(2.0, 1.0), u=(0, -1, 0), v=(0, 0, 1), depth=0.02, facing=0.9,
         mode="none", emboss=1.0),
], name="junk_scrap", wear=0.9, grime=0.9, bump=0.8, scale=0.4, emboss_distance=0.01)
WOOD_M = pbr("wood", (0.24, 0.13, 0.06), color2=(0.13, 0.07, 0.03), name="junk_wood", grime=0.9)
PIPE = pbr("metal", (0.5, 0.5, 0.52), name="junk_pipe", grime=0.8, rough=0.45)
COPPER = pbr("gold", (0.55, 0.26, 0.14), rough=0.5, name="junk_copper", grime=0.8)
TEAL = pbr("paint", (0.05, 0.3, 0.32), name="junk_teal", wear=1.0, grime=0.8)
RED_P = pbr("paint", (0.45, 0.06, 0.05), name="junk_red", wear=1.0, grime=0.8)
CHROME_M = pbr("metal", (0.6, 0.61, 0.64), rough=0.25, name="junk_chrome", grime=0.6)
CABLE = pbr("rubber", (0.6, 0.45, 0.05), name="junk_cable")
DARK = pbr("rubber", (0.02, 0.02, 0.025), name="junk_hole", grime=0.0, wear=0.0)
TUBE = pbr("neon", (0.3, 0.1, 0.02), emit=ORANGE, strength=3.0, name="junk_neon")

tile_block(SCRAP, chamfer=0.05, name="bale")

# Split wooden crate end, top left.
bm_box((0.32, 0.12, 0.2), (-0.27, F + 0.0, 0.3), WOOD_M, rot=(0, 0.14, 0.06))
# Pipe ends poking out (open, dark inside).
for (x, z, r, m) in ((0.3, 0.3, 0.085, PIPE), (0.12, -0.3, 0.065, COPPER), (0.36, -0.14, 0.05, PIPE)):
    lathe([(r * 0.72, -0.04), (r, 0.0), (r, 0.06), (r * 0.72, 0.06)], m, segments=7, loc=(x, F, z),
          rot=(math.pi / 2, 0, 0))
    lathe([(r * 0.72, 0.03), (0.0, 0.03)], DARK, segments=7, loc=(x, F, z), rot=(math.pi / 2, 0, 0))
# A hubcap half buried in the bale.
lathe([(0.16, -0.02), (0.16, 0.02), (0.1, 0.045), (0.0, 0.058)], CHROME_M, segments=11,
      loc=(-0.24, F + 0.02, -0.22), rot=(math.pi / 2 + 0.25, 0.0, 0.3))
# Bent plates.
bm_box((0.34, 0.02, 0.16), (0.08, F - 0.01, 0.06), TEAL, rot=(0.25, -0.35, 0.1))
bm_box((0.26, 0.02, 0.12), (-0.05, F - 0.01, -0.36), RED_P, rot=(-0.3, 0.2, 0.0))
# A cable loop.
tube(smooth_path([(-0.47, F + 0.02, 0.02), (-0.3, F - 0.05, -0.02), (-0.08, F - 0.04, 0.1), (0.05, F + 0.02, -0.08)], 2),
     0.022, CABLE, sides=5, name="cable")
# A broken neon tube, still lit.
rod((0.0, F - 0.02, 0.4), (0.26, F - 0.05, 0.2), 0.022, TUBE, verts=6)

finish("tile_junk", body="tile_junk")
tri_report("tile_junk")
export("tile_junk", tex=256)
sheet("tile_junk", views=[(0, 0), (25, 30), (-50, 20), (0, 70)])
