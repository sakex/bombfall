# pedestal: built by hazards.pedestal(), see blender/hazards.py.
#   blender -b --python blender/pedestal.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.pedestal()
join_static("body", keep=("beam",))
export("pedestal")
