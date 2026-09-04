# light_ring: built by hazards.light_ring(), see blender/hazards.py.
#   blender -b --python blender/light_ring.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.light_ring()
join_static("body", keep=("ring", "glow", "emitter",))
export("light_ring")
