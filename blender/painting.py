# painting: a gilded Baroque frame; the "canvas" quad is textured at runtime
# with one of the classic paintings the old game carried (painting.gd).
#   blender -b --python blender/painting.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.painting_frame()
furniture.prepare(keep=("canvas",))
export("painting")
furniture.report("painting")
