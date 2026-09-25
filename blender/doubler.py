# doubler: a casino "2X" token 1.1 m across, centred, its faces towards the
# camera (it floats and spins above the pedestal; pickup.gd owns that
# motion). A thick gold medallion with a stepped rim, a smoked-glass face
# carrying a glowing neon "2X" on both sides, and a chrome gear ring studded
# with marquee bulbs. Idle: the gear ring turns and the bulbs chase.
#   blender -b --python blender/doubler.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
FRONT = (math.pi / 2, 0, 0)
BACK = (-math.pi / 2, 0, 0)

GOLD_M = pbr("gold", (0.95, 0.66, 0.2), rough=0.2, name="dbl_gold", grime=0.2)
CHROME_M = pbr("metal", (0.22, 0.22, 0.27), rough=0.3, name="dbl_gear", grime=0.3)
FACE = pbr("plastic", (0.03, 0.01, 0.05), rough=0.06, name="dbl_face", wear=0.0, grime=0.1)
NEON_T = pbr("neon", (0.5, 0.05, 0.4), emit=(1.0, 0.15, 0.75), strength=5.0, name="dbl_text")
NEON_R = pbr("neon", (0.05, 0.4, 0.5), emit=CYAN, strength=4.0, name="dbl_ring")
BULB_A = pbr("neon", (0.6, 0.5, 0.2), emit=(1.0, 0.85, 0.4), strength=7.0, name="dbl_bulb_a")
BULB_B = pbr("neon", (0.6, 0.2, 0.5), emit=(1.0, 0.35, 0.8), strength=7.0, name="dbl_bulb_b")

# Gold medallion: a stepped rim and a recessed face each side.
lathe([(0.0, -0.05), (0.36, -0.05), (0.38, -0.07), (0.46, -0.08), (0.5, -0.06), (0.5, 0.06), (0.46, 0.08),
       (0.38, 0.07), (0.36, 0.05), (0.0, 0.05)], GOLD_M, segments=32, rot=FRONT, name="medallion", angle=30)
# Smoked glass face discs with a neon ring.
for rot, y in ((FRONT, -0.052), (BACK, 0.052)):
    lathe([(0.355, 0.0), (0.0, 0.0)], FACE, segments=32, loc=(0, y, 0), rot=rot)
    torus(0.33, 0.012, (0, y * 1.1, 0), NEON_R, rot=FRONT, major_segments=32, minor_segments=3)
# "2X" in neon on both faces.
text_mesh("2X", 0.42, (0.0, -0.056, -0.02), NEON_T, depth=0.012, kind="wide", name="label_front")
text_mesh("2X", 0.42, (0.0, 0.056, -0.02), NEON_T, rot=(math.pi / 2, 0, math.pi), depth=0.012, kind="wide",
          name="label_back")

# The gear ring with its bulbs, on a pivot that turns in the face plane.
ring = pivot("gear", (0, 0, 0))
teeth = []
N = 20
for i in range(N * 2):
    a = math.tau * i / (N * 2)
    r = 0.62 if i % 2 == 0 else 0.575
    teeth.append((r * math.cos(a), r * math.sin(a)))
bm = bmesh.new()
top = [bm.verts.new((x, -0.05, z)) for x, z in teeth]
bot = [bm.verts.new((x, 0.05, z)) for x, z in teeth]
inner_t = [bm.verts.new((0.53 * math.cos(math.tau * i / (N * 2)), -0.05, 0.53 * math.sin(math.tau * i / (N * 2))))
           for i in range(N * 2)]
inner_b = [bm.verts.new((0.53 * math.cos(math.tau * i / (N * 2)), 0.05, 0.53 * math.sin(math.tau * i / (N * 2))))
           for i in range(N * 2)]
n2 = N * 2
for i in range(n2):
    j = (i + 1) % n2
    bm.faces.new((top[i], top[j], bot[j], bot[i]))                 # outer teeth wall
    bm.faces.new((inner_t[j], inner_t[i], inner_b[i], inner_b[j]))  # inner wall
    bm.faces.new((inner_t[i], inner_t[j], top[j], top[i]))          # front face
    bm.faces.new((inner_b[j], inner_b[i], bot[i], bot[j]))          # back face
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
me = bpy.data.meshes.new("gear")
bm.to_mesh(me)
bm.free()
gear = bpy.data.objects.new("gear_ring", me)
bpy.context.collection.objects.link(gear)
me.materials.append(CHROME_M)
bpy.context.view_layer.update()
attach(gear, ring)
# Bulbs on the gear's front and back faces, alternating colours, chasing.
grp_a = pivot("bulbs_a", (0, 0, 0))
grp_b = pivot("bulbs_b", (0, 0, 0))
attach(grp_a, ring)
attach(grp_b, ring)
for i in range(12):
    a = math.tau * i / 12
    for y in (-0.06, 0.06):
        g, m = (grp_a, BULB_A) if i % 2 == 0 else (grp_b, BULB_B)
        sphere(0.032, (0.575 * math.cos(a), y, 0.575 * math.sin(a)), m, segments=6, rings=3, parent=g)

spin(ring, "idle", "Y", seconds=4.0, turns=1.0)
# Scaling a group flat along Y sinks its bulbs into the gear (switched off).
on, off = (1, 1, 1), (1, 0.01, 1)
chase_a, chase_b = [], []
for k in range(9):
    f = k * 15
    a_on = k % 2 == 0
    chase_a += [(f, on if a_on else off), (f + 13, on if a_on else off)] if k < 8 else [(120, on)]
    chase_b += [(f, off if a_on else on), (f + 13, off if a_on else on)] if k < 8 else [(120, off)]
key(grp_a, "idle", "scale", chase_a, interp="LINEAR")
key(grp_b, "idle", "scale", chase_b, interp="LINEAR")

finish("doubler")
scale_all(0.88)      # fits the float height over the pedestal
tri_breakdown()
tri_report("doubler")
export("doubler", tex=512)
sheet("doubler", views=[(0, 0), (35, 20), (180, 0)])
