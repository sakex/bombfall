# Backdrop for the bathroom (toilet1), synthwave edition: glossy navy tiles
# grouted with cyan neon, a hot-pink tile band at eye level, sinks under
# neon-framed mirrors, urinals, plum stall doors with pink edges, a sunset
# poster, a chrome pipe run, a grid floor and a spinning hologram "wet
# floor" sign. 15 m wide.
#   blender -b --python blender/backdrop_toilet1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(7.0, 3.2, 3.6, 1.6), (2.0, 7.9, 2.0, 1.0), (6.5, 7.9, 2.0, 1.0), (11.0, 7.9, 2.0, 1.0)]
TILE = ((0.05, 0.06, 0.16), 0.12, 0.2)
TILE_BAND = neon(HOT_PINK, 1.6, (0.3, 0.06, 0.2))
TILE_ICE = neon(ICE, 0.7, (0.05, 0.18, 0.22))
STALL = ((0.12, 0.04, 0.20), 0.5, 0.0)
PORCELAIN = ((0.62, 0.62, 0.74), 0.3, 0.0)


def tiles(x0, x1, z0, z1, size, m, avoid=()):
    """tile_wall that leaves the window openings empty."""
    nx = int((x1 - x0) / size)
    nz = int((z1 - z0) / size)
    for i in range(nx):
        for j in range(nz):
            cx = x0 + (i + 0.5) * size
            cz = z0 + (j + 0.5) * size
            if any(rx - 0.05 < cx < rx + rw + 0.05 and rz - 0.05 < cz < rz + rh + 0.05 for (rx, rz, rw, rh) in avoid):
                continue
            cube((size - 0.03, 0.04, size - 0.03), (cx, D + 0.0, cz), m, bevel=0.0)


# Tiled wall: big glossy navy tiles with glowing grout lines, a pink band at eye level.
cube((15.0, 0.03, 7.0), (7.5, D + 0.03, 3.5), TILE_ICE, bevel=0.0)          # "grout" glows between the tiles
tiles(0.0, 15.0, 0.0, 1.5, 0.75, TILE)
tiles(0.0, 15.0, 1.5, 2.0, 0.5, TILE_BAND)
tiles(0.0, 15.0, 2.0, 4.5, 0.75, TILE, avoid=WINDOWS)
tiles(0.0, 15.0, 4.5, 4.75, 0.25, TILE_BAND, avoid=WINDOWS)
tiles(0.0, 15.0, 4.75, 7.0, 0.75, TILE)
window_neon(WINDOWS[0], D - 0.03, NEON_HOT)
cube((15.0, 0.5, 0.06), (7.5, D - 0.25, 0.03), MAT_INK, bevel=0.0)          # skirting/floor edge
wet_floor(0.0, 15.0, 0.0, D - 0.5)
grid_floor(0.2, 14.8, 0.1, D - 0.55, z=0.02, m=NEON_ICE, m2=NEON_HOT, nx=10, ny=2)

# Sinks under neon-framed mirrors, with soap dispensers and a hand dryer.
for i in range(3):
    x = 1.4 + i * 1.3
    sink(x, D - 0.4, 0.0, m=PORCELAIN)
    mirror(x, D - 0.02, 2.0, w=0.9, h=1.1, frame=METAL_CHROME)
    neon_tube_frame(x - 0.5, x + 0.5, 1.4, 2.6, D - 0.06, NEON_HOT if i % 2 else NEON_ICE, r=0.02)
led_strip(0.8, 4.6, D - 0.45, 0.95, m=NEON_ICE, r=0.015)                     # under-counter glow
cube((0.16, 0.12, 0.28), (5.4, D - 0.08, 1.5), PORCELAIN, bevel=0.0)
cube((0.08, 0.05, 0.10), (5.4, D - 0.16, 1.4), NEON_CYAN, bevel=0.0)
cube((0.4, 0.3, 0.45), (6.2, D - 0.15, 1.35), CHROME_M, bevel=0.04)          # hand dryer
cube((0.2, 0.05, 0.05), (6.2, D - 0.33, 1.2), NEON_BLUE, bevel=0.0)
for i in range(2):
    cube((0.12, 0.08, 0.2), (0.6 + i * 0.25, D - 0.06, 2.3), NEON_SUN, bevel=0.0)  # soap bottles

# Urinals and stall doors with neon edges and vacant/engaged lights.
for i in range(3):
    urinal(7.6 + i * 0.9, D - 0.2, 0.0, m=PORCELAIN)
    cube((0.05, 0.6, 1.1), (7.15 + i * 0.9, D - 0.3, 0.9), STALL, bevel=0.0)
    cube((0.02, 0.02, 1.0), (7.15 + i * 0.9, D - 0.62, 0.9), NEON_ICE, bevel=0.0)
for i in range(3):
    x = 10.9 + i * 1.3
    cube((1.2, 0.06, 2.0), (x, D - 1.0, 1.25), STALL, bevel=0.0)
    neon_tube_frame(x - 0.55, x + 0.55, 0.3, 2.2, D - 1.04, NEON_HOT, r=0.015)
    cube((0.05, 0.9, 2.2), (x - 0.62, D - 0.55, 1.35), STALL, bevel=0.0)
    sphere(0.04, (x + 0.45, D - 1.05, 1.15), METAL_CHROME, segments=8, rings=6)
    cube((0.3, 0.02, 0.12), (x, D - 1.05, 2.05), [NEON_GREEN, NEON_RED, NEON_GREEN][i], bevel=0.0)  # vacant/engaged
cube((0.05, 0.9, 2.2), (14.48, D - 0.55, 1.35), STALL, bevel=0.0)
neon_sign("WC", 12.3, D + 0.0, 3.2, NEON_CYAN, cell=0.2, backing=MAT_INK)
neon_tube_frame(12.1, 13.6, 3.05, 4.35, D - 0.03, NEON_HOT, r=0.02)
kanji_sign(14.5, D + 0.0, 2.6, 2.6, m=NEON_HOT, seed=14, w=0.45)
sunset_mural(3.4, 4.2, D + 0.0, 0.75, frame=NEON_ICE)
neon_polygon(5.7, 4.0, D + 0.0, 0.45, 3, NEON_HOT)
horizon_lines(0.3, 1.9, D + 0.0, 3.6, n=4, spacing=0.14, m=NEON_HOT)
horizon_lines(11.0, 14.0, D + 0.0, 5.3, n=4, spacing=0.14, m=NEON_ICE)
chevron_strip(0.2, 14.8, 6.4, D + 0.0, m=NEON_HOT, h=0.24)

# Hologram wet-floor sign, mop bucket, a roll of paper.
hologram(6.7, 0.5, 0.0, "diamond", "spin_wetfloor", m=NEON_SUN, r=0.3, ring=NEON_ICE)
cyl(0.22, 0.4, (14.5, D - 1.3, 0.2), ((0.6, 0.55, 0.1), 0.5, 0.0), verts=12)
rod((14.4, D - 1.3, 0.3), (14.6, D - 1.4, 1.6), 0.02, (WOOD_LIGHT, 0.8, 0.0), verts=6)
cone(0.28, 0.7, (0.6, D - 1.4, 0.35), NEON_SUN, verts=4)
cube((0.2, 0.02, 0.1), (0.6, D - 1.55, 0.35), DARK, bevel=0.0)
cyl(0.12, 0.12, (9.9, D - 0.15, 1.3), ((0.7, 0.7, 0.8), 0.6, 0.0), rot=(0, math.pi / 2, 0), verts=12)
pipe_run(0.2, 14.8, D - 0.05, 5.6, r=0.06, m=METAL_CHROME, drops=(1.4, 2.7, 4.0, 7.6, 8.5, 9.4))

# ---- upper wall: more tiles, neon-lined windows, an extractor and pipe work.
cube((15.0, 0.03, 2.5), (7.5, D + 0.03, 8.25), TILE_ICE, bevel=0.0)
tiles(0.0, 15.0, 7.0, 7.25, 0.25, TILE_BAND)
tiles(0.0, 15.0, 7.25, 9.5, 0.75, TILE, avoid=WINDOWS)
for w in WINDOWS[1:]:
    window_neon(w, D - 0.03, NEON_ICE)
cyl(0.35, 0.12, (14.0, D - 0.05, 7.8), METAL_DARK, rot=(math.pi / 2, 0, 0), verts=16)
for i in range(4):
    cube((0.55, 0.05, 0.03), (14.0, D - 0.12, 7.8), METAL_STEEL, rot=(0, i * 0.785, 0), bevel=0.0)
torus(0.4, 0.02, (14.0, D - 0.1, 7.8), NEON_HOT, rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=4)
pipe_run(0.2, 14.8, D - 0.1, 9.2, r=0.08, m=METAL_CHROME, drops=(1.4, 4.0, 10.9, 13.5))
neon_sign("WASH", 0.4, D + 0.0, 7.5, NEON_CYAN, cell=0.12, backing=MAT_INK)
laser_fan(9.75, D - 0.4, 9.5, m=NEON_HOT, n=4, spread=1.0, length=1.9)
laser_fan(5.25, D - 0.4, 9.5, m=NEON_ICE, n=4, spread=1.0, length=1.9)
chevron_strip(4.4, 6.1, 8.4, D + 0.0, m=NEON_HOT, h=0.22)
chevron_strip(8.9, 10.6, 8.4, D + 0.0, m=NEON_ICE, h=0.22)

strip_bevels()
join_static("decor")
export("backdrop_toilet1")
