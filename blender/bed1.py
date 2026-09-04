# bed1: built by furniture.bed(0), see blender/furniture.py.
#   blender -b --python blender/bed1.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.bed(0)
join_static("body")
export("bed1")
