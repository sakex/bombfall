# A coin: gold disc with a raised rim and a glowing circuit-like emblem on
# both faces. 1 m across, axis along Y so the faces look at the camera.
#   blender -b --python blender/coin.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
R = 0.5
T = 0.12
ROT = (math.pi / 2, 0, 0)
cyl(R, T, (0, 0, 0), METAL_GOLD, rot=ROT, verts=20, bevel=0.0)
torus(R * 0.86, 0.03, (0, -T / 2, 0), METAL_BRASS, rot=ROT, major_segments=20, minor_segments=4)
torus(R * 0.86, 0.03, (0, T / 2, 0), METAL_BRASS, rot=ROT, major_segments=20, minor_segments=4)
# Emblem: a glowing ring and cross of circuit traces on each face.
GLOW = neon(YELLOW, 2.5, (0.5, 0.35, 0.05))
for y in (-T / 2 - 0.01, T / 2 + 0.01):
    torus(R * 0.45, 0.025, (0, y, 0), GLOW, rot=ROT, major_segments=14, minor_segments=4)
    for a in (0, math.pi / 2):
        cube((0.55, 0.03, 0.05), (0, y, 0), GLOW, rot=(0, a, 0), bevel=0)
    for a in range(4):
        ang = a * math.pi / 2 + math.pi / 4
        sphere(0.045, (math.cos(ang) * R * 0.66, y, math.sin(ang) * R * 0.66), GLOW, segments=6, rings=4)

join_static("body")
export("coin")
