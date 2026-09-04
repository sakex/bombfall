# shield_core: built by hazards.shield_core(), see blender/hazards.py.
#   blender -b --python blender/shield_core.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.shield_core()
join_static("body", keep=())
export("shield_core")
