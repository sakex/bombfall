# block: the bat boss's crystal block, a 0.95 m cube (its collision box),
# centred. A hand-cut chunk of frosted amethyst: a deeply chamfered cube with
# slightly irregular facets, frosted (paler, rough) edges, and clusters of
# glowing crystal points breaking out of the faces. The boss's shots leave
# them behind and the arena stacks them as stairs, so it stays solid and
# readable, with light inside.
#   blender -b --python blender/block.py -- --preview blender/previews
import math
import os
import random
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
rnd = random.Random(4)

SHELL = glow_glass((0.62, 0.32, 1.0), alpha=0.62, strength=0.55, base=(0.3, 0.12, 0.55), rough=0.3,
                   name="blk_shell")
HEART = pbr("neon", (0.35, 0.1, 0.6), emit=(0.62, 0.25, 1.0), strength=2.2, name="blk_heart")
FROST = pbr("ceramic", (0.6, 0.48, 0.85), rough=0.4, name="blk_frost", wear=0.0, grime=0.2)
SHARD = pbr("neon", (0.5, 0.2, 0.8), emit=(0.8, 0.35, 1.0), strength=3.5, name="blk_shard")
SHARD_HOT = pbr("neon", (0.8, 0.5, 1.0), emit=(1.0, 0.7, 1.0), strength=6.0, name="blk_shard_hot")


def hull(points, m, name):
    bm = bmesh.new()
    for p in points:
        bm.verts.new(p)
    bmesh.ops.convex_hull(bm, input=bm.verts)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    return o


# The chunk: the convex hull of points scattered over a chamfered cube, so
# it has many flat facets at odd angles (the glints make it read as cut
# crystal). A frosted, translucent shell over a glowing heart.
pts = []
for i in range(46):
    v = Vector((rnd.uniform(-1, 1), rnd.uniform(-1, 1), rnd.uniform(-1, 1)))
    # push to the surface of a rounded cube of half-size 0.45
    m_ = max(abs(v.x), abs(v.y), abs(v.z))
    v = v / m_
    v = Vector((v.x * 0.45, v.y * 0.45, v.z * 0.45))
    k = (abs(v.x) > 0.4) + (abs(v.y) > 0.4) + (abs(v.z) > 0.4)
    if k >= 2:
        v *= 0.86      # chamfer the edges and corners
    pts.append(v)
for sx in (-1, 1):
    for sy in (-1, 1):
        for sz in (-1, 1):
            pts.append(Vector((sx * 0.36, sy * 0.36, sz * 0.36)))
hull(pts, SHELL, "shell")
hull([p * 0.55 + Vector((rnd.uniform(-0.04, 0.04), 0, rnd.uniform(-0.04, 0.04))) for p in pts[::2]], HEART, "heart")


def crystal(base, direction, length, radius, m, sides=6, name=None):
    """A hexagonal crystal point: prism with a pyramid tip."""
    d = Vector(direction).normalized()
    q = d.to_track_quat("Z", "Y")
    bm = bmesh.new()
    ring0, ring1 = [], []
    for i in range(sides):
        a = math.tau * i / sides
        ring0.append(bm.verts.new(q @ Vector((radius * math.cos(a), radius * math.sin(a), 0.0))))
        ring1.append(bm.verts.new(q @ Vector((radius * math.cos(a), radius * math.sin(a), length * 0.7))))
    tip = bm.verts.new(q @ Vector((0, 0, length)))
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((ring0[i], ring0[j], ring1[j], ring1[i]))
        bm.faces.new((ring1[i], ring1[j], tip))
    for v in bm.verts:
        v.co += Vector(base)
    me = bpy.data.meshes.new(name or "crystal")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name or "crystal", me)
    bpy.context.collection.objects.link(o)
    me.materials.append(m)
    return o


# Clusters of points growing out of the faces (a few glow from inside).
clusters = [((0.2, -0.46, 0.2), (0.3, -1, 0.4)), ((-0.25, -0.46, -0.18), (-0.4, -1, -0.2)),
            ((0.46, 0.1, -0.2), (1, -0.3, -0.2)), ((-0.46, 0.0, 0.25), (-1, -0.2, 0.5)),
            ((0.0, 0.1, 0.46), (0.2, -0.3, 1)), ((0.15, 0.2, -0.46), (0.3, -0.2, -1))]
for k, (base, direction) in enumerate(clusters):
    for j in range(3):
        dvec = Vector(direction).normalized() + Vector((rnd.uniform(-0.35, 0.35), rnd.uniform(-0.2, 0.2),
                                                       rnd.uniform(-0.35, 0.35)))
        off = Vector((rnd.uniform(-0.07, 0.07), 0, rnd.uniform(-0.07, 0.07)))
        L = rnd.uniform(0.1, 0.2) if j else 0.22
        m = SHARD_HOT if (j == 0 and k % 2 == 0) else (SHARD if j == 0 else FROST)
        crystal(Vector(base) + off - dvec.normalized() * 0.05, dvec, L, rnd.uniform(0.03, 0.05) if j else 0.055, m)
# Light inside: a glowing seam band inlaid round the middle of the front.
for s in (-1, 1):
    crystal((s * 0.12, -0.44, -0.02), (s * 0.3, -1, 0.1), 0.08, 0.025, SHARD_HOT)

finish("block", keep=("shell", "heart"))
tri_report("block")
export("block", tex=256)
sheet("block", views=[(0, 0), (35, 25), (-50, 30)])
