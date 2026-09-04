# Backdrop for the penthouse lounge (rich1): marble columns, a long window
# onto the neon skyline, gold-framed paintings, a velvet sofa on a rug, a
# bookshelf, a fireplace with a glowing hearth and a bar cart.
#   blender -b --python blender/backdrop_rich1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
VELVET = ((0.35, 0.05, 0.12), 0.85, 0.0)
MARBLE = ((0.80, 0.78, 0.72), 0.35, 0.0)
EMBER = neon((1.0, 0.45, 0.1), 3.0, (0.3, 0.1, 0.02))

# Wainscoting: a gold rail with dark panels below it.
cube((15.0, 0.05, 0.06), (7.5, D + 0.0, 1.2), METAL_GOLD, bevel=0.005)
for i in range(10):
    cube((1.2, 0.04, 0.9), (0.9 + i * 1.5, D + 0.01, 0.62), ((0.10, 0.05, 0.04), 0.7, 0.0), bevel=0.01)
    cube((1.05, 0.02, 0.75), (0.9 + i * 1.5, D - 0.01, 0.62), ((0.14, 0.07, 0.05), 0.7, 0.0), bevel=0.005)
column(0.6, D - 0.3, 0.0, h=6.6, r=0.3, m=MARBLE)
column(14.4, D - 0.3, 0.0, h=6.6, r=0.3, m=MARBLE)
column(7.5, D - 0.3, 0.0, h=6.6, r=0.25, m=MARBLE)

# Window wall with the skyline.
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
framed_picture(10.0, D + 0.0, 3.3, w=1.6, h=1.2, face=neon((0.9, 0.3, 0.6), 0.8, (0.3, 0.08, 0.2)))
framed_picture(12.2, D + 0.0, 3.5, w=1.2, h=1.6, face=neon((0.2, 0.6, 1.0), 0.8, (0.05, 0.15, 0.3)))
framed_picture(1.8, D + 0.0, 3.9, w=1.4, h=1.0, face=neon((1.0, 0.8, 0.3), 0.7, (0.3, 0.22, 0.05)))
# Sconces.
for x in (2.7, 8.8, 13.3):
    cube((0.16, 0.16, 0.3), (x, D - 0.08, 2.6), METAL_GOLD, bevel=0.03)
    sphere(0.09, (x, D - 0.16, 2.82), NEON_YELLOW, segments=10, rings=8)

# Sofa on a rug, coffee table, lamp.
rug(4.6, D - 1.0, 0.0, w=4.2, d=1.7)
sofa(4.6, D - 1.1, 0.0, w=2.6, m=VELVET)
cube((1.1, 0.6, 0.04), (4.6, D - 1.55, 0.42), ((0.05, 0.05, 0.08), 0.1, 0.0), bevel=0.01)   # glass table top
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((4.6 + sx * 0.5, D - 1.55 + sy * 0.25, 0.0), (4.6 + sx * 0.5, D - 1.55 + sy * 0.25, 0.4), 0.02, METAL_GOLD, verts=6)
cyl(0.04, 1.5, (6.6, D - 1.0, 0.75), METAL_GOLD, verts=8)
cyl(0.28, 0.35, (6.6, D - 1.0, 1.65), neon((1.0, 0.85, 0.5), 1.2, (0.35, 0.28, 0.15)), r2=0.22, verts=14)

# Fireplace with a glowing hearth and a mantel.
cube((2.0, 0.5, 1.5), (9.9, D - 0.25, 0.75), MARBLE, bevel=0.03)
cube((1.2, 0.3, 1.0), (9.9, D - 0.45, 0.55), DARK, bevel=0.02)
for i in range(3):
    cyl(0.08, 0.5, (9.6 + i * 0.3, D - 0.55, 0.2 + (i % 2) * 0.1), (WOOD, 0.9, 0.0), rot=(0, 0.4 * (i - 1), 0.3), verts=8)
sphere(0.25, (9.9, D - 0.6, 0.3), EMBER, scale=(1.6, 0.8, 0.9), segments=10, rings=8)
cube((2.3, 0.6, 0.1), (9.9, D - 0.3, 1.55), METAL_GOLD, bevel=0.02)
cyl(0.12, 0.35, (9.3, D - 0.35, 1.78), METAL_GOLD, verts=10)                                    # trophy
sphere(0.16, (9.3, D - 0.35, 2.05), METAL_GOLD, segments=10, rings=8)
cube((0.5, 0.25, 0.4), (10.5, D - 0.35, 1.8), ((0.12, 0.06, 0.04), 0.7, 0.0), bevel=0.02)       # clock box
wall_clock(10.5, D - 0.48, 1.8, r=0.16)

# Bookshelf and a bar cart.
bookshelf(12.6, D - 0.4, 0.0, w=1.8, h=2.6)
cube((0.9, 0.5, 0.04), (1.9, D - 1.0, 0.75), METAL_GOLD, bevel=0.01)
cube((0.9, 0.5, 0.04), (1.9, D - 1.0, 0.3), METAL_GOLD, bevel=0.01)
for sx in (-1, 1):
    rod((1.9 + sx * 0.42, D - 1.0, 0.05), (1.9 + sx * 0.42, D - 1.0, 0.8), 0.015, METAL_GOLD, verts=6)
for i in range(4):
    cyl(0.05, 0.32, (1.6 + i * 0.2, D - 1.05, 0.93), [((0.1, 0.4, 0.2), 0.1, 0.0), ((0.5, 0.3, 0.05), 0.1, 0.0), ((0.4, 0.05, 0.05), 0.1, 0.0), GLASS][i], verts=8)
plant(14.2, D - 1.1, 0.0, size=1.3)

# ---- upper wall: a mezzanine rail, tall windows and a huge portrait.
cube((15.0, 0.08, 0.10), (7.5, D + 0.0, 7.05), METAL_GOLD, bevel=0.01)
for i in range(38):
    rod((0.2 + i * 0.4, D - 0.05, 7.1), (0.2 + i * 0.4, D - 0.05, 7.9), 0.02, METAL_GOLD, verts=6)
cube((15.0, 0.08, 0.06), (7.5, D - 0.05, 7.92), METAL_GOLD, bevel=0.01)
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
framed_picture(7.5, D + 0.0, 8.7, w=3.4, h=1.6, face=neon((0.9, 0.5, 0.9), 0.8, (0.3, 0.12, 0.3)))
sphere(0.5, (7.5, D - 0.06, 8.7), neon((1.0, 0.85, 0.6), 1.5, (0.4, 0.3, 0.2)), scale=(0.7, 0.2, 0.9), segments=10, rings=8)
for x in (4.9, 10.1):
    cube((0.16, 0.16, 0.3), (x, D - 0.08, 8.5), METAL_GOLD, bevel=0.03)
    sphere(0.09, (x, D - 0.16, 8.72), NEON_YELLOW, segments=10, rings=8)

join_static("decor")
export("backdrop_rich1")
