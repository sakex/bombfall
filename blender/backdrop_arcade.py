# Backdrop for the arcade: rows of glowing cabinets, a pinball machine, a
# claw crane, an air-hockey table, a prize counter, a "GAME OVER" sign, a
# ticket-token strip and a starfield carpet. 15 m wide, floor-anchored.
#   blender -b --python blender/backdrop_arcade.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
CARPET = ((0.05, 0.02, 0.12), 0.95, 0.0)
CAB = [((0.10, 0.10, 0.35), 0.5, 0.2), ((0.35, 0.05, 0.15), 0.5, 0.2), ((0.05, 0.25, 0.25), 0.5, 0.2), ((0.3, 0.2, 0.05), 0.5, 0.2)]
SCREENS = [SCREEN_CYAN, neon((1.0, 0.4, 0.7), 2.0, (0.2, 0.05, 0.1)), neon((0.4, 1.0, 0.4), 2.0, (0.05, 0.2, 0.05)), neon((1.0, 0.8, 0.2), 2.0, (0.2, 0.15, 0.02))]


def cabinet(x, y, z, k):
    m = CAB[k % 4]
    cube((0.9, 0.9, 1.9), (x, y + 0.45, z + 0.95), m, bevel=0.03)
    cube((0.9, 0.5, 0.5), (x, y + 0.25, z + 2.1), m, bevel=0.03)                 # marquee box
    cube((0.8, 0.02, 0.3), (x, y - 0.01, z + 2.1), [NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN][k % 4], bevel=0.0)
    cube((0.7, 0.03, 0.6), (x, y - 0.02, z + 1.45), SCREENS[k % 4], rot=(0.25, 0, 0), bevel=0.0)
    cube((0.8, 0.35, 0.08), (x, y + 0.1, z + 1.0), PLASTIC_BLACK, bevel=0.01)     # control panel
    for j in range(3):
        sphere(0.035, (x - 0.2 + j * 0.15, y + 0.05, z + 1.06), [NEON_RED, NEON_CYAN, NEON_YELLOW][j], segments=6, rings=4)
    rod((x + 0.28, y + 0.05, z + 1.04), (x + 0.28, y + 0.02, z + 1.18), 0.012, METAL_CHROME, verts=5)
    sphere(0.03, (x + 0.28, y + 0.02, z + 1.19), NEON_RED, segments=6, rings=4)
    for i in range(6):
        cube((0.5, 0.02, 0.025), (x, y - 0.03, z + 1.25 + i * 0.07), neon((1.0, 1.0, 1.0), 0.6, (0.3, 0.3, 0.3)) if (i + k) % 3 else PLASTIC_BLACK, rot=(0.25, 0, 0), bevel=0.0)


# Starfield carpet.
cube((15.0, 1.9, 0.02), (7.5, 0.95, 0.01), CARPET, bevel=0.0)
for i in range(36):
    k = (i * 7919) % 1000
    cube((0.08, 0.08, 0.005), (0.2 + (k % 73) / 73.0 * 14.6, 0.1 + ((k // 73) % 13) / 13.0 * 1.6, 0.025), [NEON_PINK, NEON_CYAN, NEON_YELLOW][k % 3], bevel=0.0)
wall_panel_lines(0.0, 15.0, D + 0.02, 0.0, 9.5, spacing=1.3)

# Rows of cabinets along the wall.
for i in range(6):
    cabinet(0.8 + i * 1.05, D - 0.9, 0.0, i)
for i in range(3):
    cabinet(11.3 + i * 1.05, D - 0.9, 0.0, i + 2)
# Pinball machine.
cube((0.8, 1.6, 0.1), (8.1, D - 1.0, 0.85), PLASTIC_BLACK, rot=(0.12, 0, 0), bevel=0.02)
cube((0.7, 1.45, 0.02), (8.1, D - 1.0, 0.92), neon((0.9, 0.3, 0.6), 1.2, (0.25, 0.05, 0.15)), rot=(0.12, 0, 0), bevel=0.0)
for j in range(9):
    sphere(0.035, (7.85 + (j % 3) * 0.25, D - 1.5 + (j // 3) * 0.4, 0.95 + (j // 3) * 0.05), [NEON_CYAN, NEON_YELLOW, NEON_PINK][j % 3], segments=6, rings=4)
cube((0.8, 0.3, 0.7), (8.1, D - 0.3, 1.25), PLASTIC_BLACK, bevel=0.02)
cube((0.7, 0.02, 0.5), (8.1, D - 0.46, 1.25), SCREEN_CYAN, bevel=0.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((8.1 + sx * 0.35, D - 1.0 + sy * 0.7, 0.0), (8.1 + sx * 0.35, D - 1.0 + sy * 0.7, 0.75), 0.03, METAL_CHROME, verts=6)
# Claw crane.
cube((1.2, 1.0, 0.9), (9.6, D - 0.6, 0.45), ((0.6, 0.1, 0.2), 0.5, 0.2), bevel=0.03)
cube((1.15, 0.95, 1.3), (9.6, D - 0.6, 1.55), GLASS, bevel=0.02)
for i in range(12):
    sphere(0.12, (9.2 + (i % 4) * 0.27, D - 0.9 + (i // 4) * 0.3, 1.0 + (i % 3) * 0.1), [NEON_PINK, NEON_YELLOW, NEON_CYAN, NEON_GREEN][i % 4], segments=8, rings=6)
cube((1.2, 1.0, 0.25), (9.6, D - 0.6, 2.32), ((0.6, 0.1, 0.2), 0.5, 0.2), bevel=0.03)
cube((1.0, 0.02, 0.15), (9.6, D - 1.11, 2.32), NEON_YELLOW, bevel=0.0)
rod((9.6, D - 0.6, 2.2), (9.6, D - 0.6, 1.7), 0.02, METAL_CHROME, verts=5)
for a in (0, 2.1, 4.2):
    rod((9.6, D - 0.6, 1.7), (9.6 + math.cos(a) * 0.12, D - 0.6 + math.sin(a) * 0.12, 1.5), 0.015, METAL_CHROME, verts=5)
# Prize counter with plushies and a ticket sign.
cube((2.0, 0.7, 1.0), (13.5, D - 1.0, 0.5), ((0.3, 0.05, 0.4), 0.6, 0.0), bevel=0.03)
cube((2.1, 0.8, 0.05), (13.5, D - 1.0, 1.02), METAL_CHROME, bevel=0.01)
led_strip(12.5, 14.5, D - 1.36, 0.15, m=NEON_CYAN)
for z in (2.0, 2.8):
    shelf(13.5, D - 0.35, z, w=2.0)
for i in range(4):
    sphere(0.18, (12.8 + i * 0.45, D - 0.25, 2.18), [((0.9, 0.5, 0.6), 0.9, 0.0), ((0.5, 0.7, 0.95), 0.9, 0.0)][i % 2], segments=8, rings=6)
    sphere(0.12, (12.8 + i * 0.45, D - 0.25, 2.42), [((0.9, 0.5, 0.6), 0.9, 0.0), ((0.5, 0.7, 0.95), 0.9, 0.0)][i % 2], segments=8, rings=6)
for i in range(3):
    cube((0.35, 0.3, 0.45), (12.9 + i * 0.6, D - 0.25, 3.05), [NEON_PINK, NEON_CYAN, NEON_YELLOW][i], bevel=0.05)
neon_sign("PRIZES", 12.4, D + 0.0, 3.8, NEON_YELLOW, cell=0.14)
# Big signs and screens on the wall.
neon_sign("GAME OVER", 1.0, D + 0.0, 4.2, NEON_RED, cell=0.2)
neon_sign("INSERT COIN", 3.4, D + 0.0, 3.3, NEON_CYAN, cell=0.12, backing=PLASTIC_BLACK)
monitor(7.5, D + 0.0, 4.6, w=3.2, h=1.8, screen=neon((0.9, 0.3, 0.9), 1.5, (0.2, 0.05, 0.2)), stand=False)
for r in range(5):
    for c in range(9):
        k = (r * 13 + c * 7) % 5
        cube((0.22, 0.02, 0.22), (6.5 + c * 0.28, D - 0.06, 3.9 + r * 0.3), [NEON_CYAN, NEON_PINK, NEON_YELLOW, NEON_GREEN, PLASTIC_BLACK][k], bevel=0.0)
# Upper wall: a high-score board and a tickets strip.
cube((4.0, 0.1, 2.4), (11.0, D + 0.0, 7.9), PLASTIC_BLACK, bevel=0.03)
for r in range(3):
    neon_sign(["AAA 99990", "ZED 77650", "YOU 00000"][r], 9.3, D - 0.06, 8.6 - r * 0.55, [NEON_YELLOW, NEON_CYAN, NEON_GREEN][r], cell=0.075, gap=0.5)
neon_sign("HI SCORES", 9.6, D + 0.0, 9.15, NEON_YELLOW, cell=0.09)
for i in range(18):
    cube((0.5, 0.03, 0.28), (0.6 + i * 0.8, D + 0.0, 7.6), [NEON_PINK, NEON_YELLOW][i % 2], rot=(0, 0, 0.1), bevel=0.01)
neon_sign("TICKETS", 1.2, D + 0.0, 8.3, NEON_MAGENTA, cell=0.16)
for i in range(3):
    cube((0.9, 0.06, 0.9), (5.2 + i * 1.1, D + 0.0, 7.9), NEON_CYAN if i % 2 else NEON_PINK, rot=(0, 0.785, 0), bevel=0.02)

join_static("decor")
export("backdrop_arcade")
