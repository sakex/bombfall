# shield_core: a shield generator core, 1.1 m wide, 1.2 m tall, centred (it
# floats and spins above the pedestal; pickup.gd owns that motion). A
# glowing plasma orb in a glass sphere, held in a gyroscope of two gimbal
# rings inside a hexagonal chrome cage with emitter nodes at its corners and
# brass mounting collars top and bottom. Idle: the gimbals turn on their own
# axes and the orb breathes.
#   blender -b --python blender/shield_core.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()


CHROME_M = pbr("chrome", (0.74, 0.75, 0.8), name="sc_chrome")
DARKM = pbr("paint", (0.06, 0.06, 0.1), name="sc_dark", wear=0.5)
BRASS_M = pbr("gold", (0.75, 0.52, 0.18), rough=0.25, name="sc_brass")
GIMBAL = pbr("metal", (0.55, 0.57, 0.64), rough=0.25, name="sc_gimbal")
ORB = pbr("neon", (0.35, 0.4, 1.0), emit=(0.4, 0.5, 1.0), strength=3.0, name="sc_orb")
ORB_CORE = pbr("neon", (0.9, 0.95, 1.0), emit=(0.85, 0.92, 1.0), strength=10.0, name="sc_orb_core")
GLASS = glow_glass((0.5, 0.65, 1.0), alpha=0.22, strength=0.6, name="sc_glass")
NODE = pbr("neon", (0.05, 0.3, 0.4), emit=CYAN, strength=5.0, name="sc_node")
STRIP = pbr("neon", (0.2, 0.05, 0.3), emit=(0.6, 0.3, 1.0), strength=3.0, name="sc_strip")

# The hexagonal cage: six chrome struts in the face plane, emitter nodes on
# the corners, and a violet neon edge inside it.
HR = 0.5
corners = [(HR * math.cos(math.tau * i / 6 + math.pi / 6), 0.0, HR * math.sin(math.tau * i / 6 + math.pi / 6))
           for i in range(6)]
tube(corners, 0.035, CHROME_M, sides=6, closed=True, name="cage")
tube([(c[0] * 0.9, 0.0, c[2] * 0.9) for c in corners], 0.012, STRIP, sides=4, closed=True, name="cage_glow")
for i, c in enumerate(corners):
    if i in (1, 4):          # top and bottom: the brass collars sit there
        continue
    lathe([(0.0, -0.08), (0.06, -0.08), (0.075, -0.05), (0.075, 0.05), (0.06, 0.08), (0.0, 0.08)], DARKM,
          segments=8, loc=c, rot=(math.pi / 2, 0, 0))
    sphere(0.04, (c[0], -0.08, c[2]), NODE, segments=8, rings=4)
    sphere(0.04, (c[0], 0.08, c[2]), NODE, segments=8, rings=4)
# Brass collars top and bottom that the gimbal axle runs through.
for s in (-1, 1):
    lathe([(0.0, 0.0), (0.09, 0.0), (0.11, 0.03), (0.11, 0.1), (0.07, 0.14), (0.0, 0.14)], BRASS_M, segments=12,
          loc=(0, 0, s * 0.43), rot=(0 if s > 0 else math.pi, 0, 0))
    rod((0, 0, s * 0.43), (0, 0, s * 0.37), 0.022, CHROME_M, verts=8)

# Outer gimbal: turns about the vertical axle.
g1 = pivot("gimbal_outer", (0, 0, 0))
torus(0.37, 0.028, (0, 0, 0), GIMBAL, rot=(math.pi / 2, 0, 0), major_segments=28, minor_segments=4, parent=g1)
for s in (-1, 1):
    sphere(0.035, (s * 0.37, 0, 0), BRASS_M, segments=8, rings=4, parent=g1)
# Inner gimbal: turns about the outer ring's horizontal pins.
g2 = pivot("gimbal_inner", (0, 0, 0))
attach(g2, g1)
torus(0.3, 0.022, (0, 0, 0), GIMBAL, rot=(0, math.pi / 2, 0), major_segments=24, minor_segments=4, parent=g2)
# The orb: a glass sphere round a plasma core that breathes.
orb = pivot("orb", (0, 0, 0))
sphere(0.24, (0, 0, 0), GLASS, segments=16, rings=10, name="orb_glass")
sphere(0.16, (0, 0, 0), ORB, segments=16, rings=10, parent=orb)
sphere(0.08, (0, 0, 0), ORB_CORE, segments=10, rings=6, parent=orb)

spin(g1, "idle", "Z", seconds=4.0, turns=1.0)
spin(g2, "idle", "X", seconds=4.0, turns=-2.0)
key(orb, "idle", "scale", [(0, (1, 1, 1)), (30, (1.14, 1.14, 1.14)), (60, (1, 1, 1)), (90, (1.14, 1.14, 1.14)),
                           (120, (1, 1, 1))])

finish("shield_core", keep=("orb_glass",))
tri_report("shield_core")
export("shield_core", tex=512)
sheet("shield_core", views=[(0, 0), (35, 20), (80, 10)])
