# vault_door: built by hazards.vault_door(), see blender/hazards.py.
#   blender -b --python blender/vault_door.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.vault_door()
join_static("body", keep=("wheel", "lock_light",))
export("vault_door")
