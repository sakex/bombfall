# Backdrop for the arcade, synthwave edition: rows of glowing cabinets on a
# starfield carpet with a neon grid, a pinball machine, a claw crane, a
# prize counter with a spinning holo-pyramid, a "GAME OVER" sign, a big
# scanline screen with pixel art, a sunset poster, kanji signs, and a
# high-score board, tickets, lasers and stars up top. 15 m wide.
#   blender -b --python blender/backdrop_arcade.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(0.5, 5.6, 3.2, 1.6), (10.3, 5.6, 3.8, 1.6), (4.6, 6.0, 5.4, 1.3)]
CARPET = ((0.04, 0.02, 0.10), 0.95, 0.0)
CAB = [((0.08, 0.08, 0.30), 0.5, 0.2), ((0.30, 0.04, 0.14), 0.5, 0.2), ((0.04, 0.20, 0.22), 0.5, 0.2), ((0.25, 0.15, 0.04), 0.5, 0.2)]
SCREENS = [SCREEN_CYAN, neon((1.0, 0.4, 0.7), 2.0, (0.2, 0.05, 0.1)), neon((0.4, 1.0, 0.4), 2.0, (0.05, 0.2, 0.05)), neon((1.0, 0.8, 0.2), 2.0, (0.2, 0.15, 0.02))]


def cabinet(x, y, z, k):
    m = CAB[k % 4]
    cube((0.9, 0.9, 1.9), (x, y + 0.45, z + 0.95), m, bevel=0.0)
    cube((0.9, 0.5, 0.5), (x, y + 0.25, z + 2.1), m, bevel=0.0)                 # marquee box
    cube((0.8, 0.02, 0.3), (x, y - 0.01, z + 2.1), [NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN][k % 4], bevel=0.0)
    cube((0.02, 0.02, 1.85), (x - 0.44, y - 0.01, z + 0.95), [NEON_HOT, NEON_ICE][k % 2], bevel=0.0)   # neon edge
    cube((0.7, 0.03, 0.6), (x, y - 0.02, z + 1.45), SCREENS[k % 4], rot=(0.25, 0, 0), bevel=0.0)
    cube((0.8, 0.35, 0.08), (x, y + 0.1, z + 1.0), PLASTIC_BLACK, bevel=0.0)     # control panel
    for j in range(3):
        sphere(0.035, (x - 0.2 + j * 0.15, y + 0.05, z + 1.06), [NEON_RED, NEON_CYAN, NEON_YELLOW][j], segments=6, rings=4)
    rod((x + 0.28, y + 0.05, z + 1.04), (x + 0.28, y + 0.02, z + 1.18), 0.012, METAL_CHROME, verts=5)
    sphere(0.03, (x + 0.28, y + 0.02, z + 1.19), NEON_RED, segments=6, rings=4)
    for i in range(6):
        cube((0.5, 0.02, 0.025), (x, y - 0.03, z + 1.25 + i * 0.07), neon((1.0, 1.0, 1.0), 0.6, (0.3, 0.3, 0.3)) if (i + k) % 3 else PLASTIC_BLACK, rot=(0.25, 0, 0), bevel=0.0)


# Starfield carpet with a neon grid; wall with neon seams.
cube((15.0, 1.9, 0.02), (7.5, 0.95, 0.01), CARPET, bevel=0.0)
for i in range(36):
    k = (i * 7919) % 1000
    cube((0.08, 0.08, 0.005), (0.2 + (k % 73) / 73.0 * 14.6, 0.1 + ((k // 73) % 13) / 13.0 * 1.6, 0.025), [NEON_PINK, NEON_CYAN, NEON_YELLOW][k % 3], bevel=0.0)
grid_floor(0.2, 14.8, 0.1, D - 0.1, z=0.02, m=NEON_HOT, m2=NEON_ICE, nx=10, ny=3)
cube((15.0, 0.03, 9.5), (7.5, D + 0.03, 4.75), MAT_PLUM, bevel=0.0)
neon_seams(0.0, 15.0, 0.0, 9.5, D + 0.0, NEON_LAV, spacing=1.3, avoid=WINDOWS, r=0.012)
for w in WINDOWS:
    window_neon(w, D - 0.02, NEON_HOT)

# Rows of cabinets along the wall.
for i in range(6):
    cabinet(0.8 + i * 1.05, D - 0.9, 0.0, i)
for i in range(3):
    cabinet(11.3 + i * 1.05, D - 0.9, 0.0, i + 2)
# Pinball machine.
cube((0.8, 1.6, 0.1), (8.1, D - 1.0, 0.85), PLASTIC_BLACK, rot=(0.12, 0, 0), bevel=0.0)
cube((0.7, 1.45, 0.02), (8.1, D - 1.0, 0.92), neon((0.9, 0.3, 0.6), 1.2, (0.25, 0.05, 0.15)), rot=(0.12, 0, 0), bevel=0.0)
for j in range(9):
    sphere(0.035, (7.85 + (j % 3) * 0.25, D - 1.5 + (j // 3) * 0.4, 0.95 + (j // 3) * 0.05), [NEON_CYAN, NEON_YELLOW, NEON_PINK][j % 3], segments=6, rings=4)
cube((0.8, 0.3, 0.7), (8.1, D - 0.3, 1.25), PLASTIC_BLACK, bevel=0.0)
cube((0.7, 0.02, 0.5), (8.1, D - 0.46, 1.25), SCREEN_CYAN, bevel=0.0)
neon_tube_frame(7.72, 8.48, 0.92, 1.58, D - 0.47, NEON_HOT, r=0.012)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((8.1 + sx * 0.35, D - 1.0 + sy * 0.7, 0.0), (8.1 + sx * 0.35, D - 1.0 + sy * 0.7, 0.75), 0.03, METAL_CHROME, verts=6)
# Claw crane.
cube((1.2, 1.0, 0.9), (9.6, D - 0.6, 0.45), ((0.45, 0.06, 0.2), 0.5, 0.2), bevel=0.0)
cube((1.15, 0.95, 1.3), (9.6, D - 0.6, 1.55), GLASS, bevel=0.0)
for i in range(12):
    sphere(0.12, (9.2 + (i % 4) * 0.27, D - 0.9 + (i // 4) * 0.3, 1.0 + (i % 3) * 0.1), [NEON_PINK, NEON_YELLOW, NEON_CYAN, NEON_GREEN][i % 4], segments=6, rings=4)
cube((1.2, 1.0, 0.25), (9.6, D - 0.6, 2.32), ((0.45, 0.06, 0.2), 0.5, 0.2), bevel=0.0)
cube((1.0, 0.02, 0.15), (9.6, D - 1.11, 2.32), NEON_YELLOW, bevel=0.0)
for sx in (-1, 1):
    cube((0.02, 0.02, 2.4), (9.6 + sx * 0.6, D - 1.11, 1.22), NEON_ICE, bevel=0.0)
rod((9.6, D - 0.6, 2.2), (9.6, D - 0.6, 1.7), 0.02, METAL_CHROME, verts=5)
for a in (0, 2.1, 4.2):
    rod((9.6, D - 0.6, 1.7), (9.6 + math.cos(a) * 0.12, D - 0.6 + math.sin(a) * 0.12, 1.5), 0.015, METAL_CHROME, verts=5)
# Prize counter with plushies, a hologram and a ticket sign.
cube((2.0, 0.7, 1.0), (13.5, D - 1.0, 0.5), MAT_GRAPE, bevel=0.0)
cube((2.1, 0.8, 0.05), (13.5, D - 1.0, 1.02), METAL_CHROME, bevel=0.0)
led_strip(12.5, 14.5, D - 1.36, 0.15, m=NEON_CYAN)
chevron_strip(12.55, 14.45, 0.55, D - 1.36, m=NEON_HOT, h=0.2)
hologram(13.5, D - 1.0, 1.05, "pyramid", "spin_prize", m=NEON_ICE, r=0.26, ring=NEON_HOT)
for z in (2.0, 2.8):
    shelf(13.5, D - 0.35, z, w=2.0)
    led_strip(12.55, 14.45, D - 0.37, z - 0.02, m=NEON_HOT, r=0.012)
for i in range(4):
    sphere(0.18, (12.8 + i * 0.45, D - 0.25, 2.18), [((0.9, 0.5, 0.6), 0.9, 0.0), ((0.5, 0.7, 0.95), 0.9, 0.0)][i % 2], segments=6, rings=5)
    sphere(0.12, (12.8 + i * 0.45, D - 0.25, 2.42), [((0.9, 0.5, 0.6), 0.9, 0.0), ((0.5, 0.7, 0.95), 0.9, 0.0)][i % 2], segments=6, rings=5)
for i in range(3):
    cube((0.35, 0.3, 0.45), (12.9 + i * 0.6, D - 0.25, 3.05), [NEON_PINK, NEON_CYAN, NEON_YELLOW][i], bevel=0.0)
neon_sign("PRIZES", 12.2, D + 0.0, 3.8, NEON_YELLOW, cell=0.12)
kanji_sign(14.7, D + 0.0, 1.2, 3.4, m=NEON_HOT, seed=41, w=0.4)
# Big signs and screens on the wall.
neon_sign("GAME OVER", 1.0, D + 0.0, 4.2, NEON_RED, cell=0.16)
neon_tube_frame(0.85, 6.3, 4.05, 5.05, D - 0.02, NEON_ICE, r=0.02)
neon_sign("INSERT COIN", 2.4, D + 0.0, 3.3, NEON_CYAN, cell=0.12, backing=MAT_INK)
sunset_mural(1.6, 3.2, D + 0.0, 0.45, frame=NEON_HOT, grid=False)
scanline_screen(8.6, D + 0.0, 4.5, 2.8, 1.6, colour=LAVENDER, frame=NEON_HOT, bars=False, lines=9)
for r in range(5):
    for c in range(9):
        k = (r * 13 + c * 7) % 5
        cube((0.22, 0.02, 0.22), (7.6 + c * 0.28, D - 0.07, 3.9 + r * 0.3), [NEON_CYAN, NEON_PINK, NEON_YELLOW, NEON_GREEN, MAT_INK][k], bevel=0.0)
horizon_lines(10.6, 14.0, D + 0.0, 4.6, n=4, spacing=0.14, m=NEON_ICE)
neon_polygon(11.6, 5.15, D + 0.0, 0.32, 3, NEON_HOT)
# Upper wall: a high-score board, a tickets strip, lasers and stars.
cube((4.0, 0.1, 2.0), (11.0, D + 0.0, 8.4), MAT_INK, bevel=0.0)
neon_tube_frame(9.0, 13.0, 7.4, 9.4, D - 0.06, NEON_ICE, r=0.02)
for r in range(3):
    neon_sign(["AAA 99990", "ZED 77650", "YOU 00000"][r], 9.3, D - 0.06, 8.55 - r * 0.45, [NEON_YELLOW, NEON_CYAN, NEON_GREEN][r], cell=0.075, gap=0.5)
neon_sign("HI SCORES", 9.6, D - 0.06, 9.0, NEON_YELLOW, cell=0.08)
for i in range(18):
    cube((0.5, 0.03, 0.28), (0.6 + i * 0.8, D + 0.0, 7.6), [NEON_PINK, NEON_YELLOW][i % 2], rot=(0, 0, 0.1), bevel=0.0)
neon_sign("TICKETS", 1.2, D + 0.0, 8.3, NEON_MAGENTA, cell=0.16)
for i in range(3):
    cube((0.9, 0.06, 0.9), (5.2 + i * 1.1, D + 0.0, 8.4), NEON_CYAN if i % 2 else NEON_PINK, rot=(0, 0.785, 0), bevel=0.0)
laser_fan(4.1, D - 0.4, 9.5, m=NEON_HOT, n=4, spread=1.1, length=1.5)
laser_fan(7.9, D - 0.4, 9.5, m=NEON_ICE, n=4, spread=1.1, length=1.5)
star_field(0.0, 15.0, 7.3, 9.4, D + 0.0, n=22, seed=23)
chevron_strip(13.3, 14.7, 8.4, D + 0.0, m=NEON_HOT, h=0.24)
led_column(14.6, D + 0.0, 7.1, 2.3, m=NEON_ICE, alt=NEON_HOT, w=0.2)

strip_bevels()
join_static("decor")
export("backdrop_arcade")
