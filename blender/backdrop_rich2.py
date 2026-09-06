# Backdrop for the sky bar (rich2), synthwave edition: a wall-length
# aquarium glowing cyan with fish and coral, a cocktail bar with bottles and
# stools under a neon palm, a DJ booth with a spinning holo-diamond, a "SKY
# BAR" neon, a kanji sign, a wet grid floor and an upper wall with the
# "OPEN 24/7" neon, an LED video wall, a sunset and lasers. 15 m wide.
#   blender -b --python blender/backdrop_rich2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(0.4, 5.2, 2.6, 1.6), (12.2, 5.2, 2.6, 1.6), (3.6, 5.2, 7.8, 1.5)]
WATER = neon((0.1, 0.6, 0.9), 1.1, (0.02, 0.18, 0.30))
CORAL_M = neon((1.0, 0.4, 0.5), 1.4, (0.3, 0.08, 0.12))
FISH = [neon((1.0, 0.6, 0.1), 2.0), neon((0.3, 0.9, 1.0), 2.0), neon((1.0, 0.2, 0.6), 2.0), neon((0.9, 0.9, 0.2), 2.0)]
BAR_TOP = ((0.05, 0.05, 0.08), 0.15, 0.3)

# Wall: navy with cyan/magenta seams, neon-lined windows, wet grid floor.
cube((15.0, 0.03, 7.0), (7.5, D + 0.03, 3.5), MAT_NAVY, bevel=0.0)
neon_seams(0.0, 15.0, 0.0, 7.0, D + 0.0, NEON_ICE, spacing=1.8, avoid=WINDOWS, r=0.012)
for w in WINDOWS:
    window_neon(w, D - 0.02, NEON_MAGENTA)
wet_floor(0.0, 15.0, 0.0, D)
grid_floor(0.2, 14.8, 0.1, D - 0.1, m=NEON_MAGENTA, m2=NEON_ICE, nx=10, ny=3)

# The aquarium: a glass tank set into the wall from 1.4 m to 4.6 m.
cube((8.0, 0.5, 3.2), (7.5, D - 0.1, 3.0), WATER, bevel=0.0)
cube((8.2, 0.08, 0.12), (7.5, D - 0.36, 1.4), METAL_CHROME, bevel=0.0)
cube((8.2, 0.08, 0.12), (7.5, D - 0.36, 4.6), METAL_CHROME, bevel=0.0)
neon_tube_frame(3.4, 11.6, 1.34, 4.66, D - 0.42, NEON_ICE, r=0.02)
for i in range(3):
    cube((0.08, 0.08, 3.2), (3.5 + i * 4.0, D - 0.36, 3.0), METAL_CHROME, bevel=0.0)
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
# A small sun setting behind the tank's top-right corner.
sunset_mural(9.8, 4.62, D + 0.0, 0.42, half=True, panel=False)

# Bar counter with bottles and stools, a neon palm at the end.
cube((4.0, 0.7, 1.1), (3.0, D - 1.0, 0.55), MAT_PLUM, bevel=0.0)
cube((4.2, 0.85, 0.06), (3.0, D - 1.0, 1.13), BAR_TOP, bevel=0.0)
led_strip(1.0, 5.0, D - 1.4, 0.15, m=NEON_CYAN)
led_strip(1.0, 5.0, D - 1.43, 1.09, m=NEON_HOT, r=0.015)
shelf(3.0, D - 0.35, 1.9, w=3.6)
shelf(3.0, D - 0.35, 2.6, w=3.6)
led_strip(1.2, 4.8, D - 0.37, 1.88, m=NEON_ICE, r=0.012)
led_strip(1.2, 4.8, D - 0.37, 2.58, m=NEON_MAGENTA, r=0.012)
colors = [((0.1, 0.5, 0.2), 0.05, 0.0), ((0.6, 0.35, 0.05), 0.05, 0.0), ((0.5, 0.05, 0.1), 0.05, 0.0), GLASS, ((0.1, 0.2, 0.6), 0.05, 0.0)]
for row, z in ((0, 1.92), (1, 2.62)):
    for i in range(11):
        cyl(0.045, 0.30 + (i % 3) * 0.06, (1.35 + i * 0.33, D - 0.25, z + 0.16), colors[(i + row) % 5], verts=8)
for i in range(3):
    x = 1.8 + i * 1.2
    cyl(0.03, 0.7, (x, D - 1.7, 0.35), METAL_CHROME, verts=8)
    cyl(0.22, 0.08, (x, D - 1.7, 0.74), ((0.35, 0.05, 0.12), 0.7, 0.0), verts=12)
    cyl(0.2, 0.03, (x, D - 1.7, 0.02), METAL_CHROME, verts=12)
neon_palm(0.6, D - 1.1, 0.0, 3.4, m=NEON_HOT, lean=0.1)
neon_palm(11.0, D - 1.3, 0.0, 2.2, m=NEON_ICE, lean=-0.12, fronds=5)
neon_sign("SKY BAR", 0.4, D + 0.0, 3.5, NEON_MAGENTA, cell=0.12, backing=MAT_INK)
neon_tube_frame(0.25, 3.35, 3.35, 4.2, D - 0.02, NEON_ICE, r=0.02)
neon_polygon(1.9, 4.75, D + 0.0, 0.3, 3, NEON_HOT)

# Lounge seats on the right, a DJ booth with a hologram and a speaker stack.
sofa(12.3, D - 1.1, 0.0, w=2.4, m=((0.06, 0.08, 0.24), 0.85, 0.0))
cube((1.4, 0.8, 0.9), (14.0, D - 0.9, 0.45), MAT_INK, bevel=0.0)
cube((1.4, 0.6, 0.04), (14.0, D - 0.9, 0.92), BAR_TOP, bevel=0.0)
for s in (-1, 1):
    cyl(0.22, 0.02, (14.0 + s * 0.35, D - 0.95, 0.95), PLASTIC_BLACK, verts=16)
    cyl(0.18, 0.01, (14.0 + s * 0.35, D - 0.95, 0.965), neon((0.8, 0.8, 0.9), 0.6, (0.2, 0.2, 0.25)), verts=16)
led_strip(13.3, 14.7, D - 1.31, 0.12, m=NEON_MAGENTA)
chevron_strip(13.35, 14.65, 0.55, D - 1.31, m=NEON_ICE, h=0.2)
hologram(14.0, D - 0.9, 0.96, "diamond", "spin_dj", m=NEON_HOT, r=0.22, ring=NEON_ICE)
for i in range(2):
    cube((0.7, 0.6, 0.9), (12.2, D - 0.4, 0.45 + i * 0.95), MAT_INK, bevel=0.0)
    cyl(0.22, 0.05, (12.2, D - 0.72, 0.45 + i * 0.95), PLASTIC_BLACK, rot=(math.pi / 2, 0, 0), verts=14)
    torus(0.24, 0.03, (12.2, D - 0.74, 0.45 + i * 0.95), NEON_CYAN, rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=4)
scanline_screen(12.5, D + 0.0, 2.9, 1.3, 1.5, colour=LAVENDER, frame=NEON_MAGENTA, seed=9)
kanji_sign(13.8, D + 0.0, 1.5, 2.9, m=NEON_ICE, seed=19, w=0.45)
led_column(14.55, D + 0.0, 0.0, 4.6, m=NEON_MAGENTA, alt=NEON_ICE, w=0.2)
horizon_lines(12.0, 14.2, D + 0.0, 4.55, n=3, spacing=0.14, m=NEON_HOT)

# ---- upper wall: a giant "OPEN 24/7" neon, an LED video wall, a sun and a glass rail.
cube((15.0, 0.03, 2.5), (7.5, D + 0.03, 8.25), MAT_NAVY, bevel=0.0)
neon_sign("OPEN", 1.0, D + 0.0, 8.0, NEON_MAGENTA, cell=0.2)
neon_sign("24 7", 4.6, D + 0.0, 8.0, NEON_CYAN, cell=0.2, gap=0.3)
cube((4.4, 0.12, 2.0), (10.6, D + 0.0, 8.3), MAT_INK, bevel=0.0)
for r in range(8):
    for c in range(18):
        k = (r * 31 + c * 17) % 7
        cube((0.2, 0.02, 0.2), (8.55 + c * 0.24, D - 0.07, 7.45 + r * 0.24), [NEON_MAGENTA, NEON_CYAN, NEON_VIOLET, NEON_PINK, NEON_BLUE, NEON_CYAN, NEON_MAGENTA][k], bevel=0.0)
cube((15.0, 0.06, 0.6), (7.5, D - 0.02, 7.3), GLASS, bevel=0.0)
cube((15.0, 0.08, 0.05), (7.5, D - 0.05, 7.62), METAL_CHROME, bevel=0.0)
hline(0.2, 14.8, D - 0.08, 7.0, NEON_ICE, r=0.02)
sunset_mural(14.0, 8.5, D + 0.0, 0.55, frame=NEON_ICE, grid=False)
laser_fan(7.6, D - 0.4, 9.5, m=NEON_MAGENTA, n=5, spread=1.3, length=2.0)
laser_fan(3.0, D - 0.4, 9.5, m=NEON_ICE, n=4, spread=1.0, length=1.6)
star_field(0.0, 15.0, 7.8, 9.4, D + 0.0, n=18, seed=9)
chevron_strip(0.3, 7.9, 9.25, D + 0.0, m=NEON_ICE, h=0.2)

strip_bevels()
join_static("decor")
export("backdrop_rich2")
