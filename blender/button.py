# button: built by hazards.button(), see blender/hazards.py.
#   blender -b --python blender/button.py -- --preview blender/previews
# BAKE_TEX=256 still forces a small atlas for quick looks (export() would
# otherwise let the explicit size win over the environment variable).
import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.button()
join_static("body", keep=())
# glTF takes each node's rest transform from the scene as evaluated now,
# with every clip's NLA track live: frame 0 is where all clips sit at rest.
bpy.context.scene.frame_set(0)
export("button", tex=int(os.environ.get("BAKE_TEX", 0)) or 512)
