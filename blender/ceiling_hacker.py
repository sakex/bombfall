# Ceiling for the Hotel Electra hacker den: a black-painted ceiling with a
# ladder cable tray whose bundles droop and sway, a bare bulb on a cord
# swinging, green LED strip, a projector, a security camera dome with a
# blinking eye, and a smoke detector someone taped over.
#   blender -b --python blender/ceiling_hacker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
THEME = dict(wall=(0.03, 0.06, 0.11), trim=(0.25, 1.0, 0.45), floor=(0.03, 0.05, 0.09))
TRAY = M("metal", (0.45, 0.47, 0.5), rough=0.4)
BLACK = M("plastic", (0.02, 0.02, 0.025), rough=0.4)
CABLE = [M("rubber", c) for c in ((0.02, 0.02, 0.025), (0.5, 0.05, 0.05), (0.05, 0.2, 0.6), (0.6, 0.5, 0.05), (0.05, 0.45, 0.15))]
GREEN = glow((0.25, 1.0, 0.45), 4.0)
BULB = glow((1.0, 0.8, 0.5), 5.0)
TAPE = M("plastic", (0.6, 0.55, 0.1), rough=0.6)
WHITE = M("plastic", (0.6, 0.6, 0.62), rough=0.4)

front_soffit(M("concrete", (0.06, 0.07, 0.09)), glow_m=GREEN, depth=0.3, h=0.25)
# ladder cable tray on hangers, with bundles drooping out of it
for y in (0.95, 1.35):
    rod((0.2, y, -0.45), (14.8, y, -0.45), 0.03, TRAY, verts=4)
for k in range(15):
    x = 0.5 + k * 1.0
    rod((x, 0.95, -0.45), (x, 1.35, -0.45), 0.02, TRAY, verts=4)
for x in (1.0, 5.0, 9.0, 13.0):
    for y in (0.95, 1.35):
        rod((x, y, 0.0), (x, y, -0.45), 0.012, TRAY, verts=4)
for k in range(4):
    tube_path([(0.2, 1.0 + 0.1 * k, -0.42), (14.8, 1.0 + 0.1 * k, -0.42)], 0.035, CABLE[k], verts=4, cap=False)
for k, (x0, x1, sag) in enumerate(((2.0, 4.2, 0.9), (6.3, 8.1, 0.6), (10.0, 12.6, 1.1))):
    p = pivot("droop_%d" % k, ((x0 + x1) / 2, 1.15, -0.45))
    for j in range(3):
        tube_path(catenary((x0, 1.1 + 0.05 * j, -0.45), (x1, 1.1 + 0.05 * j, -0.45), sag - 0.12 * j, n=8), 0.03,
                  CABLE[(k + j) % 5], verts=4, parent=p)
    swing(p, "X", amp=0.1, phase=k * 1.7)
# bare bulb on a cord, swinging
bulb = pivot("bulb", (5.4, 0.8, 0.0))
tube_path([(5.4, 0.8, 0.0), (5.4, 0.8, -1.4)], 0.012, BLACK, verts=4, parent=bulb)
cyl(0.06, 0.14, (5.4, 0.8, -1.45), BLACK, verts=8, bevel=0, parent=bulb)
ball(0.12, (5.4, 0.8, -1.62), BULB, scale=(1, 1, 1.3), seg=10, rings=6, parent=bulb)
swing(bulb, "X", amp=0.08, phase=0.5)
swing(bulb, "Y", amp=0.1, phase=2.0)
# green LED strip along the back
box((14.8, 0.03, 0.03), (7.5, 1.9, -0.05), GREEN)
# ceiling projector
box((0.35, 0.35, 0.3), (8.6, 1.2, -0.15), BLACK)
fbox((0.9, 0.7, 0.3), (8.6, 1.2, -0.62), WHITE, bev=0.04)
cyl(0.12, 0.08, (8.6, 0.83, -0.47), BLACK, rot=(math.pi / 2, 0, 0), verts=12, bevel=0)
cyl(0.09, 0.01, (8.6, 0.79, -0.47), glow((0.6, 0.9, 1.0), 5.0), rot=(math.pi / 2, 0, 0), verts=12, bevel=0)
# security dome with a blinking eye
cyl(0.25, 0.05, (12.8, 1.0, -0.03), WHITE, verts=16, bevel=0.01)
ball(0.2, (12.8, 1.0, -0.06), glass((0.1, 0.1, 0.12), alpha=0.7), scale=(1, 1, 0.8), seg=12, rings=6)
eye = pivot("cctv_eye", (12.8, 0.87, -0.18))
ball(0.03, (12.8, 0.87, -0.18), glow((1.0, 0.05, 0.05), 6.0), seg=6, rings=4, parent=eye)
blink(eye, [(0, 60)])
# a taped-over smoke detector
cyl(0.16, 0.06, (3.3, 1.2, -0.03), WHITE, verts=16, bevel=0.01)
box((0.45, 0.1, 0.01), (3.3, 1.2, -0.065), TAPE, rot=(0, 0, 0.5))
box((0.45, 0.1, 0.01), (3.3, 1.2, -0.068), TAPE, rot=(0, 0, -0.5))

finish("ceiling_hacker", ceiling=True, tex=1024, theme=THEME)
