# crate: built by hazards.crate(), see blender/hazards.py.
#   blender -b --python blender/crate.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.crate()
join_static("body", keep=())
export("crate")
