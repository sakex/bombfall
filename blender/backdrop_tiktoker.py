# Backdrop for the influencer studio (tiktoker), synthwave edition: a
# hot-pink LED-framed plum wall, shelves of vinyl, a ring light and phone
# tripod aimed at a plush bed under a neon cloud, a neon palm, a "LIVE"
# sign, a sunset poster, a wardrobe rail, a vanity with bulbs and a spinning
# holo-heart, plus a giant neon heart and lasers up top. 15 m wide.
#   blender -b --python blender/backdrop_tiktoker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(5.0, 4.0, 4.0, 2.2), (9.6, 4.6, 2.2, 1.6)]
PLUSH = ((0.55, 0.12, 0.38), 0.9, 0.0)
PINK_M = neon((1.0, 0.35, 0.7), 2.0, (0.3, 0.08, 0.2))
BALLOON = [((0.9, 0.2, 0.4), 0.3, 0.0), ((1.0, 0.7, 0.1), 0.3, 0.0), ((0.3, 0.6, 1.0), 0.3, 0.0)]
WALLP = ((0.13, 0.03, 0.15), 0.8, 0.0)

# Wall: dark magenta-plum with pink seams, LED strips framing it, wet grid floor.
cube((15.0, 0.03, 7.0), (7.5, D + 0.03, 3.5), WALLP, bevel=0.0)
neon_seams(0.0, 15.0, 0.0, 7.0, D + 0.0, NEON_HOT, spacing=1.75, avoid=WINDOWS, r=0.012)
led_strip(0.2, 14.8, D + 0.0, 0.25, m=NEON_PINK)
hline(0.2, 14.8, D + 0.0, 6.7, NEON_PINK, r=0.02)
for x in (0.2, 14.8):
    rod((x, D + 0.0, 0.25), (x, D + 0.0, 6.7), 0.02, NEON_PINK, verts=6)
for w in WINDOWS:
    window_neon(w, D - 0.02, NEON_ICE)
wet_floor(0.0, 15.0, 0.0, D, m=GLOSS_PLUM)
grid_floor(0.2, 14.8, 0.1, D - 0.1, m=NEON_HOT, m2=NEON_ICE, nx=10, ny=3)

# Left: shelves with records, plants and a vinyl player.
for z in (1.3, 2.1, 2.9):
    shelf(2.0, D - 0.4, z, w=3.2)
    led_strip(0.45, 3.55, D - 0.42, z - 0.02, m=NEON_ICE, r=0.012)
for i in range(14):
    cube((0.03, 0.3, 0.3), (0.6 + i * 0.2, D - 0.2, 1.47), [((0.1, 0.1, 0.12), 0.6, 0.0), ((0.8, 0.2, 0.3), 0.6, 0.0), ((0.6, 0.55, 0.8), 0.6, 0.0)][i % 3], bevel=0.0)
cube((0.5, 0.35, 0.12), (1.0, D - 0.25, 2.16), MAT_INK, bevel=0.0)
cyl(0.16, 0.01, (1.0, D - 0.25, 2.23), PLASTIC_BLACK, verts=16)
plant(2.4, D - 0.25, 2.12, size=0.6)
plant(3.2, D - 0.25, 2.92, size=0.5)
for i in range(5):
    cyl(0.05, 0.16 + (i % 2) * 0.05, (1.2 + i * 0.35, D - 0.25, 3.0), [PINK_M, ((0.9, 0.9, 0.95), 0.3, 0.0), NEON_CYAN][i % 3], verts=8)
neon_sign("LIVE", 0.8, D + 0.0, 4.3, NEON_RED, cell=0.18, backing=MAT_INK)
sphere(0.1, (2.9, D + 0.0, 4.65), NEON_RED, segments=8, rings=6)
neon_tube_frame(0.6, 3.2, 4.15, 5.3, D - 0.02, NEON_ICE, r=0.02)
sunset_mural(4.2, 5.75, D + 0.0, 0.5, frame=NEON_ICE, grid=False)
horizon_lines(0.5, 3.3, D + 0.0, 5.6, n=4, spacing=0.14, m=NEON_HOT)
neon_palm(4.1, D - 1.3, 0.0, 2.7, m=NEON_HOT, lean=-0.1)

# Centre: bed with pillows facing the ring light and tripod.
bed_flat(7.0, D - 1.7, 0.0, w=2.6, d=1.5, m=PLUSH, sheet=((0.75, 0.7, 0.85), 0.9, 0.0), frame=MAT_INK)
led_strip(5.7, 8.3, D - 0.2, 1.11, m=NEON_ICE, r=0.015)
for i in range(3):
    sphere(0.22, (6.2 + i * 0.5, D - 0.6, 0.78), [PINK_M, ((0.75, 0.7, 0.85), 0.9, 0.0), ((0.5, 0.25, 0.8), 0.9, 0.0)][i], scale=(1.2, 0.8, 0.9), segments=8, rings=6)
ring_light(9.6, D - 1.4, 0.0)
phone_tripod(10.4, D - 1.4, 0.0)
# Neon cloud and lightning above the bed.
for i, (x, r) in enumerate([(6.0, 0.35), (6.5, 0.5), (7.1, 0.45), (7.6, 0.32)]):
    torus(r, 0.03, (x, D + 0.0, 3.2 + (i % 2) * 0.15), NEON_CYAN, rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=6)
cube((1.9, 0.05, 0.06), (6.8, D + 0.0, 2.85), NEON_CYAN, bevel=0.0)
rod((7.3, D + 0.0, 2.8), (7.05, D + 0.0, 2.35), 0.025, NEON_YELLOW, verts=6)
rod((7.05, D + 0.0, 2.35), (7.35, D + 0.0, 2.35), 0.025, NEON_YELLOW, verts=6)
rod((7.35, D + 0.0, 2.35), (7.0, D + 0.0, 1.8), 0.025, NEON_YELLOW, verts=6)
chevron_strip(8.3, 10.2, 2.5, D + 0.0, m=NEON_HOT, h=0.22)
scanline_screen(9.3, D + 0.0, 3.3, 1.6, 0.9, colour=HOT_PINK, frame=NEON_ICE, seed=11)
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
    c = [((0.9, 0.3, 0.5), 0.8, 0.0), ((0.2, 0.2, 0.25), 0.8, 0.0), ((0.7, 0.65, 0.85), 0.8, 0.0), ((0.4, 0.2, 0.7), 0.8, 0.0), ((0.1, 0.5, 0.6), 0.8, 0.0)][i % 5]
    cube((0.28, 0.12, 0.9 + (i % 3) * 0.25), (x, D - 0.5, 1.75 - (i % 3) * 0.12), c, bevel=0.0)
    rod((x, D - 0.5, 2.3), (x, D - 0.5, 2.2), 0.01, METAL_CHROME, verts=4)
desk(13.0, D - 1.2, 0.0, w=1.9, d=0.6, m=MAT_PLUM, legs=METAL_CHROME)
led_strip(12.1, 13.9, D - 1.22, 0.74, m=NEON_HOT, r=0.012)
mirror(13.0, D - 0.45, 4.1, w=1.5, h=1.6, frame=METAL_CHROME)
neon_tube_frame(12.2, 13.8, 3.25, 4.95, D - 0.5, NEON_HOT, r=0.02)
for i in range(6):
    sphere(0.06, (12.3 + i * 0.28, D - 0.5, 4.95), NEON_YELLOW, segments=8, rings=6)
    sphere(0.06, (12.3 + i * 0.28, D - 0.5, 3.25), NEON_YELLOW, segments=8, rings=6)
for i in range(4):
    cyl(0.035, 0.12 + (i % 3) * 0.05, (12.3 + i * 0.22, D - 1.35, 0.84), [PINK_M, METAL_GOLD, (WHITE, 0.3, 0.0)][i % 3], verts=8)
hologram(13.5, D - 1.3, 0.81, "heart", "spin_heart", m=NEON_HOT, r=0.2, ring=NEON_ICE)
kanji_sign(10.6, D + 0.0, 0.7, 2.4, m=NEON_ICE, seed=23, w=0.45)
led_column(14.55, D + 0.0, 2.5, 3.9, m=NEON_HOT, alt=NEON_ICE, w=0.2)
horizon_lines(11.9, 14.2, D + 0.0, 5.3, n=4, spacing=0.14, m=NEON_ICE)

# ---- upper wall: a giant neon heart, a "SUBSCRIBE" sign, floating shelves and lasers.
cube((15.0, 0.03, 2.5), (7.5, D + 0.03, 8.25), WALLP, bevel=0.0)
for i, (x, z) in enumerate([(3.0, 8.1), (3.3, 8.5), (2.7, 8.5)]):
    torus(0.42 if i else 0.0001, 0.035, (x, D + 0.0, z), NEON_PINK, rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=6)
rod((2.25, D + 0.0, 8.35), (3.0, D + 0.0, 7.4), 0.035, NEON_PINK, verts=8)
rod((3.75, D + 0.0, 8.35), (3.0, D + 0.0, 7.4), 0.035, NEON_PINK, verts=8)
neon_sign("SUBSCRIBE", 5.2, D + 0.0, 7.9, NEON_CYAN, cell=0.15, backing=MAT_INK)
neon_tube_frame(5.05, 10.05, 7.75, 8.75, D - 0.02, NEON_HOT, r=0.02)
for z in (7.4, 8.4):
    shelf(12.5, D - 0.3, z, w=3.0, m=MAT_INK)
    led_strip(11.05, 13.95, D - 0.32, z - 0.02, m=NEON_ICE, r=0.012)
for i in range(6):
    sphere(0.16, (11.3 + i * 0.5, D - 0.15, 7.6), [NEON_PINK, NEON_YELLOW, NEON_CYAN][i % 3], scale=(1, 1, 1.2), segments=8, rings=6)
for i in range(4):
    cube((0.5, 0.25, 0.4), (11.4 + i * 0.75, D - 0.15, 8.62), [((0.7, 0.65, 0.85), 0.4, 0.0), ((0.9, 0.3, 0.5), 0.4, 0.0)][i % 2], bevel=0.0)
led_strip(0.2, 14.8, D + 0.0, 9.3, m=NEON_PINK)
laser_fan(3.0, D - 0.4, 9.5, m=NEON_HOT, n=5, spread=1.4, length=1.8)
laser_fan(7.5, D - 0.4, 9.5, m=NEON_ICE, n=4, spread=1.0, length=1.3)
star_field(0.0, 15.0, 7.1, 9.2, D + 0.0, n=20, seed=17)
chevron_strip(0.4, 14.6, 7.1, D + 0.0, m=NEON_ICE, h=0.22)

strip_bevels()
join_static("decor")
export("backdrop_tiktoker")
