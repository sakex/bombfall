# fire_zone: built by hazards.fire_zone(), see blender/hazards.py.
#   blender -b --python blender/fire_zone.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.fire_zone()
join_static("body", keep=())
export("fire_zone")
