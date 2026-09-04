# wall_gun: built by hazards.wall_gun(), see blender/hazards.py.
#   blender -b --python blender/wall_gun.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.wall_gun()
join_static("body", keep=("gun",))
export("wall_gun")
