# Ceiling for the Hotel Electra staff dorm (room2): a tired suspended ceiling
# (one tile missing, one water-stained), three fluorescent fixtures (the
# middle one flickers), a red sprinkler main with heads, a smoke detector
# that blinks and a clothesline of socks and a T-shirt drying in the draught.
#   blender -b --python blender/ceiling_room2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
THEME = dict(wall=(0.05, 0.07, 0.21), trim=(0.4, 0.55, 1.0), floor=(0.04, 0.05, 0.14))
TILE = pattern("concrete", (0.42, 0.42, 0.46), "grille", size=(0.08, 0.08), plane="XY", grime=0.5)
GRID = M("paint", (0.6, 0.6, 0.62), wear=0.2)
HOUSING = M("paint", (0.55, 0.56, 0.58), wear=0.3)
TUBE = glow((0.85, 0.92, 1.0), 4.0)
PIPE = M("paint", (0.45, 0.02, 0.02), wear=0.6)
CHROME = M("chrome", (0.7, 0.72, 0.78))
WHITE = M("plastic", (0.7, 0.7, 0.72), rough=0.4)
ROPE = M("fabric", (0.6, 0.55, 0.45))

drop_ceiling(TILE, GRID, missing=(7,), stained=(3,))
front_soffit(M("concrete", (0.3, 0.32, 0.4)), trim_m=GRID, glow_m=glow((0.4, 0.55, 1.0), 3.0))
for i, x in enumerate((2.4, 7.5, 12.6)):
    fluorescent(x, 1.05, -0.03, 2.6, HOUSING, TUBE, name="tube_%d" % i if i == 1 else None, flick=5 if i == 1 else None,
                width=0.42)
tube_path([(0.0, 1.65, -0.3), (15.0, 1.65, -0.3)], 0.07, PIPE, verts=8)
for x in (1.2, 5.0, 10.0, 13.8):
    rod((x, 1.65, -0.3), (x, 1.65, 0.0), 0.02, PIPE, verts=4)
for x in (3.8, 9.0, 13.0):
    tube_path([(x, 1.65, -0.3), (x, 1.2, -0.3), (x, 1.2, -0.45)], 0.035, PIPE, verts=6)
    sprinkler(x, 1.2, -0.45, CHROME)
smoke_detector(10.4, 0.9, -0.03, WHITE, glow((1.0, 0.05, 0.05), 6.0))
# clothesline between two hooks, socks and a T-shirt swaying
tube_path(catenary((8.9, 0.8, -0.35), (11.3, 0.8, -0.35), 0.25, n=8), 0.012, ROPE, verts=4)
for x in (8.9, 11.3):
    rod((x, 0.8, 0.0), (x, 0.8, -0.38), 0.02, CHROME, verts=4)
for k, (x, kind, col) in enumerate(((9.4, "sock", (0.8, 0.8, 0.8)), (9.75, "sock", (0.6, 0.05, 0.3)), (10.5, "shirt", (0.1, 0.3, 0.6)))):
    t = (x - 8.9) / 2.4
    zc = -0.35 - 0.25 * 4 * t * (1 - t)
    p = pivot("laundry_%d" % k, (x, 0.8, zc))
    m = M("fabric", col)
    if kind == "sock":
        box((0.14, 0.05, 0.5), (x, 0.8, zc - 0.25), m, bev=0.03, parent=p)
        box((0.25, 0.05, 0.14), (x + 0.07, 0.8, zc - 0.5), m, bev=0.03, parent=p)
    else:
        box((0.85, 0.05, 0.95), (x, 0.8, zc - 0.5), m, bev=0.04, parent=p)
        for s in (-1, 1):
            box((0.4, 0.05, 0.3), (x + s * 0.55, 0.8, zc - 0.15), m, rot=(0, s * 0.5, 0), bev=0.03, parent=p)
    swing(p, "X", amp=0.12, phase=k * 1.4)
    swing(p, "Y", amp=0.05, phase=k * 2.2)

finish("ceiling_room2", ceiling=True, tex=1024, theme=THEME)
