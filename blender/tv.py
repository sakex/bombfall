# tv: built by furniture.tv(), see blender/furniture.py.
#   blender -b --python blender/tv.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.tv()
join_static("body")
export("tv")
