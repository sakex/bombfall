# Ceiling for the Hotel Electra washroom (toilet1): moisture-resistant tiles
# on a grid, two fluorescent fixtures (one dying: it stutters), a copper
# pipe with a slow leak dripping, a round exhaust vent whose fan spins,
# sprinkler heads and a smoke detector.
#   blender -b --python blender/ceiling_toilet1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
THEME = dict(wall=(0.06, 0.09, 0.21), trim=(0.35, 0.9, 1.0), floor=(0.05, 0.08, 0.16))
TILE = pattern("ceramic", (0.5, 0.52, 0.58), "tiles", size=(0.3, 0.3), line=0.02, line_col=(0.2, 0.2, 0.25), plane="XY")
GRID = M("metal", (0.6, 0.62, 0.66))
HOUSING = M("paint", (0.6, 0.62, 0.64), wear=0.3)
TUBE = glow((0.8, 0.95, 1.0), 4.0)
COPPER = M("metal", (0.55, 0.25, 0.12), rough=0.35)
CHROME = M("chrome", (0.7, 0.72, 0.78))
WHITE = M("plastic", (0.7, 0.72, 0.75), rough=0.4)
WATER = glass((0.6, 0.85, 1.0), alpha=0.5)

drop_ceiling(TILE, GRID, tile=1.25, stained=(9,))
front_soffit(M("ceramic", (0.3, 0.32, 0.4)), trim_m=CHROME, glow_m=glow((0.35, 0.9, 1.0), 3.0))
fluorescent(4.0, 1.05, -0.03, 2.8, HOUSING, TUBE, name="tube_dying", flick=3, width=0.4)
fluorescent(11.5, 1.05, -0.03, 2.8, HOUSING, TUBE, width=0.4)
# copper pipe with a leaking joint
tube_path([(0.0, 1.55, -0.35), (15.0, 1.55, -0.35)], 0.06, COPPER, verts=8)
for x in (2.0, 6.5, 12.0):
    rod((x, 1.55, -0.35), (x, 1.55, 0.0), 0.02, COPPER, verts=4)
cyl(0.09, 0.14, (7.8, 1.55, -0.35), COPPER, rot=(0, math.pi / 2, 0), verts=10, bevel=0)
for k in range(2):
    d = pivot("leak_%d" % k, (7.8, 1.55, -0.44))
    ball(0.04, (7.8, 1.55, -0.44), WATER, scale=(1, 1, 1.4), seg=6, rings=4, parent=d)
    puff(d, rise=-2.2, grow=1.0, start=k * 60, life=26)
# round exhaust vent with a spinning fan
cyl(0.55, 0.08, (9.6, 1.0, -0.04), WHITE, verts=20, bevel=0.01)
cyl(0.46, 0.02, (9.6, 1.0, -0.09), M("rubber", (0.01, 0.01, 0.012)), verts=20, bevel=0)
fan = pivot("vent_fan", (9.6, 1.0, -0.07))
for k in range(5):
    a = k / 5 * math.tau
    box((0.4, 0.14, 0.02), (9.6 + math.cos(a) * 0.22, 1.0 + math.sin(a) * 0.22, -0.07), M("metal", (0.5, 0.52, 0.55)),
        rot=(0.4, 0, a), parent=fan)
spin_idle(fan, "Z", 4)
for k in range(4):
    torus(0.12 + k * 0.11, 0.01, (9.6, 1.0, -0.11), CHROME, major_segments=16, minor_segments=3)
for x in (2.5, 6.8, 13.5):
    sprinkler(x, 1.2, 0.0, CHROME)
smoke_detector(13.0, 0.9, -0.03, WHITE, glow((1.0, 0.05, 0.05), 6.0))

finish("ceiling_toilet1", ceiling=True, tex=1024, theme=THEME)
