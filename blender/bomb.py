# The bomb: a chunky steel disc with a digital countdown on its face, a neon
# ring that the game lights up as the timer runs out, and a detonator cap
# with a trailing cable on top. Centred on the origin, radius ~1.75 m
# (the old 2D bomb was 224 px across on 64 px cells).
#   blender -b --python blender/bomb.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
R = 1.75
T = 0.9   # thickness (along Y)

# Main disc, axis along Y so the face looks at the camera.
cyl(R, T, (0, 0, 0), METAL_STEEL, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.04)
# Raised inner plate and a dark rim groove.
cyl(R * 0.92, T + 0.08, (0, 0, 0), METAL_DARK, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0)
cyl(R * 0.62, T + 0.16, (0, 0, 0), METAL_STEEL, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0)
# Rivets around the rim.
for i in range(12):
    a = i / 12.0 * math.tau
    sphere(0.07, (math.cos(a) * R * 0.80, -T / 2 - 0.05, math.sin(a) * R * 0.80), METAL_CHROME, segments=6, rings=4)
# Neon progress ring (the game raises its emission as the countdown runs).
torus(R * 0.76, 0.05, (0, -T / 2 - 0.06, 0), NEON_CYAN, rot=(math.pi / 2, 0, 0), major_segments=28, minor_segments=5, name="ring")
# Countdown display: dark bezel with a red digit strip.
cube((0.95, 0.1, 0.42), (0, -T / 2 - 0.10, 0.05), PLASTIC_BLACK, bevel=0.02)
cube((0.80, 0.04, 0.26), (0, -T / 2 - 0.16, 0.05), NEON_RED, bevel=0.01, name="display")
# Detonator block on top with a bolt collar and a cable looping to the side.
cube((0.55, 0.5, 0.35), (0, 0, R + 0.10), METAL_DARK, bevel=0.03)
cyl(0.22, 0.30, (0, 0, R + 0.40), METAL_STEEL, verts=12)
cyl(0.10, 0.25, (0, 0, R + 0.62), NEON_PINK, verts=10, name="fuse")
pts = [(0.15, 0.1, R + 0.25), (0.9, 0.1, R + 0.55), (1.6, 0.1, R + 0.1), (1.85, 0.1, -0.5)]
for p0, p1 in zip(pts, pts[1:]):
    rod(p0, p1, 0.06, PLASTIC_BLACK, verts=5)
for p in pts[1:-1]:
    sphere(0.065, p, PLASTIC_BLACK, segments=6, rings=4)

join_static("body", keep=("ring", "display", "fuse"))
export("bomb")
