# Backdrop for the bathroom (toilet1): white tiled wall with a cyan tile
# band, a row of sinks under mirrors, urinals, stall doors, a hand dryer,
# soap dispensers, a mop bucket and a "WC" neon. 15 m wide.
#   blender -b --python blender/backdrop_toilet1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
TILE = ((0.80, 0.86, 0.90), 0.25, 0.0)
TILE_BAND = neon((0.3, 0.85, 0.95), 0.6, (0.1, 0.35, 0.42))
STALL = ((0.25, 0.55, 0.65), 0.5, 0.0)

# Tiled wall: big cheap tiles, with a glowing band at eye level.
tile_wall(0.0, 15.0, D + 0.0, 0.0, 1.5, size=0.75, m=TILE)
tile_wall(0.0, 15.0, D + 0.0, 1.5, 2.0, size=0.5, m=TILE_BAND)
tile_wall(0.0, 15.0, D + 0.0, 2.0, 4.5, size=0.75, m=TILE)
tile_wall(0.0, 15.0, D + 0.0, 4.5, 4.75, size=0.25, m=TILE_BAND)
cube((15.0, 0.5, 0.06), (7.5, D - 0.25, 0.03), ((0.55, 0.6, 0.62), 0.6, 0.0), bevel=0.0)  # skirting/floor edge

# Sinks under mirrors, with soap dispensers and a hand dryer.
for i in range(3):
    x = 1.4 + i * 1.3
    sink(x, D - 0.4, 0.0)
    mirror(x, D - 0.02, 2.0, w=0.9, h=1.1, frame=METAL_CHROME)
cube((0.16, 0.12, 0.28), (5.4, D - 0.08, 1.5), (WHITE, 0.4, 0.0), bevel=0.02)
cube((0.08, 0.05, 0.10), (5.4, D - 0.16, 1.4), NEON_CYAN, bevel=0.01)
cube((0.4, 0.3, 0.45), (6.2, D - 0.15, 1.35), ((0.75, 0.78, 0.8), 0.4, 0.7), bevel=0.04)     # hand dryer
cube((0.2, 0.05, 0.05), (6.2, D - 0.33, 1.2), NEON_BLUE, bevel=0.0)
for i in range(2):
    cube((0.12, 0.08, 0.2), (0.6 + i * 0.25, D - 0.06, 2.3), ((0.9, 0.5, 0.2), 0.5, 0.0), bevel=0.02)  # soap bottles

# Urinals and stall doors.
for i in range(3):
    urinal(7.6 + i * 0.9, D - 0.2, 0.0)
    cube((0.05, 0.6, 1.1), (7.15 + i * 0.9, D - 0.3, 0.9), STALL, bevel=0.01)
for i in range(3):
    x = 10.9 + i * 1.3
    cube((1.2, 0.06, 2.0), (x, D - 1.0, 1.25), STALL, bevel=0.02)
    cube((0.05, 0.9, 2.2), (x - 0.62, D - 0.55, 1.35), STALL, bevel=0.01)
    sphere(0.04, (x + 0.45, D - 1.05, 1.15), METAL_CHROME, segments=8, rings=6)
    cube((0.3, 0.02, 0.12), (x, D - 1.04, 2.05), [NEON_GREEN, NEON_RED, NEON_GREEN][i], bevel=0.0)  # vacant/engaged
cube((0.05, 0.9, 2.2), (14.48, D - 0.55, 1.35), STALL, bevel=0.01)
neon_sign("WC", 12.3, D + 0.0, 3.2, NEON_CYAN, cell=0.2, backing=PLASTIC_BLACK)

# Mop bucket, wet floor sign, a roll of paper.
cyl(0.22, 0.4, (14.5, D - 1.3, 0.2), ((0.9, 0.85, 0.2), 0.5, 0.0), verts=12)
rod((14.4, D - 1.3, 0.3), (14.6, D - 1.4, 1.6), 0.02, (WOOD_LIGHT, 0.8, 0.0), verts=6)
cone(0.28, 0.7, (0.6, D - 1.4, 0.35), ((0.95, 0.75, 0.1), 0.6, 0.0), verts=4)
cube((0.2, 0.02, 0.1), (0.6, D - 1.55, 0.35), DARK, bevel=0.0)
cyl(0.12, 0.12, (9.9, D - 0.15, 1.3), (WHITE, 0.6, 0.0), rot=(0, math.pi / 2, 0), verts=12)
pipe_run(0.2, 14.8, D - 0.05, 5.6, r=0.06, m=METAL_CHROME, drops=(1.4, 2.7, 4.0, 7.6, 8.5, 9.4))

# ---- upper wall: more tiles, frosted windows, an extractor and pipe work.
tile_wall(0.0, 15.0, D + 0.0, 7.0, 7.25, size=0.25, m=TILE_BAND)
tile_wall(0.0, 15.0, D + 0.0, 7.25, 9.5, size=0.75, m=TILE)
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
cyl(0.35, 0.12, (14.0, D - 0.05, 7.8), METAL_DARK, rot=(math.pi / 2, 0, 0), verts=16)
for i in range(4):
    cube((0.55, 0.05, 0.03), (14.0, D - 0.12, 7.8), METAL_STEEL, rot=(0, i * 0.785, 0), bevel=0.0)
pipe_run(0.2, 14.8, D - 0.1, 9.2, r=0.08, m=METAL_CHROME, drops=(1.4, 4.0, 10.9, 13.5))
neon_sign("WASH", 0.6, D + 0.0, 7.5, NEON_CYAN, cell=0.12, backing=PLASTIC_BLACK)

join_static("decor")
export("backdrop_toilet1")
