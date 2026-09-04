# bed_rich: built by furniture.bed(2), see blender/furniture.py.
#   blender -b --python blender/bed_rich.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.bed(2)
join_static("body")
export("bed_rich")
