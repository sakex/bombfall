# drone: built by hazards.drone(), see blender/hazards.py.
#   blender -b --python blender/drone.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.drone()
join_static("body", keep=("rotor_1", "rotor_2", "rotor_3", "rotor_4",))
export("drone")
