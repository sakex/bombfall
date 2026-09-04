# heart: built by hazards.heart(), see blender/hazards.py.
#   blender -b --python blender/heart.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.heart()
join_static("body", keep=())
export("heart")
