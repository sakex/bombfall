# One vault cell: a riveted chrome block with a hazard stripe. Takes three
# blasts to break. 1 x 1 x 2 m like tile_floor, centred.
#   blender -b --python blender/tile_steel.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
cube((1.0, 2.0, 1.0), (0, 0, 0), METAL_CHROME, bevel=0.05)
cube((0.84, 0.06, 0.84), (0, -1.02, 0), METAL_STEEL, bevel=0.0)
for sx in (-1, 1):
    for sz in (-1, 1):
        sphere(0.06, (sx * 0.36, -1.06, sz * 0.36), METAL_DARK, segments=6, rings=4)
cube((0.7, 0.03, 0.14), (0, -1.07, 0.0), neon(YELLOW, 1.5, (0.4, 0.3, 0.05)), bevel=0.0)
for i in range(3):
    cube((0.1, 0.02, 0.14), (-0.25 + i * 0.25, -1.08, 0.0), PLASTIC_BLACK, rot=(0, 0, 0.6), bevel=0.0)
join_static("body")
export("tile_steel")
