# air_fan: built by hazards.air_fan(), see blender/hazards.py.
#   blender -b --python blender/air_fan.py -- --preview blender/previews
# BAKE_TEX=256 still forces a small atlas for quick looks (export() would
# otherwise let the explicit size win over the environment variable).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.air_fan()
join_static("body", keep=())
export("air_fan", tex=int(os.environ.get("BAKE_TEX", 0)) or 512)
