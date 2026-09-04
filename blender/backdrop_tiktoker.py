# Backdrop for the influencer studio (tiktoker): a pink LED-lit wall of
# shelves and vinyl, a ring light and phone tripod aimed at a plush bed,
# a "LIVE" sign, a wardrobe rail full of clothes, heart balloons and a
# neon cloud. 15 m wide, floor-anchored.
#   blender -b --python blender/backdrop_tiktoker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
PLUSH = ((0.85, 0.35, 0.55), 0.9, 0.0)
PINK_M = neon((1.0, 0.35, 0.7), 2.0, (0.3, 0.08, 0.2))
BALLOON = [((0.9, 0.2, 0.4), 0.3, 0.0), ((1.0, 0.7, 0.1), 0.3, 0.0), ((0.3, 0.6, 1.0), 0.3, 0.0)]

wall_panel_lines(0.0, 15.0, D + 0.02, 0.0, 7.0, spacing=1.4)
# LED strips framing the whole wall.
led_strip(0.2, 14.8, D + 0.0, 0.25, m=NEON_PINK)
led_strip(0.2, 14.8, D + 0.0, 5.6, m=NEON_PINK)
for x in (0.2, 14.8):
    rod((x, D + 0.0, 0.25), (x, D + 0.0, 5.6), 0.02, NEON_PINK, verts=6)

# Left: shelves with records, plants and a vinyl player.
for z in (1.3, 2.1, 2.9):
    shelf(2.0, D - 0.4, z, w=3.2)
for i in range(14):
    cube((0.03, 0.3, 0.3), (0.6 + i * 0.2, D - 0.2, 1.47), [((0.1, 0.1, 0.12), 0.6, 0.0), ((0.8, 0.2, 0.3), 0.6, 0.0), ((0.9, 0.85, 0.7), 0.6, 0.0)][i % 3], bevel=0.0)
cube((0.5, 0.35, 0.12), (1.0, D - 0.25, 2.16), (SLATE, 0.5, 0.3), bevel=0.02)
cyl(0.16, 0.01, (1.0, D - 0.25, 2.23), PLASTIC_BLACK, verts=16)
plant(2.4, D - 0.25, 2.12, size=0.6)
plant(3.2, D - 0.25, 2.92, size=0.5)
for i in range(5):
    cyl(0.05, 0.16 + (i % 2) * 0.05, (1.2 + i * 0.35, D - 0.25, 3.0), [PINK_M, ((0.9, 0.9, 0.95), 0.3, 0.0), NEON_CYAN][i % 3], verts=8)
neon_sign("LIVE", 0.8, D + 0.0, 4.3, NEON_RED, cell=0.18, backing=PLASTIC_BLACK)
sphere(0.1, (2.9, D + 0.0, 4.65), NEON_RED, segments=8, rings=6)

# Centre: bed with pillows facing the ring light and tripod.
bed_flat(7.0, D - 1.7, 0.0, w=2.6, d=1.5, m=PLUSH, sheet=(WHITE, 0.9, 0.0))
for i in range(3):
    sphere(0.22, (6.2 + i * 0.5, D - 0.6, 0.78), [PINK_M, (WHITE, 0.9, 0.0), ((0.6, 0.3, 0.9), 0.9, 0.0)][i], scale=(1.2, 0.8, 0.9), segments=8, rings=6)
ring_light(9.6, D - 1.4, 0.0)
phone_tripod(10.4, D - 1.4, 0.0)
# Neon cloud and lightning above the bed.
for i, (x, r) in enumerate([(6.0, 0.35), (6.5, 0.5), (7.1, 0.45), (7.6, 0.32)]):
    torus(r, 0.03, (x, D + 0.0, 3.2 + (i % 2) * 0.15), NEON_CYAN, rot=(math.pi / 2, 0, 0), major_segments=20)
cube((1.9, 0.05, 0.06), (6.8, D + 0.0, 2.85), NEON_CYAN, bevel=0.0)
rod((7.3, D + 0.0, 2.8), (7.05, D + 0.0, 2.35), 0.025, NEON_YELLOW, verts=6)
rod((7.05, D + 0.0, 2.35), (7.35, D + 0.0, 2.35), 0.025, NEON_YELLOW, verts=6)
rod((7.35, D + 0.0, 2.35), (7.0, D + 0.0, 1.8), 0.025, NEON_YELLOW, verts=6)
# Balloons.
for i in range(6):
    x = 4.4 + i * 0.35 + (i % 2) * 0.3
    z = 2.0 + (i % 3) * 0.35
    sphere(0.22, (x, D - 0.4, z), BALLOON[i % 3], scale=(1, 1, 1.15), segments=10, rings=8)
    rod((x, D - 0.4, z - 0.25), (x + 0.1, D - 0.4, 0.05), 0.006, (WHITE, 0.5, 0.0), verts=4)

# Right: wardrobe rail with clothes, a vanity mirror with bulbs, a beauty desk.
rod((11.2, D - 0.5, 2.3), (14.6, D - 0.5, 2.3), 0.03, METAL_CHROME, verts=8)
for s in (11.2, 14.6):
    rod((s, D - 0.5, 0.0), (s, D - 0.5, 2.3), 0.03, METAL_CHROME, verts=8)
for i in range(9):
    x = 11.5 + i * 0.37
    c = [((0.9, 0.3, 0.5), 0.8, 0.0), ((0.2, 0.2, 0.25), 0.8, 0.0), ((0.95, 0.9, 0.85), 0.8, 0.0), ((0.4, 0.2, 0.7), 0.8, 0.0), ((0.1, 0.5, 0.6), 0.8, 0.0)][i % 5]
    cube((0.28, 0.12, 0.9 + (i % 3) * 0.25), (x, D - 0.5, 1.75 - (i % 3) * 0.12), c, bevel=0.04)
    rod((x, D - 0.5, 2.3), (x, D - 0.5, 2.2), 0.01, METAL_CHROME, verts=4)
desk(13.0, D - 1.2, 0.0, w=1.9, d=0.6, m=((0.95, 0.85, 0.9), 0.5, 0.0), legs=METAL_CHROME)
mirror(13.0, D - 0.45, 4.1, w=1.5, h=1.6, frame=METAL_CHROME)
for i in range(6):
    sphere(0.06, (12.3 + i * 0.28, D - 0.5, 4.95), NEON_YELLOW, segments=8, rings=6)
    sphere(0.06, (12.3 + i * 0.28, D - 0.5, 3.25), NEON_YELLOW, segments=8, rings=6)
for i in range(5):
    cyl(0.035, 0.12 + (i % 3) * 0.05, (12.3 + i * 0.22, D - 1.35, 0.84), [PINK_M, METAL_GOLD, (WHITE, 0.3, 0.0)][i % 3], verts=8)

# ---- upper wall: a giant neon heart, a "SUBSCRIBE" sign and floating shelves.
for i, (x, z) in enumerate([(3.0, 8.1), (3.3, 8.5), (2.7, 8.5)]):
    torus(0.42 if i else 0.0001, 0.035, (x, D + 0.0, z), NEON_PINK, rot=(math.pi / 2, 0, 0), major_segments=24)
rod((2.25, D + 0.0, 8.35), (3.0, D + 0.0, 7.4), 0.035, NEON_PINK, verts=8)
rod((3.75, D + 0.0, 8.35), (3.0, D + 0.0, 7.4), 0.035, NEON_PINK, verts=8)
neon_sign("SUBSCRIBE", 5.2, D + 0.0, 7.9, NEON_CYAN, cell=0.15, backing=PLASTIC_BLACK)
for z in (7.4, 8.4):
    shelf(12.5, D - 0.3, z, w=3.0, m=(WHITE, 0.6, 0.0))
for i in range(6):
    sphere(0.16, (11.3 + i * 0.5, D - 0.15, 7.6), [NEON_PINK, NEON_YELLOW, NEON_CYAN][i % 3], scale=(1, 1, 1.2), segments=8, rings=6)
for i in range(4):
    cube((0.5, 0.25, 0.4), (11.4 + i * 0.75, D - 0.15, 8.62), [((0.9, 0.9, 0.95), 0.4, 0.0), ((0.9, 0.3, 0.5), 0.4, 0.0)][i % 2], bevel=0.04)
led_strip(0.2, 14.8, D + 0.0, 9.3, m=NEON_PINK)

join_static("decor")
export("backdrop_tiktoker")
