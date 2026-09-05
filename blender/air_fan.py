# air_fan: built by hazards.air_fan(), see blender/hazards.py.
#   blender -b --python blender/air_fan.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.air_fan()
join_static("body", keep=("blades",))
export("air_fan")
