# Neon Palace kit: the modelling helpers, materials and furniture shared by
# the second tower's rooms (rich1, rich2, casino, arcade, tiktoker) and the
# skybridge.  `from kit_palace import *` after `from common import *`.
#
# Room conventions (see src/world/backdrop.gd): X runs across the room
# (0..15), +Y goes deeper (y = 0 is the front of the decor, the back wall's
# face is at y = WALL = 1.95), Z is up with the floor at 0.  Every builder
# takes floor coordinates and faces -Y (the camera).
#
# Geometry is built from a few mesh generators instead of piles of cubes:
#   lathe()      turned shapes (bottles, lamps, balusters, wheels, pots)
#   prism()      a 2D outline extruded (piano body, mantel, arches, desks)
#   tube()       a smooth swept tube along a polyline (neon, arms, cables)
#   pillow()     a cushioned, optionally button-tufted surface
#   neon_text()  tube lettering from a small stroke font
# They cost a fraction of bevelled boxes for a much better silhouette.
import math
import os

import bmesh
import bpy
import mathutils
from mathutils import Vector

import common
from common import *  # noqa: F401,F403

WALL = 1.95          # the back wall's face (decor must stay in front of it)
D = 1.85             # the usual depth of the decor band
TAU = math.tau
LOOP = 120           # every idle clip in the palace lasts 4 s (120 frames)


# ------------------------------------------------------------- materials --
class _Mats:
    """Every material of the kit, created on first use after clean_scene()."""

    def __init__(self):
        self._cache = {}

    def __getattr__(self, key):
        if key.startswith("_"):
            raise AttributeError(key)
        if key not in self._cache:
            self._cache[key] = _MAT_SPECS[key]()
        return self._cache[key]

    def reset(self):
        self._cache.clear()


def _neon(rgb, s=4.0, name=None):
    return pbr("neon", tuple(c * 0.3 for c in rgb), emit=rgb, strength=s, name=name)


_MAT_SPECS = {
    # upholstery
    "velvet_plum": lambda: pbr("fabric", (0.28, 0.03, 0.16), color2=(0.36, 0.05, 0.22), name="velvet_plum"),
    "velvet_teal": lambda: pbr("fabric", (0.02, 0.2, 0.22), color2=(0.05, 0.28, 0.3), name="velvet_teal"),
    "velvet_red": lambda: pbr("fabric", (0.45, 0.02, 0.04), color2=(0.55, 0.04, 0.07), name="velvet_red"),
    "velvet_rose": lambda: pbr("fabric", (0.62, 0.20, 0.32), color2=(0.75, 0.30, 0.42), name="velvet_rose"),
    "velvet_navy": lambda: pbr("fabric", (0.04, 0.06, 0.22), color2=(0.06, 0.09, 0.3), name="velvet_navy"),
    "velvet_gold": lambda: pbr("fabric", (0.45, 0.28, 0.06), color2=(0.55, 0.36, 0.10), name="velvet_gold"),
    "leather_ox": lambda: pbr("leather", (0.28, 0.05, 0.035), name="leather_ox"),
    "leather_tan": lambda: pbr("leather", (0.45, 0.18, 0.065), name="leather_tan"),
    "leather_black": lambda: pbr("leather", (0.035, 0.032, 0.038), name="leather_black"),
    "leather_white": lambda: pbr("leather", (0.72, 0.70, 0.72), name="leather_white"),
    "linen": lambda: pbr("fabric", (0.78, 0.74, 0.76), color2=(0.66, 0.62, 0.66), name="linen"),
    "plush_pink": lambda: pbr("fabric", (0.85, 0.35, 0.55), bump=1.0, name="plush_pink"),
    "plush_blue": lambda: pbr("fabric", (0.25, 0.55, 0.9), bump=1.0, name="plush_blue"),
    "plush_yellow": lambda: pbr("fabric", (0.9, 0.7, 0.15), bump=1.0, name="plush_yellow"),
    "plush_white": lambda: pbr("fabric", (0.85, 0.83, 0.86), bump=1.0, name="plush_white"),
    "plush_lilac": lambda: pbr("fabric", (0.5, 0.35, 0.85), bump=1.0, name="plush_lilac"),
    "plush_brown": lambda: pbr("fabric", (0.35, 0.18, 0.08), bump=1.0, name="plush_brown"),
    # woods and lacquers
    "walnut": lambda: pbr("wood", (0.22, 0.10, 0.045), color2=(0.11, 0.045, 0.02), name="walnut"),
    "mahogany": lambda: pbr("wood", (0.32, 0.08, 0.035), color2=(0.16, 0.04, 0.02), name="mahogany"),
    "oak": lambda: pbr("wood", (0.40, 0.22, 0.10), color2=(0.24, 0.12, 0.05), name="oak"),
    "ebony": lambda: pbr("plastic", (0.012, 0.011, 0.015), rough=0.08, wear=0.1, grime=0.1, name="ebony"),
    "lacquer_white": lambda: pbr("plastic", (0.80, 0.79, 0.80), rough=0.15, name="lacquer_white"),
    "lacquer_plum": lambda: pbr("plastic", (0.10, 0.02, 0.10), rough=0.15, name="lacquer_plum"),
    "lacquer_red": lambda: pbr("plastic", (0.35, 0.01, 0.02), rough=0.15, name="lacquer_red"),
    # stones
    "marble_white": lambda: pbr("marble", (0.72, 0.70, 0.68), color2=(0.22, 0.21, 0.24), name="marble_white"),
    "marble_black": lambda: pbr("marble", (0.035, 0.03, 0.04), color2=(0.6, 0.45, 0.2), name="marble_black"),
    "marble_green": lambda: pbr("marble", (0.012, 0.06, 0.04), color2=(0.35, 0.45, 0.40), name="marble_green"),
    "marble_pink": lambda: pbr("marble", (0.62, 0.42, 0.44), color2=(0.30, 0.18, 0.22), name="marble_pink"),
    "terrazzo": lambda: pbr("marble", (0.10, 0.08, 0.12), color2=(0.6, 0.55, 0.5), scale=0.3, name="terrazzo"),
    "plaster": lambda: pbr("concrete", (0.32, 0.22, 0.34), grime=0.3, name="plaster"),
    # metals
    "gold": lambda: pbr("gold", (0.95, 0.66, 0.28), name="gold"),
    "brass": lambda: pbr("gold", (0.55, 0.36, 0.12), rough=0.38, name="brass"),
    "chrome": lambda: pbr("chrome", (0.88, 0.88, 0.92), name="chrome"),
    "steel": lambda: pbr("metal", (0.50, 0.51, 0.55), name="steel"),
    "gunmetal": lambda: pbr("paint", (0.035, 0.035, 0.045), name="gunmetal"),
    "black_metal": lambda: pbr("paint", (0.012, 0.012, 0.016), rough=0.35, name="black_metal"),
    "mirror": lambda: pbr("chrome", (0.45, 0.45, 0.55), rough=0.03, grime=0.05, name="mirror"),
    # plastics and misc
    "rubber": lambda: pbr("rubber", (0.02, 0.02, 0.022), name="rubber"),
    "plastic_black": lambda: pbr("plastic", (0.015, 0.015, 0.02), name="plastic_black"),
    "plastic_white": lambda: pbr("plastic", (0.75, 0.75, 0.78), name="plastic_white"),
    "plastic_grey": lambda: pbr("plastic", (0.12, 0.12, 0.14), name="plastic_grey"),
    "plastic_pink": lambda: pbr("plastic", (0.8, 0.15, 0.4), name="plastic_pink"),
    "plastic_cyan": lambda: pbr("plastic", (0.05, 0.5, 0.65), name="plastic_cyan"),
    "plastic_red": lambda: pbr("plastic", (0.6, 0.02, 0.03), name="plastic_red"),
    "plastic_yellow": lambda: pbr("plastic", (0.85, 0.6, 0.05), name="plastic_yellow"),
    "ceramic": lambda: pbr("ceramic", (0.80, 0.80, 0.82), name="ceramic"),
    "ceramic_black": lambda: pbr("ceramic", (0.02, 0.02, 0.025), name="ceramic_black"),
    "terracotta": lambda: pbr("ceramic", (0.35, 0.10, 0.05), rough=0.6, name="terracotta"),
    "leaf": lambda: pbr("plastic", (0.035, 0.2, 0.06), rough=0.45, name="leaf"),
    "leaf_light": lambda: pbr("plastic", (0.1, 0.35, 0.08), rough=0.45, name="leaf_light"),
    "soil": lambda: pbr("concrete", (0.03, 0.02, 0.015), name="soil"),
    "paper": lambda: pbr("fabric", (0.8, 0.78, 0.72), bump=0.1, name="paper"),
    "felt_green": lambda: pbr("fabric", (0.02, 0.28, 0.1), bump=0.3, name="felt_green"),
    "felt_blue": lambda: pbr("fabric", (0.02, 0.1, 0.38), bump=0.3, name="felt_blue"),
    "felt_red": lambda: pbr("fabric", (0.45, 0.02, 0.03), bump=0.3, name="felt_red"),
    "carpet_plum": lambda: pbr("carpet", (0.14, 0.02, 0.1), color2=(0.2, 0.04, 0.14), name="carpet_plum"),
    "carpet_red": lambda: pbr("carpet", (0.36, 0.02, 0.04), color2=(0.45, 0.04, 0.06), name="carpet_red"),
    "carpet_navy": lambda: pbr("carpet", (0.03, 0.03, 0.12), color2=(0.05, 0.05, 0.18), name="carpet_navy"),
    "carpet_cream": lambda: pbr("carpet", (0.55, 0.48, 0.40), color2=(0.45, 0.38, 0.30), name="carpet_cream"),
    "carpet_gold": lambda: pbr("carpet", (0.45, 0.28, 0.06), name="carpet_gold"),
    "sand": lambda: pbr("concrete", (0.55, 0.45, 0.30), grime=0.2, name="sand"),
    "rock": lambda: pbr("concrete", (0.10, 0.09, 0.12), name="rock"),
    "acoustic": lambda: pbr("fabric", (0.03, 0.025, 0.04), bump=1.0, name="acoustic"),
    # transparent
    "glass": lambda: pbr("glass", (0.70, 0.85, 0.95), alpha=0.16, name="glass"),
    "glass_dark": lambda: pbr("glass", (0.10, 0.12, 0.18), alpha=0.55, name="glass_dark"),
    "glass_bottle_green": lambda: pbr("plastic", (0.01, 0.10, 0.03), rough=0.06, name="bottle_green"),
    "glass_bottle_amber": lambda: pbr("plastic", (0.25, 0.08, 0.01), rough=0.06, name="bottle_amber"),
    "glass_bottle_clear": lambda: pbr("plastic", (0.35, 0.40, 0.45), rough=0.05, name="bottle_clear"),
    "glass_bottle_blue": lambda: pbr("plastic", (0.02, 0.05, 0.25), rough=0.06, name="bottle_blue"),
    # lights (not baked)
    "bulb": lambda: _neon((1.0, 0.72, 0.42), 4.0, "bulb"),
    "bulb_soft": lambda: _neon((1.0, 0.62, 0.35), 2.2, "bulb_soft"),
    "shade": lambda: pbr("neon", (0.7, 0.45, 0.3), emit=(1.0, 0.6, 0.32), strength=1.3, name="shade"),
    "fire_core": lambda: _neon((1.0, 0.78, 0.30), 6.0, "fire_core"),
    "fire_outer": lambda: _neon((1.0, 0.32, 0.06), 5.0, "fire_outer"),
    "ember": lambda: _neon((1.0, 0.25, 0.04), 3.0, "ember"),
    "n_pink": lambda: _neon((1.0, 0.18, 0.62), 4.5, "n_pink"),
    "n_magenta": lambda: _neon((0.9, 0.08, 0.85), 4.5, "n_magenta"),
    "n_cyan": lambda: _neon((0.2, 0.88, 1.0), 4.0, "n_cyan"),
    "n_violet": lambda: _neon((0.55, 0.22, 1.0), 4.5, "n_violet"),
    "n_amber": lambda: _neon((1.0, 0.62, 0.18), 4.0, "n_amber"),
    "n_gold": lambda: _neon((1.0, 0.80, 0.35), 3.5, "n_gold"),
    "n_red": lambda: _neon((1.0, 0.06, 0.08), 5.0, "n_red"),
    "n_green": lambda: _neon((0.25, 1.0, 0.45), 4.0, "n_green"),
    "n_white": lambda: _neon((0.95, 0.92, 1.0), 3.5, "n_white"),
    "n_blue": lambda: _neon((0.15, 0.35, 1.0), 4.5, "n_blue"),
    "n_orange": lambda: _neon((1.0, 0.40, 0.08), 4.5, "n_orange"),
    "n_mint": lambda: _neon((0.30, 1.0, 0.78), 4.0, "n_mint"),
    "backlight": lambda: pbr("neon", (0.5, 0.3, 0.15), emit=(1.0, 0.62, 0.32), strength=0.9, name="backlight"),
    "led_dim": lambda: _neon((1.0, 0.3, 0.7), 1.2, "led_dim"),
    "water": lambda: pbr("neon", (0.0, 0.05, 0.10), emit=(0.02, 0.28, 0.55), strength=1.0, name="water"),
    "water_deep": lambda: pbr("neon", (0.0, 0.02, 0.06), emit=(0.01, 0.10, 0.30), strength=1.0, name="water_deep"),
}

M = _Mats()


def reset():
    """clean_scene() plus a fresh material cache: call it first in a script."""
    clean_scene()
    M.reset()


def pivot(name, loc=(0, 0, 0), parent=None):
    """common.pivot plus a view-layer update: a fresh Empty's matrix_world
    is stale until then, and children attached to it would end up offset
    by its location a second time."""
    e = common.pivot(name, loc, parent=parent)
    bpy.context.view_layer.update()
    return e


def neon_mat(rgb, strength=4.0, name=None):
    return _neon(rgb, strength, name)


def beam_mat(rgb, alpha=0.12, strength=1.5, name="beam"):
    """A glowing translucent light shaft (emissive + alpha blend, not baked)."""
    key = ("beam", tuple(round(c, 3) for c in rgb), alpha, strength)
    if key in common._MATS:
        return common._MATS[key]
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    b = m.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Color"].default_value = (*rgb, 1.0)
    b.inputs["Emission Strength"].default_value = strength
    b.inputs["Alpha"].default_value = alpha
    b.inputs["Roughness"].default_value = 1.0
    m.blend_method = "BLEND"
    m.shadow_method = "NONE"
    m.use_backface_culling = True
    m["bake"] = False
    common._MATS[key] = m
    return m


# ------------------------------------------------------------ mesh making --
def mesh_obj(verts, faces, m, name="part", smooth=True, bevel=0.0, parent=None, closed=True, angle=40.0, face_mats=None):
    """A mesh from raw data; `m` may be a list of materials with `face_mats`
    giving each face's index into it."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate()
    me.update()
    # common.bake_textures unwraps the faces flagged selected in edit mode:
    # raw meshes start with nothing selected, so select everything.
    me.vertices.foreach_set("select", [True] * len(me.vertices))
    me.edges.foreach_set("select", [True] * len(me.edges))
    me.polygons.foreach_set("select", [True] * len(me.polygons))
    if closed:
        bm = bmesh.new()
        bm.from_mesh(me)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        bm.to_mesh(me)
        bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    if isinstance(m, list):
        common._finish(o, m[0], bevel, smooth, None, parent, smooth_angle=angle)
        me.materials.clear()
        for mm in m:
            me.materials.append(common.mat(mm))
        me.polygons.foreach_set("material_index", face_mats)
        me.update()
    else:
        common._finish(o, m, bevel, smooth, None, parent, smooth_angle=angle)
    return o


def lathe(profile, loc, m, segs=12, rot=(0, 0, 0), scale=(1, 1, 1), smooth=True, parent=None, name="lathe",
          cap=True, angle=40.0, arc=None):
    """A surface of revolution around the local Z axis. `profile` is a list
    of (radius, z) from bottom to top; radius 0 makes a pole. `arc` limits
    the sweep (radians) for half shells."""
    verts, faces, rings = [], [], []
    full = arc is None
    n = segs if full else segs + 1
    for r, z in profile:
        if r <= 1e-5:
            rings.append([len(verts)])
            verts.append((0.0, 0.0, z))
            continue
        ring = []
        for k in range(n):
            a = (arc or TAU) * k / segs
            ring.append(len(verts))
            verts.append((r * math.cos(a), r * math.sin(a), z))
        rings.append(ring)
    for i in range(len(rings) - 1):
        a, b = rings[i], rings[i + 1]
        kmax = segs if full else segs
        for k in range(kmax):
            k2 = (k + 1) % n if full else k + 1
            if len(a) == 1 and len(b) == 1:
                continue
            if len(a) == 1:
                faces.append((a[0], b[k], b[k2])[::-1] if False else (a[0], b[k2], b[k]))
            elif len(b) == 1:
                faces.append((a[k], a[k2], b[0]))
            else:
                faces.append((a[k], a[k2], b[k2], b[k]))
    if cap and full:
        if len(rings[0]) > 1:
            faces.append(tuple(reversed(rings[0])))
        if len(rings[-1]) > 1:
            faces.append(tuple(rings[-1]))
    o = mesh_obj(verts, faces, m, name, smooth, parent=None, closed=cap and full, angle=angle)
    if not (cap and full):
        # open lathes: faces were wound outward already (profile bottom->top)
        pass
    o.location = loc
    o.rotation_euler = rot
    o.scale = scale
    if parent is not None:
        attach(o, parent)
    return o


def prism(outline, a0, a1, m, plane="xz", bevel=0.0, smooth=False, parent=None, name="prism", angle=35.0):
    """Extrude a 2D outline. plane 'xz': outline is (x, z), extruded along Y
    from a0 (front) to a1. plane 'xy': outline (x, y), extruded along Z from
    a0 (bottom) to a1. plane 'yz': outline (y, z) extruded along X."""
    pts = [tuple(p) for p in outline]
    if len(pts) > 2 and (Vector(pts[0]) - Vector(pts[-1])).length < 1e-6:
        pts = pts[:-1]
    n = len(pts)

    def P(u, v, w):
        if plane == "xz":
            return (u, w, v)
        if plane == "xy":
            return (u, v, w)
        return (w, u, v)
    verts = [P(u, v, a0) for u, v in pts] + [P(u, v, a1) for u, v in pts]
    faces = [tuple(range(n)), tuple(range(2 * n - 1, n - 1, -1))]
    for i in range(n):
        j = (i + 1) % n
        faces.append((i, j, n + j, n + i))
    return mesh_obj(verts, faces, m, name, smooth, bevel, parent, closed=True, angle=angle)


def _frames(P, closed):
    n = len(P)
    T = []
    for i in range(n):
        if closed:
            d0 = (P[i] - P[i - 1]).normalized()
            d1 = (P[(i + 1) % n] - P[i]).normalized()
        else:
            d0 = (P[i] - P[max(i - 1, 0)]).normalized() if i > 0 else (P[1] - P[0]).normalized()
            d1 = (P[min(i + 1, n - 1)] - P[i]).normalized() if i < n - 1 else d0
        t = d0 + d1
        if t.length < 1e-6:
            t = d1
        T.append((t.normalized(), d0, d1))
    t0 = T[0][0]
    up = Vector((0, -1, 0)) if abs(t0.y) < 0.9 else Vector((0, 0, 1))
    N = [(up - t0 * up.dot(t0)).normalized()]
    for i in range(1, n):
        prev = N[-1]
        nn = prev - T[i][0] * prev.dot(T[i][0])
        if nn.length < 1e-6:
            nn = T[i][0].orthogonal()
        N.append(nn.normalized())
    return T, N


def tube(points, r, m, verts=6, closed=False, caps=True, parent=None, name="tube", smooth=True, radii=None, twist=0.0):
    """A swept tube along a polyline, mitred at the corners."""
    P = [Vector(p) for p in points]
    n = len(P)
    T, N = _frames(P, closed)
    vs, fs = [], []
    for i in range(n):
        t, d0, d1 = T[i]
        B = t.cross(N[i])
        cos_half = max(min(t.dot(d1), 1.0), 0.33)
        bend = d1 - d0
        k = bend.normalized() if bend.length > 1e-6 else None
        rr = radii[i] if radii else r
        for j in range(verts):
            a = TAU * j / verts + twist
            o = (N[i] * math.cos(a) + B * math.sin(a)) * rr
            if k is not None:
                o = o + k * (o.dot(k) * (1.0 / cos_half - 1.0))
            vs.append(P[i] + o)
    segs = n if closed else n - 1
    for i in range(segs):
        i2 = (i + 1) % n
        for j in range(verts):
            j2 = (j + 1) % verts
            fs.append((i * verts + j, i * verts + j2, i2 * verts + j2, i2 * verts + j))
    has_caps = caps and not closed
    if has_caps:
        fs.append(tuple(range(verts - 1, -1, -1)))
        fs.append(tuple((n - 1) * verts + j for j in range(verts)))
    return mesh_obj(vs, fs, m, name, smooth, 0.0, parent, closed=has_caps or closed, angle=70.0)


def pillow(x0, x1, z0, z1, y, depth, m, nx=8, nz=4, facing="front", tuft=0.0, tuft_nx=0, tuft_nz=0,
           soft=0.45, parent=None, name="pillow", back=True, sag=0.0):
    """A cushion: a grid bulging towards the camera (`facing` 'front': it
    spans x0..x1, z0..z1 and bulges from y+depth to y) or upwards ('up': it
    spans x0..x1 and y from z0 to z1, bulging from y-depth up to y). With
    `tuft`, buttons (a diamond pattern of tuft_nx x tuft_nz) pull in by that
    much and pleats radiate between them. `sag` dips the middle (seats)."""
    tufts = set()
    if tuft > 0 and tuft_nx > 0 and tuft_nz > 0:
        nx, nz = tuft_nx, tuft_nz
        for j in range(tuft_nz):
            for i in range(tuft_nx if j % 2 == 0 else tuft_nx - 1):
                tufts.add((2 * i + 1 + (j % 2), 2 * j + 1))
    gx, gz = nx * 2, nz * 2
    verts, faces = [], []
    for j in range(gz + 1):
        for i in range(gx + 1):
            u, v = i / gx, j / gz
            e = (math.sin(math.pi * u) ** soft) * (math.sin(math.pi * v) ** soft)
            d = depth * e - sag * math.sin(math.pi * u) * math.sin(math.pi * v)
            if (i, j) in tufts:
                d -= tuft
            elif tufts and ((i + 1, j) in tufts or (i - 1, j) in tufts or (i, j + 1) in tufts or (i, j - 1) in tufts):
                d -= tuft * 0.25
            px = x0 + (x1 - x0) * u
            pz = z0 + (z1 - z0) * v
            if facing == "front":
                verts.append((px, y + depth - d, pz))
            else:
                verts.append((px, pz, y - depth + d))
    for j in range(gz):
        for i in range(gx):
            a = j * (gx + 1) + i
            faces.append((a, a + 1, a + gx + 2, a + gx + 1))
    if back:
        ring = [j * (gx + 1) for j in range(gz, -1, -1)] + [i for i in range(1, gx + 1)] + \
               [j * (gx + 1) + gx for j in range(1, gz + 1)] + [gz * (gx + 1) + i for i in range(gx - 1, 0, -1)]
        faces.append(tuple(ring))
    return mesh_obj(verts, faces, m, name, True, 0.0, parent, closed=back, angle=80.0)


def box(size, loc, m, bevel=0.0, rot=(0, 0, 0), parent=None, name=None):
    """A box by centre; cheap (no bevel unless asked)."""
    return cube(size, loc, m, rot=rot, bevel=bevel, parent=parent, name=name)


def slab_at(x0, x1, y0, y1, z0, z1, m, bevel=0.0, parent=None):
    """A box by its extents."""
    return cube((x1 - x0, y1 - y0, z1 - z0), ((x0 + x1) / 2, (y0 + y1) / 2, (z0 + z1) / 2), m, bevel=bevel, parent=parent)


def rounded_rect(w, h, r, n=3, cx=0.0, cy=0.0):
    """Outline of a rounded rectangle (counter-clockwise)."""
    pts = []
    r = min(r, w / 2, h / 2)
    for (sx, sy, a0) in ((1, -1, -math.pi / 2), (1, 1, 0.0), (-1, 1, math.pi / 2), (-1, -1, math.pi)):
        ccx, ccy = cx + sx * (w / 2 - r), cy + sy * (h / 2 - r)
        for k in range(n + 1):
            a = a0 + (math.pi / 2) * k / n
            pts.append((ccx + math.cos(a) * r, ccy + math.sin(a) * r))
    return pts


def arch_outline(x, z0, w, h, n=10):
    """An arched opening outline: straight sides, a semicircular top."""
    r = w / 2
    pts = [(x - r, z0), (x + r, z0)]
    spring = z0 + h - r
    for k in range(n + 1):
        a = math.pi * k / n
        pts.append((x + math.cos(a) * r, spring + math.sin(a) * r))
    return pts


def circle_pts(cx, cy, r, n=16, a0=0.0, a1=TAU, rx=None, ry=None):
    rx = rx or r
    ry = ry or r
    closed = abs(a1 - a0 - TAU) < 1e-6
    k = n if closed else n + 1
    return [(cx + math.cos(a0 + (a1 - a0) * i / n) * rx, cy + math.sin(a0 + (a1 - a0) * i / n) * ry) for i in range(k)]


def in_window(windows, x0, x1, z0, z1, margin=0.1):
    """True when the box x0..x1, z0..z1 overlaps a window rect (x, z, w, h)."""
    for (wx, wz, ww, wh) in windows:
        if x1 > wx - margin and x0 < wx + ww + margin and z1 > wz - margin and z0 < wz + wh + margin:
            return True
    return False


def split_span(a, b, cuts):
    spans = [(a, b)]
    for lo, hi in cuts:
        out = []
        for s0, s1 in spans:
            if hi <= s0 or lo >= s1:
                out.append((s0, s1))
                continue
            if lo > s0:
                out.append((s0, lo))
            if hi < s1:
                out.append((hi, s1))
        spans = out
    return [(s0, s1) for s0, s1 in spans if s1 - s0 > 0.05]


def window_cuts(windows, z0, z1, margin=0.12):
    return [(wx - margin, wx + ww + margin) for (wx, wz, ww, wh) in windows if z1 > wz - margin and z0 < wz + wh + margin]


# ------------------------------------------------------------- animation --
def keys_loop(obj, path, values, index=-1, interp="LINEAR", clip="idle"):
    """Evenly spaced keys over the 4 s loop; the first value closes it."""
    n = len(values)
    ks = [(LOOP * i / n, values[i]) for i in range(n)] + [(LOOP, values[0])]
    key(obj, clip, path, ks, index=index, interp=interp)


def flicker(obj, seed=1, amp=0.18, base=1.0, steps=16, axis=2):
    """An irregular scale flicker on one axis (flames, bulbs)."""
    rnd = rng(seed)
    vals = []
    for i in range(steps):
        v = base * (1.0 + amp * (rnd() * 2 - 1))
        s = [1.0, 1.0, 1.0]
        s[axis] = v
        if axis == 2:
            s[0] = s[1] = 1.0 + (v - 1.0) * 0.4
        vals.append(tuple(s))
    keys_loop(obj, "scale", vals, interp="BEZIER")


def blink(obj, pattern, clip="idle"):
    """Scale an emissive part to 0 when `pattern` has '0' (one char per step
    over the 4 s loop), e.g. '11110000'."""
    n = len(pattern)
    ks = []
    for i, c in enumerate(pattern):
        s = (1.0, 1.0, 1.0) if c == "1" else (0.001, 0.001, 0.001)
        ks.append((LOOP * i / n, s))
    ks.append((LOOP, ks[0][1]))
    key(obj, clip, "scale", ks, interp="CONSTANT")


def rng(seed):
    state = [seed * 7919 + 17]

    def nxt():
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return (state[0] >> 8) / float(1 << 23)
    return nxt


def merge_children(p, name):
    objs = [o for o in p.children if o.type == "MESH"]
    if len(objs) < 2:
        if objs:
            objs[0].name = name
        return objs[0] if objs else None
    return join(objs, name)


# ------------------------------------------------------------ neon letters --
_S = {
    "A": [[(0, 0), (0, 4.4), (0.7, 5.6), (2, 6), (3.3, 5.6), (4, 4.4), (4, 0)], [(0, 2.8), (4, 2.8)]],
    "B": [[(0, 0), (0, 6), (2.9, 6), (3.7, 5.4), (3.7, 3.7), (2.9, 3.1), (0, 3.1)], [(2.9, 3.1), (4, 2.4), (4, 0.7), (3.2, 0), (0, 0)]],
    "C": [[(4, 4.9), (3.1, 6), (0.9, 6), (0, 4.9), (0, 1.1), (0.9, 0), (3.1, 0), (4, 1.1)]],
    "D": [[(0, 0), (0, 6), (2.4, 6), (4, 4.5), (4, 1.5), (2.4, 0), (0, 0)]],
    "E": [[(4, 6), (0, 6), (0, 0), (4, 0)], [(0, 3.1), (3, 3.1)]],
    "F": [[(4, 6), (0, 6), (0, 0)], [(0, 3.1), (3, 3.1)]],
    "G": [[(4, 4.9), (3.1, 6), (0.9, 6), (0, 4.9), (0, 1.1), (0.9, 0), (3.1, 0), (4, 1.1), (4, 2.8), (2.2, 2.8)]],
    "H": [[(0, 0), (0, 6)], [(4, 0), (4, 6)], [(0, 3.1), (4, 3.1)]],
    "I": [[(1, 0), (1, 6)]],
    "J": [[(4, 6), (4, 1.1), (3.1, 0), (0.9, 0), (0, 1.1)]],
    "K": [[(0, 0), (0, 6)], [(4, 6), (0, 2.3)], [(1.3, 3.5), (4, 0)]],
    "L": [[(0, 6), (0, 0), (4, 0)]],
    "M": [[(0, 0), (0, 6), (2.5, 2.4), (5, 6), (5, 0)]],
    "N": [[(0, 0), (0, 6), (4, 0), (4, 6)]],
    "O": [[(0.9, 0), (0, 1.1), (0, 4.9), (0.9, 6), (3.1, 6), (4, 4.9), (4, 1.1), (3.1, 0), (0.9, 0)]],
    "P": [[(0, 0), (0, 6), (3.1, 6), (4, 5.1), (4, 3.9), (3.1, 3), (0, 3)]],
    "Q": [[(0.9, 0), (0, 1.1), (0, 4.9), (0.9, 6), (3.1, 6), (4, 4.9), (4, 1.1), (3.1, 0), (0.9, 0)], [(2.6, 1.5), (4.2, -0.3)]],
    "R": [[(0, 0), (0, 6), (3.1, 6), (4, 5.1), (4, 3.9), (3.1, 3), (0, 3)], [(2.2, 3), (4, 0)]],
    "S": [[(4, 5), (3.1, 6), (0.9, 6), (0, 5), (0, 4.1), (0.9, 3.1), (3.1, 2.9), (4, 1.9), (4, 1), (3.1, 0), (0.9, 0), (0, 1)]],
    "T": [[(0, 6), (4, 6)], [(2, 6), (2, 0)]],
    "U": [[(0, 6), (0, 1.1), (0.9, 0), (3.1, 0), (4, 1.1), (4, 6)]],
    "V": [[(0, 6), (2, 0), (4, 6)]],
    "W": [[(0, 6), (1.2, 0), (2.5, 4), (3.8, 0), (5, 6)]],
    "X": [[(0, 6), (4, 0)], [(4, 6), (0, 0)]],
    "Y": [[(0, 6), (2, 3), (4, 6)], [(2, 3), (2, 0)]],
    "Z": [[(0, 6), (4, 6), (0, 0), (4, 0)]],
    "0": [[(0.9, 0), (0, 1.1), (0, 4.9), (0.9, 6), (3.1, 6), (4, 4.9), (4, 1.1), (3.1, 0), (0.9, 0)]],
    "1": [[(0.6, 4.8), (2, 6), (2, 0)], [(0.6, 0), (3.4, 0)]],
    "2": [[(0, 4.9), (0.9, 6), (3.1, 6), (4, 4.9), (4, 3.8), (0, 0), (4, 0)]],
    "3": [[(0, 4.9), (0.9, 6), (3.1, 6), (4, 4.9), (4, 4), (3.1, 3.1), (1.4, 3.1)], [(3.1, 3.1), (4, 2.1), (4, 1.1), (3.1, 0), (0.9, 0), (0, 1.1)]],
    "4": [[(3, 0), (3, 6), (0, 1.8), (4, 1.8)]],
    "5": [[(4, 6), (0.3, 6), (0, 3.4), (3.1, 3.4), (4, 2.5), (4, 1), (3.1, 0), (0, 0)]],
    "6": [[(3.6, 6), (1.5, 6), (0, 4.2), (0, 1.1), (0.9, 0), (3.1, 0), (4, 1.1), (4, 2.3), (3.1, 3.3), (0.2, 3.3)]],
    "7": [[(0, 6), (4, 6), (1.4, 0)]],
    "8": [[(0.9, 3.1), (0, 4.1), (0, 5), (0.9, 6), (3.1, 6), (4, 5), (4, 4.1), (3.1, 3.1), (0.9, 3.1), (0, 2.1), (0, 1), (0.9, 0), (3.1, 0), (4, 1), (4, 2.1), (3.1, 3.1)]],
    "9": [[(0.4, 0), (2.5, 0), (4, 1.8), (4, 4.9), (3.1, 6), (0.9, 6), (0, 4.9), (0, 3.7), (0.9, 2.7), (3.8, 2.7)]],
    "$": [[(4, 5), (3.1, 6), (0.9, 6), (0, 5), (0, 4.1), (0.9, 3.1), (3.1, 2.9), (4, 1.9), (4, 1), (3.1, 0), (0.9, 0), (0, 1)], [(2, 7), (2, -1)]],
    "!": [[(1, 6), (1, 1.8)], [(1, 0.5), (1, 0)]],
    "-": [[(0.6, 3), (3.4, 3)]],
    "+": [[(0.4, 3), (3.6, 3)], [(2, 1.4), (2, 4.6)]],
    "/": [[(0, 0), (3, 6)]],
    "'": [[(1, 6), (1, 4.6)]],
    ".": [[(1, 0), (1, 0.4)]],
    ":": [[(1, 4), (1, 4.4)], [(1, 1), (1, 1.4)]],
    "&": [[(4, 0), (0.8, 4.2), (0.8, 5.2), (1.6, 6), (2.6, 6), (3.2, 5.2), (3, 4.4), (0, 2.2), (0, 0.9), (0.9, 0), (2.4, 0), (4, 2)]],
    "*": [[(2, 1), (2, 5)], [(0.3, 2), (3.7, 4)], [(0.3, 4), (3.7, 2)]],
    "@": [[(3, 2.2), (3, 4), (2.2, 4.4), (1.2, 4), (1, 2.6), (1.8, 2), (3, 2.4), (3.6, 1.9), (4, 3), (4, 4.5), (3.1, 5.8), (0.9, 5.8), (0, 4.5), (0, 1.4),
           (0.9, 0.2), (3.3, 0.2)]],
    "#": [[(1.2, 0), (1.6, 6)], [(2.6, 0), (3, 6)], [(0.2, 2), (4, 2)], [(0.4, 4), (4.2, 4)]],
    " ": [],
}
_WIDTH = {"I": 2, "1": 4, "!": 2, "'": 2, ".": 2, ":": 2, "M": 5, "W": 5, " ": 2.5}


def text_width(text, h, spacing=1.6):
    u = h / 6.0
    w = 0.0
    for ch in text.upper():
        w += (_WIDTH.get(ch, 4) + spacing) * u
    return w - spacing * u


def neon_text(text, x, z, y, h, m, r=None, spacing=1.6, verts=5, align="left", parent=None, italic=0.0, join_as=None):
    """Glowing tube lettering standing in the wall plane at depth y; (x, z)
    is the baseline start (or centre with align='center'). Returns width."""
    u = h / 6.0
    r = r or max(h * 0.035, 0.012)
    w = text_width(text, h, spacing)
    cx = x - w / 2 if align == "center" else (x - w if align == "right" else x)
    made = []
    for ch in text.upper():
        for stroke in _S.get(ch, []):
            pts = [(cx + (px + py * italic) * u, y, z + py * u) for px, py in stroke]
            if len(pts) == 2 and (Vector(pts[0]) - Vector(pts[1])).length < 1e-4:
                continue
            made.append(tube(pts, r, m, verts=verts, parent=parent))
        cx += (_WIDTH.get(ch, 4) + spacing) * u
    if join_as and len(made) > 1:
        join(made, join_as)
    return w


def sign_board(x, z, y, w, h, m_back, m_frame=None, depth=0.06, frame=0.04):
    """A dark backing board (and a metal frame) behind a neon sign; (x, z)
    is its centre; its face is at y."""
    box((w, depth, h), (x, y + depth / 2, z), m_back)
    if m_frame is not None:
        for zz in (z - h / 2, z + h / 2):
            box((w + frame, depth + 0.02, frame), (x, y + depth / 2, zz), m_frame)
        for xx in (x - w / 2, x + w / 2):
            box((frame, depth + 0.02, h + frame), (xx, y + depth / 2, z), m_frame)


def bulb_frame(x0, x1, z0, z1, y, m, pitch=0.16, r=0.03, n_seg=4):
    """Theatre marquee bulbs around a rectangle (use an anim marquee mat)."""
    pts = []
    for (a, b) in (((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(int(L / pitch), 1)
        for i in range(k):
            t = i / k
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    for (px, pz) in pts:
        ico(r, (px, y, pz), m, subdiv=1)
    return len(pts)


# ----------------------------------------------------------- measurement --
def tri_count(objs=None):
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in (objs or all_meshes()):
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        total += sum(len(p.vertices) - 2 for p in me.polygons)
        ev.to_mesh_clear()
    return total


def finish(name, tex, budget, strip=99.0, windows=None, wall=(0.10, 0.04, 0.14)):
    """Strip invisible small bevels, join the static set, check the triangle
    budget and export (bake unless NO_BAKE=1)."""
    if strip:
        for o in all_meshes():
            if any(md.type == "BEVEL" for md in o.modifiers):
                dims = [abs(o.dimensions[i]) for i in range(3)]
                if max(dims) < strip:
                    for md in [md for md in o.modifiers if md.type == "BEVEL"]:
                        o.modifiers.remove(md)
    # join() keeps the first object's transform: a joined mesh would carry
    # e.g. the floor slab's (15, 2, 0.02) scale, and the bake's smart UV
    # project, which works in object space, then wastes most of the atlas.
    # Apply rotation and scale everywhere first.
    bpy.ops.object.select_all(action="DESELECT")
    for o in all_meshes():
        o.select_set(True)
    bpy.context.view_layer.objects.active = all_meshes()[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, isolate_users=True)
    if os.environ.get("PALACE_TOP"):
        dg = bpy.context.evaluated_depsgraph_get()
        rows = []
        for o in all_meshes():
            ev = o.evaluated_get(dg)
            me = ev.to_mesh()
            t = sum(len(p.vertices) - 2 for p in me.polygons)
            ev.to_mesh_clear()
            c = o.matrix_world.translation
            rows.append((t, o.name, o.data.materials[0].name if o.data.materials else "-", tuple(round(v, 2) for v in c)))
        rows.sort(reverse=True)
        for r in rows[:int(os.environ["PALACE_TOP"])]:
            print("TOP %5d %-14s %-14s %s" % r)
        agg = {}
        for t, n, m, c in rows:
            agg[n.split(".")[0]] = agg.get(n.split(".")[0], 0) + t
        print("BYKIND", sorted(agg.items(), key=lambda kv: -kv[1])[:12])
    join_static("decor")
    bpy.ops.object.select_all(action="DESELECT")
    for o in all_meshes():
        o.select_set(True)
    bpy.context.view_layer.objects.active = all_meshes()[0]
    bpy.ops.object.transform_apply(location=False, rotation=True, scale=True, isolate_users=True)
    tris = tri_count()
    pivots = [o.name for o in bpy.context.scene.objects if o.type == "EMPTY"]
    mats = {s.material.name for o in all_meshes() for s in o.material_slots if s.material}
    print("PALACE %s tris=%d budget=%d pivots=%d materials=%d %s" % (name, tris, budget, len(pivots), len(mats),
                                                                     "OVER BUDGET" if tris > budget else "ok"))
    front = os.environ.get("PALACE_FRONT")
    if front:
        front_render(name, front, windows, wall)
        return
    tex = int(os.environ.get("PALACE_TEX", tex))
    dbg = os.environ.get("PALACE_UVDEBUG")
    if dbg:
        names = []
        for o in all_meshes():
            at = o.data.attributes.new("origmat", "INT", "FACE")
            vals = []
            for p in o.data.polygons:
                mn = o.material_slots[p.material_index].material.name if o.material_slots else "-"
                if mn not in names:
                    names.append(mn)
                vals.append(names.index(mn))
            at.data.foreach_set("value", vals)
        big = []
        for o in all_meshes():
            for p in o.data.polygons:
                big.append((p.area, o.name, o.material_slots[p.material_index].material.name if o.material_slots else "-", tuple(round(v, 2) for v in o.matrix_world @ p.center), len(p.vertices)))
        big.sort(reverse=True)
        for r in big[:15]:
            print("BIGFACE %.2f %s %s %s n=%d" % r)
        if os.environ.get("PALACE_UVDEBUG") == "faces":
            return
        bake_textures(name, tex=tex)
        img = [im for im in bpy.data.images if im.name.endswith("_albedo")][0]
        w, h = img.size
        px = list(img.pixels)
        import collections
        tot, blk = collections.Counter(), collections.Counter()
        for o in all_meshes():
            me = o.data
            uvl = me.uv_layers.active
            if uvl is None:
                continue
            at = me.attributes["origmat"].data
            for p in me.polygons:
                mn = names[at[p.index].value]
                us = [uvl.data[li].uv for li in p.loop_indices]
                cu = sum(u.x for u in us) / len(us)
                cv = sum(u.y for u in us) / len(us)
                x = min(max(int(cu * w), 0), w - 1)
                y = min(max(int(cv * h), 0), h - 1)
                c = px[(y * w + x) * 4:(y * w + x) * 4 + 3]
                tot[mn] += p.area
                if max(c) < 0.004:
                    blk[mn] += p.area
        for mn in sorted(tot, key=lambda k: -blk[k]):
            if blk[mn] > 0:
                print("UVDBG %-22s black %.2f of %.2f m2" % (mn, blk[mn], tot[mn]))
        return
    export(name, tex=tex)


def front_render(name, out_dir, windows=None, wall=(0.10, 0.04, 0.14), samples=12):
    """A quick Cycles render from the game camera's point of view (30 m out,
    straight on) inside a stand-in room shell, for iterating without Godot."""
    os.makedirs(out_dir, exist_ok=True)
    scn = bpy.context.scene
    lo, hi = scene_bounds()
    cx = 7.5
    if name.startswith("backdrop"):
        wm = pbr("plastic", wall, rough=0.9, name="_wall")
        top = 10.0
        for piece in _wall_pieces(15.0, top, windows or []):
            x0, z0, x1, z1 = piece
            box((x1 - x0, 0.3, z1 - z0), ((x0 + x1) / 2, WALL + 0.15, (z0 + z1) / 2), wm, name="_w")
        for (wx, wz, ww, wh) in windows or []:
            box((ww, 0.05, wh), (wx + ww / 2, WALL + 2.0, wz + wh / 2), neon_mat((0.5, 0.15, 0.45), 1.0), name="_city")
        box((15.0, 2.0, 0.3), (7.5, 1.0, -0.15), pbr("plastic", tuple(c * 0.7 for c in wall), rough=0.9), name="_floor")
    lo, hi = scene_bounds()
    cz = (lo.z + hi.z) / 2
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    scn.cycles.use_denoising = False
    scn.render.resolution_x = int(os.environ.get("PALACE_W", 900))
    span_z = max(hi.z - lo.z, 3.0) + 1.0
    scn.render.resolution_y = int(scn.render.resolution_x * span_z / 16.5)
    cam_data = bpy.data.cameras.new("front_cam")
    cam_data.type = "ORTHO"
    cam_data.ortho_scale = 16.5
    cam_data.sensor_fit = "HORIZONTAL"
    cam = bpy.data.objects.new("front_cam", cam_data)
    bpy.context.collection.objects.link(cam)
    cam.location = (cx, -30.0, cz)
    cam.rotation_euler = (math.pi / 2 - float(os.environ.get("PALACE_TILT", 0.0)), 0, 0)
    scn.camera = cam
    for (pos, colour, energy) in (((7.5, -6, cz + 3), (1.0, 0.85, 0.95), 9000), ((2, -4, cz), (0.6, 0.8, 1.0), 2500)):
        ld = bpy.data.lights.new("fl", "POINT")
        ld.energy = energy
        ld.color = colour
        ld.shadow_soft_size = 2.0
        lo_ = bpy.data.objects.new("fl", ld)
        bpy.context.collection.objects.link(lo_)
        lo_.location = pos
    scn.world = scn.world or bpy.data.worlds.new("w")
    scn.world.use_nodes = True
    scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.25, 0.18, 0.35, 1.0)
    scn.world.node_tree.nodes["Background"].inputs[1].default_value = 0.6
    scn.render.filepath = os.path.join(out_dir, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("FRONT %s" % scn.render.filepath)


# ================================================================ builders --
# Each builds at floor position (x = centre, y = front edge unless noted),
# faces -Y and returns nothing interesting (the room script joins at the end).

def moulding_frame(x0, x1, z0, z1, y, m, t=0.03, d=0.025):
    """A thin applied moulding rectangle on the wall (boiserie panels): one
    ring mesh, front and both edges (24 triangles)."""
    h = t / 2
    outer = [(x0 - h, z0 - h), (x1 + h, z0 - h), (x1 + h, z1 + h), (x0 - h, z1 + h)]
    inner = [(x0 + h, z0 + h), (x1 - h, z0 + h), (x1 - h, z1 - h), (x0 + h, z1 - h)]
    yf, yb = y - d / 2, y + d / 2
    v = [(a, yf, b) for a, b in outer] + [(a, yf, b) for a, b in inner] + [(a, yb, b) for a, b in outer] + [(a, yb, b) for a, b in inner]
    f = []
    for i in range(4):
        j = (i + 1) % 4
        f.append((i, j, 4 + j, 4 + i))            # front
        f.append((8 + i, 8 + j, j, i))            # outer edge
        f.append((4 + i, 4 + j, 12 + j, 12 + i))  # inner edge
    return mesh_obj(v, f, m, "frame", False, closed=False)


def boiserie(x0, x1, z0, z1, windows, m_frame, m_fill=None, y=WALL - 0.015, pitch=1.3, inset=0.12):
    """Rows of framed wall panels between x0..x1, skipping the windows."""
    for s0, s1 in split_span(x0, x1, window_cuts(windows, z0, z1, 0.15)):
        n = max(int(round((s1 - s0) / pitch)), 1)
        w = (s1 - s0) / n
        for i in range(n):
            a, b = s0 + i * w + inset, s0 + (i + 1) * w - inset
            if b - a < 0.25:
                continue
            if m_fill is not None:
                box((b - a, 0.012, z1 - z0 - 2 * inset), ((a + b) / 2, y + 0.008, (z0 + z1) / 2), m_fill)
            moulding_frame(a, b, z0 + inset, z1 - inset, y - 0.005, m_frame)


def wainscot(x0, x1, windows, m_panel, m_rail, h=1.05, y=WALL, pitch=0.9):
    """Raised-panel wainscoting with a chair rail and a skirting board."""
    for s0, s1 in split_span(x0, x1, window_cuts(windows, 0.0, h, 0.05)):
        box((s1 - s0, 0.04, h), ((s0 + s1) / 2, y - 0.02, h / 2), m_panel)
        box((s1 - s0, 0.07, 0.16), ((s0 + s1) / 2, y - 0.035, 0.08), m_panel, bevel=0.01)
        box((s1 - s0, 0.08, 0.05), ((s0 + s1) / 2, y - 0.04, h), m_rail, bevel=0.012)
        n = max(int(round((s1 - s0) / pitch)), 1)
        w = (s1 - s0) / n
        for i in range(n):
            a, b = s0 + i * w + 0.09, s0 + (i + 1) * w - 0.09
            box((b - a, 0.03, h - 0.42), ((a + b) / 2, y - 0.05, 0.16 + (h - 0.2) / 2), m_panel, bevel=0.012)


def column(x, y, h, m_shaft, m_trim, r=0.2, segs=10, flutes=False):
    """A round column with a turned base and capital; (x, y) is its centre."""
    lathe([(r * 1.45, 0), (r * 1.45, 0.14), (r * 1.2, 0.2), (r * 1.05, 0.3)], (x, y, 0), m_trim, segs=segs, cap=False)
    lathe([(r * 1.05, 0.3), (r * 0.92, h - 0.4)], (x, y, 0), m_shaft, segs=segs, cap=False)
    lathe([(r * 0.92, h - 0.4), (r * 1.1, h - 0.3), (r * 1.55, h - 0.12), (r * 1.55, h)], (x, y, 0), m_trim, segs=segs, cap=False)
    if flutes:
        for k in range(8):
            a = TAU * k / 8
            box((0.012, 0.012, h - 0.9), (x + math.cos(a) * r * 0.97, y + math.sin(a) * r * 0.97, h / 2), m_trim)


def sconce(x, z, y=WALL, m_metal=None, m_shade=None, arms=1):
    """A wall light: backplate, curled arm(s) and a glowing shade."""
    m_metal = m_metal or M.gold
    m_shade = m_shade or M.shade
    lathe([(0.0, 0), (0.07, 0), (0.07, 0.015), (0.05, 0.03), (0.0, 0.035)], (x, y, z), m_metal, segs=10, rot=(math.pi / 2, 0, 0))
    offs = [0.0] if arms == 1 else [-0.16, 0.16]
    for dx in offs:
        tube([(x, y - 0.03, z), (x + dx * 0.5, y - 0.14, z - 0.02), (x + dx, y - 0.2, z + 0.06), (x + dx, y - 0.2, z + 0.12)], 0.012, m_metal, verts=6)
        lathe([(0.03, 0), (0.035, 0.02), (0.0, 0.03)], (x + dx, y - 0.2, z + 0.1), m_metal, segs=8)
        lathe([(0.1, 0.0), (0.1, 0.01), (0.065, 0.16), (0.06, 0.16)], (x + dx, y - 0.2, z + 0.13), m_shade, segs=12, cap=False)


def table_lamp(x, y, z, h=0.62, m_base=None, m_shade=None):
    """A ceramic ginger-jar lamp with a pleated glowing shade; (x, y) centre."""
    m_base = m_base or M.ceramic
    m_shade = m_shade or M.shade
    b = h * 0.55
    lathe([(0.06, 0), (0.13, b * 0.35), (0.12, b * 0.7), (0.04, b)], (x, y, z), m_base, segs=10)
    rod((x, y, z + b), (x, y, z + h * 0.62), 0.008, M.gold, verts=4)
    lathe([(0.2, 0.0), (0.13, h * 0.42)], (x, y, z + h * 0.58), m_shade, segs=12, cap=False)
    lathe([(0.0, 0.0), (0.19, 0.0)], (x, y, z + h * 0.585), M.bulb, segs=10, cap=False)


def side_table(x, y, z_top=0.58, r=0.26, m_top=None, m_leg=None):
    """A round pedestal side table; (x, y) centre."""
    m_top = m_top or M.marble_black
    m_leg = m_leg or M.gold
    lathe([(r * 0.7, 0), (r * 0.25, 0.06), (0.03, 0.12), (0.028, z_top - 0.05), (0.08, z_top - 0.03)], (x, y, 0), m_leg, segs=8, cap=False)
    lathe([(r, 0), (r, 0.035), (0.0, 0.035)], (x, y, z_top - 0.035), m_top, segs=14)


def coffee_table(x, y, w=1.3, d=0.6, h=0.42, m_top=None, m_frame=None):
    """Marble slab on a gold frame, a glass under-shelf; y = front edge."""
    m_top = m_top or M.marble_white
    m_frame = m_frame or M.gold
    cy = y + d / 2
    prism(rounded_rect(w, d, 0.08, 2, x, cy), h - 0.05, h, m_top, plane="xy", bevel=0.012)
    for sx in (-1, 1):
        for sy in (-1, 1):
            rod((x + sx * (w / 2 - 0.08), cy + sy * (d / 2 - 0.08), 0), (x + sx * (w / 2 - 0.08), cy + sy * (d / 2 - 0.08), h - 0.05), 0.014, m_frame, verts=6)
    for sy in (-1, 1):
        rod((x - w / 2 + 0.08, cy + sy * (d / 2 - 0.08), h - 0.07), (x + w / 2 - 0.08, cy + sy * (d / 2 - 0.08), h - 0.07), 0.012, m_frame, verts=6)
    box((w - 0.16, d - 0.16, 0.012), (x, cy, 0.12), M.glass_dark)


def chesterfield(x, y, w=2.4, m=None, d=0.95, h=0.78, feet=None, cushions=3, tufts=True):
    """A deep-buttoned Chesterfield: rolled arms and back at one height;
    x = centre, y = front edge."""
    m = m or M.leather_ox
    feet = feet or M.walnut
    x0, x1 = x - w / 2, x + w / 2
    yb = y + d
    aw = 0.2
    for fx in (x0 + 0.1, x1 - 0.1):
        for fy in (y + 0.1, yb - 0.1):
            lathe([(0.035, 0), (0.05, 0.04), (0.03, 0.1)], (fx, fy, 0), feet, segs=6, cap=False)
    # seat base with a nailhead band
    slab_at(x0 + 0.02, x1 - 0.02, y + 0.02, yb - 0.05, 0.1, 0.42, m, bevel=0.03)
    tube([(x0 + 0.05, y + 0.012, 0.16), (x1 - 0.05, y + 0.012, 0.16)], 0.008, M.brass, verts=4)
    # seat cushions
    cw = (w - 2 * aw) / cushions
    for i in range(cushions):
        a = x0 + aw + i * cw
        pillow(a + 0.01, a + cw - 0.01, y + 0.04, yb - 0.2, 0.52, 0.1, m, nx=3, nz=2, facing="up", sag=0.02)
    # buttoned back
    nt = max(int((w - 2 * aw) / 0.26), 3)
    pillow(x0 + aw - 0.02, x1 - aw + 0.02, 0.4, h - 0.02, yb - 0.24, 0.12, m, tuft=0.05 if tufts else 0.0,
           tuft_nx=nt, tuft_nz=3, nx=nt, nz=3)
    slab_at(x0 + aw, x1 - aw, yb - 0.14, yb - 0.02, 0.4, h - 0.04, m)
    # arms: tufted outer blocks
    for (a, b) in ((x0, x0 + aw), (x1 - aw, x1)):
        slab_at(a, b, y + 0.05, yb - 0.04, 0.1, h - 0.06, m, bevel=0.03)
    # the rolled rim running along both arms and the back
    rr = 0.085
    tube([(x0 + aw / 2, y + 0.06, h - 0.07), (x0 + aw / 2 - 0.01, yb - rr, h - rr * 0.7), (x1 - aw / 2 + 0.01, yb - rr, h - rr * 0.7),
          (x1 - aw / 2, y + 0.06, h - 0.07)], rr, m, verts=10)
    for ax in (x0 + aw / 2, x1 - aw / 2):
        lathe([(rr * 0.95, 0.0), (0.0, 0.025)], (ax, y + 0.06, h - 0.07), m, segs=10, rot=(math.pi / 2, 0, 0), cap=False)
        box((aw - 0.04, 0.03, h - 0.25), (ax, y + 0.045, 0.1 + (h - 0.25) / 2), m, bevel=0.01)


def armchair(x, y, m=None, w=0.92, d=0.9, h=1.1, turn=0.0, feet=None):
    """A wingback chair; x = centre, y = front edge, `turn` yaws it."""
    m = m or M.leather_ox
    feet = feet or M.walnut
    p = pivot("_chair", (x, y + d / 2, 0))
    objs_before = set(bpy.data.objects)
    x0, x1 = x - w / 2, x + w / 2
    yb = y + d
    for fx in (x0 + 0.08, x1 - 0.08):
        for fy in (y + 0.08, yb - 0.08):
            lathe([(0.03, 0), (0.025, 0.12)], (fx, fy, 0), feet, segs=5, cap=False)
    slab_at(x0 + 0.02, x1 - 0.02, y + 0.03, yb - 0.05, 0.12, 0.4, m, bevel=0.03)
    pillow(x0 + 0.16, x1 - 0.16, y + 0.05, yb - 0.2, 0.5, 0.1, m, nx=2, nz=2, facing="up", sag=0.02)
    pillow(x0 + 0.12, x1 - 0.12, 0.42, h, yb - 0.22, 0.1, m, tuft=0.04, tuft_nx=3, tuft_nz=3)
    slab_at(x0 + 0.1, x1 - 0.1, yb - 0.14, yb - 0.03, 0.4, h - 0.02, m)
    for s in (-1, 1):
        ax = x + s * (w / 2 - 0.08)
        # wing: an outline in the y-z plane
        prism([(y + 0.1, 0.12), (yb - 0.03, 0.12), (yb - 0.03, h), (yb - 0.25, h + 0.02), (y + 0.3, h * 0.85), (y + 0.2, 0.68), (y + 0.06, 0.62)],
              ax - 0.08, ax + 0.08, m, plane="yz")
        tube([(ax, y + 0.06, 0.62), (ax, y + 0.3, 0.66)], 0.075, m, verts=8)
    made = [o for o in bpy.data.objects if o not in objs_before]
    for o in made:
        attach(o, p)
    p.rotation_euler = (0, 0, turn)
    bpy.context.view_layer.update()
    for o in made:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.data.objects.remove(p, do_unlink=True)


def curtain(x0, x1, z_top, y, m, folds=5, depth=0.12, z_bottom=0.0, gather=0.0):
    """A pleated drape hanging from z_top: a wavy outline extruded down."""
    pts_f, n = [], folds * 4
    for i in range(n + 1):
        t = i / n
        pts_f.append((x0 + (x1 - x0) * t, y + depth * 0.5 * (1 - math.cos(t * folds * TAU)) * 0.5))
    outline = pts_f + [(p[0], p[1] + 0.03) for p in reversed(pts_f)]
    return prism(outline, z_bottom, z_top, m, plane="xy", smooth=True, angle=60)


def picture(x, z, w, h, art="sunset", y=WALL, m_frame=None, light=True, frame_w=0.09):
    """An oil painting in a moulded gilt frame; (x, z) is its centre."""
    m_frame = m_frame or M.gold
    fw = frame_w
    # frame: outer moulding and an inner lip
    for (sx, sz, px, pz) in ((w + 2 * fw, fw, x, z - h / 2 - fw / 2), (w + 2 * fw, fw, x, z + h / 2 + fw / 2),
                             (fw, h, x - w / 2 - fw / 2, z), (fw, h, x + w / 2 + fw / 2, z)):
        box((sx, 0.07, sz), (px, y - 0.035, pz), m_frame)
    for (sx, sz, px, pz) in ((w, 0.025, x, z - h / 2 + 0.012), (w, 0.025, x, z + h / 2 - 0.012),
                             (0.025, h, x - w / 2 + 0.012, z), (0.025, h, x + w / 2 - 0.012, z)):
        box((sx, 0.04, sz), (px, y - 0.05, pz), M.brass)
    yc = y - 0.03
    canvas_art(x, z, w - 0.04, h - 0.04, yc, art)
    if light:
        lathe([(0.018, 0), (0.018, w * 0.5)], (x - w * 0.25, y - 0.14, z + h / 2 + fw + 0.1), M.brass, segs=8, rot=(0, math.pi / 2, 0))
        box((w * 0.46, 0.02, 0.012), (x, y - 0.14, z + h / 2 + fw + 0.08), M.bulb)
        tube([(x, y - 0.005, z + h / 2 + fw), (x, y - 0.1, z + h / 2 + fw + 0.1), (x, y - 0.14, z + h / 2 + fw + 0.1)], 0.01, M.brass, verts=5)


_ART = {}


def _paint(rgb, name):
    key = ("paint", rgb)
    if key not in _ART or _ART[key].name not in bpy.data.materials:
        _ART[key] = pbr("plastic", rgb, rough=0.55, wear=0.0, grime=0.15, name=name)
    return _ART[key]


def canvas_art(x, z, w, h, y, art="sunset"):
    """The painted image: flat shapes in oil-paint colours (baked)."""
    if art == "sunset":
        bands = [(0.35, 0.05, 0.25), (0.6, 0.12, 0.3), (0.85, 0.3, 0.25), (0.95, 0.55, 0.25)]
        for i, c in enumerate(bands):
            box((w, 0.01, h * 0.55 / 4 + 0.002), (x, y, z + h / 2 - h * 0.55 * (i + 0.5) / 4), _paint(c, "oil"))
        box((w, 0.01, h * 0.45), (x, y, z - h / 2 + h * 0.225), _paint((0.04, 0.03, 0.12), "oil"))
        r = min(w, h) * 0.24
        sun = circle_pts(x, z - h * 0.05, r, 20, 0.0, math.pi)
        prism(sun, y - 0.012, y - 0.006, _paint((1.0, 0.75, 0.3), "oil"), plane="xz")
        for k in range(4):
            box((w * 0.9 * (1 - k * 0.12), 0.01, 0.012), (x, y - 0.013, z - h * 0.12 - k * h * 0.07), _paint((0.9, 0.3, 0.5), "oil"))
        for s, px in ((1, x - w * 0.3), (-1, x + w * 0.32)):
            tube([(px, y - 0.016, z - h * 0.2), (px + s * 0.02, y - 0.016, z + h * 0.05), (px + s * 0.05, y - 0.016, z + h * 0.2)], 0.012, _paint((0.02, 0.01, 0.03), "oil"), verts=4)
            for k in range(5):
                a = math.pi * (0.1 + 0.8 * k / 4)
                tube([(px + s * 0.05, y - 0.016, z + h * 0.2), (px + s * 0.05 + math.cos(a) * w * 0.12, y - 0.016, z + h * 0.2 + math.sin(a) * h * 0.05 - h * 0.04)], 0.01, _paint((0.02, 0.01, 0.03), "oil"), verts=4)
    elif art == "abstract":
        box((w, 0.01, h), (x, y, z), _paint((0.08, 0.05, 0.12), "oil"))
        box((w * 0.8, 0.01, h * 0.42), (x, y - 0.004, z + h * 0.22), _paint((0.75, 0.18, 0.28), "oil"))
        box((w * 0.8, 0.01, h * 0.34), (x, y - 0.004, z - h * 0.24), _paint((0.9, 0.55, 0.2), "oil"))
        prism(circle_pts(x + w * 0.15, z + h * 0.05, min(w, h) * 0.16, 14), y - 0.012, y - 0.008, _paint((0.95, 0.9, 0.8), "oil"), plane="xz")
    elif art == "portrait":
        box((w, 0.01, h), (x, y, z), _paint((0.05, 0.08, 0.07), "oil"))
        prism(circle_pts(x, z + h * 0.12, w * 0.17, 12, rx=w * 0.15, ry=w * 0.2), y - 0.012, y - 0.008, _paint((0.7, 0.5, 0.4), "oil"), plane="xz")
        prism([(x - w * 0.35, z - h / 2), (x + w * 0.35, z - h / 2), (x + w * 0.3, z - h * 0.15), (x, z - h * 0.05), (x - w * 0.3, z - h * 0.15)],
              y - 0.012, y - 0.008, _paint((0.12, 0.03, 0.08), "oil"), plane="xz")
        box((w * 0.34, 0.01, h * 0.08), (x, y - 0.013, z + h * 0.3), _paint((0.25, 0.15, 0.05), "oil"))
    elif art == "waves":
        box((w, 0.01, h), (x, y, z), _paint((0.75, 0.72, 0.62), "oil"))
        for k in range(4):
            pts = [(x - w / 2 + w * i / 10, y - 0.008, z - h * 0.3 + k * h * 0.18 + math.sin(i * 1.3 + k) * h * 0.05) for i in range(11)]
            tube(pts, h * 0.035, _paint([(0.05, 0.2, 0.45), (0.1, 0.35, 0.6), (0.9, 0.4, 0.3), (0.05, 0.1, 0.25)][k], "oil"), verts=4)


def potted_palm(x, y, h=2.2, m_pot=None, fronds=9, seed=3):
    """A Kentia palm in a tall pot; (x, y) is the pot centre."""
    m_pot = m_pot or M.ceramic_black
    rnd = rng(seed)
    ph = 0.55
    lathe([(0.17, 0), (0.24, ph * 0.8), (0.25, ph), (0.22, ph), (0.0, ph - 0.05)], (x, y, 0), m_pot, segs=10)
    for k in range(fronds):
        a = TAU * k / fronds + rnd() * 0.4
        lean = 0.15 + rnd() * 0.35
        top = h * (0.6 + rnd() * 0.4)
        stem_end = (x + math.cos(a) * lean * 0.6, y + math.sin(a) * lean * 0.6 * 0.6, ph + top * 0.55)
        tube([(x, y, ph - 0.05), (x + math.cos(a) * lean * 0.25, y + math.sin(a) * lean * 0.15, ph + top * 0.3), stem_end], 0.012, M.leaf_light, verts=3, caps=False)
        frond(stem_end, a, top * 0.55, M.leaf, width=0.16 + rnd() * 0.05, droop=0.8 + rnd() * 0.5)


def frond(base, heading, length, m, width=0.18, droop=1.0, n=8, flat=0.5):
    """A pinnate palm frond: a folded ribbon with zigzag leaflets, arching
    out from `base` in the horizontal direction `heading`."""
    dx, dy = math.cos(heading), math.sin(heading) * 0.6
    pts = []
    for i in range(n + 1):
        t = i / n
        pts.append(Vector((base[0] + dx * length * t, base[1] + dy * length * t,
                           base[2] + length * (0.45 * t - droop * 0.5 * t * t))))
    side = Vector((-dy, dx, 0)).normalized()
    verts, faces = [], []
    for i, p in enumerate(pts):
        t = i / n
        wv = width * math.sin(math.pi * min(t * 1.15, 1.0)) * (1.0 if i % 2 else 0.55)
        verts += [p + side * wv - Vector((0, 0, wv * flat)), p + Vector((0, 0, 0.012)), p - side * wv - Vector((0, 0, wv * flat))]
    for i in range(n):
        a, b = i * 3, (i + 1) * 3
        faces.append((a, b, b + 1, a + 1))
        faces.append((a + 1, b + 1, b + 2, a + 2))
    return mesh_obj(verts, faces, m, "frond", True, closed=False, angle=80)


def fig_tree(x, y, h=2.0, m_pot=None, seed=5, leaves=26):
    """A fiddle-leaf fig: slim trunk and big glossy paddle leaves."""
    m_pot = m_pot or M.terracotta
    rnd = rng(seed)
    ph = 0.45
    lathe([(0.16, 0), (0.2, ph * 0.9), (0.22, ph), (0.2, ph), (0.0, ph - 0.04)], (x, y, 0), m_pot, segs=10)
    trunk = [(x, y, ph - 0.05), (x + 0.03, y, ph + h * 0.35), (x - 0.02, y + 0.02, ph + h * 0.6), (x + 0.02, y, ph + h * 0.85)]
    tube(trunk, 0.025, M.walnut, verts=5)
    for k in range(leaves):
        t = 0.35 + 0.65 * (k / leaves)
        cz = ph + h * (0.3 + 0.62 * t) + rnd() * 0.1
        a = k * 2.4 + rnd() * 0.5
        L = 0.22 + rnd() * 0.08
        cx, cy = x + math.cos(a) * 0.04, y + math.sin(a) * 0.04
        leaf((cx, cy, cz), a, L, M.leaf if k % 3 else M.leaf_light, tilt=0.3 + rnd() * 0.5)


def leaf(base, heading, L, m, tilt=0.5, w=0.55):
    """A broad paddle leaf with a fold along the midrib."""
    d = Vector((math.cos(heading), math.sin(heading) * 0.7, 0)).normalized()
    up = Vector((0, 0, 1))
    tip = Vector(base) + (d * math.cos(tilt) + up * math.sin(tilt)) * L
    b = Vector(base)
    mid = b + (tip - b) * 0.55
    side = d.cross(up).normalized() * L * w * 0.5
    verts = [b, mid + side - up * 0.03, tip, mid - side - up * 0.03, mid + up * 0.015]
    faces = [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)]
    return mesh_obj(verts, faces, m, "leaf", True, closed=False, angle=80)


def rug(x0, x1, y0, y1, m_field, m_border, m_motif=None, z=0.0):
    """A thick rug with a border band and a central medallion."""
    box((x1 - x0, y1 - y0, 0.018), ((x0 + x1) / 2, (y0 + y1) / 2, z + 0.009), m_border)
    b = min(0.14, (y1 - y0) * 0.12)
    box((x1 - x0 - 2 * b, y1 - y0 - 2 * b, 0.02), ((x0 + x1) / 2, (y0 + y1) / 2, z + 0.01), m_field)
    if m_motif is not None:
        cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
        rx, ry = (x1 - x0) * 0.22, (y1 - y0) * 0.3
        prism([(cx - rx, cy), (cx, cy - ry), (cx + rx, cy), (cx, cy + ry)], z, z + 0.022, m_motif, plane="xy")


def glass_rail(x0, x1, y, z, h=0.95, m_rail=None, post_pitch=1.5, skip=()):
    """A frameless glass balustrade with a round brass handrail."""
    m_rail = m_rail or M.brass
    box((x1 - x0, 0.02, h - 0.08), ((x0 + x1) / 2, y, z + (h - 0.08) / 2 + 0.02), M.glass)
    tube([(x0, y, z + h), (x1, y, z + h)], 0.03, m_rail, verts=8)
    box((x1 - x0, 0.06, 0.04), ((x0 + x1) / 2, y, z + 0.02), m_rail)
    n = max(int((x1 - x0) / post_pitch), 1)
    for i in range(n + 1):
        px = x0 + (x1 - x0) * i / n
        box((0.05, 0.05, h), (px, y, z + h / 2), m_rail)


def bottle(x, y, z, kind=0, m=None, h=None):
    """A spirits bottle (turned): 0 wine, 1 square-shouldered spirit,
    2 squat liqueur, 3 champagne."""
    shapes = {
        0: [(0.035, 0), (0.037, 0.02), (0.037, 0.2), (0.02, 0.25), (0.013, 0.27), (0.013, 0.32), (0.0, 0.32)],
        1: [(0.04, 0), (0.042, 0.02), (0.042, 0.17), (0.035, 0.2), (0.014, 0.22), (0.014, 0.28), (0.0, 0.28)],
        2: [(0.05, 0), (0.055, 0.03), (0.05, 0.12), (0.02, 0.16), (0.014, 0.2), (0.0, 0.2)],
        3: [(0.038, 0), (0.04, 0.02), (0.04, 0.19), (0.02, 0.26), (0.016, 0.31), (0.018, 0.32), (0.0, 0.33)],
    }
    prof = shapes[kind % 4]
    s = (h / prof[-1][1]) if h else 1.0
    lathe([(r * s, zz * s) for r, zz in prof], (x, y, z), m or M.glass_bottle_green, segs=8)
    if kind % 4 in (0, 3):
        box((0.05 * s, 0.01, 0.06 * s), (x, y - 0.035 * s, z + 0.1 * s), M.paper)


def book_row(x0, x1, y, z, m_list, seed=1, h_range=(0.2, 0.3), depth=0.2, lean_last=True):
    """Books standing on a shelf between x0 and x1; y = front of the spines.
    One mesh, each book a spine, a top and two sides (8 triangles)."""
    rnd = rng(seed)
    xx = x0
    vs, fs, fm = [], [], []
    while xx < x1 - 0.03:
        bw = 0.04 + rnd() * 0.045
        if xx + bw > x1:
            break
        bh = h_range[0] + rnd() * (h_range[1] - h_range[0])
        mi = int(rnd() * len(m_list)) % len(m_list)
        a, b = xx, xx + bw
        yf = y + (rnd() - 0.5) * 0.02
        yb = yf + depth
        k = len(vs)
        vs += [(a, yf, z), (b, yf, z), (b, yf, z + bh), (a, yf, z + bh), (a, yb, z), (b, yb, z), (b, yb, z + bh), (a, yb, z + bh)]
        fs += [(k, k + 1, k + 2, k + 3), (k + 3, k + 2, k + 6, k + 7), (k + 4, k, k + 3, k + 7), (k + 1, k + 5, k + 6, k + 2)]
        fm += [mi] * 4
        xx += bw + 0.003
        if rnd() < 0.07:
            xx += 0.08
    if fs:
        mesh_obj(vs, fs, list(m_list), "books", False, closed=False, face_mats=fm)


def _wall_pieces(w, h, windows):
    edges = sorted({0.0, h} | {wz for (wx, wz, ww, wh) in windows} | {wz + wh for (wx, wz, ww, wh) in windows})
    out = []
    for y0, y1 in zip(edges, edges[1:]):
        ym = (y0 + y1) / 2
        cr = sorted([r for r in windows if r[1] < ym < r[1] + r[3]], key=lambda r: r[0])
        x = 0.0
        for (wx, wz, ww, wh) in cr:
            if wx > x:
                out.append((x, y0, wx, y1))
            x = max(x, wx + ww)
        if x < w:
            out.append((x, y0, w, y1))
    return out


_MARK = [0]


def mark(label):
    """Print the triangles added since the previous mark (budget hunting);
    only active with PALACE_PROFILE=1."""
    if os.environ.get("PALACE_PROFILE") != "1":
        return
    t = tri_count()
    print("MARK %-14s +%6d  (total %d)" % (label, t - _MARK[0], t))
    _MARK[0] = t


# ------------------------------------------------------------- ceilings --
def crystal_mat():
    return pbr("neon", (0.6, 0.62, 0.7), emit=(1.0, 0.9, 0.8), strength=2.2, name="crystal")


def drop_crystal(p, r, m, parent=None):
    """A cut-glass pendant: an elongated octahedron (8 triangles)."""
    x, y, z = p
    v = [(x, y, z), (x + r, y, z - r * 1.4), (x, y + r, z - r * 1.4), (x - r, y, z - r * 1.4), (x, y - r, z - r * 1.4), (x, y, z - r * 3.2)]
    f = [(0, 2, 1), (0, 3, 2), (0, 4, 3), (0, 1, 4), (5, 1, 2), (5, 2, 3), (5, 3, 4), (5, 4, 1)]
    return mesh_obj(v, f, m, "crystal", False, parent=parent)


def chandelier(name, x, y, drop=1.0, r=0.6, arms=8, tiers=2, m_metal=None, spin_ball=True, chain=True, strands=14):
    """A tiered crystal chandelier hanging from the ceiling (z = 0) on a
    `sway_*` pivot the game swings: gilt rings with curtains of glowing
    crystal strands and candle bulbs; a cut crystal ball under it turns
    (`spin_*`). Built to read as a sparkling mass at game distance."""
    m_metal = m_metal or M.gold
    cry = crystal_mat()
    p = pivot(name, (x, y, 0.0))
    lathe([(0.0, -0.06), (0.12, -0.05), (0.16, 0)], (x, y, 0), m_metal, segs=10, cap=False, parent=p)
    top = -drop
    if chain:
        tube([(x, y, -0.05), (x, y, top + 0.3)], 0.014, m_metal, verts=4, caps=False, parent=p)
        tube([(x, y, -0.05), (x, y, top + 0.3)], 0.03, M.velvet_red, verts=3, caps=False, parent=p, twist=0.5)
    # the crown: a small ring of strands above
    lathe([(0.0, 0.4), (0.06, 0.35), (0.05, 0.25), (0.12, 0.1), (0.1, 0.0), (0.05, -0.12), (0.08, -0.22), (0.0, -0.3)], (x, y, top), m_metal, segs=10, parent=p)
    for t in range(tiers):
        rt = r * (1.0 - 0.42 * t)
        zt = top + t * 0.36
        na = arms if t == 0 else max(arms - 3, 4)
        torus(rt, 0.022, (x, y, zt), m_metal, major_segments=18, minor_segments=4, parent=p)
        ns = strands if t == 0 else max(strands - 5, 6)
        for k in range(ns):
            a = TAU * (k + 0.5) / ns
            px, py = x + math.cos(a) * rt, y + math.sin(a) * rt
            L = 0.26 + 0.08 * ((k % 3) == 1) - 0.06 * t
            tube([(px, py, zt - 0.02), (px, py, zt - L)], 0.012, cry, verts=3, caps=False, parent=p)
            drop_crystal((px, py, zt - L), 0.022, cry, parent=p)
        for k in range(na):
            a = TAU * (k + 0.5 * t) / na
            ex, ey = x + math.cos(a) * rt, y + math.sin(a) * rt
            tube([(x + math.cos(a) * 0.08, y + math.sin(a) * 0.08, zt + 0.1), (x + math.cos(a) * rt * 0.6, y + math.sin(a) * rt * 0.6, zt - 0.02),
                  (ex, ey, zt + 0.02), (ex, ey, zt + 0.08)], 0.016, m_metal, verts=4, caps=False, parent=p)
            lathe([(0.04, 0), (0.05, 0.03), (0.02, 0.04)], (ex, ey, zt + 0.07), m_metal, segs=6, cap=False, parent=p)
            lathe([(0.0, 0), (0.04, 0.04), (0.0, 0.11)], (ex, ey, zt + 0.1), M.bulb, segs=6, parent=p)
    # a cone of strands closing the bottom
    for k in range(8):
        a = TAU * k / 8
        tube([(x + math.cos(a) * r * 0.5, y + math.sin(a) * r * 0.5, top - 0.05), (x, y, top - 0.42)], 0.01, cry, verts=3, caps=False, parent=p)
    merge_children(p, name + "_mesh")
    if spin_ball:
        sp = pivot("spin_" + name[5:] if name.startswith("sway_") else "spin_" + name, (x, y, top - 0.42), parent=p)
        ico(0.08, (x, y, top - 0.5), cry, subdiv=1, parent=sp)
        drop_crystal((x, y, top - 0.57), 0.035, cry, parent=sp)
        merge_children(sp, sp.name + "_mesh")
    return p


def cornice(x0, x1, y, m, m_trim=None, h=0.3, d=0.25, light=None):
    """A crown moulding along the ceiling's front edge (z = 0 going down),
    stepped profile, with an optional cove light strip under it."""
    prof = [(y, 0.0), (y, -h * 0.3), (y + d * 0.2, -h * 0.45), (y + d * 0.35, -h * 0.8), (y + d * 0.6, -h), (y + d, -h), (y + d, 0.0)]
    prism(prof, x0, x1, m, plane="yz")
    if m_trim is not None:
        box((x1 - x0, 0.03, 0.03), ((x0 + x1) / 2, y - 0.01, -h * 0.3), m_trim)
    if light is not None:
        tube([(x0 + 0.1, y + d * 0.7, -h - 0.02), (x1 - 0.1, y + d * 0.7, -h - 0.02)], 0.015, light, verts=4)


# ------------------------------------------------------------ bar & lounge --
def modern_sofa(x, y, w=2.2, m=None, d=0.85, h=0.72, legs=None, cushions=2):
    """A low lounge sofa: plinth, loose seat and back cushions, slim arms,
    brass legs. x = centre, y = front edge."""
    m = m or M.velvet_teal
    legs = legs or M.brass
    x0, x1, yb = x - w / 2, x + w / 2, y + d
    for fx in (x0 + 0.08, x1 - 0.08):
        for fy in (y + 0.08, yb - 0.08):
            tube([(fx, fy, 0.0), (fx, fy, 0.12)], 0.015, legs, verts=5)
    slab_at(x0, x1, y, yb, 0.12, 0.36, m)
    cw = (w - 0.3) / cushions
    for i in range(cushions):
        a = x0 + 0.15 + i * cw
        pillow(a + 0.01, a + cw - 0.01, y + 0.02, yb - 0.25, 0.47, 0.11, m, nx=2, nz=2, facing="up", sag=0.02)
        pillow(a + 0.02, a + cw - 0.02, 0.4, h, yb - 0.3, 0.14, m, nx=2, nz=2)
    slab_at(x0 + 0.1, x1 - 0.1, yb - 0.16, yb, 0.36, h - 0.05, m)
    for (a, b) in ((x0, x0 + 0.15), (x1 - 0.15, x1)):
        slab_at(a, b, y, yb, 0.36, 0.58, m)
        tube([((a + b) / 2, y + 0.02, 0.58), ((a + b) / 2, yb - 0.02, 0.58)], 0.075, m, verts=8)


def bar_stool(x, y, h=0.78, m_seat=None, m_metal=None):
    """A chrome pedestal stool with a leather seat; (x, y) centre."""
    m_seat = m_seat or M.leather_black
    m_metal = m_metal or M.chrome
    lathe([(0.2, 0), (0.2, 0.015), (0.05, 0.04), (0.03, 0.06), (0.028, h - 0.08), (0.08, h - 0.04)], (x, y, 0), m_metal, segs=10, cap=False)
    torus(0.16, 0.012, (x, y, 0.3), m_metal, major_segments=10, minor_segments=3)
    lathe([(0.0, 0), (0.19, 0.0), (0.21, 0.04), (0.19, 0.08), (0.0, 0.09)], (x, y, h - 0.05), m_seat, segs=12)


def cocktail(x, y, z, kind=0, m_drink=None):
    """A glass: 0 martini, 1 coupe, 2 highball."""
    g = M.glass_bottle_clear
    if kind == 0:
        lathe([(0.03, 0), (0.004, 0.005), (0.004, 0.08), (0.055, 0.14)], (x, y, z), g, segs=6, cap=False)
        lathe([(0.0, 0.1), (0.045, 0.13)], (x, y, z), m_drink or M.n_pink, segs=6, cap=False)
    elif kind == 1:
        lathe([(0.03, 0), (0.004, 0.005), (0.004, 0.07), (0.03, 0.08), (0.045, 0.11)], (x, y, z), g, segs=6, cap=False)
        lathe([(0.0, 0.085), (0.04, 0.1)], (x, y, z), m_drink or M.n_amber, segs=6, cap=False)
    else:
        lathe([(0.032, 0), (0.035, 0.14)], (x, y, z), g, segs=6, cap=False)
        lathe([(0.0, 0.01), (0.03, 0.01), (0.032, 0.1), (0.0, 0.1)], (x, y, z), m_drink or M.n_cyan, segs=6)


def speaker(x, y, w=0.55, h=1.2, d=0.45, name=None, beat_phase=0.0):
    """A PA cabinet with a pulsing woofer (a keyed pivot) and a horn."""
    slab_at(x - w / 2, x + w / 2, y, y + d, 0.0, h, M.black_metal)
    box((w - 0.06, 0.012, h - 0.06), (x, y - 0.004, h / 2), M.acoustic)
    for k, zz in enumerate((h * 0.3, h * 0.66) if h > 1.0 else (h * 0.4,)):
        r = w * 0.36
        lathe([(r * 1.08, 0), (r * 1.08, -0.01), (0.0, -0.012)], (x, y - 0.006, zz), M.plastic_grey, segs=12, rot=(math.pi / 2, 0, 0), cap=False)
        p = pivot("%s_%d" % (name or "woofer", k), (x, y - 0.01, zz))
        lathe([(0.0, 0.05), (r * 0.25, 0.04), (r, -0.005)], (x, y - 0.01, zz), M.rubber, segs=12, rot=(math.pi / 2, 0, 0), parent=p, cap=False)
        lathe([(0.0, 0.07), (r * 0.22, 0.05)], (x, y - 0.01, zz), M.plastic_black, segs=8, rot=(math.pi / 2, 0, 0), parent=p, cap=False)
        merge_children(p, p.name + "_mesh")
        vals = []
        for i in range(16):
            s = 1.0 + (0.12 if i % 2 == 0 else 0.0) * (1.0 if (i // 2 + int(beat_phase)) % 4 else 0.5)
            vals.append((s, 1.0 + (s - 1.0) * 3, s))
        keys_loop(p, "scale", vals, interp="LINEAR")
    box((w * 0.5, 0.02, 0.1), (x, y - 0.01, h - 0.1), M.plastic_grey)
    box((0.06, 0.015, 0.02), (x + w / 2 - 0.08, y - 0.012, 0.08), M.n_cyan)


RGB = {"pink": (1.0, 0.18, 0.62), "magenta": (0.9, 0.08, 0.85), "cyan": (0.2, 0.88, 1.0), "violet": (0.55, 0.22, 1.0),
       "amber": (1.0, 0.62, 0.18), "gold": (1.0, 0.8, 0.35), "red": (1.0, 0.06, 0.08), "green": (0.25, 1.0, 0.45),
       "white": (0.95, 0.92, 1.0), "blue": (0.15, 0.35, 1.0), "orange": (1.0, 0.4, 0.08), "mint": (0.3, 1.0, 0.78)}


def anim_neon(rgb, kind="screen", strength=None):
    """An emissive material the game animates (anim_screen scanlines or
    anim_marquee chasing dots); `rgb` is a colour or an RGB key."""
    if isinstance(rgb, str):
        rgb = RGB[rgb]
    s = strength if strength is not None else (1.6 if kind == "screen" else 3.0)
    return pbr("screen", tuple(c * 0.3 for c in rgb), emit=rgb, strength=s, name="anim_" + kind)


def quad_dots(pts, y, size, m, diamond=False, name="dots"):
    """Many small camera-facing squares (2 triangles each) in one mesh: bulbs
    and LEDs. `pts` are (x, z) at depth y."""
    vs, fs = [], []
    h = size / 2
    for (px, pz) in pts:
        k = len(vs)
        if diamond:
            vs += [(px, y, pz - h), (px + h, y, pz), (px, y, pz + h), (px - h, y, pz)]
        else:
            vs += [(px - h, y, pz - h), (px + h, y, pz - h), (px + h, y, pz + h), (px - h, y, pz + h)]
        fs.append((k, k + 1, k + 2, k + 3))
    return mesh_obj(vs, fs, m, name, False, closed=False)


def rect_pts(x0, x1, z0, z1, pitch):
    """Points around a rectangle's border every `pitch`."""
    pts = []
    for (a, b) in (((x0, z0), (x1, z0)), ((x1, z0), (x1, z1)), ((x1, z1), (x0, z1)), ((x0, z1), (x0, z0))):
        L = math.hypot(b[0] - a[0], b[1] - a[1])
        k = max(int(L / pitch), 1)
        for i in range(k):
            t = i / k
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t))
    return pts


def stanchions(points, m_post=None, m_rope=None, h=0.95, sag=0.14):
    """Brass posts with velvet ropes sagging between consecutive points."""
    m_post = m_post or M.brass
    m_rope = m_rope or M.velvet_red
    for (px, py) in points:
        lathe([(0.15, 0), (0.15, 0.03), (0.05, 0.06), (0.025, 0.1), (0.022, h - 0.06), (0.04, h - 0.03), (0.0, h + 0.03)], (px, py, 0), m_post, segs=8)
    for (a, b) in zip(points, points[1:]):
        pts = []
        for i in range(7):
            t = i / 6
            pts.append((a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t, h - 0.08 - sag * math.sin(t * math.pi)))
        tube(pts, 0.022, m_rope, verts=5)


def chip_stack(x, y, z, n, m, r=0.02):
    lathe([(r, 0), (r, n * 0.0035), (0.0, n * 0.0035)], (x, y, z), m, segs=7)


def flat_dots(pts, z, size, m, name="flat"):
    """Small squares lying flat (facing up) at height z: board layouts."""
    vs, fs = [], []
    h = size / 2
    for (px, py) in pts:
        k = len(vs)
        vs += [(px - h, py - h, z), (px + h, py - h, z), (px + h, py + h, z), (px - h, py + h, z)]
        fs.append((k, k + 1, k + 2, k + 3))
    return mesh_obj(vs, fs, m, name, False, closed=False)


def ring_segments(cx, cy, z, r0, r1, n, mats, name="ring", parent=None, start=0.0, upright=False):
    """A flat annulus split into n wedges cycling through `mats` (roulette
    pockets, wheel segments). Facing up; with `upright`, it stands in the
    wall plane facing the camera: (cx, cy) is then (x, z) and z is the depth."""
    vs, fs, fm = [], [], []
    P = (lambda u, v: (u, z, v)) if upright else (lambda u, v: (u, v, z))
    for i in range(n):
        a0 = start + TAU * i / n
        a1 = start + TAU * (i + 1) / n
        k = len(vs)
        vs += [P(cx + math.cos(a0) * r0, cy + math.sin(a0) * r0), P(cx + math.cos(a0) * r1, cy + math.sin(a0) * r1),
               P(cx + math.cos(a1) * r1, cy + math.sin(a1) * r1), P(cx + math.cos(a1) * r0, cy + math.sin(a1) * r0)]
        fs.append((k, k + 1, k + 2, k + 3))
        fm.append(i % len(mats))
    return mesh_obj(vs, fs, list(mats), name, False, parent=parent, closed=False, face_mats=fm)


def ceiling_fan(name, x, y, drop=0.45, r=0.75, blades=5, m_metal=None, m_blade=None, light=True):
    """A ceiling fan: downrod, motor housing, leaf-shaped blades on a
    `spin_*` pivot the game turns, and a glowing bowl."""
    m_metal = m_metal or M.brass
    m_blade = m_blade or M.walnut
    lathe([(0.0, -0.04), (0.1, -0.03), (0.1, 0.0)], (x, y, 0.0), m_metal, segs=10, cap=False)
    tube([(x, y, -0.03), (x, y, -drop + 0.1)], 0.02, m_metal, verts=5, caps=False)
    lathe([(0.0, 0.14), (0.09, 0.12), (0.13, 0.06), (0.13, 0.0), (0.1, -0.04), (0.0, -0.05)], (x, y, -drop), m_metal, segs=12)
    p = pivot(name, (x, y, -drop - 0.02))
    for k in range(blades):
        a = TAU * k / blades
        c, s_ = math.cos(a), math.sin(a)
        tube([(x + c * 0.1, y + s_ * 0.1, -drop - 0.02), (x + c * 0.24, y + s_ * 0.24, -drop - 0.03)], 0.012, m_metal, verts=4, parent=p)
        outline = []
        for i in range(9):
            t = i / 8
            w = 0.09 * math.sin(math.pi * min(t * 1.1, 1.0)) + 0.02
            outline.append((0.22 + t * (r - 0.22), w))
        outline += [(u, -v) for (u, v) in reversed(outline)]
        pts = [(x + c * u - s_ * v, y + s_ * u + c * v) for (u, v) in outline]
        o = prism(pts, -drop - 0.045, -drop - 0.03, m_blade, plane="xy", parent=p)
    if light:
        lathe([(0.0, -0.12), (0.1, -0.1), (0.13, -0.04), (0.12, 0.0)], (x, y, -drop - 0.04), M.shade, segs=10, cap=False, parent=p)
    merge_children(p, name + "_mesh")
    return p


def plush(x, y, z, s, m, kind=0):
    """A soft toy: 0 teddy, 1 bunny, 2 blob with a bow."""
    sphere(0.16 * s, (x, y, z + 0.16 * s), m, scale=(1.0, 0.85, 1.05), segments=8, rings=5)
    sphere(0.12 * s, (x, y - 0.02 * s, z + 0.38 * s), m, segments=8, rings=5)
    if kind == 0:
        for sx in (-1, 1):
            ico(0.045 * s, (x + sx * 0.09 * s, y, z + 0.48 * s), m, subdiv=1)
    elif kind == 1:
        for sx in (-1, 1):
            ico(0.035 * s, (x + sx * 0.05 * s, y, z + 0.55 * s), m, subdiv=1).scale = (1, 0.7, 3.0)
    else:
        ico(0.04 * s, (x, y - 0.1 * s, z + 0.5 * s), M.plastic_red, subdiv=1)
    ico(0.035 * s, (x, y - 0.13 * s, z + 0.36 * s), M.plush_white, subdiv=1)
    quad_dots([(x - 0.04 * s, z + 0.42 * s), (x + 0.04 * s, z + 0.42 * s)], y - 0.13 * s, 0.028 * s, M.plastic_black)
    for sx in (-1, 1):
        ico(0.05 * s, (x + sx * 0.14 * s, y - 0.05 * s, z + 0.2 * s), m, subdiv=1)


def disco_ball(name, x, y, drop=0.8, r=0.3, sparkle=None):
    """A mirror ball on a chain, on a `spin_*` pivot the game turns; glints
    (small glowing squares on its skin) orbit with it."""
    tube([(x, y, 0.0), (x, y, -drop + r)], 0.01, M.chrome, verts=4, caps=False)
    lathe([(0.0, -0.03), (0.06, -0.02), (0.06, 0.0)], (x, y, 0.0), M.chrome, segs=8, cap=False)
    p = pivot(name, (x, y, -drop))
    o = sphere(r, (x, y, -drop), pbr("chrome", (0.8, 0.82, 0.9), rough=0.12, name="mirrorball"), segments=14, rings=9, smooth=False, parent=p)
    rnd = rng(int(x * 10))
    vs, fs = [], []
    for i in range(26):
        a = rnd() * TAU
        e = (rnd() - 0.5) * 2.4
        n = Vector((math.cos(a) * math.cos(e), math.sin(a) * math.cos(e), math.sin(e)))
        c = Vector((x, y, -drop)) + n * (r + 0.004)
        t1 = n.cross(Vector((0, 0, 1))).normalized() if abs(n.z) < 0.99 else Vector((1, 0, 0))
        t2 = n.cross(t1)
        h = 0.022
        k = len(vs)
        vs += [c - t1 * h - t2 * h, c + t1 * h - t2 * h, c + t1 * h + t2 * h, c - t1 * h + t2 * h]
        fs.append((k, k + 1, k + 2, k + 3))
    mesh_obj(vs, fs, sparkle or neon_mat((1.0, 0.95, 1.0), 4.0, "glint"), "glints", False, parent=p, closed=False)
    merge_children(p, name + "_mesh")
    return p


def moving_head(name, x, y, colour, beam=2.6, aim=0.0, sweep=0.45, phase=0.0, sway=False):
    """A stage moving-head light under the ceiling with a translucent beam;
    it sweeps side to side (keyed idle) or, with `sway`, is left to the
    game's sway_* swing."""
    slab_at(x - 0.12, x + 0.12, y - 0.1, y + 0.1, -0.06, 0.0, M.black_metal)
    tube([(x - 0.1, y, -0.06), (x - 0.1, y, -0.2)], 0.015, M.black_metal, verts=4)
    tube([(x + 0.1, y, -0.06), (x + 0.1, y, -0.2)], 0.015, M.black_metal, verts=4)
    p = pivot(name, (x, y, -0.2))
    lathe([(0.0, 0.1), (0.08, 0.09), (0.09, 0.0), (0.075, -0.12), (0.0, -0.13)], (x, y, -0.2), M.black_metal, segs=10, parent=p)
    lathe([(0.0, 0.0), (0.065, 0.0)], (x, y, -0.33), neon_mat(colour, 5.0, "lens"), segs=10, rot=(math.pi, 0, 0), parent=p, cap=False)
    lathe([(0.06, 0.0), (beam * 0.18, -beam)], (x, y, -0.33), beam_mat(colour, 0.1, 1.2), segs=12, parent=p, cap=False)
    merge_children(p, name + "_mesh")
    p.rotation_euler = (0, aim, 0)
    if not sway:
        key(p, "idle", "rotation_euler", [(LOOP * k / 8, (0.08 * math.sin(k * math.pi / 2 + phase), aim + sweep * math.sin(k * math.pi / 4 + phase), 0)) for k in range(9)],
            interp="BEZIER")
    return p


def pendant(name, x, y, drop, m_shade=None, m_metal=None, kind="globe", r=0.14):
    """A hanging lamp on a `sway_*` pivot: globe, dome or lantern."""
    m_metal = m_metal or M.brass
    p = pivot(name, (x, y, 0.0))
    lathe([(0.0, -0.02), (0.07, -0.015), (0.07, 0.0)], (x, y, 0.0), m_metal, segs=8, parent=p, cap=False)
    tube([(x, y, -0.02), (x, y, -drop + r)], 0.006, M.plastic_black, verts=3, caps=False, parent=p)
    if kind == "globe":
        lathe([(0.03, r * 1.05), (0.035, r * 0.95)], (x, y, -drop), m_metal, segs=8, parent=p, cap=False)
        sphere(r, (x, y, -drop), m_shade or M.shade, segments=10, rings=7, parent=p)
    elif kind == "dome":
        lathe([(0.0, r * 0.9), (r * 0.5, r * 0.75), (r * 1.2, 0.0), (r * 1.25, -0.02)], (x, y, -drop), m_metal, segs=12, parent=p, cap=False)
        lathe([(0.0, 0.0), (r * 1.15, 0.0)], (x, y, -drop + 0.01), m_shade or M.bulb, segs=12, parent=p, cap=False, rot=(math.pi, 0, 0))
    else:
        lathe([(0.0, r * 1.2), (r * 0.7, r * 0.9), (r, 0.0), (r * 0.7, -r * 0.9), (0.0, -r * 1.2)], (x, y, -drop), m_shade or M.shade, segs=10, parent=p)
        for k in range(4):
            a = TAU * k / 4
            tube([(x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72, -drop + r * 0.88), (x + math.cos(a) * r * 1.01, y + math.sin(a) * r * 1.01, -drop),
                  (x + math.cos(a) * r * 0.72, y + math.sin(a) * r * 0.72, -drop - r * 0.88)], 0.006, m_metal, verts=3, caps=False, parent=p)
    merge_children(p, name + "_mesh")
    return p


def beacon(name, x, y, colour=(1.0, 0.1, 0.1)):
    """A rotating warning beacon: a clear dome over a spinning mirror and
    lamp on a `spin_*` pivot."""
    lathe([(0.1, 0.0), (0.1, -0.08), (0.0, -0.08)], (x, y, 0.0), M.black_metal, segs=10)
    p = pivot(name, (x, y, -0.2))
    lathe([(0.0, 0.0), (0.075, 0.0), (0.075, 0.1), (0.0, 0.1)], (x, y, -0.2), M.chrome, segs=8, parent=p, arc=math.pi)
    lathe([(0.0, 0.0), (0.075, 0.0), (0.075, 0.1), (0.0, 0.1)], (x, y, -0.2), neon_mat(colour, 5.0, "beacon"), segs=8, parent=p,
          arc=math.pi, rot=(0, 0, math.pi))
    lathe([(0.08, 0.0), (0.4, -1.8)], (x, y, -0.15), beam_mat(colour, 0.1, 1.5), segs=10, arc=math.pi * 0.35, parent=p, rot=(math.pi / 2, 0, 0))
    merge_children(p, name + "_mesh")
    lathe([(0.1, -0.08), (0.1, -0.2), (0.07, -0.26), (0.0, -0.28)], (x, y, 0.0), pbr("glass", colour, alpha=0.35, name="beacon_dome"), segs=10, cap=False)
    return p
