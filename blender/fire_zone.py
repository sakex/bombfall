# fire_zone: built by hazards.fire_zone(), see blender/hazards.py.
#   blender -b --python blender/fire_zone.py -- --preview blender/previews
# BAKE_TEX=256 still forces a small atlas for quick looks (export() would
# otherwise let the explicit size win over the environment variable).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.fire_zone()
join_static("body", keep=())
export("fire_zone", tex=int(os.environ.get("BAKE_TEX", 0)) or 256)
