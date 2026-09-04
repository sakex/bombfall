# Influencer studio ceiling: softbox lights on booms, fairy lights and a
# paper lantern.
#   blender -b --python blender/ceiling_tiktoker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
for x in (5.0, 9.5):
    rod((x, D - 0.3, 0.0), (x, D - 1.2, -0.9), 0.03, METAL_DARK, verts=8)
    cube((0.9, 0.7, 0.35), (x, D - 1.3, -1.05), METAL_DARK, rot=(0.6, 0, 0), bevel=0.02)
    cube((0.8, 0.6, 0.03), (x, D - 1.55, -1.28), NEON_WHITE, rot=(0.6, 0, 0), bevel=0.0)
for i in range(30):
    x = 0.3 + i * 0.5
    sphere(0.035, (x, D - 0.2, -0.15 - abs(math.sin(i * 0.8)) * 0.35), [NEON_PINK, NEON_YELLOW, NEON_CYAN][i % 3], segments=6, rings=4)
cable_drape(0.3, 15.0, D - 0.2, -0.1, sag=0.3, m=PLASTIC_BLACK, segments=10, r=0.008)
rod((12.5, D - 1.0, 0.0), (12.5, D - 1.0, -0.5), 0.01, PLASTIC_BLACK, verts=4)
sphere(0.4, (12.5, D - 1.0, -0.95), neon((1.0, 0.6, 0.8), 1.2, (0.5, 0.3, 0.4)), segments=12, rings=8)

join_static("decor")
export("ceiling_tiktoker")
