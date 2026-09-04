# boss_bat: built by hazards.boss_bat(), see blender/hazards.py.
#   blender -b --python blender/boss_bat.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.boss_bat()
join_static("body", keep=("wing_l", "wing_r",))
export("boss_bat")
