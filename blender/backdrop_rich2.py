# Backdrop for the sky bar (rich2): a wall-length aquarium glowing cyan with
# fish and coral, a cocktail bar with bottles and stools, a DJ booth, a
# "SKY BAR" neon and lounge seats. 15 m wide, floor-anchored.
#   blender -b --python blender/backdrop_rich2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
WATER = neon((0.1, 0.6, 0.9), 1.1, (0.02, 0.18, 0.30))
CORAL_M = neon((1.0, 0.4, 0.5), 1.4, (0.3, 0.08, 0.12))
FISH = [neon((1.0, 0.6, 0.1), 2.0), neon((0.3, 0.9, 1.0), 2.0), neon((1.0, 0.2, 0.6), 2.0), neon((0.9, 0.9, 0.2), 2.0)]
BAR_TOP = ((0.05, 0.05, 0.08), 0.15, 0.3)

wall_panel_lines(0.0, 15.0, D + 0.02, 0.0, 7.0, spacing=1.8)

# The aquarium: a glass tank set into the wall from 1.4 m to 4.6 m.
cube((8.0, 0.5, 3.2), (7.5, D - 0.1, 3.0), WATER, bevel=0.02)
cube((8.2, 0.08, 0.12), (7.5, D - 0.36, 1.4), METAL_CHROME, bevel=0.01)
cube((8.2, 0.08, 0.12), (7.5, D - 0.36, 4.6), METAL_CHROME, bevel=0.01)
for i in range(3):
    cube((0.08, 0.08, 3.2), (3.5 + i * 4.0, D - 0.36, 3.0), METAL_CHROME, bevel=0.01)
# Coral and rocks along the bottom, bubbles rising.
for i in range(9):
    x = 3.9 + i * 0.85
    sphere(0.28, (x, D - 0.15, 1.65), ((0.12, 0.12, 0.16), 0.9, 0.0), scale=(1.4, 0.8, 0.7), segments=8, rings=6)
    for j in range(3):
        rod((x + (j - 1) * 0.12, D - 0.15, 1.75), (x + (j - 1) * 0.22, D - 0.15, 2.15 + (j % 2) * 0.2), 0.035, CORAL_M, verts=6)
for i in range(7):
    a = i * 1.7
    x = 4.2 + i * 1.05
    z = 2.4 + (i % 3) * 0.55
    f = sphere(0.14, (x, D - 0.2, z), FISH[i % 4], scale=(1.8, 0.5, 1.0), segments=8, rings=6)
    f.rotation_euler = (0, 0, math.sin(a) * 0.3)
    cone(0.10, 0.2, (x + 0.3, D - 0.2, z), FISH[i % 4], rot=(0, math.pi / 2, 0), verts=6)
for i in range(12):
    sphere(0.03 + (i % 3) * 0.015, (4.0 + i * 0.6, D - 0.3, 1.8 + (i * 0.37) % 2.4), (WHITE, 0.1, 0.0), segments=6, rings=4)

# Bar counter with bottles and stools.
cube((4.0, 0.7, 1.1), (3.0, D - 1.0, 0.55), ((0.14, 0.10, 0.22), 0.6, 0.2), bevel=0.03)
cube((4.2, 0.85, 0.06), (3.0, D - 1.0, 1.13), BAR_TOP, bevel=0.01)
led_strip(1.0, 5.0, D - 1.4, 0.15, m=NEON_CYAN)
shelf(3.0, D - 0.35, 1.9, w=3.6)
shelf(3.0, D - 0.35, 2.6, w=3.6)
colors = [((0.1, 0.5, 0.2), 0.05, 0.0), ((0.6, 0.35, 0.05), 0.05, 0.0), ((0.5, 0.05, 0.1), 0.05, 0.0), GLASS, ((0.1, 0.2, 0.6), 0.05, 0.0)]
for row, z in ((0, 1.92), (1, 2.62)):
    for i in range(11):
        cyl(0.045, 0.30 + (i % 3) * 0.06, (1.35 + i * 0.33, D - 0.25, z + 0.16), colors[(i + row) % 5], verts=8)
for i in range(3):
    x = 1.8 + i * 1.2
    cyl(0.03, 0.7, (x, D - 1.7, 0.35), METAL_CHROME, verts=8)
    cyl(0.22, 0.08, (x, D - 1.7, 0.74), ((0.35, 0.05, 0.12), 0.7, 0.0), verts=12)
    cyl(0.2, 0.03, (x, D - 1.7, 0.02), METAL_CHROME, verts=12)
neon_sign("SKY BAR", 1.2, D + 0.0, 3.5, NEON_MAGENTA, cell=0.17)

# Lounge seats on the right, a DJ booth and a speaker stack.
sofa(12.3, D - 1.1, 0.0, w=2.4, m=((0.08, 0.12, 0.3), 0.85, 0.0))
cube((1.4, 0.8, 0.9), (14.0, D - 0.9, 0.45), ((0.06, 0.06, 0.1), 0.5, 0.3), bevel=0.03)
cube((1.4, 0.6, 0.04), (14.0, D - 0.9, 0.92), BAR_TOP, bevel=0.01)
for s in (-1, 1):
    cyl(0.22, 0.02, (14.0 + s * 0.35, D - 0.95, 0.95), PLASTIC_BLACK, verts=16)
    cyl(0.18, 0.01, (14.0 + s * 0.35, D - 0.95, 0.965), neon((0.8, 0.8, 0.9), 0.6, (0.2, 0.2, 0.25)), verts=16)
led_strip(13.3, 14.7, D - 1.31, 0.12, m=NEON_MAGENTA)
for i in range(2):
    cube((0.7, 0.6, 0.9), (12.2, D - 0.4, 0.45 + i * 0.95), (SLATE, 0.6, 0.3), bevel=0.03)
    cyl(0.22, 0.05, (12.2, D - 0.72, 0.45 + i * 0.95), PLASTIC_BLACK, rot=(math.pi / 2, 0, 0), verts=14)
    torus(0.24, 0.03, (12.2, D - 0.74, 0.45 + i * 0.95), NEON_CYAN, rot=(math.pi / 2, 0, 0))
poster(12.6, D + 0.0, 2.8, w=1.2, h=1.7, face=neon((0.8, 0.2, 1.0), 1.2, (0.2, 0.05, 0.3)))
poster(14.1, D + 0.0, 2.6, w=1.0, h=1.4, face=neon((0.2, 1.0, 0.8), 1.2, (0.03, 0.25, 0.2)))
plant(0.6, D - 1.1, 0.0, size=1.2)
plant(11.0, D - 1.3, 0.0, size=0.9)

# ---- upper wall: a giant "OPEN 24/7" neon, an LED video wall and a glass rail.
neon_sign("OPEN", 1.0, D + 0.0, 8.0, NEON_MAGENTA, cell=0.2)
neon_sign("24 7", 4.6, D + 0.0, 8.0, NEON_CYAN, cell=0.2, gap=0.3)
cube((4.4, 0.12, 2.0), (10.6, D + 0.0, 8.3), PLASTIC_BLACK, bevel=0.02)
for r in range(8):
    for c in range(18):
        k = (r * 31 + c * 17) % 7
        cube((0.2, 0.02, 0.2), (8.55 + c * 0.24, D - 0.07, 7.45 + r * 0.24), [NEON_MAGENTA, NEON_CYAN, NEON_VIOLET, NEON_PINK, NEON_BLUE, NEON_CYAN, NEON_MAGENTA][k], bevel=0.0)
cube((15.0, 0.06, 0.6), (7.5, D - 0.02, 7.3), GLASS, bevel=0.0)
cube((15.0, 0.08, 0.05), (7.5, D - 0.05, 7.62), METAL_CHROME, bevel=0.0)
for i in range(3):
    spotlight(13.4 + i * 0.5, D - 0.3, 9.5, m=[NEON_MAGENTA, NEON_CYAN, NEON_PINK][i], aim=0.3)

join_static("decor")
export("backdrop_rich2")
