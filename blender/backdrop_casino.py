# Backdrop for the casino, synthwave edition: a plum hall with gold and
# hot-pink neon, a wall of slot machines, a roulette table, a card table
# with chips, a cashier cage, a "JACKPOT" neon under a bulb ellipse, a
# sunset mural, chrome columns wrapped in neon rings, a spinning holo-chip
# and an upper gallery with neon palms and lasers. 15 m wide.
#   blender -b --python blender/backdrop_casino.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(5.6, 5.85, 4.4, 1.05), (11.0, 6.0, 3.0, 0.9)]
FELT = ((0.04, 0.22, 0.12), 0.9, 0.0)
CARPET = ((0.16, 0.03, 0.10), 0.95, 0.0)
CARPET2 = ((0.22, 0.04, 0.14), 0.95, 0.0)
WOODY = ((0.14, 0.06, 0.05), 0.7, 0.0)
CHIP = [((0.8, 0.1, 0.1), 0.4, 0.0), ((0.1, 0.3, 0.8), 0.4, 0.0), ((0.9, 0.9, 0.9), 0.4, 0.0), ((0.1, 0.1, 0.1), 0.4, 0.0)]
GOLD_N = neon((1.0, 0.8, 0.3), 3.0)


def slot(x, y, z, k):
    cube((0.8, 0.7, 1.7), (x, y + 0.35, z + 0.85), MAT_PLUM, bevel=0.0)
    cube((0.8, 0.5, 0.45), (x, y + 0.25, z + 1.9), MAT_PLUM, bevel=0.0)
    cube((0.7, 0.02, 0.28), (x, y - 0.01, z + 1.9), [NEON_YELLOW, NEON_PINK, NEON_CYAN][k % 3], bevel=0.0)
    cube((0.62, 0.03, 0.34), (x, y - 0.02, z + 1.3), PLASTIC_BLACK, bevel=0.0)
    for j in range(3):
        cube((0.16, 0.02, 0.26), (x - 0.2 + j * 0.2, y - 0.04, z + 1.3), [neon((1.0, 0.9, 0.9), 0.8, (0.4, 0.35, 0.3)), neon((1.0, 0.5, 0.5), 0.8, (0.4, 0.15, 0.15))][(j + k) % 2], bevel=0.0)
        cube((0.1, 0.01, 0.08), (x - 0.2 + j * 0.2, y - 0.05, z + 1.3), [NEON_RED, NEON_YELLOW, NEON_GREEN][(j * 2 + k) % 3], bevel=0.0)
    cube((0.02, 0.02, 1.6), (x - 0.4, y - 0.01, z + 0.85), [NEON_HOT, NEON_ICE][k % 2], bevel=0.0)   # neon edge
    cube((0.7, 0.3, 0.06), (x, y + 0.1, z + 0.9), METAL_GOLD, bevel=0.0)
    sphere(0.04, (x + 0.15, y - 0.02, z + 0.94), NEON_RED, segments=6, rings=4)
    rod((x + 0.44, y + 0.3, z + 1.1), (x + 0.5, y + 0.3, z + 1.55), 0.02, METAL_CHROME, verts=5)
    sphere(0.06, (x + 0.5, y + 0.3, z + 1.58), ((0.8, 0.05, 0.05), 0.3, 0.0), segments=6, rings=4)
    for i in range(8):
        cube((0.05, 0.03, 0.05), (x - 0.35 + i * 0.1, y - 0.01, z + 2.16), NEON_YELLOW if (i + k) % 2 else NEON_WHITE, bevel=0.0)


# Carpet with a diamond pattern and a neon grid, gold dado, chrome columns.
cube((15.0, 1.9, 0.02), (7.5, 0.95, 0.01), CARPET, bevel=0.0)
for i in range(15):
    if i % 2:
        cube((0.9, 1.9, 0.005), (0.5 + i * 1.0, 0.95, 0.025), CARPET2, bevel=0.0)
grid_floor(0.2, 14.8, 0.1, D - 0.1, z=0.03, m=NEON_HOT, m2=GOLD_N, nx=10, ny=2)
cube((15.0, 0.03, 7.0), (7.5, D + 0.03, 3.5), MAT_PLUM, bevel=0.0)
cube((15.0, 0.06, 0.08), (7.5, D + 0.0, 1.35), METAL_GOLD, bevel=0.0)
hline(0.2, 14.8, D - 0.02, 1.42, NEON_HOT, r=0.02)
for i in range(11):
    cube((1.1, 0.04, 1.1), (0.75 + i * 1.4, D + 0.01, 0.7), MAT_INK, bevel=0.0)
    neon_tube_frame(0.3 + i * 1.4, 1.2 + i * 1.4, 0.25, 1.15, D - 0.015, GOLD_N if i % 2 else NEON_HOT, r=0.012)
neon_seams(0.0, 15.0, 1.5, 7.0, D + 0.0, NEON_LAV, spacing=1.8, avoid=WINDOWS, r=0.012)
for x in (0.5, 14.5):
    column(x, D - 0.3, 0.0, h=7.5, r=0.3, m=CHROME_M, cap=METAL_GOLD)
    for zz in (2.2, 4.0, 5.8):
        torus(0.34, 0.025, (x, D - 0.3, zz), NEON_HOT if zz != 4.0 else NEON_ICE, major_segments=16, minor_segments=4)
for w in WINDOWS:
    window_neon(w, D - 0.02, GOLD_N)

# Slots along the left wall.
for i in range(5):
    slot(1.4 + i * 0.95, D - 0.7, 0.0, i)
# Holo-chip on a plinth between the slots and the roulette.
cube((0.5, 0.5, 0.6), (6.2, 0.55, 0.3), MAT_INK, bevel=0.0)
cube((0.5, 0.02, 0.05), (6.2, 0.29, 0.3), GOLD_N, bevel=0.0)
hologram(6.2, 0.55, 0.6, "coin", "spin_chip", m=GOLD_N, r=0.3, ring=NEON_HOT)
# Roulette table.
cube((2.6, 1.3, 0.85), (8.0, D - 1.0, 0.43), WOODY, bevel=0.0)
cube((2.5, 1.2, 0.03), (8.0, D - 1.0, 0.87), FELT, bevel=0.0)
cube((2.6, 0.02, 0.03), (8.0, D - 1.66, 0.86), NEON_HOT, bevel=0.0)
cyl(0.55, 0.12, (7.2, D - 1.0, 0.94), WOODY, verts=20)
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
cyl(0.9, 0.1, (11.2, D - 1.0, 0.85), WOODY, verts=20)
cyl(0.82, 0.03, (11.2, D - 1.0, 0.92), FELT, verts=20)
torus(0.86, 0.015, (11.2, D - 1.0, 0.91), NEON_ICE, major_segments=20, minor_segments=4)
cyl(0.1, 0.8, (11.2, D - 1.0, 0.4), METAL_GOLD, verts=10)
for i in range(5):
    a = i * 0.55 + 2.0
    cube((0.16, 0.24, 0.005), (11.2 + math.cos(a) * 0.55, D - 1.0 + math.sin(a) * 0.55, 0.94), (WHITE, 0.6, 0.0), rot=(0, 0, a), bevel=0.0)
for i in range(3):
    x = 10.4 + i * 0.8
    cyl(0.03, 0.55, (x, D - 1.7, 0.27), METAL_CHROME, verts=8)
    cyl(0.2, 0.08, (x, D - 1.7, 0.58), ((0.35, 0.04, 0.12), 0.7, 0.0), verts=12)
# Cashier cage.
cube((1.6, 0.6, 1.1), (13.6, D - 0.5, 0.55), WOODY, bevel=0.0)
for i in range(9):
    rod((12.85 + i * 0.19, D - 0.75, 1.1), (12.85 + i * 0.19, D - 0.75, 2.6), 0.015, METAL_GOLD, verts=5)
cube((1.7, 0.06, 0.1), (13.6, D - 0.75, 2.62), METAL_GOLD, bevel=0.0)
neon_sign("CASH", 13.05, D + 0.0, 2.9, NEON_GREEN, cell=0.12)
# Signs and murals.
neon_sign("JACKPOT", 4.3, D + 0.0, 4.2, NEON_YELLOW, cell=0.22, backing=MAT_INK)
for i in range(30):
    a = i / 30.0 * math.tau
    cube((0.1, 0.03, 0.1), (7.6 + math.cos(a) * 3.1, D - 0.02, 4.75 + math.sin(a) * 1.0), NEON_YELLOW if i % 2 else NEON_WHITE, bevel=0.0)
neon_sign("777", 10.7, D + 0.0, 4.4, NEON_RED, cell=0.24, gap=0.4)
sunset_mural(2.1, 3.9, D + 0.0, 0.85, frame=GOLD_N)
scanline_screen(13.2, D + 0.0, 4.5, 1.5, 1.0, colour=(1.0, 0.8, 0.3), frame=GOLD_N, seed=5)
kanji_sign(14.6, D + 0.0, 2.2, 3.4, m=NEON_HOT, seed=21, w=0.4)
horizon_lines(0.3, 3.9, D + 0.0, 5.7, n=4, spacing=0.14, m=NEON_HOT)
chevron_strip(0.3, 5.2, 6.6, D + 0.0, m=GOLD_N, h=0.24)
neon_polygon(11.3, 5.3, D + 0.0, 0.35, 4, NEON_ICE, rot=math.pi / 4)

# Upper gallery with a gold rail, neon palms, slots, lasers and a VIP sign.
cube((15.0, 0.03, 2.5), (7.5, D + 0.03, 8.25), MAT_PLUM, bevel=0.0)
cube((15.0, 0.08, 0.10), (7.5, D + 0.0, 7.05), METAL_GOLD, bevel=0.0)
for i in range(30):
    rod((0.25 + i * 0.5, D - 0.05, 7.1), (0.25 + i * 0.5, D - 0.05, 7.9), 0.02, METAL_GOLD, verts=6)
cube((15.0, 0.08, 0.06), (7.5, D - 0.05, 7.92), METAL_GOLD, bevel=0.0)
hline(0.2, 14.8, D - 0.1, 7.0, NEON_HOT, r=0.02)
for i in range(5):
    slot(1.0 + i * 0.95, D - 0.5, 7.1, i + 1)
neon_palm(6.0, D - 0.3, 7.1, 2.2, m=NEON_HOT, lean=0.1, fronds=5)
neon_palm(10.9, D - 0.3, 7.1, 2.2, m=NEON_HOT, lean=-0.1, fronds=5)
for i in range(3):
    x = 7.4 + i * 1.2
    cube((0.16, 0.16, 0.3), (x, D - 0.08, 8.6), METAL_GOLD, bevel=0.0)
    sphere(0.09, (x, D - 0.16, 8.82), NEON_YELLOW, segments=10, rings=8)
neon_sign("VIP", 12.4, D + 0.0, 8.2, NEON_MAGENTA, cell=0.2)
neon_tube_frame(12.2, 14.2, 8.05, 9.15, D - 0.02, GOLD_N, r=0.02)
laser_fan(8.6, D - 0.4, 9.5, m=GOLD_N, n=5, spread=1.3, length=2.0)
star_field(0.0, 15.0, 8.0, 9.4, D + 0.0, n=16, seed=6, m=neon((1.0, 0.9, 0.7), 2.5, (0.3, 0.28, 0.2)))

strip_bevels()
join_static("decor")
export("backdrop_casino")
