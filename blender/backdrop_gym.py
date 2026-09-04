# Backdrop for the gym: mirrored wall, dumbbell racks, treadmills in a row,
# a punching bag, a "NO PAIN NO GAIN" neon, motivational posters, rubber
# floor mats and a water cooler. Floor-anchored set dressing, 15 m wide.
#   blender -b --python blender/backdrop_gym.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
MINT = neon((0.3, 1.0, 0.75), 2.2, (0.03, 0.12, 0.09))
MAT = ((0.06, 0.09, 0.10), 0.9, 0.0)

wall_panel_lines(0.0, 15.0, D + 0.02, 0.0, 7.0, spacing=1.5)
# Rubber floor mats.
for i in range(5):
    cube((2.8, 1.6, 0.03), (1.6 + i * 3.0, D - 0.9, 0.015), MAT, bevel=0.0)
    cube((2.8, 0.03, 0.02), (1.6 + i * 3.0, D - 0.9, 0.035), MINT, bevel=0.0)

# Left: weight racks and a bench with a barbell.
weight_rack(1.4, D - 0.6, 0.0, w=2.2)
weight_rack(1.4, D - 0.6, 1.3, w=2.2)
cube((0.4, 1.2, 0.08), (3.6, D - 0.9, 0.5), (SLATE, 0.6, 0.3), bevel=0.02)          # bench
for s in (-1, 1):
    cube((0.06, 0.06, 0.45), (3.6, D - 0.9 + s * 0.5, 0.25), METAL_DARK, bevel=0.005)
dumbbell(3.6, D - 1.2, 1.15, length=1.8, r=0.22)                                    # barbell on the rack
for s in (-1, 1):
    cube((0.06, 0.08, 1.15), (3.6 + s * 0.7, D - 1.2, 0.58), METAL_DARK, bevel=0.005)

# Mirror wall with a rail, plus the big neon slogan.
for i in range(4):
    mirror(5.4 + i * 1.15, D + 0.0, 1.55, w=1.1, h=2.2)
rod((4.8, D - 0.05, 1.0), (9.4, D - 0.05, 1.0), 0.03, METAL_CHROME, verts=10)
neon_sign("NO PAIN", 4.8, D + 0.0, 3.4, NEON_PINK, cell=0.17)
neon_sign("NO GAIN", 9.2, D + 0.0, 3.4, MINT, cell=0.17)

# Centre-right: treadmills and an exercise bike silhouette.
treadmill_silhouette(10.3, D - 1.0, 0.0)
treadmill_silhouette(12.2, D - 1.0, 0.0)
# Bike.
rod((14.0, D - 1.0, 0.35), (14.4, D - 1.0, 1.1), 0.04, METAL_DARK, verts=8)
rod((14.0, D - 1.0, 0.35), (13.5, D - 1.0, 0.9), 0.04, METAL_DARK, verts=8)
torus(0.28, 0.04, (13.5, D - 1.0, 0.3), METAL_DARK, rot=(math.pi / 2, 0, 0))
torus(0.28, 0.04, (14.5, D - 1.0, 0.3), METAL_DARK, rot=(math.pi / 2, 0, 0))
cube((0.3, 0.2, 0.06), (13.55, D - 1.0, 0.95), PLASTIC_BLACK, bevel=0.02)
cube((0.5, 0.05, 0.3), (14.4, D - 1.0, 1.25), (SLATE, 0.5, 0.4), bevel=0.02)
cube((0.4, 0.02, 0.2), (14.4, D - 1.04, 1.25), SCREEN_CYAN, bevel=0.0)

# Posters and a wall TV.
poster(10.6, D + 0.0, 2.4, w=0.9, h=1.3, face=neon((1.0, 0.5, 0.1), 1.0, (0.25, 0.1, 0.02)))
poster(11.8, D + 0.0, 2.4, w=0.9, h=1.3, face=neon((0.2, 0.7, 1.0), 1.0, (0.03, 0.12, 0.25)))
monitor(13.6, D + 0.0, 2.6, w=1.6, h=0.95, screen=SCREEN_CYAN, stand=False)
exit_sign(0.5, D + 0.0, 4.8)

# Water cooler and a towel shelf.
cyl(0.18, 0.9, (0.55, D - 0.5, 0.45), (SLATE, 0.5, 0.4), verts=12)
cyl(0.16, 0.5, (0.55, D - 0.5, 1.15), ((0.3, 0.7, 0.9), 0.1, 0.0), verts=12)
shelf(2.4, D - 0.4, 2.6, w=2.2)
for i in range(4):
    cube((0.35, 0.3, 0.14), (1.6 + i * 0.5, D - 0.25, 2.68), [(WHITE, 0.9, 0.0), ((0.9, 0.3, 0.5), 0.9, 0.0)][i % 2], bevel=0.04)

# ---- upper wall: scoreboard, basketball hoop, banners and high windows.
cube((3.2, 0.12, 1.2), (7.5, D + 0.0, 8.2), PLASTIC_BLACK, bevel=0.03)
neon_sign("24 07", 6.2, D - 0.07, 7.9, NEON_RED, cell=0.12, gap=0.4)
cube((2.8, 0.03, 0.05), (7.5, D - 0.07, 8.72), MINT, bevel=0.0)
cube((0.12, 0.12, 1.2), (2.6, D + 0.0, 7.6), METAL_STEEL, bevel=0.01)
cube((1.4, 0.06, 1.0), (2.6, D + 0.0, 8.6), (WHITE, 0.6, 0.0), bevel=0.02)
torus(0.28, 0.025, (2.6, D - 0.35, 8.15), NEON_ORANGE, major_segments=20)
for i in range(8):
    a = i / 8.0 * math.tau
    rod((2.6 + math.cos(a) * 0.28, D - 0.35 + math.sin(a) * 0.28, 8.15), (2.6 + math.cos(a) * 0.1, D - 0.35 + math.sin(a) * 0.1, 7.75), 0.008, (WHITE, 0.6, 0.0), verts=4)
for i, c in enumerate([NEON_PINK, MINT, NEON_YELLOW]):
    cube((0.9, 0.04, 1.6), (10.6 + i * 1.3, D + 0.0, 8.3), c, bevel=0.02)
    cube((0.9, 0.05, 0.08), (10.6 + i * 1.3, D - 0.02, 9.12), METAL_DARK, bevel=0.0)
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
wall_panel_lines(0.0, 15.0, D + 0.02, 7.0, 9.5, spacing=1.5)

join_static("decor")
export("backdrop_gym")
