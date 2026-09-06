# One floor/wall cell of the hotel: a 1 x 1 m armoured panel, 2 m deep, with
# bevelled edges, a recessed seam and a thin neon groove. Instanced by the
# game through a MultiMesh, so it must stay very cheap. Centred on origin.
#   blender -b --python blender/tile_floor.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
D = 2.0
cube((1.0, D, 1.0), (0, 0, 0), METAL_DARK, bevel=0.05)
# Raised plate on the front face with a slot of neon light.
cube((0.80, 0.08, 0.80), (0, -D / 2 - 0.02, 0), (SLATE, 0.5, 0.6), bevel=0.0)
cube((0.62, 0.03, 0.06), (0, -D / 2 - 0.07, 0.30), neon(MAGENTA, 1.6), bevel=0.0)
cube((0.62, 0.03, 0.04), (0, -D / 2 - 0.07, -0.32), neon(CYAN, 1.2), bevel=0.0)
# Top face hatch strips (the walkable surface).
cube((0.86, 1.2, 0.05), (0, 0.15, 0.50), (SLATE, 0.55, 0.5), bevel=0.0)
for i in range(3):
    cube((0.86, 0.06, 0.03), (0, -0.55 + i * 0.28, 0.535), METAL_STEEL, bevel=0.0)

join_static("body")
export("tile_floor")
