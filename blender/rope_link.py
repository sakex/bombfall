# rope_link: built by hazards.rope_link(), see blender/hazards.py.
#   blender -b --python blender/rope_link.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.rope_link()
join_static("body", keep=())
export("rope_link")
