# The skybridge between two towers: a 48 m open-air deck with glass
# parapets, neon gate arches, lamp posts, holo-ads and, at the far end,
# the lit facade and doorway of the next building. Origin: x=0 at the
# first deck cell, z=0 at the deck top, +Y deeper into the scene.
#   blender -b --python blender/skybridge.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import neon_sign  # noqa: F401

clean_scene()
L = 48.0
FACADE = ((0.05, 0.03, 0.09), 0.7, 0.2)
GLASS_P = ((0.3, 0.7, 0.9), 0.1, 0.0)
POST = (GUNMETAL, 0.4, 0.8)
HOT = neon(PINK, 4.0)
ICE = neon(CYAN, 3.5)
LAV = neon(VIOLET, 3.0)
SUNNY = neon(YELLOW, 3.0)
WIN = neon((1.0, 0.55, 0.85), 1.4, (0.35, 0.12, 0.3))
WIN2 = neon((0.4, 0.9, 1.0), 1.4, (0.1, 0.3, 0.35))

# Parapets: a low glass panel at the front, a taller one at the back, both
# capped with a neon tube and held by posts every 2 m.
for y, h, m in ((-1.15, 0.85, GLASS_P), (1.15, 1.35, GLASS_P)):
    cube((L, 0.04, h), (L / 2, y, h / 2), m, bevel=0.0)
    rod((0.0, y, h + 0.03), (L, y, h + 0.03), 0.035, HOT if y > 0 else ICE, verts=6)
    for i in range(int(L / 2) + 1):
        cube((0.08, 0.10, h + 0.08), (i * 2.0, y, (h + 0.08) / 2), POST, bevel=0.0)
# Deck edge trim under the cells (the cells themselves come from the game).
for y in (-1.02, 1.02):
    rod((0.0, y, -0.05), (L, y, -0.05), 0.05, POST, verts=6)
    rod((0.0, y, -0.55), (L, y, -0.55), 0.03, LAV, verts=6)
# Under-deck trusses.
for i in range(int(L / 4)):
    x = i * 4.0 + 2.0
    rod((x - 1.6, -1.0, -0.2), (x + 1.6, 1.0, -1.4), 0.05, POST, verts=5)
    rod((x + 1.6, -1.0, -0.2), (x - 1.6, 1.0, -1.4), 0.05, POST, verts=5)
    rod((x, -1.0, -1.5), (x, 1.0, -1.5), 0.06, POST, verts=5)

# Gate arches every 8 m: two posts and a lintel wrapped in neon.
for i in range(6):
    x = 4.0 + i * 8.0
    for y in (-1.3, 1.3):
        cube((0.22, 0.22, 4.4), (x, y, 2.2), POST, bevel=0.01)
        rod((x, y, 0.1), (x, y, 4.3), 0.03, HOT if i % 2 else ICE, verts=6)
    cube((0.3, 2.9, 0.3), (x, 0.0, 4.55), POST, bevel=0.01)
    rod((x, -1.4, 4.75), (x, 1.4, 4.75), 0.035, HOT if i % 2 else ICE, verts=6)
    # a chevron pointing onward on the lintel
    rod((x - 0.35, -0.1, 4.4), (x, -0.1, 4.7), 0.02, SUNNY, verts=5)
    rod((x, -0.1, 4.7), (x - 0.35, -0.1, 5.0), 0.02, SUNNY, verts=5)

# Lamp posts on the back rail with glowing globes, holo-ad panels between.
for i in range(8):
    x = 2.0 + i * 6.0
    rod((x, 1.25, 1.3), (x, 1.25, 3.4), 0.05, POST, verts=6)
    rod((x, 1.25, 3.4), (x, 0.6, 3.6), 0.04, POST, verts=6)
    sphere(0.22, (x, 0.55, 3.55), LAV if i % 2 else SUNNY, segments=8, rings=6)
for i in range(4):
    x = 9.0 + i * 12.0
    cube((2.0, 0.06, 1.1), (x, 1.5, 2.6), PLASTIC_BLACK, bevel=0.0)
    cube((1.86, 0.02, 0.96), (x, 1.46, 2.6), anim([WIN, WIN2, neon((0.5, 1.0, 0.6), 1.4, (0.1, 0.35, 0.15)), WIN][i], "screen"), bevel=0.0)

# The far tower: a dark facade with lit windows and a glowing doorway.
FX = L + 0.5
cube((6.0, 4.0, 14.0), (FX + 3.0, 1.0, 5.0), FACADE, bevel=0.0)          # the tower's bulk, behind the door plane
cube((6.0, 0.6, 8.0), (FX + 3.0, -1.6, 8.0), FACADE, bevel=0.0)          # front face above the door
cube((1.6, 0.6, 4.0), (FX + 0.8, -1.6, 2.0), FACADE, bevel=0.0)          # left jamb
cube((1.8, 0.6, 4.0), (FX + 5.1, -1.6, 2.0), FACADE, bevel=0.0)          # right jamb
cube((0.9, 0.06, 3.9), (FX + 3.2, -1.3, 1.95), neon((1.0, 0.6, 0.9), 2.2, (0.6, 0.2, 0.5)), bevel=0.0)   # lit doorway
rod((FX + 2.0, -1.95, 0.0), (FX + 2.0, -1.95, 4.1), 0.035, HOT, verts=6)
rod((FX + 4.4, -1.95, 0.0), (FX + 4.4, -1.95, 4.1), 0.035, HOT, verts=6)
rod((FX + 2.0, -1.95, 4.1), (FX + 4.4, -1.95, 4.1), 0.035, HOT, verts=6)
for r in range(6):
    for c in range(3):
        cube((0.7, 0.04, 0.5), (FX + 1.3 + c * 1.1, -1.92, 5.2 + r * 1.1), [WIN, WIN2, PLASTIC_BLACK][(r * 3 + c * 5) % 3], bevel=0.0)
neon_sign("LOBBY", FX + 1.1, -1.95, 4.6, ICE, cell=0.13, gap=0.4, backing=PLASTIC_BLACK)
# Awning over the door and a mat.
cube((3.2, 1.6, 0.08), (FX + 3.2, -2.6, 4.2), ((0.6, 0.08, 0.3), 0.6, 0.0), bevel=0.0)
rod((FX + 1.7, -3.35, 4.2), (FX + 1.7, -3.35, 3.5), 0.03, POST, verts=5)
rod((FX + 4.7, -3.35, 4.2), (FX + 4.7, -3.35, 3.5), 0.03, POST, verts=5)

# Portal frame around the doorway in the first tower's wall (x < 0).
rod((-0.05, -1.1, 0.0), (-0.05, -1.1, 3.2), 0.04, ICE, verts=6)
rod((-0.05, 1.1, 0.0), (-0.05, 1.1, 3.2), 0.04, ICE, verts=6)
rod((-0.05, -1.1, 3.2), (-0.05, 1.1, 3.2), 0.04, ICE, verts=6)
neon_sign("EXIT", -0.05, -0.95, 3.5, HOT, cell=0.1, gap=0.4)

join_static("decor")
export("skybridge")
