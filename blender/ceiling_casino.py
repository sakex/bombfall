# Casino ceiling: two chandeliers, a mirrored strip and gold cornices.
#   blender -b --python blender/ceiling_casino.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
cube((15.0, 0.12, 0.12), (7.5, D - 0.06, -0.06), METAL_GOLD, bevel=0.01)
chandelier(4.0, D - 1.0, 0.0, drop=1.0)
chandelier(11.0, D - 1.0, 0.0, drop=1.0)
sp = pivot("spin_lights", (7.5, D - 1.0, -0.4))
for i in range(6):
    a = i / 6.0 * math.tau
    spotlight(7.5 + math.cos(a) * 0.6, D - 1.0 + math.sin(a) * 0.6, 0.0, m=[NEON_YELLOW, NEON_MAGENTA, NEON_CYAN][i % 3], aim=0.6)
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.parent is None and abs(o.location.x - 7.5) < 0.9 and abs(o.location.y - (D - 1.0)) < 0.9 and o.location.z < 0.0:
        attach(o, sp)
join_under(sp, "spin_lights_mesh")
cube((6.0, 0.8, 0.03), (7.5, D - 0.5, -0.015), ((0.45, 0.55, 0.65), 0.05, 1.0), bevel=0.0)
led_strip(0.2, 14.8, D + 0.02, -0.2, m=neon((1.0, 0.8, 0.3), 2.0))

# Synthwave touch: a neon cornice along the front edge and a laser fan.
hline(0.2, 14.8, 0.15, -0.06, NEON_HOT, r=0.025)
laser_fan(1.5, D - 1.0, 0.0, m=neon((1.0, 0.8, 0.3), 3.0), n=4, spread=1.2, length=1.0)

join_static("decor")
export("ceiling_casino")
