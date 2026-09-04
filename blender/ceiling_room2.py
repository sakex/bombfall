# Dorm ceiling: two bare fluorescent tubes, a sprinkler pipe and a vent.
#   blender -b --python blender/ceiling_room2.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85
for x in (4.0, 11.0):
    light_bar(x, D - 0.9, -0.1, length=2.4, m=neon((0.8, 0.9, 1.0), 2.5))
pipe_run(0.2, 14.8, D - 0.4, -0.2, r=0.05, m=(CREST_RED, 0.5, 0.4), drops=(2.5, 7.5, 12.5))
cube((0.7, 0.5, 0.06), (7.5, D - 1.3, -0.03), METAL_STEEL, bevel=0.005)
for i in range(4):
    cube((0.6, 0.04, 0.02), (7.5, D - 1.5 + i * 0.13, -0.05), METAL_DARK, bevel=0.0)

join_static("decor")
export("ceiling_room2")
