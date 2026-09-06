# Ceiling dressing for the hacker rooms: cables looping between hooks, an
# air duct, and a lone lamp on a cord. Origin at the ceiling on the left
# wall; everything hangs downwards, no lower than 3 m.
#   blender -b --python blender/ceiling_hacker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
air_duct(0.3, 14.7, D - 0.4, -0.35)
for i in range(7):
    cable_drape(0.5 + i * 2.0, 2.5 + i * 2.0, D - 1.0 + (i % 3) * 0.25, -0.1, sag=0.55 + (i % 2) * 0.2, m=(PLASTIC_BLACK if i % 2 else (0.5, 0.05, 0.05)))
for i in range(8):
    sphere(0.04, (0.5 + i * 2.0, D - 1.0 + (i % 3) * 0.25, -0.08), METAL_STEEL, segments=8, rings=6)
lamp = pivot("sway_lamp", (7.5, D - 1.2, 0.0))
hanging_lamp(7.5, D - 1.2, 0.0, drop=1.3, m=NEON_YELLOW)
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.parent is None and abs(o.location.x - 7.5) < 0.3 and abs(o.location.y - (D - 1.2)) < 0.3 and o.location.z < 0.0:
        attach(o, lamp)
hanging_lamp(2.2, D - 1.4, 0.0, drop=0.9, m=NEON_GREEN)
led_strip(0.2, 14.8, D + 0.02, -0.25, m=NEON_GREEN, r=0.025)

# Synthwave touch: a neon cornice along the front edge and a laser fan.
hline(0.2, 14.8, 0.15, -0.06, NEON_ICE, r=0.025)
laser_fan(12.0, D - 1.0, 0.0, m=NEON_GREEN, n=4, spread=1.2, length=1.1)

join_static("decor")
export("ceiling_hacker")
