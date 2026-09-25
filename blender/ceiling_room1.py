# Ceiling for the Hotel Electra bedroom (room1): a plaster soffit along the
# front with a violet cove light, a ceiling rose under a walnut-and-brass
# ceiling fan with a frosted light bowl (spinning), recessed downlights,
# sprinkler heads, a square air diffuser and a smoke detector whose LED
# blinks.  z = 0 is the ceiling, everything hangs below it.
#   blender -b --python blender/ceiling_room1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
THEME = dict(wall=(0.12, 0.05, 0.23), trim=(0.7, 0.3, 1.0), floor=(0.09, 0.04, 0.16))
PLASTER = M("concrete", (0.34, 0.26, 0.40), grime=0.4, bump=0.3)
IVORY = M("plastic", (0.62, 0.6, 0.56), rough=0.45)
WALNUT = M("wood", (0.12, 0.055, 0.03), color2=(0.085, 0.037, 0.02), rough=0.32)
BRASS = M("gold", (0.85, 0.58, 0.25), rough=0.25)
CHROME = M("chrome", (0.7, 0.7, 0.75))
COVE = glow((0.65, 0.3, 1.0), 3.0)
BOWL = glow((1.0, 0.85, 0.65), 1.6, base=(0.9, 0.85, 0.8))
DOWN = glow((1.0, 0.9, 0.75), 3.5)
LED_RED = glow((1.0, 0.05, 0.05), 6.0)

# Front soffit with a cove light, and a moulded lip along the back wall.
box((15.0, 0.4, 0.32), (7.5, 0.2, -0.16), PLASTER, bev=0.03)
box((15.0, 0.12, 0.06), (7.5, 0.42, -0.29), IVORY, bev=0.015)
box((14.9, 0.03, 0.03), (7.5, 0.46, -0.24), COVE)
moulding(0.0, 15.0, -0.3, [(0.0, 0.0), (0.18, 0.08), (0.2, 0.2), (0.12, 0.26), (0.0, 0.3)], IVORY, y=1.95)

# Ceiling fan between the high windows, on a plaster rose.
lathe([(0.55, 0.0), (0.5, -0.04), (0.35, -0.07), (0.2, -0.08), (0.0, -0.08)], (6.5, 1.0, 0.0), IVORY, verts=20, cap_top=False)
ceiling_fan(6.5, 1.0, -0.08, 0.55, WALNUT, BRASS, lamp_m=BOWL, blades=5, r=1.6, name="fan_blades", turns=3, k=1.35)

# Downlights, sprinklers, a diffuser, the smoke detector.
for x in (2.6, 10.6, 13.6):
    downlight(x, 1.1, 0.0, CHROME, DOWN)
for x in (3.8, 9.2, 12.4):
    sprinkler(x, 1.2, 0.0, CHROME)
box((0.9, 0.9, 0.04), (13.9, 1.05, -0.02), IVORY, bev=0.01)
for k in range(4):
    s = 0.75 - k * 0.16
    box((s, s, 0.03), (13.9, 1.05, -0.045 - k * 0.015), PLASTER, bev=0.005)
smoke_detector(11.4, 1.1, 0.0, IVORY, LED_RED)
# A brass track with three spotlights washing the bed wall.
box((4.2, 0.08, 0.05), (8.75, 1.35, -0.025), BRASS, bev=0.01)
for k, x in enumerate((7.3, 8.75, 10.2)):
    rod((x, 1.35, -0.05), (x, 1.35, -0.22), 0.02, BRASS, verts=6)
    head = cyl(0.11, 0.34, (x, 1.45, -0.3), M("paint", (0.03, 0.03, 0.035)), rot=(0.8, 0, 0), verts=12, bevel=0.01)
    cyl(0.085, 0.02, (x, 1.45 + 0.13, -0.3 - 0.12), DOWN, rot=(0.8, 0, 0), verts=12, bevel=0)

finish("ceiling_room1", ceiling=True, tex=1024, theme=THEME)
