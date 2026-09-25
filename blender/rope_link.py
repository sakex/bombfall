# rope_link: built by hazards.rope_link(), see blender/hazards.py.
#   blender -b --python blender/rope_link.py -- --preview blender/previews
# BAKE_TEX=256 still forces a small atlas for quick looks (export() would
# otherwise let the explicit size win over the environment variable).
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.rope_link()
join_static("body", keep=())
export("rope_link", tex=int(os.environ.get("BAKE_TEX", 0)) or 256)
