# Backdrop for the casino: a wall of slot machines, a roulette table, a
# card table with chips, a cashier cage, a "JACKPOT" neon, gold columns,
# a red carpet and a chandelier-lit upper gallery. 15 m wide, floor-anchored.
#   blender -b --python blender/backdrop_casino.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
FELT = ((0.05, 0.3, 0.12), 0.9, 0.0)
RED_CARPET = ((0.45, 0.04, 0.06), 0.95, 0.0)
CHIP = [((0.8, 0.1, 0.1), 0.4, 0.0), ((0.1, 0.3, 0.8), 0.4, 0.0), ((0.9, 0.9, 0.9), 0.4, 0.0), ((0.1, 0.1, 0.1), 0.4, 0.0)]


def slot(x, y, z, k):
    cube((0.8, 0.7, 1.7), (x, y + 0.35, z + 0.85), ((0.15, 0.05, 0.2), 0.4, 0.4), bevel=0.03)
    cube((0.8, 0.5, 0.45), (x, y + 0.25, z + 1.9), ((0.15, 0.05, 0.2), 0.4, 0.4), bevel=0.03)
    cube((0.7, 0.02, 0.28), (x, y - 0.01, z + 1.9), [NEON_YELLOW, NEON_PINK, NEON_CYAN][k % 3], bevel=0.0)
    cube((0.62, 0.03, 0.34), (x, y - 0.02, z + 1.3), PLASTIC_BLACK, bevel=0.0)
    for j in range(3):
        cube((0.16, 0.02, 0.26), (x - 0.2 + j * 0.2, y - 0.04, z + 1.3), [neon((1.0, 0.9, 0.9), 0.8, (0.4, 0.35, 0.3)), neon((1.0, 0.5, 0.5), 0.8, (0.4, 0.15, 0.15))][(j + k) % 2], bevel=0.0)
        cube((0.1, 0.01, 0.08), (x - 0.2 + j * 0.2, y - 0.05, z + 1.3), [NEON_RED, NEON_YELLOW, NEON_GREEN][(j * 2 + k) % 3], bevel=0.0)
    cube((0.7, 0.3, 0.06), (x, y + 0.1, z + 0.9), METAL_GOLD, bevel=0.01)
    sphere(0.04, (x + 0.15, y - 0.02, z + 0.94), NEON_RED, segments=6, rings=4)
    rod((x + 0.44, y + 0.3, z + 1.1), (x + 0.5, y + 0.3, z + 1.55), 0.02, METAL_CHROME, verts=5)
    sphere(0.06, (x + 0.5, y + 0.3, z + 1.58), ((0.8, 0.05, 0.05), 0.3, 0.0), segments=6, rings=4)
    for i in range(8):
        sphere(0.025, (x - 0.35 + i * 0.1, y - 0.01, z + 2.16), NEON_YELLOW if (i + k) % 2 else NEON_WHITE, segments=5, rings=4)


cube((15.0, 1.9, 0.02), (7.5, 0.95, 0.01), RED_CARPET, bevel=0.0)
for i in range(15):
    cube((0.9, 1.9, 0.005), (0.5 + i * 1.0, 0.95, 0.025), ((0.55, 0.06, 0.08), 0.95, 0.0), bevel=0.0) if i % 2 else None
cube((15.0, 0.06, 0.08), (7.5, D + 0.0, 1.35), METAL_GOLD, bevel=0.005)
for i in range(11):
    cube((1.1, 0.04, 1.1), (0.75 + i * 1.4, D + 0.01, 0.7), ((0.25, 0.04, 0.10), 0.7, 0.0), bevel=0.01)
column(0.5, D - 0.3, 0.0, h=7.5, r=0.3, m=((0.85, 0.75, 0.55), 0.35, 0.0))
column(14.5, D - 0.3, 0.0, h=7.5, r=0.3, m=((0.85, 0.75, 0.55), 0.35, 0.0))

# Slots along the left wall.
for i in range(5):
    slot(1.4 + i * 0.95, D - 0.7, 0.0, i)
# Roulette table.
cube((2.6, 1.3, 0.85), (8.0, D - 1.0, 0.43), ((0.3, 0.15, 0.06), 0.7, 0.0), bevel=0.04)
cube((2.5, 1.2, 0.03), (8.0, D - 1.0, 0.87), FELT, bevel=0.0)
cyl(0.55, 0.12, (7.2, D - 1.0, 0.94), ((0.3, 0.15, 0.06), 0.7, 0.0), verts=20)
cyl(0.45, 0.06, (7.2, D - 1.0, 1.0), ((0.05, 0.05, 0.05), 0.4, 0.3), verts=20)
for i in range(18):
    a = i / 18.0 * math.tau
    cube((0.12, 0.06, 0.02), (7.2 + math.cos(a) * 0.35, D - 1.0 + math.sin(a) * 0.35, 1.03), [((0.8, 0.05, 0.05), 0.4, 0.0), ((0.05, 0.05, 0.05), 0.4, 0.0)][i % 2], rot=(0, 0, a), bevel=0.0)
sphere(0.04, (7.4, D - 0.8, 1.06), (WHITE, 0.2, 0.0), segments=6, rings=4)
for r in range(3):
    for c in range(4):
        cube((0.2, 0.2, 0.02), (8.2 + c * 0.24, D - 1.35 + r * 0.24, 0.9), [((0.8, 0.05, 0.05), 0.9, 0.0), ((0.05, 0.05, 0.05), 0.9, 0.0)][(r + c) % 2], bevel=0.0)
for i in range(7):
    cyl(0.06, 0.04 + (i % 3) * 0.04, (8.6 + (i % 4) * 0.15, D - 0.65 + (i // 4) * 0.15, 0.9 + (0.02 + (i % 3) * 0.02)), CHIP[i % 4], verts=10)
# Card table with stools.
cyl(0.9, 0.1, (11.2, D - 1.0, 0.85), ((0.3, 0.15, 0.06), 0.7, 0.0), verts=20)
cyl(0.82, 0.03, (11.2, D - 1.0, 0.92), FELT, verts=20)
cyl(0.1, 0.8, (11.2, D - 1.0, 0.4), METAL_GOLD, verts=10)
for i in range(5):
    a = i * 0.55 + 2.0
    cube((0.16, 0.24, 0.005), (11.2 + math.cos(a) * 0.55, D - 1.0 + math.sin(a) * 0.55, 0.94), (WHITE, 0.6, 0.0), rot=(0, 0, a), bevel=0.0)
for i in range(3):
    x = 10.4 + i * 0.8
    cyl(0.03, 0.55, (x, D - 1.7, 0.27), METAL_CHROME, verts=8)
    cyl(0.2, 0.08, (x, D - 1.7, 0.58), ((0.45, 0.04, 0.06), 0.7, 0.0), verts=12)
# Cashier cage.
cube((1.6, 0.6, 1.1), (13.6, D - 0.5, 0.55), ((0.3, 0.15, 0.06), 0.7, 0.0), bevel=0.03)
for i in range(9):
    rod((12.85 + i * 0.19, D - 0.75, 1.1), (12.85 + i * 0.19, D - 0.75, 2.6), 0.015, METAL_GOLD, verts=5)
cube((1.7, 0.06, 0.1), (13.6, D - 0.75, 2.62), METAL_GOLD, bevel=0.01)
neon_sign("CASH", 13.05, D + 0.0, 2.9, NEON_GREEN, cell=0.12)
# Signs.
neon_sign("JACKPOT", 4.3, D + 0.0, 4.2, NEON_YELLOW, cell=0.22, backing=PLASTIC_BLACK)
for i in range(30):
    a = i / 30.0 * math.tau
    sphere(0.06, (7.6 + math.cos(a) * 3.1, D - 0.02, 4.75 + math.sin(a) * 1.0), NEON_YELLOW if i % 2 else NEON_WHITE, segments=5, rings=4)
neon_sign("777", 10.7, D + 0.0, 4.4, NEON_RED, cell=0.24, gap=0.4)
framed_picture(2.0, D + 0.0, 3.4, w=1.6, h=1.2, face=neon((0.9, 0.7, 0.3), 0.8, (0.3, 0.2, 0.05)))
framed_picture(13.2, D + 0.0, 4.6, w=1.4, h=1.0, face=neon((0.3, 0.9, 0.5), 0.8, (0.05, 0.3, 0.12)))
# Upper gallery with a gold rail and chandeliers' glow spots.
cube((15.0, 0.08, 0.10), (7.5, D + 0.0, 7.05), METAL_GOLD, bevel=0.01)
for i in range(30):
    rod((0.25 + i * 0.5, D - 0.05, 7.1), (0.25 + i * 0.5, D - 0.05, 7.9), 0.02, METAL_GOLD, verts=6)
cube((15.0, 0.08, 0.06), (7.5, D - 0.05, 7.92), METAL_GOLD, bevel=0.01)
for i in range(5):
    slot(1.0 + i * 0.95, D - 0.5, 7.1, i + 1)
for i in range(4):
    x = 7.6 + i * 1.6
    cube((0.16, 0.16, 0.3), (x, D - 0.08, 8.6), METAL_GOLD, bevel=0.03)
    sphere(0.09, (x, D - 0.16, 8.82), NEON_YELLOW, segments=10, rings=8)
neon_sign("VIP", 12.4, D + 0.0, 8.2, NEON_MAGENTA, cell=0.2)

join_static("decor")
export("backdrop_casino")
