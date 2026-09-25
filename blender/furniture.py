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


# ------------------------------------------------------------ mesh helpers --
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
    return common._finish(o, m, bevel, smooth, None, parent, smooth_angle=angle)


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


def yaw_all(angle):
    """Rotate every top-level object about the origin's Z axis (and apply)."""
    rot = mathutils.Matrix.Rotation(angle, 4, "Z")
    for o in bpy.context.scene.objects:
        if o.parent is None:
            o.matrix_world = rot @ o.matrix_world


# ------------------------------------------------------------- animation --
def flicker(p, clip="idle", seconds=2.0, amount=0.25, seed=1, base=1.0, sway=0.0):
    """A candle-flame flicker on a pivot: irregular scale jitter (taller and
    thinner in turns) plus an optional sideways lean, seamless over the clip."""
    rnd = random.Random(seed)
    end = int(round(seconds * 30))
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


def rise(p, z0, z1, clip="idle", seconds=2.0, phase=0.0, size=1.0, drift=0.0):
    """A bubble on a pivot looping from z0 up to z1 (grows in, shrinks out)."""
    end = int(round(seconds * 30))
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
    keys = []
    for s in range(9):
        k = 0.5 + 0.5 * math.sin(TAU * s / 8 + phase)
        v = lo + (hi - lo) * k
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
        ((0.9, -1.4, 1.5), (1.0, 0.93, 0.88), 1400, 0.6),
        ((-1.6, -0.5, 0.6), (0.35, 0.8, 1.0), 500, 0.3),
        ((0.6, 1.3, 1.2), (1.0, 0.3, 0.8), 700, 0.3),
        ((0.0, -1.0, -0.2), (0.6, 0.3, 1.0), 120, 0.5),
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
