# Builders for BombFall's pushable furniture and casino/arcade machines.
#
# Each builder makes one prop at the origin (bottom centre on the floor, front
# facing -Y; the painting is centred) and is called from a tiny per-asset
# script, so every model keeps its own .glb:
#     blender -b --python blender/toilet.py -- --preview blender/previews
# Set FURN_SHOTS=<dir> to also render a front (game-like), three-quarter and
# side close-up of the model into <dir>/<name>_{game,three,side}.png.
#
# The props are the game's cartoon scale (a toilet is 2.7 m tall next to the
# 1.5 m hero), so each one is modelled from real dimensions times a scale
# factor S and keeps the footprint listed in src/world/spawn_registry.gd.
# Collision shapes live in tools/gen_prop_scenes.py (simple props) or in the
# hand-written .tscn files (desktop, statue, painting, slot machine, ...).
import math
import os
import random

import bmesh
import bpy
import mathutils
from mathutils import Vector

import common
from common import *  # noqa: F401,F403

V = Vector
TAU = math.tau

# ------------------------------------------------------------------ materials
# Every material is a pbr() preset; `edge` is scaled up because the props are
# 2-3x life size and a 1 cm rounded edge would vanish.
PORCELAIN = pbr("ceramic", (0.86, 0.88, 0.92), edge=0.02, name="porcelain")
CHROME_M = pbr("chrome", (0.80, 0.82, 0.86), edge=0.01, name="chrome")
GOLD_M = pbr("gold", (0.95, 0.66, 0.24), edge=0.01, name="gold")
BLACK_GLASS = pbr("plastic", (0.012, 0.012, 0.018), rough=0.06, wear=0.0, grime=0.1, bump=0.0, name="black_glass")
RUBBER_M = pbr("rubber", (0.02, 0.02, 0.025), name="rubber")
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_SERIF = "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf"


def mats_reset():
    """clean_scene() empties the material cache; rebuild the shared presets."""
    global PORCELAIN, CHROME_M, GOLD_M, BLACK_GLASS, RUBBER_M
    PORCELAIN = pbr("ceramic", (0.86, 0.88, 0.92), edge=0.02, name="porcelain")
    CHROME_M = pbr("chrome", (0.80, 0.82, 0.86), edge=0.01, name="chrome")
    GOLD_M = pbr("gold", (0.95, 0.66, 0.24), edge=0.01, name="gold")
    BLACK_GLASS = pbr("plastic", (0.012, 0.012, 0.018), rough=0.06, wear=0.0, grime=0.1, bump=0.0, name="black_glass")
    RUBBER_M = pbr("rubber", (0.02, 0.02, 0.025), name="rubber")


def glow(rgb, strength=4.0, base=None):
    return pbr("neon", base or tuple(c * 0.25 for c in rgb), emit=rgb, strength=strength)


def anim_m(rgb, kind, strength=2.0):
    """An emissive material the game swaps for its animated shader
    ("screen": scanlines, "marquee": chasing dots). See common.anim()."""
    return pbr("screen", tuple(c * 0.2 for c in rgb), emit=rgb, strength=strength, name="anim_" + kind)


# ------------------------------------------------------------ mesh helpers --
def attach(child, parent):
    """common.attach() reads the parent's matrix_world, which is stale until
    the depsgraph updates (no operator has run since the pivot was made), so
    refresh it first. Shadows the kit's version for this module."""
    bpy.context.view_layer.update()
    return common.attach(child, parent)


def _obj(name, bm, m, smooth=True, bevel=0.0, parent=None, angle=40.0, loc=None):
    me = bpy.data.meshes.new(name)
    bm.normal_update()
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    common._link(o)
    if loc is not None:
        o.location = loc
    bpy.context.view_layer.objects.active = o
    o = common._finish(o, m, bevel, smooth, None, None, smooth_angle=angle)
    if parent is not None:
        attach(o, parent)
    return o


def _ring_faces(bm, rings, closed=True, cap0=False, cap1=False):
    """Bridge consecutive vertex rings with quads; optionally cap the ends."""
    n = len(rings[0])
    for a, b in zip(rings, rings[1:]):
        for i in range(n if closed else n - 1):
            j = (i + 1) % n
            if a[i] is b[i]:
                continue
            quad = [a[i], a[j], b[j], b[i]]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                try:
                    bm.faces.new(uniq)
                except ValueError:
                    pass
    if cap0 and len(set(rings[0])) > 2:
        bm.faces.new(list(reversed(rings[0])))
    if cap1 and len(set(rings[-1])) > 2:
        bm.faces.new(rings[-1])


def lathe(profile, m, loc=(0, 0, 0), segs=24, scale=(1.0, 1.0), rot=(0, 0, 0), name="lathe",
          smooth=True, parent=None, angle=60.0, cap=True):
    """Revolve a (radius, z) profile around Z (bottom to top). A radius of 0
    makes a pole; open ends are capped flat unless cap=False."""
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r <= 1e-6:
            v = bm.verts.new((0, 0, z))
            rings.append([v] * segs)
        else:
            rings.append([bm.verts.new((math.cos(TAU * i / segs) * r * scale[0], math.sin(TAU * i / segs) * r * scale[1], z))
                          for i in range(segs)])
    _ring_faces(bm, rings, cap0=cap and profile[0][0] > 1e-6, cap1=cap and profile[-1][0] > 1e-6)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _obj(name, bm, m, smooth=smooth, parent=None, angle=angle)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        attach(o, parent)
    return o


def loft(rings, m, closed=True, cap0=True, cap1=True, name="loft", smooth=True, parent=None, angle=60.0, bevel=0.0):
    """Skin a list of point rings (each a list of 3D points, same count)."""
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    _ring_faces(bm, vr, closed=closed, cap0=cap0, cap1=cap1)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(name, bm, m, smooth=smooth, parent=parent, angle=angle, bevel=bevel)


def superellipse(a, b, n=4.0, segs=32, cx=0.0, cy=0.0, z=0.0, b_back=None, start=0.0):
    """Points of a superellipse |x/a|^n + |y/b|^n = 1 (n=2 ellipse, big n
    rounded rectangle). b_back gives the +Y half its own radius (egg shapes)."""
    pts = []
    for i in range(segs):
        t = start + TAU * i / segs
        c, s = math.cos(t), math.sin(t)
        x = a * math.copysign(abs(c) ** (2.0 / n), c)
        bb = b_back if (b_back is not None and s > 0) else b
        y = bb * math.copysign(abs(s) ** (2.0 / n), s)
        pts.append((cx + x, cy + y, z))
    return pts


def sweep(profile, path, m, closed=True, plane_normal=(0, 0, 1), name="sweep", smooth=True, parent=None, angle=50.0,
          closed_profile=True):
    """Sweep a 2D profile [(u, v)] along a planar path. u points away from the
    path's inside (left of travel when looking down plane_normal), v along
    plane_normal. Corners are mitred."""
    pn = V(plane_normal).normalized()
    P = [V(p) for p in path]
    n = len(P)
    rings = []
    for i in range(n):
        if closed:
            a, b = P[i - 1], P[(i + 1) % n]
            e_in = (P[i] - P[i - 1]).normalized()
            e_out = (P[(i + 1) % n] - P[i]).normalized()
        else:
            a = P[max(i - 1, 0)]
            b = P[min(i + 1, n - 1)]
            e_in = (P[i] - a).normalized() if i > 0 else (b - P[i]).normalized()
            e_out = (b - P[i]).normalized() if i < n - 1 else e_in
        t = (e_in + e_out).normalized()
        nrm = t.cross(pn).normalized()
        edge_n = e_in.cross(pn).normalized()
        k = 1.0 / max(0.3, nrm.dot(edge_n))
        rings.append([P[i] + nrm * (u * k) + pn * v for u, v in profile])
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in r] for r in rings]
    if closed:
        vr.append(vr[0])
    # bridge along the path; profile ring closed or open
    for ra, rb in zip(vr, vr[1:]):
        cnt = len(profile)
        for j in range(cnt if closed_profile else cnt - 1):
            k2 = (j + 1) % cnt
            try:
                bm.faces.new([ra[j], ra[k2], rb[k2], rb[j]])
            except ValueError:
                pass
    if not closed and closed_profile:
        bm.faces.new(list(reversed(vr[0])))
        bm.faces.new(vr[-1])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(name, bm, m, smooth=smooth, parent=parent, angle=angle)


def soft_box(size, loc, m, r=0.25, puff=0.0, pinch=0.0, cuts=4, rot=(0, 0, 0), name="soft", parent=None,
             sag=0.0, taper=0.0):
    """A rounded, optionally puffy box (cushions, mattresses, pillows).
    r: corner radius as a fraction of the smallest half-size (0..1)
    puff: top/bottom bulge (fraction of the height) towards the centre
    pinch: thins the corners (pillow ears)
    sag: the middle of the top dips (a sat-in seat)
    taper: the top face is narrower in X by this fraction"""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=2.0)
    bmesh.ops.subdivide_edges(bm, edges=bm.edges[:], cuts=cuts, use_grid_fill=True)
    hx, hy, hz = size[0] / 2.0, size[1] / 2.0, size[2] / 2.0
    rad = r * min(hx, hy, hz)
    for v in bm.verts:
        p = V((v.co.x * hx, v.co.y * hy, v.co.z * hz))
        q = V((max(-hx + rad, min(hx - rad, p.x)), max(-hy + rad, min(hy - rad, p.y)), max(-hz + rad, min(hz - rad, p.z))))
        d = p - q
        if d.length > 1e-9:
            p = q + d.normalized() * rad
        u, w = v.co.x, v.co.y
        bulge = (1 - u * u) * (1 - w * w)
        p.z *= 1.0 + puff * bulge - pinch * (u * u) * (w * w)
        if sag and v.co.z > 0:
            p.z -= sag * hz * bulge
        if taper:
            p.x *= 1.0 - taper * (v.co.z * 0.5 + 0.5)
        v.co = p
    o = _obj(name, bm, m, smooth=True, angle=80.0)
    o.location = loc
    o.rotation_euler = rot
    if parent is not None:
        attach(o, parent)
    return o


def text(s, size, loc, m, extrude=0.02, rot=(math.pi / 2, 0, 0), font=FONT, align="CENTER", name="text",
         parent=None, res=3, spacing=1.0):
    """Extruded text converted to a mesh, standing up and facing -Y by default."""
    bpy.ops.object.text_add(location=loc, rotation=rot)
    t = bpy.context.object
    t.data.body = s
    t.data.size = size
    t.data.extrude = extrude
    t.data.align_x = align
    t.data.align_y = "CENTER"
    t.data.resolution_u = res
    t.data.space_character = spacing
    t.data.font = bpy.data.fonts.load(font, check_existing=True)
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.name = name
    o.data.materials.clear()
    o.data.materials.append(common.mat(m))
    if parent is not None:
        attach(o, parent)
    return o


def arc_points(c, r, a0, a1, n, plane="XZ"):
    out = []
    for i in range(n + 1):
        a = a0 + (a1 - a0) * i / n
        if plane == "XZ":
            out.append((c[0] + math.cos(a) * r, c[1], c[2] + math.sin(a) * r))
        else:
            out.append((c[0] + math.cos(a) * r, c[1] + math.sin(a) * r, c[2]))
    return out


def tube(points, r, m, verts=8, closed=False, name="tube", parent=None, smooth=True):
    """A round tube along a 3D polyline (pipes, cables, drips, bed rails)."""
    P = [V(p) for p in points]
    n = len(P)
    rings = []
    prev_nrm = None
    for i in range(n):
        if closed:
            t = (P[(i + 1) % n] - P[i - 1]).normalized()
        else:
            t = (P[min(i + 1, n - 1)] - P[max(i - 1, 0)]).normalized()
        if prev_nrm is None:
            ref = V((0, 0, 1)) if abs(t.z) < 0.9 else V((1, 0, 0))
            nrm = t.cross(ref).normalized()
        else:
            nrm = (prev_nrm - t * prev_nrm.dot(t)).normalized()
        prev_nrm = nrm
        bi = t.cross(nrm)
        rr = r(i / max(1, n - 1)) if callable(r) else r
        rings.append([P[i] + (nrm * math.cos(TAU * k / verts) + bi * math.sin(TAU * k / verts)) * rr for k in range(verts)])
    if closed:
        rings.append(rings[0])
    bm = bmesh.new()
    vr = [[bm.verts.new(p) for p in ring] for ring in rings]
    if closed:
        vr[-1] = vr[0]
    _ring_faces(bm, vr, cap0=not closed, cap1=not closed)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    return _obj(name, bm, m, smooth=smooth, parent=parent, angle=70.0)


def sheet(fn, nx, ny, m, thick=0.03, name="sheet", parent=None):
    """A cloth sheet: fn(u, v) -> 3D point for u, v in [0, 1], solidified."""
    bm = bmesh.new()
    grid = [[bm.verts.new(fn(i / nx, j / ny)) for i in range(nx + 1)] for j in range(ny + 1)]
    for j in range(ny):
        for i in range(nx):
            bm.faces.new([grid[j][i], grid[j][i + 1], grid[j + 1][i + 1], grid[j + 1][i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _obj(name, bm, m, smooth=True, angle=80.0)
    if thick:
        s = o.modifiers.new("solid", "SOLIDIFY")
        s.thickness = thick
        s.offset = -1.0
    if parent is not None:
        attach(o, parent)
    return o


def join_under(objs, name, parent=None):
    """Join meshes into one object and (re)parent it under a pivot."""
    o = join(objs, name)
    if parent is not None:
        o.parent = None
        o.matrix_parent_inverse.identity()
        attach(o, parent)
    return o


_LATER = []
_SCALE = [1.0]


def later(fn, *a, **k):
    """Queue an animation call until the model has been placed (scaled and
    turned) by place(), so keys use the final transforms."""
    _LATER.append((fn, a, k))


def run_later():
    while _LATER:
        fn, a, k = _LATER.pop(0)
        fn(*a, **k)


def place(scale=1.0, yaw=0.0):
    """Scale about the origin and turn about Z every top-level object, then
    apply the scale to static meshes and run the queued animation calls."""
    bpy.context.view_layer.update()
    M = mathutils.Matrix.Rotation(yaw, 4, "Z") @ mathutils.Matrix.Scale(scale, 4)
    tops = [o for o in bpy.context.scene.objects if o.parent is None]
    for o in tops:
        o.matrix_world = M @ o.matrix_world
    bpy.context.view_layer.update()
    for o in tops:
        if o.type == "MESH" and not o.children:
            bpy.ops.object.select_all(action="DESELECT")
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    _SCALE[0] = scale
    run_later()


# ------------------------------------------------------------- animation --
def flicker(p, clip="idle", seconds=2.0, amount=0.25, seed=1, base=1.0, sway=0.0):
    """A candle-flame flicker on a pivot: irregular scale jitter (taller and
    thinner in turns) plus an optional sideways lean, seamless over the clip."""
    rnd = random.Random(seed)
    end = int(round(seconds * 30))
    base = base * p.scale.x
    step = 3
    frames = list(range(0, end, step)) + [end]
    vals = []
    for f in frames[:-1]:
        k = rnd.uniform(-1, 1)
        vals.append((f, (base * (1 - 0.4 * amount * k), base * (1 - 0.4 * amount * k), base * (1 + amount * k))))
    vals.append((end, vals[0][1]))
    key(p, clip, "scale", vals)
    if sway:
        rv = [(f, rnd.uniform(-sway, sway)) for f in frames[:-1]]
        rv.append((end, rv[0][1]))
        key(p, clip, "rotation_euler", rv, index=1)


def rise(p, dz, clip="idle", seconds=2.0, phase=0.0, size=1.0, drift=0.0):
    """A bubble on a pivot looping from its place up by dz (grows in, shrinks
    out). dz and drift are in model units before place() scaled it."""
    end = int(round(seconds * 30))
    z0 = p.location.z
    z1 = z0 + dz * _SCALE[0]
    drift *= _SCALE[0]
    size *= p.scale.x
    x0 = p.location.x
    pts = []
    for s in range(13):
        u = (phase + s / 12.0) % 1.0
        pts.append((s / 12.0 * end, u))
    loc_keys, scl_keys = [], []
    for i, (f, u) in enumerate(pts):
        # insert a wrap point so the jump from top to bottom takes one frame
        if i > 0 and u < pts[i - 1][1]:
            fw = pts[i - 1][0] + (1.0 - pts[i - 1][1]) / (u + 1.0 - pts[i - 1][1]) * (f - pts[i - 1][0])
            loc_keys.append((fw - 0.01, (x0, p.location.y, z1)))
            scl_keys.append((fw - 0.01, (0.0, 0.0, 0.0)))
            loc_keys.append((fw + 0.01, (x0, p.location.y, z0)))
            scl_keys.append((fw + 0.01, (0.0, 0.0, 0.0)))
        z = z0 + (z1 - z0) * u
        sc = size * min(1.0, u * 6.0) * min(1.0, (1.0 - u) * 5.0)
        loc_keys.append((f, (x0 + drift * math.sin(u * TAU * 1.5), p.location.y, z)))
        scl_keys.append((f, (sc, sc, sc)))
    key(p, clip, "location", loc_keys, interp="LINEAR")
    key(p, clip, "scale", scl_keys, interp="LINEAR")


def pulse(p, clip="idle", seconds=2.0, lo=0.7, hi=1.2, phase=0.0):
    """A breathing scale loop on a pivot (LEDs, glowing buttons)."""
    end = int(round(seconds * 30))
    s0 = p.scale.x
    keys = []
    for s in range(9):
        k = 0.5 + 0.5 * math.sin(TAU * s / 8 + phase)
        v = (lo + (hi - lo) * k) * s0
        keys.append((end * s / 8, (v, v, v)))
    key(p, clip, "scale", keys)


# ---------------------------------------------------------------- shots --
def shots(name, out_dir=None, size=440, samples=36, offsets=None):
    """Product shots after export: a near-orthographic front view like the
    game camera, a three-quarter view and a side view, lit like a neon
    hotel room. `offsets` moves named objects first (multi-body pieces are
    authored around their body's origin)."""
    out_dir = out_dir or os.environ.get("FURN_SHOTS")
    if not out_dir:
        return
    os.makedirs(out_dir, exist_ok=True)
    for oname, off in (offsets or {}).items():
        o = bpy.data.objects.get(oname)
        if o is not None:
            o.location = V(o.location) + V(off)
    bpy.context.view_layer.update()
    lo, hi = scene_bounds()
    centre = (lo + hi) / 2.0
    radius = max((hi - lo).length / 2.0, 0.3)
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    scn.cycles.use_denoising = False
    scn.render.resolution_x = size
    scn.render.resolution_y = size
    scn.view_settings.view_transform = "Filmic" if "Filmic" in [v.identifier for v in scn.view_settings.bl_rna.properties["view_transform"].enum_items] else scn.view_settings.view_transform
    scn.world = scn.world or bpy.data.worlds.new("w")
    scn.world.use_nodes = True
    scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.035, 0.02, 0.055, 1.0)
    scn.world.node_tree.nodes["Background"].inputs[1].default_value = 1.0
    fm = bpy.data.materials.new("_floor")
    fm.use_nodes = True
    b = fm.node_tree.nodes["Principled BSDF"]
    b.inputs["Base Color"].default_value = (0.05, 0.03, 0.07, 1)
    b.inputs["Roughness"].default_value = 0.35
    bpy.ops.mesh.primitive_plane_add(size=radius * 12, location=(centre.x, centre.y, lo.z - 0.002))
    fl = bpy.context.object
    fl.name = "_shot_floor"
    fl.data.materials.append(fm)
    bpy.ops.mesh.primitive_plane_add(size=radius * 12, location=(centre.x, hi.y + radius * 1.2, lo.z), rotation=(math.pi / 2, 0, 0))
    wl = bpy.context.object
    wl.name = "_shot_wall"
    wl.data.materials.append(fm)
    for (pos, colour, energy, soft) in (
        ((0.9, -1.4, 1.5), (1.0, 0.93, 0.88), 1800, 0.6),
        ((-1.6, -0.5, 0.6), (0.35, 0.8, 1.0), 500, 0.3),
        ((0.6, 1.3, 1.2), (1.0, 0.3, 0.8), 700, 0.3),
        ((0.0, -1.3, 0.2), (0.7, 0.45, 1.0), 200, 0.8),
    ):
        ld = bpy.data.lights.new("_shot_light", "POINT")
        ld.energy = energy * radius * radius
        ld.color = colour
        ld.shadow_soft_size = radius * soft
        lo_ = bpy.data.objects.new("_shot_light", ld)
        common._link(lo_)
        lo_.location = centre + V(pos) * radius * 2.2
    cam_data = bpy.data.cameras.new("_shot_cam")
    cam = bpy.data.objects.new("_shot_cam", cam_data)
    common._link(cam)
    scn.camera = cam
    views = {
        "game": ((0.0, -1.0, 0.12), 160, 3.0),
        "three": ((0.8, -1.0, 0.5), 50, 1.0),
        "side": ((-1.0, -0.35, 0.25), 60, 1.15),
    }
    for vname, (d, lens, dist_k) in views.items():
        cam_data.lens = lens
        # distance so the bounding sphere fills the frame
        fov = 2 * math.atan(18.0 / lens)
        dist = radius / math.tan(fov / 2) * 1.08
        dvec = V(d).normalized()
        cam.location = centre + dvec * dist
        cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
        cam_data.clip_end = dist * 4
        scn.render.filepath = os.path.join(out_dir, "%s_%s.png" % (name, vname))
        bpy.ops.render.render(write_still=True)
    print("SHOTS %s -> %s" % (name, out_dir))


def finish(name, keep=(), tex=None, offsets=None, ao_distance=None):
    """Join the static parts, bake, export and render the product shots."""
    run_later()
    # Small parts do not need two-segment bevels (a 108-triangle cube).
    for o in all_meshes():
        for md in o.modifiers:
            if md.type == "BEVEL" and max(o.dimensions) < 0.45:
                md.segments = 1
    if os.environ.get("FURN_TRIS"):
        dg = bpy.context.evaluated_depsgraph_get()
        rows = []
        for o in all_meshes():
            me = o.evaluated_get(dg).to_mesh()
            rows.append((sum(len(p.vertices) - 2 for p in me.polygons), o.name))
        for n, on in sorted(rows, reverse=True)[:12]:
            print("OBJTRIS %6d %s" % (n, on))
    join_static("body", keep=keep)
    export(name, tex=tex, ao_distance=ao_distance)
    shots(name, offsets=offsets)
    tris = 0
    for o in all_meshes():
        if o.name.startswith("_"):
            continue
        me = o.evaluated_get(bpy.context.evaluated_depsgraph_get()).to_mesh()
        tris += sum(len(p.vertices) - 2 for p in me.polygons)
    print("TRIS %s %d" % (name, tris))
    for o in all_meshes():
        if o.name.startswith("_"):
            continue
        ws = [o.matrix_world @ V(c) for c in o.bound_box]
        print("BOUNDS %s %-12s x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (name, o.name, min(w.x for w in ws), max(w.x for w in ws),
              min(w.y for w in ws), max(w.y for w in ws), min(w.z for w in ws), max(w.z for w in ws)))


# ================================================================= toilet ==
def _egg(a, bf, bb, z, cy=0.0, n=2.6, segs=24):
    return superellipse(a, bf, n=n, segs=segs, cy=cy, z=z, b_back=bb, start=-math.pi / 2)


def toilet():
    """A glazed porcelain smart toilet at 2.3x life size: elongated bowl,
    white seat with the lid up on chrome hinges, a tall porcelain cistern
    with a black-glass control panel (display, glowing buttons, chrome dual
    flush plate), a chrome flush lever, a paper roll and a neon underglow.
    Turned 30 degrees so the camera sees into the bowl. ~1.9 x 2.7 m."""
    mats_reset()
    seat_m = pbr("plastic", (0.90, 0.90, 0.92), rough=0.25, wear=0.1, grime=0.2, edge=0.015, name="seat")
    water_m = pbr("glass", (0.55, 0.85, 1.0), alpha=0.55, name="water")
    paper_m = pbr("fabric", (0.92, 0.92, 0.9), bump=0.3, name="paper")
    # Bowl: one lofted porcelain shell, outside up to the rim, then down inside.
    outer = [
        (0.30, 0.40, 0.40, 0.00, 0.05),
        (0.30, 0.40, 0.40, 0.04, 0.05),
        (0.27, 0.36, 0.38, 0.30, 0.04),
        (0.36, 0.60, 0.40, 0.62, -0.08),
        (0.44, 0.72, 0.42, 0.84, -0.14),
        (0.445, 0.73, 0.425, 0.89, -0.14),
        (0.43, 0.71, 0.41, 0.92, -0.14),
    ]
    inner = [
        (0.36, 0.62, 0.33, 0.925, -0.14),
        (0.33, 0.57, 0.30, 0.86, -0.14),
        (0.22, 0.40, 0.20, 0.64, -0.12),
        (0.12, 0.20, 0.12, 0.50, -0.06),
    ]
    rings = [_egg(a, bf, bb, z, cy) for a, bf, bb, z, cy in outer + inner]
    loft(rings, PORCELAIN, cap0=True, cap1=True, name="bowl")
    water = loft([_egg(0.235, 0.42, 0.21, 0.63, -0.12)], water_m, cap0=True, cap1=False, name="water")
    water.location.z += 0.0
    # Seat ring and hinges.
    seat = []
    for dz, grow in ((0.925, 0.0), (0.955, 0.012), (0.985, 0.0)):
        seat.append(_egg(0.35 - grow, 0.60 - grow, 0.30 - grow, dz, -0.14))
    seat_out = []
    for dz, grow in ((0.985, 0.0), (0.955, 0.012), (0.925, 0.0)):
        seat_out.append(_egg(0.445 + grow, 0.735 + grow, 0.41 + grow, dz, -0.14))
    loft(seat + seat_out + [seat[0]], seat_m, cap0=False, cap1=False, name="seat")
    for sx in (-1, 1):
        cyl(0.045, 0.14, (sx * 0.2, 0.29, 0.975), CHROME_M, rot=(0, math.pi / 2, 0), verts=12)
        cube((0.1, 0.12, 0.04), (sx * 0.2, 0.33, 0.93), CHROME_M, bevel=0.012)
    # Lid, raised against the cistern.
    lid_rings = [
        _egg(0.425, 0.71, 0.40, 0.0, 0.0),
        _egg(0.445, 0.73, 0.415, 0.025, 0.0),
        _egg(0.43, 0.715, 0.40, 0.06, 0.0),
        _egg(0.36, 0.60, 0.33, 0.075, 0.0),
    ]
    lid = loft(lid_rings, seat_m, name="lid")
    lid.rotation_euler = (-math.radians(99), 0, 0)
    lid.location = (0, 0.25, 0.99 + 0.415)
    # Cistern: glazed tank with a porcelain cap.
    TY = 0.54
    soft_box((0.94, 0.44, 1.02), (0, TY, 0.90 + 0.51), PORCELAIN, r=0.3, cuts=3, name="tank")
    soft_box((1.0, 0.5, 0.13), (0, TY, 1.98), PORCELAIN, r=0.5, cuts=2, name="tank_cap")
    # Dual flush buttons on top of the cap.
    cyl(0.13, 0.03, (0, TY, 2.05), CHROME_M, verts=24)
    for sx in (-1, 1):
        cube((0.1, 0.18, 0.03), (sx * 0.057, TY, 2.07), pbr("chrome", (0.9, 0.9, 0.92), rough=0.2, name="chrome_satin"), bevel=0.01)
    # Black glass smart panel on two chrome posts: display, glowing buttons.
    PY = TY + 0.1
    PZ = 2.33
    soft_box((0.8, 0.1, 0.46), (0, PY, PZ), BLACK_GLASS, r=0.35, cuts=2, name="panel")
    soft_box((0.84, 0.08, 0.5), (0, PY + 0.03, PZ), CHROME_M, r=0.3, cuts=1, name="bezel")
    cube((0.46, 0.012, 0.16), (0, PY - 0.053, PZ + 0.09), anim_m((0.25, 0.8, 1.0), "screen", 2.0), bevel=0.0, name="display")
    text("26\u00b0", 0.08, (-0.1, PY - 0.063, PZ + 0.09), glow((0.9, 1.0, 1.0), 3.0), extrude=0.003)
    sphere(0.028, (0.13, PY - 0.06, PZ + 0.09), glow((1.0, 0.5, 0.8), 4.0), segments=8, rings=6)
    for i, (col, x) in enumerate(((PINK, -0.2), (CYAN, 0.0), (GREEN, 0.2))):
        cyl(0.056, 0.02, (x, PY - 0.052, PZ - 0.1), CHROME_M, rot=(math.pi / 2, 0, 0), verts=16)
        p = pivot("led_%d" % i, (x, PY - 0.064, PZ - 0.1))
        cyl(0.04, 0.012, (x, PY - 0.064, PZ - 0.1), glow(col, 5.0), rot=(math.pi / 2, 0, 0), verts=16, parent=p)
        later(pulse, p, lo=0.75, hi=1.1, phase=i * 2.1)
    for sx in (-1, 1):
        cyl(0.03, 0.12, (sx * 0.28, PY + 0.02, 2.08), CHROME_M, verts=10)   # panel posts
    # Chrome flush lever on the tank's front-left corner.
    cyl(0.06, 0.05, (-0.34, TY - 0.23, 1.78), CHROME_M, rot=(math.pi / 2, 0, 0), verts=16)
    rod((-0.34, TY - 0.25, 1.78), (-0.12, TY - 0.28, 1.74), 0.025, CHROME_M, verts=10)
    sphere(0.036, (-0.11, TY - 0.28, 1.74), CHROME_M, segments=12, rings=8)
    # Paper roll on a chrome arm on the right of the tank.
    cube((0.05, 0.2, 0.08), (0.49, TY - 0.02, 1.52), CHROME_M, bevel=0.015)
    rod((0.49, TY - 0.08, 1.52), (0.49, TY - 0.24, 1.52), 0.02, CHROME_M, verts=8)
    roll = cyl(0.14, 0.22, (0.52, TY - 0.14, 1.40), paper_m, verts=20)
    roll.rotation_euler = (0, math.pi / 2, 0)
    cyl(0.045, 0.23, (0.52, TY - 0.14, 1.40), pbr("plastic", (0.4, 0.3, 0.2), name="card"), verts=12).rotation_euler = (0, math.pi / 2, 0)
    # Neon underglow around the foot.
    torus(1.0, 0.018, (0, 0.05, 0.02), glow(CYAN, 4.0), scale=(0.315, 0.415, 1.0), major_segments=32, minor_segments=6)
    place(1.07, math.radians(-30))


# ================================================================ bathtub ==
def _claw_foot(x, y, top_z, m):
    """A cast claw-and-ball foot under a tub corner, pointing outwards."""
    out = V((x, y, 0)).normalized()
    ball = V((x, y, 0)) + out * 0.08
    parts = [sphere(0.13, (ball.x, ball.y, 0.13), m, segments=14, rings=8)]
    side = V((-out.y, out.x, 0))
    for k in (-1, 0, 1):
        d = (out * 0.9 + side * 0.55 * k).normalized()
        base = ball + d * 0.02
        pts = [base + V((0, 0, 0.26)), base + d * 0.12 + V((0, 0, 0.2)), base + d * 0.16 + V((0, 0, 0.08)), base + d * 0.13 + V((0, 0, 0.0))]
        parts.append(tube(pts, lambda t: 0.05 - 0.03 * t, m, verts=5))
    leg = [ball + V((0, 0, 0.22)), ball + V((0, 0, 0.34)) - out * 0.02, V((x, y, top_z - 0.05)) - out * 0.12, V((x, y, top_z)) - out * 0.2]
    parts.append(tube(leg, lambda t: 0.085 + 0.07 * t, m, verts=10))
    parts.append(sphere(0.2, tuple(V((x, y, top_z + 0.02)) - out * 0.22), m, scale=(1.0, 1.0, 0.45), segments=12, rings=6))
    return parts


def bathtub():
    """A roll-top clawfoot tub at 3.3x life size: plum lacquered cast-iron
    shell, porcelain rim and bowl, gold claw feet, a chrome telephone mixer,
    bubble-bath foam, a rubber duck and a candle on a wooden caddy.
    Idle: foam bobs, bubbles rise, the duck rocks, the candle flickers.
    ~5.8 x 2.25 x 2.3 m."""
    mats_reset()
    enamel = pbr("paint", (0.07, 0.025, 0.11), rough=0.16, wear=0.2, grime=0.25, edge=0.03, name="enamel")
    water_m = pbr("glass", (0.35, 0.75, 0.95), alpha=0.6, name="water")
    foam_m = pbr("plastic", (0.95, 0.95, 0.98), rough=0.5, wear=0.0, grime=0.15, bump=0.5, name="foam")
    bubble_m = pbr("glass", (0.85, 0.95, 1.0), alpha=0.35, name="bubble")
    wood_m = pbr("wood", (0.30, 0.15, 0.07), color2=(0.16, 0.07, 0.03), edge=0.012, name="teak")
    duck_m = pbr("plastic", (1.0, 0.78, 0.05), rough=0.3, wear=0.0, name="duck")
    beak_m = pbr("plastic", (1.0, 0.35, 0.02), rough=0.35, wear=0.0, name="beak")
    wax_m = pbr("plastic", (0.95, 0.9, 0.82), rough=0.5, wear=0.0, name="wax")
    SEG = 32

    def ring(a, b, z, n=3.0):
        return superellipse(a, b, n=n, segs=SEG, z=z)

    outer = [ring(2.05, 0.66, 0.34), ring(2.32, 0.82, 0.42), ring(2.62, 0.97, 0.78), ring(2.76, 1.04, 1.26), ring(2.8, 1.06, 1.62)]
    loft(outer, enamel, cap0=True, cap1=False, name="shell")
    rim = [ring(2.8, 1.06, 1.62), ring(2.86, 1.11, 1.69), ring(2.875, 1.125, 1.78), ring(2.84, 1.095, 1.85), ring(2.77, 1.03, 1.86),
           ring(2.71, 0.975, 1.82), ring(2.66, 0.93, 1.74), ring(2.5, 0.82, 1.1), ring(2.2, 0.66, 0.66)]
    loft(rim, PORCELAIN, cap0=False, cap1=True, name="rim")
    tube(ring(2.815, 1.075, 1.625), 0.022, glow(PINK, 5.0), verts=6, closed=True, name="rim_neon")
    loft([ring(2.6, 0.885, 1.56)], water_m, cap0=True, cap1=False, name="water")
    for sx in (-1, 1):
        for sy in (-1, 1):
            _claw_foot(sx * 2.05, sy * 0.62, 0.52, GOLD_M)
    # Foam: a static bank of suds plus a few bobbing blobs.
    rnd = random.Random(7)
    for i in range(24):
        x = -2.2 + (i / 24.0) * 4.3 + rnd.uniform(-0.2, 0.2)
        y = rnd.uniform(-0.62, 0.62) * (1.0 - (abs(x) / 2.6) ** 4) ** 0.5
        r = rnd.uniform(0.16, 0.34)
        if abs(x + 0.8) < 0.3:
            continue
        sphere(r, (x, y, 1.52 + r * 0.55), foam_m, scale=(1.0, 1.0, 0.75), segments=8, rings=5)
    for i, (x, y) in enumerate(((-1.6, 0.35), (0.3, -0.45), (1.5, 0.4))):
        p = pivot("foam_%d" % i, (x, y, 1.5))
        for k in range(3):
            sphere(0.18 + 0.05 * k, (x + 0.15 * (k - 1), y + 0.05 * k, 1.7 + 0.05 * k), foam_m, scale=(1, 1, 0.75), segments=8, rings=5, parent=p)
        wobble(p, "idle", "location", 2, 0.03, seconds=2.0, phase=i * 2.0)
    for i in range(6):
        x = -2.0 + i * 0.8 + rnd.uniform(-0.2, 0.2)
        p = pivot("bubble_%d" % i, (x, rnd.uniform(-0.5, 0.5), 1.62))
        sphere(0.07 + 0.02 * (i % 3), (x, p.location.y, 1.62), bubble_m, segments=10, rings=6, parent=p)
        rise(p, 0.9, phase=i / 6.0, drift=0.08)
    # Rubber duck, rocking on the water.
    DZ = 0.1
    d = pivot("duck", (0.95, -0.35, 1.5 + DZ))
    sphere(0.24, (0.95, -0.35, 1.6 + DZ), duck_m, scale=(1.25, 0.95, 0.75), segments=14, rings=8, parent=d)
    sphere(0.15, (0.78, -0.4, 1.83 + DZ), duck_m, segments=12, rings=8, parent=d)
    cone(0.07, 0.14, (0.64, -0.43, 1.81 + DZ), beak_m, rot=(0, -math.pi / 2, 0.2), verts=8, parent=d)
    for sy in (-1, 1):
        sphere(0.025, (0.7, -0.4 + sy * 0.09, 1.88 + DZ), PLASTIC_BLACK, segments=6, rings=4, parent=d)
    sphere(0.1, (1.2, -0.35, 1.72 + DZ), duck_m, scale=(1.0, 0.8, 0.8), segments=8, rings=6, parent=d)   # tail
    wobble(d, "idle", "rotation_euler", 0, 0.08, seconds=2.0)
    wobble(d, "idle", "location", 2, 0.025, seconds=2.0, phase=1.2)
    # Teak caddy across the tub with a candle.
    cube((0.46, 2.36, 0.06), (-0.8, 0, 1.9), wood_m, bevel=0.015)
    for sx in (-1, 1):
        cube((0.04, 2.3, 0.08), (-0.8 + sx * 0.2, 0, 1.94), wood_m, bevel=0.01)
    lathe([(0.0, 1.93), (0.11, 1.93), (0.11, 2.2), (0.09, 2.21), (0.0, 2.2)], wax_m, segs=14, loc=(-0.8, -0.35, 0))
    cyl(0.008, 0.05, (-0.8, -0.35, 2.23), PLASTIC_BLACK, verts=4)
    f = pivot("flame", (-0.8, -0.35, 2.235))
    lathe([(0.0, 0.0), (0.035, 0.03), (0.04, 0.06), (0.02, 0.11), (0.0, 0.15)], glow((1.0, 0.65, 0.2), 8.0), segs=8, loc=(-0.8, -0.35, 2.235), parent=f)
    flicker(f, seed=3, sway=0.1)
    # Chrome telephone mixer on the +X end.
    TX, TZ = 2.52, 1.84
    for sy in (-1, 1):
        cyl(0.05, 0.28, (TX, sy * 0.3, TZ + 0.14), CHROME_M, verts=12)
        cyl(0.07, 0.04, (TX, sy * 0.3, TZ + 0.02), CHROME_M, verts=14)
        h = (TX, sy * 0.3, TZ + 0.33)
        cyl(0.035, 0.08, h, CHROME_M, verts=10)
        for k in range(4):
            a = k * math.pi / 2 + math.pi / 4
            rod(h, (h[0] + math.cos(a) * 0.13, h[1] + math.sin(a) * 0.13, h[2] + 0.02), 0.018, CHROME_M, verts=6)
            sphere(0.028, (h[0] + math.cos(a) * 0.13, h[1] + math.sin(a) * 0.13, h[2] + 0.02), CHROME_M, segments=8, rings=5)
        cyl(0.04, 0.03, (h[0], h[1], h[2] + 0.05), PORCELAIN, verts=12)
    rod((TX, -0.3, TZ + 0.2), (TX, 0.3, TZ + 0.2), 0.04, CHROME_M, verts=10)
    tube([(TX, 0, TZ + 0.2), (TX, 0, TZ + 0.42), (TX - 0.05, 0, TZ + 0.55), (TX - 0.2, 0, TZ + 0.58), (TX - 0.33, 0, TZ + 0.5), (TX - 0.36, 0, TZ + 0.4)],
         0.04, CHROME_M, verts=10, name="spout")
    # handset on its cradle
    tube([(TX + 0.02, -0.18, TZ + 0.3), (TX + 0.04, -0.1, TZ + 0.36), (TX + 0.04, 0.1, TZ + 0.36), (TX + 0.02, 0.18, TZ + 0.3)], 0.03, CHROME_M, verts=8)
    lathe([(0.0, 0.0), (0.06, 0.0), (0.075, 0.06), (0.0, 0.07)], CHROME_M, segs=12, loc=(TX + 0.02, -0.2, TZ + 0.3), rot=(0.5, 0, 0))
    place(1.0, 0.0)


# ================================================================== chair ==
def _caster(x, y, a, m_body, m_wheel):
    """A twin-wheel office-chair caster under a leg tip, rolling along a."""
    parts = [cyl(0.03, 0.12, (x, y, 0.28), CHROME_M, verts=8)]
    parts.append(soft_box((0.2, 0.14, 0.1), (x, y, 0.2), m_body, r=0.6, cuts=1, rot=(0, 0, a)))
    for s in (-1, 1):
        ox, oy = -math.sin(a) * 0.055 * s, math.cos(a) * 0.055 * s
        w = cyl(0.1, 0.05, (x + ox, y + oy, 0.1), m_wheel, verts=12, bevel=0.0)
        w.rotation_euler = (math.pi / 2, 0, a)
    return parts


def chair():
    """An executive office chair at 2.5x life size: oxblood leather with
    channel-tufted back and a plump seat, chrome armrests and five-star base,
    twin-wheel casters. ~2.0 x 1.8 x 3.0 m, front facing -Y."""
    mats_reset()
    leather = pbr("leather", (0.26, 0.035, 0.06), rough=0.42, wear=0.35, grime=0.35, edge=0.03, name="oxblood")
    leather_dk = pbr("leather", (0.10, 0.02, 0.03), rough=0.5, edge=0.02, name="oxblood_dark")
    plastic = pbr("plastic", (0.02, 0.02, 0.025), rough=0.35, edge=0.015, name="black_abs")
    # Five-star base.
    lathe([(0.0, 0.22), (0.17, 0.22), (0.2, 0.28), (0.17, 0.36), (0.0, 0.38)], CHROME_M, segs=20)
    for i in range(5):
        a = TAU * i / 5 - math.pi / 2
        ca, sa = math.cos(a), math.sin(a)
        tube([(ca * 0.12, sa * 0.12, 0.31), (ca * 0.45, sa * 0.45, 0.3), (ca * 0.78, sa * 0.78, 0.33)],
             lambda t: 0.075 - 0.025 * t, CHROME_M, verts=8)
        cyl(0.06, 0.05, (ca * 0.8, sa * 0.8, 0.33), CHROME_M, verts=10)
        _caster(ca * 0.8, sa * 0.8, a + math.pi / 2, plastic, RUBBER_M)
    # Gas lift with its black shroud, then the tilt mechanism.
    lathe([(0.0, 0.36), (0.1, 0.36), (0.1, 0.62), (0.085, 0.64), (0.0, 0.64)], plastic, segs=16)
    cyl(0.06, 0.42, (0, 0, 0.84), CHROME_M, verts=14)
    soft_box((0.55, 0.6, 0.14), (0, 0.0, 1.1), plastic, r=0.5, cuts=1)
    rod((0.2, -0.1, 1.07), (0.62, -0.25, 1.02), 0.02, CHROME_M, verts=6)
    sphere(0.045, (0.63, -0.25, 1.02), plastic, segments=8, rings=6)
    # Seat: a shell plus a plump cushion with a waterfall front.
    soft_box((1.45, 1.35, 0.14), (0, -0.05, 1.22), leather_dk, r=0.5, cuts=2)
    soft_box((1.4, 1.3, 0.3), (0, -0.07, 1.4), leather, r=0.55, puff=0.18, sag=0.12, cuts=4)
    # Back: a leather frame with channel-quilted bolsters, leaning back.
    t = math.radians(12)
    up = V((0, math.sin(t), math.cos(t)))
    base = V((0, 0.62, 1.55))
    soft_box((1.5, 0.26, 1.66), tuple(base + up * 0.8 + V((0, 0.12, 0))), leather_dk, r=0.8, cuts=2, rot=(-t, 0, 0), name="back_shell")
    for sx in (-1, 1):
        soft_box((0.18, 0.3, 1.58), tuple(base + up * 0.8 + V((sx * 0.64, 0.0, 0))), leather, r=0.95, puff=0.0, cuts=2, rot=(-t, 0, 0))
    h = 0.29
    for i in range(5):
        c = base + up * (0.17 + i * h)
        soft_box((1.14, 0.22, h + 0.01), tuple(c), leather, r=0.75, puff=0.15, cuts=2, rot=(-t, 0, 0))
    soft_box((1.5, 0.3, 0.34), tuple(base + up * 1.6 - V((0, 0.02, 0))), leather, r=0.95, puff=0.1, cuts=2, rot=(-t, 0, 0))   # top roll
    # Chrome spine from the mechanism up the back.
    tube([(0, 0.2, 1.1), (0, 0.55, 1.1), (0, 0.8, 1.35), tuple(base + up * 0.7 + V((0, 0.26, 0)))], 0.06, CHROME_M, verts=8)
    # Armrests: chrome loops with leather pads.
    for sx in (-1, 1):
        x = sx * 0.8
        tube([(sx * 0.3, 0.25, 1.12), (x, 0.3, 1.18), (x, 0.3, 1.55), (x, 0.1, 1.78)], 0.045, CHROME_M, verts=8)
        tube([(sx * 0.3, -0.35, 1.12), (x, -0.4, 1.18), (x, -0.4, 1.7)], 0.045, CHROME_M, verts=8)
        soft_box((0.2, 0.9, 0.1), (x, -0.12, 1.8), leather_dk, r=0.8, cuts=2)
    place(1.0, 0.0)


# ================================================================== table ==
def table():
    """A round dining table at 1.8x life size: Calacatta marble top with a
    bullnose edge on a brass tulip pedestal, laid for two with gold-rimmed
    plates, cutlery, red wine and a three-arm candelabra whose flames
    flicker. 2 m across, the top at 1.35 m (2.1 m with the candles)."""
    mats_reset()
    marble = pbr("marble", (0.86, 0.85, 0.83), color2=(0.45, 0.38, 0.28), edge=0.01, name="calacatta")
    brass = pbr("gold", (0.85, 0.6, 0.28), rough=0.28, name="brass")
    glass_m = pbr("glass", (0.85, 0.9, 1.0), alpha=0.25, name="wine_glass")
    wine_m = pbr("plastic", (0.3, 0.0, 0.03), rough=0.08, wear=0.0, name="wine")
    wax_m = pbr("plastic", (0.95, 0.92, 0.86), rough=0.5, wear=0.0, name="wax")
    napkin_m = pbr("fabric", (0.55, 0.05, 0.25), name="napkin")
    TOP = 1.35
    lathe([(0.0, TOP - 0.09), (0.97, TOP - 0.09), (1.0, TOP - 0.075), (1.012, TOP - 0.045), (1.0, TOP - 0.015), (0.975, TOP), (0.0, TOP)],
          marble, segs=48, name="top")
    lathe([(0.9, TOP - 0.13), (0.93, TOP - 0.13), (0.93, TOP - 0.09), (0.9, TOP - 0.09)], brass, segs=40, cap=False)
    lathe([(0.0, 0.0), (0.62, 0.0), (0.64, 0.02), (0.61, 0.05), (0.4, 0.1), (0.2, 0.2), (0.11, 0.38), (0.095, 0.7), (0.1, 1.0),
           (0.14, 1.12), (0.3, 1.2), (0.34, TOP - 0.1), (0.0, TOP - 0.09)], brass, segs=32, name="pedestal")
    for sx in (-1, 1):
        x = sx * 0.58
        lathe([(0.0, TOP + 0.02), (0.14, TOP + 0.02), (0.22, TOP + 0.04), (0.235, TOP + 0.05), (0.22, TOP + 0.052), (0.13, TOP + 0.03), (0.0, TOP + 0.03)],
              PORCELAIN, segs=28, loc=(x, 0, 0))
        lathe([(0.0, TOP), (0.3, TOP), (0.31, TOP + 0.015), (0.29, TOP + 0.02), (0.0, TOP + 0.01)], GOLD_M, segs=28, loc=(x, 0, 0))
        for k, dy in enumerate((-0.33, 0.33)):
            cube((0.24, 0.035, 0.012), (x, dy, TOP + 0.008), CHROME_M, bevel=0.004)
        # wine glass with wine
        gx, gy = x - sx * 0.05, 0.42
        lathe([(0.0, TOP), (0.08, TOP), (0.075, TOP + 0.01), (0.015, TOP + 0.03), (0.012, TOP + 0.16), (0.05, TOP + 0.2), (0.1, TOP + 0.27),
               (0.095, TOP + 0.36), (0.09, TOP + 0.36), (0.093, TOP + 0.27), (0.048, TOP + 0.21), (0.0, TOP + 0.2)], glass_m, segs=16, loc=(gx, gy, 0))
        lathe([(0.0, TOP + 0.205), (0.05, TOP + 0.215), (0.085, TOP + 0.26), (0.0, TOP + 0.265)], wine_m, segs=14, loc=(gx, gy, 0))
        # folded napkin
        wedge((0.14, 0.2, 0.08), (x + sx * 0.02, -0.02, TOP + 0.09), napkin_m)
    # Three-arm candelabra on a gold trivet.
    lathe([(0.0, TOP), (0.24, TOP), (0.25, TOP + 0.012), (0.23, TOP + 0.016), (0.0, TOP + 0.01)], GOLD_M, segs=28)
    lathe([(0.0, TOP), (0.13, TOP), (0.13, TOP + 0.02), (0.06, TOP + 0.06), (0.03, TOP + 0.12), (0.04, TOP + 0.2), (0.025, TOP + 0.26),
           (0.03, TOP + 0.36), (0.0, TOP + 0.37)], brass, segs=16, name="candelabra")
    cups = [(0.0, 0.0, TOP + 0.42)]
    for sx in (-1, 1):
        tube([(0, 0, TOP + 0.3), (sx * 0.12, 0, TOP + 0.28), (sx * 0.2, 0, TOP + 0.32), (sx * 0.22, 0, TOP + 0.37)], 0.015, brass, verts=6)
        cups.append((sx * 0.22, 0.0, TOP + 0.38))
    for i, (cx, cy, cz) in enumerate(cups):
        lathe([(0.0, cz - 0.04), (0.035, cz - 0.04), (0.05, cz), (0.045, cz + 0.005), (0.0, cz)], brass, segs=12, loc=(cx, cy, 0))
        hgt = 0.26 if i == 0 else 0.22
        lathe([(0.0, cz), (0.03, cz), (0.03, cz + hgt), (0.022, cz + hgt + 0.008), (0.0, cz + hgt)], wax_m, segs=10, loc=(cx, cy, 0))
        f = pivot("flame_%d" % i, (cx, cy, cz + hgt + 0.01))
        lathe([(0.0, 0.0), (0.018, 0.015), (0.022, 0.035), (0.012, 0.07), (0.0, 0.1)], glow((1.0, 0.62, 0.18), 8.0), segs=8,
              loc=(cx, cy, cz + hgt + 0.01), parent=f)
        flicker(f, seed=11 + i, sway=0.12)
    place(1.0, 0.0)


# ===================================================================== tv ==
def _squircle(x, y, n=5.0):
    """Map a point of the square [-1, 1]^2 into a superellipse of order n."""
    rs = max(abs(x), abs(y))
    if rs < 1e-9:
        return x, y
    re = (abs(x) ** n + abs(y) ** n) ** (1.0 / n)
    return x * rs / re, y * rs / re


def square_ring(n_side=10, ccw=True):
    """(u, v) points walking the boundary of the unit square (for rings that
    must follow a squircle-mapped sheet's edge)."""
    pts = []
    for side in range(4):
        for k in range(n_side):
            t = k / n_side
            u, v = [(t, 0.0), (1.0, t), (1.0 - t, 1.0), (0.0, 1.0 - t)][side]
            pts.append((u, v))
    return pts if ccw else list(reversed(pts))


def tv():
    """A 1970s CRT colour TV at 3x life size on a mid-century walnut stand:
    walnut veneer cabinet, brushed-aluminium front, a bulging glass screen
    playing a synthwave sunset (the grid scrolls in the idle clip), chrome
    knobs, speaker slots, a power LED and rabbit-ear antennas.
    ~1.9 x 1.5 x 2.6 m, front facing -Y."""
    mats_reset()
    walnut = pbr("wood", (0.24, 0.11, 0.05), color2=(0.12, 0.05, 0.02), rough=0.35, edge=0.02, name="walnut")
    alu = pbr("metal", (0.66, 0.64, 0.6), rough=0.28, grime=0.12, edge=0.01, name="brushed_alu")
    bakelite = pbr("plastic", (0.05, 0.035, 0.03), rough=0.4, edge=0.015, name="bakelite")
    # Stand: splayed tapered legs with brass ferrules, rails and a shelf.
    for sx in (-1, 1):
        for sy in (-1, 1):
            top = V((sx * 0.7, sy * 0.42, 0.6))
            foot = V((sx * 0.82, sy * 0.55, 0.0))
            tube([tuple(top), tuple(foot + V((0, 0, 0.09)))], lambda t: 0.06 - 0.025 * t, walnut, verts=8)
            tube([tuple(foot + V((0, 0, 0.1))), tuple(foot)], 0.035, GOLD_M, verts=8)
    soft_box((1.6, 0.98, 0.1), (0, 0, 0.58), walnut, r=0.3, cuts=1)
    cube((1.5, 0.9, 0.05), (0, 0, 0.3), walnut, bevel=0.01)
    # Cabinet with the tapering tube housing behind it.
    Z0, Z1 = 0.64, 2.06
    FY = -0.62
    soft_box((1.9, 0.9, Z1 - Z0), (0, FY + 0.45, (Z0 + Z1) / 2), walnut, r=0.2, cuts=3, name="cabinet")
    back = []
    for k, (w, h, y) in enumerate(((1.7, 1.25, 0.25), (1.4, 1.0, 0.5), (0.9, 0.7, 0.72))):
        back.append([(x * w / 2, y, (Z0 + Z1) / 2 + z * h / 2) for x, z in (_squircle(*p) for p in
                     [(math.cos(TAU * i / 24), math.sin(TAU * i / 24)) for i in range(24)])])
    loft(back, bakelite, cap0=False, cap1=True, name="tube_back")
    # Brushed aluminium front panel.
    soft_box((1.78, 0.06, 1.3), (0, FY - 0.01, (Z0 + Z1) / 2), alu, r=0.4, cuts=2, name="front")
    # Bulging screen, a rubber mask around it and a chrome trim ring.
    SX, SZ, SW, SH = -0.2, (Z0 + Z1) / 2 + 0.02, 1.18, 1.0
    BULGE = 0.06

    def surf(u, v, dy=0.0):
        x, z = _squircle(u * 2 - 1, v * 2 - 1, 4.0)
        b = (1 - x * x) * (1 - z * z)
        return (SX + x * SW / 2, FY - 0.05 - BULGE * b - dy, SZ + z * SH / 2)

    sheet(lambda u, v: surf(u, v), 16, 14, anim_m((0.16, 0.05, 0.36), "screen", 1.5), thick=0.0, name="screen")
    ring = [surf(u, v) for u, v in square_ring(10)]
    sweep([(0.0, 0.0), (0.09, 0.0), (0.09, -0.05), (0.0, -0.07)], [(p[0], 0, p[2]) for p in ring], bakelite,
          plane_normal=(0, -1, 0), name="mask").location.y = FY - 0.04
    sweep([(0.09, 0.0), (0.12, 0.0), (0.12, -0.02), (0.09, -0.02)], [(p[0], 0, p[2]) for p in ring], CHROME_M,
          plane_normal=(0, -1, 0), name="trim").location.y = FY - 0.04
    # The show: a striped synthwave sun over a scrolling neon grid.
    sun_cols = [(1.0, 0.85, 0.2), (1.0, 0.6, 0.2), (1.0, 0.4, 0.35), (1.0, 0.25, 0.55), (0.95, 0.15, 0.7)]
    cxu, cvz, rad = 0.5, 0.45, 0.26
    bands = [(0.93, 0.7), (0.67, 0.5), (0.47, 0.33), (0.3, 0.18), (0.155, 0.06)]
    for (t0, t1), col in zip(bands, sun_cols):
        pts_top, pts_bot = [], []
        for k in range(9):
            for tt, lst in ((t0, pts_top), (t1, pts_bot)):
                zz = tt
                half = math.sqrt(max(0.0, 1 - zz * zz))
                xx = -half + 2 * half * k / 8
                lst.append(surf(cxu + xx * rad * SH / SW, cvz + zz * rad, 0.006))
        loft([pts_bot, pts_top], glow(col, 3.0), closed=False, cap0=False, cap1=False, name="sun")
    # horizon and the grid
    loft([[surf(0.02, 0.44, 0.006), surf(0.98, 0.44, 0.006)], [surf(0.02, 0.455, 0.006), surf(0.98, 0.455, 0.006)]],
         glow((1.0, 0.3, 0.8), 4.0), closed=False, cap0=False, cap1=False, name="horizon")
    grid_m = glow((0.2, 0.9, 1.0), 3.5)
    for k in range(-5, 6):
        x0 = 0.5 + k * 0.03
        x1 = 0.5 + k * 0.12
        loft([[surf(x0 - 0.004, 0.44, 0.006), surf(x1 - 0.006, 0.02, 0.006)], [surf(x0 + 0.004, 0.44, 0.006), surf(x1 + 0.006, 0.02, 0.006)]],
             grid_m, closed=False, cap0=False, cap1=False, name="grid_v")
    g = pivot("grid_scroll", (0, 0, 0))
    step = 0.1
    for k in range(5):
        v = 0.40 - k * step
        if v < 0.0:
            continue
        loft([[surf(0.03, v, 0.007), surf(0.97, v, 0.007)], [surf(0.03, v + 0.012, 0.007), surf(0.97, v + 0.012, 0.007)]],
             grid_m, closed=False, cap0=False, cap1=False, name="grid_h", parent=g)
    key(g, "idle", "location", [(0, (0, 0, 0)), (60, (0, 0, -step * SH))], index=2, interp="LINEAR") if False else None
    key(g, "idle", "location", [(0, 0.0), (60, -step * SH)], index=2, interp="LINEAR")
    # Controls: two chrome dials, two small knobs, speaker slots, power LED.
    CX = 0.62
    for i, z in enumerate((SZ + 0.32, SZ + 0.02)):
        prof = [(0.0, 0.0), (0.13, 0.0), (0.13, 0.03), (0.1, 0.1), (0.0, 0.11)]
        lathe(prof, CHROME_M, segs=20, loc=(CX, FY - 0.04, z), rot=(math.pi / 2, 0, 0))
        cube((0.03, 0.02, 0.16), (CX, FY - 0.15, z), bakelite, bevel=0.005)
        for k in range(12):
            a = TAU * k / 12
            sphere(0.012, (CX + math.cos(a) * 0.17, FY - 0.045, z + math.sin(a) * 0.17), glow((1.0, 0.8, 0.5), 2.0) if i == 0 and k == 3 else alu,
                   segments=6, rings=4)
    for k, x in enumerate((CX - 0.1, CX + 0.1)):
        lathe([(0.0, 0.0), (0.06, 0.0), (0.05, 0.06), (0.0, 0.065)], bakelite, segs=12, loc=(x, FY - 0.04, SZ - 0.26), rot=(math.pi / 2, 0, 0))
    for k in range(6):
        cube((0.3, 0.03, 0.025), (CX, FY - 0.045, SZ - 0.38 - k * 0.05), bakelite, bevel=0.006)
    sphere(0.028, (CX + 0.14, FY - 0.05, SZ - 0.62), glow((1.0, 0.1, 0.1), 6.0), segments=8, rings=6)
    text("NEONIC", 0.07, (CX, FY - 0.045, SZ + 0.52), GOLD_M, extrude=0.008)
    # Rabbit ears.
    lathe([(0.0, Z1), (0.2, Z1), (0.19, Z1 + 0.05), (0.13, Z1 + 0.12), (0.0, Z1 + 0.14)], bakelite, segs=16, loc=(0.35, FY + 0.6, 0))
    for sx in (-1, 1):
        a = V((sx * 0.45, 0.15, 1.0)).normalized()
        p0 = V((0.35, FY + 0.6, Z1 + 0.12))
        segs = [(0.0, 0.18, 0.022), (0.18, 0.36, 0.016), (0.36, 0.55, 0.011)]
        for s0, s1, r in segs:
            rod(tuple(p0 + a * s0), tuple(p0 + a * s1), r, CHROME_M, verts=6)
        sphere(0.03, tuple(p0 + a * 0.56), CHROME_M, segments=8, rings=6)
    place(1.0, 0.0)


# ============================================================== champagne ==
def champagne():
    """A bottle of champagne on ice at 2.8x life size: a hammered silver
    bucket with ring handles, clear ice cubes, a dark green bottle with a
    gold foil neck and cream label, uncorked and fizzing (the bubbles rise
    in the idle clip). ~0.6 m across, 0.95 m tall."""
    mats_reset()
    silver = pbr("chrome", (0.86, 0.87, 0.9), rough=0.12, bump=0.25, grime=0.25, edge=0.006, name="silver")
    bottle_m = pbr("plastic", (0.02, 0.08, 0.03), rough=0.06, wear=0.05, grime=0.1, bump=0.0, name="bottle_glass")
    foil = pbr("gold", (1.0, 0.75, 0.3), rough=0.3, bump=0.9, scale=0.3, name="foil")
    label_m = pbr("plastic", (0.92, 0.86, 0.7), rough=0.6, wear=0.1, name="label")
    ink = pbr("plastic", (0.02, 0.02, 0.03), rough=0.5, name="ink")
    ice_m = pbr("glass", (0.8, 0.95, 1.0), alpha=0.45, name="ice")
    foam_m = pbr("plastic", (1.0, 0.97, 0.88), rough=0.45, wear=0.0, bump=0.4, name="fizz")
    bubble_m = pbr("glass", (1.0, 0.95, 0.75), alpha=0.5, name="bubble")
    # Bucket.
    lathe([(0.0, 0.0), (0.2, 0.0), (0.21, 0.02), (0.19, 0.045), (0.2, 0.065), (0.27, 0.42), (0.29, 0.44), (0.29, 0.465),
           (0.27, 0.47), (0.255, 0.44), (0.19, 0.09), (0.0, 0.09)], silver, segs=28, name="bucket")
    lathe([(0.265, 0.33), (0.276, 0.33), (0.281, 0.37), (0.271, 0.37)], GOLD_M, segs=28, cap=False)
    for sx in (-1, 1):
        cyl(0.035, 0.03, (sx * 0.265, 0, 0.36), GOLD_M, rot=(0, math.pi / 2, 0), verts=10, bevel=0.0)
        torus(0.065, 0.012, (sx * 0.295, 0, 0.3), GOLD_M, rot=(math.pi / 2, 0, math.pi / 2), major_segments=14, minor_segments=5)
    # Ice: a crushed layer and loose cubes.
    lathe([(0.0, 0.37), (0.25, 0.37), (0.24, 0.4), (0.0, 0.4)], pbr("plastic", (0.75, 0.85, 0.9), rough=0.2, bump=0.8, scale=0.2, name="crushed"), segs=20)
    rnd = random.Random(5)
    for i in range(9):
        a = TAU * i / 9 + 0.3
        r = 0.17 + rnd.uniform(-0.03, 0.04)
        c = cube((0.09, 0.09, 0.08), (math.cos(a) * r, math.sin(a) * r, 0.42 + rnd.uniform(0, 0.05)), ice_m, bevel=0.012)
        c.rotation_euler = (rnd.uniform(-0.6, 0.6), rnd.uniform(-0.6, 0.6), rnd.uniform(0, 3))
    # The bottle, tilted towards the back-right corner of the bucket.
    tilt = pivot("_bottle_frame", (0.0, 0.0, 0.1))
    prof = [(0.0, 0.0), (0.1, 0.0), (0.118, 0.02), (0.12, 0.44), (0.114, 0.49), (0.075, 0.58), (0.047, 0.64), (0.042, 0.73),
            (0.048, 0.745), (0.048, 0.765), (0.036, 0.77), (0.0, 0.765)]
    parts = [lathe(prof, bottle_m, segs=20, name="bottle")]
    parts.append(lathe([(0.121, 0.18), (0.123, 0.18), (0.123, 0.38), (0.121, 0.38)], label_m, segs=20, cap=False))
    parts.append(lathe([(0.1225, 0.23), (0.124, 0.23), (0.124, 0.33), (0.1225, 0.33)], ink, segs=20, cap=False))
    parts.append(text("ROSÉ", 0.045, (0.0, -0.126, 0.28), GOLD_M, extrude=0.004, font=FONT_SERIF))
    parts.append(lathe([(0.078, 0.56), (0.05, 0.62), (0.046, 0.7), (0.05, 0.745), (0.051, 0.768), (0.04, 0.775), (0.03, 0.77)],
                       foil, segs=16, cap=False))
    parts.append(lathe([(0.0, 0.76), (0.036, 0.765), (0.05, 0.8), (0.045, 0.84), (0.02, 0.855), (0.0, 0.855)], foam_m, segs=12))
    for o in parts:
        attach(o, tilt)
    tilt.rotation_euler = (math.radians(8), math.radians(12), 0)
    tilt.location = (-0.03, 0.02, 0.1)
    tilt.scale = (1.12, 1.12, 1.12)
    bpy.context.view_layer.update()
    mouth = tilt.matrix_world @ V((0, 0, 0.84))
    for o in parts:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.data.objects.remove(tilt)
    # Fizz rising out of the neck.
    for i in range(6):
        p = pivot("bubble_%d" % i, (mouth.x + (i % 3 - 1) * 0.015, mouth.y, mouth.z - 0.03))
        sphere(0.014 + 0.005 * (i % 3), tuple(p.location), bubble_m, segments=8, rings=5, parent=p)
        later(rise, p, 0.12, phase=i / 6.0, drift=0.02)
    place(1.0, 0.0)


# =================================================================== cake ==
def cake():
    """A three-tier party cake at 2.5x life size on a gold stand: pink and
    cream fondant, white icing drips, piped borders, macarons, gold leaf
    and five striped candles whose flames flicker. ~0.9 m across."""
    mats_reset()
    pink = pbr("plastic", (0.95, 0.45, 0.62), rough=0.55, wear=0.0, grime=0.2, bump=0.25, edge=0.02, name="fondant_pink")
    cream = pbr("plastic", (0.95, 0.88, 0.8), rough=0.55, wear=0.0, grime=0.2, bump=0.25, edge=0.02, name="fondant_cream")
    lilac = pbr("plastic", (0.7, 0.55, 0.95), rough=0.55, wear=0.0, grime=0.2, bump=0.25, edge=0.02, name="fondant_lilac")
    icing = pbr("plastic", (0.98, 0.97, 0.96), rough=0.25, wear=0.0, grime=0.1, bump=0.1, name="icing")
    mac_cols = [(0.55, 0.9, 0.85), (1.0, 0.75, 0.4), (0.8, 0.6, 1.0), (1.0, 0.55, 0.7), (0.6, 0.85, 1.0)]
    # Gold cake stand.
    lathe([(0.0, 0.0), (0.22, 0.0), (0.23, 0.015), (0.2, 0.03), (0.06, 0.06), (0.045, 0.1), (0.05, 0.12), (0.12, 0.13), (0.44, 0.13),
           (0.45, 0.145), (0.44, 0.155), (0.0, 0.155)], GOLD_M, segs=24, name="stand")
    tiers = [(0.37, 0.24, pink), (0.27, 0.22, cream), (0.185, 0.2, lilac)]
    z = 0.155
    rnd = random.Random(9)
    for ti, (r, h, m) in enumerate(tiers):
        lathe([(0.0, z), (r, z), (r + 0.004, z + h * 0.5), (r, z + h - 0.015), (r - 0.015, z + h), (0.0, z + h)], m, segs=32)
        torus(r + 0.004, 0.018, (0, 0, z + 0.015), icing, major_segments=32, minor_segments=4)      # piped border
        # icing cap with drips on the upper two tiers, gold leaf band on the bottom one
        if ti > 0:
            lathe([(0.0, z + h), (r - 0.01, z + h), (r + 0.008, z + h - 0.012), (r + 0.01, z + h - 0.03), (r - 0.01, z + h + 0.012), (0.0, z + h + 0.014)],
                  icing, segs=32)
            n = 11 if ti == 1 else 9
            for k in range(n):
                a = TAU * (k + rnd.uniform(-0.2, 0.2)) / n
                L = rnd.uniform(0.04, 0.12)
                ca, sa = math.cos(a), math.sin(a)
                rr = r + 0.012
                tube([(ca * rr, sa * rr, z + h - 0.02), (ca * (rr + 0.004), sa * (rr + 0.004), z + h - 0.02 - L * 0.6), (ca * rr, sa * rr, z + h - 0.02 - L)],
                     lambda t: 0.014 + 0.006 * t, icing, verts=6)
                sphere(0.019, (ca * rr, sa * rr, z + h - 0.02 - L), icing, segments=6, rings=4)
        else:
            lathe([(r + 0.005, z + 0.1), (r + 0.007, z + 0.1), (r + 0.007, z + 0.13), (r + 0.005, z + 0.13)], GOLD_M, segs=32, cap=False)
            for k in range(8):
                a = TAU * k / 8 + 0.2
                mx, my, mz = math.cos(a) * (r - 0.05), math.sin(a) * (r - 0.05), z + h
                col = pbr("plastic", mac_cols[k % 5], rough=0.5, wear=0.0, name="macaron%d" % (k % 5))
                lathe([(0.0, 0.0), (0.035, 0.0), (0.04, 0.012), (0.036, 0.02), (0.0, 0.02)], col, segs=10, loc=(mx, my, mz))
                lathe([(0.0, 0.02), (0.032, 0.02), (0.032, 0.028), (0.0, 0.028)], cream, segs=10, loc=(mx, my, mz))
                lathe([(0.0, 0.028), (0.036, 0.028), (0.04, 0.036), (0.035, 0.046), (0.0, 0.05)], col, segs=10, loc=(mx, my, mz))
        z += h
    # Candles with flickering flames.
    stripes = [(1.0, 0.4, 0.7), (0.4, 0.9, 1.0), (1.0, 0.85, 0.3), (0.7, 0.5, 1.0), (0.5, 1.0, 0.6)]
    for i in range(5):
        a = TAU * i / 5 + 0.3
        cx, cy = math.cos(a) * 0.11, math.sin(a) * 0.11
        cz = z + 0.01
        lathe([(0.0, 0.0), (0.012, 0.0), (0.012, 0.12), (0.0, 0.125)], pbr("plastic", stripes[i], rough=0.5, wear=0.0, name="candle%d" % i),
              segs=8, loc=(cx, cy, cz))
        for k in range(3):
            torus(0.0125, 0.003, (cx, cy, cz + 0.025 + k * 0.035), icing, rot=(0.35, 0, 0), major_segments=8, minor_segments=3)
        f = pivot("flame_%d" % i, (cx, cy, cz + 0.13))
        lathe([(0.0, 0.0), (0.012, 0.012), (0.014, 0.028), (0.007, 0.052), (0.0, 0.07)], glow((1.0, 0.6, 0.15), 8.0), segs=8,
              loc=(cx, cy, cz + 0.13), parent=f)
        flicker(f, seed=21 + i, sway=0.14)
    # a few gold sugar pearls on top
    for k in range(10):
        a = rnd.uniform(0, TAU)
        rr = rnd.uniform(0.02, 0.16)
        sphere(0.009, (math.cos(a) * rr, math.sin(a) * rr, z + 0.014), GOLD_M, segments=6, rings=4)
    place(1.0, 0.0)


# ============================================================ bench press ==
def _plate(x, r, t, face_rgb, name="plate"):
    """A rubber bumper plate on the bar's X axis with a coloured face ring
    and a steel hub."""
    rub = pbr("rubber", (0.025, 0.025, 0.03), rough=0.75, edge=0.01, name="bumper_rubber")
    face = pbr("plastic", face_rgb, rough=0.45, wear=0.3, name="plate_%d%d%d" % tuple(int(c * 9) for c in face_rgb))
    prof = [(0.06, -t / 2), (r - 0.02, -t / 2), (r, -t / 2 + 0.02), (r, t / 2 - 0.02), (r - 0.02, t / 2), (0.06, t / 2)]
    out = [lathe(prof, rub, segs=28, loc=(x, 0, 0), rot=(0, math.pi / 2, 0), cap=False, name=name)]
    for s in (-1, 1):
        out.append(lathe([(r * 0.62, s * (t / 2 + 0.003)), (r * 0.9, s * (t / 2 + 0.003))], face, segs=28, loc=(x, 0, 0),
                         rot=(0, math.pi / 2, 0), cap=False))
        out.append(lathe([(0.03, s * (t / 2 + 0.006)), (0.09, s * (t / 2 + 0.006))], CHROME_M, segs=16, loc=(x, 0, 0), rot=(0, math.pi / 2, 0), cap=False))
    return out


def bench_press():
    """A flat bench under a squat-style rack at 2.2x life size: graphite
    powder-coated steel, a black vinyl pad with lime piping, J-hooks and
    spotter arms, a loaded Olympic barbell with coloured bumper plates and
    spring collars, a towel and a water bottle. 4 x 2.6 x 3 m."""
    mats_reset()
    steel = pbr("paint", (0.05, 0.055, 0.065), rough=0.5, wear=0.5, grime=0.4, edge=0.015, name="graphite")
    vinyl = pbr("leather", (0.03, 0.03, 0.035), rough=0.35, wear=0.25, bump=0.3, edge=0.03, name="vinyl")
    piping = pbr("plastic", (0.3, 0.95, 0.35), rough=0.4, wear=0.2, name="lime")
    towel_m = pbr("fabric", (0.1, 0.75, 0.7), bump=0.8, name="towel")
    bottle_m = pbr("glass", (0.3, 0.9, 1.0), alpha=0.5, name="bottle")
    Y0, Y1 = -1.2, 0.95
    # Rack: two uprights on floor rails with rubber feet.
    for sx in (-1, 1):
        x = sx * 0.95
        cube((0.13, 0.13, 2.8), (x, 0.95, 1.43), steel, bevel=0.012)
        cube((0.14, 1.3, 0.12), (x, 0.7, 0.09), steel, bevel=0.012)
        for yy in (0.1, 1.3):
            cube((0.18, 0.14, 0.04), (x, yy, 0.02), RUBBER_M, bevel=0.01)
        for k in range(10):
            cube((0.03, 0.135, 0.03), (x, 0.95, 0.9 + k * 0.16), PLASTIC_BLACK, bevel=0.0)   # hole row
        # J-hook holding the bar
        cube((0.16, 0.22, 0.08), (x, 0.84, 2.36), steel, bevel=0.01)
        cube((0.16, 0.05, 0.16), (x, 0.73, 2.43), steel, bevel=0.01)
        cube((0.14, 0.2, 0.012), (x, 0.84, 2.405), RUBBER_M, bevel=0.0)
        # spotter arm
        cube((0.1, 0.9, 0.1), (x, 0.5, 1.72), steel, bevel=0.01)
        cube((0.1, 0.05, 0.16), (x, 0.07, 1.77), steel, bevel=0.01)
        cube((0.06, 0.02, 2.2), (x, 1.02, 1.5), glow((0.2, 1.0, 0.45), 3.5), bevel=0.0)   # neon strip on the back face
        cap = cube((0.15, 0.15, 0.03), (x, 0.95, 2.84), PLASTIC_BLACK, bevel=0.008)
    cube((2.0, 0.13, 0.13), (0, 0.95, 2.7), steel, bevel=0.012)     # top crossbar
    cube((2.0, 0.13, 0.12), (0, 1.3, 0.09), steel, bevel=0.012)
    text("BOMBFALL GYM", 0.11, (0, 0.88, 2.7), glow((0.2, 1.0, 0.45), 3.0), extrude=0.0, res=1)
    # Bench: T-feet, posts, frame rail and the padded top.
    for yy in (-0.95, 0.55):
        cube((0.75, 0.12, 0.1), (0, yy, 0.07), steel, bevel=0.01)
        for sx in (-1, 1):
            cube((0.12, 0.14, 0.04), (sx * 0.34, yy, 0.02), RUBBER_M, bevel=0.01)
        cube((0.12, 0.12, 0.72), (0, yy, 0.46), steel, bevel=0.01)
    cube((0.3, 2.1, 0.1), (0, -0.2, 0.84), steel, bevel=0.01)
    soft_box((0.72, 2.3, 0.05), (0, -0.15, 0.915), PLASTIC_BLACK, r=0.5, cuts=1)          # plywood base
    soft_box((0.74, 2.32, 0.03), (0, -0.15, 0.95), piping, r=0.5, cuts=1)                 # piping seam
    soft_box((0.72, 2.3, 0.2), (0, -0.15, 1.06), vinyl, r=0.45, puff=0.1, cuts=4, name="pad")
    # Towel draped over the foot end.
    def towel(u, v):
        x = (u - 0.5) * 0.55
        yy = Y0 + 0.35 - v * 0.55
        zt = 1.175
        if yy < Y0 + 0.05:
            d = (Y0 + 0.05) - yy
            return (x + 0.02 * math.sin(u * 9), Y0 + 0.05 - 0.06 * math.sin(min(d, 0.1) * 15), zt - d * 1.2)
        return (x, yy, zt + 0.015 * math.sin(v * 8 + u * 3))
    sheet(towel, 8, 10, towel_m, thick=0.025, name="towel")
    # Barbell: shaft, sleeves, collars and plates.
    BZ, BY = 2.47, 0.84
    bar = pivot("_bar", (0, 0, 0))
    rod((-1.25, BY, BZ), (1.25, BY, BZ), 0.034, pbr("metal", (0.7, 0.7, 0.72), rough=0.35, bump=0.9, scale=0.2, name="knurl"), verts=12)
    for sx in (-1, 1):
        rod((sx * 1.25, BY, BZ), (sx * 1.3, BY, BZ), 0.075, CHROME_M, verts=16)
        rod((sx * 1.3, BY, BZ), (sx * 2.0, BY, BZ), 0.055, CHROME_M, verts=16)
        xs = sx * 1.39
        for r, t, col in ((0.5, 0.14, (0.8, 0.05, 0.08)), (0.46, 0.12, (0.05, 0.25, 0.85)), (0.34, 0.1, (1.0, 0.75, 0.05))):
            for o in _plate(xs + sx * t / 2, r, t, col):
                o.location = (o.location.x, BY, BZ)
            xs += sx * (t + 0.01)
        # spring collar
        tube([(xs + sx * 0.03 + math.cos(k * 0.6) * 0.0, BY + math.cos(k * 1.2) * 0.07, BZ + math.sin(k * 1.2) * 0.07) for k in range(12)],
             0.012, CHROME_M, verts=5)
        tube([(xs + sx * 0.03, BY + 0.07, BZ), (xs + sx * 0.03, BY + 0.2, BZ + 0.08)], 0.012, CHROME_M, verts=5)
    bpy.data.objects.remove(bar)
    # Water bottle on the floor.
    lathe([(0.0, 0.0), (0.09, 0.0), (0.1, 0.02), (0.1, 0.34), (0.07, 0.4), (0.04, 0.43), (0.0, 0.43)], bottle_m, segs=16, loc=(0.62, -0.9, 0))
    lathe([(0.0, 0.43), (0.045, 0.43), (0.045, 0.5), (0.0, 0.5)], pbr("plastic", (1.0, 0.2, 0.6), rough=0.4, name="cap"), segs=12, loc=(0.62, -0.9, 0))
    lathe([(0.1, 0.12), (0.102, 0.12), (0.102, 0.24), (0.1, 0.24)], pbr("plastic", (1.0, 0.2, 0.6), rough=0.4, name="cap"), segs=16, loc=(0.62, -0.9, 0), cap=False)
    place(1.0, 0.0)


# ================================================================== beds ==
def _wrap(e, rr):
    """Distance e past a mattress edge -> (outward offset, drop) for cloth
    rolling over a rounded edge of radius rr and then hanging straight."""
    if e <= 0:
        return e, 0.0
    q = math.pi / 2 * rr
    if e < q:
        t = e / rr
        return rr * math.sin(t), rr * (1 - math.cos(t))
    return rr, rr + (e - q)


def duvet(xa, xb, w, zt, m, hang=0.55, foot_hang=0.5, rr=0.12, puff=0.06, thick=0.06, nx=22, ny=16, seed=1, name="duvet",
          fold_amp=0.05):
    """A duvet lying on a mattress top at height zt: from x = xa (turned
    down near the pillows) to the foot at x = xb (< xa), across a width w,
    falling `hang` over the long sides and `foot_hang` over the foot, with
    soft folds on the hanging parts and a puffy, rumpled top."""
    rnd = random.Random(seed)
    ph = [rnd.uniform(0, TAU) for _ in range(4)]
    L = xa - xb

    def fn(u, v):
        s = (v - 0.5) * (w + 2 * hang)
        e = abs(s) - w / 2
        off, drop_y = _wrap(e, rr)
        y = math.copysign(w / 2 + off, s) if e > 0 else s
        xl = u * (L + foot_hang)            # distance from xa towards the foot
        ex = xl - L
        offx, drop_x = _wrap(ex, rr)
        x = xb - offx if ex > 0 else xa - xl
        top = 1.0 if (e <= 0 and ex <= 0) else 0.0
        z = zt - drop_y - drop_x
        hangf = min(1.0, max(0.0, max(e, ex) / 0.2))
        # folds: vertical ripples on the hanging parts, rumples on top
        y += math.copysign(1, s) * fold_amp * hangf * math.sin(x * 5.0 + ph[0]) * (0.6 + 0.4 * math.sin(x * 2.3 + ph[1]))
        x -= fold_amp * (hangf if ex > 0 else 0) * math.sin(y * 6.0 + ph[2])
        z += top * puff * (math.sin(x * 2.1 + ph[1]) * math.sin(y * 2.7 + ph[3]) * 0.5 + 0.5)
        z = max(z, zt - hang - rr)
        return (x, y, z)
    return sheet(fn, nx, ny, m, thick=thick, name=name)


def pillow(size, loc, m, tilt=0.0, yaw=0.0, name="pillow"):
    """A plump pillow with pinched corners, leaning back by `tilt`."""
    return soft_box(size, loc, m, r=0.95, puff=0.35, pinch=0.55, cuts=4, rot=(0, tilt, yaw), name=name)


def _mattress(x0, x1, w, z0, z1, m, trim):
    soft_box((x1 - x0, w, z1 - z0), ((x0 + x1) / 2, 0, (z0 + z1) / 2), m, r=0.35, puff=0.03, cuts=3, name="mattress")
    for z in (z0 + 0.02, z1 - 0.02):
        sweep([(0.0, -0.012), (0.018, 0.0), (0.0, 0.012)], [(x0 + 0.03, -w / 2 + 0.03, z), (x1 - 0.03, -w / 2 + 0.03, z),
              (x1 - 0.03, w / 2 - 0.03, z), (x0 + 0.03, w / 2 - 0.03, z)], trim, name="piping")


def bed1():
    """A low hotel bed at 2.8x life size, seen from the side: walnut plinth
    floating on a cyan LED kick, crisp white mattress and duvet with a plum
    and gold runner, two pillows and a velvet cushion, a low upholstered
    headboard. 5.8 x 2.2 x 1.9 m, headboard at +X."""
    mats_reset()
    walnut = pbr("wood", (0.13, 0.06, 0.03), color2=(0.09, 0.04, 0.02), rough=0.3, edge=0.02, name="walnut")
    sheet_m = pbr("fabric", (0.9, 0.9, 0.92), color2=(0.82, 0.83, 0.88), edge=0.03, name="cotton")
    runner_m = pbr("fabric", (0.35, 0.06, 0.28), color2=(0.25, 0.04, 0.2), edge=0.02, name="runner")
    velvet = pbr("fabric", (0.06, 0.07, 0.2), color2=(0.04, 0.05, 0.14), bump=0.3, edge=0.03, name="navy_velvet")
    trim = pbr("fabric", (0.75, 0.75, 0.8), name="piping")
    W = 2.1
    cube((5.4, W - 0.25, 0.14), (0, 0, 0.07), PLASTIC_BLACK, bevel=0.01)
    tube([(-2.66, -W / 2 + 0.14, 0.03), (2.66, -W / 2 + 0.14, 0.03)], 0.02, glow(CYAN, 5.0), verts=5)
    soft_box((5.7, W, 0.36), (0, 0, 0.14 + 0.18), walnut, r=0.15, cuts=2, name="plinth")
    _mattress(-2.78, 2.62, W - 0.1, 0.5, 1.02, sheet_m, trim)
    duvet(1.25, -2.8, W - 0.1, 1.04, sheet_m, hang=0.42, foot_hang=0.35, puff=0.1, seed=3)
    duvet(-1.3, -2.25, W - 0.08, 1.12, runner_m, hang=0.36, foot_hang=0.0, rr=0.1, puff=0.02, thick=0.03, nx=8, ny=16, seed=4,
          name="runner", fold_amp=0.03)
    soft_box((0.24, W - 0.05, 0.16), (1.25, 0, 1.13), sheet_m, r=0.9, puff=0.2, cuts=3, name="turndown")
    for k, y in enumerate((-0.48, 0.48)):
        pillow((0.66, 1.0, 0.36), (2.2, y, 1.24), sheet_m, tilt=-0.35, yaw=0.05 * (k * 2 - 1))
    pillow((0.45, 0.62, 0.3), (1.78, -0.2, 1.24), velvet, tilt=-0.2, yaw=0.3, name="cushion")
    # Low headboard: velvet panel in a walnut frame with a pink backlight.
    soft_box((0.18, W + 0.2, 1.3), (2.78, 0, 1.25), velvet, r=0.5, puff=0.08, cuts=3, name="headboard")
    soft_box((0.12, W + 0.28, 1.38), (2.9, 0, 1.23), walnut, r=0.3, cuts=2)
    tube([(2.97, -W / 2 - 0.14, 0.62), (2.97, -W / 2 - 0.14, 1.9), (2.97, W / 2 + 0.14, 1.9), (2.97, W / 2 + 0.14, 0.62)], 0.018,
         glow(PINK, 5.0), verts=5)
    place(1.0, 0.0)


def bed2():
    """A double bed with a tall channel-tufted velvet wingback headboard at
    2.8x life size: lilac bedding, four pillows, a faux-fur throw and a pink
    neon halo behind the headboard. 5.8 x 2.5 x 2.85 m."""
    mats_reset()
    velvet = pbr("fabric", (0.45, 0.12, 0.35), color2=(0.32, 0.07, 0.25), bump=0.3, edge=0.03, name="rose_velvet")
    base_v = pbr("fabric", (0.2, 0.05, 0.16), color2=(0.14, 0.03, 0.11), bump=0.3, edge=0.03, name="plum_velvet")
    sheet_m = pbr("fabric", (0.62, 0.52, 0.86), color2=(0.5, 0.42, 0.75), edge=0.03, name="lilac")
    white = pbr("fabric", (0.9, 0.88, 0.92), edge=0.03, name="cotton")
    fur = pbr("fabric", (0.95, 0.9, 0.85), bump=1.0, scale=0.4, edge=0.04, name="faux_fur")
    trim = pbr("fabric", (0.8, 0.75, 0.85), name="piping")
    W = 2.3
    # Upholstered frame on gold feet.
    soft_box((5.6, W + 0.1, 0.5), (-0.1, 0, 0.42), base_v, r=0.35, puff=0.05, cuts=3, name="frame")
    for sx in (-1, 1):
        for sy in (-1, 1):
            lathe([(0.0, 0.0), (0.07, 0.0), (0.09, 0.1), (0.07, 0.17), (0.0, 0.17)], GOLD_M, segs=12, loc=(sx * 2.6 - 0.1, sy * (W / 2 - 0.1), 0))
    _mattress(-2.8, 2.5, W - 0.1, 0.67, 1.2, white, trim)
    duvet(1.05, -2.82, W - 0.1, 1.22, sheet_m, hang=0.5, foot_hang=0.4, puff=0.09, seed=5)
    soft_box((0.28, W, 0.18), (1.05, 0, 1.32), white, r=0.9, puff=0.2, cuts=3, name="turndown")
    # faux-fur throw folded across the foot
    duvet(-1.5, -2.6, W + 0.02, 1.34, fur, hang=0.6, foot_hang=0.0, rr=0.1, puff=0.04, thick=0.07, nx=8, ny=16, seed=6,
          name="throw", fold_amp=0.07)
    for k, y in enumerate((-0.55, 0.55)):
        pillow((0.6, 1.0, 0.34), (2.2, y, 1.42), white, tilt=-0.45, yaw=0.05 * (k * 2 - 1))
        pillow((0.55, 0.9, 0.32), (1.9, y * 0.95, 1.4), sheet_m, tilt=-0.3, yaw=-0.08 * (k * 2 - 1))
    pillow((0.4, 0.6, 0.3), (1.55, 0.1, 1.42), velvet, tilt=-0.2, yaw=0.5, name="cushion")
    # Tall wingback headboard with vertical channel tufting.
    HX, HT = 2.72, 2.85
    soft_box((0.25, W + 0.3, HT - 0.4), (HX + 0.06, 0, 0.4 + (HT - 0.4) / 2), base_v, r=0.6, cuts=3, name="head_back")
    n = 7
    cw = (W + 0.1) / n
    for i in range(n):
        y = -(W + 0.1) / 2 + cw * (i + 0.5)
        soft_box((0.2, cw + 0.01, HT - 0.75), (HX - 0.07, y, 0.6 + (HT - 0.75) / 2 - 0.03), velvet, r=0.95, puff=0.0, cuts=3)
    for sy in (-1, 1):
        wing = soft_box((0.62, 0.22, HT - 0.55), (HX - 0.25, sy * (W / 2 + 0.2), 0.45 + (HT - 0.55) / 2), velvet, r=0.9, puff=0.1, cuts=3,
                        rot=(0, 0, sy * 0.35), name="wing")
        for k in range(3):
            soft_box((0.2, 0.2, HT - 0.75), (HX - 0.12 - k * 0.18, sy * (W / 2 + 0.12 + k * 0.07), 0.55 + (HT - 0.75) / 2), velvet, r=0.95,
                     cuts=2, rot=(0, 0, sy * 0.35))
    tube([(HX + 0.22, -W / 2 - 0.1, 0.9), (HX + 0.22, -W / 2 - 0.1, HT - 0.1), (HX + 0.22, W / 2 + 0.1, HT - 0.1), (HX + 0.22, W / 2 + 0.1, 0.9)],
         0.022, glow(PINK, 6.0), verts=5, name="halo")
    place(1.0, 0.0)


def bed_rich():
    """A royal four-poster at 2.8x life size: turned gilt posts with
    finials, a burgundy velvet canopy with a scalloped valance, curtains
    (the loose pair at the head sways in the idle clip, the foot pair is
    tied back with gold cord), a button-tufted ivory headboard, satin
    bedding with gold trim and a heap of pillows. 5.8 x 2.6 x 2.8 m."""
    mats_reset()
    gilt = pbr("gold", (0.95, 0.68, 0.28), rough=0.28, grime=0.5, bump=0.2, edge=0.012, name="gilt")
    wine = pbr("fabric", (0.32, 0.02, 0.07), color2=(0.22, 0.01, 0.05), bump=0.35, edge=0.03, name="wine_velvet")
    satin = pbr("fabric", (0.45, 0.03, 0.1), color2=(0.6, 0.08, 0.15), rough=0.45, bump=0.1, edge=0.03, name="satin")
    ivory = pbr("fabric", (0.88, 0.82, 0.7), color2=(0.8, 0.73, 0.6), bump=0.3, edge=0.03, name="ivory_velvet")
    white = pbr("fabric", (0.92, 0.9, 0.86), edge=0.03, name="linen")
    goldcloth = pbr("fabric", (0.85, 0.6, 0.2), color2=(0.6, 0.4, 0.1), rough=0.5, bump=0.3, name="gold_brocade")
    W, X0, X1 = 2.3, -2.62, 2.62
    # Carved gilt base with a velvet inset.
    soft_box((5.5, W + 0.12, 0.42), (0, 0, 0.36), wine, r=0.3, cuts=2, name="base")
    for z in (0.16, 0.56):
        sweep([(0.0, -0.035), (0.04, -0.01), (0.03, 0.035), (0.0, 0.035)], [(X0 + 0.05, -W / 2 - 0.05, z), (X1 - 0.05, -W / 2 - 0.05, z),
              (X1 - 0.05, W / 2 + 0.05, z), (X0 + 0.05, W / 2 + 0.05, z)], gilt, name="moulding")
    _mattress(-2.6, 2.45, W - 0.05, 0.6, 1.14, white, gilt)
    duvet(0.95, -2.62, W - 0.05, 1.16, satin, hang=0.5, foot_hang=0.45, puff=0.08, seed=8)
    tube([(0.95 + 0.05, -W / 2 - 0.02, 1.2), (0.95 + 0.05, W / 2 + 0.02, 1.2)], 0.03, gilt, verts=6)
    soft_box((0.3, W + 0.04, 0.2), (0.95, 0, 1.28), white, r=0.9, puff=0.2, cuts=3, name="turndown")
    soft_box((0.3, W - 0.3, 0.3), (2.0, 0, 1.3), goldcloth, r=0.95, cuts=3, name="bolster").rotation_euler = (0, 0, 0)
    for k, y in enumerate((-0.6, 0.0, 0.6)):
        pillow((0.55, 0.75, 0.34), (2.25, y, 1.55), white if k != 1 else ivory, tilt=-0.45, yaw=0.08 * (k - 1))
    for k, y in enumerate((-0.45, 0.45)):
        pillow((0.45, 0.62, 0.3), (1.75, y, 1.46), goldcloth if k else wine, tilt=-0.25, yaw=0.3 * (k * 2 - 1), name="cushion")
    # Button-tufted headboard in a gilt frame.
    HX = 2.62
    soft_box((0.22, W + 0.1, 1.5), (HX, 0, 1.55), ivory, r=0.5, puff=0.1, cuts=4, name="headboard")
    sweep([(0.0, -0.05), (0.06, 0.0), (0.0, 0.05)], [(HX - 0.12, -W / 2 - 0.05, 0.8), (HX - 0.12, -W / 2 - 0.05, 2.3),
          (HX - 0.12, W / 2 + 0.05, 2.3), (HX - 0.12, W / 2 + 0.05, 0.8)], gilt, plane_normal=(1, 0, 0), name="head_frame")
    for iz in range(4):
        for iy in range(6):
            y = -0.95 + iy * 0.38 + (0.19 if iz % 2 else 0)
            if abs(y) > 1.05:
                continue
            sphere(0.035, (HX - 0.115, y, 1.0 + iz * 0.3), gilt, segments=6, rings=4)
    # Four turned gilt posts with finials.
    post = [(0.0, 0.0), (0.14, 0.0), (0.15, 0.06), (0.1, 0.14), (0.13, 0.3), (0.08, 0.5), (0.065, 0.6), (0.09, 0.66), (0.06, 0.72),
            (0.055, 1.5), (0.08, 1.58), (0.05, 1.64), (0.045, 2.5), (0.07, 2.56), (0.05, 2.62), (0.06, 2.66), (0.0, 2.68)]
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 2.72, sy * (W / 2 + 0.16)
            lathe(post, gilt, segs=10, loc=(x, y, 0), name="post")
            lathe([(0.0, 2.68), (0.05, 2.7), (0.075, 2.74), (0.05, 2.78), (0.02, 2.8), (0.0, 2.81)], gilt, segs=10, loc=(x, y, 0))
    # Canopy: frame rails, a velvet ceiling and a scalloped valance.
    for sy in (-1, 1):
        cube((5.5, 0.07, 0.07), (0, sy * (W / 2 + 0.16), 2.56), gilt, bevel=0.012)
    for sx in (-1, 1):
        cube((0.07, W + 0.36, 0.07), (sx * 2.72, 0, 2.56), gilt, bevel=0.012)
    cube((5.5, W + 0.32, 0.03), (0, 0, 2.6), wine, bevel=0.0)

    def valance(p0, p1, n, depth=0.3, sag=0.07):
        a, b = V(p0), V(p1)
        def fn(u, v):
            p = a.lerp(b, u)
            scal = abs(math.sin(u * n * math.pi))
            return (p.x, p.y - 0.015 * math.sin(u * n * TAU * 2), p.z - v * (depth - 0.06 + sag * scal))
        return sheet(fn, n * 6, 3, wine, thick=0.0, name="valance")
    ye = W / 2 + 0.2
    valance((-2.76, -ye, 2.62), (2.76, -ye, 2.62), 7)
    valance((-2.76, ye, 2.62), (2.76, ye, 2.62), 7)
    valance((-2.76, -ye, 2.62), (-2.76, ye, 2.62), 3)
    for sy in (-1, 1):
        tube([(-2.76, sy * ye, 2.34), (2.76, sy * ye, 2.34)], 0.02, goldcloth, verts=5, name="fringe")

    def curtain(x, y, tied, sy):
        """A gathered velvet curtain hanging from the rail at post (x, y)."""
        width = 0.6
        def fn(u, v):
            z = 2.55 - v * 2.5
            pinch = 1.0 - (0.75 * math.exp(-((v - 0.55) ** 2) / 0.02) if tied else 0.0)
            spread = width * (0.35 + 0.65 * v) * pinch if tied else width * (0.8 + 0.2 * v)
            s = (u - 0.5) * spread
            wav = 0.05 * math.sin(u * TAU * 3.0) * (0.5 + 0.5 * v)
            return (x + s, y + sy * (0.05 + wav), max(z, 0.02))
        return sheet(fn, 12, 10, wine, thick=0.0, name="curtain")
    for sx in (-1, 1):
        for sy in (-1, 1):
            x, y = sx * 2.6, sy * (W / 2 + 0.28)
            if sx < 0:
                curtain(x + 0.25, y, True, sy)
                torus(0.1, 0.025, (x + 0.25, y + sy * 0.05, 2.55 - 0.55 * 2.5), goldcloth, rot=(0, math.pi / 2, 0), major_segments=10, minor_segments=4)
                sphere(0.05, (x + 0.25, y + sy * 0.09, 2.55 - 0.62 * 2.5), goldcloth, segments=6, rings=4)
            else:
                p = pivot("sway_%s" % ("front" if sy < 0 else "back"), (x - 0.3, y, 2.55))
                c = curtain(x - 0.3, y, False, sy)
                attach(c, p)
                later(wobble, p, "idle", "rotation_euler", 0, 0.03 * sy, seconds=4.0, phase=1.0 if sy > 0 else 0.0)
                later(wobble, p, "idle", "rotation_euler", 1, 0.015, seconds=4.0, phase=2.0)
    place(1.0, 0.0)


# ========================================================== arcade cabinet ==
INVADER = ["..X.....X..", "...X...X...", "..XXXXXXX..", ".XX.XXX.XX.", "XXXXXXXXXXX", "X.XXXXXXX.X", "X.X.....X.X", "...XX.XX..."]
SQUID = ["...XX...", "..XXXX..", ".XXXXXX.", "XX.XX.XX", "XXXXXXXX", "..X..X..", ".X.XX.X.", "X.X..X.X"]
SHIP = [".....X.....", "....XXX....", ".XXXXXXXXX.", "XXXXXXXXXXX", "XXXXXXXXXXX"]


def pixel_sprite(rows, px, centre, m, name="sprite", parent=None):
    """A flat pixel-art sprite in the XZ plane facing -Y (one quad per lit
    pixel), centred on `centre`."""
    bm = bmesh.new()
    h, w = len(rows), len(rows[0])
    cx, cy, cz = centre
    for j, row in enumerate(rows):
        for i, ch in enumerate(row):
            if ch != "X":
                continue
            x0 = cx + (i - w / 2) * px
            z0 = cz + (h / 2 - j - 1) * px
            vs = [bm.verts.new((x0, cy, z0)), bm.verts.new((x0 + px, cy, z0)), bm.verts.new((x0 + px, cy, z0 + px)), bm.verts.new((x0, cy, z0 + px))]
            bm.faces.new([vs[0], vs[3], vs[2], vs[1]])
    return _obj(name, bm, m, smooth=False, parent=parent)


def extrude_profile(pts, x0, x1, m, name="panel"):
    """A flat polygon in the YZ plane (list of (y, z)) extruded from x0 to x1."""
    bm = bmesh.new()
    a = [bm.verts.new((x0, y, z)) for y, z in pts]
    b = [bm.verts.new((x1, y, z)) for y, z in pts]
    bm.faces.new(a)
    bm.faces.new(list(reversed(b)))
    n = len(pts)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new([a[i], a[j], b[j], b[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    o = _obj(name, bm, m, smooth=False)
    return o


def arcade_cabinet():
    """A classic upright arcade cabinet at 1.5x life size: black laminate
    sides with synthwave side art and glowing T-molding, a coin door, a
    control panel with a ball-top joystick and six LED buttons, a CRT
    ("screen", animated shader) where pixel invaders march in the idle clip,
    and a lit marquee ringed by chasing bulbs ("marquee"). 1.3 x 1.25 x 2.8 m."""
    mats_reset()
    lam = pbr("paint", (0.02, 0.018, 0.03), rough=0.35, wear=0.35, grime=0.3, edge=0.012, name="laminate")
    panel_art = pbr("plastic", (0.08, 0.03, 0.18), rough=0.3, wear=0.3, name="cp_art")
    art_pink = pbr("plastic", (0.95, 0.15, 0.55), rough=0.4, wear=0.3, name="art_pink")
    art_orange = pbr("plastic", (1.0, 0.5, 0.1), rough=0.4, wear=0.3, name="art_orange")
    art_cyan = pbr("plastic", (0.1, 0.75, 0.9), rough=0.4, wear=0.3, name="art_cyan")
    W = 0.62
    prof = [(0.55, 0.0), (-0.45, 0.0), (-0.45, 0.98), (-0.64, 1.08), (-0.64, 1.17), (-0.32, 1.27), (-0.24, 1.33), (-0.1, 2.12),
            (-0.3, 2.2), (-0.32, 2.74), (-0.26, 2.8), (0.55, 2.8)]
    for sx in (-1, 1):
        extrude_profile(prof, sx * W, sx * (W + 0.05), lam, name="side")
        # neon T-molding along the front edge
        edge = [(sx * (W + 0.025), y - 0.012 if k else y, z) for k, (y, z) in enumerate(prof[1:11])]
        tube(edge, 0.022, glow(PINK if sx < 0 else CYAN, 5.0), verts=5, name="tmold")
        # side art: sun with stripes and two slashes
        xo = sx * (W + 0.052)
        for k, (t0, t1) in enumerate(((0.95, 0.72), (0.62, 0.44), (0.34, 0.2), (0.12, 0.02))):
            pts = []
            for tt in (t0, t1):
                half = math.sqrt(max(0.0, 1 - tt * tt))
                row = [(0.1 + (-half + 2 * half * i / 8) * 0.32, 1.72 + tt * 0.32) for i in range(9)]
                pts.append(row if tt == t0 else list(reversed(row)))
            poly = pts[0] + pts[1]
            bm = bmesh.new()
            vs = [bm.verts.new((xo, y, z)) for y, z in poly]
            bm.faces.new(vs)
            _obj("art", bm, art_orange if k < 2 else art_pink, smooth=False)
        for k, (m, dz) in enumerate(((art_pink, 0.0), (art_cyan, 0.2))):
            bm = bmesh.new()
            vs = [bm.verts.new((xo, y, z)) for y, z in ((0.5, 0.2 + dz), (0.5, 0.33 + dz), (-0.4, 1.0 + dz), (-0.4, 0.87 + dz))]
            bm.faces.new(vs)
            _obj("art", bm, m, smooth=False)
    # Carcass between the sides.
    cube((2 * W, 0.04, 0.98), (0, -0.43, 0.49), lam, bevel=0.0)                 # kick panel
    cube((2 * W, 0.98, 0.04), (0, 0.06, 0.02), lam, bevel=0.0)
    cube((2 * W, 0.04, 2.8), (0, 0.53, 1.4), lam, bevel=0.0)                   # back
    cube((2 * W, 0.8, 0.04), (0, 0.14, 2.78), lam, bevel=0.0)                  # top
    # Coin door.
    soft_box((0.46, 0.04, 0.56), (0, -0.46, 0.52), pbr("metal", (0.35, 0.35, 0.38), rough=0.4, grime=0.5, name="door_steel"), r=0.2, cuts=1)
    for k, x in enumerate((-0.1, 0.1)):
        cube((0.1, 0.02, 0.16), (x, -0.485, 0.64), CHROME_M, bevel=0.005)
        cube((0.03, 0.01, 0.1), (x, -0.497, 0.64), glow((1.0, 0.1, 0.1), 5.0), bevel=0.0)
        cube((0.08, 0.02, 0.05), (x, -0.487, 0.44), glow((1.0, 0.55, 0.1), 3.0), bevel=0.0)
    text("25¢", 0.05, (0, -0.49, 0.75), glow((1.0, 0.85, 0.3), 3.0), extrude=0.0, res=2)
    cyl(0.025, 0.02, (0.16, -0.49, 0.3), CHROME_M, rot=(math.pi / 2, 0, 0), verts=10, bevel=0.0)
    # Control panel: apron, sloped deck, joystick, buttons.
    extrude_profile([(-0.64, 1.08), (-0.64, 1.17), (-0.32, 1.27), (-0.24, 1.33), (-0.24, 1.08)], -W, W, lam, name="cp")
    deck_t = math.atan2(1.27 - 1.17, -0.32 + 0.64)
    deck = pivot("_deck", (0, -0.48, 1.222))
    deck.rotation_euler = (deck_t, 0, 0)
    bpy.context.view_layer.update()
    kids = [cube((2 * W - 0.02, 0.33, 0.006), (0, -0.48, 1.225), panel_art, bevel=0.0)]
    jx = -0.32
    kids.append(cyl(0.05, 0.012, (jx, -0.48, 1.232), PLASTIC_BLACK, verts=12, bevel=0.0))
    kids.append(rod((jx, -0.48, 1.23), (jx, -0.49, 1.36), 0.013, CHROME_M, verts=8))
    kids.append(sphere(0.05, (jx, -0.49, 1.39), glow((1.0, 0.1, 0.25), 0.6, (0.8, 0.02, 0.08)), segments=12, rings=8))
    cols = [(1.0, 0.15, 0.3), (1.0, 0.85, 0.1), (0.1, 0.9, 1.0), (0.3, 1.0, 0.4), (0.8, 0.3, 1.0), (1.0, 0.5, 0.1)]
    for i in range(6):
        bx = -0.08 + (i % 3) * 0.13 + (0.03 if i >= 3 else 0)
        by = -0.53 + (0.1 if i >= 3 else 0)
        kids.append(cyl(0.042, 0.012, (bx, by, 1.232), PLASTIC_BLACK, verts=12, bevel=0.0))
        kids.append(lathe([(0.0, 0.0), (0.034, 0.0), (0.034, 0.02), (0.02, 0.028), (0.0, 0.03)], glow(cols[i], 1.4), segs=12, loc=(bx, by, 1.23)))
    for i, x in enumerate((0.38, 0.47)):
        kids.append(cube((0.05, 0.05, 0.02), (x, -0.45, 1.235), glow((0.95, 0.95, 1.0), 2.0 + i), bevel=0.004))
    for o in kids:
        attach(o, deck)
    bpy.context.view_layer.update()
    for o in kids:
        mw = o.matrix_world.copy()
        o.parent = None
        o.matrix_world = mw
    bpy.data.objects.remove(deck)
    # Screen: a bezel on the sloped face with a bulging CRT inside.
    st = math.atan2(-0.1 + 0.24, 2.12 - 1.33)          # lean back from vertical
    sc = V((0, (-0.24 - 0.1) / 2 - 0.01, (1.33 + 2.12) / 2))
    up = V((0, math.sin(st), math.cos(st)))
    nrm = V((0, -math.cos(st), math.sin(st)))
    right = V((1, 0, 0))
    bez = soft_box((2 * W, 0.04, 0.83), tuple(sc - nrm * 0.0), pbr("plastic", (0.01, 0.01, 0.015), rough=0.25, name="bezel"), r=0.1, cuts=1,
                   rot=(-st, 0, 0), name="bezel")
    SW, SH = 0.86, 0.66

    def surf(u, v, lift=0.0):
        x, z = _squircle(u * 2 - 1, v * 2 - 1, 4.0)
        b = (1 - x * x) * (1 - z * z)
        return tuple(sc + right * (x * SW / 2) + up * (z * SH / 2 + 0.02) + nrm * (0.03 + 0.04 * b + lift))
    sheet(lambda u, v: surf(u, v), 16, 12, anim_m((0.06, 0.08, 0.3), "screen", 1.2), thick=0.0, name="screen")
    ring = [surf(u, v) for u, v in square_ring(10, ccw=False)]
    sweep([(-0.01, -0.012), (0.03, 0.0), (0.03, 0.012), (-0.01, 0.012)], ring, CHROME_M, plane_normal=tuple(nrm), name="crt_trim")
    # The game on screen: rows of invaders marching, a ship, a score line.
    frame = pivot("screen_frame", tuple(sc + nrm * 0.075 + up * 0.02))
    frame.rotation_euler = (-st, 0, 0)
    bpy.context.view_layer.update()
    march = pivot("invaders", (0, 0, 0))
    march.parent = frame
    sprite_cols = [(1.0, 0.3, 0.8), (0.3, 1.0, 1.0), (0.5, 1.0, 0.4)]
    local = []
    for r in range(3):
        for c in range(5):
            rows = SQUID if r == 0 else INVADER
            local.append((rows, (-0.26 + c * 0.13, 0, 0.2 - r * 0.1), sprite_cols[r], march))
    ship = pivot("ship", (0, 0, 0))
    ship.parent = frame
    local.append((SHIP, (0.0, 0, -0.24), (0.3, 1.0, 0.5), ship))
    for rows, pos, col, par in local:
        o = pixel_sprite(rows, 0.0095, pos, glow(col, 3.0), name="sprite")
        o.parent = par
    shot = cube((0.008, 0.002, 0.04), (0.0, 0.0, -0.1), glow((1.0, 1.0, 0.6), 4.0), bevel=0.0, name="shot")
    shot.parent = ship
    shot.matrix_parent_inverse.identity()
    shot.location = (0, 0, -0.15)
    sc_txt = text("SCORE 01980   HI 99999", 0.035, (0, 0, 0.3), glow((1.0, 1.0, 1.0), 2.5), extrude=0.0, rot=(math.pi / 2, 0, 0), res=1)
    sc_txt.parent = frame
    sc_txt.matrix_parent_inverse.identity()
    sc_txt.location = (0, 0.0, 0.3)
    sc_txt.rotation_euler = (math.pi / 2, 0, 0)
    for o in [ob for ob in bpy.context.scene.objects if ob.parent in (march, ship) and ob.type == "MESH"]:
        o.matrix_parent_inverse.identity()
    later(key, march, "idle", "location", [(0, -0.05), (30, 0.05), (60, -0.05)], index=0, interp="LINEAR")
    later(key, ship, "idle", "location", [(0, 0.12), (20, -0.1), (40, 0.2), (60, 0.12)], index=0)
    later(key, shot, "idle", "location", [(0, -0.15), (29, 0.35), (30, -0.15), (59, 0.35), (60, -0.15)], index=2, interp="LINEAR")
    # Speaker panel and the marquee box with a bulb-ringed sign.
    sp_t = math.atan2(-0.3 + 0.1, 2.2 - 2.12)
    cube((2 * W, 0.06, 0.1), (0, -0.2, 2.16), lam, rot=(0, 0, 0), bevel=0.0)
    for k in range(9):
        cyl(0.012, 0.01, (-0.4 + k * 0.1, -0.235, 2.16), PLASTIC_BLACK, rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0)
    MY = -0.335
    cube((2 * W, 0.04, 0.54), (0, MY + 0.03, 2.47), pbr("plastic", (0.06, 0.02, 0.12), rough=0.3, name="sign"), bevel=0.0)
    text("BOMBFALL", 0.2, (0, MY - 0.005, 2.49), glow((1.0, 0.35, 0.75), 4.5), extrude=0.015, res=2)
    text("★ ARCADE ★", 0.07, (0, MY - 0.005, 2.33), glow((0.3, 0.95, 1.0), 4.0), extrude=0.0, res=1)
    bulbs = []
    for i in range(22):
        t = i / 22.0
        per = 2 * (1.12 + 0.44)
        d = t * per
        if d < 1.12:
            x, z = -0.56 + d, 2.23
        elif d < 1.56:
            x, z = 0.56, 2.23 + (d - 1.12)
        elif d < 2.68:
            x, z = 0.56 - (d - 1.56), 2.67
        else:
            x, z = -0.56, 2.67 - (d - 2.68)
        bulbs.append(sphere(0.024, (x, MY - 0.01, z), anim_m((1.0, 0.8, 0.3), "marquee", 4.0), segments=6, rings=4))
    join(bulbs, "marquee")
    cube((2 * W + 0.1, 0.12, 0.04), (0, MY + 0.03, 2.78), lam, bevel=0.01)
    place(1.0, 0.0)


# ============================================================ slot machine ==
def _reel_symbol(kind, m7, mbar, mcherry, mstem, mbell, mgem):
    """One reel symbol built facing -Y around the origin (about 0.2 m)."""
    out = []
    if kind == "7":
        out.append(text("7", 0.2, (0, 0, 0), m7, extrude=0.0, font=FONT_SERIF, res=2))
    elif kind == "bar":
        out.append(cube((0.2, 0.004, 0.08), (0, 0.002, 0), PLASTIC_BLACK, bevel=0.0))
        out.append(text("BAR", 0.065, (0, -0.002, -0.002), mbar, extrude=0.0, res=1))
    elif kind == "cherry":
        for dx, dz in ((-0.045, -0.04), (0.045, -0.05)):
            out.append(sphere(0.045, (dx, 0.0, dz), mcherry, scale=(1, 0.5, 1), segments=10, rings=6))
            out.append(tube([(dx, -0.005, dz + 0.04), (dx * 0.4, -0.005, dz + 0.1), (0.02, -0.005, 0.08)], 0.008, mstem, verts=4))
        out.append(sphere(0.03, (0.05, 0.0, 0.08), mstem, scale=(1.4, 0.4, 0.7), segments=8, rings=4))
    elif kind == "bell":
        b = lathe([(0.0, -0.07), (0.08, -0.07), (0.075, -0.05), (0.05, 0.0), (0.045, 0.05), (0.02, 0.075), (0.0, 0.08)], mbell, segs=12)
        b.scale = (1, 0.5, 1)
        out.append(b)
        out.append(sphere(0.02, (0, -0.01, -0.08), mbell, segments=6, rings=4))
    elif kind == "gem":
        g = cone(0.08, 0.09, (0, 0, -0.02), mgem, rot=(math.pi, 0, 0), verts=6, bevel=0.0)
        g.scale = (1, 0.4, 1)
        out.append(g)
        t = cyl(0.08, 0.04, (0, 0, 0.045), mgem, r2=0.05, verts=6, bevel=0.0)
        t.scale = (1, 0.4, 1)
        out.append(t)
    return out


def slot_machine():
    """A classic casino slot at 1.4x life size: candy-red metal-flake cabinet
    with chrome trim, an arched topper with a JACKPOT sign ringed by chasing
    bulbs ("marquee"), a candle light on top, a reel window with three
    drums ("reel_1".."reel_3", spun by the game about X) carrying 7s, BARs,
    cherries, bells and gems, a lit pay table, a button deck, a chrome coin
    tray and a side "lever" with a red ball (pulled by the game).
    1.35 (1.6 with the lever) x 1.2 x 2.6 m."""
    mats_reset()
    candy = pbr("paint", (0.5, 0.01, 0.04), rough=0.18, metal=0.45, wear=0.15, grime=0.25, edge=0.015, name="candy_red")
    dark = pbr("paint", (0.03, 0.02, 0.04), rough=0.35, wear=0.3, grime=0.3, edge=0.012, name="slot_dark")
    reel_m = pbr("plastic", (0.95, 0.93, 0.88), rough=0.35, wear=0.1, grime=0.2, name="reel_face")
    m7 = pbr("plastic", (0.85, 0.02, 0.05), rough=0.3, wear=0.0, name="sym_red")
    mbar = pbr("plastic", (0.98, 0.98, 0.98), rough=0.4, wear=0.0, name="sym_white")
    mcherry = pbr("plastic", (0.8, 0.0, 0.08), rough=0.15, wear=0.0, name="sym_cherry")
    mstem = pbr("plastic", (0.1, 0.5, 0.1), rough=0.4, wear=0.0, name="sym_stem")
    mgem = pbr("plastic", (0.1, 0.6, 1.0), rough=0.1, wear=0.0, name="sym_gem")
    glass_m = pbr("glass", (0.8, 0.9, 1.0), alpha=0.15, name="reel_glass")
    W = 0.66
    # Base cabinet with chrome kick and trims.
    soft_box((2 * W, 1.0, 0.12), (0, 0.02, 0.06), CHROME_M, r=0.3, cuts=1)
    soft_box((2 * W, 1.0, 1.0), (0, 0.02, 0.62), candy, r=0.12, cuts=2, name="base")
    soft_box((2 * W - 0.04, 0.9, 0.84), (0, 0.06, 1.52), candy, r=0.12, cuts=2, name="head")
    for z in (1.1, 1.95):
        cube((2 * W + 0.02, 1.02, 0.035), (0, 0.02, z), CHROME_M, bevel=0.008)
    for sx in (-1, 1):
        cube((0.035, 0.035, 1.85), (sx * (W + 0.003), -0.48, 1.03), CHROME_M, bevel=0.008)
    # Belly glass pay table.
    cube((1.0, 0.03, 0.4), (0, -0.49, 0.58), BLACK_GLASS, bevel=0.01)
    cube((1.06, 0.02, 0.46), (0, -0.475, 0.58), CHROME_M, bevel=0.01)
    text("777", 0.14, (-0.24, -0.51, 0.64), glow((1.0, 0.15, 0.2), 4.0), extrude=0.0, font=FONT_SERIF, res=2)
    text("= 500", 0.08, (0.2, -0.51, 0.64), glow((1.0, 0.85, 0.3), 3.5), extrude=0.0, res=1)
    text("BAR BAR BAR = 100", 0.055, (0, -0.51, 0.49), glow((0.4, 1.0, 1.0), 3.0), extrude=0.0, res=1)
    # Coin tray.
    lathe([(0.0, 0.0), (0.18, 0.0), (0.2, 0.08), (0.19, 0.09), (0.165, 0.02), (0.0, 0.02)], CHROME_M, segs=20, scale=(1.8, 1.0),
          loc=(0, -0.5, 0.18), name="tray")
    cube((0.7, 0.2, 0.12), (0, -0.43, 0.28), CHROME_M, bevel=0.02)
    for k in range(3):
        cyl(0.05, 0.012, (-0.16 + k * 0.16, -0.54, 0.206), GOLD_M, verts=14, bevel=0.0)         # a few coins
    # Button deck.
    extrude_profile([(-0.48, 1.12), (-0.62, 1.12), (-0.62, 1.16), (-0.46, 1.24), (-0.36, 1.24), (-0.36, 1.12)], -W + 0.02, W - 0.02, dark, name="deck")
    dt = math.atan2(1.24 - 1.16, 0.62 - 0.46)
    for i, (x, col, w) in enumerate(((-0.42, (1.0, 0.85, 0.2), 0.14), (-0.2, (1.0, 0.85, 0.2), 0.14), (0.28, (0.3, 1.0, 0.4), 0.3))):
        cube((w, 0.08, 0.035), (x, -0.54, 1.215), glow(col, 2.5), rot=(dt, 0, 0), bevel=0.01)
    text("SPIN", 0.045, (0.28, -0.62, 1.15), glow((0.3, 1.0, 0.4), 3.0), extrude=0.0, res=1)
    cube((0.12, 0.03, 0.2), (0.05, -0.49, 1.0), CHROME_M, bevel=0.01)                            # coin slot plate
    cube((0.015, 0.01, 0.1), (0.05, -0.51, 1.0), glow((1.0, 0.1, 0.1), 5.0), bevel=0.0)
    cube((0.24, 0.03, 0.14), (-0.3, -0.49, 0.95), PLASTIC_BLACK, bevel=0.01)                     # bill acceptor
    cube((0.18, 0.01, 0.015), (-0.3, -0.51, 0.97), glow((0.2, 1.0, 0.4), 5.0), bevel=0.0)
    # Reel window: chrome surround, dark box, three drums, payline, glass.
    RZ, RY, RR = 1.53, -0.2, 0.3
    soft_box((1.14, 0.06, 0.62), (0, -0.44, RZ), CHROME_M, r=0.3, cuts=1, name="surround")
    cube((1.0, 0.36, 0.5), (0, -0.28, RZ), pbr("plastic", (0.01, 0.01, 0.012), rough=0.8, name="reel_box"), bevel=0.0)
    cube((1.02, 0.01, 0.52), (0, -0.475, RZ), glass_m, bevel=0.0)
    cube((1.0, 0.005, 0.012), (0, -0.47, RZ), glow((1.0, 0.1, 0.15), 5.0), bevel=0.0)             # payline
    kinds = ["7", "cherry", "bar", "bell", "7", "gem", "bar", "cherry"]
    for j in range(3):
        x = (j - 1) * 0.31
        r = pivot("reel_%d" % (j + 1), (x, RY, RZ))
        cyl(RR, 0.26, (x, RY, RZ), reel_m, rot=(0, math.pi / 2, 0), verts=24, bevel=0.0, parent=r)
        for side in (-1, 1):
            cyl(RR + 0.012, 0.012, (x + side * 0.13, RY, RZ), CHROME_M, rot=(0, math.pi / 2, 0), verts=24, bevel=0.0, parent=r)
        for k in range(8):
            a = TAU * k / 8 + j * math.pi / 2
            sym = _reel_symbol(kinds[(k + j * 3) % 8], m7, mbar, mcherry, mstem, GOLD_M, mgem)
            if not sym:
                continue
            o = join(sym, "sym") if len(sym) > 1 else sym[0]
            bpy.context.view_layer.update()
            M = (mathutils.Matrix.Translation((x, RY, RZ)) @ mathutils.Matrix.Rotation(-a, 4, "X") @
                 mathutils.Matrix.Translation((0, -RR - 0.004, 0)))
            o.matrix_world = M @ o.matrix_world
            attach(o, r)
    # Arched topper with the JACKPOT sign and a ring of chasing bulbs.
    TZ = 2.0
    arch = []
    for i in range(17):
        a = math.pi * i / 16
        arch.append((math.cos(a) * 0.62, math.sin(a) * 0.42))
    bm = bmesh.new()
    ring_pts = [(-0.62, 0.0)] + [(x, z) for x, z in reversed(arch)][1:-1] + [(0.62, 0.0)]
    front = [bm.verts.new((x, -0.36, TZ + z + 0.1)) for x, z in [(0.62, -0.1)] + [(x, z) for x, z in arch] + [(-0.62, -0.1)]]
    back = [bm.verts.new((x, 0.4, TZ + z + 0.1)) for x, z in [(0.62, -0.1)] + [(x, z) for x, z in arch] + [(-0.62, -0.1)]]
    bm.faces.new(front)
    bm.faces.new(list(reversed(back)))
    for i in range(len(front)):
        k = (i + 1) % len(front)
        bm.faces.new([front[i], front[k], back[k], back[i]])
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    _obj("topper", bm, dark, smooth=False, bevel=0.015)
    sweep([(0.0, -0.02), (0.04, 0.0), (0.0, 0.02)], [(x, -0.37, TZ + 0.1 + z) for x, z in arch] + [(-0.62, -0.37, TZ), (0.62, -0.37, TZ)],
          CHROME_M, closed=True, plane_normal=(0, 1, 0), name="topper_trim")
    text("JACKPOT", 0.17, (0, -0.375, TZ + 0.2), glow((1.0, 0.8, 0.25), 5.0), extrude=0.01, font=FONT_SERIF, res=2)
    text("★ 7 7 7 ★", 0.09, (0, -0.375, TZ + 0.37), glow((1.0, 0.2, 0.35), 5.0), extrude=0.0, res=1)
    bulbs = []
    for i in range(1, 16):
        a = math.pi * i / 16
        bulbs.append(sphere(0.028, (math.cos(a) * 0.56, -0.39, TZ + 0.1 + math.sin(a) * 0.37), anim_m((1.0, 0.85, 0.35), "marquee", 4.0),
                            segments=6, rings=4))
    for i in range(7):
        bulbs.append(sphere(0.028, (-0.5 + i * (1.0 / 6), -0.39, TZ + 0.06), anim_m((1.0, 0.85, 0.35), "marquee", 4.0), segments=6, rings=4))
    join(bulbs, "marquee")
    # Candle light on top: red over white, with a chrome cap.
    lathe([(0.0, TZ + 0.48), (0.08, TZ + 0.48), (0.08, TZ + 0.5), (0.0, TZ + 0.5)], CHROME_M, segs=14)
    lathe([(0.0, TZ + 0.5), (0.065, TZ + 0.5), (0.065, TZ + 0.54), (0.0, TZ + 0.54)], glow((1.0, 0.95, 0.9), 3.0), segs=14)
    lathe([(0.0, TZ + 0.54), (0.065, TZ + 0.54), (0.065, TZ + 0.58), (0.0, TZ + 0.58)], glow((1.0, 0.1, 0.15), 4.0), segs=14)
    lathe([(0.0, TZ + 0.58), (0.075, TZ + 0.58), (0.06, TZ + 0.6), (0.0, TZ + 0.605)], CHROME_M, segs=14)
    # Lever on the right side: a chrome hub (static) and the arm (pivot).
    LX, LY, LZ = W + 0.05, -0.05, 1.36
    cyl(0.12, 0.1, (LX, LY, LZ), CHROME_M, rot=(0, math.pi / 2, 0), verts=20)
    cube((0.06, 0.28, 0.3), (W + 0.02, LY, LZ), CHROME_M, bevel=0.02)
    lv = pivot("lever", (LX + 0.06, LY, LZ))
    cyl(0.07, 0.06, (LX + 0.09, LY, LZ), CHROME_M, rot=(0, math.pi / 2, 0), verts=16, parent=lv)
    rod((LX + 0.09, LY, LZ), (LX + 0.13, LY + 0.02, LZ + 0.9), 0.028, CHROME_M, verts=10, parent=lv)
    sphere(0.1, (LX + 0.135, LY + 0.02, LZ + 0.95), pbr("plastic", (0.85, 0.02, 0.04), rough=0.12, wear=0.1, name="knob_red"),
           segments=16, rings=10, parent=lv)
    place(1.0, 0.0)


# ================================================================ desktop ==
def _fan(centre, r, col, name, frame_m, blade_m, axis="Y"):
    """An RGB case fan facing -Y: a square frame and glowing ring (static)
    plus a pivot with the hub and blades (spun in the idle clip)."""
    cx, cy, cz = centre
    static = [soft_box((2 * r + 0.06, 0.06, 2 * r + 0.06), (cx, cy + 0.03, cz), frame_m, r=0.25, cuts=1),
              torus(r - 0.01, 0.018, (cx, cy - 0.005, cz), glow(col, 5.0), rot=(math.pi / 2, 0, 0), major_segments=24, minor_segments=4)]
    p = pivot(name, (cx, cy, cz))
    parts = [cyl(r * 0.3, 0.04, (cx, cy, cz), frame_m, rot=(math.pi / 2, 0, 0), verts=12, bevel=0.0)]
    for k in range(7):
        a = TAU * k / 7
        b = cube((r * 0.62, 0.012, r * 0.28), (cx + math.cos(a) * r * 0.58, cy, cz + math.sin(a) * r * 0.58), blade_m, bevel=0.0)
        b.rotation_euler = (0.35, -a, 0)
        parts.append(b)
    blades = join(parts, name + "_blades")
    attach(blades, p)
    later(spin, p, "idle", "Y", seconds=2.0, turns=-3)
    return static, p


def desktop_parts():
    """The gamer workstation in three pieces, each authored around the
    origin of the body that carries it in desktop.tscn:
      desk    - 3.9 x 1.8 m carbon top on a drawer pedestal and a panel leg,
                RGB edge light, mechanical keyboard, mouse, mat, headphones,
                energy drink (body at the origin, top at z = 2.0)
      monitor - a curved ultrawide on a V stand, the screen an animated
                shader with code and a game window (body at z = 2.0)
      tower   - a glass-fronted case with three spinning RGB fans, a lit GPU
                and RAM (body at x = 2.7)
    Returns {name: [objects]} and the fan pivots to parent to the tower."""
    mats_reset()
    carbon = pbr("plastic", (0.02, 0.02, 0.025), rough=0.28, bump=0.6, scale=0.15, edge=0.02, name="carbon")
    steel = pbr("paint", (0.03, 0.03, 0.035), rough=0.4, wear=0.4, edge=0.015, name="black_steel")
    red = pbr("paint", (0.6, 0.02, 0.1), rough=0.3, wear=0.3, name="accent_red")
    keycap = pbr("plastic", (0.05, 0.05, 0.06), rough=0.4, wear=0.3, name="keycap")
    mat_m = pbr("fabric", (0.04, 0.03, 0.06), bump=0.2, name="desk_mat")
    case_m = pbr("paint", (0.02, 0.02, 0.025), rough=0.3, wear=0.25, edge=0.02, name="case")
    board = pbr("plastic", (0.02, 0.05, 0.04), rough=0.5, name="pcb")
    blade_m = pbr("glass", (0.8, 0.85, 1.0), alpha=0.35, name="fan_blade")
    glass = pbr("glass", (0.2, 0.2, 0.3), alpha=0.18, name="tinted_glass")
    parts = {}
    # ---- desk
    d = []
    d.append(soft_box((3.9, 1.8, 0.12), (0, 0, 1.94), carbon, r=0.3, cuts=2, name="desk_top"))
    d.append(tube([(-1.9, -0.905, 1.89), (1.9, -0.905, 1.89)], 0.02, glow((0.9, 0.15, 1.0), 5.0), verts=5))
    # drawer pedestal (left) and panel leg with a lit logo (right)
    d.append(soft_box((1.0, 1.6, 1.86), (-1.38, 0.05, 0.94), steel, r=0.08, cuts=1))
    for k, z in enumerate((1.5, 0.95, 0.4)):
        d.append(soft_box((0.9, 0.04, 0.46 if k < 2 else 0.6), (-1.38, -0.76, z if k < 2 else 0.36), steel, r=0.2, cuts=1))
        d.append(cube((0.5, 0.03, 0.03), (-1.38, -0.795, (z if k < 2 else 0.36) + 0.12), glow((0.2, 0.9, 1.0), 4.0), bevel=0.0))
    d.append(soft_box((0.12, 1.6, 1.86), (1.82, 0.05, 0.94), steel, r=0.3, cuts=1))
    d.append(cube((0.7, 0.1, 0.1), (1.6, 0.05, 0.05), steel, bevel=0.01))
    d.append(cube((0.02, 0.9, 0.9), (1.755, 0.05, 1.0), red, bevel=0.0))
    d.append(text("BF", 0.35, (1.74, 0.05, 1.0), glow((1.0, 0.2, 0.5), 4.0), rot=(math.pi / 2, 0, -math.pi / 2), extrude=0.0, res=2))
    d.append(soft_box((1.2, 1.5, 0.12), (1.1, 0.05, 1.8), steel, r=0.3, cuts=1))             # under-desk cable tray
    # desk mat, keyboard, mouse
    d.append(soft_box((2.2, 0.8, 0.02), (0.35, -0.42, 2.01), mat_m, r=0.5, cuts=1))
    d.append(tube([(-0.75, -0.82, 2.012), (1.45, -0.82, 2.012), (1.45, -0.02, 2.012), (-0.75, -0.02, 2.012), (-0.75, -0.82, 2.012)], 0.008,
                  glow((0.2, 0.9, 1.0), 4.0), verts=4))
    d.append(soft_box((1.24, 0.42, 0.06), (0.1, -0.45, 2.05), steel, r=0.3, cuts=1, name="keyboard"))
    d.append(cube((1.2, 0.38, 0.01), (0.1, -0.45, 2.075), glow((0.8, 0.2, 1.0), 2.5), bevel=0.0))
    keys = []
    for row in range(5):
        for col in range(14):
            kx = -0.47 + col * 0.082 + (0.03 if row % 2 else 0)
            if kx > 0.62:
                continue
            ky = -0.6 + row * 0.075
            w = 0.07 if not (row == 0 and 4 <= col <= 9) else 0.07
            keys.append(cube((w, 0.062, 0.045), (kx, ky, 2.1), keycap, bevel=0.0))
    keys.append(cube((0.45, 0.062, 0.045), (0.1, -0.675, 2.1), keycap, bevel=0.0))        # space bar
    d.append(join(keys, "keys"))
    d.append(soft_box((0.14, 0.24, 0.07), (1.05, -0.45, 2.055), steel, r=0.9, puff=0.3, cuts=2, name="mouse"))
    d.append(cube((0.02, 0.06, 0.01), (1.05, -0.52, 2.09), glow((1.0, 0.2, 0.5), 4.0), bevel=0.0))
    # headphone stand with headphones, an energy drink
    d.append(lathe([(0.0, 2.0), (0.14, 2.0), (0.14, 2.02), (0.03, 2.04), (0.025, 2.5), (0.0, 2.5)], steel, segs=14, loc=(-1.35, -0.2, 0)))
    d.append(soft_box((0.16, 0.08, 0.04), (-1.35, -0.2, 2.52), steel, r=0.5, cuts=1))
    arc = [(-1.35 + math.cos(a) * 0.0, -0.2 + math.cos(a) * 0.2, 2.34 + math.sin(a) * 0.2) for a in [math.pi * k / 10 for k in range(11)]]
    d.append(tube(arc, 0.025, steel, verts=6))
    for sy in (-1, 1):
        d.append(soft_box((0.12, 0.08, 0.18), (-1.35, -0.2 + sy * 0.21, 2.3), steel, r=0.9, cuts=2))
        d.append(torus(0.06, 0.012, (-1.35, -0.2 + sy * 0.255, 2.3), glow((0.2, 0.9, 1.0), 4.0), rot=(math.pi / 2, 0, 0), major_segments=12,
                       minor_segments=4))
    d.append(lathe([(0.0, 2.0), (0.06, 2.0), (0.065, 2.02), (0.065, 2.26), (0.05, 2.28), (0.0, 2.28)], pbr("metal", (0.2, 0.9, 0.3), rough=0.25,
                   name="can"), segs=14, loc=(-0.95, -0.55, 0)))
    parts["desk"] = d
    # ---- monitor (z = 0 is the desk top)
    m = []
    R = 3.2
    MY = 0.3

    def arc_xy(u, off):
        """A monitor curved around a centre in front of it (edges come
        towards the viewer); off > 0 is further back."""
        a = (u - 0.5) * 2.36 / R
        return math.sin(a) * (R + off), MY - R + math.cos(a) * (R + off)

    def screen_pt(u, v):
        x, y = arc_xy(u, 0.0)
        return (x, y, 0.52 + v * 1.06)

    def shell_pt(u, v, off=0.0):
        x, y = arc_xy(u, off)
        return (x, y, 0.47 + v * 1.16)
    shell = sheet(lambda u, v: shell_pt(u - 0.012 + u * 0.024, v, 0.07), 24, 2, steel, thick=0.0, name="monitor_shell")
    sm = shell.modifiers.new("solid", "SOLIDIFY")
    sm.thickness = 0.06
    sm.offset = 0.0
    m.append(shell)
    m.append(sheet(screen_pt, 24, 3, anim_m((0.05, 0.12, 0.2), "screen", 1.3), thick=0.0, name="monitor_screen"))
    # code editor lines on the left, a game window on the right
    rnd = random.Random(4)
    code_cols = [(0.3, 1.0, 0.5), (1.0, 0.4, 0.8), (0.4, 0.8, 1.0), (1.0, 0.8, 0.3)]
    for i in range(12):
        v = 0.88 - i * 0.07
        ind = 0.03 * rnd.randint(0, 3)
        L = rnd.uniform(0.08, 0.3)
        c = code_cols[rnd.randint(0, 3)]
        u0 = 0.05 + ind
        pts0 = [screen_pt(u0 + (L * k / 3), v) for k in range(4)]
        pts1 = [screen_pt(u0 + (L * k / 3), v + 0.025) for k in range(4)]
        o = loft([[(p[0], p[1] - 0.006, p[2]) for p in pts0], [(p[0], p[1] - 0.006, p[2]) for p in pts1]], glow(c, 3.0), closed=False,
                 cap0=False, cap1=False, name="code")
        m.append(o)
    win = [[screen_pt(0.52 + 0.43 * k / 6, 0.12)[0:1] + (screen_pt(0.52 + 0.43 * k / 6, 0.12)[1] - 0.005, screen_pt(0.52, 0.12)[2]) for k in range(7)],
           [screen_pt(0.52 + 0.43 * k / 6, 0.12)[0:1] + (screen_pt(0.52 + 0.43 * k / 6, 0.12)[1] - 0.005, screen_pt(0.52, 0.9)[2]) for k in range(7)]]
    m.append(loft(win, glow((0.35, 0.1, 0.6), 2.0), closed=False, cap0=False, cap1=False, name="game_win"))
    sun = screen_pt(0.735, 0.55)
    m.append(sphere(0.16, (sun[0], sun[1] - 0.012, sun[2]), glow((1.0, 0.45, 0.6), 3.5), scale=(1, 0.05, 1), segments=16, rings=8))
    for k in range(4):
        a0 = screen_pt(0.53, 0.35 - k * 0.07)
        a1 = screen_pt(0.94, 0.35 - k * 0.07)
        m.append(rod((a0[0], a0[1] - 0.015, a0[2]), (a1[0], a1[1] - 0.015, a1[2]), 0.006, glow((0.2, 0.9, 1.0), 4.0), verts=4))
    m.append(tube([shell_pt(k / 12, 0.0, -0.08)[0:2] + (0.46,) for k in range(13)], 0.012, glow((1.0, 0.2, 0.6), 5.0), verts=4))
    # V stand
    m.append(cube((0.16, 0.12, 0.62), (0, MY + 0.2, 0.36), steel, rot=(-0.15, 0, 0), bevel=0.02))
    for sx in (-1, 1):
        m.append(rod((0, MY + 0.28, 0.03), (sx * 0.55, MY - 0.2, 0.02), 0.035, CHROME_M, verts=8))
    m.append(cyl(0.09, 0.05, (0, MY + 0.28, 0.025), CHROME_M, verts=14))
    parts["monitor"] = m
    # ---- tower (at its own origin, glass front facing -Y)
    t = []
    TW, TD, TH = 0.9, 1.2, 2.1
    t.append(soft_box((TW, TD, 0.1), (0, 0, 0.05), case_m, r=0.3, cuts=1))
    t.append(soft_box((TW, TD, 0.12), (0, 0, TH - 0.06), case_m, r=0.3, cuts=1))
    t.append(soft_box((0.06, TD, TH), (TW / 2 - 0.03, 0, TH / 2), case_m, r=0.3, cuts=1))
    t.append(cube((0.02, TD - 0.1, TH - 0.2), (-TW / 2 + 0.02, 0, TH / 2), glass, bevel=0.0))       # side glass (towards the desk)
    t.append(cube((TW - 0.08, 0.02, TH - 0.2), (0, -TD / 2 + 0.01, TH / 2), glass, bevel=0.0))       # front glass
    for sx in (-1, 1):
        t.append(cube((0.05, 0.05, TH), (sx * (TW / 2 - 0.025), -TD / 2 + 0.025, TH / 2), case_m, bevel=0.01))
    t.append(cube((TW - 0.04, 0.04, TH - 0.1), (0, TD / 2 - 0.04, TH / 2), board, bevel=0.0))       # back wall / board
    # PSU shroud, GPU, RAM, cooler behind the fans
    t.append(soft_box((TW - 0.1, TD - 0.1, 0.4), (0, 0.02, 0.3), case_m, r=0.2, cuts=1))
    t.append(text("BOMB", 0.14, (0, -TD / 2 + 0.05, 0.3), glow((1.0, 0.25, 0.6), 4.0), extrude=0.0, res=1))
    t.append(soft_box((TW - 0.2, 0.75, 0.18), (0, 0.15, 0.85), steel, r=0.3, cuts=1, name="gpu"))
    t.append(cube((TW - 0.22, 0.02, 0.03), (0, -0.23, 0.9), glow((0.2, 0.9, 1.0), 4.0), bevel=0.0))
    for k in range(4):
        t.append(cube((0.05, 0.3, 0.02), (-0.2 + k * 0.1, 0.35, 1.7), glow((0.8, 0.3, 1.0), 3.0), bevel=0.0))
        t.append(cube((0.03, 0.28, 0.25), (-0.2 + k * 0.1, 0.35, 1.56), steel, bevel=0.0))
    t.append(cyl(0.15, 0.1, (0.0, 0.1, 1.35), steel, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.0))
    t.append(torus(0.14, 0.015, (0.0, 0.05, 1.35), glow((1.0, 0.3, 0.7), 5.0), rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=4))
    fans = []
    for k, z in enumerate((0.72, 1.18, 1.64)):
        st, p = _fan((0.0, -TD / 2 + 0.1, z), 0.2, [(1.0, 0.2, 0.6), (0.6, 0.2, 1.0), (0.2, 0.8, 1.0)][k], "fan_%d" % (k + 1), case_m, blade_m)
        t.extend(st)
        fans.append(p)
    t.append(cube((0.12, 0.02, 0.03), (0.3, -TD / 2 - 0.005, TH - 0.2), glow((0.3, 1.0, 0.4), 5.0), bevel=0.0))   # power LED
    parts["tower"] = t
    return parts, fans


# ================================================================= statue ==
def metaball_mesh(elements, m, resolution=0.07, threshold=0.6, tris=None, name="meta"):
    """Blend spheres/ellipsoids [(co, radius[, (sx, sy, sz)])] into one smooth
    mesh (organic forms), optionally decimated to about `tris` triangles."""
    mb = bpy.data.metaballs.new(name)
    mb.resolution = resolution
    mb.render_resolution = resolution
    mb.threshold = threshold
    for e in elements:
        co, r = e[0], e[1]
        el = mb.elements.new(type="ELLIPSOID" if len(e) > 2 else "BALL")
        el.co = co
        el.radius = r
        if len(e) > 2:
            el.size_x, el.size_y, el.size_z = e[2]
    o = bpy.data.objects.new(name, mb)
    common._link(o)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    o.name = name
    if tris:
        n = sum(len(p.vertices) - 2 for p in o.data.polygons)
        if n > tris:
            d = o.modifiers.new("dec", "DECIMATE")
            d.ratio = tris / n
            bpy.ops.object.modifier_apply(modifier=d.name)
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.materials.clear()
    o.data.materials.append(common.mat(m))
    return o


def _limb(pts, r0, r1, step=0.55):
    """Metaball spheres along a polyline, radius r0 -> r1."""
    P = [V(p) for p in pts]
    total = sum((b - a).length for a, b in zip(P, P[1:]))
    out = []
    d = 0.0
    for a, b in zip(P, P[1:]):
        seg = (b - a).length
        t = 0.0
        while t <= seg:
            f = (d + t) / total
            r = r0 + (r1 - r0) * f
            out.append((tuple(a + (b - a) * (t / seg)), r))
            t += max(0.04, r * step)
        d += seg
    out.append((tuple(P[-1]), r1))
    return out


def statue_parts():
    """The Disco Droid: a chrome android striking a disco point on a black
    marble plinth, in three pieces the game makes separate bodies:
      base - nero marble plinth with gilt mouldings, a brass plaque and a
             cyan neon under the cornice (0..1.95 m)
      body - the metaball-sculpted chrome figure with neon joint rings and a
             glowing chest core that pulses (1.95..~8 m)
      head - a crested helmet head with a black visor and a cyan eye line
    All authored in place (every body sits at the origin in statue.tscn)."""
    mats_reset()
    marble = pbr("marble", (0.03, 0.026, 0.036), color2=(0.22, 0.2, 0.24), rough=0.12, edge=0.012, scale=2.5, name="nero_marble")
    gilt = pbr("gold", (0.95, 0.68, 0.28), rough=0.25, grime=0.5, edge=0.01, name="gilt")
    chrome = pbr("chrome", (0.86, 0.87, 0.92), rough=0.06, grime=0.1, edge=0.01, name="android_chrome")
    visor_m = pbr("plastic", (0.01, 0.01, 0.015), rough=0.04, wear=0.0, grime=0.0, bump=0.0, name="visor")
    parts = {}
    # ---- base
    b = []
    b.append(soft_box((3.6, 2.2, 0.3), (0, 0, 0.15), marble, r=0.2, cuts=1))
    b.append(soft_box((3.1, 1.8, 1.4), (0, 0, 0.98), marble, r=0.06, cuts=1))
    b.append(soft_box((3.5, 2.1, 0.28), (0, 0, 1.81), marble, r=0.25, cuts=1))
    for z, (w, dpt) in ((0.33, (3.2, 1.9)), (1.64, (3.24, 1.94))):
        b.append(sweep([(0.0, -0.04), (0.05, -0.02), (0.06, 0.02), (0.02, 0.05), (0.0, 0.05)],
                       [(-w / 2, -dpt / 2, z), (w / 2, -dpt / 2, z), (w / 2, dpt / 2, z), (-w / 2, dpt / 2, z)], gilt, name="moulding"))
    b.append(tube([(-1.62, -0.99, 1.6), (1.62, -0.99, 1.6)], 0.02, glow(CYAN, 5.0), verts=5))
    b.append(soft_box((1.5, 0.04, 0.45), (0, -0.91, 1.0), gilt, r=0.3, cuts=1, name="plaque"))
    b.append(text("THE DISCO DROID", 0.1, (0, -0.935, 1.07), pbr("plastic", (0.05, 0.03, 0.02), rough=0.5, name="engrave"), extrude=0.0, res=1))
    b.append(text("MMXXVI", 0.07, (0, -0.935, 0.92), pbr("plastic", (0.05, 0.03, 0.02), rough=0.5, name="engrave"), extrude=0.0, res=1))
    for sx in (-1, 1):
        b.append(sphere(0.03, (sx * 0.66, -0.94, 1.0), gilt, segments=6, rings=4))
    parts["base"] = b
    # ---- body
    Z = 1.95
    els = []
    els += [((0, 0.0, Z + 2.95), 0.62, (0.95, 0.62, 0.55)),          # pelvis
            ((0, 0.0, Z + 3.4), 0.55, (0.78, 0.55, 0.6)),            # waist
            ((0, -0.02, Z + 4.0), 0.72, (1.0, 0.62, 0.72)),          # chest
            ((0, 0.05, Z + 4.45), 0.6, (1.25, 0.6, 0.45))]           # shoulder girdle
    for sx in (-1, 1):
        els.append(((sx * 0.25, -0.26, Z + 4.1), 0.34))             # pecs
    els += _limb([(0, 0, Z + 4.55), (0, 0, Z + 4.95)], 0.26, 0.22)   # neck
    # legs: left straight, right bent out on tiptoe
    els += _limb([(-0.32, 0, Z + 2.85), (-0.36, -0.02, Z + 1.6), (-0.4, 0.02, Z + 0.3)], 0.42, 0.22)
    els += _limb([(-0.4, 0.0, Z + 0.25), (-0.45, -0.38, Z + 0.1)], 0.2, 0.16)
    els += _limb([(0.32, 0, Z + 2.85), (0.8, -0.35, Z + 1.75), (0.66, 0.05, Z + 0.4)], 0.42, 0.22)
    els += _limb([(0.66, 0.05, Z + 0.35), (0.8, -0.3, Z + 0.1)], 0.19, 0.15)
    # arms: right points up to the mirror ball, left hand on the hip
    els += [((0.9, 0.0, Z + 4.45), 0.34), ((-0.9, 0.0, Z + 4.4), 0.34)]
    els += _limb([(0.95, 0, Z + 4.5), (1.3, -0.1, Z + 5.15), (1.55, -0.15, Z + 5.75)], 0.27, 0.17)
    els += _limb([(1.55, -0.15, Z + 5.75), (1.65, -0.18, Z + 6.0)], 0.17, 0.09)
    els += _limb([(-0.95, 0, Z + 4.4), (-1.3, 0.12, Z + 3.7), (-0.78, -0.12, Z + 3.2)], 0.27, 0.17)
    els += [((-0.7, -0.14, Z + 3.1), 0.2, (1.0, 0.7, 1.3))]
    body = metaball_mesh(els, chrome, resolution=0.06, threshold=0.3, tris=4200, name="figure")
    bb = [body]
    # neon joint rings, belt and the chest core
    bb.append(torus(1.0, 0.03, (0, 0.0, Z + 3.35), glow(PINK, 5.0), scale=(0.5, 0.36, 1.0), major_segments=28, minor_segments=4))
    for c, r, rot in (((1.47, -0.14, Z + 5.52), 0.14, (0.35, -0.5, 0)), ((-0.84, -0.14, Z + 3.35), 0.14, (0.4, 1.1, 0)),
                      ((-0.4, 0.0, Z + 0.45), 0.2, (0, 0, 0)), ((0.68, 0.0, Z + 0.52), 0.2, (0.1, 0.2, 0))):
        bb.append(torus(r, 0.022, c, glow(CYAN, 5.0), rot=rot, major_segments=16, minor_segments=4))
    bb.append(lathe([(0.0, Z - 0.0), (1.0, Z), (1.02, Z + 0.03), (0.98, Z + 0.06), (0.0, Z + 0.06)], CHROME_M, segs=32))
    parts["body"] = bb
    core = pivot("core", (0, -0.5, Z + 4.02))
    cyl(0.14, 0.06, (0, -0.52, Z + 4.02), glow((1.0, 0.3, 0.7), 6.0), rot=(math.pi / 2, 0, 0), verts=6, bevel=0.0, parent=core)
    later(pulse, core, lo=0.8, hi=1.15)
    # ---- head
    HZ = Z + 5.35
    h = []
    h.append(sphere(0.46, (0, 0, HZ), chrome, scale=(0.88, 0.95, 1.1), segments=20, rings=14))
    h.append(sphere(0.4, (0, -0.2, HZ + 0.02), visor_m, scale=(0.95, 0.6, 0.42), segments=18, rings=10))
    h.append(torus(0.36, 0.014, (0, -0.215, HZ + 0.03), glow(CYAN, 6.0), scale=(1.0, 0.62, 0.3), major_segments=24, minor_segments=4))
    for sx in (-1, 1):
        h.append(cyl(0.12, 0.08, (sx * 0.4, 0, HZ), chrome, rot=(0, math.pi / 2, 0), verts=16))
        h.append(torus(0.1, 0.016, (sx * 0.445, 0, HZ), glow(PINK, 5.0), rot=(0, math.pi / 2, 0), major_segments=14, minor_segments=4))
    crest = sweep([(0.0, 0.0), (0.035, 0.0), (0.0, 0.0)], [(0, -0.28 + 0.56 * k / 8, HZ + 0.44 + 0.12 * math.sin(math.pi * k / 8)) for k in range(9)],
                  chrome, closed=False, plane_normal=(1, 0, 0), closed_profile=False, name="crest")
    h.append(sphere(0.12, (0, 0.02, HZ + 0.48), chrome, scale=(0.35, 2.2, 1.0), segments=12, rings=8))
    crest.hide_set(True)
    bpy.data.objects.remove(crest)
    parts["head"] = h
    return parts, [core]
