# Arcade ceiling: a disco-striped light rig, hanging planets, a spinning
# sign and neon tubes.
#   blender -b --python blender/ceiling_arcade.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
for i in range(5):
    light_bar(1.6 + i * 3.0, D - 0.7, -0.1, length=2.2, m=[NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN, NEON_MAGENTA][i])
for i in range(4):
    x = 2.5 + i * 3.4
    rod((x, D - 1.2, 0.0), (x, D - 1.2, -0.7), 0.01, PLASTIC_BLACK, verts=4)
    sphere(0.3 + (i % 2) * 0.12, (x, D - 1.2, -1.05), [neon((1.0, 0.5, 0.2), 1.2, (0.4, 0.2, 0.05)), neon((0.4, 0.6, 1.0), 1.2, (0.1, 0.2, 0.4))][i % 2], segments=12, rings=8)
    if i % 2:
        torus(0.55, 0.04, (x, D - 1.2, -1.05), NEON_CYAN, rot=(0.4, 0, 0))
sg = pivot("spin_sign", (7.5, D - 1.0, -0.3))
rod((7.5, D - 1.0, 0.0), (7.5, D - 1.0, -0.3), 0.02, METAL_CHROME, verts=6, parent=sg)
cube((1.6, 0.08, 0.5), (7.5, D - 1.0, -0.6), PLASTIC_BLACK, bevel=0.02, parent=sg)
for o in list(bpy.context.scene.objects):
    pass
neon_sign("PLAY", 6.95, D - 1.05, -0.8, NEON_PINK, cell=0.07)
for o in list(bpy.context.scene.objects):
    if o.type == "MESH" and o.parent is None and abs(o.location.x - 7.5) < 0.9 and abs(o.location.y - (D - 1.05)) < 0.1:
        attach(o, sg)
led_strip(0.2, 14.8, D + 0.02, -0.2, m=NEON_MAGENTA)

join_static("decor")
export("ceiling_arcade")
