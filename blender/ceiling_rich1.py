# Ceiling of the penthouse lounge (rich1), Neon Palace: a walnut coffered
# ceiling behind a gilt crown moulding with a warm cove light, plaster
# rosettes and three crystal chandeliers that sway (sway_*), each with a
# cut-crystal ball turning under it (spin_*).
#   blender -b --python blender/ceiling_rich1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
# coffers: walnut beams with gold fillets
slab_at(0.0, 15.0, 0.0, WALL, -0.06, 0.0, M.walnut)
for i in range(7):
    bx = 0.1 + i * 2.465
    slab_at(bx - 0.09, bx + 0.09, 0.2, WALL, -0.22, -0.06, M.walnut)
    box((0.02, WALL - 0.2, 0.02), (bx, 0.2 + (WALL - 0.2) / 2, -0.225), M.gold)
slab_at(0.0, 15.0, 1.1, 1.26, -0.2, -0.06, M.walnut)
box((15.0, 0.02, 0.02), (7.5, 1.1, -0.205), M.gold)
cornice(0.0, 15.0, 0.0, M.walnut, M.gold, h=0.34, d=0.24, light=M.n_amber)
box((15.0, 0.02, 0.03), (7.5, -0.005, -0.06), M.gold)
for (cx, drop, r, arms) in ((3.9, 1.0, 0.62, 8), (7.6, 0.75, 0.45, 6), (11.3, 1.0, 0.62, 8)):
    lathe([(0.36, 0), (0.34, -0.02), (0.26, -0.04), (0.22, -0.035), (0.12, -0.06), (0.0, -0.065)], (cx, 0.95, -0.06), M.plaster, segs=16, cap=False)
    chandelier("sway_chandelier_%d" % int(cx), cx, 0.95, drop=drop, r=r, arms=arms, tiers=2)

finish("ceiling_rich1", 1024, 5000)
