# slot_machine: built by hazards.slot_machine(), see blender/hazards.py.
#   blender -b --python blender/slot_machine.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import hazards

clean_scene()
hazards.slot_machine()
join_static("body", keep=("reel_1", "reel_2", "reel_3", "lever", "marquee",))
export("slot_machine")
