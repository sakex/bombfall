# doubler: a golden "2X" token, 1.2 m across, centred (a pick-up that
# doubles coin values for a while).
#   blender -b --python blender/doubler.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import neon_sign

clean_scene()
ROT = (math.pi / 2, 0, 0)
cyl(0.6, 0.16, (0, 0, 0), METAL_GOLD, rot=ROT, verts=28, bevel=0.02)
torus(0.55, 0.04, (0, -0.08, 0), NEON_YELLOW, rot=ROT, major_segments=28)
torus(0.55, 0.04, (0, 0.08, 0), NEON_YELLOW, rot=ROT, major_segments=28)
for y in (-0.1, 0.1):
    neon_sign("2X", -0.33, y, -0.28, neon(WHITE, 5.0), cell=0.11, gap=0.4)
join_static("body")
export("doubler")
