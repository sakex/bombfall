# Hotel Electra kit: shared helpers for the first tower's rooms (room1,
# room2, toilet1, gym, hacker) -- their backdrop_<theme>.py and
# ceiling_<theme>.py scripts.  Built on common.py (never edited from here).
#
# Scale: the game's furniture is toy-sized next to the 1.5 m hero (a bed is
# 6 m long, a toilet 3 m tall), so room dressing is built at about 2.5x real
# size: S converts real metres to game metres.  Rooms: x 0..15 across, y 0
# (front) .. 1.93 (the back wall's face is at y = 1.95), z 0 = floor up to
# 9.5 m for backdrops, z 0 = ceiling down to -3 m for ceilings.
#
# What the kit adds on top of common.py:
#   * box()/rbox(): boxes with their size applied to the mesh, so bevels are
#     round and even, and cheap chamfered variants for silhouettes;
#   * pattern materials baked like any pbr(): tiles, quilting, planks,
#     stripes, perforation (see pattern());
#   * finish(): applies modifiers and transforms, culls faces the game camera
#     can never see (backs against the wall, bottoms on the floor), joins the
#     static meshes, bakes with a temporary back wall so the decor gets
#     contact shadows from it, exports, prints the triangle count and renders
#     a front view (front_preview) that frames the room like the game does;
#   * animation helpers for the "idle" clip (one period per model: T seconds):
#     blink(), flicker(), spin_idle(), swing(), bob(), puff();
#   * props shared by several rooms (lamps, fixtures, fans, curtains, ...).
import math
import os
import sys

import bmesh
import bpy
import mathutils

from common import *  # noqa: F401,F403
import common as _common

S = 2.5            # real metres -> game metres
D = 1.85           # legacy: the old scripts' back-wall reference
WALL = 1.945       # front face of wall-hung decor (the shell wall is at 1.95)
T = 4.0            # period of every idle clip in these rooms, seconds
F = int(T * FPS)   # ... in frames (120)

# ------------------------------------------------------------ materials --
# A few shared looks (all pbr kinds bake into the atlas).
# The game lights rooms with a dim purple ambient and one high omni light,
# which greys out dark or cool albedos; every surface colour is lifted so
# the decor keeps its hue in game (the Cycles previews look a bit bright).
LIFT = 1.35


def _lift(c):
    return tuple(min(0.92, v * LIFT) for v in c) if c else c


def M(kind, colour, **kw):
    if "color2" in kw:
        kw["color2"] = _lift(kw["color2"])
    return pbr(kind, _lift(colour), **kw)


NEON_SCALE = 0.65   # keeps emissive hues from clipping to white under the game's glow


def glow(colour, strength=3.0, base=None):
    """Emissive (not baked)."""
    strength *= NEON_SCALE
    if base is None:
        return pbr("neon", colour, strength=strength)
    return pbr("neon", base, emit=colour, strength=strength)


def flat(colour, rough=0.6):
    """A plain, unbaked material (no normal map): for thin cards such as
    leaves, whose tiny UV islands give broken tangents once baked."""
    m = pbr("neon", _lift(colour), emit=(0.0, 0.0, 0.0), strength=0.0, rough=rough, name="flat")
    return m


def screen(colour, strength=1.1):
    """An animated screen material (rolling scanlines in the game)."""
    return anim(neon(colour, strength, tuple(c * 0.15 for c in colour)), "screen")


def marquee(colour, strength=3.0):
    return anim(neon(colour, strength), "marquee")


def glass(colour=(0.6, 0.75, 0.9), alpha=0.25, rough=0.05):
    return pbr("glass", colour, alpha=alpha, rough=rough)


def _find(nt, kind):
    for n in nt.nodes:
        if n.type == kind:
            return n
    return None


_PATTERNS = {}


def pattern(kind, colour, pat, size=(0.3, 0.3), line=0.012, line_col=None, plane="XZ", depth=1.0,
            offset=0.0, name=None, duty=0.5, **kw):
    """A pbr() material with a regular pattern mixed into colour, roughness and
    bump.  pat: "tiles" (square grid with grout lines, `offset` 0.5 for
    running bond), "planks" (long boards), "quilt" (diamond stitched puffs),
    "stripes" (bands along the first axis), "grille" (perforated metal: dots),
    "channels" (vertical tufted channels).  `plane` picks the two world
    axes the pattern lies in ("XZ" walls facing the camera, "XY" floors)."""
    ck = (kind, tuple(colour), pat, tuple(size), line, tuple(line_col) if line_col else None, plane, depth, offset, duty,
          tuple(sorted((k, str(v)) for k, v in kw.items())))
    if ck in _PATTERNS and _PATTERNS[ck].name in bpy.data.materials:
        return _PATTERNS[ck]
    colour = _lift(colour)
    line_col = _lift(line_col)
    if "color2" in kw:
        kw["color2"] = _lift(kw["color2"])
    m = pbr(kind, colour, name=name or "%s_%s_%d" % (kind, pat, len(bpy.data.materials)), **kw)
    _PATTERNS[ck] = m
    nt = m.node_tree
    bsdf = _find(nt, "BSDF_PRINCIPLED")
    bump = _find(nt, "BUMP")
    co = nt.nodes.new("ShaderNodeTexCoord").outputs["Object"]
    sep = nt.nodes.new("ShaderNodeSeparateXYZ")
    nt.links.new(co, sep.inputs[0])
    a, b = {"XZ": ("X", "Z"), "XY": ("X", "Y"), "YZ": ("Y", "Z")}[plane]
    comb = nt.nodes.new("ShaderNodeCombineXYZ")
    nt.links.new(sep.outputs[a], comb.inputs[0])
    nt.links.new(sep.outputs[b], comb.inputs[1])
    vec = comb.outputs[0]
    lc = line_col or tuple(c * 0.35 for c in colour)
    grout = None
    if pat == "checker":
        ck = nt.nodes.new("ShaderNodeTexChecker")
        ck.inputs["Color1"].default_value = (1, 1, 1, 1)
        ck.inputs["Color2"].default_value = (0, 0, 0, 1)
        ck.inputs["Scale"].default_value = 1.0
        mpc = nt.nodes.new("ShaderNodeMapping")
        mpc.inputs["Scale"].default_value = (0.5 / size[0], 0.5 / size[1], 1.0)
        nt.links.new(vec, mpc.inputs["Vector"])
        nt.links.new(mpc.outputs[0], ck.inputs["Vector"])
        pat = "tiles"
        grout = ck.outputs["Fac"]
    if pat in ("tiles", "planks"):
        br = nt.nodes.new("ShaderNodeTexBrick")
        br.offset = offset if pat == "tiles" else 0.5
        br.offset_frequency = 2 if pat == "tiles" else 1
        br.squash = 1.0
        br.inputs["Color1"].default_value = (1, 1, 1, 1)
        br.inputs["Color2"].default_value = (1, 1, 1, 1) if pat == "tiles" else (0.8, 0.8, 0.8, 1)
        br.inputs["Mortar"].default_value = (0, 0, 0, 1)
        br.inputs["Scale"].default_value = 1.0
        br.inputs["Mortar Size"].default_value = line
        br.inputs["Mortar Smooth"].default_value = 0.3
        br.inputs["Bias"].default_value = 0.0
        br.inputs["Brick Width"].default_value = size[0]
        br.inputs["Row Height"].default_value = size[1]
        nt.links.new(vec, br.inputs["Vector"])
        mask = br.outputs["Color"]          # 1 on the tile, 0 in the grout
    elif pat == "quilt":
        # Two diagonal sine bands multiplied: puffy diamonds, seams at 0.
        outs = []
        for sgn in (1, -1):
            mp = nt.nodes.new("ShaderNodeMapping")
            mp.inputs["Rotation"].default_value = (0, 0, sgn * math.pi / 4)
            nt.links.new(vec, mp.inputs["Vector"])
            wv = nt.nodes.new("ShaderNodeTexWave")
            wv.wave_type = "BANDS"
            wv.bands_direction = "X"
            wv.wave_profile = "SIN"
            wv.inputs["Scale"].default_value = math.pi / (10.0 * size[0])
            wv.inputs["Distortion"].default_value = 0.0
            wv.inputs["Detail"].default_value = 0.0
            nt.links.new(mp.outputs[0], wv.inputs["Vector"])
            outs.append(wv.outputs["Fac"])
        mul = nt.nodes.new("ShaderNodeMath")
        mul.operation = "MINIMUM"
        nt.links.new(outs[0], mul.inputs[0])
        nt.links.new(outs[1], mul.inputs[1])
        pw = nt.nodes.new("ShaderNodeMath")
        pw.operation = "POWER"
        nt.links.new(mul.outputs[0], pw.inputs[0])
        pw.inputs[1].default_value = 0.35
        mask = pw.outputs[0]
    elif pat in ("stripes", "channels"):
        wv = nt.nodes.new("ShaderNodeTexWave")
        wv.wave_type = "BANDS"
        wv.bands_direction = "X"
        wv.wave_profile = "SIN" if pat == "channels" else "SAW"
        wv.inputs["Scale"].default_value = math.pi / (10.0 * size[0])
        wv.inputs["Distortion"].default_value = 0.0
        wv.inputs["Detail"].default_value = 0.0
        nt.links.new(vec, wv.inputs["Vector"])
        if pat == "channels":
            pw = nt.nodes.new("ShaderNodeMath")
            pw.operation = "POWER"
            nt.links.new(wv.outputs["Fac"], pw.inputs[0])
            pw.inputs[1].default_value = 0.4
            mask = pw.outputs[0]
        else:
            gt = nt.nodes.new("ShaderNodeMath")
            gt.operation = "GREATER_THAN"
            nt.links.new(wv.outputs["Fac"], gt.inputs[0])
            gt.inputs[1].default_value = duty
            mask = gt.outputs[0]
    elif pat == "grille":
        vo = nt.nodes.new("ShaderNodeTexVoronoi")
        vo.feature = "F1"
        vo.inputs["Scale"].default_value = 1.0 / size[0]
        vo.inputs["Randomness"].default_value = 0.0
        nt.links.new(vec, vo.inputs["Vector"])
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.clamp = True
        nt.links.new(vo.outputs["Distance"], mr.inputs["Value"])
        mr.inputs["From Min"].default_value = 0.28
        mr.inputs["From Max"].default_value = 0.34
        mask = mr.outputs["Result"]
    else:
        raise ValueError(pat)
    # Colour: grout/seam colour where mask = 0 (for a checker: the second
    # tile colour, and the grout darkens both).
    link = bsdf.inputs["Base Color"].links[0]
    src = link.from_socket
    mix = nt.nodes.new("ShaderNodeMix")
    mix.data_type = "RGBA"
    mix.clamp_result = True
    nt.links.new(grout if grout is not None else mask, mix.inputs["Factor"])
    mix.inputs[6].default_value = (*lc, 1.0)
    nt.links.new(src, mix.inputs[7])
    out = mix.outputs[2]
    if grout is not None:
        dk = nt.nodes.new("ShaderNodeMix")
        dk.data_type = "RGBA"
        dk.clamp_result = True
        nt.links.new(mask, dk.inputs["Factor"])
        dk.inputs[6].default_value = (0.08, 0.08, 0.09, 1.0)
        nt.links.new(out, dk.inputs[7])
        out = dk.outputs[2]
    nt.links.new(out, bsdf.inputs["Base Color"])
    # Roughness: seams rougher.
    rl = bsdf.inputs["Roughness"].links[0].from_socket if bsdf.inputs["Roughness"].is_linked else None
    if rl is not None:
        inv = nt.nodes.new("ShaderNodeMath")
        inv.operation = "SUBTRACT"
        inv.inputs[0].default_value = 1.0
        nt.links.new(mask, inv.inputs[1])
        add = nt.nodes.new("ShaderNodeMath")
        add.operation = "MULTIPLY_ADD"
        nt.links.new(inv.outputs[0], add.inputs[0])
        add.inputs[1].default_value = 0.35
        nt.links.new(rl, add.inputs[2])
        cl = nt.nodes.new("ShaderNodeMath")
        cl.operation = "MINIMUM"
        cl.inputs[1].default_value = 1.0
        nt.links.new(add.outputs[0], cl.inputs[0])
        nt.links.new(cl.outputs[0], bsdf.inputs["Roughness"])
    # Height: pattern relief on top of the kind's own bump.
    if bump is not None:
        h_src = bump.inputs["Height"].links[0].from_socket if bump.inputs["Height"].is_linked else None
        madd = nt.nodes.new("ShaderNodeMath")
        madd.operation = "MULTIPLY_ADD"
        nt.links.new(mask, madd.inputs[0])
        madd.inputs[1].default_value = depth
        if h_src is not None:
            sc = nt.nodes.new("ShaderNodeMath")
            sc.operation = "MULTIPLY"
            nt.links.new(h_src, sc.inputs[0])
            sc.inputs[1].default_value = 0.25
            nt.links.new(sc.outputs[0], madd.inputs[2])
        nt.links.new(madd.outputs[0], bump.inputs["Height"])
        bump.inputs["Strength"].default_value = max(bump.inputs["Strength"].default_value, 0.5)
        bump.inputs["Distance"].default_value = 0.02
    return m


# ------------------------------------------------------------- geometry --
def pivot(name, loc=(0, 0, 0), parent=None):
    """common.pivot, with the scene updated at once so children attached to
    it right after get the right parent inverse (a new Empty's matrix_world
    is stale until the depsgraph runs)."""
    e = _common.pivot(name, loc, parent)
    bpy.context.view_layer.update()
    return e


def attach(child, parent):
    bpy.context.view_layer.update()
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    return child


def _bake_scale(o):
    s = o.scale.copy()
    if s != mathutils.Vector((1, 1, 1)):
        o.data.transform(mathutils.Matrix.Diagonal((s.x, s.y, s.z, 1.0)))
        o.scale = (1, 1, 1)
    return o


def _bevel(o, width, seg=1, angle=35.0):
    if width and width > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = width
        b.segments = seg
        b.limit_method = "ANGLE"
        b.angle_limit = math.radians(angle)
        b.harden_normals = False
    return o


def _smooth(o, angle=40.0):
    for p in o.data.polygons:
        p.use_smooth = True
    o.data.use_auto_smooth = True
    o.data.auto_smooth_angle = math.radians(angle)


def box(size, loc, m, rot=(0, 0, 0), bev=0.0, seg=1, name=None, parent=None, smooth=True):
    """An axis box of full `size` centred at `loc`, scale applied to the mesh
    (so bevels stay even).  bev: bevel width (segments `seg`)."""
    o = cube(size, loc, m, rot=rot, bevel=0, name=name)
    _bake_scale(o)
    _bevel(o, bev, seg)
    if smooth and bev:
        _smooth(o, 35.0)
    if parent is not None:
        attach(o, parent)
    return o


def fbox(size, loc, m, **kw):
    """box() with `loc` at its bottom centre (floor standing)."""
    x, y, z = loc
    return box(size, (x, y, z + size[2] / 2.0), m, **kw)


def wbox(size, x, z, m, y=WALL, **kw):
    """box() hung on the back wall: its back face at y (default WALL),
    centred at (x, z)."""
    return box(size, (x, y - size[1] / 2.0, z), m, **kw)


def pill(size, loc, m, seg=3, rot=(0, 0, 0), name=None, parent=None, round_=None):
    """A soft box (cushion, pillow, mattress): strongly bevelled, smooth."""
    r = round_ if round_ is not None else min(size) * 0.45
    o = box(size, loc, m, rot=rot, bev=r, seg=seg, name=name, parent=parent)
    _smooth(o, 80.0)
    return o


def ball(r, loc, m, scale=(1, 1, 1), seg=12, rings=8, name=None, parent=None):
    o = sphere(r, loc, m, scale=scale, segments=seg, rings=rings, name=name)
    _bake_scale(o)
    if parent is not None:
        attach(o, parent)
    return o


def tube_path(points, r, m, verts=8, closed=False, name=None, parent=None, cap=True):
    """A pipe/cable along a polyline (sharp joints) built as one mesh."""
    bm = bmesh.new()
    pts = [mathutils.Vector(p) for p in points]
    rings = []
    n = len(pts)
    for i, p in enumerate(pts):
        if i == 0:
            d = pts[1] - pts[0]
        elif i == n - 1:
            d = pts[-1] - pts[-2]
        else:
            d = (pts[i + 1] - pts[i]).normalized() + (pts[i] - pts[i - 1]).normalized()
        d.normalize()
        q = d.to_track_quat("Z", "Y")
        ring = []
        for k in range(verts):
            a = k / verts * math.tau
            v = q @ mathutils.Vector((math.cos(a) * r, math.sin(a) * r, 0))
            ring.append(bm.verts.new(p + v))
        rings.append(ring)
    for i in range(n - 1):
        for k in range(verts):
            a, b = rings[i][k], rings[i][(k + 1) % verts]
            c, d2 = rings[i + 1][(k + 1) % verts], rings[i + 1][k]
            bm.faces.new((a, b, c, d2))
    if cap:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    me = bpy.data.meshes.new(name or "tube")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name or "tube", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(m))
    _smooth(o, 60.0)
    if parent is not None:
        attach(o, parent)
    return o


def catenary(p0, p1, sag, n=8):
    """Points of a hanging cable from p0 to p1 (sag metres at the middle)."""
    a, b = mathutils.Vector(p0), mathutils.Vector(p1)
    return [tuple(a + (b - a) * (i / n) - mathutils.Vector((0, 0, sag * 4 * (i / n) * (1 - i / n)))) for i in range(n + 1)]


def cable(p0, p1, sag, r=0.02, m=None, n=8, verts=6, **kw):
    return tube_path(catenary(p0, p1, sag, n), r, m or M("rubber", (0.02, 0.02, 0.025)), verts=verts, **kw)


def grid_mesh(nx, nz, fn, m, name="sheet", parent=None, smooth=True):
    """A sheet of (nx x nz) quads; fn(u, v) -> (x, y, z) with u, v in 0..1."""
    bm = bmesh.new()
    vs = [[bm.verts.new(fn(i / nx, j / nz)) for j in range(nz + 1)] for i in range(nx + 1)]
    for i in range(nx):
        for j in range(nz):
            # Winding so the normal faces -Y for a sheet spread along +X, +Z.
            bm.faces.new((vs[i][j], vs[i + 1][j], vs[i + 1][j + 1], vs[i][j + 1]))
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name, me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(m))
    if smooth:
        _smooth(o, 80.0)
    if parent is not None:
        attach(o, parent)
    return o


def lathe(profile, loc, m, verts=16, name=None, parent=None, cap_top=True, cap_bottom=False):
    """A solid of revolution around Z: profile = [(radius, z), ...] bottom to top."""
    bm = bmesh.new()
    rings = []
    for (r, z) in profile:
        ring = []
        for k in range(verts):
            a = k / verts * math.tau
            ring.append(bm.verts.new((loc[0] + math.cos(a) * r, loc[1] + math.sin(a) * r, loc[2] + z)))
        rings.append(ring)
    for i in range(len(rings) - 1):
        for k in range(verts):
            bm.faces.new((rings[i][k], rings[i][(k + 1) % verts], rings[i + 1][(k + 1) % verts], rings[i + 1][k]))
    if cap_top and profile[-1][0] > 1e-4:
        bm.faces.new(rings[-1])
    if cap_bottom and profile[0][0] > 1e-4:
        bm.faces.new(list(reversed(rings[0])))
    me = bpy.data.meshes.new(name or "lathe")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name or "lathe", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(m))
    _smooth(o, 50.0)
    if parent is not None:
        attach(o, parent)
    return o


def extrude_xz(outline, y0, y1, m, name=None, parent=None):
    """A prism: a 2D outline [(x, z), ...] (counter-clockwise seen from the
    front) extruded from y0 (front) to y1 (back)."""
    bm = bmesh.new()
    front = [bm.verts.new((x, y0, z)) for x, z in outline]
    back = [bm.verts.new((x, y1, z)) for x, z in outline]
    bm.faces.new(list(reversed(front)))
    bm.faces.new(back)
    n = len(outline)
    for i in range(n):
        j = (i + 1) % n
        bm.faces.new((front[i], front[j], back[j], back[i]))
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
    me = bpy.data.meshes.new(name or "prism")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name or "prism", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(m))
    if parent is not None:
        attach(o, parent)
    return o


# ------------------------------------------------------------ animation --
def _keys(obj, path, keys, interp="LINEAR"):
    key(obj, "idle", path, keys, interp=interp)


def blink(p, off=(), on_scale=(1, 1, 1), period=F):
    """Show/hide pivot `p` (scale) on a loop: `off` lists (start, end) frame
    ranges within 0..period when it is hidden."""
    tiny = (0.0001, 0.0001, 0.0001)
    keys = [(0, on_scale)]
    for a, b in off:
        keys.append((a, tiny))
        keys.append((b, on_scale))
    keys.append((period, on_scale))
    keys.sort(key=lambda k: k[0])
    _keys(p, "scale", keys, interp="CONSTANT")


def flicker(p, seed=1, bursts=2, period=F):
    """A dying fluorescent tube: mostly on, a couple of stutters per loop."""
    rnd = _rng(seed)
    off = []
    t = 6 + int(rnd() * 20)
    for _ in range(bursts):
        n = 2 + int(rnd() * 3)
        for _k in range(n):
            a = t
            b = t + 1 + int(rnd() * 3)
            if b >= period - 1:
                break
            off.append((a, b))
            t = b + 1 + int(rnd() * 3)
        t += 20 + int(rnd() * 30)
        if t >= period - 8:
            break
    blink(p, off, period=period)


def _rng(seed):
    state = [seed * 7919 + 17]

    def nxt():
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return (state[0] >> 8) / float(1 << 23)
    return nxt


def spin_idle(p, axis="Z", turns=1):
    spin(p, "idle", axis, seconds=T, turns=turns)


def swing(p, axis="X", amp=0.05, cycles=1, phase=0.0):
    """A seamless swing about a local axis (`cycles` swings per loop)."""
    i = "XYZ".index(axis)
    v0 = p.rotation_euler[i]
    steps = 8 * cycles
    keys = [(F * s / steps, v0 + amp * math.sin(2 * math.pi * cycles * s / steps + phase)) for s in range(steps + 1)]
    key(p, "idle", "rotation_euler", keys, index=i)


def bob(p, axis="Z", amp=0.05, cycles=1, phase=0.0):
    i = "XYZ".index(axis)
    v0 = p.location[i]
    steps = 8 * cycles
    keys = [(F * s / steps, v0 + amp * math.sin(2 * math.pi * cycles * s / steps + phase)) for s in range(steps + 1)]
    key(p, "idle", "location", keys, index=i)


def slide_loop(p, axis, dist, cycles=1):
    """A sawtooth: move `dist` along a local axis, snap back, `cycles` times
    per loop (conveyor belts)."""
    i = "XYZ".index(axis)
    v0 = p.location[i]
    step = F / cycles
    keys = []
    for c in range(cycles):
        keys.append((c * step, v0))
        keys.append((c * step + step - 0.02, v0 + dist))
    keys.append((F, v0))
    key(p, "idle", "location", keys, index=i, interp="LINEAR")


def puff(p, rise=0.8, grow=2.2, start=0, life=None, drift=0.0, step=4):
    """A steam/smoke puff (or a drip, with a negative rise): starting at
    frame `start` it rises and swells from its pivot over `life` frames,
    then stays hidden until it starts again; wraps around the loop, so
    every key stays inside 0..F."""
    life = life or F // 2
    z0, x0 = p.location.z, p.location.x
    tiny = 0.0001
    ks, kz, kx = [], [], []
    pre = (start - 1) % F
    frames = sorted(set(list(range(0, F + 1, step)) + [(start + life) % F, start % F, pre]))
    for f in frames:
        t = ((f - start) % F) / float(life)
        if f == (start + life) % F and life < F:
            t = 1.0
        if f == pre and life < F - 1:
            ks.append((f, (tiny, tiny, tiny)))
            kz.append((f, z0))
            kx.append((f, x0))
            continue
        if t < 1.0:
            s = 0.3 + (grow - 0.3) * t
            ks.append((f, (s, s, s)))
            kz.append((f, z0 + rise * t))
            kx.append((f, x0 + drift * t))
        else:
            ks.append((f, (tiny, tiny, tiny)))
            kz.append((f, z0 + rise))
            kx.append((f, x0 + drift))
    key(p, "idle", "scale", ks, interp="LINEAR")
    key(p, "idle", "location", kz, index=2, interp="LINEAR")
    if drift:
        key(p, "idle", "location", kx, index=0, interp="LINEAR")


# ------------------------------------------------------------- finishing --
def _select(objs, active=None):
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = active or (objs[0] if objs else None)


def _animated_ancestor(o):
    p = o.parent
    while p is not None:
        if p.animation_data and p.animation_data.nla_tracks:
            return True
        if p.name.startswith(("spin_", "sway_")):
            return True
        p = p.parent
    return False


def tri_count(objs=None):
    n = 0
    dg = bpy.context.evaluated_depsgraph_get()
    for o in objs or all_meshes():
        if o.name.startswith("_"):
            continue
        ev = o.evaluated_get(dg)
        me = ev.to_mesh()
        n += sum(len(p.vertices) - 2 for p in me.polygons)
        ev.to_mesh_clear()
    return n


def _cull(o, ceiling=False):
    """Delete faces the game camera can never see: ones turned towards the
    back wall and, for floor decor, bottoms lying on the floor (for ceiling
    decor, tops pressed against the ceiling)."""
    mw = o.matrix_world
    nm = mw.to_3x3().inverted().transposed()
    bm = bmesh.new()
    bm.from_mesh(o.data)
    kill = []
    for f in bm.faces:
        n = (nm @ f.normal).normalized()
        c = mw @ f.calc_center_median()
        if n.y > 0.5:
            kill.append(f)
        elif not ceiling and n.z < -0.9 and c.z < 0.03:
            kill.append(f)
        elif ceiling and n.z > 0.9 and c.z > -0.03:
            kill.append(f)
    if kill:
        bmesh.ops.delete(bm, geom=kill, context="FACES")
        bm.to_mesh(o.data)
    bm.free()


def finish(name, windows=(), ceiling=False, tex=2048, cull=True, preview=True, theme=None, ao=0.45):
    """Apply, cull, join, bake (with a temporary wall behind), export and
    preview.  `windows` are the theme's openings (x, z, w, h)."""
    # 1. Apply modifiers on every mesh.
    meshes = [o for o in all_meshes() if not o.name.startswith("_")]
    _select(meshes)
    bpy.ops.object.convert(target="MESH")
    # 2. Static meshes: apply transforms so their object space is world space
    #    (the pattern materials and the noise stay undistorted after the join).
    static = [o for o in all_meshes() if o.parent is None and not o.name.startswith("_")]
    _select(static)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    if cull:
        for o in all_meshes():
            if o.name.startswith("_") or _animated_ancestor(o):
                continue
            _cull(o, ceiling)
    # Drop meshes left empty.
    for o in list(all_meshes()):
        if len(o.data.polygons) == 0:
            bpy.data.objects.remove(o, do_unlink=True)
    join_static("decor")
    tris = tri_count()
    print("TRIS %s %d" % (name, tris))
    # 3. Bake with a temporary wall (and ceiling slab) for contact shadows.
    temp = _occluders(windows, ceiling)
    if os.environ.get("NO_BAKE") != "1":
        bake_textures(name, tex=int(os.environ.get("BAKE_TEX", 0)) or tex, ground=not ceiling, ao_distance=ao)
    for o in temp:
        bpy.data.objects.remove(o, do_unlink=True)
    _, preview_dir = parse_args()
    argv = sys.argv[:]
    if "--preview" in sys.argv:          # export() would render its own preview
        i = sys.argv.index("--preview")
        del sys.argv[i:i + 2]
    export(name, bake=False)
    sys.argv[:] = argv
    if preview_dir and preview:
        front_preview(name, preview_dir, windows=windows, ceiling=ceiling, theme=theme)
    return tris


def _occluders(windows, ceiling):
    """A wall behind the decor (with the window openings) and the floor or
    ceiling slab, only while baking."""
    grey = pbr("neon", (0.05, 0.05, 0.05), strength=0.0, name="_occluder")
    objs = []
    if ceiling:
        objs.append(box((15.0, 2.0, 0.1), (7.5, 0.95, 0.05), grey, name="_ceil"))
        objs.append(box((15.0, 0.1, 3.5), (7.5, 1.99, -1.75), grey, name="_wall"))
    else:
        for (x, z, w, h) in _wall_rects(15.0, 9.6, windows):
            objs.append(box((w, 0.1, h), (x + w / 2, 1.99, z + h / 2), grey, name="_wall"))
    return objs


def _wall_rects(w, h, windows):
    """Mirror of Backdrop._wall_pieces: rectangles covering the wall minus
    the windows."""
    edges = sorted({0.0, h} | {r[1] for r in windows} | {r[1] + r[3] for r in windows})
    out = []
    for y0, y1 in zip(edges, edges[1:]):
        if y1 - y0 < 1e-3:
            continue
        ym = (y0 + y1) / 2
        crossing = sorted([r for r in windows if r[1] < ym < r[1] + r[3]], key=lambda r: r[0])
        x = 0.0
        for r in crossing:
            if r[0] > x:
                out.append((x, y0, r[0] - x, y1 - y0))
            x = max(x, r[0] + r[2])
        if x < w:
            out.append((x, y0, w - x, y1 - y0))
    return out


wall_rects = _wall_rects


def front_preview(name, preview_dir, windows=(), ceiling=False, theme=None, width=900, samples=None):
    """Render the model the way the game frames a room: straight on from the
    front, with the shell wall, floor/ceiling slabs, a city glow in the
    windows, the key light, the room's omni light and purple ambient."""
    theme = theme or {}
    wall_c = theme.get("wall", (0.12, 0.05, 0.23))
    trim_c = theme.get("trim", (0.7, 0.3, 1.0))
    floor_c = theme.get("floor", (0.09, 0.04, 0.16))
    os.makedirs(preview_dir, exist_ok=True)
    scn = bpy.context.scene
    lin = lambda c: tuple(pow(v, 2.2) for v in c)   # theme colours are sRGB
    wall_m = pbr("neon", lin(wall_c), strength=0.0, name="_pv_wall")
    wall_m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.9
    floor_m = pbr("neon", lin(floor_c), strength=0.0, name="_pv_floor")
    city = pbr("neon", (0.02, 0.01, 0.05), emit=(0.35, 0.12, 0.45), strength=1.0, name="_pv_city")
    trim = pbr("neon", lin(trim_c), strength=3.0, name="_pv_trim")
    if ceiling:
        box((15.0, 2.2, 0.3), (7.5, 0.9, 0.15), wall_m, name="_pv")
        box((15.0, 0.3, 4.0), (7.5, 2.1, -2.0), wall_m, name="_pv")
        z_lo, z_hi = -3.2, 0.4
    else:
        for (x, z, w, h) in _wall_rects(15.0, 10.0, windows):
            box((w, 0.3, h), (x + w / 2, 2.1, z + h / 2), wall_m, name="_pv")
        for (x, z, w, h) in windows:
            box((w, 0.05, h), (x + w / 2, 6.0, z + h / 2), city, name="_pv")
            # a few lit windows of the city
            rnd = _rng(int(x * 10 + z))
            for k in range(int(w * h * 4)):
                c = [(1.0, 0.3, 0.7), (0.3, 0.9, 1.0), (1.0, 0.8, 0.4)][k % 3]
                box((0.12, 0.05, 0.08), (x + 0.1 + rnd() * (w - 0.2), 5.9, z + 0.1 + rnd() * (h - 0.2)),
                    pbr("neon", c, strength=3.0, name="_pv_lit%d" % (k % 3)), name="_pv")
        box((15.0, 2.2, 0.3), (7.5, 0.9, -0.15), floor_m, name="_pv")
        box((15.0, 0.06, 0.06), (7.5, 1.92, 0.05), trim, name="_pv")
        z_lo, z_hi = -0.3, 9.8
    cam_data = bpy.data.cameras.new("pv_cam")
    cam_data.type = "PERSP"
    cam_data.sensor_fit = "HORIZONTAL"
    dist = 30.0
    view_w = 16.4
    cam_data.angle = 2 * math.atan(view_w / 2 / dist)
    cam = bpy.data.objects.new("_pv_cam", cam_data)
    bpy.context.collection.objects.link(cam)
    zc = (z_lo + z_hi) / 2
    dz = -6.0 if ceiling else 1.5     # the camera looks up at ceilings
    cam.location = (7.5, -dist, zc + dz)
    cam.rotation_euler = (math.radians(90) - math.atan(dz / dist), 0, 0)
    scn.camera = cam
    aspect = (z_hi - z_lo) / view_w
    scn.render.resolution_x = width
    scn.render.resolution_y = int(width * aspect)
    # Lights: key (sun from the front-left-top), the room's omni, ambient.
    sd = bpy.data.lights.new("pv_sun", "SUN")
    sd.energy = float(os.environ.get("PV_SUN", 1.3))
    sd.color = (1.0, 0.92, 0.9)
    sun = bpy.data.objects.new("_pv_sun", sd)
    bpy.context.collection.objects.link(sun)
    sun.rotation_euler = (math.radians(55), 0, math.radians(-30))
    od = bpy.data.lights.new("pv_omni", "POINT")
    tc = lin(trim_c)
    od.color = tuple(0.5 * c + 0.5 for c in tc)
    od.energy = float(os.environ.get("PV_OMNI", 5000.0))
    od.shadow_soft_size = 1.0
    omni = bpy.data.objects.new("_pv_omni", od)
    bpy.context.collection.objects.link(omni)
    omni.location = (7.5, -0.5, (z_lo + z_hi) / 2 + 1.0)
    scn.world = scn.world or bpy.data.worlds.new("w")
    scn.world.use_nodes = True
    bg = scn.world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = (0.26, 0.15, 0.52, 1.0)
    bg.inputs[1].default_value = float(os.environ.get("PV_AMB", 0.45))
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples or int(os.environ.get("PV_SAMPLES", 24))
    scn.cycles.use_denoising = False
    scn.cycles.max_bounces = 3
    scn.render.film_transparent = False
    try:
        scn.view_settings.view_transform = "Filmic"
    except TypeError:
        pass
    scn.render.filepath = os.path.join(preview_dir, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("PREVIEW %s" % scn.render.filepath)


# ----------------------------------------------------------------- props --
def by_normal(o, top, side):
    """Give faces looking up/down material `top` and the rest `side` (for
    pattern materials that need the right projection plane per face)."""
    o.data.materials.clear()
    o.data.materials.append(mat(side))
    o.data.materials.append(mat(top))
    for p in o.data.polygons:
        p.material_index = 1 if abs(p.normal.z) > 0.7 else 0
    return o


def curtain(x0, x1, z0, z1, y, m, folds=5, amp=0.08, name="curtain", sway=0.02, phase=0.0, seed=1,
            pleats=True, rings=None):
    """A hanging drape with soft folds (a sheet facing the camera, folds
    towards -Y from `y`), on a pivot at its top that drifts in a draught.
    Returns the pivot."""
    rnd = _rng(seed)
    ph = [rnd() * 0.8 for _ in range(folds + 2)]
    nx, nz = folds * 6, 5

    def fn(u, v):
        k = u * folds
        fi = int(min(k, folds - 1))
        wobble = ph[fi] * math.sin(math.pi * (k - fi))
        a = amp * (0.75 + 0.5 * (1 - v)) * (1.0 + 0.3 * wobble)
        dy = a * (0.5 + 0.5 * math.sin(2 * math.pi * k + phase))
        flare = (1 - v) ** 2 * 0.06 * (u - 0.5) * 2
        return (x0 + (x1 - x0) * u + flare, y - dy, z0 + (z1 - z0) * v)

    p = pivot("sway_" + name if False else name, ((x0 + x1) / 2, y, z1))
    grid_mesh(nx, nz, fn, m, name=name + "_mesh", parent=p)
    if rings:
        for i in range(folds + 1):
            torus(0.05, 0.012, (x0 + (x1 - x0) * i / folds, y - 0.02, z1 + 0.06), rings,
                  rot=(math.pi / 2, 0, 0), major_segments=8, minor_segments=4)
    if sway:
        p.rotation_euler = (-sway * 0.5, 0, 0)
        swing(p, "X", amp=sway * 0.5, phase=phase)
        swing(p, "Y", amp=sway * 0.6, phase=phase + 1.3)
    return p


def curtain_rod(x0, x1, z, y, m, r=0.035, finial=None):
    rod((x0, y, z), (x1, y, z), r, m, verts=10)
    for x in (x0, x1):
        ball(r * 2.2, (x, y, z), finial or m, seg=10, rings=6)
    for x in (x0 + 0.25, x1 - 0.25):
        rod((x, y, z), (x, WALL, z + 0.02), r * 0.6, m, verts=6)
        cyl(r * 1.8, 0.03, (x, WALL - 0.015, z + 0.02), m, rot=(math.pi / 2, 0, 0), verts=10)


def table_lamp(x, y, z, base_m, shade_m, brass, h=1.0, shade_r=0.34, bulb=None):
    """Ceramic urn base, brass neck and a glowing drum shade.  Total height
    about 1.75 * h (game metres)."""
    lathe([(0.12 * h, 0), (0.2 * h, 0.08 * h), (0.26 * h, 0.3 * h), (0.22 * h, 0.5 * h), (0.09 * h, 0.62 * h),
           (0.07 * h, 0.7 * h)], (x, y, z), base_m, verts=14)
    cyl(0.03 * h, 0.35 * h, (x, y, z + 0.87 * h), brass, verts=8, bevel=0)
    lathe([(shade_r * 1.12, 0), (shade_r, 0.55 * h)], (x, y, z + 0.95 * h), shade_m, verts=18, cap_top=False)
    torus(shade_r * 1.12, 0.012, (x, y, z + 0.95 * h), brass, major_segments=18, minor_segments=4)
    torus(shade_r, 0.012, (x, y, z + 1.5 * h), brass, major_segments=18, minor_segments=4)
    if bulb is not None:
        cyl(shade_r * 1.05, 0.01, (x, y, z + 0.97 * h), bulb, verts=14, bevel=0)


def leaf(x, y, z, length, width, yaw, pitch, m, roll=0.0, cup=0.25, n=6, parent=None):
    """A broad leaf card (cupped along its midrib) whose base sits at
    (x, y, z); it points along +X, its face up (+Z), before roll (about
    its midrib), pitch and yaw."""
    bm = bmesh.new()
    mid, left, right = [], [], []
    for i in range(n + 1):
        t = i / n
        w = width * 0.5 * math.sin(math.pi * min(1.0, t * 1.05)) ** 0.7
        droop = -0.12 * length * t * t
        mid.append(bm.verts.new((t * length, 0, droop)))
        if 0 < i < n:
            left.append(bm.verts.new((t * length, w, droop - cup * w)))
            right.append(bm.verts.new((t * length, -w, droop - cup * w)))
    L = [mid[0]] + left + [mid[-1]]
    R = [mid[0]] + right + [mid[-1]]
    for i in range(n):
        for side, rim in ((0, L), (1, R)):
            a, b = mid[i], mid[i + 1]
            c, d = rim[i + 1], rim[i]
            quad = [a, b, c, d] if side == 0 else [b, a, d, c]
            uniq = []
            for v in quad:
                if v not in uniq:
                    uniq.append(v)
            if len(uniq) >= 3:
                bm.faces.new(uniq)
    me = bpy.data.meshes.new("leaf")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new("leaf", me)
    bpy.context.collection.objects.link(o)
    o.data.materials.append(mat(m))
    _smooth(o, 80.0)
    o.location = (x, y, z)
    o.rotation_euler = (roll, -pitch, yaw)
    if parent is not None:
        attach(o, parent)
    return o


def monstera(x, y, pot_m, leaf_m, stem_m, h=3.2, seed=3, n=11, sway_groups=2, name="plant", pot_h=0.9, reach=(0.4, 1.2),
             bias=0.0):
    """A leafy plant (monstera/philodendron) in a tall planter.  A couple of
    leaf clusters sit on pivots that nod in the air conditioning."""
    rnd = _rng(seed)
    lathe([(0.30, 0), (0.36, 0.1), (0.40, pot_h * 0.9), (0.42, pot_h)], (x, y, 0), pot_m, verts=16)
    cyl(0.38, 0.04, (x, y, pot_h - 0.03), M("concrete", (0.05, 0.03, 0.02)), verts=14, bevel=0)
    groups = [pivot("%s_%d" % (name, g), (x, y, pot_h)) for g in range(sway_groups)]
    for i in range(n):
        a = (i / n) * math.tau + rnd() * 0.5
        side = max(-1.0, min(1.0, math.cos(a) + bias))
        top = pot_h + (h - pot_h) * (0.35 + 0.65 * rnd())
        rr = reach[0] + (reach[1] - reach[0]) * rnd()
        tip = (x + side * rr, y - 0.25 - rnd() * 0.3, top)
        g = groups[i % sway_groups] if i % 3 != 0 else None
        mid = (x + side * rr * 0.4, y - 0.1, pot_h + (top - pot_h) * 0.6)
        tube_path([(x + side * 0.05, y, pot_h - 0.05), mid, tip], 0.018, stem_m, verts=5, parent=g, cap=False)
        yaw = (0 if side > 0 else math.pi) + (rnd() - 0.5) * 0.9
        yaw = yaw - 0.25 * (1 if side > 0 else -1)
        size = 0.55 + 0.45 * rnd()
        leaf(tip[0], tip[1], tip[2], 0.9 * size * (h / 3.2), 0.75 * size * (h / 3.2), yaw, -0.2 - 0.5 * rnd(), leaf_m,
             roll=(1.3 + (rnd() - 0.5) * 0.4) * (1 if side > 0 else -1), parent=g)
    for i, g in enumerate(groups):
        swing(g, "Y", amp=0.025, phase=i * 2.1)
    return groups


def ac_split(x, z, body_m, dark_m, led=None, w=1.9, name="ac_flap"):
    """A split air-conditioner on the wall (centre x, z): rounded body,
    intake grille, and a louvre flap that sweeps back and forth."""
    d = 0.55
    y = WALL - d / 2
    box((w, d, 0.62), (x, y, z), body_m, bev=0.08, seg=3)
    box((w * 0.96, 0.02, 0.08), (x, WALL - d - 0.005, z + 0.2), dark_m)       # panel seam
    box((w * 0.9, 0.3, 0.1), (x, WALL - d + 0.12, z - 0.29), dark_m)           # outlet slot
    p = pivot(name, (x, WALL - d + 0.06, z - 0.3))
    box((w * 0.88, 0.2, 0.025), (x, WALL - d - 0.02, z - 0.34), body_m, rot=(0.35, 0, 0), parent=p)
    p.rotation_euler = (0.0, 0, 0)
    swing(p, "X", amp=0.28, cycles=1)
    if led is not None:
        box((0.14, 0.02, 0.06), (x + w * 0.32, WALL - d - 0.012, z + 0.02), led)
        box((0.03, 0.02, 0.03), (x + w * 0.42, WALL - d - 0.012, z + 0.02), glow((0.2, 1.0, 0.4), 4.0))
    # refrigerant line down into the wall
    tube_path([(x + w / 2 - 0.1, WALL - 0.15, z - 0.2), (x + w / 2 + 0.15, WALL - 0.15, z - 0.35),
               (x + w / 2 + 0.15, WALL - 0.15, z - 1.2)], 0.045, M("rubber", (0.55, 0.55, 0.55)), verts=6)
    return p


def moulding(x0, x1, z, profile, m, y=WALL, avoid=()):
    """A run of moulding along the wall: `profile` [(depth, height), ...]
    (depth from the wall, height above z), split around windows."""
    spans = [(x0, x1)]
    for (rx, rz, rw, rh) in avoid:
        top = z + max(h for _, h in profile)
        if rz - 0.15 < top and z < rz + rh + 0.15:
            out = []
            for a, b in spans:
                lo, hi = rx - 0.15, rx + rw + 0.15
                if hi <= a or lo >= b:
                    out.append((a, b))
                    continue
                if lo > a:
                    out.append((a, lo))
                if hi < b:
                    out.append((hi, b))
            spans = out
    for a, b in spans:
        if b - a < 0.1:
            continue
        bm = bmesh.new()
        ring_a = [bm.verts.new((a, y - dd, z + hh)) for dd, hh in profile]
        ring_b = [bm.verts.new((b, y - dd, z + hh)) for dd, hh in profile]
        for i in range(len(profile) - 1):
            bm.faces.new((ring_a[i], ring_a[i + 1], ring_b[i + 1], ring_b[i]))
        bm.faces.new(list(reversed(ring_a)))
        bm.faces.new(ring_b)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
        me = bpy.data.meshes.new("moulding")
        bm.to_mesh(me)
        bm.free()
        o = bpy.data.objects.new("moulding", me)
        bpy.context.collection.objects.link(o)
        o.data.materials.append(mat(m))


CROWN = [(0.0, 0.0), (0.04, 0.02), (0.06, 0.08), (0.14, 0.16), (0.2, 0.22), (0.22, 0.3), (0.0, 0.3)]
SKIRT = [(0.0, 0.0), (0.05, 0.0), (0.05, 0.22), (0.03, 0.26), (0.03, 0.3), (0.0, 0.32)]
RAIL = [(0.0, 0.0), (0.03, 0.01), (0.05, 0.04), (0.05, 0.08), (0.03, 0.11), (0.0, 0.12)]

# Stroke font for neon tube lettering: polylines in a 1 x 1 cell.
STROKES = {
    "A": [[(0, 0), (0.5, 1), (1, 0)], [(0.22, 0.42), (0.78, 0.42)]],
    "B": [[(0, 0), (0, 1), (0.7, 1), (0.9, 0.85), (0.9, 0.62), (0.7, 0.52), (0, 0.52)], [(0.7, 0.52), (1, 0.38), (1, 0.14), (0.8, 0), (0, 0)]],
    "C": [[(1, 0.82), (0.78, 1), (0.22, 1), (0, 0.78), (0, 0.22), (0.22, 0), (0.78, 0), (1, 0.18)]],
    "D": [[(0, 0), (0, 1), (0.6, 1), (1, 0.7), (1, 0.3), (0.6, 0), (0, 0)]],
    "E": [[(1, 1), (0, 1), (0, 0), (1, 0)], [(0, 0.52), (0.72, 0.52)]],
    "F": [[(1, 1), (0, 1), (0, 0)], [(0, 0.52), (0.72, 0.52)]],
    "G": [[(1, 0.82), (0.78, 1), (0.22, 1), (0, 0.78), (0, 0.22), (0.22, 0), (0.78, 0), (1, 0.2), (1, 0.45), (0.55, 0.45)]],
    "H": [[(0, 0), (0, 1)], [(1, 0), (1, 1)], [(0, 0.52), (1, 0.52)]],
    "I": [[(0.5, 0), (0.5, 1)]],
    "K": [[(0, 0), (0, 1)], [(1, 1), (0, 0.45)], [(0.3, 0.6), (1, 0)]],
    "L": [[(0, 1), (0, 0), (1, 0)]],
    "M": [[(0, 0), (0, 1), (0.5, 0.45), (1, 1), (1, 0)]],
    "N": [[(0, 0), (0, 1), (1, 0), (1, 1)]],
    "O": [[(0.22, 0), (0, 0.22), (0, 0.78), (0.22, 1), (0.78, 1), (1, 0.78), (1, 0.22), (0.78, 0), (0.22, 0)]],
    "P": [[(0, 0), (0, 1), (0.75, 1), (1, 0.82), (1, 0.62), (0.75, 0.46), (0, 0.46)]],
    "R": [[(0, 0), (0, 1), (0.75, 1), (1, 0.82), (1, 0.62), (0.75, 0.48), (0, 0.48)], [(0.45, 0.48), (1, 0)]],
    "S": [[(1, 0.82), (0.8, 1), (0.2, 1), (0, 0.8), (0.1, 0.58), (0.9, 0.42), (1, 0.2), (0.8, 0), (0.2, 0), (0, 0.18)]],
    "T": [[(0, 1), (1, 1)], [(0.5, 1), (0.5, 0)]],
    "U": [[(0, 1), (0, 0.22), (0.22, 0), (0.78, 0), (1, 0.22), (1, 1)]],
    "V": [[(0, 1), (0.5, 0), (1, 1)]],
    "W": [[(0, 1), (0.22, 0), (0.5, 0.6), (0.78, 0), (1, 1)]],
    "X": [[(0, 0), (1, 1)], [(0, 1), (1, 0)]],
    "Y": [[(0, 1), (0.5, 0.5), (1, 1)], [(0.5, 0.5), (0.5, 0)]],
    "Z": [[(0, 1), (1, 1), (0, 0), (1, 0)]],
    "0": [[(0.22, 0), (0, 0.22), (0, 0.78), (0.22, 1), (0.78, 1), (1, 0.78), (1, 0.22), (0.78, 0), (0.22, 0)]],
    "1": [[(0.2, 0.8), (0.55, 1), (0.55, 0)]],
    "2": [[(0, 0.8), (0.2, 1), (0.8, 1), (1, 0.8), (1, 0.6), (0, 0), (1, 0)]],
    "3": [[(0, 0.85), (0.2, 1), (0.8, 1), (1, 0.82), (1, 0.62), (0.75, 0.52), (0.3, 0.52)], [(0.75, 0.52), (1, 0.4), (1, 0.18), (0.8, 0), (0.2, 0), (0, 0.15)]],
    "4": [[(0.8, 0), (0.8, 1), (0, 0.3), (1, 0.3)]],
    "5": [[(1, 1), (0.05, 1), (0, 0.55), (0.7, 0.58), (1, 0.4), (1, 0.18), (0.8, 0), (0.2, 0), (0, 0.15)]],
    "6": [[(0.9, 0.9), (0.7, 1), (0.25, 1), (0, 0.7), (0, 0.22), (0.22, 0), (0.78, 0), (1, 0.2), (1, 0.4), (0.78, 0.58), (0.2, 0.58), (0, 0.4)]],
    "8": [[(0.5, 0.52), (0.15, 0.62), (0.05, 0.82), (0.25, 1), (0.75, 1), (0.95, 0.82), (0.85, 0.62), (0.5, 0.52), (0.1, 0.4), (0, 0.18), (0.2, 0), (0.8, 0), (1, 0.18), (0.9, 0.4), (0.5, 0.52)]],
    "9": [[(0.1, 0.1), (0.3, 0), (0.75, 0), (1, 0.3), (1, 0.78), (0.78, 1), (0.22, 1), (0, 0.8), (0, 0.6), (0.22, 0.42), (0.8, 0.42), (1, 0.6)]],
    "7": [[(0, 1), (1, 1), (0.35, 0)]],
    "!": [[(0.5, 1), (0.5, 0.3)], [(0.5, 0.1), (0.5, 0.0)]],
    "-": [[(0.1, 0.5), (0.9, 0.5)]],
    "/": [[(0, 0), (1, 1)]],
    "+": [[(0.5, 0.15), (0.5, 0.85)], [(0.15, 0.5), (0.85, 0.5)]],
    "<": [[(1, 1), (0, 0.5), (1, 0)]],
    ">": [[(0, 1), (1, 0.5), (0, 0)]],
    "_": [[(0, 0), (1, 0)]],
    "$": [[(1, 0.82), (0.8, 0.95), (0.2, 0.95), (0, 0.8), (0.1, 0.58), (0.9, 0.42), (1, 0.2), (0.8, 0.05), (0.2, 0.05), (0, 0.18)], [(0.5, 1.1), (0.5, -0.1)]],
}


def neon_text(text, x, z, h, m, y=WALL - 0.06, r=0.028, aspect=0.62, gap=0.28, flicker_idx=(), seed=5,
              tube_m=None, italic=0.0):
    """Tube lettering on the wall, left edge at x, baseline at z, cap height
    h.  Letters listed in `flicker_idx` sit on pivots that stutter like a
    failing transformer.  Returns the total width."""
    cw = h * aspect
    cx = x
    for i, ch in enumerate(text.upper()):
        if ch == " ":
            cx += cw * 0.6
            continue
        strokes = STROKES.get(ch)
        if strokes is None:
            cx += cw
            continue
        w = cw * (0.3 if ch in "I!1" else 1.0)
        par = None
        if i in flicker_idx:
            par = pivot("neon_%d_%d" % (seed, i), (cx + w / 2, y, z + h / 2))
        for s in strokes:
            pts = [(cx + px * w + italic * py * h, y, z + py * h) for px, py in s]
            tube_path(pts, r, m, verts=6, parent=par, cap=False)
            # dark electrode caps at each end
        if par is not None:
            flicker(par, seed=seed + i, bursts=3)
        cx += w + cw * gap
    return cx - x - cw * gap


def bottle(x, y, z, h, m, cap=None, r=None):
    r = r or h * 0.16
    lathe([(r, 0), (r, h * 0.62), (r * 0.45, h * 0.8), (r * 0.35, h * 0.97), (r * 0.38, h)], (x, y, z), m, verts=10)
    if cap is not None:
        cyl(r * 0.4, h * 0.06, (x, y, z + h + h * 0.03), cap, verts=8, bevel=0)


def books(x0, y, z, n, h, seed=2, cols=None, lean_last=True, depth=0.5):
    """A row of book spines standing on a shelf from x0 to the right.
    Returns the end x."""
    rnd = _rng(seed)
    cols = cols or [(0.30, 0.04, 0.05), (0.04, 0.10, 0.22), (0.05, 0.16, 0.08), (0.45, 0.30, 0.08), (0.20, 0.06, 0.25), (0.5, 0.45, 0.4)]
    x = x0
    for i in range(n):
        t = h * (0.28 + 0.12 * rnd()) / 0.4 * 0.1 * 4 * 0.25 + h * 0.0
        bw = h * (0.12 + 0.1 * rnd())
        bh = h * (0.75 + 0.25 * rnd())
        c = cols[int(rnd() * len(cols)) % len(cols)]
        box((bw, depth * (0.8 + 0.2 * rnd()), bh), (x + bw / 2, y, z + bh / 2), M("plastic", c, rough=0.7))
        x += bw + 0.005
    return x


def mirror_panel(x, z, w, h, frame_m, y=WALL, glass_m=None, sheen=None, depth=0.06):
    """A wall mirror: frame, a dark reflective pane and two diagonal sheen
    streaks so it reads as glass from far away."""
    box((w, depth, h), (x, y - depth / 2, z), frame_m, bev=0.02)
    g = glass_m or M("chrome", (0.12, 0.14, 0.2), rough=0.03)
    box((w - 0.12, 0.02, h - 0.12), (x, y - depth - 0.005, z), g)
    if sheen is not None:
        for k, (dx, ww) in enumerate(((-0.15, 0.12), (0.12, 0.05))):
            ln = min(w, h) * 0.8
            box((ww * min(w, 1.2), 0.01, ln), (x + dx * w, y - depth - 0.018, z + 0.05 * k), sheen, rot=(0, 0.6, 0))


def smoke_detector(x, y, z, body_m, led_m, name="led_smoke"):
    cyl(0.16, 0.06, (x, y, z - 0.03), body_m, verts=16, bevel=0.01)
    cyl(0.1, 0.03, (x, y, z - 0.07), body_m, verts=12, bevel=0)
    p = pivot(name, (x + 0.07, y - 0.05, z - 0.07))
    ball(0.018, (x + 0.07, y - 0.05, z - 0.075), led_m, seg=6, rings=4, parent=p)
    blink(p, [(8, 116)])
    return p


def sprinkler(x, y, z, m):
    cyl(0.06, 0.02, (x, y, z - 0.01), m, verts=10, bevel=0)
    cyl(0.018, 0.1, (x, y, z - 0.07), m, verts=6, bevel=0)
    cyl(0.05, 0.012, (x, y, z - 0.13), m, verts=8, bevel=0)


def downlight(x, y, z, rim_m, lamp_m, r=0.16):
    cyl(r, 0.02, (x, y, z - 0.01), rim_m, verts=16, bevel=0)
    cyl(r * 0.7, 0.012, (x, y, z - 0.022), lamp_m, verts=14, bevel=0)


def ceiling_fan(x, y, z, drop, blade_m, body_m, lamp_m=None, blades=5, r=1.3, name="fan", turns=3, rod_m=None, k=1.0):
    """A ceiling fan hanging `drop` below z: canopy, down-rod, motor, blades
    on a pivot spinning in the idle clip (k scales the hardware).  Returns
    the pivot."""
    cyl(0.18 * k, 0.12 * k, (x, y, z - 0.06 * k), body_m, verts=14, bevel=0.01)
    cyl(0.035 * k, drop, (x, y, z - drop / 2), rod_m or body_m, verts=8, bevel=0)
    zm = z - drop
    lathe([(0.12 * k, 0.14 * k), (0.3 * k, 0.07 * k), (0.33 * k, -0.05 * k), (0.22 * k, -0.14 * k), (0.0, -0.16 * k)],
          (x, y, zm), body_m, verts=16)
    p = pivot(name, (x, y, zm - 0.02))
    for i in range(blades):
        a = i / blades * math.tau + 0.3
        ca, sa = math.cos(a), math.sin(a)
        box((0.4 * k, 0.07 * k, 0.035 * k), (x + ca * 0.42 * k, y + sa * 0.42 * k, zm - 0.03), body_m, rot=(0, 0, a), parent=p)
        rr = 0.55 * k
        box((r - rr, 0.3 * k, 0.025 * k), (x + ca * (rr + (r - rr) / 2), y + sa * (rr + (r - rr) / 2), zm - 0.02),
            blade_m, rot=(0.14, 0, a), bev=0.02, parent=p)
    if lamp_m is not None:
        lathe([(0.24 * k, 0.0), (0.22 * k, -0.14 * k), (0.12 * k, -0.24 * k), (0.0, -0.26 * k)], (x, y, zm - 0.15 * k),
              lamp_m, verts=14)
    spin_idle(p, "Z", turns)
    return p


def fluorescent(x, y, z, length, housing_m, tube_m, name=None, flick=None, width=0.32, tubes=2):
    """A surface-mounted fluorescent fixture under the ceiling at z: a
    metal housing, open reflector and glowing tubes (on a pivot that
    flickers when `flick` is a seed)."""
    box((length, width, 0.1), (x, y, z - 0.05), housing_m, bev=0.015)
    for s in (-1, 1):
        box((0.03, width, 0.06), (x + s * (length / 2 - 0.02), y, z - 0.13), housing_m)
    par = pivot(name, (x, y, z - 0.13)) if flick is not None else None
    for i in range(tubes):
        off = (i - (tubes - 1) / 2) * width * 0.45
        rod((x - length / 2 + 0.05, y + off, z - 0.13), (x + length / 2 - 0.05, y + off, z - 0.13), 0.028, tube_m,
            verts=6, parent=par)
    if par is not None:
        flicker(par, seed=flick, bursts=2)
    return par


def vent_grille(x, z, w, h, frame_m, slat_m, y=WALL, slats=None, rot=None):
    box((w, 0.05, h), (x, y - 0.025, z), frame_m, bev=0.01)
    box((w - 0.1, 0.02, h - 0.1), (x, y - 0.045, z), M("rubber", (0.01, 0.01, 0.012)))
    n = slats or max(int(h / 0.08), 3)
    for i in range(n):
        box((w - 0.12, 0.05, 0.02), (x, y - 0.06, z - h / 2 + 0.06 + i * (h - 0.12) / max(n - 1, 1)), slat_m,
            rot=(0.5, 0, 0))


def exit_sign(x, y, z, body_m, text_m, hang=0.0):
    """A lit EXIT box (running man omitted) hung from the ceiling or wall."""
    if hang:
        for s in (-1, 1):
            rod((x + s * 0.3, y, z), (x + s * 0.3, y, z - hang), 0.01, body_m, verts=4)
    zc = z - hang - 0.2
    box((1.0, 0.12, 0.38), (x, y, zc), body_m, bev=0.02)
    box((0.92, 0.02, 0.3), (x, y - 0.065, zc), glow((0.1, 0.9, 0.3), 1.2, (0.02, 0.2, 0.05)))
    neon_text("EXIT", x - 0.34, zc - 0.08, 0.16, glow((0.85, 1.0, 0.85), 3.0), y=y - 0.08, r=0.012, gap=0.3)


def drop_ceiling(m, grid_m, y0=0.0, y1=1.95, z=0.0, tile=1.5, missing=(), stained=(), stain_m=None):
    """A suspended ceiling seen from below: tile panel with a T-bar grid; a
    few tiles missing (dark void) or water-stained."""
    box((15.0, y1 - y0, 0.03), (7.5, (y0 + y1) / 2, z - 0.015), m)
    nx = int(15.0 / tile)
    for i in range(nx + 1):
        box((0.04, y1 - y0, 0.025), (i * tile, (y0 + y1) / 2, z - 0.04), grid_m)
    for yy in (y0 + (y1 - y0) / 2,):
        box((15.0, 0.04, 0.025), (7.5, yy, z - 0.04), grid_m)
    for i in missing:
        box((tile - 0.06, (y1 - y0) / 2 - 0.06, 0.01), (i * tile + tile / 2, y0 + (y1 - y0) * 0.25, z - 0.034),
            M("rubber", (0.005, 0.005, 0.006)))
    for i in stained:
        ball(tile * 0.3, (i * tile + tile / 2, y0 + (y1 - y0) * 0.72, z - 0.031), stain_m or M("concrete", (0.25, 0.18, 0.1)),
             scale=(1.2, 0.8, 0.02), seg=10, rings=4)


def front_soffit(m, trim_m=None, glow_m=None, depth=0.4, h=0.3):
    """A plaster bulkhead along the front edge of the ceiling (frames the
    room from the game camera) with an optional cove light behind it."""
    box((15.0, depth, h), (7.5, depth / 2, -h / 2), m, bev=0.02)
    if trim_m is not None:
        box((15.0, 0.08, 0.05), (7.5, depth + 0.02, -h + 0.02), trim_m)
    if glow_m is not None:
        box((14.9, 0.03, 0.03), (7.5, depth + 0.05, -h + 0.06), glow_m)
