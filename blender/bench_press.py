# bench_press: built by furniture.bench_press(), see blender/furniture.py.
#   blender -b --python blender/bench_press.py -- --preview blender/previews
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
import furniture

clean_scene()
furniture.bench_press()
join_static("body")
export("bench_press")
