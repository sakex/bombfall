# Ceiling for the Hotel Electra gym: open industrial ceiling -- black steel
# beams, a big five-blade HVLS fan turning slowly, a spiral duct with
# diffusers, mint LED linear lights, a climbing rope and a pair of
# gymnastic rings on straps that sway.
#   blender -b --python blender/ceiling_gym.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
THEME = dict(wall=(0.05, 0.09, 0.17), trim=(0.25, 1.0, 0.75), floor=(0.06, 0.10, 0.18))
STEEL = M("paint", (0.03, 0.03, 0.035), wear=0.8)
DUCT = M("metal", (0.5, 0.52, 0.55), rough=0.4)
MINT = glow((0.3, 1.0, 0.75), 4.0)
YELLOW = M("paint", (0.7, 0.55, 0.05), wear=0.5)
ROPE = M("fabric", (0.55, 0.45, 0.28), bump=1.0)
STRAP = M("fabric", (0.05, 0.05, 0.06))
WOOD = M("wood", (0.4, 0.25, 0.1), color2=(0.3, 0.18, 0.07))

front_soffit(M("concrete", (0.15, 0.17, 0.22)), glow_m=MINT, depth=0.3, h=0.35)
# I-beams across the room (seen end-on) and a longitudinal beam
for x in (0.8, 4.4, 8.0, 11.6, 14.4):
    box((0.35, 1.6, 0.06), (x, 1.1, -0.03), STEEL)
    box((0.06, 1.6, 0.45), (x, 1.1, -0.26), STEEL)
    box((0.35, 1.6, 0.06), (x, 1.1, -0.5), STEEL)
box((15.0, 0.3, 0.3), (7.5, 1.75, -0.15), STEEL)
# spiral duct with round diffusers
tube_path([(0.0, 1.55, -0.75), (15.0, 1.55, -0.75)], 0.32, DUCT, verts=12)
for x in (0.0, 3.0, 6.0, 9.0, 12.0, 15.0):
    torus(0.33, 0.03, (x, 1.55, -0.75), M("metal", (0.4, 0.42, 0.45)), rot=(0, math.pi / 2, 0), major_segments=12, minor_segments=3)
for x in (2.0, 13.0):
    cyl(0.2, 0.3, (x, 1.55, -1.1), DUCT, verts=12, bevel=0)
    cyl(0.3, 0.06, (x, 1.55, -1.28), DUCT, verts=14, bevel=0.01)
# mint LED linear lights
for x in (2.6, 9.8):
    rod((x - 1.3, 0.8, 0.0), (x - 1.3, 0.8, -0.6), 0.01, STEEL, verts=4)
    rod((x + 1.3, 0.8, 0.0), (x + 1.3, 0.8, -0.6), 0.01, STEEL, verts=4)
    box((2.8, 0.18, 0.1), (x, 0.8, -0.65), STEEL, bev=0.02)
    box((2.7, 0.14, 0.02), (x, 0.8, -0.71), MINT)
# HVLS fan
ceiling_fan(6.2, 1.0, -0.55, 0.4, YELLOW, STEEL, blades=5, r=2.3, name="hvls", turns=1, k=1.6)
# climbing rope and gym rings on straps
rope = pivot("rope", (12.2, 0.9, -0.5))
tube_path([(12.2, 0.9, -0.5), (12.2, 0.9, -3.0)], 0.07, ROPE, verts=6, parent=rope)
ball(0.1, (12.2, 0.9, -2.98), ROPE, scale=(1, 1, 1.4), seg=8, rings=6, parent=rope)
swing(rope, "X", amp=0.06, phase=0.3)
swing(rope, "Y", amp=0.05, phase=1.5)
for k, x in enumerate((13.1, 13.8)):
    p = pivot("ring_%d" % k, (x, 0.9, -0.5))
    rod((x, 0.9, -0.5), (x, 0.9, -2.2), 0.025, STRAP, verts=4, parent=p)
    torus(0.18, 0.035, (x, 0.9, -2.38), WOOD, rot=(math.pi / 2, 0, 0), major_segments=14, minor_segments=5, parent=p)
    swing(p, "Y", amp=0.07, phase=k * 0.8)
    swing(p, "X", amp=0.04, phase=k * 2.0)
box((1.5, 0.12, 0.12), (13.45, 0.9, -0.5), STEEL)

finish("ceiling_gym", ceiling=True, tex=1024, theme=THEME)
