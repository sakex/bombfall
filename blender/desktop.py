# desktop: a gamer workstation in three pieces (desk, monitor, tower), each
# its own rigid body in desktop.tscn. The tower's RGB fans spin in the idle
# clip (multi_body.gd keeps the animation when it splits the model).
#   blender -b --python blender/desktop.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
parts, fans = furniture.desktop_parts()
joined = {name: join(objs, name) for name, objs in parts.items()}
for p in fans:
    furniture.attach(p, joined["tower"])
furniture.prepare(keep=tuple(parts))
export("desktop")
furniture.report("desktop", offsets={"monitor": (0, 0, 2.0), "tower": (2.7, 0, 0)})
