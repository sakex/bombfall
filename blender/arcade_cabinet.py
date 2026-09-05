# arcade_cabinet: built by hazards.arcade_cabinet(), see blender/hazards.py.
#   blender -b --python blender/arcade_cabinet.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.arcade_cabinet()
join_static("body", keep=("screen", "marquee",))
export("arcade_cabinet")
