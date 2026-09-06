# Bathroom ceiling: frosted light panels, an extractor fan and a leaky pipe.
#   blender -b --python blender/ceiling_toilet1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
for i in range(4):
    cube((1.4, 0.9, 0.05), (2.0 + i * 3.6, D - 0.9, -0.03), neon((0.85, 0.95, 1.0), 2.2, (0.4, 0.45, 0.5)), bevel=0.0)
    cube((1.5, 1.0, 0.03), (2.0 + i * 3.6, D - 0.9, -0.005), METAL_STEEL, bevel=0.0)
cyl(0.3, 0.06, (12.0, D - 1.2, -0.03), METAL_DARK, verts=16)
ex = pivot("spin_extractor", (12.0, D - 1.2, -0.06))
for i in range(4):
    cube((0.5, 0.05, 0.02), (12.0, D - 1.2, -0.06), METAL_STEEL, rot=(0, 0, i * 0.785), bevel=0.0, parent=ex)
pipe_run(0.2, 14.8, D - 0.3, -0.3, r=0.07, m=METAL_CHROME, drops=(6.0,))
sphere(0.05, (6.0, D - 0.3, -0.95), neon((0.6, 0.85, 1.0), 1.0, (0.2, 0.3, 0.4)), segments=6, rings=4)

# Synthwave touch: a neon cornice along the front edge and a laser fan.
hline(0.2, 14.8, 0.15, -0.06, NEON_ICE, r=0.025)
laser_fan(9.0, D - 1.0, 0.0, m=NEON_HOT, n=4, spread=1.2, length=1.0)

join_static("decor")
export("ceiling_toilet1")
