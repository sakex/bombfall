# Backdrop for the penthouse lounge (rich1), synthwave edition: obsidian
# wainscoting under a gold rail, chrome columns ringed with neon, a velvet
# sofa on a rug with a hologram globe on the coffee table, a fireplace with
# a glowing hearth, a bookshelf, a bar cart, a neon palm, a wall screen and
# a huge sunset mural over the mezzanine. 15 m wide.
#   blender -b --python blender/backdrop_rich1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(1.7, 2.0, 4.6, 2.6), (1.5, 7.7, 2.2, 1.2), (11.3, 7.7, 2.2, 1.2)]
VELVET = ((0.30, 0.04, 0.14), 0.85, 0.0)
OBSIDIAN = ((0.05, 0.03, 0.09), 0.25, 0.3)
EMBER = neon((1.0, 0.45, 0.1), 3.0, (0.3, 0.1, 0.02))
GOLD_N = neon((1.0, 0.8, 0.3), 3.0)
WARM = neon((1.0, 0.75, 0.4), 2.0, (0.35, 0.25, 0.12))

# Wall: deep plum with gold rail, obsidian wainscot panels edged in violet neon.
cube((15.0, 0.03, 7.0), (7.5, D + 0.03, 3.5), MAT_PLUM, bevel=0.0)
cube((15.0, 0.05, 0.06), (7.5, D + 0.0, 1.2), METAL_GOLD, bevel=0.0)
hline(0.2, 14.8, D - 0.02, 1.27, NEON_LAV, r=0.015)
for i in range(10):
    cube((1.2, 0.04, 0.9), (0.9 + i * 1.5, D + 0.01, 0.62), OBSIDIAN, bevel=0.0)
    neon_tube_frame(0.4 + i * 1.5, 1.4 + i * 1.5, 0.22, 1.02, D - 0.015, NEON_LAV if i % 2 else NEON_HOT, r=0.012)
neon_seams(0.0, 15.0, 1.3, 7.0, D + 0.0, NEON_LAV, spacing=1.9, avoid=WINDOWS, r=0.012)
window_neon(WINDOWS[0], D - 0.02, GOLD_N)
for x, r in ((0.6, 0.3), (14.4, 0.3), (7.5, 0.25)):
    column(x, D - 0.3, 0.0, h=6.6, r=r, m=CHROME_M, cap=METAL_GOLD)
    for zz in (1.6, 3.4, 5.2):
        torus(r + 0.05, 0.025, (x, D - 0.3, zz), NEON_HOT if zz != 3.4 else NEON_ICE, major_segments=16, minor_segments=4)
# Floor: glossy plum with a gold/pink grid.
wet_floor(0.0, 15.0, 0.0, D, m=GLOSS_PLUM)
grid_floor(0.2, 14.8, 0.1, D - 0.1, m=GOLD_N, m2=NEON_HOT, nx=10, ny=3)

# Art wall: a neon triangle piece, a wall screen and neon sconces.
neon_polygon(10.0, 3.5, D + 0.0, 0.75, 3, NEON_HOT)
neon_polygon(10.0, 3.4, D + 0.0, 0.45, 3, GOLD_N, rot=math.pi)
neon_polygon(10.0, 3.5, D + 0.0, 0.2, 3, NEON_ICE)
scanline_screen(12.3, D + 0.0, 3.6, 1.5, 1.4, colour=(1.0, 0.7, 0.3), frame=GOLD_N, seed=7)
kanji_sign(13.7, D + 0.0, 3.1, 2.4, m=GOLD_N, seed=17, w=0.4)
horizon_lines(8.3, 11.7, D + 0.0, 5.2, n=4, spacing=0.14, m=NEON_HOT)
for x in (8.8, 13.3):
    cube((0.16, 0.16, 0.3), (x, D - 0.08, 2.6), METAL_GOLD, bevel=0.0)
    sphere(0.09, (x, D - 0.16, 2.82), NEON_YELLOW, segments=10, rings=8)
neon_arch(8.8, 5.6, D + 0.0, 0.6, m=GOLD_N, segments=8)

# Sofa on a rug, a coffee table with a hologram globe, a lamp.
rug(4.6, D - 1.0, 0.0, w=4.2, d=1.7, m=((0.22, 0.03, 0.10), 0.9, 0.0), border=GOLD_N)
sofa(4.6, D - 1.1, 0.0, w=2.6, m=VELVET)
led_strip(3.3, 5.9, D - 1.12, 0.08, m=NEON_HOT, r=0.015)
cube((1.1, 0.6, 0.04), (4.6, D - 1.55, 0.42), OBSIDIAN, bevel=0.0)                        # glass table top
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((4.6 + sx * 0.5, D - 1.55 + sy * 0.25, 0.0), (4.6 + sx * 0.5, D - 1.55 + sy * 0.25, 0.4), 0.02, METAL_GOLD, verts=6)
hologram(4.6, D - 1.55, 0.44, "globe", "spin_globe", m=NEON_ICE, r=0.26, ring=GOLD_N)
cyl(0.04, 1.5, (6.6, D - 1.0, 0.75), METAL_GOLD, verts=8)
cyl(0.28, 0.35, (6.6, D - 1.0, 1.65), WARM, r2=0.22, verts=14)

# Fireplace with a glowing hearth and a mantel.
cube((2.0, 0.5, 1.5), (9.9, D - 0.25, 0.75), OBSIDIAN, bevel=0.0)
neon_tube_frame(8.95, 10.85, 0.05, 1.45, D - 0.51, NEON_SUN, r=0.015)
cube((1.2, 0.3, 1.0), (9.9, D - 0.45, 0.55), DARK, bevel=0.0)
for i in range(3):
    cyl(0.08, 0.5, (9.6 + i * 0.3, D - 0.55, 0.2 + (i % 2) * 0.1), (WOOD, 0.9, 0.0), rot=(0, 0.4 * (i - 1), 0.3), verts=8)
sphere(0.25, (9.9, D - 0.6, 0.3), EMBER, scale=(1.6, 0.8, 0.9), segments=10, rings=8)
cube((2.3, 0.6, 0.1), (9.9, D - 0.3, 1.55), METAL_GOLD, bevel=0.0)
cyl(0.12, 0.35, (9.3, D - 0.35, 1.78), METAL_GOLD, verts=10)                                    # trophy
sphere(0.16, (9.3, D - 0.35, 2.05), METAL_GOLD, segments=10, rings=8)
cube((0.5, 0.25, 0.4), (10.5, D - 0.35, 1.8), OBSIDIAN, bevel=0.0)                              # clock box
wall_clock(10.5, D - 0.48, 1.8, r=0.16)

# Bookshelf, a bar cart and a neon palm.
bookshelf(12.6, D - 0.4, 0.0, w=1.8, h=2.6, m=OBSIDIAN)
led_strip(11.75, 13.45, D - 0.62, 2.62, m=NEON_HOT, r=0.012)
cube((0.9, 0.5, 0.04), (1.9, D - 1.0, 0.75), METAL_GOLD, bevel=0.0)
cube((0.9, 0.5, 0.04), (1.9, D - 1.0, 0.3), METAL_GOLD, bevel=0.0)
for sx in (-1, 1):
    rod((1.9 + sx * 0.42, D - 1.0, 0.05), (1.9 + sx * 0.42, D - 1.0, 0.8), 0.015, METAL_GOLD, verts=6)
for i in range(4):
    cyl(0.05, 0.32, (1.6 + i * 0.2, D - 1.05, 0.93), [((0.1, 0.4, 0.2), 0.1, 0.0), ((0.5, 0.3, 0.05), 0.1, 0.0), ((0.4, 0.05, 0.05), 0.1, 0.0), GLASS][i], verts=8)
neon_palm(14.1, D - 1.1, 0.0, 2.6, m=NEON_HOT, lean=-0.12)
neon_palm(1.0, D - 0.2, 4.9, 1.7, m=GOLD_N, lean=0.1, fronds=5)

# ---- upper wall: a mezzanine rail, neon-lined windows and a huge sunset.
cube((15.0, 0.03, 2.5), (7.5, D + 0.03, 8.25), MAT_PLUM, bevel=0.0)
cube((15.0, 0.08, 0.10), (7.5, D + 0.0, 7.05), METAL_GOLD, bevel=0.0)
for i in range(38):
    rod((0.2 + i * 0.4, D - 0.05, 7.1), (0.2 + i * 0.4, D - 0.05, 7.9), 0.02, METAL_GOLD, verts=6)
cube((15.0, 0.08, 0.06), (7.5, D - 0.05, 7.92), METAL_GOLD, bevel=0.0)
hline(0.2, 14.8, D - 0.1, 7.0, NEON_HOT, r=0.02)
for w in WINDOWS[1:]:
    window_neon(w, D - 0.02, GOLD_N)
sunset_mural(7.5, 8.55, D + 0.0, 0.95, frame=GOLD_N, grid=False, bands=9)
laser_fan(4.7, D - 0.4, 9.5, m=NEON_HOT, n=4, spread=1.0, length=1.8)
laser_fan(10.3, D - 0.4, 9.5, m=GOLD_N, n=4, spread=1.0, length=1.8)
star_field(0.0, 15.0, 7.4, 9.4, D + 0.0, n=20, seed=13, m=neon((1.0, 0.9, 0.7), 2.5, (0.3, 0.28, 0.2)), avoid=WINDOWS)
chevron_strip(0.3, 14.7, 9.25, D + 0.0, m=GOLD_N, h=0.2)

strip_bevels()
join_static("decor")
export("backdrop_rich1")
