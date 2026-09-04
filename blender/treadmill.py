# treadmill: built by hazards.treadmill(), see blender/hazards.py.
#   blender -b --python blender/treadmill.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.treadmill()
join_static("body", keep=("roller_1", "roller_2",))
export("treadmill")
