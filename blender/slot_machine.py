# slot_machine: a classic casino one-armed bandit, built by
# furniture.slot_machine(). The game spins the "reel_1".."reel_3" pivots,
# pulls the "lever" pivot and relies on the "marquee" mesh's animated shader.
#   blender -b --python blender/slot_machine.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.slot_machine()
furniture.finish("slot_machine", keep=("marquee",))
