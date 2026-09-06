# Backdrop for the staff dorm (room2), synthwave edition: a navy wall with
# a blue neon dado, a bunk bed with LED rails, lockers, a vending machine, a
# scanline wall TV, a clock, a radiator, a noticeboard, a kanji sign, a
# sunset poster, a grid floor, a spinning holo-cube and neon-lined windows,
# ducts and lasers up top. 15 m wide.
#   blender -b --python blender/backdrop_room2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
WINDOWS = [(3.0, 4.7, 4.0, 1.9), (1.1, 7.6, 2.6, 1.1), (6.2, 7.6, 2.6, 1.1), (11.3, 7.6, 2.6, 1.1)]
PAINT = ((0.05, 0.07, 0.20), 0.9, 0.0)
NOTE = [((0.95, 0.9, 0.5), 0.9, 0.0), ((0.6, 0.9, 0.95), 0.9, 0.0), ((0.95, 0.6, 0.7), 0.9, 0.0), ((0.8, 0.8, 0.9), 0.9, 0.0)]
BLUE_N = neon((0.4, 0.55, 1.0), 4.0)
DORM_ICE = neon(ICE, 3.5)

# Wall: painted navy dado under a chrome rail, dark upper panels with blue seams.
cube((15.0, 0.03, 7.0), (7.5, D + 0.03, 3.5), MAT_NAVY, bevel=0.0)
cube((15.0, 0.04, 1.4), (7.5, D + 0.015, 0.7), PAINT, bevel=0.0)              # painted dado
chrome_trim(0.0, 15.0, D - 0.02, 1.4)
hline(0.2, 14.8, D - 0.01, 1.32, BLUE_N, r=0.02)
neon_seams(0.0, 15.0, 1.4, 7.0, D + 0.0, BLUE_N, spacing=1.6, avoid=WINDOWS, r=0.012)
window_neon(WINDOWS[0], D - 0.02, NEON_HOT)
wet_floor(0.0, 15.0, 0.0, D)
grid_floor(0.2, 14.8, 0.1, D - 0.1, m=BLUE_N, m2=NEON_HOT, nx=10, ny=3)

# Bunk bed on the left, with LED rails.
for z in (0.0, 1.25):
    cube((2.2, 1.0, 0.18), (1.6, D - 0.6, z + 0.55), MAT_INK, bevel=0.0)
    cube((2.2, 0.02, 0.03), (1.6, D - 1.11, z + 0.5), DORM_ICE, bevel=0.0)
    cube((2.1, 0.95, 0.16), (1.6, D - 0.6, z + 0.72), ((0.12, 0.2, 0.45), 0.9, 0.0), bevel=0.0)
    cube((0.5, 0.6, 0.12), (0.8, D - 0.6, z + 0.86), ((0.7, 0.7, 0.85), 0.9, 0.0), bevel=0.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((1.6 + sx * 1.05, D - 0.6 + sy * 0.45, 0.0), (1.6 + sx * 1.05, D - 0.6 + sy * 0.45, 2.3), 0.03, METAL_STEEL, verts=8)
for i in range(4):
    rod((2.75, D - 1.0, 0.3 + i * 0.5), (2.75, D - 0.2, 0.3 + i * 0.5), 0.015, METAL_STEEL, verts=6)  # ladder rungs
rod((2.75, D - 1.0, 0.0), (2.75, D - 1.0, 2.1), 0.02, METAL_STEEL, verts=6)
rod((2.75, D - 0.2, 0.0), (2.75, D - 0.2, 2.1), 0.02, METAL_STEEL, verts=6)
kanji_sign(0.5, D + 0.0, 2.8, 2.6, m=NEON_HOT, seed=31, w=0.45, frame=DORM_ICE)
neon_polygon(1.8, 3.5, D + 0.0, 0.4, 3, DORM_ICE)
horizon_lines(0.3, 2.6, D + 0.0, 5.6, n=4, spacing=0.14, m=NEON_HOT)

# Lockers and the vending machine.
for i in range(5):
    locker(4.0 + i * 0.65, D - 0.5, 0.0, m=MAT_INK, accent=[DORM_ICE, NEON_HOT][i % 2])
led_strip(3.65, 6.95, D - 0.52, 1.92, m=BLUE_N, r=0.012)
vending_machine(8.2, D - 0.8, 0.0, glow=NEON_HOT)
neon_tube_frame(7.68, 8.72, 0.02, 2.0, D - 0.82, DORM_ICE, r=0.012)
neon_sign("STAFF ONLY", 3.9, D + 0.0, 3.6, NEON_ORANGE, cell=0.14, backing=MAT_INK)
neon_tube_frame(3.75, 9.05, 3.45, 4.45, D - 0.02, NEON_HOT, r=0.02)

# Wall TV, clock, radiator, noticeboard, a hologram by the chair.
scanline_screen(11.3, D + 0.0, 3.0, 1.9, 1.1, colour=(0.6, 0.7, 1.0), frame=DORM_ICE, seed=13)
sunset_mural(9.4, 4.55, D + 0.0, 0.55, frame=NEON_HOT, grid=False)
wall_clock(13.6, D + 0.0, 4.2, r=0.35)
torus(0.4, 0.02, (13.6, D - 0.03, 4.2), NEON_HOT, rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=4)
for i in range(9):
    cube((0.16, 0.14, 0.7), (12.6 + i * 0.2, D - 0.08, 0.5), ((0.35, 0.36, 0.5), 0.6, 0.2), bevel=0.0)
rod((12.5, D - 0.15, 0.85), (14.3, D - 0.15, 0.85), 0.02, METAL_STEEL, verts=6)
rod((12.5, D - 0.15, 0.15), (14.3, D - 0.15, 0.15), 0.02, METAL_STEEL, verts=6)
cube((2.2, 0.06, 1.5), (13.3, D + 0.0, 2.2), MAT_INK, bevel=0.0)
cube((2.0, 0.03, 1.3), (13.3, D - 0.03, 2.2), MAT_PLUM, bevel=0.0)
neon_tube_frame(12.2, 14.4, 1.45, 2.95, D - 0.03, BLUE_N, r=0.015)
for i in range(11):
    x = 12.5 + (i * 0.37) % 1.7
    z = 1.7 + (i * 0.53) % 1.0
    cube((0.3, 0.02, 0.36), (x, D - 0.05, z), NOTE[i % 4], rot=(0, ((i * 7) % 5 - 2) * 0.08, 0), bevel=0.0)
    sphere(0.02, (x, D - 0.07, z + 0.16), NEON_RED, segments=6, rings=4)
led_column(14.65, D + 0.0, 1.0, 4.8, m=DORM_ICE, alt=NEON_HOT, w=0.2)
horizon_lines(12.4, 14.3, D + 0.0, 5.0, n=3, spacing=0.14, m=DORM_ICE)
chevron_strip(7.6, 14.4, 6.5, D + 0.0, m=BLUE_N, h=0.22)
# A chair and a stack of towels; a mop in the corner; a holo-cube notice.
cube((0.5, 0.5, 0.05), (10.0, D - 1.2, 0.45), MAT_PLUM, bevel=0.0)
cube((0.5, 0.05, 0.5), (10.0, D - 0.98, 0.72), MAT_PLUM, bevel=0.0)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((10.0 + sx * 0.22, D - 1.2 + sy * 0.22, 0.0), (10.0 + sx * 0.22, D - 1.2 + sy * 0.22, 0.44), 0.02, METAL_STEEL, verts=6)
hologram(11.2, 0.5, 0.0, "cube", "spin_notice", m=DORM_ICE, r=0.3, ring=NEON_HOT)
rod((14.7, D - 0.4, 0.0), (14.6, D - 0.5, 1.5), 0.02, (WOOD_LIGHT, 0.8, 0.0), verts=6)
sphere(0.12, (14.7, D - 0.4, 0.1), ((0.5, 0.5, 0.6), 0.9, 0.0), scale=(1.2, 1.2, 0.6), segments=8, rings=6)
cyl(0.18, 0.3, (14.35, D - 1.2, 0.15), ((0.6, 0.08, 0.1), 0.5, 0.0), verts=10)

# ---- upper wall: neon-lined windows, a stencil, ducts, lasers and a fire hose cabinet.
cube((15.0, 0.03, 2.5), (7.5, D + 0.03, 8.25), MAT_NAVY, bevel=0.0)
for w in WINDOWS[1:]:
    window_neon(w, D - 0.02, BLUE_N)
neon_sign("DORM B", 9.0, D + 0.0, 8.9, neon((0.8, 0.85, 1.0), 1.2, (0.3, 0.3, 0.35)), cell=0.12)
air_duct(0.2, 14.8, D - 0.5, 9.2, size=0.5, m=(GUNMETAL, 0.5, 0.6))
hline(0.3, 14.7, D - 0.78, 9.2, NEON_HOT, r=0.015)
cube((0.8, 0.3, 0.9), (14.4, D - 0.15, 7.6), ((0.5, 0.04, 0.06), 0.5, 0.2), bevel=0.0)
cube((0.6, 0.02, 0.7), (14.4, D - 0.31, 7.6), ((0.6, 0.6, 0.7), 0.1, 0.0), bevel=0.0)
torus(0.2, 0.06, (14.4, D - 0.33, 7.6), ((0.8, 0.1, 0.1), 0.6, 0.0), rot=(math.pi / 2, 0, 0))
laser_fan(5.0, D - 0.4, 8.7, m=NEON_HOT, n=4, spread=1.2, length=1.3)
laser_fan(10.0, D - 0.4, 8.7, m=DORM_ICE, n=4, spread=1.2, length=1.3)
star_field(0.0, 15.0, 7.1, 8.7, D + 0.0, n=16, seed=19, avoid=WINDOWS)
chevron_strip(0.3, 14.7, 7.15, D + 0.0, m=DORM_ICE, h=0.2, avoid=WINDOWS)

strip_bevels()
join_static("decor")
export("backdrop_room2")
