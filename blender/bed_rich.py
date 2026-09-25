# bed_rich: built by furniture.bed_rich(), see blender/furniture.py.
#   blender -b --python blender/bed_rich.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.bed_rich()
furniture.finish("bed_rich")
