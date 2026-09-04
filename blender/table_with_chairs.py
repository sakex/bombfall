# table_with_chairs: built by furniture.table_with_chairs(), see blender/furniture.py.
#   blender -b --python blender/table_with_chairs.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.table_with_chairs()
join_static("body")
export("table_with_chairs")
