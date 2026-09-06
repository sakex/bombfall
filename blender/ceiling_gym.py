# Gym ceiling: long fluorescent light bars, a punching bag on a chain and a
# pull-up bar hanging from a beam.
#   blender -b --python blender/ceiling_gym.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
MINT = neon((0.3, 1.0, 0.75), 3.0)
for i in range(4):
    light_bar(2.0 + i * 3.6, D - 0.9, -0.12, length=2.6, m=MINT)
cube((15.0, 0.25, 0.25), (7.5, D - 0.3, -0.15), METAL_DARK, bevel=0.02)
bag = pivot("sway_bag", (6.2, D - 1.1, 0.0))
punching_bag(6.2, D - 1.1, 0.0, drop=0.6, h=1.3)
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.parent is None and abs(o.location.x - 6.2) < 0.4 and abs(o.location.y - (D - 1.1)) < 0.4 and o.location.z < 0.0:
        attach(o, bag)
rod((10.5, D - 1.0, 0.0), (10.5, D - 1.0, -0.8), 0.03, METAL_CHROME, verts=8)
rod((12.5, D - 1.0, 0.0), (12.5, D - 1.0, -0.8), 0.03, METAL_CHROME, verts=8)
rod((10.5, D - 1.0, -0.8), (12.5, D - 1.0, -0.8), 0.03, METAL_CHROME, verts=8)
led_strip(0.2, 14.8, D + 0.02, -0.2, m=MINT)

# Synthwave touch: a neon cornice along the front edge and a laser fan.
hline(0.2, 14.8, 0.15, -0.06, NEON_HOT, r=0.025)
laser_fan(3.0, D - 1.0, 0.0, m=MINT, n=4, spread=1.2, length=1.1)

join_static("decor")
export("ceiling_gym")
