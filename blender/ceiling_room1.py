# Bedroom ceiling: a ceiling fan, a smoke detector and a cornice light.
#   blender -b --python blender/ceiling_room1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
rod((7.5, D - 1.0, 0.0), (7.5, D - 1.0, -0.5), 0.03, METAL_BRASS, verts=8)
fan = pivot("spin_fan", (7.5, D - 1.0, -0.55))
sphere(0.16, (7.5, D - 1.0, -0.55), METAL_BRASS, segments=10, rings=8, parent=fan)
for i in range(4):
    a = i * math.pi / 2
    cube((1.1, 0.24, 0.03), (7.5 + math.cos(a) * 0.65, D - 1.0 + math.sin(a) * 0.65, -0.55), (WOOD, 0.7, 0.0), rot=(0, 0.15, a), bevel=0.01, parent=fan)
sphere(0.12, (7.5, D - 1.0, -0.72), neon((1.0, 0.85, 0.6), 1.5, (0.4, 0.3, 0.2)), segments=10, rings=8)
cyl(0.08, 0.04, (3.0, D - 1.0, -0.02), (WHITE, 0.5, 0.0), verts=12)
cube((0.02, 0.02, 0.02), (3.05, D - 1.05, -0.05), NEON_RED, bevel=0.0)
led_strip(0.2, 14.8, D + 0.02, -0.15, m=neon((1.0, 0.8, 0.5), 1.8))

join_static("decor")
export("ceiling_room1")
