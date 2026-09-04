# Backdrop for the hotel bedroom (room1): a big window on the neon city,
# a made bed with a headboard, bedside lamps, a wardrobe, a mini bar,
# a framed print, a coat rack and a room number sign. 15 m wide.
#   blender -b --python blender/backdrop_room1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
CARPET = ((0.18, 0.10, 0.30), 0.95, 0.0)
LAMP = neon((1.0, 0.8, 0.5), 1.6, (0.4, 0.3, 0.18))
WALLPAPER = ((0.25, 0.15, 0.40), 0.9, 0.0)

# Wallpaper stripes and the picture rail.
for i in range(15):
    cube((0.5, 0.03, 6.8), (0.5 + i * 1.0, D + 0.015, 3.4), WALLPAPER, bevel=0.0)
cube((15.0, 0.06, 0.06), (7.5, D + 0.0, 2.6), METAL_BRASS, bevel=0.005)
cube((6.0, 4.0, 0.03), (7.5, D - 1.0, 0.015), CARPET, bevel=0.0)

# Window with curtains.
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
for s in (-1, 1):
    cube((0.6, 0.25, 3.0), (3.6 + s * 2.05, D - 0.15, 3.3), ((0.5, 0.08, 0.18), 0.9, 0.0), bevel=0.06)
rod((1.2, D - 0.2, 4.85), (6.0, D - 0.2, 4.85), 0.025, METAL_BRASS, verts=8)

# Bed with a headboard, pillows and lamps on nightstands.
bed_flat(8.2, D - 1.6, 0.0, w=2.8, d=1.6, m=((0.30, 0.10, 0.35), 0.9, 0.0), sheet=((0.95, 0.9, 0.85), 0.9, 0.0), frame=(WOOD, 0.7, 0.0))
cube((3.2, 0.14, 1.4), (8.2, D - 0.07, 1.0), ((0.35, 0.18, 0.08), 0.8, 0.0), bevel=0.04)
for i in range(4):
    cube((0.7, 0.10, 0.4), (7.2 + (i % 2) * 2.0, D - 0.16, 0.9 + (i // 2) * 0.45), ((0.35, 0.18, 0.08), 0.8, 0.0), bevel=0.05)
for s in (-1, 1):
    x = 8.2 + s * 2.0
    cube((0.6, 0.5, 0.6), (x, D - 0.3, 0.3), (WOOD, 0.7, 0.0), bevel=0.02)
    cyl(0.03, 0.35, (x, D - 0.3, 0.78), METAL_BRASS, verts=8)
    cyl(0.2, 0.25, (x, D - 0.3, 1.05), LAMP, r2=0.14, verts=12)
cube((0.4, 0.3, 0.02), (6.2, D - 0.3, 0.61), (WHITE, 0.6, 0.0), bevel=0.0)   # book
cyl(0.06, 0.16, (10.4, D - 0.35, 0.69), GLASS, verts=8)                       # water glass

# Wardrobe, mini bar with a kettle, a framed print and coat rack.
cube((1.6, 0.6, 2.6), (12.2, D - 0.3, 1.3), (WOOD, 0.7, 0.0), bevel=0.03)
cube((0.03, 0.02, 2.4), (12.2, D - 0.61, 1.3), METAL_BRASS, bevel=0.0)
for s in (-1, 1):
    cube((0.04, 0.05, 0.3), (12.2 + s * 0.12, D - 0.63, 1.3), METAL_BRASS, bevel=0.005)
cube((1.0, 0.6, 0.9), (14.0, D - 0.3, 0.45), (SLATE, 0.5, 0.3), bevel=0.02)
cube((0.6, 0.02, 0.5), (14.0, D - 0.61, 0.45), neon((0.3, 0.8, 1.0), 0.8, (0.05, 0.15, 0.25)), bevel=0.0)
cyl(0.12, 0.22, (13.8, D - 0.3, 1.01), METAL_CHROME, verts=10)
cube((0.4, 0.3, 0.06), (14.3, D - 0.3, 0.93), (SLATE, 0.5, 0.3), bevel=0.01)
for i in range(2):
    cyl(0.05, 0.08, (14.2 + i * 0.2, D - 0.3, 1.0), (WHITE, 0.3, 0.0), verts=8)
framed_picture(13.0, D + 0.0, 3.4, w=1.4, h=1.0, frame=(WOOD, 0.7, 0.0), face=neon((0.9, 0.5, 0.2), 0.7, (0.3, 0.15, 0.05)))
framed_picture(1.0, D + 0.0, 3.6, w=0.9, h=1.2, frame=(WOOD, 0.7, 0.0), face=neon((0.2, 0.5, 0.9), 0.7, (0.05, 0.12, 0.25)))
rod((1.0, D - 0.4, 0.0), (1.0, D - 0.4, 1.9), 0.03, METAL_BRASS, verts=8)
for a in range(4):
    ang = a * math.pi / 2
    rod((1.0, D - 0.4, 1.85), (1.0 + math.cos(ang) * 0.25, D - 0.4 + math.sin(ang) * 0.25, 1.95), 0.015, METAL_BRASS, verts=6)
cube((0.3, 0.12, 0.8), (1.18, D - 0.5, 1.45), ((0.5, 0.08, 0.18), 0.9, 0.0), bevel=0.04)
neon_sign("4 2 7", 5.6, D + 0.0, 5.4, neon((1.0, 0.75, 0.3), 2.5), cell=0.14, gap=0.3, backing=PLASTIC_BLACK)
pipe_run(0.2, 14.8, D - 0.15, 6.4, r=0.07, drops=(2.5, 9.0))

# ---- upper wall: high windows with curtains, an AC unit and the exposed pipes.
for x in (3.6, 11.4):
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
    for s in (-1, 1):
        cube((0.5, 0.22, 2.4), (x + s * 1.8, D - 0.12, 8.4), ((0.5, 0.08, 0.18), 0.9, 0.0), bevel=0.06)
cube((1.6, 0.5, 0.7), (7.5, D - 0.25, 8.9), (WHITE, 0.5, 0.2), bevel=0.04)
for i in range(6):
    cube((1.4, 0.04, 0.03), (7.5, D - 0.52, 8.62 + i * 0.1), (SLATE, 0.5, 0.3), bevel=0.0)
cube((0.16, 0.03, 0.05), (8.1, D - 0.52, 9.2), NEON_GREEN, bevel=0.0)
pipe_run(0.2, 14.8, D - 0.2, 7.5, r=0.07, m=METAL_STEEL, drops=(7.5,))
for i in range(15):
    cube((0.5, 0.03, 2.5), (0.5 + i * 1.0, D + 0.015, 8.25), WALLPAPER, bevel=0.0)
cube((15.0, 0.06, 0.06), (7.5, D + 0.0, 9.45), METAL_BRASS, bevel=0.005)

join_static("decor")
export("backdrop_room1")
