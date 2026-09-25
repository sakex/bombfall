# heart: the bat boss's heart, about 1 m tall, centred (it dangles on a
# rope near the ceiling; grab it to win). A glossy, stylised anatomical
# heart: plump ventricles meeting in the apex, two atria on top, the aortic
# arch and vessels rising to where the rope ties on (+Z), glowing neon
# veins over its surface. Idle: a lub-dub heartbeat once a second.
#   blender -b --python blender/heart.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()

FLESH = pbr("skin", (0.42, 0.03, 0.06), rough=0.16, name="heart_flesh", scale=0.5)
VESSEL = pbr("skin", (0.5, 0.12, 0.16), rough=0.22, name="heart_vessel")
VEIN = pbr("neon", (0.6, 0.05, 0.25), emit=(1.0, 0.15, 0.45), strength=4.0, name="heart_vein")

beat = pivot("beat", (0, 0, 0))

# The body: metaballs blended into one smooth organ.
mb = bpy.data.metaballs.new("heart_mb")
mb.resolution = 0.07
mb.render_resolution = 0.07
mb.threshold = 0.6
mbo = bpy.data.objects.new("heart_mb", mb)
bpy.context.collection.objects.link(mbo)


def ball(co, r, scale=(1, 1, 1)):
    e = mb.elements.new(type="ELLIPSOID")
    e.co = co
    e.radius = r
    e.size_x, e.size_y, e.size_z = scale
    return e


ball((-0.14, 0.0, 0.05), 0.42, (0.9, 0.75, 1.0))      # left ventricle
ball((0.14, -0.04, 0.08), 0.4, (0.85, 0.72, 0.95))     # right ventricle
ball((0.0, 0.0, -0.22), 0.3, (0.7, 0.6, 0.9))          # towards the apex
ball((0.02, 0.0, -0.4), 0.16, (0.6, 0.55, 0.8))        # apex
ball((-0.2, 0.05, 0.3), 0.26, (0.9, 0.8, 0.7))         # left atrium
ball((0.22, 0.02, 0.28), 0.25, (0.9, 0.8, 0.7))        # right atrium
bpy.context.view_layer.objects.active = mbo
bpy.ops.object.select_all(action="DESELECT")
mbo.select_set(True)
bpy.ops.object.convert(target="MESH")
body = bpy.context.object
body.name = "organ"
dec = body.modifiers.new("dec", "DECIMATE")
dec.ratio = 0.35
bpy.ops.object.modifier_apply(modifier="dec")
for p in body.data.polygons:
    p.use_smooth = True
body.data.materials.clear()
body.data.materials.append(FLESH)
attach(body, beat)

# Aortic arch and the great vessels up top (the rope ties on above them).
tube(smooth_path([(0.05, 0.0, 0.3), (0.06, 0.02, 0.5), (-0.05, 0.02, 0.62), (-0.2, 0.0, 0.58),
                  (-0.27, 0.0, 0.46)], 3), [0.12, 0.12, 0.11, 0.1, 0.1, 0.095, 0.09, 0.085, 0.085, 0.08, 0.08,
                                          0.075, 0.075], VESSEL, sides=10, name="aorta", parent=beat)
tube(smooth_path([(0.2, -0.03, 0.35), (0.25, -0.05, 0.52), (0.33, -0.04, 0.6)], 2), 0.075, VESSEL, sides=8,
     name="pulmonary", parent=beat)
for x, h in ((-0.02, 0.72), (-0.1, 0.7), (-0.18, 0.66)):
    tube([(x, 0.0, 0.58), (x, 0.0, h)], 0.035, VESSEL, sides=6, name="branch", parent=beat)
bpy.context.view_layer.update()


def on_surface(points, lift):
    """Drop a path onto the organ's surface (plus `lift` along the normal)."""
    out = []
    for p in points:
        ok, loc, nrm, _ = body.closest_point_on_mesh(Vector(p))
        out.append(loc + nrm * lift if ok else Vector(p))
    return out


# Glowing veins over the front: a branching coronary pattern.
veins = [
    [(0.0, -0.33, 0.14), (-0.04, -0.37, 0.0), (-0.02, -0.36, -0.16), (0.01, -0.3, -0.3), (0.02, -0.2, -0.42)],
    [(-0.04, -0.37, 0.0), (-0.18, -0.35, -0.06), (-0.3, -0.26, -0.1)],
    [(-0.02, -0.36, -0.16), (0.12, -0.33, -0.2), (0.24, -0.26, -0.22)],
    [(0.1, -0.33, 0.2), (0.24, -0.3, 0.08), (0.34, -0.22, -0.02)],
    [(-0.12, -0.32, 0.18), (-0.26, -0.28, 0.12), (-0.38, -0.18, 0.02)],
]
for i, v in enumerate(veins):
    pts = on_surface(smooth_path(v, 3), 0.008)
    tube(pts, [0.02 * (1 - 0.6 * k / (len(pts) - 1)) for k in range(len(pts))], VEIN, sides=4,
         name="vein%d" % i, parent=beat)

# Idle: lub-dub once a second.
key(beat, "idle", "scale", [(0, (1, 1, 1)), (3, (1.1, 1.08, 1.06)), (6, (0.98, 0.98, 0.99)), (9, (1.06, 1.05, 1.04)),
                            (14, (1, 1, 1)), (30, (1, 1, 1))])

fix_scratches()
join([c for c in beat.children if c.type == "MESH"], "heart_mesh")      # one draw, still beating
finish("heart")
tri_report("heart")
export("heart", tex=512)
sheet("heart", views=[(0, 0), (35, 15), (-70, 10)])
