# bed2: built by furniture.bed2(), see blender/furniture.py.
#   blender -b --python blender/bed2.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.bed2()
furniture.prepare()
export("bed2")
furniture.report("bed2")
