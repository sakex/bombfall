# Backdrop for the staff dorm (room2): a bunk bed, a row of lockers, a
# vending machine, a wall TV playing static, a clock, a radiator, a
# noticeboard full of notes and a "STAFF ONLY" sign. 15 m wide.
#   blender -b --python blender/backdrop_room2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
PAINT = ((0.16, 0.22, 0.40), 0.9, 0.0)
NOTE = [((0.95, 0.9, 0.5), 0.9, 0.0), ((0.6, 0.9, 0.95), 0.9, 0.0), ((0.95, 0.6, 0.7), 0.9, 0.0), (WHITE, 0.9, 0.0)]

cube((15.0, 0.04, 1.4), (7.5, D + 0.015, 0.7), PAINT, bevel=0.0)              # painted dado
cube((15.0, 0.05, 0.06), (7.5, D + 0.0, 1.4), METAL_STEEL, bevel=0.0)
wall_panel_lines(0.0, 15.0, D + 0.02, 1.4, 7.0, spacing=1.6)

# Bunk bed on the left.
for z in (0.0, 1.25):
    cube((2.2, 1.0, 0.18), (1.6, D - 0.6, z + 0.55), ((0.15, 0.16, 0.2), 0.6, 0.6), bevel=0.02)
    cube((2.1, 0.95, 0.16), (1.6, D - 0.6, z + 0.72), ((0.3, 0.45, 0.6), 0.9, 0.0), bevel=0.05)
    cube((0.5, 0.6, 0.12), (0.8, D - 0.6, z + 0.86), (WHITE, 0.9, 0.0), bevel=0.04)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((1.6 + sx * 1.05, D - 0.6 + sy * 0.45, 0.0), (1.6 + sx * 1.05, D - 0.6 + sy * 0.45, 2.3), 0.03, METAL_STEEL, verts=8)
for i in range(4):
    rod((2.75, D - 1.0, 0.3 + i * 0.5), (2.75, D - 0.2, 0.3 + i * 0.5), 0.015, METAL_STEEL, verts=6)  # ladder rungs
rod((2.75, D - 1.0, 0.0), (2.75, D - 1.0, 2.1), 0.02, METAL_STEEL, verts=6)
rod((2.75, D - 0.2, 0.0), (2.75, D - 0.2, 2.1), 0.02, METAL_STEEL, verts=6)

# Lockers and the vending machine.
for i in range(5):
    locker(4.0 + i * 0.65, D - 0.5, 0.0, accent=[NEON_CYAN, NEON_PINK][i % 2])
vending_machine(8.2, D - 0.8, 0.0)
neon_sign("STAFF ONLY", 3.9, D + 0.0, 3.6, NEON_ORANGE, cell=0.14, backing=PLASTIC_BLACK)

# Wall TV, clock, radiator, noticeboard.
monitor(11.3, D + 0.0, 3.0, w=1.9, h=1.1, screen=neon((0.7, 0.75, 0.8), 1.2, (0.2, 0.22, 0.25)), stand=False)
for i in range(12):
    cube((0.10, 0.015, 0.05), (10.55 + (i % 4) * 0.5, D - 0.05, 2.6 + (i // 4) * 0.35), (DARK, 0.5, 0.0), bevel=0.0)  # static lines
wall_clock(13.6, D + 0.0, 4.2, r=0.35)
for i in range(9):
    cube((0.16, 0.14, 0.7), (12.6 + i * 0.2, D - 0.08, 0.5), (WHITE, 0.6, 0.2), bevel=0.02)
rod((12.5, D - 0.15, 0.85), (14.3, D - 0.15, 0.85), 0.02, METAL_STEEL, verts=6)
rod((12.5, D - 0.15, 0.15), (14.3, D - 0.15, 0.15), 0.02, METAL_STEEL, verts=6)
cube((2.2, 0.06, 1.5), (13.3, D + 0.0, 2.2), (WOOD, 0.8, 0.0), bevel=0.02)
cube((2.0, 0.03, 1.3), (13.3, D - 0.03, 2.2), ((0.25, 0.15, 0.1), 0.9, 0.0), bevel=0.0)
for i in range(11):
    x = 12.5 + (i * 0.37) % 1.7
    z = 1.7 + (i * 0.53) % 1.0
    p = cube((0.3, 0.02, 0.36), (x, D - 0.05, z), NOTE[i % 4], rot=(0, ((i * 7) % 5 - 2) * 0.08, 0), bevel=0.0)
    sphere(0.02, (x, D - 0.07, z + 0.16), NEON_RED, segments=6, rings=4)
# A chair and a stack of towels; a mop in the corner.
cube((0.5, 0.5, 0.05), (10.0, D - 1.2, 0.45), (SLATE, 0.6, 0.3), bevel=0.01)
cube((0.5, 0.05, 0.5), (10.0, D - 0.98, 0.72), (SLATE, 0.6, 0.3), bevel=0.01)
for sx in (-1, 1):
    for sy in (-1, 1):
        rod((10.0 + sx * 0.22, D - 1.2 + sy * 0.22, 0.0), (10.0 + sx * 0.22, D - 1.2 + sy * 0.22, 0.44), 0.02, METAL_STEEL, verts=6)
rod((14.7, D - 0.4, 0.0), (14.6, D - 0.5, 1.5), 0.02, (WOOD_LIGHT, 0.8, 0.0), verts=6)
sphere(0.12, (14.7, D - 0.4, 0.1), ((0.7, 0.7, 0.6), 0.9, 0.0), scale=(1.2, 1.2, 0.6), segments=8, rings=6)
cyl(0.18, 0.3, (14.35, D - 1.2, 0.15), ((0.8, 0.1, 0.1), 0.5, 0.0), verts=10)

# ---- upper wall: frosted windows, a big stencil, ducts and a fire hose cabinet.
# (window openings are cut into the wall by the game, see SpawnRegistry themes)
neon_sign("DORM B", 8.9, D + 0.0, 7.2, neon((0.9, 0.9, 0.8), 0.6, (0.35, 0.35, 0.3)), cell=0.16)
air_duct(0.2, 14.8, D - 0.5, 9.2, size=0.5)
cube((0.8, 0.3, 0.9), (13.0, D - 0.15, 7.6), ((0.7, 0.05, 0.05), 0.5, 0.2), bevel=0.02)
cube((0.6, 0.02, 0.7), (13.0, D - 0.31, 7.6), ((0.9, 0.9, 0.9), 0.1, 0.0), bevel=0.0)
torus(0.2, 0.06, (13.0, D - 0.33, 7.6), ((0.8, 0.1, 0.1), 0.6, 0.0), rot=(math.pi / 2, 0, 0))

join_static("decor")
export("backdrop_room2")
