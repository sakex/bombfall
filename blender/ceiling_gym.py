# Gym ceiling: long fluorescent light bars, a punching bag on a chain and a
# pull-up bar hanging from a beam.
#   blender -b --python blender/ceiling_gym.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
MINT = neon((0.3, 1.0, 0.75), 3.0)
for i in range(4):
    light_bar(2.0 + i * 3.6, D - 0.9, -0.12, length=2.6, m=MINT)
cube((15.0, 0.25, 0.25), (7.5, D - 0.3, -0.15), METAL_DARK, bevel=0.02)
punching_bag(6.2, D - 1.1, 0.0, drop=0.6, h=1.3)
rod((10.5, D - 1.0, 0.0), (10.5, D - 1.0, -0.8), 0.03, METAL_CHROME, verts=8)
rod((12.5, D - 1.0, 0.0), (12.5, D - 1.0, -0.8), 0.03, METAL_CHROME, verts=8)
rod((10.5, D - 1.0, -0.8), (12.5, D - 1.0, -0.8), 0.03, METAL_CHROME, verts=8)
led_strip(0.2, 14.8, D + 0.02, -0.2, m=MINT)

join_static("decor")
export("ceiling_gym")
