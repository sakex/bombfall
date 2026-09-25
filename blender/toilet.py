# toilet: a porcelain smart toilet, built by furniture.toilet().
#   blender -b --python blender/toilet.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.toilet()
furniture.finish("toilet", keep=("display",))
