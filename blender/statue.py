# statue: "The Disco Droid", a chrome android on a marble plinth, in three
# separate pieces (base, body, head) so the game can knock the head off.
# The chest core pulses in the idle clip. 3.6 m wide, 7.9 m tall.
#   blender -b --python blender/statue.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
parts, pivots = furniture.statue_parts()
joined = {name: join(objs, name) for name, objs in parts.items()}
for p in pivots:
    furniture.attach(p, joined["body"])
furniture.prepare(keep=tuple(parts))
export("statue", tex=1024)
furniture.report("statue")
