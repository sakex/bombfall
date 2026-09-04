# shield_battery: built by hazards.shield_battery(), see blender/hazards.py.
#   blender -b --python blender/shield_battery.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.shield_battery()
join_static("body", keep=())
export("shield_battery")
