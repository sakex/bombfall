# Ceiling of the arcade, Neon Palace: a black exposed ceiling with ducts
# and a steel truss along the front carrying spinning red and blue beacon
# lights (spin_*), moving heads sweeping beams (sweep_*) and hanging neon
# signs that swing (sway_*): a pixel heart, a "1UP" and a "HI" cloud; a
# grid of neon tubes; a mirror ball over the claw machine.
#   blender -b --python blender/ceiling_arcade.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
slab_at(0.0, 15.0, 0.0, WALL, -0.04, 0.0, M.black_metal)
# ducts along the back
tube([(0.0, 1.55, -0.25), (15.0, 1.55, -0.25)], 0.2, M.steel, verts=10)
for i in range(8):
    torus(0.2, 0.02, (0.9 + i * 1.9, 1.55, -0.25), M.steel, rot=(0, math.pi / 2, 0), major_segments=10, minor_segments=3)
# neon tube grid
for i in range(6):
    tube([(0.5 + i * 2.8, 0.25, -0.06), (0.5 + i * 2.8, 1.3, -0.06)], 0.02, [M.n_pink, M.n_cyan][i % 2], verts=4)
tube([(0.1, 0.25, -0.06), (14.9, 0.25, -0.06)], 0.02, M.n_violet, verts=4)
# a box truss along the front
TY, TZ = 0.45, -0.45
for dy in (-0.15, 0.15):
    for dz in (-0.15, 0.15):
        tube([(0.0, TY + dy, TZ + dz), (15.0, TY + dy, TZ + dz)], 0.02, M.steel, verts=5, caps=False)
for i in range(31):
    x = i * 0.5
    tube([(x, TY - 0.15, TZ - 0.15), (x + 0.25, TY - 0.15, TZ + 0.15), (x + 0.5, TY - 0.15, TZ - 0.15)], 0.008, M.steel, verts=3, caps=False)
for tx in (1.5, 7.5, 13.5):
    tube([(tx, TY, 0.0), (tx, TY, TZ + 0.15)], 0.01, M.steel, verts=3, caps=False)
for i, (bx, col) in enumerate(((3.0, (1.0, 0.1, 0.1)), (6.0, (0.1, 0.3, 1.0)), (9.0, (1.0, 0.1, 0.1)), (12.0, (0.1, 0.3, 1.0)))):
    # beacons hang under the truss
    lathe([(0.1, 0.0), (0.1, -0.08), (0.0, -0.08)], (bx, TY, TZ - 0.15), M.black_metal, segs=10)
    p = pivot("spin_beacon_%d" % i, (bx, TY, TZ - 0.3))
    lathe([(0.0, 0.0), (0.07, 0.0), (0.07, 0.1), (0.0, 0.1)], (bx, TY, TZ - 0.33), neon_mat(col, 5.0, "beacon"), segs=8, parent=p, arc=math.pi)
    lathe([(0.0, 0.0), (0.07, 0.0), (0.07, 0.1), (0.0, 0.1)], (bx, TY, TZ - 0.33), M.chrome, segs=8, parent=p, arc=math.pi, rot=(0, 0, math.pi))
    lathe([(0.07, 0.0), (0.45, -1.6)], (bx, TY, TZ - 0.28), beam_mat(col, 0.09, 1.5), segs=8, arc=math.pi * 0.3, parent=p, rot=(math.pi / 2, 0, 0))
    merge_children(p, p.name + "_mesh")
    lathe([(0.1, -0.08), (0.1, -0.2), (0.07, -0.26), (0.0, -0.28)], (bx, TY, TZ - 0.15), pbr("glass", col, alpha=0.3, name="beacon_dome"), segs=10, cap=False)
moving_head("sweep_0", 4.6, 0.8, (1.0, 0.2, 0.7), beam=2.6, aim=0.3, phase=0.0)
moving_head("sweep_1", 10.4, 0.8, (0.2, 0.9, 1.0), beam=2.6, aim=-0.3, phase=2.5)
# hanging neon signs


def hanging_sign(name, x, drop, draw):
    p = pivot(name, (x, 0.9, TZ - 0.15))
    for sx in (-0.35, 0.35):
        tube([(x + sx, 0.9, TZ - 0.15), (x + sx, 0.9, -drop + 0.3)], 0.004, M.steel, verts=3, caps=False, parent=p)
    slab_at(x - 0.45, x + 0.45, 0.88, 0.92, -drop - 0.2, -drop + 0.32, M.black_metal, parent=p)
    draw(x, -drop, p)
    merge_children(p, name + "_mesh")


HEART = ["0110110", "1111111", "1111111", "0111110", "0011100", "0001000"]


def pixel_heart(x, z, p):
    pts = [(x + (c - 3) * 0.075, z + 0.2 - r * 0.075) for r, row in enumerate(HEART) for c, ch in enumerate(row) if ch == "1"]
    attach(quad_dots(pts, 0.86, 0.068, M.n_red), p)


hanging_sign("sway_sign_heart", 2.0, 1.1, pixel_heart)
hanging_sign("sway_sign_1up", 13.0, 1.1, lambda x, z, p: neon_text("1UP", x, z - 0.12, 0.86, 0.3, M.n_green, r=0.018, align="center", verts=4, parent=p))
hanging_sign("sway_sign_hi", 7.5, 1.25, lambda x, z, p: neon_text("HI!", x, z - 0.12, 0.86, 0.3, M.n_amber, r=0.018, align="center", verts=4, parent=p))
disco_ball("spin_disco", 8.55, 1.0, drop=0.9, r=0.25)

finish("ceiling_arcade", 1024, 5000)
