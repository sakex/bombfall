# Penthouse ceiling: gold cornice, two chandeliers and a row of spotlights.
#   blender -b --python blender/ceiling_rich1.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
cube((15.0, 0.12, 0.12), (7.5, D - 0.06, -0.06), METAL_GOLD, bevel=0.01)
chandelier(4.6, D - 1.0, 0.0, drop=1.1)
chandelier(10.4, D - 1.0, 0.0, drop=1.1)
for i in range(5):
    spotlight(1.5 + i * 3.0, D - 0.5, 0.0, m=NEON_YELLOW)
led_strip(0.2, 14.8, D + 0.02, -0.2, m=neon((1.0, 0.75, 0.3), 2.0))

# Synthwave touch: a neon cornice along the front edge and a laser fan.
hline(0.2, 14.8, 0.15, -0.06, NEON_HOT, r=0.025)
laser_fan(7.5, D - 1.0, 0.0, m=neon((1.0, 0.8, 0.3), 3.0), n=5, spread=1.3, length=1.0)

join_static("decor")
export("ceiling_rich1")
