# Builders for the hazards, gadgets and the bat boss: things with moving
# pivots the game animates. Same conventions as the rest of the kit: origin at
# the bottom centre for floor props (centred for things that fly or tumble),
# the front faces -Y in Blender (+Z in Godot, towards the camera).
#
# The first half holds small mesh helpers (surfaces of revolution, swept
# tubes, coil springs, text, animation shorthands); each builder then makes
# one model. Materials are pbr() presets (see common.py / STYLE.md) and are
# created inside the builders because clean_scene() empties the cache.
import math

import bmesh
import bpy
from mathutils import Matrix, Quaternion, Vector

import common
from common import *  # noqa: F401,F403

TAU = math.tau
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


# ------------------------------------------------------------ mesh helpers --
def _obj(name, bm, m, smooth=True, bevel=0.0, parent=None, angle=45.0, mats=()):
    """Turn a bmesh into an object with material `m` (+ extra slots `mats`,
    addressed by the faces' material_index)."""
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    common._link(o)
    bpy.context.view_layer.objects.active = o
    idx = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", idx)   # materials.clear() resets them
    if parent is not None:
        bpy.context.view_layer.update()   # attach() reads parent.matrix_world
    common._finish(o, m, bevel, smooth, None, parent, smooth_angle=angle)
    for x in mats:
        o.data.materials.append(common.mat(x))
    me.polygons.foreach_set("material_index", idx)
    return o


def piv(name, loc=(0, 0, 0), parent=None):
    """A named pivot (Empty). Under a parent it is placed relative to it with
    an identity parent-inverse, so its keyed location/rotation/scale are the
    plain glTF node values (parents are unrotated at rest)."""
    bpy.context.view_layer.update()
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    common._link(e)
    if parent is not None:
        e.parent = parent
        e.location = Vector(loc) - parent.matrix_world.translation
    else:
        e.location = loc
    bpy.context.view_layer.update()
    return e


def merge_under(p, name, keep=()):
    """Join the mesh children of pivot `p` into one mesh (fewer draw calls);
    children named in `keep` stay separate."""
    kids = [c for c in p.children if c.type == "MESH" and c.name not in keep]
    if len(kids) < 2:
        if kids:
            kids[0].name = name
        return kids[0] if kids else None
    o = join(kids, name)
    return o


def hang(child, parent):
    """attach() with fresh world matrices."""
    bpy.context.view_layer.update()
    return attach(child, parent)


def _bridge(bm, a, b, closed=True, mat=None):
    """Quads between two vertex rings (a vertex repeated = a pole)."""
    faces = []
    n = len(a)
    for i in range(n if closed else n - 1):
        j = (i + 1) % n
        quad = []
        for v in (a[i], a[j], b[j], b[i]):
            if v not in quad:
                quad.append(v)
        if len(quad) >= 3:
            try:
                f = bm.faces.new(quad)
            except ValueError:
                continue
            if mat is not None:
                f.material_index = mat(i) if callable(mat) else mat
            faces.append(f)
    return faces


def lathe(profile, m, loc=(0, 0, 0), segs=24, rot=(0, 0, 0), name="lathe", parent=None, smooth=True,
          angle=50.0, cap=True, arc=None, scale=(1.0, 1.0), band_mats=None, seg_mat=None, mats=(), bevel=0.0):
    """Revolve a (radius, z) profile around Z, listed from the bottom centre
    outwards and up (normals then face out). r = 0 makes a pole. `arc`
    = (a0, a1) revolves only part of the way (ends capped). `band_mats[i]`
    / `seg_mat(i)` pick material slots per profile band / per segment."""
    bm = bmesh.new()
    if arc is None:
        angles = [TAU * i / segs for i in range(segs)]
        closed = True
    else:
        angles = [arc[0] + (arc[1] - arc[0]) * i / segs for i in range(segs + 1)]
        closed = False
    rings = []
    for r, z in profile:
        if r <= 1e-6:
            v = bm.verts.new((0, 0, z))
            rings.append([v] * len(angles))
        else:
            rings.append([bm.verts.new((math.cos(a) * r * scale[0], math.sin(a) * r * scale[1], z)) for a in angles])
    for k in range(len(rings) - 1):
        mat = seg_mat
        if band_mats is not None:
            mat = band_mats[k]
        _bridge(bm, rings[k], rings[k + 1], closed=closed, mat=mat)
    if cap and profile[0][0] > 1e-6 and closed:
        bm.faces.new(list(reversed(rings[0])))
    if cap and profile[-1][0] > 1e-6 and closed:
        bm.faces.new(rings[-1])
    if not closed and cap:
        for idx in (0, -1):
            ring = [r[idx] for r in rings]
            uniq = []
            for v in ring:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                try:
                    bm.faces.new(uniq if idx == 0 else list(reversed(uniq)))
                except ValueError:
                    pass
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _obj(name, bm, m, smooth=smooth, angle=angle, mats=mats, bevel=bevel)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        attach(o, parent)
    return o


def _frames(pts):
    """Parallel-transport frames (tangent, normal, binormal) along a polyline."""
    pts = [Vector(p) for p in pts]
    n = len(pts)
    tans = []
    for i in range(n):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, n - 1)]
        tans.append((b - a).normalized())
    t0 = tans[0]
    ref = Vector((0, 0, 1)) if abs(t0.z) < 0.9 else Vector((1, 0, 0))
    nrm = t0.cross(ref).normalized()
    out = []
    for i in range(n):
        if i > 0:
            q = tans[i - 1].rotation_difference(tans[i])
            nrm = (q @ nrm).normalized()
        out.append((pts[i], tans[i], nrm, tans[i].cross(nrm)))
    return out


def sweep(points, r, m, prof=6, name="tube", parent=None, smooth=True, cap=True, angle=60.0, closed=False,
          squash=1.0, twist=0.0, mats=(), mat=None, bevel=0.0):
    """A tube along a 3D polyline. `r` is a radius or one radius per point;
    `squash` flattens the section along the binormal; closed=True joins the
    ends (a ring)."""
    radii = r if isinstance(r, (list, tuple)) else [r] * len(points)
    pts = list(points)
    if closed:
        pts = pts + [pts[0], pts[1]]
        radii = list(radii) + [radii[0], radii[1]]
    fr = _frames(pts)
    if closed:
        fr = fr[1:-1]
        radii = radii[1:-1]
        fr = fr[-1:] + fr[:-1]
        radii = radii[-1:] + radii[:-1]
    bm = bmesh.new()
    rings = []
    for k, ((p, t, nrm, b), rad) in enumerate(zip(fr, radii)):
        if rad <= 1e-6:
            v = bm.verts.new(p)
            rings.append([v] * prof)
            continue
        ring = []
        for i in range(prof):
            a = TAU * i / prof + twist * k
            ring.append(bm.verts.new(p + (nrm * math.cos(a) + b * math.sin(a) * squash) * rad))
        rings.append(ring)
    for k in range(len(rings) - 1):
        _bridge(bm, rings[k], rings[k + 1], mat=mat)
    if closed:
        _bridge(bm, rings[-1], rings[0], mat=mat)
    elif cap:
        if radii[0] > 1e-6:
            bm.faces.new(list(reversed(rings[0])))
        if radii[-1] > 1e-6:
            bm.faces.new(rings[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(name, bm, m, smooth=smooth, parent=parent, angle=angle, mats=mats, bevel=bevel)


def coil(p0, p1, radius, wire, turns, m, spt=6, prof=3, name="spring", parent=None):
    """A helical coil spring from p0 to p1 (with short straight hooks)."""
    a, b = Vector(p0), Vector(p1)
    axis = b - a
    length = axis.length
    rot = axis.normalized().to_track_quat("Z", "Y").to_matrix()
    hook = min(0.2 * length, 0.02)
    pts = [a]
    n = int(turns * spt)
    for i in range(n + 1):
        t = i / n
        ang = TAU * turns * t
        local = Vector((math.cos(ang) * radius, math.sin(ang) * radius, hook + (length - 2 * hook) * t))
        pts.append(a + rot @ local)
    pts.append(b)
    return sweep(pts, wire, m, prof=prof, name=name, parent=parent, cap=False)


def superellipse(cx, cz, w, h, n=2.6, count=20, y0=0.0, plane="YZ"):
    """Points of a rounded-rectangle section (|y/w|^n + |z/h|^n = 1)."""
    out = []
    for i in range(count):
        a = TAU * i / count
        c, s = math.cos(a), math.sin(a)
        y = w * math.copysign(abs(c) ** (2.0 / n), c)
        z = h * math.copysign(abs(s) ** (2.0 / n), s)
        if plane == "YZ":
            out.append((cx, y, cz + z))
        else:   # XZ section at depth y0 (cx is the centre x)
            out.append((cx + y, y0, cz + z))
    return out


def loft(rings, m, name="loft", mats=(), mat_fn=None, smooth=True, angle=60.0, parent=None, cap=True, bevel=0.0):
    """Skin rings of points (same count; a single point = a pole). `mat_fn`
    gets a face's centre and returns its material slot."""
    bm = bmesh.new()
    vr = []
    n = max(len(r) for r in rings)
    for r in rings:
        if len(r) == 1:
            v = bm.verts.new(r[0])
            vr.append([v] * n)
        else:
            vr.append([bm.verts.new(p) for p in r])
    for a, b in zip(vr, vr[1:]):
        _bridge(bm, a, b)
    if cap:
        if len(rings[0]) > 1:
            bm.faces.new(list(reversed(vr[0])))
        if len(rings[-1]) > 1:
            bm.faces.new(vr[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    if mat_fn is not None:
        for f in bm.faces:
            f.material_index = mat_fn(f.calc_center_median())
    return _obj(name, bm, m, smooth=smooth, angle=angle, parent=parent, mats=mats, bevel=bevel)


def rbox(size, loc, m, r=0.02, rot=(0, 0, 0), name=None, parent=None):
    """A box with rounded (bevelled) edges."""
    return cube(size, loc, m, rot=rot, bevel=r, name=name, parent=parent)


def prism(poly, depth, m, y=0.0, name="prism", parent=None, bevel=0.0, smooth=False, axis="Y"):
    """Extrude a 2D polygon given in the XZ plane (x, z) along Y, centred on
    `y` (axis="Y"); axis="Z" extrudes an XY polygon upward from z = y."""
    bm = bmesh.new()
    if axis == "Y":
        f = [bm.verts.new((x, y - depth / 2, z)) for x, z in poly]
        g = [bm.verts.new((x, y + depth / 2, z)) for x, z in poly]
    else:
        f = [bm.verts.new((x, yy, y)) for x, yy in poly]
        g = [bm.verts.new((x, yy, y + depth)) for x, yy in poly]
    bm.faces.new(f)
    bm.faces.new(list(reversed(g)))
    _bridge(bm, f, g)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(name, bm, m, smooth=smooth, parent=parent, bevel=bevel)


def hazard_band(x0, x1, z0, z1, y, stripe=0.12, slant=0.1, depth=0.02, parent=None, P=None):
    """Yellow/black warning stripes on a band facing -Y (at depth y)."""
    P = P or palette()
    parts = [cube((x1 - x0, depth, z1 - z0), ((x0 + x1) / 2, y + depth * 0.25, (z0 + z1) / 2), P.stripe_black, bevel=0)]
    x = x0 - slant
    while x < x1:
        poly = [(max(x0, min(x1, x)), z0), (max(x0, min(x1, x + stripe)), z0),
                (max(x0, min(x1, x + stripe + slant)), z1), (max(x0, min(x1, x + slant)), z1)]
        if poly[1][0] - poly[0][0] > 0.005 or poly[2][0] - poly[3][0] > 0.005:
            parts.append(prism(poly, depth, P.yellow, y=y))
        x += stripe * 2
    o = join(parts, "hazard_band")
    if parent is not None:
        hang(o, parent)
    return o


def text(s, size, loc, m, extrude=0.01, rot=(math.pi / 2, 0, 0), name="text", parent=None, res=2, align="CENTER"):
    """Extruded text converted to a mesh; stands up facing -Y by default."""
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object
    t.data.body = s
    t.data.size = size
    t.data.extrude = extrude
    t.data.align_x = align
    t.data.align_y = "CENTER"
    t.data.resolution_u = res
    t.data.font = bpy.data.fonts.load(FONT, check_existing=True)
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.name = name
    o.data.materials.clear()
    o.data.materials.append(common.mat(m))
    if parent is not None:
        attach(o, parent)
    return o


def ring_pts(c, r, n, plane="XY", a0=0.0, a1=TAU, endpoint=False):
    """Points on a circle (or an arc) around c in the XY, XZ or YZ plane."""
    out = []
    count = n + (1 if endpoint else 0)
    for i in range(count):
        a = a0 + (a1 - a0) * i / n
        ca, sa = math.cos(a) * r, math.sin(a) * r
        if plane == "XY":
            out.append((c[0] + ca, c[1] + sa, c[2]))
        elif plane == "XZ":
            out.append((c[0] + ca, c[1], c[2] + sa))
        else:
            out.append((c[0], c[1] + ca, c[2] + sa))
    return out


def hexbolt(loc, r, m, axis="-Y", h=None, parent=None, name="bolt", washer=True):
    """A hex bolt head (with a washer), its face looking along `axis`."""
    h = h or r * 0.6
    rot = {"-Y": (math.pi / 2, 0, 0), "Y": (-math.pi / 2, 0, 0), "Z": (0, 0, 0), "-Z": (math.pi, 0, 0),
           "X": (0, math.pi / 2, 0), "-X": (0, -math.pi / 2, 0)}[axis]
    d = {"-Y": (0, -1, 0), "Y": (0, 1, 0), "Z": (0, 0, 1), "-Z": (0, 0, -1), "X": (1, 0, 0), "-X": (-1, 0, 0)}[axis]
    loc = Vector(loc)
    head = cyl(r, h, tuple(loc + Vector(d) * h * 0.8), m, rot=rot, verts=6, bevel=0, smooth=False, parent=parent)
    if not washer:
        head.name = name
        return head
    washer = cyl(r * 1.35, h * 0.3, tuple(loc + Vector(d) * h * 0.15), m, rot=rot, verts=10, bevel=0, parent=parent)
    return join([head, washer], name)


# ------------------------------------------------------ animation helpers --
def osc(obj, clip, path, index, amp, seconds=2.0, cycles=1, phase=0.0, base=None, steps=8):
    """A seamless sine loop with `cycles` whole periods in `seconds`."""
    v0 = getattr(obj, path)[index] if base is None else base
    end = int(round(seconds * FPS))
    n = steps * cycles
    keys = [(end * s / n, v0 + amp * math.sin(TAU * cycles * s / n + phase)) for s in range(n + 1)]
    key(obj, clip, path, keys, index=index)


def blink(obj, clip, seconds=2.0, at=0.0, length=0.15, lo=0.35, hi=1.0, count=1, gap=0.25):
    """Scale an emissive part up for `length` s at `at` (optionally `count`
    times, `gap` s apart), small the rest of the loop: an LED blinking."""
    end = int(round(seconds * FPS))
    keys = [(0, (lo,) * 3)]
    for c in range(count):
        s = int(round((at + c * gap) * FPS)) % end
        e = min(s + max(1, int(round(length * FPS))), end - 1)
        if s <= keys[-1][0]:
            s = keys[-1][0] + 1
        keys += [(s, (lo,) * 3), (s + 1, (hi,) * 3), (e, (hi,) * 3), (e + 1, (lo,) * 3)]
    keys.append((end, (lo,) * 3))
    keys = sorted({k: v for k, v in keys}.items())
    key(obj, clip, "scale", keys, interp="LINEAR")
    obj.scale = (lo,) * 3


def palette():
    """Shared material presets (call inside a builder, after clean_scene)."""
    class P:
        pass
    p = P()
    p.navy = pbr("paint", (0.030, 0.034, 0.075), name="navy_paint")
    p.gun = pbr("paint", (0.055, 0.058, 0.070), name="gunmetal_paint")
    p.plum = pbr("paint", (0.16, 0.035, 0.20), name="plum_paint")
    p.steel = pbr("metal", (0.56, 0.58, 0.62), name="steel")
    p.dsteel = pbr("metal", (0.26, 0.27, 0.30), rough=0.42, name="dark_steel")
    p.chrome = pbr("chrome", (0.80, 0.82, 0.86), name="chrome")
    p.gold = pbr("gold", (0.95, 0.66, 0.24), name="gold")
    p.rubber = pbr("rubber", (0.022, 0.022, 0.026), name="rubber")
    p.black = pbr("plastic", (0.018, 0.018, 0.024), rough=0.3, name="black_plastic")
    p.yellow = pbr("paint", (0.85, 0.55, 0.02), wear=0.5, name="hazard_yellow")
    p.stripe_black = pbr("paint", (0.015, 0.015, 0.02), wear=0.3, name="hazard_black")
    p.glass = pbr("glass", (0.6, 0.8, 1.0), alpha=0.25, name="glass")
    return p


# ------------------------------------------------ legacy builders --
# Kept for models other specialists are replacing; no longer used by the
# hazard scripts below.
RUBBER = ((0.06, 0.06, 0.09), 0.9, 0.0)
DRONE_BODY = ((0.10, 0.11, 0.16), 0.4, 0.6)


def plasma_bullet():
    """A crackling plasma ball, 0.6 m across, centred."""
    sphere(0.22, (0, 0, 0), neon((1.0, 0.95, 0.7), 8.0, (0.9, 0.85, 0.6)), segments=12, rings=8)
    sphere(0.30, (0, 0, 0), neon((0.5, 0.3, 1.0), 4.0, (0.3, 0.15, 0.6)), scale=(1.0, 0.85, 1.0), segments=12, rings=8)
    for i in range(6):
        a = i / 6.0 * math.tau
        cone(0.06, 0.28, (math.cos(a) * 0.36, 0, math.sin(a) * 0.36), neon((0.6, 0.4, 1.0), 5.0), rot=(0, a + math.pi / 2, 0), verts=5)


def pedestal():
    """The pick-up pedestal ('pusher'): a heavy column 1.5 m wide, 1.5 m tall
    with a cyan tractor beam rising above it where the item floats."""
    cube((1.5, 1.2, 0.35), (0, 0, 0.18), METAL_DARK, bevel=0.06)
    cyl(0.5, 0.9, (0, 0, 0.8), METAL_STEEL, r2=0.42, verts=16)
    cyl(0.56, 0.16, (0, 0, 1.3), METAL_DARK, verts=16)
    torus(0.5, 0.04, (0, 0, 1.36), NEON_CYAN, major_segments=24)
    for i in range(4):
        a = i / 4.0 * math.tau
        cube((0.12, 0.05, 0.6), (math.cos(a) * 0.46, math.sin(a) * 0.46, 0.75), NEON_CYAN, rot=(0, 0, a), bevel=0.0)
    cyl(0.42, 1.3, (0, 0, 2.05), neon((0.3, 0.9, 1.0), 0.5, (0.05, 0.25, 0.3)), r2=0.3, verts=16, name="beam")


def shield_battery():
    """A glowing cyan energy cell, 0.8 m wide, 1.4 m tall, centred."""
    cyl(0.32, 1.1, (0, 0, 0), METAL_STEEL, verts=14)
    cyl(0.34, 0.5, (0, 0, 0), neon((0.2, 0.9, 1.0), 3.5, (0.05, 0.3, 0.4)), verts=14)
    for z in (-0.32, 0.32):
        torus(0.33, 0.04, (0, 0, z), METAL_DARK, major_segments=16)
    cyl(0.16, 0.18, (0, 0, 0.62), METAL_CHROME, verts=10)
    cube((0.2, 0.05, 0.05), (0, -0.36, 0.0), NEON_WHITE, bevel=0.0)
    cube((0.05, 0.05, 0.2), (0, -0.36, 0.0), NEON_WHITE, bevel=0.0)


def shield_core():
    """A hexagonal shield core token, 1 m wide, 1.2 m tall, centred."""
    cyl(0.6, 0.18, (0, 0, 0), METAL_CHROME, rot=(math.pi / 2, 0, 0), verts=6)
    cyl(0.5, 0.2, (0, 0, 0), neon((0.4, 0.5, 1.0), 2.5, (0.1, 0.12, 0.35)), rot=(math.pi / 2, 0, 0), verts=6)
    for s in (-1, 1):
        cyl(0.28, 0.04, (0, s * 0.12, 0), neon((0.8, 0.9, 1.0), 4.0, (0.5, 0.6, 0.7)), rot=(math.pi / 2, 0, 0), verts=6)
        torus(0.42, 0.03, (0, s * 0.11, 0), NEON_CYAN, rot=(math.pi / 2, 0, 0), major_segments=12)


def magnet():
    """A classic horseshoe magnet 1.2 m tall, poles pointing up, centred."""
    RED_M = ((0.85, 0.06, 0.08), 0.35, 0.2)
    arc = torus(0.4, 0.14, (0, 0, -0.15), RED_M, rot=(math.pi / 2, 0, 0), major_segments=24, minor_segments=10)
    bpy.ops.object.select_all(action="DESELECT")
    arc.select_set(True)
    bpy.context.view_layer.objects.active = arc
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, -0.15), plane_no=(0, 0, 1), clear_inner=True, use_fill=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for s in (-1, 1):
        cube((0.28, 0.28, 0.5), (s * 0.4, 0, 0.1), RED_M, bevel=0.03)
        cube((0.28, 0.28, 0.25), (s * 0.4, 0, 0.47), METAL_CHROME, bevel=0.03)
        cube((0.29, 0.29, 0.03), (s * 0.4, 0, 0.35), NEON_CYAN, bevel=0.0)
    for i in range(3):
        torus(0.15 + i * 0.12, 0.012, (0, 0, 0.75 + i * 0.05), neon((0.5, 0.9, 1.0), 2.5), rot=(0, 0, 0), major_segments=16, minor_segments=5)


def crate():
    """A supply crate 1.4 m wide, 1.2 m tall, centred, with a glowing cross."""
    cube((1.4, 1.0, 1.2), (0, 0, 0), ((0.45, 0.30, 0.10), 0.85, 0.0), bevel=0.04)
    for z in (-0.5, 0.5):
        cube((1.45, 1.05, 0.08), (0, 0, z), METAL_DARK, bevel=0.01)
    for x in (-0.6, 0.6):
        cube((0.08, 1.05, 1.25), (x, 0, 0), METAL_DARK, bevel=0.01)
    cube((0.5, 0.04, 0.16), (0, -0.52, 0), NEON_GREEN, bevel=0.0)
    cube((0.16, 0.04, 0.5), (0, -0.52, 0), NEON_GREEN, bevel=0.0)
    cube((0.7, 0.02, 0.7), (0, -0.51, 0), ((0.9, 0.9, 0.85), 0.8, 0.0), bevel=0.0)


def heart():
    """A glowing heart 1 m tall, centred."""
    HEART_M = neon((1.0, 0.15, 0.3), 4.0, (0.5, 0.05, 0.1))
    for s in (-1, 1):
        sphere(0.3, (s * 0.25, 0, 0.2), HEART_M, segments=12, rings=8)
    cone(0.5, 0.75, (0, 0, -0.2), HEART_M, rot=(math.pi, 0, 0), verts=12)
    sphere(0.08, (-0.3, -0.2, 0.35), NEON_WHITE, segments=6, rings=4)


def block():
    """A 1 m crystal block the boss's shots leave behind, centred."""
    cube((0.95, 0.95, 0.95), (0, 0, 0), neon((0.5, 0.2, 0.9), 1.0, (0.25, 0.1, 0.45)), bevel=0.12)
    cube((0.6, 0.6, 0.6), (0, 0, 0), neon((0.9, 0.5, 1.0), 3.0), rot=(0.6, 0.4, 0.3), bevel=0.05)


def slot_machine():
    """A one-armed bandit 1.6 m wide, 2.6 m tall: pull the 'lever' pivot
    (the game does it when something hits the machine) and the reels spin."""
    BODY = ((0.18, 0.05, 0.22), 0.4, 0.4)
    cube((1.5, 1.2, 2.0), (0, 0, 1.0), BODY, bevel=0.05)
    cube((1.5, 0.9, 0.6), (0, 0.1, 2.3), BODY, bevel=0.05)
    cube((1.3, 0.03, 0.4), (0, -0.46, 2.3), NEON_YELLOW, bevel=0.0, name="marquee")
    cube((1.2, 0.04, 0.6), (0, -0.62, 1.4), PLASTIC_BLACK, bevel=0.0)
    for j in range(3):
        r = pivot("reel_%d" % (j + 1), (-0.36 + j * 0.36, -0.55, 1.4))
        cyl(0.26, 0.3, (-0.36 + j * 0.36, -0.55, 1.4), (WHITE, 0.6, 0.0), rot=(0, math.pi / 2, 0), verts=12, parent=r)
        for k in range(4):
            a = k * math.pi / 2
            cube((0.2, 0.03, 0.14), (-0.36 + j * 0.36, -0.55 + math.cos(a) * 0.27, 1.4 + math.sin(a) * 0.27), [NEON_RED, NEON_YELLOW, NEON_GREEN, NEON_CYAN][(k + j) % 4], rot=(-a, 0, 0), bevel=0.0, parent=r)
    cube((1.3, 0.5, 0.1), (0, -0.4, 0.95), METAL_GOLD, bevel=0.02)
    cube((0.9, 0.2, 0.3), (0, -0.5, 0.45), PLASTIC_BLACK, bevel=0.02)            # coin tray
    lv = pivot("lever", (0.82, 0.2, 1.6))
    rod((0.82, 0.2, 1.6), (0.95, 0.2, 2.5), 0.04, METAL_CHROME, parent=lv)
    sphere(0.12, (0.95, 0.2, 2.55), ((0.85, 0.05, 0.05), 0.3, 0.0), segments=10, rings=8, parent=lv)
    for i in range(10):
        sphere(0.04, (-0.6 + i * 0.133, -0.47, 2.62), NEON_YELLOW if i % 2 else NEON_WHITE, segments=5, rings=4)
    cube((0.5, 0.03, 0.2), (0, -0.46, 0.7), NEON_RED, bevel=0.0)


def arcade_cabinet():
    """An arcade cabinet 1.4 m wide, 2.9 m tall with a glowing screen and
    marquee (the game animates the 'screen' material)."""
    BODY = ((0.10, 0.10, 0.35), 0.5, 0.2)
    cube((1.3, 1.2, 2.2), (0, 0, 1.1), BODY, bevel=0.04)
    cube((1.3, 0.7, 0.6), (0, 0.2, 2.5), BODY, bevel=0.04)
    cube((1.15, 0.03, 0.4), (0, -0.16, 2.5), NEON_PINK, bevel=0.0, name="marquee")
    cube((1.05, 0.04, 0.85), (0, -0.55, 1.75), SCREEN_CYAN, rot=(0.25, 0, 0), bevel=0.0, name="screen")
    cube((1.2, 0.5, 0.12), (0, -0.45, 1.25), PLASTIC_BLACK, bevel=0.02)
    for j in range(4):
        sphere(0.05, (-0.3 + j * 0.2, -0.5, 1.33), [NEON_RED, NEON_CYAN, NEON_YELLOW, NEON_GREEN][j], segments=6, rings=4)
    rod((0.45, -0.5, 1.3), (0.45, -0.55, 1.5), 0.02, METAL_CHROME, verts=5)
    sphere(0.05, (0.45, -0.55, 1.52), NEON_RED, segments=6, rings=4)
    cube((0.16, 0.02, 0.06), (-0.4, -0.61, 0.7), NEON_YELLOW, bevel=0.0)             # coin slot
    for s in (-1, 1):
        cube((0.05, 0.4, 2.2), (s * 0.66, -0.3, 1.1), NEON_CYAN if s > 0 else NEON_PINK, bevel=0.0)




# ================================================================ builders ==
def trampoline():
    """A 2 m round backyard trampoline, hotel-party edition: black woven mat
    with a printed pink/cyan target, 16 galvanised coil springs, a padded
    vinyl frame cover with a neon strip, W-shaped steel legs. The mat hangs
    on the 'mat' pivot at the rim; the one-shot `bounce` clip scales its sag
    (dip, rebound, settle). trampoline.gd plays it when it flings something."""
    P = palette()
    FR, FZ = 0.92, 0.572          # frame tube radius / height
    MR, MZ = 0.755, 0.60          # mat radius / rim height
    SAG = 0.035                   # resting sag at the centre
    frame_m = pbr("metal", (0.66, 0.68, 0.71), rough=0.3, name="galvanised")
    leg_m = pbr("paint", (0.035, 0.035, 0.06), name="leg_paint")
    spring_m = pbr("chrome", (0.72, 0.74, 0.78), rough=0.18, name="spring_steel")
    mat_m = pbr("fabric", (0.010, 0.010, 0.014), color2=(0.025, 0.025, 0.032), rough=0.62, grime=0.1, name="mat_weave")
    pink_m = pbr("fabric", (0.85, 0.07, 0.42), color2=(0.6, 0.04, 0.3), rough=0.62, grime=0.1, name="mat_print_pink")
    cyan_m = pbr("fabric", (0.04, 0.55, 0.72), color2=(0.02, 0.4, 0.55), rough=0.62, grime=0.1, name="mat_print_cyan")
    web_m = pbr("fabric", (0.10, 0.10, 0.12), name="webbing")
    pad_m = pbr("leather", (0.17, 0.04, 0.32), rough=0.32, name="pad_vinyl")
    pad_side = pbr("leather", (0.05, 0.02, 0.10), rough=0.4, name="pad_side")
    neon_m = pbr("neon", (0.05, 0.85, 0.95), strength=5.0, name="neon_cyan")

    # Frame ring and its leg sockets.
    torus(FR, 0.03, (0, 0, FZ), frame_m, major_segments=40, minor_segments=6)

    # Four W legs (two posts joined by a curved floor tube) at 45 degrees.
    for i in range(4):
        a = TAU * i / 4 + math.pi / 4
        d = 0.21
        def at(ang, r, z):
            return (math.cos(ang) * r, math.sin(ang) * r, z)
        pts = [at(a - d, FR, FZ - 0.01), at(a - d, FR, 0.16), at(a - d * 0.93, FR - 0.01, 0.07),
               at(a - d * 0.7, FR - 0.03, 0.035), at(a, FR - 0.05, 0.03), at(a + d * 0.7, FR - 0.03, 0.035),
               at(a + d * 0.93, FR - 0.01, 0.07), at(a + d, FR, 0.16), at(a + d, FR, FZ - 0.01)]
        sweep(pts, 0.024, leg_m, prof=6, name="leg")
        for s in (-1, 1):
            cyl(0.034, 0.09, at(a + s * d, FR, FZ - 0.04), frame_m, verts=8, bevel=0)      # T socket
            cyl(0.045, 0.025, at(a + s * d * 0.62, FR - 0.035, 0.0125), P.rubber, verts=8, bevel=0)  # foot pad

    # Padded frame cover: eight vinyl sections with seams, a neon strip.
    pad_prof = [(0.845, 0.593), (0.835, 0.612), (0.85, 0.636), (0.90, 0.646), (0.98, 0.643), (1.012, 0.628), (1.015, 0.598), (0.99, 0.586)]
    gap = math.radians(1.2)
    for i in range(8):
        a0 = TAU * i / 8 + gap
        a1 = TAU * (i + 1) / 8 - gap
        lathe(pad_prof, pad_m, segs=5, arc=(a0, a1), name="pad", band_mats=[1, 0, 0, 0, 0, 1, 1], mats=(pad_side,))
    torus(1.017, 0.011, (0, 0, 0.613), neon_m, major_segments=48, minor_segments=4)

    # Springs from the mat's edge rings out to the frame.
    for i in range(16):
        a = TAU * (i + 0.5) / 16
        c, s = math.cos(a), math.sin(a)
        coil((c * (MR + 0.012), s * (MR + 0.012), MZ - 0.004), (c * (FR - 0.022), s * (FR - 0.022), FZ + 0.012),
             0.019, 0.0065, 4.5, spring_m, spt=5, prof=3)
    # Stitched webbing hem around the mat (fixed: only the middle sags).
    torus(MR, 0.013, (0, 0, MZ), web_m, major_segments=40, minor_segments=4, scale=(1, 1, 0.6))

    # The mat: a shallow bowl with a printed target, on the 'mat' pivot at
    # rim height so scaling the pivot on Z deepens (or inverts) the sag.
    mp = piv("mat", (0, 0, MZ))
    rings = [(0.0, 1), (0.055, 0), (0.16, 1), (0.205, 0), (0.25, 0), (0.43, 2), (0.465, 0), (0.62, 0), (0.715, 0), (MR, 0)]
    segs = 32
    bm = bmesh.new()
    verts = []
    for r, _ in rings:
        z = MZ - SAG * (1.0 - (r / MR) ** 2)
        if r == 0.0:
            v = bm.verts.new((0, 0, z))
            verts.append([v] * segs)
        else:
            verts.append([bm.verts.new((math.cos(TAU * j / segs) * r, math.sin(TAU * j / segs) * r, z)) for j in range(segs)])
    for k in range(len(rings) - 1):
        # each entry's print colour runs out to the next radius
        _bridge(bm, verts[k], verts[k + 1], mat=rings[k][1])
    # (single surface: materials are double-sided, so the print shows from
    # both sides and the inverted rebound pose still reads)
    bm.normal_update()
    top = _obj("mat_surface", bm, mat_m, smooth=True, angle=80, mats=(pink_m, cyan_m))
    # Faces point where they were built (top up, underside down).
    hang(top, mp)
    key(mp, "bounce", "scale", [(0, (1, 1, 1)), (3, (1, 1, 5.2)), (6, (1, 1, 4.0)), (9, (1, 1, -1.3)),
                                 (13, (1, 1, 2.4)), (17, (1, 1, 0.4)), (21, (1, 1, 1.3)), (25, (1, 1, 1))])


def wall_gun():
    """A wall-mounted security turret. The armoured bracket hugs the wall at
    x = 0; the 'gun' pivot (x = 0.7, z = 1.0) is aimed by wall_gun.gd and
    carries the gun body, a sensor pod and the 'barrel' pivot (cooling fins,
    barrel, muzzle brake, 'flare'). Clips: `fire` (recoil kick + muzzle
    flare, played on every shot) and `idle` (sensor nod, status LEDs)."""
    P = palette()
    body_m = pbr("paint", (0.035, 0.04, 0.085), name="turret_paint")
    panel_m = pbr("paint", (0.20, 0.04, 0.24), name="turret_plum")
    fin_m = pbr("metal", (0.78, 0.80, 0.84), rough=0.22, name="fin_alu")
    barrel_m = pbr("metal", (0.14, 0.14, 0.16), rough=0.35, name="gun_steel")
    red = pbr("neon", (1.0, 0.08, 0.12), strength=6.0, name="led_red")
    amber = pbr("neon", (1.0, 0.45, 0.05), strength=5.0, name="led_amber")
    mag = pbr("neon", (1.0, 0.15, 0.75), strength=5.0, name="neon_magenta")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=3.0, name="neon_cyan")
    flare_m = pbr("neon", (1.0, 0.55, 0.95), strength=12.0, name="flare")
    GX, GZ = 0.7, 1.0

    # --- wall bracket (static) ---------------------------------------------
    rbox((0.1, 1.3, 1.9), (0.05, 0, 1.0), P.gun, r=0.035)                     # wall plate
    for z in (0.2, 1.8):
        for y in (-0.5, 0.5):
            hexbolt((0.1, y, z), 0.045, P.chrome, axis="X")
    prism([(0.08, 0.28), (0.26, 0.28), (0.46, 0.52), (0.46, 1.48), (0.26, 1.72), (0.08, 1.72)], 1.05, body_m, bevel=0.03)
    # side panels facing the camera (and the back), hazard band, vents
    for s in (-1, 1):
        prism([(0.12, 0.38), (0.25, 0.38), (0.40, 0.58), (0.40, 1.42), (0.25, 1.62), (0.12, 1.62)], 0.02, panel_m, y=s * 0.53, bevel=0.006)
        for k in range(5):
            rbox((0.13, 0.02, 0.025), (0.27, s * 0.545, 0.72 + k * 0.06), P.black, r=0.006)
        for k in range(4):
            cube((0.07, 0.02, 0.1), (0.155 + k * 0.08, s * 0.55, 0.47), P.yellow if k % 2 == 0 else P.stripe_black, rot=(0, 0.6, 0), bevel=0)
    # yoke arms carrying the trunnion
    for s in (-1, 1):
        prism([(0.35, 0.72), (0.62, 0.74), (0.86, 0.86), (0.9, 1.0), (0.86, 1.14), (0.62, 1.26), (0.35, 1.28)], 0.1, P.gun, y=s * 0.47, bevel=0.02)
        cyl(0.13, 0.05, (GX, s * 0.53, GZ), P.chrome, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.01)
        cyl(0.06, 0.06, (GX, s * 0.565, GZ), P.dsteel, rot=(math.pi / 2, 0, 0), verts=6, bevel=0, smooth=False)
    # status LEDs (blink in idle) and an amber strip
    for k in range(3):
        p = piv("led_%d" % (k + 1), (0.3, -0.56, 1.3 + k * 0.08))
        sphere(0.022, (0.3, -0.56, 1.3 + k * 0.08), red if k == 0 else amber, segments=8, rings=5, parent=p)
        blink(p, "idle", seconds=2.0, at=0.2 + k * 0.5, length=0.25, lo=0.5, hi=1.25)
    cube((0.02, 0.03, 0.8), (0.465, -0.3, 1.0), amber, bevel=0)
    # cables from the bracket down into the wall, with a gland
    for k, (m, y) in enumerate(((P.rubber, -0.18), (pbr("rubber", (0.35, 0.12, 0.02), name="orange_cable"), 0.02), (P.rubber, 0.2))):
        sweep([(0.2, y, 0.3), (0.19, y, 0.2), (0.13, y, 0.1), (0.05, y, 0.06 + k * 0.03), (0.0, y, 0.06 + k * 0.03)], 0.03, m, prof=6)
        cyl(0.045, 0.05, (0.025, y, 0.06 + k * 0.03), P.dsteel, rot=(0, math.pi / 2, 0), verts=8, bevel=0)

    # --- the gun (aimed in code) --------------------------------------------
    g = piv("gun", (GX, 0, GZ))
    parts = []
    parts.append(cyl(0.27, 0.8, (GX, 0, GZ), body_m, rot=(math.pi / 2, 0, 0), verts=20, bevel=0.02))     # drum
    shell = [(0.72, -0.2), (1.8, -0.24), (2.06, -0.13), (2.06, 0.13), (1.86, 0.25), (1.05, 0.29), (0.8, 0.2)]   # (x, dz)
    parts.append(prism([(x, GZ + z) for x, z in shell], 0.56, body_m, bevel=0.035))
    for s in (-1, 1):   # side armour plates with plum inlay and a neon slit
        parts.append(prism([(0.95, GZ - 0.17), (1.75, GZ - 0.19), (1.92, GZ - 0.1), (1.92, GZ + 0.1), (1.78, GZ + 0.19), (1.1, GZ + 0.22)], 0.03, panel_m, y=s * 0.29, bevel=0.008))
        parts.append(cube((0.6, 0.012, 0.035), (1.42, s * 0.31, GZ + 0.03), mag, bevel=0))
        for k in range(3):
            parts.append(hexbolt((1.0 + k * 0.38, s * 0.305, GZ - 0.12), 0.022, P.chrome, axis="-Y" if s < 0 else "Y"))
    # energy cell under the body with a cyan window
    parts.append(cyl(0.1, 0.55, (1.3, 0, GZ - 0.32), P.dsteel, rot=(0, math.pi / 2, 0), verts=12, bevel=0.01))
    parts.append(cube((0.36, 0.2, 0.04), (1.3, -0.02, GZ - 0.32), cyan, bevel=0))
    for x in (1.06, 1.54):
        parts.append(cyl(0.115, 0.04, (x, 0, GZ - 0.32), P.chrome, rot=(0, math.pi / 2, 0), verts=12, bevel=0))
    # hose from the cell into the drum
    parts.append(sweep([(1.02, 0.0, GZ - 0.34), (0.86, 0.05, GZ - 0.36), (0.74, 0.1, GZ - 0.24)], 0.03, P.rubber, prof=6))
    for o in parts:
        hang(o, g)
    merge_under(g, "gun_body")

    # sensor pod on top: nods while idling
    sp = piv("sensor", (1.3, 0, GZ + 0.3), parent=g)
    rbox((0.4, 0.28, 0.15), (1.32, 0, GZ + 0.37), P.gun, r=0.045, parent=sp)
    sphere(0.09, (1.52, 0, GZ + 0.37), P.black, scale=(0.6, 1, 1), segments=12, rings=8, parent=sp)
    sphere(0.062, (1.555, 0, GZ + 0.37), red, scale=(0.5, 1, 1), segments=10, rings=6, parent=sp)
    cube((0.24, 0.012, 0.035), (1.3, -0.145, GZ + 0.38), red, bevel=0, parent=sp)
    merge_under(sp, "sensor_pod")
    osc(sp, "idle", "rotation_euler", 1, 0.12, seconds=2.0)

    # barrel assembly on its own pivot for the recoil kick
    b = piv("barrel", (GX, 0, GZ), parent=g)
    bparts = [cyl(0.085, 1.5, (2.55, 0, GZ), barrel_m, rot=(0, math.pi / 2, 0), verts=14, bevel=0.01)]
    for k in range(7):
        bparts.append(cube((0.035, 0.38, 0.38), (2.12 + k * 0.1, 0, GZ), fin_m, bevel=0))
    bparts.append(cyl(0.13, 0.08, (2.02, 0, GZ), P.chrome, rot=(0, math.pi / 2, 0), verts=16, bevel=0.01))
    bparts.append(cyl(0.135, 0.24, (3.36, 0, GZ), P.gun, rot=(0, math.pi / 2, 0), verts=12, bevel=0.015))    # muzzle brake
    for s in (-1, 1):
        bparts.append(cube((0.13, 0.03, 0.07), (3.36, s * 0.13, GZ), P.black, bevel=0))
    bparts.append(torus(0.1, 0.018, (3.49, 0, GZ), mag, rot=(0, math.pi / 2, 0), major_segments=14, minor_segments=4))
    for o in bparts:
        hang(o, b)
    merge_under(b, "barrel_mesh")
    f = piv("flare", (3.52, 0, GZ), parent=b)
    fl = [cone(0.12, 0.7, (3.87, 0, GZ), flare_m, rot=(0, math.pi / 2, 0), verts=6, bevel=0)]
    for k in range(4):
        a = k * math.pi / 2 + math.pi / 4
        fl.append(rod((3.55, 0, GZ), (3.62, math.cos(a) * 0.3, GZ + math.sin(a) * 0.3), 0.05, flare_m, r2=0.0, verts=4))
    fl.append(sphere(0.13, (3.56, 0, GZ), flare_m, segments=8, rings=6))
    for o in fl:
        hang(o, f)
    fm = merge_under(f, "flare_mesh")
    # Hidden at rest: the mesh itself is shrunk 100x round the pivot (a glTF
    # node's rest scale is not reliably the keyed one), the clip scales the
    # pivot up to show it.
    bpy.context.view_layer.update()
    to_piv = fm.matrix_world.inverted() @ f.matrix_world
    fm.data.transform(to_piv.inverted())
    fm.data.transform(Matrix.Scale(0.01, 4))
    fm.data.transform(to_piv)
    key(f, "fire", "scale", [(0, (1,) * 3), (1, (130, 110, 110)), (3, (90, 125, 125)), (5, (50, 60, 60)), (7, (1,) * 3), (12, (1,) * 3)], interp="LINEAR")
    x0 = b.location.x
    key(b, "fire", "location", [(0, (x0, 0, 0)), (1, (x0 - 0.24, 0, 0)), (3, (x0 - 0.2, 0, 0)), (9, (x0 + 0.02, 0, 0)), (12, (x0, 0, 0))])


def _prop_blade(ax, ay, z, a, m, length=0.34, parent=None):
    """One tapered, twisted propeller blade from the hub outwards at angle a."""
    bm = bmesh.new()
    rows = []
    n = 5
    for i in range(n + 1):
        t = i / n
        r = 0.03 + length * t
        chord = 0.085 * (1 - t) + 0.035 * t + 0.03 * math.sin(math.pi * t)
        pitch = math.radians(24 * (1 - t) + 9 * t)
        ca, sa = math.cos(a), math.sin(a)
        ta, tb = -sa, ca                     # chord direction (tangential)
        row = []
        for u, th in ((-0.5, 0.0), (0.0, 0.006), (0.5, 0.0)):
            cx = u * chord * math.cos(pitch)
            cz = u * chord * math.sin(pitch) + th
            row.append(bm.verts.new((ax + ca * r + ta * cx, ay + sa * r + tb * cx, z + cz)))
        rows.append(row)
    for k in range(n):
        A, B = rows[k], rows[k + 1]
        bm.faces.new((A[0], A[1], B[1], B[0]))
        bm.faces.new((A[1], A[2], B[2], B[1]))
    return _obj("blade", bm, m, smooth=True, angle=70, parent=parent)


def drone():
    """A sleek security quadcopter, ~2.4 m across, centred, nose towards -X
    (drone.gd mirrors the model to fly right). Pearl shell over a carbon
    belly, carbon arms, motor bells with two-blade props on 'rotor_1..4'
    (spun in code, never keyed), prop guards, skids, a gimballed camera pod
    ('gimbal', 'cam_tilt') and blinking nav lights ('nav_*', 'beacon') in
    `idle`."""
    P = palette()
    shell = pbr("plastic", (0.72, 0.74, 0.8), rough=0.22, wear=0.15, name="pearl_shell")
    carbon = pbr("plastic", (0.05, 0.055, 0.11), rough=0.32, bump=0.5, scale=0.2, name="carbon")
    trim = pbr("paint", (0.20, 0.04, 0.26), name="drone_plum")
    visor = pbr("plastic", (0.01, 0.012, 0.02), rough=0.05, wear=0.0, grime=0.05, name="visor_black")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=4.0, name="neon_cyan")
    mag = pbr("neon", (1.0, 0.1, 0.7), strength=4.0, name="neon_magenta")
    red = pbr("neon", (1.0, 0.06, 0.08), strength=7.0, name="nav_red")
    green = pbr("neon", (0.1, 1.0, 0.3), strength=6.0, name="nav_green")
    white = pbr("neon", (1.0, 0.95, 0.9), strength=8.0, name="nav_white")
    prop_m = pbr("plastic", (0.03, 0.03, 0.04), rough=0.3, name="prop")

    # Hull: a lofted, rounded-box fuselage; pearl on top, carbon below, a
    # dark glossy visor over the nose, a cyan seam light round the waist.
    secs = [(-0.66, 0.0, 0.0, 0.02), (-0.62, 0.1, 0.07, 0.025), (-0.52, 0.22, 0.13, 0.035), (-0.36, 0.31, 0.18, 0.04),
            (-0.12, 0.35, 0.2, 0.04), (0.14, 0.33, 0.18, 0.035), (0.38, 0.25, 0.13, 0.04), (0.55, 0.14, 0.08, 0.05),
            (0.61, 0.0, 0.0, 0.055)]
    rings = []
    for x, w, h, zc in secs:
        rings.append([(x, 0, zc)] if w == 0 else superellipse(x, zc, w, h, n=2.4, count=20))

    def hull_mat(c):
        if c.z < -0.03:
            return 1
        if c.x < -0.3 and c.z > 0.07:
            return 2
        return 0
    loft(rings, shell, name="hull", mats=(carbon, visor), mat_fn=hull_mat, angle=70)
    seam_r = [(x, w * 1.02, zc) for x, w, h, zc in secs[1:-1]]
    seam = seam_r + [(x, -y, z) for x, y, z in reversed(seam_r)]
    sweep(seam, 0.012, cyan, prof=4, closed=True)
    # Top spine and a sensor bump.
    sphere(0.12, (-0.05, 0, 0.22), trim, scale=(2.2, 0.8, 0.45), segments=14, rings=7)
    cube((0.42, 0.012, 0.012), (-0.05, -0.098, 0.235), mag, bevel=0)
    cube((0.42, 0.012, 0.012), (-0.05, 0.098, 0.235), mag, bevel=0)
    # Tail: antenna and a heat vent.
    rod((0.46, 0, 0.12), (0.62, 0, 0.36), 0.012, P.dsteel, verts=6)
    sphere(0.022, (0.62, 0, 0.36), P.black, segments=6, rings=4)
    for k in range(4):
        rbox((0.02, 0.2, 0.012), (0.36 + k * 0.035, 0, 0.16 - k * 0.012), P.black, r=0.004)
    p = piv("beacon", (0.2, 0, 0.2))
    sphere(0.03, (0.2, 0, 0.2), white, segments=8, rings=5, parent=p)
    blink(p, "idle", seconds=2.0, at=0.0, length=0.07, lo=0.4, hi=1.5, count=2, gap=0.2)

    # Arms, motors, props (rotor pivots), guards, nav lights.
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
        ax, ay = sx * 0.86, sy * 0.56
        root = (sx * 0.34, sy * 0.2, 0.0)
        mid = (sx * 0.6, sy * 0.39, 0.05)
        tip = (ax, ay, 0.08)
        sweep([root, mid, tip], [0.055, 0.042, 0.036], carbon, prof=6, squash=0.6)
        # motor mount and bell
        cyl(0.075, 0.03, (ax, ay, 0.085), P.gun, verts=12, bevel=0)
        lathe([(0.0, 0.1), (0.085, 0.1), (0.09, 0.13), (0.088, 0.17), (0.07, 0.19), (0.0, 0.195)], P.chrome, loc=(ax, ay, 0), segs=14)
        torus(0.089, 0.008, (ax, ay, 0.14), mag if i % 2 else cyan, major_segments=14, minor_segments=3)
        # rotor: hub, two blades, spinner, blur disc
        r = piv("rotor_%d" % (i + 1), (ax, ay, 0.21))
        cyl(0.03, 0.05, (ax, ay, 0.21), P.dsteel, verts=8, bevel=0, parent=r)
        for k in range(2):
            _prop_blade(ax, ay, 0.225, k * math.pi + (0.3 if i % 2 else -0.3), prop_m, parent=r)
        lathe([(0.03, 0.235), (0.025, 0.25), (0.0, 0.262)], P.chrome, loc=(ax, ay, 0), segs=8, parent=r)
        merge_under(r, "rotor_%d_mesh" % (i + 1))
        # prop guard: a slim ring with two struts
        torus(0.4, 0.014, (ax, ay, 0.2), trim, major_segments=28, minor_segments=4, scale=(1, 1, 1.6))
        for k in (0.9, 2.4):
            ga = math.atan2(ay, ax) + (k - 1.65) * 0.9 + math.pi
            rod((ax + math.cos(ga) * 0.09, ay + math.sin(ga) * 0.09, 0.1), (ax + math.cos(ga) * 0.39, ay + math.sin(ga) * 0.39, 0.2), 0.011, trim, verts=5)
        # nav light under each arm tip: red port, green starboard
        n = piv("nav_%d" % (i + 1), (ax, ay, 0.02))
        sphere(0.034, (ax, ay, 0.04), red if sy < 0 else green, segments=8, rings=5, parent=n)
        blink(n, "idle", seconds=2.0, at=0.9 + 0.08 * i, length=0.3, lo=0.55, hi=1.35)

    # Landing skids.
    for sy in (-1, 1):
        sweep([(-0.3, sy * 0.2, -0.12), (-0.34, sy * 0.3, -0.36), (-0.36, sy * 0.33, -0.5)], 0.02, P.dsteel, prof=6)
        sweep([(0.3, sy * 0.2, -0.12), (0.34, sy * 0.3, -0.36), (0.36, sy * 0.33, -0.5)], 0.02, P.dsteel, prof=6)
        sweep([(-0.5, sy * 0.33, -0.47), (-0.42, sy * 0.33, -0.52), (0.42, sy * 0.33, -0.52), (0.5, sy * 0.33, -0.47)], 0.026, P.rubber, prof=6)

    # Gimballed camera pod under the nose: yaw on 'gimbal', pitch on 'cam_tilt'.
    GX, GZ = -0.4, -0.2
    cyl(0.07, 0.08, (GX, 0, -0.1), P.gun, verts=12, bevel=0)
    gb = piv("gimbal", (GX, 0, GZ))
    cyl(0.1, 0.03, (GX, 0, GZ + 0.015), P.gun, verts=12, bevel=0, parent=gb)
    for sy in (-1, 1):
        sweep([(GX, sy * 0.08, GZ), (GX, sy * 0.14, GZ - 0.05), (GX, sy * 0.14, GZ - 0.12), (GX, sy * 0.12, GZ - 0.14)], 0.02, P.gun, prof=5, parent=gb)
    merge_under(gb, "gimbal_yoke")
    CZ = GZ - 0.13
    ct = piv("cam_tilt", (GX, 0, CZ), parent=gb)
    sphere(0.105, (GX, 0, CZ), shell, segments=16, rings=10, parent=ct)
    d = Vector((-0.55, -0.8, -0.25)).normalized()
    rot = d.to_track_quat("Z", "Y").to_euler()
    base = Vector((GX, 0, CZ)) + d * 0.06
    lathe([(0.0, 0.0), (0.075, 0.0), (0.078, 0.05), (0.064, 0.07), (0.0, 0.066)], P.black, loc=tuple(base), rot=rot, segs=14, parent=ct)
    sphere(0.048, tuple(base + d * 0.068), red, scale=(1, 1, 1), segments=12, rings=6, parent=ct)
    merge_under(ct, "camera_pod")
    osc(gb, "idle", "rotation_euler", 2, 0.45, seconds=2.0)
    osc(ct, "idle", "rotation_euler", 1, 0.2, seconds=2.0, phase=1.3)


def light_ring():
    """A laser emitter ring on a plinth, 2.6 m wide, 3.85 m tall. The ring
    (centre z = 2.35) sits in a cradle; its inner light tube and front lip
    are the mesh 'glow' (light_ring.gd raises its emission as it charges).
    The emitter head at the ring's left fires the game's beam along -X from
    x = -1.8. `idle` slowly turns the front detail ring ('spin_detail',
    12-fold, so 1/12 turn per loop is seamless) and blinks status LEDs."""
    P = palette()
    RZ = 2.35
    ring_m = pbr("paint", (0.035, 0.04, 0.085), name="ring_paint")
    inner_m = pbr("metal", (0.62, 0.64, 0.68), rough=0.25, name="ring_inner")
    face_m = pbr("metal", (0.14, 0.14, 0.17), rough=0.35, name="ring_face")
    plate_m = pbr("paint", (0.18, 0.04, 0.24), name="ring_plum")
    glow_m = pbr("neon", (0.6, 0.3, 1.0), strength=1.0, name="ring_glow")
    pink = pbr("neon", (1.0, 0.25, 0.6), strength=6.0, name="lens_pink")
    amber = pbr("neon", (1.0, 0.45, 0.05), strength=5.0, name="led_amber")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=4.0, name="neon_cyan")

    # --- plinth ---------------------------------------------------------------
    rbox((2.6, 1.5, 0.2), (0, 0, 0.12), P.gun, r=0.04)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.1, 0.04, (sx * 1.15, sy * 0.6, 0.02), P.rubber, verts=10, bevel=0)
    hazard_band(-1.2, 1.2, 0.05, 0.19, -0.755, stripe=0.1, slant=0.1, P=P)
    prism([(-1.1, 0.22), (1.1, 0.22), (1.1, 0.56), (0.95, 0.66), (-0.95, 0.66), (-1.1, 0.56)], 1.15, ring_m, bevel=0.03)
    rbox((1.3, 0.03, 0.26), (0.0, -0.585, 0.43), P.black, r=0.02)                 # display bezel
    cube((1.16, 0.02, 0.17), (0.0, -0.6, 0.43), anim(((0.02, 0.1, 0.12), 0.3, 0.0, (1.0, 0.25, 0.6), 1.6), "screen"), bevel=0)
    for sx in (-1, 1):
        for k in range(4):
            rbox((0.03, 0.02, 0.2), (sx * (0.8 + k * 0.06), -0.585, 0.43), P.black, r=0.008)   # vents
    for k in range(3):
        p = piv("led_%d" % (k + 1), (-0.95 + k * 0.08, -0.59, 0.6))
        sphere(0.02, (-0.95 + k * 0.08, -0.59, 0.6), amber if k else pbr("neon", (0.1, 1.0, 0.3), strength=5, name="led_green"), segments=8, rings=5, parent=p)
        blink(p, "idle", seconds=4.0, at=0.3 + k * 0.4, length=0.3, lo=0.5, hi=1.3, count=3, gap=1.3)
    cube((2.0, 0.02, 0.02), (0, -0.585, 0.24), cyan, bevel=0)

    # --- cradle and struts ------------------------------------------------------
    CR = 1.6
    arc = ring_pts((0, 0, RZ), CR, 12, plane="XZ", a0=math.radians(-150), a1=math.radians(-30), endpoint=True)
    sweep(arc, 0.1, P.gun, prof=8, squash=1.8, name="cradle")
    for a in (-150, -30):
        x, z = math.cos(math.radians(a)) * CR, RZ + math.sin(math.radians(a)) * CR
        sweep([(x, 0, z), (x * 0.92, 0, (z + 0.66) / 2), (x * 0.85, 0, 0.62)], 0.11, P.gun, prof=8, squash=1.6)
        cyl(0.2, 0.08, (x * 0.85, 0, 0.66), P.dsteel, verts=12, bevel=0.01)
    for a in (-130, -90, -50):
        ca, sa = math.cos(math.radians(a)), math.sin(math.radians(a))
        for y in (-0.19, 0.19):
            rod((ca * 1.43, y, RZ + sa * 1.43), (ca * CR, y, RZ + sa * CR), 0.035, P.chrome, verts=8)

    # --- the ring -----------------------------------------------------------------
    prof = [(1.16, -0.12), (1.18, -0.16), (1.42, -0.16), (1.445, -0.12), (1.445, 0.12), (1.42, 0.16), (1.18, 0.16), (1.16, 0.12), (1.16, -0.12)]
    lathe(prof, ring_m, loc=(0, 0, RZ), rot=(math.pi / 2, 0, 0), segs=40, name="ring_body", cap=False,
          band_mats=[2, 1, 2, 0, 2, 1, 2, 1], mats=(face_m, inner_m), angle=35)
    # back-face bolts
    for i in range(16):
        a = TAU * i / 16
        cyl(0.025, 0.02, (math.cos(a) * 1.3, 0.17, RZ + math.sin(a) * 1.3), P.chrome, rot=(math.pi / 2, 0, 0), verts=6, bevel=0, smooth=False)
    # light tube and front lip: the 'glow' mesh
    g1 = torus(1.165, 0.04, (0, 0, RZ), glow_m, rot=(math.pi / 2, 0, 0), major_segments=40, minor_segments=5)
    g2 = torus(1.215, 0.016, (0, -0.165, RZ), glow_m, rot=(math.pi / 2, 0, 0), major_segments=40, minor_segments=3)
    join([g1, g2], "glow")

    # front detail ring: turns slowly
    sd = piv("spin_detail", (0, 0, RZ))
    for i in range(12):
        a = TAU * i / 12
        ca, sa = math.cos(a), math.sin(a)
        plate = prism([(-0.1, 1.25), (0.1, 1.25), (0.075, 1.4), (-0.075, 1.4)], 0.035, plate_m, bevel=0, axis="Z", y=0)
        # prism(axis="Z") builds in XY; lay it on the front face radially
        plate.rotation_euler = (math.pi / 2, 0, 0)
        plate.location = (0, -0.16, RZ)
        bpy.context.view_layer.update()
        plate.data.transform(Matrix.Rotation(a - math.pi / 2, 4, "Z"))
        hang(plate, sd)
        sphere(0.022, (ca * 1.36, -0.2, RZ + sa * 1.36), pink if i % 3 == 0 else cyan, segments=6, rings=4, parent=sd)
    merge_under(sd, "detail_ring")
    spin(sd, "idle", "Y", seconds=4.0, turns=-1.0 / 12)

    # --- emitter head at the left -----------------------------------------------
    rbox((0.3, 0.5, 0.56), (-1.47, 0, RZ), P.gun, r=0.05)                          # clamp block
    cyl(0.24, 0.26, (-1.6, 0, RZ), ring_m, rot=(0, math.pi / 2, 0), verts=16, bevel=0.02)
    for k in range(3):
        cyl(0.265, 0.03, (-1.52 - k * 0.07, 0, RZ), inner_m, rot=(0, math.pi / 2, 0), verts=16, bevel=0)
    lathe([(0.0, 0.0), (0.24, 0.0), (0.24, 0.03), (0.2, 0.08), (0.15, 0.1), (0.0, 0.1)], P.chrome, loc=(-1.72, 0, RZ), rot=(0, -math.pi / 2, 0), segs=16)
    sphere(0.12, (-1.8, 0, RZ), pink, scale=(0.45, 1, 1), segments=14, rings=8)
    sphere(0.14, (-1.8, 0, RZ), P.glass, scale=(0.5, 1, 1), segments=14, rings=8)
    torus(0.15, 0.012, (-1.83, 0, RZ), pink, rot=(0, math.pi / 2, 0), major_segments=14, minor_segments=3)

    # --- cables from the plinth up the back to the ring ---------------------------
    for k, m in enumerate((P.rubber, pbr("rubber", (0.35, 0.12, 0.02), name="orange_cable"), P.rubber)):
        x = 0.35 + k * 0.12
        sweep([(x, 0.45, 0.62), (x + 0.1, 0.5, 0.85), (x + 0.12, 0.34, 1.02), (x + 0.1, 0.22, 1.1)], 0.03, m, prof=6)


def button():
    """A big industrial floor push button, 1.9 x 1.3 m: bolted tread-plate
    base, a steel collar with a yellow/black warning ring and amber LEDs,
    and a glossy red mushroom cap on the 'top' pivot (button.gd pushes it
    down 0.15 m). `idle` chases the collar LEDs."""
    P = palette()
    base_m = pbr("paint", (0.05, 0.055, 0.075), name="button_base")
    tread = pbr("metal", (0.42, 0.44, 0.48), rough=0.38, name="tread_plate")
    red = pbr("plastic", (0.62, 0.02, 0.03), rough=0.14, wear=0.1, name="cap_red")
    red_glow = pbr("neon", (1.0, 0.12, 0.15), strength=3.5, name="cap_glow")
    amber = pbr("neon", (1.0, 0.45, 0.05), strength=5.0, name="led_amber")
    white = pbr("neon", (1.0, 0.95, 0.9), strength=3.0, name="label_white")

    # base: a chamfered slab with a tread-plate top and six hex bolts
    prism([(-0.95, 0.0), (0.95, 0.0), (0.95, 0.08), (0.9, 0.14), (-0.9, 0.14), (-0.95, 0.08)], 1.3, base_m, bevel=0.02)
    rbox((1.7, 1.12, 0.02), (0, 0, 0.145), tread, r=0.008)
    for x in (-0.6, -0.3, 0.3, 0.6):
        for y in (-0.4, -0.2, 0.2, 0.4):
            if abs(x) > 0.5 or abs(y) > 0.3:
                cube((0.1, 0.022, 0.008), (x, y, 0.158), tread, rot=(0, 0, 0.785 if (x > 0) == (y > 0) else -0.785), bevel=0)
    for x in (-0.8, 0.8):
        for y in (-0.48, 0.48):
            hexbolt((x, y, 0.155), 0.04, P.chrome, axis="Z")
    hexbolt((0, -0.52, 0.155), 0.035, P.chrome, axis="Z")
    hexbolt((0, 0.52, 0.155), 0.035, P.chrome, axis="Z")
    # front label plate
    rbox((0.52, 0.02, 0.07), (0, -0.655, 0.075), P.black, r=0.01)
    text("PUSH", 0.055, (0, -0.668, 0.075), white, extrude=0.004, name="label")

    # collar: steel ring with a sloped warning-striped face
    col = lathe([(0.72, 0.15), (0.72, 0.2), (0.68, 0.24), (0.58, 0.33), (0.56, 0.35), (0.51, 0.35), (0.51, 0.2)], P.steel,
                segs=48, cap=False, band_mats=[0, 0, 3, 0, 0, 0], mats=(P.yellow, P.stripe_black, P.black), name="collar")
    for poly in col.data.polygons:                  # the sloped band: 16 yellow/black blocks
        if poly.material_index == 3:
            a = math.atan2(poly.center.y, poly.center.x)
            poly.material_index = 1 if int((a + math.pi) / TAU * 16) % 2 == 0 else 2
    torus(0.72, 0.018, (0, 0, 0.2), P.chrome, major_segments=40, minor_segments=4)
    # chase LEDs round the collar
    for i in range(8):
        a = TAU * i / 8 + math.pi / 8
        x, y = math.cos(a) * 0.7, math.sin(a) * 0.7
        p = piv("led_%d" % (i + 1), (x, y, 0.22))
        sphere(0.024, (x * 1.03, y * 1.03, 0.22), amber, segments=8, rings=5, parent=p)
        blink(p, "idle", seconds=2.0, at=i * 0.25, length=0.2, lo=0.5, hi=1.4)
    # chrome bezel the button travels in, with a red glow gasket
    lathe([(0.51, 0.2), (0.51, 0.35), (0.535, 0.365), (0.52, 0.378), (0.495, 0.372), (0.495, 0.2)], P.chrome, segs=40, cap=False, name="bezel")
    torus(0.497, 0.01, (0, 0, 0.372), red_glow, major_segments=40, minor_segments=3)

    # the button itself: a big domed arcade-style cap. button.gd moves the
    # 'top' pivot between y = 0 and -0.15: pressed, its top sits flush with
    # the bezel (and with the base collision box, 0.36 m).
    t = piv("top", (0, 0, 0))
    lathe([(0.0, 0.2), (0.488, 0.2), (0.488, 0.37), (0.482, 0.41), (0.46, 0.45), (0.41, 0.485), (0.3, 0.508), (0.16, 0.518), (0.0, 0.52)],
          red, segs=40, name="cap", parent=t)
    torus(0.33, 0.008, (0, 0, 0.505), red_glow, major_segments=32, minor_segments=3, parent=t)
    merge_under(t, "cap_mesh")


def bumper():
    """A pinball pop bumper, 1.2 m across, 0.98 m tall: black base with
    screws, a chrome skirt ('skirt' pivot), a translucent body with a
    rubber kick ring, and a mushroom cap ('cap' pivot) whose star insert is
    the mesh 'cap_light' (bumper.gd flashes it). `hit` is the kick: the
    skirt snaps down, the cap squashes and rebounds, the ring bulges; `idle`
    chases the base LEDs."""
    P = palette()
    body_m = pbr("plastic", (0.55, 0.03, 0.3), rough=0.12, wear=0.05, name="bumper_body")
    cap_m = pbr("plastic", (0.8, 0.78, 0.82), rough=0.18, wear=0.1, name="cap_white")
    cap_edge = pbr("plastic", (0.55, 0.03, 0.3), rough=0.15, name="cap_pink")
    ring_m = pbr("rubber", (0.03, 0.03, 0.035), rough=0.55, name="kick_rubber")
    light_m = pbr("neon", (1.0, 0.85, 0.2), strength=2.5, name="cap_light")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=5.0, name="neon_cyan")

    # base plate with screws and a chasing LED ring
    lathe([(0.0, 0.0), (0.6, 0.0), (0.6, 0.05), (0.57, 0.09), (0.3, 0.1), (0.0, 0.1)], P.black, segs=32, name="base")
    for i in range(6):
        a = TAU * i / 6
        hexbolt((math.cos(a) * 0.5, math.sin(a) * 0.5, 0.075), 0.025, P.chrome, axis="Z")
    for i in range(12):
        a = TAU * i / 12 + TAU / 24
        x, y = math.cos(a) * 0.585, math.sin(a) * 0.585
        p = piv("led_%d" % (i + 1), (x, y, 0.06))
        sphere(0.02, (x, y, 0.06), cyan, segments=6, rings=4, parent=p)
        blink(p, "idle", seconds=2.0, at=(i * 2.0 / 12) % 2.0, length=0.2, lo=0.5, hi=1.4)
    # body column
    lathe([(0.0, 0.1), (0.3, 0.1), (0.3, 0.72), (0.0, 0.72)], body_m, segs=24, name="column")
    for i in range(8):
        a = TAU * i / 8
        cube((0.03, 0.02, 0.4), (math.cos(a) * 0.305, math.sin(a) * 0.305, 0.44), P.chrome, rot=(0, 0, a + math.pi / 2), bevel=0)
    # chrome skirt (snaps down on a kick)
    sk = piv("skirt", (0, 0, 0.1))
    lathe([(0.3, 0.3), (0.34, 0.3), (0.52, 0.13), (0.55, 0.12), (0.56, 0.14), (0.36, 0.33), (0.3, 0.34)], P.chrome,
          segs=32, cap=False, parent=sk, name="skirt_mesh")
    # rubber kick ring
    rg = piv("ring", (0, 0, 0.5))
    torus(0.37, 0.06, (0, 0, 0.5), ring_m, major_segments=32, minor_segments=8, scale=(1, 1, 1.3), parent=rg)
    # the cap
    cp = piv("cap", (0, 0, 0.72))
    lathe([(0.0, 0.72), (0.34, 0.72), (0.56, 0.78), (0.6, 0.82), (0.6, 0.86), (0.55, 0.9), (0.4, 0.93), (0.0, 0.94)],
          cap_m, segs=32, band_mats=[1, 1, 1, 0, 0, 0, 0], mats=(cap_edge,), parent=cp, name="cap_shell")
    torus(0.6, 0.02, (0, 0, 0.805), P.chrome, major_segments=32, minor_segments=4, parent=cp)
    merge_under(cp, "cap_body")
    # star insert under a clear dome: the flashing light
    star = []
    for i in range(10):
        a = TAU * i / 10 + math.pi / 2
        r = 0.3 if i % 2 == 0 else 0.13
        star.append((math.cos(a) * r, math.sin(a) * r))
    st = prism(star, 0.03, light_m, y=0.935, axis="Z", name="star")
    band = lathe([(0.603, 0.825), (0.607, 0.845), (0.603, 0.865)], light_m, segs=32, cap=False, name="band")
    hang(join([st, band], "cap_light"), cp)
    lathe([(0.0, 0.94), (0.36, 0.94), (0.32, 0.965), (0.18, 0.98), (0.0, 0.985)], P.glass, segs=24, parent=cp, name="dome")

    # the kick
    key(cp, "hit", "scale", [(0, (1, 1, 1)), (2, (1.16, 1.16, 0.72)), (5, (0.93, 0.93, 1.12)), (8, (1.04, 1.04, 0.96)), (11, (1, 1, 1))])
    key(cp, "hit", "location", [(0, (0, 0, 0.72)), (2, (0, 0, 0.66)), (5, (0, 0, 0.75)), (8, (0, 0, 0.715)), (11, (0, 0, 0.72))])
    key(sk, "hit", "location", [(0, (0, 0, 0.1)), (1, (0, 0, 0.05)), (4, (0, 0, 0.05)), (8, (0, 0, 0.1)), (11, (0, 0, 0.1))])
    key(rg, "hit", "scale", [(0, (1, 1, 1)), (2, (1.12, 1.12, 0.85)), (5, (0.96, 0.96, 1.05)), (8, (1.02, 1.02, 0.99)), (11, (1, 1, 1))])


def _fan_blade(a, r0, r1, z, m, parent=None, chord=0.3, pitch=0.55):
    """A swept, twisted fan blade from r0 to r1 at angle a (thin, two-sided)."""
    bm = bmesh.new()
    rows = []
    n = 5
    for i in range(n + 1):
        t = i / n
        r = r0 + (r1 - r0) * t
        c = chord * (0.75 + 0.45 * math.sin(math.pi * min(1.0, t * 1.1)))
        p = pitch * (1 - 0.45 * t)
        sweep_a = a + 0.25 * t * t                      # swept tips
        row = []
        for u in (-0.5, 0.0, 0.5):
            da = (u * c * math.cos(p)) / r
            row.append(bm.verts.new((math.cos(sweep_a + da) * r, math.sin(sweep_a + da) * r, z + u * c * math.sin(p) + (0.008 if u == 0 else 0))))
        rows.append(row)
    for k in range(n):
        A, B = rows[k], rows[k + 1]
        bm.faces.new((A[0], A[1], B[1], B[0]))
        bm.faces.new((A[1], A[2], B[2], B[1]))
    return _obj("fan_blade", bm, m, smooth=True, angle=70, parent=parent)


def air_fan():
    """An industrial floor fan, 2 x 2 m, 0.9 m tall, blowing straight up:
    a painted steel housing with warning stripes and rubber feet, a round
    duct with a neon under-glow, five swept blades on 'blades' (spun by
    air_fan.gd) under a wire grille, a control box and a power cable."""
    P = palette()
    house = pbr("paint", (0.03, 0.09, 0.11), name="fan_housing")
    duct = pbr("metal", (0.34, 0.35, 0.39), rough=0.4, name="duct_steel")
    blade_m = pbr("paint", (0.55, 0.57, 0.62), wear=0.4, name="blade_paint")
    wire = pbr("chrome", (0.72, 0.74, 0.78), rough=0.2, name="grille_wire")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=4.0, name="neon_cyan")
    green = pbr("neon", (0.1, 1.0, 0.3), strength=5.0, name="led_green")

    # housing: a chamfered box with a round opening (as a lathe top plate)
    prism([(-1.0, 0.06), (1.0, 0.06), (1.0, 0.62), (0.94, 0.72), (-0.94, 0.72), (-1.0, 0.62)], 2.0, house, bevel=0.025)
    for sx in (-1, 1):
        for sy in (-1, 1):
            cyl(0.1, 0.06, (sx * 0.85, sy * 0.85, 0.03), P.rubber, verts=10, bevel=0.01)
            hexbolt((sx * 0.86, sy * 0.86, 0.72), 0.035, P.chrome, axis="Z")
    # warning stripes on the front and sides
    hazard_band(-0.9, 0.9, 0.14, 0.3, -1.012, stripe=0.1, slant=0.1, P=P)
    for s in (-1, 1):
        o = hazard_band(-0.9, 0.9, 0.14, 0.3, -1.012, stripe=0.1, slant=0.1, P=P)
        o.matrix_world = Matrix.Rotation(s * math.pi / 2, 4, "Z") @ o.matrix_world
    # louvres on the front
    for k in range(5):
        rbox((1.2, 0.03, 0.03), (0, -1.01, 0.38 + k * 0.05), P.black, r=0.008)
    # duct ring + collar on top
    lathe([(0.8, 0.3), (0.8, 0.72), (0.86, 0.73), (0.92, 0.75), (0.93, 0.83), (0.91, 0.86), (0.86, 0.86), (0.82, 0.85)],
          duct, segs=40, cap=False, name="duct")
    torus(0.79, 0.02, (0, 0, 0.34), cyan, major_segments=40, minor_segments=4)
    cyl(0.8, 0.02, (0, 0, 0.3), P.black, verts=40, bevel=0)                  # duct floor
    # motor under the hub, on three struts
    lathe([(0.0, 0.3), (0.2, 0.3), (0.22, 0.34), (0.22, 0.5), (0.18, 0.52), (0.0, 0.52)], P.gun, segs=20, name="motor")
    for i in range(3):
        a = TAU * i / 3 + 0.3
        rod((math.cos(a) * 0.2, math.sin(a) * 0.2, 0.36), (math.cos(a) * 0.79, math.sin(a) * 0.79, 0.36), 0.03, P.gun, verts=6)

    # the rotor
    b = piv("blades", (0, 0, 0.58))
    lathe([(0.0, 0.53), (0.17, 0.53), (0.17, 0.6), (0.13, 0.66), (0.06, 0.69), (0.0, 0.695)], P.chrome, segs=20, parent=b, name="spinner")
    for i in range(5):
        _fan_blade(TAU * i / 5, 0.14, 0.76, 0.59, blade_m, parent=b)
    merge_under(b, "blade_mesh")

    # wire grille: rings + spokes + a centre badge
    dome = lambda r: 0.86 + 0.07 * (1 - (r / 0.88) ** 2)
    for r in (0.2, 0.36, 0.52, 0.68, 0.84):
        torus(r, 0.011, (0, 0, dome(r)), wire, major_segments=max(16, int(r * 44)), minor_segments=3)
    for i in range(16):
        a = TAU * i / 16
        sweep([(math.cos(a) * r, math.sin(a) * r, dome(r)) for r in (0.1, 0.35, 0.6, 0.88)], 0.01, wire, prof=4)
    cyl(0.12, 0.03, (0, 0, 0.93), P.gun, verts=16, bevel=0.01)
    cyl(0.07, 0.034, (0, 0, 0.93), cyan, verts=16, bevel=0)

    # control box, LED, switch and a cable running off the back
    rbox((0.34, 0.12, 0.3), (0.62, -1.05, 0.45), P.gun, r=0.02)
    p = piv("led_1", (0.53, -1.115, 0.53))
    sphere(0.022, (0.53, -1.115, 0.53), green, segments=8, rings=5, parent=p)
    blink(p, "idle", seconds=2.0, at=0.0, length=1.0, lo=0.6, hi=1.2)
    rbox((0.07, 0.04, 0.12), (0.68, -1.12, 0.45), pbr("plastic", (0.7, 0.03, 0.03), name="switch_red"), r=0.012)
    sweep([(0.8, 1.0, 0.3), (0.82, 1.08, 0.24), (0.85, 1.12, 0.08), (0.88, 1.25, 0.035), (0.9, 1.5, 0.035)], 0.035, P.rubber, prof=6)


def treadmill():
    """A commercial gym treadmill, 4.3 m long, 2.7 m tall. The running belt
    is its own mesh ('belt', material 'haz_belt': treadmill.gd swaps it for
    a scrolling ribbed-rubber shader); 'roller_1' (rear) and 'roller_2'
    (front, under the motor hood) are spun in code. Aluminium side rails
    with rubber foot strips, motor hood, uprights, handlebars with grips, a
    console with an animated screen, buttons and a safety key."""
    P = palette()
    frame = pbr("paint", (0.035, 0.038, 0.06), name="tm_frame")
    alu = pbr("metal", (0.66, 0.68, 0.72), rough=0.26, name="tm_alu")
    hood = pbr("plastic", (0.05, 0.05, 0.07), rough=0.3, name="tm_hood")
    accent = pbr("plastic", (0.55, 0.03, 0.32), rough=0.25, name="tm_pink")
    grip = pbr("rubber", (0.05, 0.05, 0.06), bump=0.8, name="tm_grip")
    belt_m = pbr("neon", (0.03, 0.03, 0.035), emit=(0.0, 0.0, 0.0), strength=0.0, name="haz_belt")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=4.0, name="neon_cyan")
    pink = pbr("neon", (1.0, 0.15, 0.6), strength=4.0, name="neon_pink")
    key_red = pbr("plastic", (0.75, 0.03, 0.04), rough=0.25, name="key_red")
    X0, X1 = -1.85, 1.45          # roller centres
    RR = 0.14                     # roller radius
    RZ = 0.43                     # roller axis height -> belt top 0.57

    # --- base frame, rails, feet -----------------------------------------------
    rbox((3.7, 1.1, 0.16), (-0.2, 0, 0.26), frame, r=0.03)                                  # deck under the belt
    for s in (-1, 1):
        prism([(-2.02, 0.14), (1.55, 0.14), (1.6, 0.3), (1.55, 0.58), (-2.0, 0.58), (-2.05, 0.5), (-2.05, 0.2)], 0.14, alu, y=s * 0.64, bevel=0.02)
        rbox((3.3, 0.12, 0.025), (-0.25, s * 0.64, 0.59), grip, r=0.008)                   # foot strips
        rbox((3.3, 0.012, 0.03), (-0.25, s * 0.715, 0.42), cyan if s < 0 else pink, r=0.004)
        for x in (-1.8, 1.3):
            cyl(0.07, 0.12, (x, s * 0.6, 0.07), P.rubber, verts=10, bevel=0.01)             # levelling feet
        # rear end cap
        rbox((0.12, 0.2, 0.36), (-2.05, s * 0.64, 0.36), hood, r=0.04)
    rbox((0.1, 1.42, 0.08), (-2.08, 0, 0.26), hood, r=0.03)                                 # rear bumper
    # transport wheels at the front
    for s in (-1, 1):
        cyl(0.09, 0.06, (2.12, s * 0.5, 0.1), P.rubber, rot=(math.pi / 2, 0, 0), verts=14, bevel=0.01)
        cyl(0.04, 0.07, (2.12, s * 0.5, 0.1), P.chrome, rot=(math.pi / 2, 0, 0), verts=10, bevel=0)

    # --- rollers (code spins them about the Y axis) -----------------------------
    for k, x in enumerate((X0, X1)):
        p = piv("roller_%d" % (k + 1), (x, 0, RZ))
        cyl(RR - 0.012, 1.14, (x, 0, RZ), alu, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.005, parent=p)
        for s in (-1, 1):                     # spoked end caps so the spin reads
            cyl(RR * 0.8, 0.02, (x, s * 0.72, RZ), P.chrome, rot=(math.pi / 2, 0, 0), verts=12, bevel=0, parent=p)
            for j in range(3):
                a = TAU * j / 3
                cube((RR * 1.3, 0.024, 0.03), (x + math.cos(a) * RR * 0.3, s * 0.735, RZ + math.sin(a) * RR * 0.3), accent,
                     rot=(0, -a, 0), bevel=0, parent=p)
        merge_under(p, "roller_%d_mesh" % (k + 1))

    # --- the belt: a loop round both rollers ------------------------------------
    pts = []
    n = 8
    for i in range(n + 1):                                    # front curve
        a = math.pi / 2 - math.pi * i / n
        pts.append((X1 + math.cos(a) * RR, RZ + math.sin(a) * RR))
    for i in range(n + 1):                                    # rear curve
        a = -math.pi / 2 - math.pi * i / n
        pts.append((X0 + math.cos(a) * RR, RZ + math.sin(a) * RR))
    bm = bmesh.new()
    left = [bm.verts.new((x, -0.55, z)) for x, z in pts]
    right = [bm.verts.new((x, 0.55, z)) for x, z in pts]
    for i in range(len(pts)):
        j = (i + 1) % len(pts)
        bm.faces.new((left[i], left[j], right[j], right[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _obj("belt", bm, belt_m, smooth=True, angle=60)

    # --- motor hood ----------------------------------------------------------------
    prism([(1.25, 0.14), (2.2, 0.14), (2.25, 0.3), (2.12, 0.62), (1.95, 0.7), (1.3, 0.68), (1.22, 0.62)], 1.4, hood, bevel=0.04)
    rbox((0.7, 0.02, 0.05), (1.75, -0.71, 0.5), accent, r=0.01)
    text("BOMBFIT", 0.1, (1.75, -0.712, 0.34), pbr("neon", (1.0, 0.95, 0.95), strength=2.0, name="label_white"), extrude=0.004, name="brand")
    for k in range(6):
        rbox((0.035, 1.0, 0.02), (1.45 + k * 0.1, 0, 0.69), P.black, r=0.006)            # vent slots

    # --- uprights, console, handlebars --------------------------------------------
    for s in (-1, 1):
        sweep([(1.75, s * 0.6, 0.6), (1.8, s * 0.6, 1.2), (1.9, s * 0.58, 1.85), (1.96, s * 0.56, 2.2)], 0.075, frame, prof=8, squash=0.7)
        rbox((0.2, 0.18, 0.1), (1.74, s * 0.6, 0.66), alu, r=0.02)                        # upright foot
        # handlebar: from the console back along the side
        sweep([(1.85, s * 0.56, 1.95), (1.55, s * 0.62, 1.88), (1.0, s * 0.64, 1.72), (0.72, s * 0.64, 1.6)], 0.04, alu, prof=8)
        sweep([(1.45, s * 0.625, 1.86), (0.8, s * 0.64, 1.63)], 0.052, grip, prof=8)        # rubber grip / pulse sensor
        cube((0.3, 0.02, 0.03), (1.15, s * 0.667, 1.76), cyan, rot=(0, 0.3, 0), bevel=0)
    rbox((0.34, 1.5, 0.08), (2.0, 0, 1.98), frame, r=0.03)                                  # crossbar
    # console: a wedge whose face leans back, towards the runner and up
    F0, F1 = Vector((1.62, 0, 2.05)), Vector((1.9, 0, 2.6))       # face, bottom -> top
    prism([(F0.x, F0.z), (2.2, 2.05), (2.26, 2.42), (2.12, 2.62), (F1.x, F1.z)], 1.45, hood, bevel=0.05)
    along = (F1 - F0).normalized()
    nrm = Vector((-along.z, 0, along.x))                           # outward: -X and up
    tilt = (0, math.atan2(nrm.z, -nrm.x), 0)                       # turns a -X facing plate onto the face

    def on_face(u, v, d=0.0):
        """Point on the console face: u along it (bottom -> top), v across (y)."""
        return tuple(F0.lerp(F1, u) + nrm * d + Vector((0, v, 0)))
    rbox((0.05, 1.2, 0.44), on_face(0.52, 0, 0.0), P.black, r=0.02, rot=tilt)
    cube((0.02, 0.64, 0.32), on_face(0.55, 0, 0.03), anim(((0.02, 0.1, 0.12), 0.3, 0.0, (0.2, 0.9, 1.0), 1.8), "screen"), rot=tilt, bevel=0)
    for j, m in enumerate((pink, cyan, pink)):
        cube((0.02, 0.1, 0.05), on_face(0.72 - j * 0.14, -0.46, 0.03), m, rot=tilt, bevel=0)
    for j in range(4):
        rbox((0.03, 0.08, 0.05), on_face(0.72 - (j // 2) * 0.16, 0.42 + (j % 2) * 0.1, 0.03), accent if j == 0 else P.gun, r=0.01, rot=tilt)
    cube((0.02, 1.3, 0.03), on_face(0.97, 0, 0.0), pink, rot=tilt, bevel=0)
    for s in (-1, 1):
        cube((0.5, 0.02, 0.025), (2.0, s * 0.73, 2.52), cyan if s < 0 else pink, rot=(0, 0.25, 0), bevel=0)   # side light
        cyl(0.07, 0.08, (1.8, s * 0.62, 2.06), P.black, verts=12, bevel=0.01)                                # cup holders
    rbox((0.06, 0.09, 0.06), on_face(0.1, -0.3, 0.02), key_red, r=0.015, rot=tilt)
    k0 = Vector(on_face(0.1, -0.3, 0.03))
    sweep([tuple(k0), tuple(k0 + Vector((-0.05, -0.02, -0.12))), tuple(k0 + Vector((-0.06, 0.02, -0.25))), tuple(k0 + Vector((-0.03, 0.05, -0.3)))], 0.008, key_red, prof=4)
    # status LEDs over the screen (the only `idle` motion: rollers and belt
    # are driven by treadmill.gd)
    for j in range(3):
        loc = on_face(0.9, -0.2 + j * 0.2, 0.035)
        p = piv("led_%d" % (j + 1), loc)
        sphere(0.022, loc, (cyan, pink, cyan)[j], segments=6, rings=4, parent=p)
        blink(p, "idle", seconds=2.0, at=j * 0.6, length=0.3, lo=0.5, hi=1.3)


def rope_link():
    """One 1 m segment of a thick three-strand rope (one strand neon-pink
    nylon), lying along X and centred. rope.gd chains many of them, so the
    lay makes one whole turn per metre and strands meet link to link.
    Three swept strands, 300 triangles."""
    navy = pbr("fabric", (0.05, 0.05, 0.12), color2=(0.1, 0.1, 0.2), rough=0.8, scale=0.3, name="rope_navy")
    pink = pbr("fabric", (0.75, 0.06, 0.4), color2=(0.95, 0.2, 0.55), rough=0.7, scale=0.3, name="rope_pink")
    L = 1.06                  # a hair longer than a link so bends don't gap
    n = 10
    parts = []
    for s in range(3):
        pts = []
        for i in range(n + 1):
            x = -L / 2 + L * i / n
            a = TAU * (x + 0.5) + TAU * s / 3
            pts.append((x, math.cos(a) * 0.064, math.sin(a) * 0.064))
        parts.append(sweep(pts, 0.074, pink if s == 0 else navy, prof=5, cap=False, angle=100, name="strand"))
    join(parts, "rope")


def _flame(loc, height, width, m, name, parent=None, lean=(0.0, 0.0), segs=10):
    """A flame tongue: a unit-height teardrop (mesh z runs 0..1 so the
    haz_flame shader can read the height from VERTEX.y), scaled on the
    object to `height` x `width`."""
    prof = [(0.0, 0.0), (0.2, 0.02), (0.36, 0.1), (0.42, 0.22), (0.38, 0.38), (0.28, 0.56), (0.16, 0.74), (0.06, 0.9), (0.0, 1.0)]
    o = lathe(prof, m, segs=segs, name=name, smooth=True, angle=80, cap=False)
    # a gentle S-bend so tongues don't look like cones
    for v in o.data.vertices:
        z = v.co.z
        v.co.x += 0.12 * math.sin(z * 2.6) * z
    o.location = loc
    o.scale = (width, width, height)
    o.rotation_euler = (lean[0], lean[1], 0)
    if parent is not None:
        hang(o, parent)
    return o


def fire_zone():
    """A burning clump of wreckage, ~1.7 m across and centred (it falls as a
    ball in the game): charred beams and a bent steel girder over a glowing
    ember bed, with layered flame tongues on 'flame_*' pivots (flickering in
    `idle`; their 'haz_flame_*' materials become an animated shader in
    fire_zone.gd) and embers rising on 'ember_*' pivots."""
    P = palette()
    DZ = -0.17                     # the clump rests on the 0.86 m ball's bottom
    char = pbr("wood", (0.035, 0.022, 0.016), color2=(0.008, 0.006, 0.005), rough=0.85, bump=1.0, name="charcoal")
    burnt = pbr("paint", (0.06, 0.035, 0.03), wear=0.9, grime=1.0, name="burnt_paint")
    ember_m = pbr("neon", (1.0, 0.22, 0.03), strength=2.2, name="ember_glow")
    hot = pbr("neon", (1.0, 0.6, 0.15), strength=8.0, name="ember_hot")
    f_outer = pbr("neon", (1.0, 0.28, 0.04), strength=4.0, name="haz_flame_outer")
    f_mid = pbr("neon", (1.0, 0.55, 0.1), strength=5.0, name="haz_flame_mid")
    f_core = pbr("neon", (1.0, 0.85, 0.45), strength=7.0, name="haz_flame_core")

    # ember bed: a glowing, cracked lump under everything
    ico(0.5, (0, 0, -0.42), ember_m, subdiv=2, smooth=True)
    b = bpy.context.object
    b.scale = (1.35, 1.0, 0.45)
    ico(0.46, (0.05, 0.02, -0.4), char, subdiv=2, smooth=False)
    c = bpy.context.object
    c.scale = (1.45, 1.1, 0.52)
    for v in c.data.vertices:                          # lumpy, cracked charcoal shell
        n = math.sin(v.co.x * 13.1) * math.cos(v.co.y * 11.7) * math.sin(v.co.z * 9.3)
        v.co *= 1.0 + 0.18 * n
    # charred beams, crossed
    for (p0, p1, r) in (((-0.85, -0.2, -0.45), (0.7, 0.25, 0.05), 0.12), ((0.8, -0.25, -0.5), (-0.55, 0.2, 0.12), 0.11),
                        ((-0.3, -0.45, -0.55), (0.25, 0.4, 0.2), 0.1), ((0.1, -0.35, -0.2), (0.75, 0.3, -0.45), 0.09)):
        o = rod(p0, p1, r, char, verts=6, smooth=False)
        v = Vector(p1) - Vector(p0)
        # glowing cracks along each beam
        mid = (Vector(p0) + Vector(p1)) / 2
        rod(tuple(mid - v * 0.3 + Vector((0, -r * 0.8, 0))), tuple(mid + v * 0.2 + Vector((0, -r * 0.8, 0))), r * 0.2, hot, verts=4)
    # a bent steel I-beam sticking out
    web = [(-0.2, 0.15, -0.3), (0.3, 0.1, 0.05), (0.55, 0.05, 0.45)]
    sweep(web, 0.05, burnt, prof=4, squash=2.5)
    for dz in (-0.08, 0.08):
        sweep([(x + dz * 0.6, y, z - dz) for x, y, z in web], 0.035, burnt, prof=4, squash=0.4)
    # debris plank splinters
    for i, (x, y, a) in enumerate(((-0.55, -0.35, 0.5), (0.45, -0.4, -0.7), (-0.2, 0.4, 1.2))):
        cube((0.5, 0.06, 0.1), (x, y, -0.35), char, rot=(0.2, a * 0.3, a), bevel=0.01)

    # flames: three layers of tongues, each on a flickering pivot
    specs = []
    for i in range(7):                     # outer ring of tall red-orange tongues
        a = TAU * i / 7 + 0.3
        specs.append(((math.cos(a) * 0.45, math.sin(a) * 0.3, -0.25), 1.1 + 0.35 * ((i * 37) % 5) / 4, 0.4, f_outer, (math.sin(a) * 0.25, -math.cos(a) * 0.25)))
    for i in range(5):                     # middle orange
        a = TAU * i / 5 + 0.9
        specs.append(((math.cos(a) * 0.25, math.sin(a) * 0.15, -0.2), 1.25 + 0.3 * ((i * 53) % 3) / 2, 0.32, f_mid, (math.sin(a) * 0.15, -math.cos(a) * 0.15)))
    for i in range(3):                     # hot core
        a = TAU * i / 3
        specs.append(((math.cos(a) * 0.1, math.sin(a) * 0.06 - 0.05, -0.2), 0.95, 0.24, f_core, (0.0, 0.0)))
    for k, (loc, h, w, m, lean) in enumerate(specs):
        p = piv("flame_%d" % (k + 1), loc)
        _flame(loc, h, w, m, "flame_mesh_%d" % (k + 1), parent=p, lean=lean)
        ph = k * 1.7
        osc(p, "idle", "scale", 2, 0.22, seconds=2.0, cycles=3 + k % 3, phase=ph, base=1.0)
        osc(p, "idle", "scale", 0, 0.1, seconds=2.0, cycles=2 + k % 2, phase=ph + 1.0, base=1.0)
        osc(p, "idle", "scale", 1, 0.1, seconds=2.0, cycles=2 + k % 2, phase=ph + 1.0, base=1.0)
        osc(p, "idle", "rotation_euler", 1, 0.12, seconds=2.0, cycles=2, phase=ph)

    for o in list(bpy.context.scene.objects):
        if o.parent is None:
            o.location.z += DZ
    # embers rising and fading
    for k in range(9):
        a = TAU * k / 9
        x, y = math.cos(a) * 0.4, math.sin(a) * 0.25
        p = piv("ember_%d" % (k + 1), (x, y, 0.1 + DZ))
        sphere(0.03, (x, y, 0.1 + DZ), hot, segments=5, rings=3, parent=p)
        end = 60
        s = (k * 7) % end
        rise = 1.3 + 0.2 * (k % 3)
        drift = 0.25 * math.sin(a * 3)
        keys_l, keys_s = [], []
        for f in range(0, end + 1, 6):
            t = ((f - s) % end) / end
            keys_l.append((f, (x + drift * t, y, 0.1 + DZ + rise * t)))
            keys_s.append((f, (max(0.01, 1.0 - t),) * 3 if t > 0.05 else (0.01,) * 3))
        key(p, "idle", "location", keys_l, interp="LINEAR")
        key(p, "idle", "scale", keys_s, interp="LINEAR")


def vault_door():
    """A massive bank-vault door, 6.6 m across its frame, centred and facing
    -Y: stepped circular steel layers with engraved grooves, a gold inlay
    ring and 'VAULT' plaque, 24 rim rivets, a heavy two-knuckle hinge, the
    spoked 'wheel' (spun by vault.gd), a combination 'dial' and a lock box
    whose red bar is the mesh 'lock_light' (turns green when cracked).
    `idle`: the dial ticks back and forth, indicator LEDs blink."""
    P = palette()
    steel = pbr("metal", (0.58, 0.6, 0.64), rough=0.3, scale=2.0, name="vault_steel")
    field = pbr("metal", (0.36, 0.37, 0.41), rough=0.4, scale=2.0, name="vault_field")
    frame_m = pbr("paint", (0.045, 0.05, 0.075), scale=2.0, name="vault_frame")
    red = pbr("neon", (1.0, 0.08, 0.1), strength=5.0, name="lock_red")
    amber = pbr("neon", (1.0, 0.45, 0.05), strength=5.0, name="led_amber")
    cyan = pbr("neon", (0.05, 0.85, 0.95), strength=3.0, name="neon_cyan")
    ROT = (math.pi / 2, 0, 0)          # lathe z -> towards the camera (-Y)

    # --- the wall frame ---------------------------------------------------------
    lathe([(2.86, -0.3), (2.86, 0.3), (2.92, 0.4), (3.3, 0.4), (3.36, 0.34), (3.36, -0.3)], frame_m, rot=ROT, segs=48,
          cap=False, name="frame")
    for i in range(20):
        a = TAU * (i + 0.5) / 20
        hexbolt((math.cos(a) * 3.13, -0.4, math.sin(a) * 3.13), 0.055, P.chrome, axis="-Y", washer=False)
    torus(2.87, 0.025, (0, -0.33, 0), cyan, rot=ROT, major_segments=48, minor_segments=3)

    # --- the door ---------------------------------------------------------------
    prof = [(0.0, 0.5), (0.62, 0.5), (0.66, 0.46), (0.9, 0.46), (0.92, 0.44), (1.02, 0.44), (1.04, 0.46), (1.86, 0.46),
            (1.9, 0.52), (2.06, 0.52), (2.1, 0.48), (2.46, 0.48), (2.5, 0.56), (2.7, 0.56), (2.78, 0.5), (2.8, 0.42), (2.8, -0.3)]
    bands = [1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0]
    lathe(prof, steel, rot=ROT, segs=48, cap=False, name="door", band_mats=[0 if b == 0 else 1 for b in bands], mats=(field,))
    torus(1.98, 0.022, (0, -0.52, 0), P.gold, rot=ROT, major_segments=48, minor_segments=3)      # gold inlay
    torus(0.96, 0.012, (0, -0.44, 0), P.gold, rot=ROT, major_segments=32, minor_segments=3)
    for i in range(32):                                              # engraved sunburst ridges
        a = TAU * i / 32
        if abs(math.sin(a) - 1.0) < 0.12:
            continue                                                 # leave room for the plaque
        ca, sa = math.cos(a), math.sin(a)
        rod((ca * 2.14, -0.485, sa * 2.14), (ca * 2.42, -0.485, sa * 2.42), 0.012, steel, verts=4)
    for i in range(20):                                              # rim rivets
        a = TAU * (i + 0.5) / 20
        sphere(0.065, (math.cos(a) * 2.6, -0.57, math.sin(a) * 2.6), P.chrome, scale=(1, 0.6, 1), segments=6, rings=3)
    # plaque
    rbox((1.1, 0.04, 0.3), (0, -0.5, 2.28), P.gold, r=0.02)
    text("VAULT", 0.2, (0, -0.525, 2.28), P.black, extrude=0.01, name="plaque_text")

    # --- hinge on the right -------------------------------------------------------
    for z in (-1.55, 1.55):
        cyl(0.26, 0.85, (3.05, -0.55, z), steel, verts=16, bevel=0)
        cyl(0.29, 0.08, (3.05, -0.55, z + 0.45), P.chrome, verts=16, bevel=0)
        cyl(0.29, 0.08, (3.05, -0.55, z - 0.45), P.chrome, verts=16, bevel=0)
        rbox((0.9, 0.24, 0.6), (2.55, -0.6, z), steel, r=0.05)
        for k in range(3):
            hexbolt((2.25 + k * 0.22, -0.72, z + 0.18), 0.04, P.chrome, axis="-Y", washer=False)
            hexbolt((2.25 + k * 0.22, -0.72, z - 0.18), 0.04, P.chrome, axis="-Y", washer=False)
    cyl(0.1, 3.9, (3.05, -0.55, 0), P.chrome, verts=12, bevel=0)                               # hinge pin

    # --- the wheel ------------------------------------------------------------------
    w = piv("wheel", (0, -0.6, 0))
    parts = [torus(0.95, 0.075, (0, -0.95, 0), P.gold, rot=ROT, major_segments=36, minor_segments=6)]
    parts.append(lathe([(0.0, 0.5), (0.28, 0.5), (0.3, 0.6), (0.24, 0.9), (0.18, 0.98), (0.0, 1.0)], P.chrome, rot=ROT, segs=20, name="hub"))
    for i in range(6):
        a = TAU * i / 6
        ca, sa = math.cos(a), math.sin(a)
        parts.append(rod((ca * 0.2, -0.9, sa * 0.2), (ca * 0.93, -0.95, sa * 0.93), 0.05, P.gold, verts=8))
        parts.append(sphere(0.1, (ca * 1.08, -0.95, sa * 1.08), P.black, segments=8, rings=5))    # grips
        parts.append(rod((ca * 0.95, -0.95, sa * 0.95), (ca * 1.02, -0.95, sa * 1.02), 0.045, P.gold, verts=8))
    for o in parts:
        hang(o, w)
    merge_under(w, "wheel_mesh")

    # --- combination dial above the wheel --------------------------------------------
    lathe([(0.0, 0.46), (0.42, 0.46), (0.42, 0.52), (0.38, 0.55), (0.0, 0.55)], P.black, loc=(0, 0, 1.45), rot=ROT, segs=32, name="dial_ring")
    for i in range(20):
        a = TAU * i / 20
        cube((0.018, 0.01, 0.06 if i % 5 else 0.1), (math.cos(a) * 0.36, -0.555, 1.45 + math.sin(a) * 0.36), P.gold, rot=(0, -a + math.pi / 2, 0), bevel=0)
    dl = piv("dial", (0, -0.55, 1.45))
    lathe([(0.0, 0.55), (0.28, 0.55), (0.3, 0.6), (0.26, 0.66), (0.08, 0.7), (0.0, 0.71)], P.chrome, loc=(0, 0, 1.45), rot=ROT, segs=24, parent=dl, name="dial_knob")
    cube((0.03, 0.02, 0.18), (0, -0.7, 1.45 + 0.17), red, bevel=0, parent=dl)
    merge_under(dl, "dial_mesh")
    key(dl, "idle", "rotation_euler", [(0, (0, 0, 0)), (10, (0, 0.5, 0)), (30, (0, 0.5, 0)), (45, (0, -0.8, 0)),
                                       (70, (0, -0.8, 0)), (85, (0, 0.2, 0)), (110, (0, 0.2, 0)), (120, (0, 0, 0))])

    # --- lock box below the wheel ------------------------------------------------------
    rbox((1.3, 0.14, 0.52), (0, -0.52, -1.45), P.gun, r=0.04)
    rbox((1.1, 0.04, 0.2), (0, -0.6, -1.4), P.black, r=0.02)
    cube((1.0, 0.03, 0.13), (0, -0.62, -1.4), red, bevel=0, name="lock_light")
    for k in range(4):
        p = piv("led_%d" % (k + 1), (-0.36 + k * 0.24, -0.6, -1.63))
        sphere(0.03, (-0.36 + k * 0.24, -0.6, -1.63), amber if k % 2 else cyan, segments=8, rings=5, parent=p)
        blink(p, "idle", seconds=4.0, at=0.4 + k * 0.9, length=0.4, lo=0.45, hi=1.25, count=2, gap=0.55)


# ------------------------------------------------------------- bat boss --
def _skin(o, weights):
    """Give mesh `o` vertex groups: `weights` is a bone name (every vertex)
    or a list with one {bone: weight} dict per vertex."""
    if isinstance(weights, str):
        vg = o.vertex_groups.get(weights) or o.vertex_groups.new(name=weights)
        vg.add(list(range(len(o.data.vertices))), 1.0, "REPLACE")
        return o
    for i, wd in enumerate(weights):
        for bone, w in wd.items():
            if w <= 1e-4:
                continue
            vg = o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone)
            vg.add([i], w, "ADD")
    return o


class _Spar:
    """A polyline of joints with one bone per segment; samples points and
    bone weights by normalised arc length (blended across the joints)."""

    def __init__(self, pts, bones):
        self.p = [Vector(x) for x in pts]
        self.bones = bones if isinstance(bones, list) else [bones] * (len(pts) - 1)
        self.len = [(b - a).length for a, b in zip(self.p, self.p[1:])]
        self.total = sum(self.len)

    def at(self, t):
        d = t * self.total
        for k, L in enumerate(self.len):
            if d <= L or k == len(self.len) - 1:
                tau = min(1.0, d / L if L > 0 else 0.0)
                pt = self.p[k].lerp(self.p[k + 1], tau)
                w = {self.bones[k]: 1.0}
                if tau < 0.25 and k > 0 and self.bones[k - 1] != self.bones[k]:
                    mix = 0.5 * (1 - tau / 0.25)
                    w = {self.bones[k]: 1 - mix, self.bones[k - 1]: mix}
                elif tau > 0.75 and k < len(self.len) - 1 and self.bones[k + 1] != self.bones[k]:
                    mix = 0.5 * (tau - 0.75) / 0.25
                    w = {self.bones[k]: 1 - mix, self.bones[k + 1]: mix}
                return pt, w
            d -= L
        return self.p[-1], {self.bones[-1]: 1.0}


def _membrane(A, B, skin_m, edge_m, nu=8, vs=None, sag=0.2, billow=0.16):
    """A wing panel spanning spars A and B (same root or not) with a
    scalloped free edge between their tips and a thin glowing hem."""
    vs = vs or [0.0, 0.12, 0.24, 0.36, 0.48, 0.6, 0.72, 0.84, 0.93, 0.975, 1.0]
    bm = bmesh.new()
    weights = []
    rows = []
    root = (A.p[0] + B.p[0]) / 2
    for v in vs:
        pa, wa = A.at(v)
        pb, wb = B.at(v)
        if (pa - pb).length < 1e-4:
            vert = bm.verts.new(pa)
            w = dict(wa)
            weights.append(w)
            rows.append([vert] * (nu + 1))
            continue
        row = []
        for i in range(nu + 1):
            u = i / nu
            p = pa.lerp(pb, u)
            p = p + (root - p) * sag * math.sin(math.pi * u) * v ** 3
            p.y += billow * math.sin(math.pi * u) * math.sin(math.pi * min(v, 0.999)) ** 0.7
            w = {}
            for bone, x in wa.items():
                w[bone] = w.get(bone, 0) + x * (1 - u)
            for bone, x in wb.items():
                w[bone] = w.get(bone, 0) + x * u
            row.append(bm.verts.new(p))
            weights.append(w)
        rows.append(row)
    for k in range(len(rows) - 1):
        _bridge(bm, rows[k], rows[k + 1], closed=False, mat=1 if k == len(rows) - 2 else 0)
    bm.verts.index_update()
    o = _obj("membrane", bm, skin_m, smooth=True, angle=80, mats=(edge_m,))
    # bmesh kept vertex creation order, so weights line up with indices
    return _skin(o, weights)


def boss_bat():
    """The bat boss: a 4 m furry, armour-plated robo-bat with a 9 m
    wingspan, rigged. Bones: root, head, jaw (driven by boss_bat.gd when it
    shoots/screams), blink, ear.L/R, upperarm/forearm/f2_1..f4_2 per wing,
    leg.L/R. One skinned body mesh plus separate skinned meshes 'eyes'
    and 'heart_glow' (the code flares/dims them). Clips: `idle` (2 s, two
    wing beats with the membrane folding on the upstroke, body bob, blink,
    ear twitch) and `fall_loop` (wings flailing as it drops; Godot's importer drops the
    _loop suffix and loops it, so the game plays "fall"). Centred."""
    fur = pbr("carpet", (0.1, 0.045, 0.15), color2=(0.2, 0.1, 0.27), bump=0.8, name="bat_fur")
    fur_light = pbr("carpet", (0.36, 0.18, 0.36), color2=(0.46, 0.24, 0.42), bump=0.8, name="bat_fur_light")
    skin = pbr("skin", (0.3, 0.06, 0.22), rough=0.68, bump=0.4, name="bat_membrane")
    skin_pink = pbr("skin", (0.7, 0.26, 0.38), rough=0.5, name="bat_skin_pink")
    bone_skin = pbr("leather", (0.12, 0.05, 0.13), rough=0.5, name="bat_bone_skin")
    armour = pbr("paint", (0.075, 0.07, 0.11), name="bat_armour")
    chrome = pbr("chrome", (0.8, 0.82, 0.86), name="bat_chrome")
    ivory = pbr("ceramic", (0.86, 0.82, 0.72), rough=0.25, name="bat_ivory")
    mouth = pbr("plastic", (0.08, 0.0, 0.02), rough=0.5, name="bat_mouth")
    eye_m = pbr("neon", (1.0, 0.78, 0.1), strength=7.0, name="bat_eyes")
    pupil = pbr("plastic", (0.01, 0.0, 0.01), rough=0.2, name="bat_pupil")
    heart_m = pbr("neon", (1.0, 0.1, 0.55), strength=5.0, name="bat_heart")
    edge_m = pbr("neon", (1.0, 0.12, 0.6), strength=2.0, name="bat_wing_edge")
    seam = pbr("neon", (1.0, 0.12, 0.6), strength=3.0, name="bat_seam")

    # ---------------------------------------------------------- skeleton --
    J = {}
    J["root"] = ((0, 0.05, -0.4), (0, 0.05, 0.5))
    J["head"] = ((0, -0.05, 0.95), (0, -0.05, 1.75))
    J["jaw"] = ((0, -0.35, 1.3), (0, -0.78, 1.1))
    J["blink"] = ((0, -0.62, 1.52), (0, -0.62, 1.72))
    wing = {}
    for s, side in ((1, "L"), (-1, "R")):
        sh = (s * 0.78, 0.12, 0.72)
        el = (s * 1.95, 0.2, 1.45)
        wr = (s * 3.05, 0.22, 1.95)
        f = {"f2": [(s * 3.72, 0.22, 2.12), (s * 4.45, 0.24, 1.78)],
             "f3": [(s * 3.78, 0.24, 1.4), (s * 4.3, 0.26, 0.45)],
             "f4": [(s * 3.38, 0.24, 1.05), (s * 3.45, 0.26, -0.05)]}
        wing[side] = dict(s=s, sh=sh, el=el, wr=wr, f=f, hip=(s * 0.6, 0.14, -0.85))
        J["upperarm." + side] = (sh, el)
        J["forearm." + side] = (el, wr)
        for name, (a, b) in f.items():
            J["%s_1.%s" % (name, side)] = (wr, a)
            J["%s_2.%s" % (name, side)] = (a, b)
        J["ear." + side] = ((s * 0.36, -0.05, 1.85), (s * 0.66, 0.0, 2.75))
        J["leg." + side] = ((s * 0.38, 0.0, -0.95), (s * 0.46, -0.1, -1.6))
    parents = {"head": "root", "jaw": "head", "blink": "head"}
    for side in ("L", "R"):
        parents.update({"upperarm." + side: "root", "forearm." + side: "upperarm." + side,
                        "ear." + side: "head", "leg." + side: "root"})
        for fn in ("f2", "f3", "f4"):
            parents["%s_1.%s" % (fn, side)] = "forearm." + side
            parents["%s_2.%s" % (fn, side)] = "%s_1.%s" % (fn, side)

    arm_data = bpy.data.armatures.new("bat_rig")
    rig = bpy.data.objects.new("bat_rig", arm_data)
    common._link(rig)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.mode_set(mode="EDIT")
    for name, (h, t) in J.items():
        eb = arm_data.edit_bones.new(name)
        eb.head, eb.tail = h, t
        eb.align_roll(Vector((0, -1, 0)) if abs((Vector(t) - Vector(h)).normalized().y) < 0.9 else Vector((0, 0, 1)))
    for name, par in parents.items():
        eb = arm_data.edit_bones[name]
        eb.parent = arm_data.edit_bones[par]
        eb.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")

    parts = []

    def part(o, bone):
        parts.append(_skin(o, bone))
        return o

    # ------------------------------------------------------------ body --
    torso = part(sphere(1.0, (0, 0.05, 0.0), fur, scale=(0.92, 0.78, 1.12), segments=24, rings=14), "root")
    # chest armour: the front of a slightly bigger ellipsoid
    plate = sphere(1.0, (0, 0.05, 0.02), armour, scale=(0.86, 0.8, 0.98), segments=20, rings=12)
    bpy.context.view_layer.update()
    bm = bmesh.new()
    bm.from_mesh(plate.data)
    bmesh.ops.transform(bm, matrix=plate.matrix_world, verts=bm.verts)
    plate.matrix_world = Matrix.Identity(4)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, -0.42, 0), plane_no=(0, 1, 0), clear_outer=True)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, 0.72), plane_no=(0, 0, 1), clear_outer=True)
    bmesh.ops.bisect_plane(bm, geom=bm.verts[:] + bm.edges[:] + bm.faces[:], plane_co=(0, 0, -0.62), plane_no=(0, 0, -1), clear_outer=True)
    for v in bm.verts:
        v.co.y -= 0.035
    bm.to_mesh(plate.data)
    bm.free()
    part(plate, "root")
    for z in (0.35, -0.3):                                                 # neon seams across the plate
        w = math.sqrt(max(0.0, 1 - (z / 0.98) ** 2)) * 0.86
        d = math.sqrt(max(0.0, 1 - (z / 0.98) ** 2)) * 0.8
        pts = []
        for i in range(9):
            a = -math.pi / 2 + (i - 4) * 0.17
            pts.append((math.cos(a) * w, 0.05 + math.sin(a) * d - 0.05, z))
        part(sweep(pts, 0.014, seam, prof=4), "root")
    for sx in (-1, 1):
        for z in (0.5, -0.45):
            part(sphere(0.035, (sx * 0.42, -0.72 if abs(z) < 0.5 else -0.68, z), chrome, segments=6, rings=4), "root")
    # the heart socket: a dark ring holding a glowing heart
    part(torus(0.2, 0.045, (0, -0.8, 0.02), chrome, rot=(math.pi / 2, 0, 0), major_segments=18, minor_segments=5), "root")
    hs = [sphere(0.085, (sx * 0.07, -0.8, 0.07), heart_m, segments=10, rings=6) for sx in (-1, 1)]
    hs.append(cone(0.13, 0.17, (0, -0.8, -0.06), heart_m, rot=(math.pi, 0, 0), verts=10))
    for o in hs:
        o.scale = (o.scale[0], 0.45 * o.scale[1], o.scale[2])
    heart = join(hs, "heart_glow")
    _skin(heart, "root")
    # fur ruff round the neck and a fluffy belly
    for i in range(18):
        a = TAU * i / 18
        ca, sa = math.cos(a), math.sin(a)
        o = cone(0.13, 0.36, (ca * 0.62, 0.05 + sa * 0.52, 0.86), fur, verts=6)
        o.rotation_euler = Vector((ca, sa * 0.8, -0.9)).to_track_quat("Z", "Y").to_euler()
        part(o, "root")
    part(sphere(0.5, (0, -0.42, -0.72), fur_light, scale=(1.05, 0.7, 0.62), segments=16, rings=8), "root")

    # ------------------------------------------------------------ head --
    part(sphere(0.72, (0, -0.02, 1.42), fur, scale=(1.05, 0.9, 0.86), segments=22, rings=14), "head")
    part(sphere(0.36, (0, -0.55, 1.26), skin_pink, scale=(1.15, 0.8, 0.7), segments=16, rings=10), "head")
    # nose leaf and nostrils
    nl = cone(0.13, 0.26, (0, -0.83, 1.42), skin_pink, verts=8)
    nl.scale = (1.0, 0.35, 1.0)
    part(nl, "head")
    for sx in (-1, 1):
        part(sphere(0.035, (sx * 0.06, -0.85, 1.3), mouth, segments=6, rings=4), "head")
    # brow armour: two angled plates (the angry look) with a centre crest
    for sx in (-1, 1):
        o = rbox((0.46, 0.12, 0.11), (sx * 0.28, -0.63, 1.7), armour, r=0.035, rot=(0.3, 0, sx * -0.5))
        part(o, "head")
        part(sphere(0.03, (sx * 0.44, -0.66, 1.79), chrome, segments=6, rings=4), "head")
        # short chrome horns at the brow corners
        part(cone(0.075, 0.34, (sx * 0.52, -0.42, 1.93), chrome, rot=(-0.35, sx * 0.55, 0), verts=8), "head")
    part(sphere(0.035, (0, -0.6, 1.83), seam, segments=6, rings=4), "head")
    # eyes (own mesh; they blink on the 'blink' bone) with slit pupils
    ev = []
    for sx in (-1, 1):
        ev.append(sphere(0.16, (sx * 0.3, -0.6, 1.55), eye_m, scale=(1.15, 0.55, 0.85), segments=14, rings=8))
    eyes = join(ev, "eyes")
    _skin(eyes, "blink")
    for sx in (-1, 1):
        part(sphere(0.03, (sx * 0.3, -0.69, 1.55), pupil, scale=(0.8, 0.5, 3.3), segments=8, rings=6), "blink")
    # upper fangs on the head, jaw with lower fangs
    part(sphere(0.2, (0, -0.72, 1.17), mouth, scale=(1.3, 0.45, 0.35), segments=12, rings=6), "head")
    for sx in (-1, 1):
        part(cone(0.055, 0.24, (sx * 0.14, -0.82, 1.1), ivory, rot=(math.pi + 0.15, 0, 0), verts=8), "head")
    part(sphere(0.27, (0, -0.58, 1.02), skin_pink, scale=(1.05, 0.72, 0.4), segments=14, rings=8), "jaw")
    for sx in (-1, 1):
        part(cone(0.035, 0.12, (sx * 0.2, -0.72, 1.12), ivory, rot=(-0.15, 0, 0), verts=6), "jaw")
    # ears: fur shells with pink insides and chrome tips; a gold ring
    for s, side in ((1, "L"), (-1, "R")):
        h, t = Vector(J["ear." + side][0]), Vector(J["ear." + side][1])
        d = (t - h)
        L = d.length
        rot = d.normalized().to_track_quat("Z", "Y").to_euler()
        mid = h + d * 0.5
        o = cone(0.46, L * 1.12, tuple(mid), fur, verts=12)
        o.scale = (1.0, 0.4, 1.0)
        o.rotation_euler = rot
        part(o, "ear." + side)
        o = cone(0.36, L * 0.97, tuple(mid + Vector((0, -0.09, -0.04))), skin_pink, verts=10)
        o.scale = (1.0, 0.3, 1.0)
        o.rotation_euler = rot
        part(o, "ear." + side)
        part(cone(0.06, 0.22, tuple(t + d.normalized() * 0.05), chrome, verts=6, rot=rot), "ear." + side)
        if s < 0:
            part(torus(0.1, 0.018, tuple(h + d * 0.35 + Vector((s * 0.22, 0, 0))), pbr("gold", (0.95, 0.66, 0.24), name="bat_gold"),
                       rot=(0, math.pi / 2, 0), major_segments=12, minor_segments=4), "ear." + side)

    # ------------------------------------------------------------ legs --
    for s, side in ((1, "L"), (-1, "R")):
        h, t = Vector(J["leg." + side][0]), Vector(J["leg." + side][1])
        part(sweep([tuple(h), tuple(h.lerp(t, 0.5) + Vector((s * 0.05, -0.05, 0))), tuple(t)], [0.2, 0.13, 0.09], fur, prof=8), "leg." + side)
        part(sphere(0.12, tuple(t), bone_skin, scale=(1.1, 1.2, 0.7), segments=10, rings=6), "leg." + side)
        for k in (-1, 0, 1):
            c = t + Vector((k * 0.08, -0.08, -0.06))
            part(sweep([tuple(c), tuple(c + Vector((k * 0.03, -0.1, -0.08))), tuple(c + Vector((k * 0.03, -0.06, -0.2)))],
                       [0.035, 0.028, 0.0], ivory, prof=5), "leg." + side)

    # ----------------------------------------------------------- wings --
    for side, W in wing.items():
        s = W["s"]
        # arm and finger bones: skin-covered, armoured bracers, chrome joints
        part(sweep([W["sh"], W["el"]], [0.2, 0.12], bone_skin, prof=8), "upperarm." + side)
        part(sweep([W["el"], W["wr"]], [0.12, 0.075], bone_skin, prof=8), "forearm." + side)
        el, wr = Vector(W["el"]), Vector(W["wr"])
        bracer = sweep([tuple(el.lerp(wr, 0.2)), tuple(el.lerp(wr, 0.75))], [0.14, 0.1], armour, prof=8, squash=0.8)
        part(bracer, "forearm." + side)
        part(sweep([tuple(Vector(W["sh"]).lerp(el, 0.15)), tuple(Vector(W["sh"]).lerp(el, 0.6))], [0.25, 0.17], armour, prof=8, squash=0.85), "upperarm." + side)
        for p, bone in ((W["el"], "forearm." + side), (W["wr"], "forearm." + side)):
            part(sphere(0.11 if bone.startswith("forearm") and p == W["el"] else 0.085, p, chrome, segments=10, rings=6), bone)
        for fn, (a, b) in W["f"].items():
            part(sweep([W["wr"], a], [0.06, 0.042], bone_skin, prof=6), "%s_1.%s" % (fn, side))
            part(sweep([a, b], [0.042, 0.012], bone_skin, prof=6), "%s_2.%s" % (fn, side))
            part(sphere(0.05, a, chrome, segments=8, rings=5), "%s_2.%s" % (fn, side))
        # thumb claw at the wrist
        part(sweep([tuple(wr), tuple(wr + Vector((s * 0.05, -0.05, 0.22))), tuple(wr + Vector((s * -0.05, -0.1, 0.32)))], [0.05, 0.035, 0.0], ivory, prof=5), "forearm." + side)
        # membranes
        f2 = _Spar([W["wr"]] + W["f"]["f2"], ["f2_1." + side, "f2_2." + side])
        f3 = _Spar([W["wr"]] + W["f"]["f3"], ["f3_1." + side, "f3_2." + side])
        f4 = _Spar([W["wr"]] + W["f"]["f4"], ["f4_1." + side, "f4_2." + side])
        armc = _Spar([W["sh"], W["el"], W["wr"]] + W["f"]["f4"], ["upperarm." + side, "forearm." + side, "f4_1." + side, "f4_2." + side])
        body = _Spar([W["sh"], (s * 0.8, 0.14, -0.1), W["hip"]], "root")
        parts.append(_membrane(f2, f3, skin, edge_m, nu=7, sag=0.28))
        parts.append(_membrane(f3, f4, skin, edge_m, nu=7, sag=0.28))
        parts.append(_membrane(body, armc, skin, edge_m, nu=9, sag=0.12, billow=0.25))

    # ---------------------------------------------------- one skinned mesh --
    body_mesh = join(parts, "bat_body")
    for o in (body_mesh, eyes, heart):
        o.parent = rig
        o.matrix_parent_inverse = Matrix.Identity(4)
        md = o.modifiers.new("rig", "ARMATURE")
        md.object = rig

    # -------------------------------------------------------- animation --
    _bat_clips(rig)
    return rig


def _q(axis, angle):
    return tuple(Quaternion(axis, angle))


def _bat_clips(rig):
    """idle: 60 frames, two wing beats; fall_loop: 30 frames of flailing."""
    T, beats = 60, 2
    Z = Vector((0, 0, 1))
    X = Vector((1, 0, 0))

    def wave(f, amp, phase, cycles=beats, period=T, off=0.0):
        return off + amp * math.sin(TAU * cycles * f / period + phase)

    frames = list(range(0, T + 1, 3))
    for side, s in (("L", 1), ("R", -1)):
        # rotation about the bone's local Z (= world -Y): positive lifts the
        # left (+X) wing, so the right wing takes the negated angle.
        def chain(bone, amp, phase, off=0.0, curl_amp=0.0, curl_phase=0.0, clip="idle", fr=frames, period=T, cycles=beats):
            keys = []
            for f in fr:
                qa = Quaternion(Z, s * wave(f, amp, phase, cycles, period, off))
                if curl_amp:
                    qa = qa @ Quaternion(X, wave(f, curl_amp, curl_phase, cycles, period))
                keys.append((f, tuple(qa)))
            key(rig, clip, 'pose.bones["%s.%s"].rotation_quaternion' % (bone, side), keys)
        chain("upperarm", 0.7, 0.0, off=-0.06)
        chain("forearm", 0.3, -0.9, off=-0.05)
        chain("f2_1", 0.12, -1.3, curl_amp=0.1, curl_phase=-1.5)
        chain("f3_1", 0.22, -1.3, off=0.05, curl_amp=0.15, curl_phase=-1.5)
        chain("f4_1", 0.3, -1.3, off=0.08, curl_amp=0.15, curl_phase=-1.5)
        chain("f2_2", 0.1, -1.7)
        chain("f3_2", 0.14, -1.7)
        chain("f4_2", 0.16, -1.7)
        # ears twitch once, legs dangle
        key(rig, "idle", 'pose.bones["ear.%s"].rotation_quaternion' % side,
            [(0, _q(Z, 0)), (34, _q(Z, 0)), (37, _q(X, 0.35 if side == "L" else 0.05)), (41, _q(X, -0.1)), (45, _q(Z, 0)), (T, _q(Z, 0))])
        key(rig, "idle", 'pose.bones["leg.%s"].rotation_quaternion' % side,
            [(f, tuple(Quaternion(X, wave(f, 0.18, -2.2 + (0.4 if s > 0 else 0)))) ) for f in frames])
        # fall: wings thrown up and flailing, legs kicking
        ff = list(range(0, 31, 3))
        chain("upperarm", 0.35, 0.0, off=0.75, clip="fall_loop", fr=ff, period=30, cycles=2)
        chain("forearm", 0.4, -1.0, off=0.2, clip="fall_loop", fr=ff, period=30, cycles=2)
        for fn in ("f2_1", "f3_1", "f4_1"):
            chain(fn, 0.25, -1.6, off=-0.25, clip="fall_loop", fr=ff, period=30, cycles=2)
        key(rig, "fall_loop", 'pose.bones["leg.%s"].rotation_quaternion' % side,
            [(f, tuple(Quaternion(X, wave(f, 0.5, s * 1.5, 3, 30)))) for f in ff])
    # body bob (the beat lifts it), head counter-nod
    key(rig, "idle", 'pose.bones["root"].location', [(f, (0, wave(f, 0.12, 1.7), 0)) for f in frames])
    key(rig, "idle", 'pose.bones["head"].rotation_quaternion', [(f, tuple(Quaternion(X, wave(f, 0.06, 2.4)))) for f in frames])
    key(rig, "idle", 'pose.bones["blink"].scale', [(0, (1, 1, 1)), (46, (1, 1, 1)), (48, (1, 0.12, 1)), (50, (1, 0.12, 1)), (53, (1, 1, 1)), (T, (1, 1, 1))])
    key(rig, "fall_loop", 'pose.bones["root"].rotation_quaternion', [(f, tuple(Quaternion(Vector((0, 1, 0)), wave(f, 0.12, 0.0, 1, 30)))) for f in range(0, 31, 3)])
    key(rig, "fall_loop", 'pose.bones["head"].rotation_quaternion', [(f, tuple(Quaternion(X, wave(f, 0.2, 0.5, 2, 30)))) for f in range(0, 31, 3)])
