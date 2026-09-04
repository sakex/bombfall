# cake: built by furniture.cake(), see blender/furniture.py.
#   blender -b --python blender/cake.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.cake()
join_static("body")
export("cake")
