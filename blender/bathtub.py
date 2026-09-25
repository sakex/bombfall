# bathtub: a roll-top clawfoot tub full of bubble bath, built by
# furniture.bathtub().
#   blender -b --python blender/bathtub.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.bathtub()
furniture.prepare()
export("bathtub")
furniture.report("bathtub")
