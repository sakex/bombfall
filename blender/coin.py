# A coin: a minted gold token 1 m across, its faces towards the camera. A
# raised, chamfered rim frames a frosted field with a polished relief of the
# synthwave sun over a horizon and a ring of beads (both faces), and the edge
# is reeded. The relief lives in the normal map; two star glints flash in
# the idle clip. The game spins the whole model and tints it by value.
#   blender -b --python blender/coin.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
R = 0.5
H = 0.045          # half thickness of the field
FRONT = (math.pi / 2, 0, 0)
FIELD = 0.86       # emblem art covers the field inside the rim (m)


def draw_emblem(img, d):
    n = img.size[0]
    k = n / FIELD
    c = n / 2
    white = (250, 224, 150, 255)   # a paler, frosted gold
    # Ring of beads.
    for i in range(40):
        a = math.tau * i / 40
        x, y = c + 0.365 * k * math.cos(a), c + 0.365 * k * math.sin(a)
        r = 0.011 * k
        d.ellipse((x - r, y - r, x + r, y + r), fill=white)
    # The sun, sliced by horizon bands on its lower half.
    sy = c - 0.05 * k
    r = 0.2 * k
    d.ellipse((c - r, sy - r, c + r, sy + r), fill=white)
    gap = 0.012
    for j in range(5):
        y0 = sy + (0.02 + j * 0.037) * k
        d.rectangle((c - r - 2, y0, c + r + 2, y0 + (gap + j * 0.004) * k), fill=(0, 0, 0, 0))
    # Horizon and a perspective floor.
    hy = sy + 0.215 * k
    d.rectangle((c - 0.3 * k, hy, c + 0.3 * k, hy + 0.018 * k), fill=white)
    for j in range(1, 3):
        y = hy + j * 0.045 * k
        half = (0.27 - j * 0.045) * k
        d.rectangle((c - half, y, c + half, y + 0.012 * k), fill=white)
    # Two four-point stars.
    for sx, syy, s in ((-0.2, -0.24, 0.045), (0.23, -0.2, 0.03)):
        x, y = c + sx * k, c + syy * k
        s *= k
        d.polygon([(x, y - s), (x + s * 0.25, y - s * 0.25), (x + s, y), (x + s * 0.25, y + s * 0.25),
                   (x, y + s), (x - s * 0.25, y + s * 0.25), (x - s, y), (x - s * 0.25, y - s * 0.25)], fill=white)


def draw_reeds(img, d):
    w, h = img.size
    for x in range(0, w, 4):
        d.rectangle((x, 0, x + 1, h), fill=(255, 255, 255, 255))


emblem = decal_image("coin_emblem", 512, 512, draw_emblem)
reeds = decal_image("coin_reeds", 64, 8, draw_reeds)
GOLD_M = decal_pbr("gold", (0.9, 0.53, 0.1), [
    dict(image=emblem, origin=(0, -H, 0), size=(FIELD, FIELD), depth=0.01, rough=0.42, emboss=1.0),
    dict(image=emblem, origin=(0, H, 0), size=(FIELD, FIELD), u=(-1, 0, 0), depth=0.01, rough=0.42, emboss=1.0),
    dict(image=reeds, origin=(0, 0, R), size=(0.16, 0.2), v=(0, -1, 0), repeat=True,
         cyl=((0, 0, 0), (0, 1, 0), R), depth=0.004, mode="none", emboss=0.6),
], name="coin_gold", rough=0.3, metal=0.85, grime=0.04, wear=0.0, scale=0.6, emboss_distance=0.006)
GLINT = pbr("neon", (1.0, 0.9, 0.6), emit=(1.0, 0.92, 0.7), strength=7.0, name="coin_glint")

# Raised chamfered rim around a flat field, both faces.
lathe([(0.0, -H), (0.412, -H), (0.428, -0.062), (0.478, -0.062), (0.5, -0.04), (0.5, 0.04),
       (0.478, 0.062), (0.428, 0.062), (0.412, H), (0.0, H)], GOLD_M, segments=32, rot=FRONT, name="coin",
      angle=30)


def star(name, loc, size, y_sign):
    """A flat four-point star glint facing out of one face."""
    bm = bmesh.new()
    x0, y0, z0 = loc
    pts = []
    for i in range(8):
        a = math.tau * i / 8
        r = size if i % 2 == 0 else size * 0.16
        pts.append((x0 + r * math.cos(a), y0, z0 + r * math.sin(a)))
    ctr = bm.verts.new(loc)
    vs = [bm.verts.new(p) for p in pts]
    for i in range(8):
        f = (ctr, vs[i], vs[(i + 1) % 8]) if y_sign > 0 else (ctr, vs[(i + 1) % 8], vs[i])
        bm.faces.new(f)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(GLINT)
    return o


# Glints: tiny stars at the rim that pop in turn (scaled from nothing).
for i, (x, z, y) in enumerate(((-0.3, 0.33, -0.075), (0.34, -0.28, 0.075))):
    p = pivot("glint_%d" % (i + 1), (x, y, z))
    bpy.context.view_layer.update()
    s = star("glint_mesh_%d" % (i + 1), (x, y, z), 0.13, 1 if y > 0 else -1)
    attach(s, p)
    t0 = 0 if i == 0 else 30
    key(p, "idle", "scale", [(0, (0.001,) * 3), (t0, (0.001,) * 3), (t0 + 4, (1, 1, 1)), (t0 + 10, (0.001,) * 3),
                             (60, (0.001,) * 3)], interp="LINEAR")
    key(p, "idle", "rotation_euler", [(0, (0, 0, 0)), (60, (0, math.radians(90), 0))], interp="LINEAR")

finish("coin")
tri_report("coin")
# Gold only reflects, and the hotel is dark: the baked albedo also feeds a
# faint emission so coins read as gold anywhere, and so the game's value
# tiers (which scale emission) make rich coins glow.
if os.environ.get("NO_BAKE") != "1":
    bake_textures("coin", tex=512)
    baked = bpy.data.materials["coin_baked"]
    nt = baked.node_tree
    bsdf = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    alb = bsdf.inputs["Base Color"].links[0].from_node
    nt.links.new(alb.outputs["Color"], bsdf.inputs["Emission Color"])
    bsdf.inputs["Emission Strength"].default_value = 0.3
export("coin", bake=False)
sheet("coin", views=[(0, 0), (40, 15), (90, 0), (180, 0)])
