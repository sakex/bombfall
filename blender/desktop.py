# desktop: a gaming workstation in three pieces (desk, monitor, tower).
#   blender -b --python blender/desktop.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
parts = furniture.desktop_parts()
for name, objs in parts.items():
    join(objs, name)
export("desktop")
