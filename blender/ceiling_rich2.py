# Sky bar ceiling: a mirror ball, colour spotlights and a neon grid.
#   blender -b --python blender/ceiling_rich2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85
rod((7.5, D - 1.0, 0.0), (7.5, D - 1.0, -0.6), 0.015, METAL_CHROME, verts=6)
ball = pivot("spin_ball", (7.5, D - 1.0, -0.95))
sphere(0.35, (7.5, D - 1.0, -0.95), neon((0.8, 0.85, 1.0), 1.5, (0.5, 0.5, 0.6)), segments=14, rings=10, parent=ball)
for i in range(14):
    a = i / 14.0 * math.tau
    cube((0.06, 0.06, 0.06), (7.5 + math.cos(a) * 0.36, D - 1.0 + math.sin(a) * 0.36, -0.95), neon((0.9, 0.5, 1.0), 3.0), rot=(0, 0, a), bevel=0.0, parent=ball)
join_under(ball, "spin_ball_mesh")
for i, m in enumerate([NEON_MAGENTA, NEON_CYAN, NEON_VIOLET, NEON_PINK, NEON_CYAN]):
    spotlight(1.5 + i * 3.0, D - 0.6, 0.0, m=m, aim=0.5 if i % 2 else -0.2)
for i in range(3):
    led_strip(0.2, 14.8, D - 0.3 - i * 0.6, -0.08, m=[NEON_MAGENTA, NEON_CYAN, NEON_VIOLET][i], r=0.02)

# Synthwave touch: a neon cornice along the front edge and a laser fan.
hline(0.2, 14.8, 0.15, -0.06, NEON_MAGENTA, r=0.025)
laser_fan(12.5, D - 1.0, 0.0, m=NEON_ICE, n=4, spread=1.2, length=1.0)

join_static("decor")
export("ceiling_rich2")
