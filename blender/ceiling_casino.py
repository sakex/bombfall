# Ceiling of the casino, Neon Palace: a gilt coffered ceiling with a
# cornice ringed by chasing marquee bulbs; two grand crystal chandeliers
# that sway (sway_*) with turning crystal balls (spin_*); green-glass
# gaming-table lamps over the roulette and blackjack tables (sway_*); the
# eye-in-the-sky camera domes; a pair of moving heads sweeping gold light.
#   blender -b --python blender/ceiling_casino.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
BULBS = anim_neon((1.0, 0.8, 0.4), "marquee", 3.0)
slab_at(0.0, 15.0, 0.0, WALL, -0.05, 0.0, M.lacquer_red)
for i in range(7):
    bx = 0.05 + i * 2.48
    slab_at(bx - 0.07, bx + 0.07, 0.2, WALL, -0.18, -0.05, M.gold)
slab_at(0.0, 15.0, 1.05, 1.15, -0.18, -0.05, M.gold)
cornice(0.0, 15.0, 0.0, M.gold, M.gold, h=0.32, d=0.24)
quad_dots([(0.1 + i * 0.16, -0.2) for i in range(93)], -0.01, 0.05, BULBS)
for (cx, r) in ((2.3, 0.8), (13.2, 0.72)):
    lathe([(0.0, -0.065), (0.2, -0.05), (0.35, 0)], (cx, 0.95, -0.05), M.gold, segs=12, cap=False)
    chandelier("sway_chandelier_%d" % int(cx), cx, 0.95, drop=1.05, r=r, arms=8, tiers=2, strands=16)
# table lamps: long green-glass shades on brass rods
for i, (tx, w) in enumerate(((6.7, 1.6), (10.1, 1.2))):
    p = pivot("sway_tablelamp_%d" % i, (tx, 0.95, 0.0))
    for sx in (-1, 1):
        tube([(tx + sx * w * 0.4, 0.95, -0.05), (tx + sx * w * 0.4, 0.95, -1.35)], 0.006, M.brass, verts=3, caps=False, parent=p)
    prism([(0.95 - 0.16, -1.35), (0.95 + 0.16, -1.35), (0.95 + 0.1, -1.2), (0.95 - 0.1, -1.2)], tx - w / 2, tx + w / 2,
          pbr("plastic", (0.02, 0.3, 0.12), rough=0.1, name="banker_green"), plane="yz", parent=p)
    box((w - 0.04, 0.28, 0.01), (tx, 0.95, -1.36), M.bulb, parent=p)
    box((w + 0.04, 0.34, 0.02), (tx, 0.95, -1.345), M.gold, parent=p)
    merge_children(p, p.name + "_mesh")
for dx in (4.6, 8.5, 11.6):
    lathe([(0.0, -0.14), (0.08, -0.12), (0.13, -0.05), (0.14, 0.0)], (dx, 0.6, -0.05), pbr("glass", (0.05, 0.05, 0.07), alpha=0.8, name="dome"), segs=10, cap=False)
    box((0.02, 0.02, 0.02), (dx, 0.55, -0.12), M.n_red)
moving_head("sweep_0", 4.6, 1.5, (1.0, 0.75, 0.3), beam=2.4, aim=-0.3, phase=0.0)
moving_head("sweep_1", 11.6, 1.5, (1.0, 0.75, 0.3), beam=2.4, aim=0.3, phase=3.0)

finish("ceiling_casino", 1024, 5000)
