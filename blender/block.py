# block: built by hazards.block(), see blender/hazards.py.
#   blender -b --python blender/block.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.block()
join_static("body", keep=())
export("block")
