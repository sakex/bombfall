# Backdrop for the hotel bedroom (room1), synthwave edition: dark plum wall
# panels seamed with violet neon, a striped sunset mural over the bed, a
# neon-framed headboard, a wall screen, neon palms by the wardrobe, a grid
# floor and a little hologram globe turning on the mini bar. 15 m wide.
#   blender -b --python blender/backdrop_room1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
# Window openings the game cuts into the wall (x, z, w, h), see SpawnRegistry.
WINDOWS = [(0.9, 2.1, 3.4, 2.6), (1.1, 7.4, 3.0, 1.5), (8.9, 7.4, 3.0, 1.5)]
LAMP = neon((1.0, 0.7, 0.5), 2.0, (0.4, 0.25, 0.15))
VELVET = ((0.32, 0.04, 0.16), 0.9, 0.0)
DARK_WOOD = ((0.12, 0.06, 0.10), 0.7, 0.0)

# Wall panels: dark plum with violet neon seams, a chrome picture rail.
for i in range(15):
    cube((0.9, 0.03, 6.8), (0.5 + i * 1.0, D + 0.02, 3.4), MAT_PLUM if i % 2 else MAT_INK, bevel=0.0)
neon_seams(0.0, 15.0, 0.0, 7.0, D + 0.0, NEON_LAV, spacing=1.75, avoid=WINDOWS)
chrome_trim(0.0, 15.0, D - 0.02, 2.6)
for w in WINDOWS[:1]:
    window_neon(w, D - 0.02, NEON_HOT)
# Floor: glossy dark slab with a pink/violet grid.
wet_floor(0.0, 15.0, 0.0, D, m=GLOSS_PLUM)
grid_floor(0.2, 14.8, 0.1, D - 0.1, m=NEON_HOT, m2=NEON_LAV, nx=10, ny=3)

# Window with velvet curtains and a chrome rail.
for s in (-1, 1):
    cube((0.6, 0.25, 3.0), (2.6 + s * 2.05, D - 0.15, 3.3), VELVET, bevel=0.06)
chrome_trim(0.2, 5.0, D - 0.2, 4.95)

# Bed with a neon-framed headboard, pillows and lamps on nightstands.
bed_flat(8.2, D - 1.6, 0.0, w=2.8, d=1.6, m=((0.18, 0.05, 0.28), 0.9, 0.0), sheet=((0.75, 0.72, 0.85), 0.9, 0.0), frame=DARK_WOOD)
cube((3.2, 0.14, 1.4), (8.2, D - 0.07, 1.0), DARK_WOOD, bevel=0.04)
neon_tube_frame(6.65, 9.75, 0.35, 1.65, D - 0.16, NEON_HOT, r=0.03)
for i in range(4):
    cube((0.7, 0.10, 0.4), (7.2 + (i % 2) * 2.0, D - 0.16, 0.9 + (i // 2) * 0.45), MAT_GRAPE, bevel=0.05)
for s in (-1, 1):
    x = 8.2 + s * 2.0
    cube((0.6, 0.5, 0.6), (x, D - 0.3, 0.3), DARK_WOOD, bevel=0.02)
    cube((0.6, 0.02, 0.05), (x, D - 0.56, 0.5), NEON_LAV, bevel=0.0)
    cyl(0.03, 0.35, (x, D - 0.3, 0.78), CHROME_M, verts=8)
    cyl(0.2, 0.25, (x, D - 0.3, 1.05), LAMP, r2=0.14, verts=12)
cube((0.4, 0.3, 0.02), (6.2, D - 0.3, 0.61), ((0.6, 0.6, 0.75), 0.6, 0.0), bevel=0.0)   # book
cyl(0.06, 0.16, (10.4, D - 0.35, 0.69), GLASS, verts=8)                               # water glass
# The sunset mural above the bed.
sunset_mural(8.2, 4.1, D + 0.0, 1.05, frame=NEON_LAV)

# Wardrobe with a neon edge, mini bar with a hologram, wall screen, coat rack.
cube((1.6, 0.6, 2.6), (12.2, D - 0.3, 1.3), DARK_WOOD, bevel=0.03)
cube((0.03, 0.02, 2.4), (12.2, D - 0.61, 1.3), NEON_ICE, bevel=0.0)
for s in (-1, 1):
    cube((0.04, 0.05, 0.3), (12.2 + s * 0.12, D - 0.63, 1.3), CHROME_M, bevel=0.005)
neon_tube_frame(11.4, 13.0, 0.02, 2.6, D - 0.62, NEON_HOT, r=0.02)
cube((1.0, 0.6, 0.9), (14.0, D - 0.3, 0.45), MAT_INK, bevel=0.02)
cube((0.6, 0.02, 0.5), (14.0, D - 0.61, 0.45), SCREEN_ICE, bevel=0.0)
for i in range(3):
    cube((0.5, 0.01, 0.03), (14.0, D - 0.625, 0.3 + i * 0.15), NEON_ICE, bevel=0.0)
hologram(14.0, D - 0.3, 0.9, "globe", "spin_holo", m=NEON_ICE, r=0.28)
cyl(0.05, 0.08, (13.55, D - 0.3, 0.94), (WHITE, 0.3, 0.0), verts=8)
scanline_screen(13.0, D + 0.0, 3.6, 1.5, 0.95, colour=SUN_ORANGE, frame=NEON_SUN, seed=4)
neon_palm(11.0, D - 0.15, 0.0, 2.7, m=NEON_HOT, lean=-0.1)
neon_palm(14.6, D - 0.15, 0.0, 2.4, m=NEON_LAV, lean=-0.14, fronds=5)
rod((0.6, D - 0.4, 0.0), (0.6, D - 0.4, 1.9), 0.03, CHROME_M, verts=8)
for a in range(4):
    ang = a * math.pi / 2
    rod((0.6, D - 0.4, 1.85), (0.6 + math.cos(ang) * 0.25, D - 0.4 + math.sin(ang) * 0.25, 1.95), 0.015, CHROME_M, verts=6)
cube((0.3, 0.12, 0.8), (0.78, D - 0.5, 1.45), VELVET, bevel=0.04)
neon_sign("4 2 7", 5.6, D + 0.0, 5.8, NEON_SUN, cell=0.16, gap=0.3, backing=MAT_INK)
neon_tube_frame(5.45, 7.85, 5.65, 6.75, D - 0.02, NEON_ICE, r=0.02)
kanji_sign(0.45, D + 0.0, 5.0, 1.9, m=NEON_HOT, seed=7)
horizon_lines(10.6, 14.9, D + 0.0, 5.3, n=4, spacing=0.14, m=NEON_HOT)
pipe_run(0.2, 14.8, D - 0.15, 6.88, r=0.06, m=METAL_DARK, drops=(2.5, 9.0))

# ---- upper wall: high windows with curtains, an AC unit, stars and lasers.
for i in range(15):
    cube((0.9, 0.03, 2.5), (0.5 + i * 1.0, D + 0.02, 8.25), MAT_PLUM if i % 2 else MAT_INK, bevel=0.0)
for w in WINDOWS[1:]:
    window_neon(w, D - 0.02, NEON_LAV)
for x in (2.6, 10.4):
    for s in (-1, 1):
        cube((0.5, 0.22, 2.4), (x + s * 1.9, D - 0.12, 8.4), VELVET, bevel=0.06)
cube((1.6, 0.5, 0.7), (6.5, D - 0.25, 8.9), (SLATE, 0.5, 0.3), bevel=0.04)
for i in range(6):
    cube((1.4, 0.04, 0.03), (6.5, D - 0.52, 8.62 + i * 0.1), MAT_INK, bevel=0.0)
cube((0.16, 0.03, 0.05), (7.1, D - 0.52, 9.2), NEON_GREEN, bevel=0.0)
star_field(0.0, 15.0, 7.2, 9.4, D + 0.0, n=26, seed=11, avoid=WINDOWS)
laser_fan(7.5, D - 0.4, 9.5, m=NEON_HOT, n=5, spread=1.4, length=2.2)
led_column(13.4, D + 0.0, 7.1, 2.3, m=NEON_ICE, alt=NEON_HOT)
led_column(14.4, D + 0.0, 7.1, 2.3, m=NEON_LAV, alt=NEON_HOT)
chevron_strip(0.2, 14.8, 7.1, D + 0.0, m=NEON_LAV, h=0.28, avoid=WINDOWS)
pipe_run(0.2, 14.8, D - 0.2, 7.5, r=0.07, m=METAL_DARK, drops=(7.5,))
chrome_trim(0.0, 15.0, D - 0.02, 9.45)

strip_bevels()
join_static("decor")
export("backdrop_room1")
