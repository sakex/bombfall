# arcade_cabinet: a classic upright arcade machine, built by
# furniture.arcade_cabinet(). The game looks up the meshes "screen" and
# "marquee" (both animated-shader materials).
#   blender -b --python blender/arcade_cabinet.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.arcade_cabinet()
furniture.finish("arcade_cabinet", keep=("screen", "marquee"))
