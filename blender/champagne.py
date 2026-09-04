# champagne: built by furniture.champagne(), see blender/furniture.py.
#   blender -b --python blender/champagne.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.champagne()
join_static("body")
export("champagne")
