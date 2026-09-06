# Backdrop for the gym, synthwave edition: a dark navy hall seamed with mint
# neon, mirrored wall under a "NO PAIN NO GAIN" neon, a grid floor of rubber
# mats, weight racks, treadmills, a bike, a sunset poster, LED columns, a
# hologram trophy turning on a plinth and laser fans over the scoreboard.
#   blender -b --python blender/backdrop_gym.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(0.2, 7.6, 1.6, 1.3), (13.2, 7.6, 1.6, 1.3), (4.2, 4.6, 6.6, 2.2)]
MINT = neon((0.3, 1.0, 0.75), 3.0, (0.03, 0.12, 0.09))
MAT = ((0.04, 0.05, 0.09), 0.9, 0.0)
IRON = ((0.09, 0.09, 0.13), 0.5, 0.7)

# Wall: dark navy panels with mint seams, a hot pink stripe at the dado.
cube((15.0, 0.03, 7.0), (7.5, D + 0.025, 3.5), MAT_NAVY, bevel=0.0)
neon_seams(0.0, 15.0, 0.0, 7.0, D + 0.0, MINT, spacing=1.75, avoid=WINDOWS)
window_neon(WINDOWS[2], D - 0.02, NEON_HOT)
hline(0.2, 14.8, D - 0.01, 3.05, NEON_HOT, r=0.02)
# Floor: glossy slab, rubber mats with neon edges and a cyan grid.
wet_floor(0.0, 15.0, 0.0, D)
for i in range(5):
    cube((2.8, 1.6, 0.03), (1.6 + i * 3.0, D - 0.9, 0.015), MAT, bevel=0.0)
    cube((2.8, 0.03, 0.02), (1.6 + i * 3.0, D - 0.9, 0.035), MINT, bevel=0.0)
grid_floor(0.2, 14.8, 0.08, D - 0.08, z=0.03, m=NEON_ICE, m2=NEON_HOT, nx=10, ny=2)

# Left: weight racks and a bench with a barbell.
weight_rack(1.4, D - 0.6, 0.0, w=2.2)
weight_rack(1.4, D - 0.6, 1.3, w=2.2)
cube((0.4, 1.2, 0.08), (3.6, D - 0.9, 0.5), MAT_PLUM, bevel=0.02)          # bench
for s in (-1, 1):
    cube((0.06, 0.06, 0.45), (3.6, D - 0.9 + s * 0.5, 0.25), IRON, bevel=0.005)
dumbbell(3.6, D - 1.2, 1.15, length=1.8, r=0.22)                             # barbell on the rack
for s in (-1, 1):
    cube((0.06, 0.08, 1.15), (3.6 + s * 0.7, D - 1.2, 0.58), IRON, bevel=0.005)
    cube((0.02, 0.02, 1.1), (3.6 + s * 0.7, D - 1.25, 0.58), NEON_ICE, bevel=0.0)

# Mirror wall with a chrome rail, LED columns and the big neon slogan.
for i in range(4):
    mirror(5.4 + i * 1.15, D + 0.0, 1.55, w=1.1, h=2.2)
neon_tube_frame(4.8, 9.95, 0.42, 2.68, D - 0.03, NEON_HOT, r=0.02)
chrome_trim(4.8, 9.95, D - 0.06, 1.0)
led_column(4.5, D + 0.0, 0.0, 2.9, m=MINT, alt=NEON_HOT)
led_column(10.25, D + 0.0, 0.0, 2.9, m=MINT, alt=NEON_HOT)
neon_sign("NO PAIN", 4.8, D + 0.0, 3.4, NEON_PINK, cell=0.17)
neon_sign("NO GAIN", 9.2, D + 0.0, 3.4, MINT, cell=0.17)
chevron_strip(4.9, 10.1, 4.45, D + 0.0, m=NEON_ICE, h=0.22)

# Centre-right: treadmills and an exercise bike silhouette.
treadmill_silhouette(10.3, D - 1.0, 0.0, m=IRON)
treadmill_silhouette(12.2, D - 1.0, 0.0, m=IRON)
for x in (10.3, 12.2):
    cube((1.4, 0.02, 0.02), (x, D - 1.36, 0.19), NEON_HOT, bevel=0.0)
rod((14.0, D - 1.0, 0.35), (14.4, D - 1.0, 1.1), 0.04, IRON, verts=8)
rod((14.0, D - 1.0, 0.35), (13.5, D - 1.0, 0.9), 0.04, IRON, verts=8)
torus(0.28, 0.04, (13.5, D - 1.0, 0.3), IRON, rot=(math.pi / 2, 0, 0))
torus(0.28, 0.04, (14.5, D - 1.0, 0.3), IRON, rot=(math.pi / 2, 0, 0))
torus(0.2, 0.015, (13.5, D - 1.0, 0.3), NEON_ICE, rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=4)
cube((0.3, 0.2, 0.06), (13.55, D - 1.0, 0.95), PLASTIC_BLACK, bevel=0.02)
cube((0.5, 0.05, 0.3), (14.4, D - 1.0, 1.25), MAT_INK, bevel=0.02)
cube((0.4, 0.02, 0.2), (14.4, D - 1.04, 1.25), SCREEN_ICE, bevel=0.0)
# Hologram trophy on a plinth between the mirrors and the treadmills.
cube((0.5, 0.5, 0.5), (9.9, 0.55, 0.25), MAT_INK, bevel=0.0)
cube((0.5, 0.02, 0.05), (9.9, 0.29, 0.25), NEON_HOT, bevel=0.0)
hologram(9.9, 0.55, 0.5, "diamond", "spin_trophy", m=MINT, r=0.3)

# Sunset poster, wall screen, kanji sign and the exit.
sunset_mural(12.35, 4.85, D + 0.0, 0.8, frame=NEON_HOT, grid=True)
scanline_screen(11.2, D + 0.0, 2.35, 1.4, 0.9, colour=ICE, frame=NEON_ICE, seed=2)
neon_stripe_panel(12.9, 2.35, D + 0.0, 1.5, 0.9, colours=(NEON_HOT, MINT, NEON_ICE))
kanji_sign(14.55, D + 0.0, 1.1, 2.6, m=MINT, seed=5)
exit_sign(0.5, D + 0.0, 4.8)
neon_polygon(2.4, 5.4, D + 0.0, 0.55, 3, NEON_HOT)
neon_polygon(2.4, 5.4, D + 0.0, 0.32, 3, NEON_ICE)
horizon_lines(0.3, 4.0, D + 0.0, 6.2, n=3, spacing=0.14, m=MINT)

# Water cooler and a towel shelf.
cyl(0.18, 0.9, (0.55, D - 0.5, 0.45), MAT_INK, verts=12)
cyl(0.16, 0.5, (0.55, D - 0.5, 1.15), neon((0.3, 0.7, 0.9), 1.0, (0.05, 0.2, 0.3)), verts=12)
shelf(2.4, D - 0.4, 2.6, w=2.2)
for i in range(4):
    cube((0.35, 0.3, 0.14), (1.6 + i * 0.5, D - 0.25, 2.68), [((0.7, 0.7, 0.85), 0.9, 0.0), ((0.9, 0.2, 0.5), 0.9, 0.0)][i % 2], bevel=0.04)

# ---- upper wall: scoreboard, basketball hoop, banners, lasers and stars.
cube((15.0, 0.03, 2.5), (7.5, D + 0.025, 8.25), MAT_NAVY, bevel=0.0)
for w in WINDOWS[:2]:
    window_neon(w, D - 0.02, MINT)
cube((3.2, 0.12, 1.2), (7.5, D + 0.0, 8.2), MAT_INK, bevel=0.03)
neon_sign("24 07", 6.2, D - 0.07, 7.9, NEON_RED, cell=0.12, gap=0.4)
cube((2.8, 0.03, 0.05), (7.5, D - 0.07, 8.72), MINT, bevel=0.0)
neon_tube_frame(5.9, 9.1, 7.6, 8.8, D - 0.07, NEON_HOT, r=0.02)
cube((0.12, 0.12, 1.2), (2.6, D + 0.0, 7.6), METAL_STEEL, bevel=0.01)
cube((1.4, 0.06, 1.0), (2.6, D + 0.0, 8.6), MAT_INK, bevel=0.02)
neon_tube_frame(1.95, 3.25, 8.15, 9.05, D - 0.04, NEON_ICE, r=0.02)
torus(0.28, 0.025, (2.6, D - 0.35, 8.15), NEON_ORANGE, major_segments=20)
for i in range(8):
    a = i / 8.0 * math.tau
    rod((2.6 + math.cos(a) * 0.28, D - 0.35 + math.sin(a) * 0.28, 8.15), (2.6 + math.cos(a) * 0.1, D - 0.35 + math.sin(a) * 0.1, 7.75), 0.008, (WHITE, 0.6, 0.0), verts=4)
for i, c in enumerate([NEON_PINK, MINT, NEON_YELLOW]):
    cube((0.9, 0.04, 1.6), (10.2 + i * 1.15, D + 0.0, 8.3), c, bevel=0.02)
    cube((0.9, 0.05, 0.08), (10.2 + i * 1.15, D - 0.02, 9.12), METAL_DARK, bevel=0.0)
laser_fan(4.6, D - 0.4, 9.5, m=NEON_HOT, n=4, spread=1.1, length=2.0)
laser_fan(9.9, D - 0.4, 9.5, m=MINT, n=4, spread=1.1, length=2.0)
star_field(0.0, 15.0, 7.1, 9.4, D + 0.0, n=18, seed=3, avoid=WINDOWS)
chevron_strip(0.2, 14.8, 7.2, D + 0.0, m=MINT, h=0.26, avoid=WINDOWS)
chrome_trim(0.0, 15.0, D - 0.02, 9.45)

strip_bevels()
join_static("decor")
export("backdrop_gym")
