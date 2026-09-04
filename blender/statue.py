# statue: a chrome android on a plinth, in three separate pieces (base,
# body, head) so the game can knock the head off. 4 m wide, 8 m tall.
#   blender -b --python blender/statue.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
parts = furniture.statue_parts()
for name, objs in parts.items():
    join(objs, name)
export("statue")
