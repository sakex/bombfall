# plasma_bullet: built by hazards.plasma_bullet(), see blender/hazards.py.
#   blender -b --python blender/plasma_bullet.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.plasma_bullet()
join_static("body", keep=())
export("plasma_bullet")
