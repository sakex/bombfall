# One vault cell: armoured steel that takes three blasts. 1 x 1 x 2 m like
# tile_floor (front at -Y), centred. A heavy brushed-steel block with deep
# chamfers, a thick bevelled armour plate on the front held by domed rivets
# and crossed by a worn hazard band, and tread plate on top. Much lighter and
# heavier-looking than the dark floor slabs, so it reads as "tough".
# One mesh for the game's MultiMesh; the game shakes it when it is hit.
#   blender -b --python blender/tile_steel.py -- --preview blender/previews
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
F = -1.0


def draw_hazard(img, d):
    """The hazard band across the armour plate, chipped at the edges."""
    w, h = img.size
    d.rectangle((0, 0, w, h), fill=(236, 176, 18, 255))
    step = h * 1.6
    x = -h
    while x < w + h:
        d.polygon([(x, h), (x + step / 2, h), (x + step / 2 + h, 0), (x + h, 0)], fill=(22, 20, 24, 255))
        x += step
    rnd = random.Random(11)
    for _ in range(70):     # chips knocked out of the paint
        cx, cy = rnd.uniform(0, w), rnd.choice((rnd.uniform(0, 6), rnd.uniform(h - 6, h), rnd.uniform(0, h)))
        r = rnd.uniform(1.5, 5)
        d.ellipse((cx - r, cy - r * 0.7, cx + r, cy + r * 0.7), fill=(0, 0, 0, 0))


def draw_tread(img, d):
    """Diamond tread plate: slim raised lozenges in alternating directions."""
    w, h = img.size
    n = 9                      # lozenges per 1 m
    cell = w / n
    L, W = cell * 0.34, cell * 0.075
    for j in range(int(h / cell) + 2):
        for i in range(n + 1):
            cx, cy = (i + 0.5) * cell, (j + 0.5) * cell
            s = 1 if (i + j) % 2 == 0 else -1
            ax, ay = L * 0.7071, s * L * 0.7071        # long axis
            bx, by = -W * 0.7071 * s, W * 0.7071        # short axis
            d.polygon([(cx - ax, cy - ay), (cx + bx, cy + by), (cx + ax, cy + ay), (cx - bx, cy - by)],
                      fill=(255, 255, 255, 255))


def draw_plate(img, d):
    """Stencil and weld seams on the armour plate."""
    w, h = img.size
    k = w / 0.84
    f = pil_font(int(0.075 * k))
    d.text((0.42 * k, 0.2 * k), "VAULT-9", font=f, fill=(30, 30, 36, 255), anchor="mm")
    d.text((0.42 * k, 0.66 * k), "ARMOR  CL.3", font=pil_font(int(0.05 * k)), fill=(30, 30, 36, 255), anchor="mm")


hazard = decal_image("steel_hazard", 256, 32, draw_hazard)
tread = decal_image("steel_tread", 256, 512, draw_tread)
plate_art = decal_image("steel_plate", 256, 256, draw_plate)

STEEL_BODY = decal_pbr("metal", (0.34, 0.36, 0.42), [
    dict(image=tread, origin=(0, 0, 0.5), size=(1.0, 2.0), u=(1, 0, 0), v=(0, 1, 0), depth=0.02, facing=0.9,
         mode="none", emboss=1.0, rough=0.25),
], name="steel_body", rough=0.4, grime=0.3, scale=0.6, emboss_distance=0.008)
ARMOR = decal_pbr("metal", (0.46, 0.48, 0.54), [
    dict(image=hazard, origin=(0, F - 0.07, 0.0), size=(0.84, 0.16), depth=0.03, rough=0.55),
    dict(image=plate_art, origin=(0, F - 0.07, 0.0), size=(0.84, 0.84), depth=0.03, mode="multiply", rough=0.5),
], name="steel_armor", rough=0.3, grime=0.15, scale=0.6)
RIVET = pbr("chrome", (0.62, 0.63, 0.68), rough=0.18, name="steel_rivet")

tile_block(STEEL_BODY, chamfer=0.07, name="block", front_only=True)
# The armour plate: 6 cm thick with a deep chamfer that catches the light.
bm_box((0.84, 0.08, 0.84), (0, F - 0.03, 0), ARMOR, chamfer=0.035)
# Domed rivets round the plate (the band runs between the middle pair).
for x, z in ((-0.34, 0.34), (0.0, 0.34), (0.34, 0.34), (-0.34, -0.34), (0.0, -0.34), (0.34, -0.34),
             (-0.34, 0.0), (0.34, 0.0)):
    if z == 0.0:
        continue
    bolt((x, F - 0.07, z), (0, -1, 0), 0.04, 0.012, RIVET, dome=0.025)
# Heavy corner brackets tying the plate to the block.
for sx in (-1, 1):
    for sz in (-1, 1):
        bm_box((0.1, 0.15, 0.1), (sx * 0.43, F - 0.015, sz * 0.43), RIVET, chamfer=0.012)

finish("tile_steel", body="tile_steel")
tri_report("tile_steel")
export("tile_steel", tex=256)
sheet("tile_steel", views=[(0, 0), (25, 30), (-50, 20), (0, 70)])
