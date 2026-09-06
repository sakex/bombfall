# table: built by furniture.table(), see blender/furniture.py. The chairs of
# the dinner set are separate bodies using chair.glb (table_with_chairs.tscn).
#   blender -b --python blender/table.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.table()
join_static("body")
export("table")
