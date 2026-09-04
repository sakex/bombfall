# toilet: built by furniture.toilet(), see blender/furniture.py.
#   blender -b --python blender/toilet.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.toilet()
join_static("body")
export("toilet")
