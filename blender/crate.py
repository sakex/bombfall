# crate: a casino loot crate 1.4 m wide, 1.2 m tall, 1 m deep, centred (it
# floats and spins above the pedestal; pickup.gd owns that motion, and the
# game bursts it into coins). A lacquered plum case with gold corner guards,
# chrome latches and handles, a lid on a hinge with a glowing seam, and a
# porthole on the front showing the stacked coins inside. Idle: the lid
# rattles as if the loot wants out.
#   blender -b --python blender/crate.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
W, D, H = 1.4, 1.0, 1.2
LID_Z = 0.28          # the lid seam


def draw_front(img, d):
    w, h = img.size
    k = w / W
    gold = (236, 188, 80, 255)
    for sx in (-1, 1):           # pinstripes
        x = w / 2 + sx * 0.52 * k
        d.line((x, h * 0.3, x, h * 0.92), fill=gold, width=3)


def draw_lid(img, d):
    w, h = img.size
    f = pil_font(int(h * 0.62), "wide")
    d.text((w / 2, h / 2), "JACKPOT", font=f, fill=(240, 196, 90, 255), anchor="mm")


front_art = decal_image("crate_front", 512, 256, draw_front)
lid_art = decal_image("crate_lid", 512, 64, draw_lid)
BODY = decal_pbr("paint", (0.1, 0.02, 0.14), [
    dict(image=front_art, origin=(0, -D / 2, 0.02), size=(W, W / 2), depth=0.03, rough=0.3),
], name="crate_body", rough=0.2, wear=0.6, grime=0.4)
LID = decal_pbr("paint", (0.1, 0.02, 0.14), [
    dict(image=lid_art, origin=(0, -D / 2, 0.355), size=(0.9, 0.1125), depth=0.03, rough=0.25, emboss=0.4),
], name="crate_lid", rough=0.2, wear=0.6, grime=0.4)
GOLD_M = pbr("gold", (0.95, 0.68, 0.24), rough=0.2, name="crate_gold")
CHROME_M = pbr("chrome", (0.74, 0.75, 0.8), name="crate_chrome")
RUBBER = pbr("rubber", (0.03, 0.03, 0.04), name="crate_rubber")
SEAM = pbr("neon", (0.4, 0.2, 0.02), emit=(1.0, 0.55, 0.1), strength=5.0, name="crate_seam")
GLASS = glass((0.9, 0.85, 0.7), alpha=0.18, rough=0.03, name="crate_glass")
COIN_M = pbr("gold", (0.9, 0.6, 0.15), rough=0.3, name="crate_coins")
GLOW = pbr("neon", (0.6, 0.4, 0.1), emit=(1.0, 0.7, 0.25), strength=2.0, name="crate_inner_glow")

# Case body (below the seam) and the lid (above it, on its hinge).
PZ = -0.12             # porthole centre height
body = bm_box((W, D, H / 2 + LID_Z), (0, 0, (-H / 2 + LID_Z) / 2), BODY, chamfer=0.05)
# Cut the porthole's pocket out of the front.
cutter = cyl(0.2, 0.3, (0, -D / 2, PZ), BODY, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0)
bool_mod = body.modifiers.new("porthole", "BOOLEAN")
bool_mod.operation = "DIFFERENCE"
bool_mod.solver = "EXACT"
bool_mod.object = cutter
bpy.ops.object.select_all(action="DESELECT")
body.select_set(True)
bpy.context.view_layer.objects.active = body
bpy.ops.object.modifier_apply(modifier="porthole")
bpy.data.objects.remove(cutter, do_unlink=True)
lid = pivot("lid", (0, D / 2, LID_Z))
bm_box((W, D, H / 2 - LID_Z), (0, 0, (H / 2 + LID_Z) / 2), LID, chamfer=0.05, parent=lid)
# Glowing seam round the case under the lid.
bm_box((W - 0.03, D - 0.03, 0.018), (0, 0, LID_Z), SEAM)
# Gold corner guards (eight), each a chamfered block over the corner.
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            loc = (sx * (W / 2 - 0.07), sy * (D / 2 - 0.07), sz * (H / 2 - 0.07))
            bm_box((0.18, 0.18, 0.18), loc, GOLD_M, chamfer=0.035, parent=lid if sz > 0 else None)
# Gold bands round the case.
for z in (-0.38,):
    bm_box((W + 0.02, D + 0.02, 0.06), (0, 0, z), GOLD_M, chamfer=0.012)
bm_box((W + 0.02, D + 0.02, 0.06), (0, 0, 0.45), GOLD_M, chamfer=0.012, parent=lid)
# Chrome latches across the seam, and side handles.
for sx in (-1, 1):
    bm_box((0.12, 0.05, 0.16), (sx * 0.4, -D / 2 - 0.02, LID_Z - 0.04), CHROME_M, chamfer=0.012)
    bm_box((0.08, 0.04, 0.08), (sx * 0.4, -D / 2 - 0.02, LID_Z + 0.07), CHROME_M, chamfer=0.01, parent=lid)
    tube(smooth_path([(sx * W / 2, -0.2, 0.0), (sx * (W / 2 + 0.1), -0.18, 0.02), (sx * (W / 2 + 0.1), 0.18, 0.02),
                      (sx * W / 2, 0.2, 0.0)], 2), 0.025, CHROME_M, sides=6)
# Porthole with the coins inside.
lathe([(0.25, -0.02), (0.27, 0.02), (0.27, 0.05), (0.23, 0.07), (0.2, 0.05), (0.2, -0.02)], CHROME_M, segments=24,
      loc=(0, -D / 2, PZ), rot=(math.pi / 2, 0, 0), name="porthole")
cyl(0.205, 0.01, (0, -D / 2 - 0.035, PZ), GLASS, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.0, name="port_glass")
cyl(0.2, 0.02, (0, -D / 2 + 0.12, PZ), GLOW, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.0)   # lit back wall
for i, (x, z, rz) in enumerate(((-0.08, -0.2, 0.2), (0.07, -0.18, -0.3), (0.0, -0.08, 0.1), (-0.1, -0.02, 0.6),
                                (0.11, -0.04, -0.5), (0.02, 0.06, 0.9))):
    cyl(0.07, 0.018, (x, -D / 2 + 0.06 + 0.012 * (i % 2), PZ + z), COIN_M, rot=(math.pi / 2 - 0.25, 0, rz),
        verts=10, bevel=0.0)
for sx in (-1, 1):
    for sz in (-1, 1):
        cyl(0.05, 0.03, (sx * 0.52, sz * 0.36, -H / 2 - 0.0), RUBBER, verts=8, bevel=0.0)

# Idle, 2 s: two quick rattles of the lid, then rest.
rattle = [(0, (0, 0, 0)), (3, (math.radians(-6), 0, math.radians(1.5))), (6, (0, 0, 0)),
          (9, (math.radians(-4), 0, math.radians(-1.2))), (12, (0, 0, 0)), (60, (0, 0, 0))]
key(lid, "idle", "rotation_euler", rattle, interp="LINEAR")

finish("crate", keep=("port_glass",))
tri_report("crate")
export("crate", tex=512)
sheet("crate", views=[(0, 0), (35, 20), (80, 10)])
