# One cell of the "junkyard" special level: a crushed cube of scrap plates,
# pipes and a stray neon shard. 1 x 1 x 2 m like tile_floor, centred.
#   blender -b --python blender/tile_junk.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
RUST = ((0.30, 0.12, 0.06), 0.8, 0.3)
cube((0.96, 1.9, 0.96), (0, 0, 0), (SLATE, 0.85, 0.4), bevel=0.04)
cube((0.7, 0.5, 0.3), (0.1, -0.85, 0.25), RUST, rot=(0, 0, 0.3), bevel=0.0)
cube((0.4, 0.4, 0.5), (-0.25, -0.9, -0.15), METAL_DARK, rot=(0.2, 0, -0.4), bevel=0.0)
cyl(0.09, 0.9, (0.25, -0.75, -0.2), METAL_STEEL, rot=(0, 1.1, 0.4), verts=6, bevel=0.0)
cyl(0.06, 0.6, (-0.3, -0.8, 0.3), RUST, rot=(0.5, 0.2, 1.2), verts=6, bevel=0.0)
cube((0.3, 0.05, 0.05), (0.2, -1.0, -0.38), neon(ORANGE, 2.0), rot=(0, 0, 0.7), bevel=0)
sphere(0.12, (-0.32, -0.95, -0.3), METAL_CHROME, segments=6, rings=4)

join_static("body")
export("tile_junk")
