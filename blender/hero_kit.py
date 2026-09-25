# Helpers for the hero character (blender/player.py): lofted organic
# geometry, decals that hug an ellipsoid, procedural material masks baked
# into the atlas, an armature with parametric skin weights, pose-based clip
# authoring and contact-sheet renders. Built on top of common.py.
import math
import os
import subprocess

import bmesh
import bpy
import mathutils
from mathutils import Matrix, Quaternion, Vector

from common import FPS, key, mat  # noqa: F401

V = Vector


# ------------------------------------------------------------- geometry --
def mesh_object(name, verts, faces, m, smooth=True):
    """A mesh object from raw verts/faces with one material."""
    me = bpy.data.meshes.new(name)
    me.from_pydata([tuple(v) for v in verts], [], [tuple(f) for f in faces])
    me.validate()
    me.update()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    me.materials.append(mat(m))
    for p in me.polygons:
        p.use_smooth = smooth
    return o


def _frames(P, closed, ref, fixed):
    n = len(P)
    T = []
    for i in range(n):
        if closed:
            t = P[(i + 1) % n] - P[i - 1]
        else:
            t = P[min(i + 1, n - 1)] - P[max(i - 1, 0)]
        T.append(t.normalized())
    N = []
    if fixed:
        for i in range(n):
            r = V(ref[i]) if isinstance(ref, list) else V(ref)
            N.append((r - r.dot(T[i]) * T[i]).normalized())
        return T, N
    r0 = V(ref) if ref is not None else (V((0, 0, 1)) if abs(T[0].z) < 0.9 else V((1, 0, 0)))
    nrm = (r0 - r0.dot(T[0]) * T[0]).normalized()
    for i in range(n):
        nrm = (nrm - nrm.dot(T[i]) * T[i]).normalized()
        N.append(nrm.copy())
    return T, N


def tube(path, radii, m, segs=12, closed=False, caps=(True, True), ref=None, fixed=False,
         shape=None, name="tube", start=0.0, smooth=True, cap_depth=0.0):
    """A generalised cylinder along `path`. radii[i] is r or (r_n, r_b): the
    cross-section radius along the frame normal N (from `ref`) and the
    binormal T x N. `shape(i, angle)` scales a ring vertex (folds, flats).
    `fixed=True` derives N from `ref` at every point instead of parallel
    transport (use for closed loops); `ref` may be a list per point."""
    P = [V(p) for p in path]
    n = len(P)
    T, N = _frames(P, closed, ref, fixed)
    verts = []
    for i in range(n):
        B = T[i].cross(N[i])
        r = radii[i]
        rn, rb = (r, r) if not isinstance(r, (tuple, list)) else r
        for k in range(segs):
            a = 2 * math.pi * k / segs + start
            f = shape(i, a) if shape else 1.0
            verts.append(P[i] + (N[i] * math.cos(a) * rn + B * math.sin(a) * rb) * f)
    faces = []
    rows = n if closed else n - 1
    for i in range(rows):
        j = (i + 1) % n
        for k in range(segs):
            k2 = (k + 1) % segs
            faces.append((i * segs + k, i * segs + k2, j * segs + k2, j * segs + k))
    if not closed:
        for end, on in ((0, caps[0]), (n - 1, caps[1])):
            if not on:
                continue
            c = len(verts)
            d = -T[0] if end == 0 else T[-1]
            verts.append(P[end] + d * cap_depth)
            base = end * segs
            for k in range(segs):
                k2 = (k + 1) % segs
                tri = (c, base + k2, base + k) if end == 0 else (c, base + k, base + k2)
                faces.append(tri)
    return mesh_object(name, verts, faces, m, smooth)


def lathe(rings, m, segs=20, name="lathe", shape=None, caps=(True, True), axis_x=(1, 0, 0)):
    """Surface of revolution along Z: rings are (z, rx, ry[, cx, cy])."""
    path = [(r[3] if len(r) > 3 else 0.0, r[4] if len(r) > 4 else 0.0, r[0]) for r in rings]
    radii = [(r[1], r[2]) for r in rings]
    return tube(path, radii, m, segs=segs, ref=axis_x, fixed=True, shape=shape, caps=caps, name=name)


def ell_point(C, R, d, lift=0.0):
    """Point on the ellipsoid (centre C, radii R) along unit direction d, pushed out by `lift`."""
    d = V(d).normalized()
    return V(C) + V((d.x * (R[0] + lift), d.y * (R[1] + lift), d.z * (R[2] + lift)))


def ell_normal(R, d):
    d = V(d).normalized()
    return V((d.x / R[0], d.y / R[1], d.z / R[2])).normalized()


def patch(C, R, dir_fn, nu, nv, m, name="patch", lift=0.0, closed_u=False, lift_fn=None):
    """A quad grid on an ellipsoid: dir_fn(u, v) -> direction, u,v in [0, 1]."""
    verts = []
    us = nu if closed_u else nu + 1
    for i in range(us):
        for j in range(nv + 1):
            u, v = i / nu, j / nv
            d = dir_fn(u, v)
            extra = lift_fn(u, v) if lift_fn else 0.0
            verts.append(ell_point(C, R, d, lift + extra))
    faces = []
    for i in range(nu):
        i2 = (i + 1) % us
        for j in range(nv):
            a, b = i * (nv + 1) + j, i2 * (nv + 1) + j
            faces.append((a, b, b + 1, a + 1))
    o = mesh_object(name, verts, faces, m)
    fix_normals(o, outward_from=C)
    return o


def disc(C, R, d0, w, h, m, lift=0.004, dome=0.0, rings=3, segs=16, name="disc", up=(0, 0, 1),
         roll=0.0, shape=None):
    """An oval decal hugging the ellipsoid (C, R) around direction d0.
    w/h are half extents in unit-sphere units along the local right/up,
    `dome` bulges the centre outward, `shape(a)` scales the outline."""
    d0 = V(d0).normalized()
    upv = V(up)
    U = (upv - upv.dot(d0) * d0).normalized()
    E = U.cross(d0).normalized()     # right-hand side when looking at the decal
    if roll:
        q = Quaternion(d0, roll)
        U, E = q @ U, q @ E
    verts = [ell_point(C, R, d0, lift + dome)]
    for r in range(1, rings + 1):
        rr = r / rings
        for k in range(segs):
            a = 2 * math.pi * k / segs
            f = shape(a) if shape else 1.0
            d = d0 + E * (w * rr * math.cos(a) * f) + U * (h * rr * math.sin(a) * f)
            verts.append(ell_point(C, R, d, lift + dome * (1.0 - rr * rr)))
    faces = []
    for k in range(segs):
        faces.append((0, 1 + k, 1 + (k + 1) % segs))
    for r in range(1, rings):
        a0, b0 = 1 + (r - 1) * segs, 1 + r * segs
        for k in range(segs):
            k2 = (k + 1) % segs
            faces.append((a0 + k, b0 + k, b0 + k2, a0 + k2))
    o = mesh_object(name, verts, faces, m)
    fix_normals(o, outward_dir=ell_normal(R, d0))
    return o


def fix_normals(o, outward_from=None, outward_dir=None):
    """Make every face point away from a centre (or along a direction)."""
    me = o.data
    for p in me.polygons:
        c = p.center
        want = (c - V(outward_from)) if outward_from is not None else V(outward_dir)
        if p.normal.dot(want) < 0:
            p.flip()
    me.update()


def recalc(o):
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    bm.to_mesh(o.data)
    bm.free()


def rounded_box(size, loc, m, radius=0.03, segs=3, name="box", rot=(0, 0, 0)):
    """A box with properly rounded edges (bevel applied), smooth shaded."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.name = name
    o.scale = size
    apply_xform(o)
    b = o.modifiers.new("bevel", "BEVEL")
    b.width = radius
    b.segments = segs
    b.limit_method = "NONE"
    b.harden_normals = False
    apply_mods(o)
    o.data.materials.clear()
    o.data.materials.append(mat(m))
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.use_auto_smooth = True
    o.data.auto_smooth_angle = math.radians(50)
    return o


def prim(kind, m, name, smooth=True, auto=50, **kw):
    getattr(bpy.ops.mesh, "primitive_%s_add" % kind)(**kw)
    o = bpy.context.object
    o.name = name
    o.data.materials.clear()
    o.data.materials.append(mat(m))
    for p in o.data.polygons:
        p.use_smooth = smooth
    if auto:
        o.data.use_auto_smooth = True
        o.data.auto_smooth_angle = math.radians(auto)
    return o


def select_only(o):
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def apply_xform(o):
    select_only(o)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def apply_mods(o):
    select_only(o)
    for md in list(o.modifiers):
        bpy.ops.object.modifier_apply(modifier=md.name)


def subsurf(o, levels=1):
    md = o.modifiers.new("sub", "SUBSURF")
    md.levels = levels
    md.render_levels = levels
    apply_mods(o)
    return o


def solidify(o, thickness, offset=-1.0, rim_mat=None, bevel=0.0, bevel_segs=2):
    md = o.modifiers.new("solid", "SOLIDIFY")
    md.thickness = thickness
    md.offset = offset
    md.use_even_offset = True
    md.use_rim = True
    if rim_mat is not None:
        o.data.materials.append(mat(rim_mat))
        md.material_offset_rim = len(o.data.materials) - 1
    if bevel > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = bevel_segs
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(50)
    apply_mods(o)
    o.data.use_auto_smooth = True
    o.data.auto_smooth_angle = math.radians(60)
    for p in o.data.polygons:
        p.use_smooth = True
    return o


def cut_below(o, z, keep_above=True, axis=(0, 0, 1)):
    """Bisect `o` by a plane and drop one side (no fill)."""
    bm = bmesh.new()
    bm.from_mesh(o.data)
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    no = V(axis)
    co = no * z
    bmesh.ops.bisect_plane(bm, geom=geom, plane_co=co, plane_no=no,
                           clear_inner=keep_above, clear_outer=not keep_above)
    bm.to_mesh(o.data)
    bm.free()
    o.data.update()
    return o


def tris(o):
    return sum(len(p.vertices) - 2 for p in o.data.polygons)


def transform(o, loc=(0, 0, 0), rot=None, scale=None, about=(0, 0, 0)):
    """Transform mesh data in place (rotation as Euler XYZ radians or Quaternion)."""
    M = Matrix.Translation(V(loc) + V(about))
    if rot is not None:
        q = rot if isinstance(rot, Quaternion) else mathutils.Euler(rot).to_quaternion()
        M = M @ q.to_matrix().to_4x4()
    if scale is not None:
        M = M @ Matrix.Diagonal((*scale, 1.0))
    M = M @ Matrix.Translation(-V(about))
    o.data.transform(M)
    o.data.update()
    return o


def mirror_x(o, name):
    """A mirrored duplicate across X = 0 (mesh data flipped, normals fixed)."""
    me = o.data.copy()
    c = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(c)
    me.transform(Matrix.Diagonal((-1, 1, 1, 1)))
    me.flip_normals()
    me.update()
    for k, v in o.items():
        c[k] = v
    return c


# ------------------------------------------------------ material masking --
class Ex:
    """Tiny expression builder for shader math on object-space coordinates.
    Values are floats or node sockets; operators add Math nodes."""

    def __init__(self, material):
        self.m = material
        self.nt = material.node_tree
        tc = self.nt.nodes.new("ShaderNodeTexCoord")
        sep = self.nt.nodes.new("ShaderNodeSeparateXYZ")
        self.nt.links.new(tc.outputs["Object"], sep.inputs[0])
        self.x, self.y, self.z = (W(self, sep.outputs[i]) for i in range(3))

    def op(self, operation, a, b=None, c=None):
        n = self.nt.nodes.new("ShaderNodeMath")
        n.operation = operation
        for i, v in enumerate((a, b, c)):
            if v is None:
                continue
            if isinstance(v, W):
                self.nt.links.new(v.s, n.inputs[i])
            else:
                n.inputs[i].default_value = float(v)
        return W(self, n.outputs[0])

    def smooth(self, e0, e1, v):
        """smoothstep from e0 to e1 (e0 > e1 allowed: a falling edge)."""
        n = self.nt.nodes.new("ShaderNodeMapRange")
        n.interpolation_type = "SMOOTHSTEP"
        n.clamp = True
        self.nt.links.new(v.s, n.inputs["Value"])
        n.inputs["From Min"].default_value = e0
        n.inputs["From Max"].default_value = e1
        return W(self, n.outputs["Result"])

    def band(self, v, centre, half, soft=0.002):
        """1 where |v - centre| < half, soft edges."""
        d = abs(v - centre)
        return self.smooth(half + soft, half - soft, d)

    def length(self, *comps):
        s = comps[0] * comps[0]
        for c in comps[1:]:
            s = s + c * c
        return self.op("SQRT", s)

    def sin(self, v):
        return self.op("SINE", v)

    def noise(self, scale, stretch=(1, 1, 1)):
        tc = self.nt.nodes.new("ShaderNodeTexCoord")
        mp = self.nt.nodes.new("ShaderNodeMapping")
        mp.inputs["Scale"].default_value = stretch
        self.nt.links.new(tc.outputs["Object"], mp.inputs[0])
        n = self.nt.nodes.new("ShaderNodeTexNoise")
        n.inputs["Scale"].default_value = scale
        self.nt.links.new(mp.outputs[0], n.inputs["Vector"])
        return W(self, n.outputs["Fac"])

    def _bsdf(self):
        for n in self.nt.nodes:
            if n.type == "BSDF_PRINCIPLED":
                return n

    def paint(self, mask, colour, rough=None, metal=None):
        """Mix a flat colour (and roughness/metallic) in where mask = 1."""
        bsdf = self._bsdf()
        for sock, val in (("Base Color", colour), ("Roughness", rough), ("Metallic", metal)):
            if val is None:
                continue
            inp = bsdf.inputs[sock]
            src = inp.links[0].from_socket if inp.is_linked else None
            if sock == "Base Color":
                mix = self.nt.nodes.new("ShaderNodeMix")
                mix.data_type = "RGBA"
                self.nt.links.new(mask.s, mix.inputs["Factor"])
                if src is not None:
                    self.nt.links.new(src, mix.inputs[6])
                else:
                    mix.inputs[6].default_value = tuple(inp.default_value)
                mix.inputs[7].default_value = (*colour, 1.0)
                self.nt.links.new(mix.outputs[2], inp)
            else:
                if src is not None and src.type != "VALUE":
                    conv = self.nt.nodes.new("ShaderNodeRGBToBW")
                    self.nt.links.new(src, conv.inputs[0])
                    src = conv.outputs[0]
                a = W(self, src) if src is not None else float(inp.default_value)
                out = (a + mask * (val - a)) if isinstance(a, W) else (mask * (val - a) + a)
                self.nt.links.new(out.s, inp)

    def darken(self, mask, amount):
        """Multiply the base colour by (1 - amount * mask)."""
        bsdf = self._bsdf()
        inp = bsdf.inputs["Base Color"]
        src = inp.links[0].from_socket
        mix = self.nt.nodes.new("ShaderNodeMix")
        mix.data_type = "RGBA"
        mix.blend_type = "MULTIPLY"
        self.nt.links.new((mask * amount).s, mix.inputs["Factor"])
        self.nt.links.new(src, mix.inputs[6])
        mix.inputs[7].default_value = (0.25, 0.25, 0.27, 1.0)
        self.nt.links.new(mix.outputs[2], inp)

    def relief(self, height, strength=1.0):
        """Add `height` (metres-ish, negative = groove) to the bump chain."""
        bump = next(n for n in self.nt.nodes if n.type == "BUMP")
        inp = bump.inputs["Height"]
        src = inp.links[0].from_socket
        old = W(self, src)
        bump.inputs["Strength"].default_value = max(bump.inputs["Strength"].default_value, strength)
        new = old * 0.35 + height
        self.nt.links.new(new.s, inp)


class W:
    def __init__(self, ex, s):
        self.ex, self.s = ex, s

    def _o(self, op, other, rev=False):
        return self.ex.op(op, other, self) if rev else self.ex.op(op, self, other)

    def __add__(self, o): return self._o("ADD", o)
    def __radd__(self, o): return self._o("ADD", o, True)
    def __sub__(self, o): return self._o("SUBTRACT", o)
    def __rsub__(self, o): return self._o("SUBTRACT", o, True)
    def __mul__(self, o): return self._o("MULTIPLY", o)
    def __rmul__(self, o): return self._o("MULTIPLY", o, True)
    def __truediv__(self, o): return self._o("DIVIDE", o)
    def __abs__(self): return self.ex.op("ABSOLUTE", self)
    def __neg__(self): return self.ex.op("MULTIPLY", self, -1.0)
    def max(self, o): return self._o("MAXIMUM", o)
    def min(self, o): return self._o("MINIMUM", o)
    def frac(self): return self.ex.op("FRACT", self)


# --------------------------------------------------------------- skinning --
def _closest_on_chain(p, joints):
    """(param along the polyline, distance) of p's closest point."""
    best = (0.0, 1e9)
    acc = 0.0
    for a, b in zip(joints[:-1], joints[1:]):
        ab = b - a
        L = ab.length
        t = max(0.0, min(1.0, (p - a).dot(ab) / (L * L))) if L > 1e-9 else 0.0
        d = (a + ab * t - p).length
        if d < best[1]:
            best = (acc + t * L, d)
        acc += L
    return best


def _smooth(t):
    t = max(0.0, min(1.0, t))
    return t * t * (3 - 2 * t)


def weigh_chain(o, bones, joints, widths):
    """Skin `o` along a bone chain. `joints` are the chain's points (len =
    len(bones) + 1): bone i spans joints[i]..joints[i+1]. Around each inner
    joint the weight blends between the two bones over +-widths[j]."""
    J = [V(j) for j in joints]
    seg = [0.0]
    for a, b in zip(J[:-1], J[1:]):
        seg.append(seg[-1] + (b - a).length)
    groups = {b: (o.vertex_groups.get(b) or o.vertex_groups.new(name=b)) for b in bones}
    for v in o.data.vertices:
        s, _ = _closest_on_chain(v.co, J)
        w = [0.0] * len(bones)
        w[0] = 1.0
        for j in range(1, len(bones)):
            t = _smooth((s - (seg[j] - widths[j - 1])) / (2 * widths[j - 1]))
            # Move weight t from everything before j to bone j.
            for i in range(j):
                w[i] *= (1 - t)
            w[j] = t
        tot = sum(w)
        for b, x in zip(bones, w):
            if x / tot > 0.002:
                groups[b].add([v.index], x / tot, "REPLACE")


def weigh_rigid(o, bone):
    g = o.vertex_groups.get(bone) or o.vertex_groups.new(name=bone)
    g.add([v.index for v in o.data.vertices], 1.0, "REPLACE")


def weigh_fn(o, fn):
    """fn(co) -> {bone: weight}"""
    for v in o.data.vertices:
        ws = fn(v.co)
        tot = sum(ws.values()) or 1.0
        for b, x in ws.items():
            if x / tot <= 0.002:
                continue
            g = o.vertex_groups.get(b) or o.vertex_groups.new(name=b)
            g.add([v.index], x / tot, "REPLACE")


# --------------------------------------------------------------- armature --
def build_armature(bones, name="Armature"):
    """bones: list of (name, head, tail, parent, roll_axis) -> armature object.
    roll_axis is the world direction the bone's local Z should face."""
    arm = bpy.data.armatures.new(name)
    obj = bpy.data.objects.new(name, arm)
    bpy.context.collection.objects.link(obj)
    select_only(obj)
    bpy.ops.object.mode_set(mode="EDIT")
    eb = arm.edit_bones
    for bname, head, tail, parent, roll_axis in bones:
        b = eb.new(bname)
        b.head = head
        b.tail = tail
        b.align_roll(V(roll_axis))
        if parent:
            b.parent = eb[parent]
            b.use_connect = False
    bpy.ops.object.mode_set(mode="OBJECT")
    for pb in obj.pose.bones:
        pb.rotation_mode = "XYZ"
    return obj


def world_to_bone(arm, bone, vec):
    """A world-space offset expressed in the bone's local (pose) space."""
    b = arm.data.bones[bone]
    return b.matrix_local.to_3x3().inverted() @ V(vec)


MIRROR = ("_l", "_r")


def author(arm, clip, poses, loop=False, all_bones=True, interp="BEZIER"):
    """Key a clip from a list of (frame, pose). A pose maps bone -> (rx, ry,
    rz) degrees in the bone's local axes, using *semantic* signs on the
    right side too (they are mirrored here: y and z flip for "*_r"), and the
    special key "hips@" -> world offset (x, y, z) in metres of the hips.
    Every deform bone gets keys in every clip, and none is left exactly
    constant, because the importer and ModelUtil strip constant tracks."""
    names = [b.name for b in arm.data.bones] if all_bones else sorted({k for _, p in poses for k in p})
    last = poses[-1][0]
    rot_keys = {n: [] for n in names}
    loc_keys = []
    for frame, pose in poses:
        for n in names:
            r = pose.get(n, (0.0, 0.0, 0.0))
            r = tuple(math.radians(a) for a in r)
            if n.endswith("_r"):
                r = (r[0], -r[1], -r[2])
            rot_keys[n].append((frame, r))
        off = pose.get("hips@", (0.0, 0.0, 0.0))
        loc_keys.append((frame, tuple(world_to_bone(arm, "hips", off))))
    for n in names:
        ks = rot_keys[n]
        ks = _unconstant(ks, last)
        key(arm, clip, 'pose.bones["%s"].rotation_euler' % n, ks, interp=interp)
    key(arm, clip, 'pose.bones["hips"].location', _unconstant(loc_keys, last, amp=0.0005), interp=interp)
    act = bpy.data.actions.get("%s|%s" % (arm.name, clip))
    if loop:
        for fc in act.fcurves:
            if not fc.modifiers:
                fc.modifiers.new("CYCLES")
            for kp in fc.keyframe_points:
                kp.handle_left_type = "AUTO_CLAMPED"
                kp.handle_right_type = "AUTO_CLAMPED"
            fc.update()
    return act


def _unconstant(ks, last, amp=0.002):
    """Nudge a constant channel so no exported track is immutable."""
    vals = [v for _, v in ks]
    if all(all(abs(a - b) < 1e-4 for a, b in zip(v, vals[0])) for v in vals):
        mid = last / 2.0
        base = vals[0]
        bumped = tuple(x + amp for x in base)
        ks = [(0, base), (mid, bumped), (last, base)] if last > 0 else [(0, base), (1, bumped)]
    return ks


def show_clip(arm, clip, frame):
    """Evaluate only `clip` (solo its NLA track) at `frame`."""
    ad = arm.animation_data
    for t in ad.nla_tracks:
        t.mute = t.name != clip
    bpy.context.scene.frame_set(int(frame))


def unmute_all(arm):
    if arm.animation_data:
        for t in arm.animation_data.nla_tracks:
            t.mute = False


# ---------------------------------------------------------------- renders --
def setup_render(size=512, samples=48):
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    scn.cycles.use_denoising = False
    scn.render.resolution_x = size
    scn.render.resolution_y = size
    scn.render.film_transparent = False
    scn.world = scn.world or bpy.data.worlds.new("w")
    scn.world.use_nodes = True
    bg = scn.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.035, 0.018, 0.055, 1.0)
    bg.inputs[1].default_value = 1.0
    if "hero_cam" not in bpy.data.objects:
        cd = bpy.data.cameras.new("hero_cam")
        cam = bpy.data.objects.new("hero_cam", cd)
        bpy.context.collection.objects.link(cam)
        for nm, pos, col, e in (("key", (1.6, -2.4, 2.6), (1.0, 0.92, 0.95), 260),
                                ("fill", (-2.4, -1.2, 1.4), (0.45, 0.8, 1.0), 120),
                                ("rim", (0.6, 2.6, 2.2), (1.0, 0.35, 0.85), 220)):
            ld = bpy.data.lights.new("hero_" + nm, "AREA")
            ld.energy = e
            ld.size = 1.2
            ld.color = col
            lo = bpy.data.objects.new("hero_" + nm, ld)
            bpy.context.collection.objects.link(lo)
            lo.location = pos
            lo.rotation_euler = (V((0, 0, 0.8)) - V(pos)).to_track_quat("-Z", "Y").to_euler()
        fl = bpy.data.meshes.new("hero_floor")
        fo = bpy.data.objects.new("hero_floor", fl)
        bm = bmesh.new()
        bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=6)
        bm.to_mesh(fl)
        bm.free()
        m = bpy.data.materials.new("hero_floor_mat")
        m.use_nodes = True
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0.05, 0.04, 0.07, 1)
        m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.35
        fl.materials.append(m)
        bpy.context.collection.objects.link(fo)
        scn.camera = cam
    return bpy.data.objects["hero_cam"]


def shoot(path, yaw_deg=35.0, target=(0, 0, 0.85), dist=4.2, lens=50, elev=0.15, size=None, samples=None):
    cam = setup_render()
    scn = bpy.context.scene
    if size:
        scn.render.resolution_x = scn.render.resolution_y = size
    if samples:
        scn.cycles.samples = samples
    cam.data.lens = lens
    a = math.radians(yaw_deg)
    d = V((math.sin(a), -math.cos(a), elev)).normalized()
    cam.location = V(target) + d * dist
    cam.rotation_euler = (V(target) - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.render.filepath = path
    bpy.ops.render.render(write_still=True)
    print("RENDER", path)


def montage(paths, out, tile=None, cols=4, labels=None):
    args = ["montage"]
    for i, p in enumerate(paths):
        if labels:
            args += ["-label", labels[i]]
        args.append(p)
    args += ["-tile", "%dx" % cols, "-geometry", "+2+2", "-background", "#1a1024", "-fill", "white",
             "-pointsize", "14", out]
    subprocess.run(args, check=False)
    print("SHEET", out)


# ------------------------------------------------------------------ baking --
# A copy of common.bake_textures with a better atlas for a character: the
# stock unwrap (smart project + pack) leaves much of the square empty and
# gives hidden faces as much room as the face. Here islands are weighted by
# importance (the `uv_weight` float attribute per face, default 1) before a
# tight pack. The passes and the baked material are the same as common's.
from common import _bakeable, _principled, _output, _source, _merge_slots, all_meshes, scene_bounds  # noqa: E402


def _island_weights(o, size):
    """Scale each UV island of `o` by the mean uv_weight of its faces."""
    from bpy_extras import bmesh_utils
    bm = bmesh.new()
    bm.from_mesh(o.data)
    uv = bm.loops.layers.uv.active
    wl = bm.faces.layers.float.get("uv_weight")
    islands = bmesh_utils.bmesh_linked_uv_islands(bm, uv)
    for isl in islands:
        if not isl or not isl[0].select:
            continue
        w = sum(f[wl] if wl else 1.0 for f in isl) / len(isl)
        if abs(w - 1.0) < 1e-3:
            continue
        pts = [l[uv].uv for f in isl for l in f.loops]
        c = sum(pts, Vector((0, 0))) / len(pts)
        k = math.sqrt(max(w, 0.05))
        for f in isl:
            for l in f.loops:
                l[uv].uv = c + (l[uv].uv - c) * k
    bm.to_mesh(o.data)
    bm.free()


def bake_hero(name, tex=1024, ao_distance=None):
    scn = bpy.context.scene
    meshes = [o for o in all_meshes() if any(_bakeable(s.material) for s in o.material_slots)]
    lo, hi = scene_bounds()
    size = tex
    extent = max((hi - lo).x, (hi - lo).y, (hi - lo).z)
    ao_dist = ao_distance or max(0.05, min(0.6, extent * 0.12))
    for o in meshes:
        select_only(o)
        for md in list(o.modifiers):
            if md.type != "ARMATURE":
                bpy.ops.object.modifier_apply(modifier=md.name)
    for o in meshes:
        me = o.data
        while me.uv_layers:
            me.uv_layers.remove(me.uv_layers[0])
        me.uv_layers.new(name="UVMap")
        for p in me.polygons:
            p.select = _bakeable(o.material_slots[p.material_index].material) if o.material_slots else False
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.mode_set(mode="EDIT")
    scn.tool_settings.use_uv_select_sync = True
    bpy.ops.uv.smart_project(angle_limit=math.radians(66), island_margin=0.0, area_weight=0.0,
                             correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.object.mode_set(mode="OBJECT")
    for o in meshes:
        _island_weights(o, size)
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.uv.pack_islands(rotate=True, margin_method="FRACTION", margin=3.0 / size, shape_method="CONCAVE")
    bpy.ops.object.mode_set(mode="OBJECT")
    cover = uv_coverage(meshes[0])
    print("UV coverage %.0f%%" % (cover * 100))

    def image(suffix, colour):
        img = bpy.data.images.new("%s_%s" % (name, suffix), size, size, alpha=False)
        img.colorspace_settings.name = "sRGB" if colour else "Non-Color"
        return img
    albedo, orm, normal = image("albedo", True), image("orm", False), image("normal", False)
    mats = {s.material for o in meshes for s in o.material_slots if _bakeable(s.material)}
    info = {}
    for m in mats:
        nt = m.node_tree
        bsdf = _principled(m)
        out = _output(m)
        img_node = nt.nodes.new("ShaderNodeTexImage")
        nt.nodes.active = img_node
        emis = nt.nodes.new("ShaderNodeEmission")
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao.samples = 16
        ao.inputs["Distance"].default_value = ao_dist
        comb = nt.nodes.new("ShaderNodeCombineColor")
        nt.links.new(ao.outputs["AO"], comb.inputs[0])
        nt.links.new(_source(nt, bsdf.inputs["Roughness"]), comb.inputs[1])
        nt.links.new(_source(nt, bsdf.inputs["Metallic"]), comb.inputs[2])
        info[m] = dict(nt=nt, bsdf=bsdf, out=out, img=img_node, emis=emis, comb=comb,
                       base=_source(nt, bsdf.inputs["Base Color"]), surface=out.inputs["Surface"].links[0].from_socket)
    bpy.ops.mesh.primitive_plane_add(size=max(4.0, extent * 4), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
    floor = bpy.context.object
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.use_denoising = False
    scn.cycles.use_preview_denoising = False
    bk = scn.render.bake
    bk.margin = max(4, size // 128)
    bk.margin_type = "EXTEND"
    bk.use_clear = True

    def run(kind, target, samples, wire):
        for m, d in info.items():
            d["img"].image = target
            d["nt"].links.new(wire(d), d["out"].inputs["Surface"])
        scn.cycles.samples = samples
        bpy.ops.object.select_all(action="DESELECT")
        for o in meshes:
            o.select_set(True)
        bpy.context.view_layer.objects.active = meshes[0]
        if kind == "NORMAL":
            bpy.ops.object.bake(type="NORMAL", normal_space="TANGENT")
        else:
            bpy.ops.object.bake(type="EMIT")

    def emission_of(sock_key):
        def wire(d):
            d["nt"].links.new(d[sock_key] if sock_key != "comb" else d["comb"].outputs[0], d["emis"].inputs["Color"])
            return d["emis"].outputs[0]
        return wire
    run("EMIT", albedo, 4, emission_of("base"))
    run("EMIT", orm, 24, emission_of("comb"))
    run("NORMAL", normal, 8, lambda d: d["surface"])
    bpy.data.objects.remove(floor, do_unlink=True)
    dump = os.environ.get("BAKE_DUMP")
    for img in (albedo, orm, normal):
        if dump:
            os.makedirs(dump, exist_ok=True)
            img.filepath_raw = os.path.join(dump, img.name + ".png")
            img.file_format = "PNG"
            img.save()
        img.pack()
    baked = bpy.data.materials.new(name + "_baked")
    baked.use_nodes = True
    nt = baked.node_tree
    bsdf = _principled(baked)
    t_alb = nt.nodes.new("ShaderNodeTexImage")
    t_alb.image = albedo
    nt.links.new(t_alb.outputs["Color"], bsdf.inputs["Base Color"])
    t_orm = nt.nodes.new("ShaderNodeTexImage")
    t_orm.image = orm
    sep = nt.nodes.new("ShaderNodeSeparateColor")
    nt.links.new(t_orm.outputs["Color"], sep.inputs[0])
    nt.links.new(sep.outputs[1], bsdf.inputs["Roughness"])
    nt.links.new(sep.outputs[2], bsdf.inputs["Metallic"])
    group = bpy.data.node_groups.get("glTF Material Output")
    if group is None:
        group = bpy.data.node_groups.new("glTF Material Output", "ShaderNodeTree")
        group.interface.new_socket(name="Occlusion", in_out="INPUT", socket_type="NodeSocketFloat")
    gnode = nt.nodes.new("ShaderNodeGroup")
    gnode.node_tree = group
    nt.links.new(sep.outputs[0], gnode.inputs["Occlusion"])
    t_nrm = nt.nodes.new("ShaderNodeTexImage")
    t_nrm.image = normal
    nmap = nt.nodes.new("ShaderNodeNormalMap")
    nt.links.new(t_nrm.outputs["Color"], nmap.inputs["Color"])
    nt.links.new(nmap.outputs["Normal"], bsdf.inputs["Normal"])
    bsdf.inputs["Emission Strength"].default_value = 0.0
    for o in meshes:
        for s in o.material_slots:
            if _bakeable(s.material):
                s.material = baked
        select_only(o)
        _merge_slots(o)
    print("BAKED %s %dpx ao=%.2fm objects=%d" % (name, size, ao_dist, len(meshes)))


def uv_coverage(o, res=256):
    """Fraction of the unit UV square covered by the selected faces (raster estimate)."""
    grid = bytearray(res * res)
    uv = o.data.uv_layers.active.data
    for p in o.data.polygons:
        if not p.select:
            continue
        pts = [uv[i].uv for i in p.loop_indices]
        for k in range(1, len(pts) - 1):
            a, b, c = pts[0], pts[k], pts[k + 1]
            x0, x1 = int(max(0, min(a.x, b.x, c.x) * res)), int(min(res - 1, max(a.x, b.x, c.x) * res))
            y0, y1 = int(max(0, min(a.y, b.y, c.y) * res)), int(min(res - 1, max(a.y, b.y, c.y) * res))
            d = (b.y - c.y) * (a.x - c.x) + (c.x - b.x) * (a.y - c.y)
            if abs(d) < 1e-12:
                continue
            for yy in range(y0, y1 + 1):
                for xx in range(x0, x1 + 1):
                    px, py = (xx + 0.5) / res, (yy + 0.5) / res
                    l1 = ((b.y - c.y) * (px - c.x) + (c.x - b.x) * (py - c.y)) / d
                    l2 = ((c.y - a.y) * (px - c.x) + (a.x - c.x) * (py - c.y)) / d
                    if l1 >= 0 and l2 >= 0 and l1 + l2 <= 1:
                        grid[yy * res + xx] = 1
    return sum(grid) / (res * res)
