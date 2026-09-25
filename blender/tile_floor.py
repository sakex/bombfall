# One floor/wall cell of the hotel: 1 m wide, 1 m tall, 2 m deep (front at
# -Y), centred on the origin. A dark steel slab with chamfered edges: a
# carpeted walkway on top (hotel corridor carpet with a gold border), a
# brass nosing along the front edge, a raised bolted panel on the front,
# and two inset neon strips that run edge to edge so neighbouring cells form
# continuous lines. Drawn through a MultiMesh (hundreds on screen): one
# mesh, few triangles, a 256 px atlas.
#   blender -b --python blender/tile_floor.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
F = -1.0          # the front face (y)


def draw_carpet(img, d):
    """The top face, 1 x 2 m (x across, image y = depth, front at the
    bottom of the image). Repeats every 0.5 m across so cells join."""
    w, h = img.size
    k = w / 1.0
    d.rectangle((0, 0, w, h), fill=(58, 16, 52, 255))
    gold = (196, 150, 70, 255)
    dark = (34, 8, 34, 255)
    # Art-deco lattice: diamonds on a 0.5 m grid, dark inlay with gold lines.
    for gy in range(-1, 5):
        for gx in range(0, 3):
            cx, cy = gx * 0.5 * k, (gy * 0.5 + 0.25) * k
            r = 0.2 * k
            d.polygon([(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)], fill=dark)
            r2 = 0.16 * k
            d.polygon([(cx, cy - r2), (cx + r2, cy), (cx, cy + r2), (cx - r2, cy)], outline=gold, width=2)
            d.ellipse((cx - 3, cy - 3, cx + 3, cy + 3), fill=gold)
    # Border along the front edge: a dark band framed by gold lines.
    y0 = h - 0.2 * k
    d.rectangle((0, y0, w, h), fill=dark)
    d.rectangle((0, y0 + 0.03 * k, w, y0 + 0.03 * k + 2), fill=gold)
    d.rectangle((0, h - 0.06 * k, w, h - 0.06 * k + 2), fill=gold)


def draw_front(img, d):
    """Front face details: seams, a vent grille and a stencilled cell code."""
    w, h = img.size
    k = w / 1.0
    for j in range(5):              # vent slots in the lower part of the panel
        y = (0.62 + j * 0.05) * k
        d.rounded_rectangle((0.14 * k, y, 0.42 * k, y + 0.022 * k), radius=3, fill=(10, 10, 16, 255))
    f = pil_font(int(0.07 * k))
    d.text((0.72 * k, 0.72 * k), "F-12", font=f, fill=(150, 160, 180, 255), anchor="mm")


carpet = decal_image("tile_carpet", 256, 512, draw_carpet)
front_art = decal_image("tile_front", 256, 256, draw_front)

CARPET = decal_pbr("carpet", (0.2, 0.05, 0.18), [
    dict(image=carpet, origin=(0, 0, 0.5), size=(1.0, 2.0), u=(1, 0, 0), v=(0, 1, 0), depth=0.02, facing=0.9,
         repeat=False),
], name="tile_carpet", grime=0.3)
BODY = pbr("paint", (0.07, 0.075, 0.1), name="tile_body", wear=0.6, grime=0.7, scale=0.5)
PANEL = decal_pbr("metal", (0.2, 0.21, 0.26), [
    dict(image=front_art, origin=(0, F - 0.03, -0.05), size=(0.86, 0.86), depth=0.01, rough=0.6, emboss=-0.6,
         mode="multiply"),
], name="tile_panel", rough=0.38, grime=0.25, scale=0.25)
BRASS_M = pbr("gold", (0.62, 0.42, 0.14), rough=0.3, name="tile_brass", grime=0.4)
BOLT = pbr("chrome", (0.6, 0.6, 0.65), name="tile_bolt")
PINK = pbr("neon", (0.2, 0.02, 0.18), emit=MAGENTA, strength=2.2, name="tile_neon_pink")
AQUA = pbr("neon", (0.02, 0.15, 0.2), emit=CYAN, strength=1.6, name="tile_neon_cyan")

tile_block(BODY, top=CARPET, chamfer=0.035, name="slab", front_only=True)
# Raised front panel with four bolts.
bm_box((0.86, 0.03, 0.56), (0, F - 0.012, -0.07), PANEL, chamfer=0.012)
for sx in (-1, 1):
    for sz in (-1, 1):
        bolt((sx * 0.37, F - 0.027, -0.07 + sz * 0.22), (0, -1, 0), 0.028, 0.014, BOLT, spin=0.3)
# Brass nosing along the walkable edge (continuous from cell to cell).
bm_box((1.0, 0.06, 0.05), (0, F + 0.02, 0.475), BRASS_M, chamfer=0.012)
# Neon strips: under the nosing and along the bottom, edge to edge.
cube((1.0, 0.02, 0.03), (0, F - 0.004, 0.33), PINK, bevel=0.0)
cube((1.0, 0.02, 0.022), (0, F - 0.004, -0.43), AQUA, bevel=0.0)

finish("tile_floor", body="tile_floor")
tri_report("tile_floor")
export("tile_floor", tex=256)
sheet("tile_floor", views=[(0, 0), (25, 30), (-50, 20), (0, 70)])
