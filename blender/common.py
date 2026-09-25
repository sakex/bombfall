# Shared kit for BombFall's Blender-built models.
#
# Every model in this folder is a small Python script run headlessly:
#     blender -b --python blender/<name>.py -- [--out DIR] [--preview DIR]
# Each script builds its object from primitives, exports a .glb next to the
# other models (assets/models/<name>.glb by default) and, when --preview is
# given, renders a small Cycles turntable still so the result can be eyeballed
# without opening Blender.
#
# Conventions
#   * 1 Blender unit = 1 metre = 1 game cell (the old 2D game used 64 px cells).
#   * Blender is Z-up; the glTF exporter converts to Godot's Y-up. The front of
#     a model faces Blender -Y, which becomes Godot +Z (towards the camera).
#   * Floor-standing props have their origin at the bottom centre; things that
#     tumble (bombs, coins, drones) are centred on their origin.
#   * Empties become Node3D pivots in Godot and keep their names, so scripts
#     can find them with get_node("%leg_l") style paths. Names used by the
#     game: leg_l/leg_r/arm_l/arm_r (player), rotor_1..4 (drone), gun
#     (wall gun), wing_l/wing_r (boss bat), belt (treadmill), ring (light ring),
#     top (button), screen (desktop monitor), lid (toilet).
#   * Materials are flat colours with optional emission: the game's look is
#     dark metal + neon strips, and the mobile renderer adds glow on top.
import math
import os
import sys

import bpy
import mathutils

# ---------------------------------------------------------------- palette --
# Base colours (linear RGB).
DARK = (0.020, 0.018, 0.028)
GUNMETAL = (0.070, 0.075, 0.095)
STEEL = (0.32, 0.34, 0.40)
CHROME = (0.62, 0.64, 0.70)
SLATE = (0.13, 0.14, 0.19)
NAVY = (0.045, 0.045, 0.12)
PLUM = (0.16, 0.05, 0.22)
GRAPE = (0.30, 0.09, 0.42)
WHITE = (0.85, 0.86, 0.90)
BONE = (0.72, 0.68, 0.60)
LEATHER = (0.16, 0.06, 0.05)
WOOD = (0.28, 0.14, 0.06)
GOLD = (0.75, 0.52, 0.12)
BRASS = (0.45, 0.30, 0.08)
RED = (0.70, 0.04, 0.05)
CORAL = (0.90, 0.22, 0.28)   # the player's suit
PINK = (0.95, 0.10, 0.60)
MAGENTA = (0.85, 0.05, 0.75)
CYAN = (0.05, 0.85, 0.95)
TEAL = (0.02, 0.45, 0.50)
GREEN = (0.15, 0.95, 0.35)
LIME = (0.55, 0.95, 0.15)
ORANGE = (1.00, 0.40, 0.05)
YELLOW = (1.00, 0.85, 0.15)
BLUE = (0.10, 0.30, 1.00)
VIOLET = (0.55, 0.15, 1.00)
SKY = (0.30, 0.65, 1.00)

# Emissive neon materials: (base, roughness, metallic, emission, strength).
def neon(rgb, strength=4.0, base=None):
    """A glowing material; the base colour defaults to a dim version of rgb."""
    if base is None:
        base = tuple(c * 0.25 for c in rgb)
    return (base, 0.4, 0.0, rgb, strength)


NEON_PINK = neon(PINK)
NEON_MAGENTA = neon(MAGENTA)
NEON_CYAN = neon(CYAN)
NEON_GREEN = neon(GREEN)
NEON_ORANGE = neon(ORANGE)
NEON_YELLOW = neon(YELLOW)
NEON_BLUE = neon(BLUE)
NEON_VIOLET = neon(VIOLET)
NEON_WHITE = neon(WHITE, 3.0)
NEON_RED = neon(RED, 5.0)
SCREEN_CYAN = neon((0.20, 0.90, 0.95), 2.0, (0.02, 0.10, 0.12))

# Metals: (base, roughness, metallic).
METAL_DARK = (GUNMETAL, 0.45, 0.8)
METAL_STEEL = (STEEL, 0.35, 0.9)
METAL_CHROME = (CHROME, 0.20, 1.0)
METAL_GOLD = (GOLD, 0.30, 1.0)
METAL_BRASS = (BRASS, 0.40, 0.9)
PLASTIC_DARK = (SLATE, 0.6, 0.0)
PLASTIC_BLACK = (DARK, 0.5, 0.0)
GLASS = (WHITE, 0.05, 0.0)

_MATS = {}


def anim(spec, kind):
    """An emissive material named `anim_<kind>` that the game swaps for an
    animated shader at load time on any model (ModelUtil.animate_materials):
    "screen" (rolling scanlines, static, glitches) or "marquee" (chasing,
    twinkling dots). Never baked; a non-emissive spec glows in its own colour.
    """
    if isinstance(spec, tuple) and len(spec) and isinstance(spec[0], tuple):
        base = spec[0]
        emit = spec[3] if len(spec) > 3 else None
        strength = spec[4] if len(spec) > 4 else 1.5
    else:
        base, emit, strength = tuple(spec), None, 1.5
    return pbr("screen", base, emit=emit or base, strength=strength, name="anim_" + kind)


def mat(spec, rough=0.6, metal=0.0, emit=None, strength=3.0, name=None):
    """Return a cached material for a legacy colour spec.

    `spec` may be an (r, g, b) base colour, a tuple
    (base, roughness, metallic[, emission, strength]) such as NEON_CYAN, or a
    material already built with `pbr()`. Plain specs are routed to the closest
    physically based preset, so every old script gets real surfaces:
    emissive -> neon, very glossy white -> glass, glossy metal -> chrome,
    dark metal -> painted metal with worn edges, other metal -> brushed metal,
    very rough -> fabric, everything else -> plastic.
    """
    if isinstance(spec, bpy.types.Material):
        return spec
    if isinstance(spec, tuple) and len(spec) and isinstance(spec[0], tuple):
        base = spec[0]
        rough = spec[1] if len(spec) > 1 else rough
        metal = spec[2] if len(spec) > 2 else metal
        emit = spec[3] if len(spec) > 3 else None
        strength = spec[4] if len(spec) > 4 else strength
    else:
        base = tuple(spec)
    if emit:
        return pbr("neon", base, emit=emit, strength=strength, name=name)
    lum = 0.2126 * base[0] + 0.7152 * base[1] + 0.0722 * base[2]
    if metal < 0.3 and rough <= 0.08 and lum > 0.5:
        kind = "glass"
    elif metal >= 0.9 and rough <= 0.25:
        kind = "gold" if base[0] > base[2] * 2.5 else "chrome"
    elif metal >= 0.5:
        kind = "paint" if lum < 0.12 else "metal"
    elif rough >= 0.85:
        kind = "fabric"
    else:
        kind = "plastic"
    return pbr(kind, base, rough=rough, metal=metal if kind in ("metal", "chrome", "gold") else None, name=name)


# ------------------------------------------------------ physically based --
# pbr(kind, colour) builds a Cycles node tree with real surface detail:
# rounded edges (Bevel node), wear on the edges, grime in the crevices
# (Ambient Occlusion node), colour and roughness breakup from noise, scratches
# and small bumps. None of that survives a glTF export as nodes, so export()
# bakes every such material into three texture maps (see bake_textures).
# Emissive ("neon", "screen") and "glass" materials are not baked: they stay
# flat and keep their emission or transparency.
KINDS = {
    #            rough  metal  wear  grime  bump   edge
    "paint":    (0.42, 0.0, 0.65, 0.55, 0.25, 0.010),
    "metal":    (0.34, 1.0, 0.0, 0.40, 0.15, 0.008),
    "chrome":   (0.08, 1.0, 0.0, 0.18, 0.04, 0.006),
    "gold":     (0.24, 1.0, 0.0, 0.30, 0.08, 0.006),
    "plastic":  (0.38, 0.0, 0.25, 0.35, 0.12, 0.008),
    "rubber":   (0.85, 0.0, 0.0, 0.45, 0.35, 0.010),
    "fabric":   (0.95, 0.0, 0.0, 0.35, 0.60, 0.020),
    "leather":  (0.52, 0.0, 0.3, 0.40, 0.45, 0.015),
    "wood":     (0.45, 0.0, 0.3, 0.35, 0.25, 0.006),
    "ceramic":  (0.10, 0.0, 0.0, 0.20, 0.02, 0.010),
    "marble":   (0.18, 0.0, 0.0, 0.15, 0.02, 0.006),
    "concrete": (0.90, 0.0, 0.2, 0.75, 0.70, 0.006),
    "carpet":   (1.00, 0.0, 0.0, 0.35, 0.90, 0.004),
    "skin":     (0.45, 0.0, 0.0, 0.20, 0.10, 0.010),
}
BARE_METAL = (0.55, 0.56, 0.58)


def _node(nt, kind, loc=(0, 0), **props):
    n = nt.nodes.new(kind)
    n.location = loc
    for k, v in props.items():
        setattr(n, k, v)
    return n


def _math(nt, op, a, b=None, clamp=False):
    n = _node(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
    _feed(nt, n.inputs[0], a)
    if b is not None:
        _feed(nt, n.inputs[1], b)
    return n.outputs[0]


def _feed(nt, socket, value):
    if isinstance(value, bpy.types.NodeSocket):
        nt.links.new(value, socket)
    else:
        socket.default_value = value


def _mix_rgb(nt, blend, fac, a, b):
    n = _node(nt, "ShaderNodeMix", data_type="RGBA", blend_type=blend, clamp_result=True)
    _feed(nt, n.inputs["Factor"], fac)
    _feed(nt, n.inputs[6], a)
    _feed(nt, n.inputs[7], b)
    return n.outputs[2]


def _noise(nt, vec, scale, detail=4.0, rough=0.55, stretch=None):
    n = _node(nt, "ShaderNodeTexNoise")
    n.inputs["Scale"].default_value = scale
    n.inputs["Detail"].default_value = detail
    n.inputs["Roughness"].default_value = rough
    if stretch is not None:
        m = _node(nt, "ShaderNodeMapping")
        m.inputs["Scale"].default_value = stretch
        nt.links.new(vec, m.inputs["Vector"])
        vec = m.outputs[0]
    nt.links.new(vec, n.inputs["Vector"])
    return n.outputs["Fac"]


def _ramp(nt, value, lo, hi):
    """Map range: value in [lo, hi] -> [0, 1], clamped."""
    n = _node(nt, "ShaderNodeMapRange", clamp=True)
    _feed(nt, n.inputs["Value"], value)
    n.inputs["From Min"].default_value = lo
    n.inputs["From Max"].default_value = hi
    return n.outputs["Result"]


def pbr(kind, color=(0.5, 0.5, 0.5), rough=None, metal=None, name=None, wear=None, grime=None,
        bump=None, edge=None, scale=1.0, color2=None, emit=None, strength=4.0, alpha=0.3):
    """A physically based material. `kind` is one of KINDS, or "neon",
    "screen" (emissive, not baked) or "glass" (transparent, not baked).
    `color2` is a secondary tone (wood grain, marble veins, fabric weave).
    `scale` multiplies the size of the noise features (bigger = coarser).
    """
    key = ("pbr", kind, tuple(round(c, 4) for c in color), rough, metal, name, wear, grime, bump, edge,
           scale, tuple(color2) if color2 else None, tuple(emit) if emit else None, strength, alpha)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name or "%s%02d" % (kind, len(_MATS)))
    m.use_nodes = True
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    _MATS[key] = m
    if kind in ("neon", "screen"):
        m["bake"] = False
        e = emit or color
        base = color if emit else tuple(c * 0.25 for c in e)
        bsdf.inputs["Base Color"].default_value = (*base, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.35 if rough is None else rough
        bsdf.inputs["Emission Color"].default_value = (*e, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
        return m
    if kind == "glass":
        m["bake"] = False
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = 0.05 if rough is None else rough
        bsdf.inputs["Alpha"].default_value = alpha
        m.blend_method = "BLEND"
        m.shadow_method = "NONE"
        return m
    d_rough, d_metal, d_wear, d_grime, d_bump, d_edge = KINDS[kind]
    rough = d_rough if rough is None else rough
    metal = d_metal if metal is None else metal
    wear = d_wear if wear is None else wear
    grime = d_grime if grime is None else grime
    bump = d_bump if bump is None else bump
    edge = d_edge if edge is None else edge
    m["bake"] = True
    bsdf.inputs["Emission Strength"].default_value = 0.0

    co = _node(nt, "ShaderNodeTexCoord").outputs["Object"]
    if scale != 1.0:
        sc = _node(nt, "ShaderNodeVectorMath", operation="SCALE")
        nt.links.new(co, sc.inputs[0])
        sc.inputs["Scale"].default_value = 1.0 / scale
        co = sc.outputs["Vector"]
    big = _noise(nt, co, 2.2, 6.0, 0.6)
    fine = _noise(nt, co, 38.0, 3.0, 0.5)

    # Rounded edges and the edge mask they give for free.
    bev = _node(nt, "ShaderNodeBevel", samples=8)
    bev.inputs["Radius"].default_value = edge
    geo = _node(nt, "ShaderNodeNewGeometry")
    dot = _node(nt, "ShaderNodeVectorMath", operation="DOT_PRODUCT")
    nt.links.new(bev.outputs[0], dot.inputs[0])
    nt.links.new(geo.outputs["Normal"], dot.inputs[1])
    edge_mask = _ramp(nt, _math(nt, "SUBTRACT", 1.0, dot.outputs["Value"]), 0.004, 0.06)

    ao = _node(nt, "ShaderNodeAmbientOcclusion", samples=12)
    ao.inputs["Distance"].default_value = 0.2
    cavity = _math(nt, "SUBTRACT", 1.0, ao.outputs["AO"])   # 1 in crevices

    col = tuple(color)
    base = _mix_rgb(nt, "MULTIPLY", 0.35 * grime, (*col, 1.0), _mix_rgb(nt, "MIX", big, (0.72, 0.72, 0.72, 1), (1.08, 1.08, 1.08, 1)))
    height = fine
    if kind == "wood":
        wave = _node(nt, "ShaderNodeTexWave", wave_type="BANDS", bands_direction="X")
        wave.inputs["Scale"].default_value = 3.0
        wave.inputs["Distortion"].default_value = 6.0
        wave.inputs["Detail"].default_value = 3.0
        st = _node(nt, "ShaderNodeMapping")
        st.inputs["Scale"].default_value = (1.0, 8.0, 1.0)
        nt.links.new(co, st.inputs["Vector"])
        nt.links.new(st.outputs[0], wave.inputs["Vector"])
        c2 = color2 or tuple(c * 0.55 for c in col)
        base = _mix_rgb(nt, "MIX", wave.outputs["Fac"], base, (*c2, 1.0))
        height = wave.outputs["Fac"]
    elif kind == "marble":
        wave = _node(nt, "ShaderNodeTexWave", wave_type="BANDS", bands_direction="DIAGONAL")
        wave.inputs["Scale"].default_value = 1.6
        wave.inputs["Distortion"].default_value = 14.0
        wave.inputs["Detail"].default_value = 6.0
        nt.links.new(co, wave.inputs["Vector"])
        veins = _ramp(nt, wave.outputs["Fac"], 0.85, 1.0)
        c2 = color2 or (0.35, 0.33, 0.32)
        base = _mix_rgb(nt, "MIX", veins, base, (*c2, 1.0))
    elif kind in ("fabric", "carpet"):
        weave = _noise(nt, co, 180.0 if kind == "fabric" else 260.0, 2.0, 0.4)
        height = weave
        if color2:
            base = _mix_rgb(nt, "MIX", _ramp(nt, big, 0.45, 0.6), base, (*color2, 1.0))
    elif kind == "leather":
        vor = _node(nt, "ShaderNodeTexVoronoi", feature="DISTANCE_TO_EDGE")
        vor.inputs["Scale"].default_value = 60.0
        nt.links.new(co, vor.inputs["Vector"])
        height = vor.outputs["Distance"]
    elif kind == "concrete":
        height = _noise(nt, co, 14.0, 8.0, 0.7)
    elif kind == "metal":
        height = _noise(nt, co, 6.0, 2.0, 0.5, stretch=(1.0, 1.0, 60.0))   # brushed streaks
    # Grime gathers in crevices.
    base = _mix_rgb(nt, "MULTIPLY", _math(nt, "MULTIPLY", cavity, 0.8 * grime), base, (0.25, 0.22, 0.24, 1))

    # Scratches: thin stretched noise lines.
    scratch = _ramp(nt, _noise(nt, co, 9.0, 1.0, 0.3, stretch=(1.0, 40.0, 1.0)), 0.62, 0.66)
    r = _math(nt, "ADD", rough, _math(nt, "MULTIPLY", _math(nt, "SUBTRACT", big, 0.5), 0.3 * grime + 0.05))
    r = _math(nt, "ADD", r, _math(nt, "MULTIPLY", cavity, 0.25 * grime))
    r = _math(nt, "ADD", r, _math(nt, "MULTIPLY", scratch, 0.18 if metal > 0.5 else 0.08))
    met = metal
    if wear > 0.0:
        worn = _math(nt, "MULTIPLY", edge_mask, _ramp(nt, big, 0.25, 0.75))
        worn = _ramp(nt, _math(nt, "MULTIPLY", worn, 2.0 * wear), 0.35, 0.55)
        if kind == "paint":
            base = _mix_rgb(nt, "MIX", worn, base, (*BARE_METAL, 1.0))
            r = _mix_rgb(nt, "MIX", worn, r, (0.3, 0.3, 0.3, 1.0))
            met = _math(nt, "MAXIMUM", metal, worn)
        else:
            base = _mix_rgb(nt, "MIX", _math(nt, "MULTIPLY", worn, 0.25), base, (1.0, 1.0, 1.0, 1.0))
    rc = _math(nt, "MAXIMUM", _math(nt, "MINIMUM", r, 1.0), 0.02) if isinstance(r, bpy.types.NodeSocket) and r.node.type == "MATH" else r
    if not isinstance(rc, bpy.types.NodeSocket) or rc.type != "VALUE":
        conv = _node(nt, "ShaderNodeRGBToBW")
        nt.links.new(rc, conv.inputs[0])
        rc = conv.outputs[0]
    nt.links.new(base, bsdf.inputs["Base Color"])
    nt.links.new(rc, bsdf.inputs["Roughness"])
    _feed(nt, bsdf.inputs["Metallic"], met)
    bmp = _node(nt, "ShaderNodeBump")
    bmp.inputs["Strength"].default_value = min(1.0, 0.35 * bump)
    bmp.inputs["Distance"].default_value = 0.01
    nt.links.new(height, bmp.inputs["Height"])
    nt.links.new(bev.outputs[0], bmp.inputs["Normal"])
    nt.links.new(bmp.outputs[0], bsdf.inputs["Normal"])
    return m


# --------------------------------------------------------------- animation --
FPS = 30


def key(obj, clip, path, keys, index=-1, interp="BEZIER"):
    """Keyframe `obj.<path>` for animation `clip`.

    `keys` is a list of (frame, value) with frames at 30 fps; value is a
    number (with `index`) or a tuple for vector properties. Every object's
    keys for the same clip are exported as one glTF animation of that name
    (one NLA track per object, merged by name). In Godot, a clip called
    "idle" loops and auto-plays on every instance (see Game autoload);
    others are played by the game's scripts through the model's
    AnimationPlayer.
    """
    ad = obj.animation_data or obj.animation_data_create()
    act_name = "%s|%s" % (obj.name, clip)
    act = bpy.data.actions.get(act_name) or bpy.data.actions.new(act_name)
    for frame, value in keys:
        vals = value if isinstance(value, (tuple, list)) else [value]
        idxs = range(len(vals)) if index < 0 else [index]
        for i, v in zip(idxs, vals):
            fc = act.fcurves.find(path, index=i) or act.fcurves.new(path, index=i)
            kp = fc.keyframe_points.insert(frame, v, options={"FAST"})
            kp.interpolation = interp
    for fc in act.fcurves:
        fc.update()
    track = next((t for t in ad.nla_tracks if t.name == clip), None)
    if track is None:
        track = ad.nla_tracks.new()
        track.name = clip
        track.strips.new(clip, 0, act)
    else:
        track.strips[0].action_frame_end = max(track.strips[0].action_frame_end, act.frame_range[1])
    ad.action = None
    return act


def spin(obj, clip, axis="Z", seconds=2.0, turns=1.0):
    """A constant-speed loop rotation (rotor, fan, wheel) about a local axis."""
    i = "XYZ".index(axis)
    r0 = obj.rotation_euler[i]
    end = seconds * FPS
    # Key every quarter turn: glTF stores rotations as quaternions, and 0 and
    # 360 degrees are the same quaternion, so two keys would not move at all.
    steps = max(4, int(round(abs(turns) * 4)))
    keys = [(end * k / steps, r0 + turns * 2 * math.pi * k / steps) for k in range(steps + 1)]
    key(obj, clip, "rotation_euler", keys, index=i, interp="LINEAR")


def wobble(obj, clip, path, index, amp, seconds=2.0, phase=0.0, base=None):
    """A seamless sine loop on one channel: base + amp * sin(2pi t/T + phase)."""
    v0 = getattr(obj, path)[index] if base is None else base
    end = int(round(seconds * FPS))
    steps = 8
    keys = [(end * s / steps, v0 + amp * math.sin(2 * math.pi * s / steps + phase)) for s in range(steps + 1)]
    key(obj, clip, path, keys, index=index)


# ------------------------------------------------------------ scene setup --
def clean_scene():
    """Wipe the default scene so a script always starts from nothing."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete(use_global=False)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras, bpy.data.lights):
        for item in list(block):
            if item.users == 0:
                block.remove(item)
    _MATS.clear()


def _link(o):
    bpy.context.collection.objects.link(o)
    return o


def _finish(o, m, bevel, smooth, name, parent, smooth_angle=40.0):
    if name:
        o.name = name
    if bevel and bevel > 0:
        b = o.modifiers.new("bevel", "BEVEL")
        b.width = bevel
        b.segments = 2
        b.limit_method = "ANGLE"
    if smooth:
        for p in o.data.polygons:
            p.use_smooth = True
        o.data.use_auto_smooth = True
        o.data.auto_smooth_angle = math.radians(smooth_angle)
    o.data.materials.clear()
    o.data.materials.append(mat(m))
    if parent is not None:
        attach(o, parent)
    return o


def cube(size, loc, m, rot=(0, 0, 0), bevel=0.02, smooth=False, name=None, parent=None):
    """An axis-aligned box of full size `size` centred at `loc`."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = size
    return _finish(o, m, bevel, smooth, name, parent)


def slab(size, loc, m, **kw):
    """A cube whose `loc` is its bottom centre (handy for floor-standing parts)."""
    x, y, z = loc
    return cube(size, (x, y, z + size[2] / 2.0), m, **kw)


def cyl(r, depth, loc, m, rot=(0, 0, 0), r2=None, verts=16, bevel=0.01, smooth=True, name=None, parent=None):
    """A cylinder (axis Z before rotation) or, with r2, a truncated cone."""
    if r2 is None:
        bpy.ops.mesh.primitive_cylinder_add(vertices=verts, radius=r, depth=depth, location=loc, rotation=rot)
    else:
        bpy.ops.mesh.primitive_cone_add(vertices=verts, radius1=r, radius2=r2, depth=depth, location=loc, rotation=rot)
    o = bpy.context.object
    return _finish(o, m, bevel, smooth, name, parent)


def cone(r, depth, loc, m, **kw):
    return cyl(r, depth, loc, m, r2=0.0, **kw)


def sphere(r, loc, m, scale=(1, 1, 1), segments=16, rings=10, smooth=True, name=None, parent=None):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=segments, ring_count=rings, radius=r, location=loc)
    o = bpy.context.object
    o.scale = scale
    return _finish(o, m, 0, smooth, name, parent, smooth_angle=80.0)


def ico(r, loc, m, subdiv=1, smooth=False, name=None, parent=None):
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=subdiv, radius=r, location=loc)
    o = bpy.context.object
    return _finish(o, m, 0, smooth, name, parent)


def torus(major, minor, loc, m, rot=(0, 0, 0), scale=(1, 1, 1), major_segments=24, minor_segments=8, smooth=True, name=None, parent=None):
    bpy.ops.mesh.primitive_torus_add(major_radius=major, minor_radius=minor, location=loc, rotation=rot,
                                     major_segments=major_segments, minor_segments=minor_segments)
    o = bpy.context.object
    o.scale = scale
    return _finish(o, m, 0, smooth, name, parent, smooth_angle=80.0)


def plane(size, loc, m, rot=(0, 0, 0), name=None, parent=None):
    """A single quad of size (w, h) lying in the XY plane before rotation."""
    bpy.ops.mesh.primitive_plane_add(size=1.0, location=loc, rotation=rot)
    o = bpy.context.object
    o.scale = (size[0], size[1], 1.0)
    return _finish(o, m, 0, False, name, parent)


def wall_panel(size, loc, m, name=None, parent=None):
    """A quad standing upright, facing -Y (the camera), of size (w, h)."""
    return plane(size, loc, m, rot=(math.pi / 2, 0, 0), name=name, parent=parent)


def rod(p0, p1, r, m, r2=None, verts=12, bevel=0.0, smooth=True, name=None, parent=None):
    """A cylinder running from p0 to p1; rotation derived from the direction."""
    a, b = mathutils.Vector(p0), mathutils.Vector(p1)
    v = b - a
    o = cyl(r, v.length, tuple((a + b) / 2.0), m, r2=r2, verts=verts, bevel=bevel, smooth=smooth, name=name, parent=parent)
    o.rotation_euler = v.to_track_quat("Z", "Y").to_euler()
    return o


def wedge(size, loc, m, name=None, parent=None):
    """A right-triangle prism: full box `size`, with the +Y/+Z edge cut away
    so the sloped face looks up and towards -Y."""
    o = cube(size, loc, m, bevel=0, name=name, parent=parent)
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    x, y, z = loc
    sx, sy, sz = size
    bpy.ops.mesh.bisect(plane_co=(x, y, z), plane_no=(0, sz, sy), clear_outer=True, use_fill=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    return o


def pivot(name, loc=(0, 0, 0), parent=None):
    """An Empty; exported as a named Node3D the game can rotate."""
    e = bpy.data.objects.new(name, None)
    e.empty_display_size = 0.1
    e.location = loc
    _link(e)
    if parent is not None:
        attach(e, parent)
    return e


def attach(child, parent):
    """Parent `child` to `parent` keeping its world transform."""
    child.parent = parent
    child.matrix_parent_inverse = parent.matrix_world.inverted()
    return child


def join(objs, name):
    """Merge several meshes into one object (fewer draw calls for static props)."""
    objs = [o for o in objs if o.type == "MESH"]
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    # Bake each object's own modifiers (bevels) before merging; a join keeps
    # only the active object's modifier stack.
    bpy.ops.object.convert(target="MESH")
    bpy.ops.object.join()
    o = bpy.context.object
    o.name = name
    return o


def join_static(name="body", keep=()):
    """Join every top-level mesh that is not a named part into one object.

    Meshes parented under a pivot, or whose name is listed in `keep`, stay
    separate so the game can still animate or recolour them. Everything else
    becomes one multi-material mesh: one MeshInstance3D in Godot instead of
    dozens, which matters on phones.
    """
    keep = set(keep)
    static = [o for o in all_meshes() if o.parent is None and o.name not in keep and not o.name.startswith("_")]
    if len(static) < 2:
        return static[0] if static else None
    return join(static, name)


def mirror_copy(o, axis="X", name=None):
    """Duplicate `o` mirrored across the given world axis through the origin."""
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.duplicate()
    c = bpy.context.object
    idx = "XYZ".index(axis)
    s = list(c.scale)
    s[idx] = -s[idx]
    c.scale = s
    loc = list(c.location)
    loc[idx] = -loc[idx]
    c.location = loc
    if name:
        c.name = name
    return c


def all_meshes():
    return [o for o in bpy.context.scene.objects if o.type == "MESH"]


def scene_bounds():
    lo = mathutils.Vector((1e9, 1e9, 1e9))
    hi = mathutils.Vector((-1e9, -1e9, -1e9))
    for o in all_meshes():
        for corner in o.bound_box:
            w = o.matrix_world @ mathutils.Vector(corner)
            lo = mathutils.Vector((min(lo.x, w.x), min(lo.y, w.y), min(lo.z, w.z)))
            hi = mathutils.Vector((max(hi.x, w.x), max(hi.y, w.y), max(hi.z, w.z)))
    return lo, hi


# ------------------------------------------------------- export & preview --
def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    here = os.path.dirname(os.path.abspath(__file__))
    root = os.path.dirname(here)
    out = os.path.join(root, "assets", "models")
    preview = None
    i = 0
    while i < len(argv):
        if argv[i] == "--out":
            out = argv[i + 1]
            i += 2
        elif argv[i] == "--preview":
            preview = argv[i + 1]
            i += 2
        else:
            i += 1
    return out, preview


def export(name, out_dir=None, preview_dir=None, tex=None, ground=None, bake=True, ao_distance=None):
    """Bake the procedural materials, then export the scene as `<name>.glb`
    (with its animation clips) and optionally render a preview.

    `tex` is the atlas size in pixels (default from the model's size), `ground`
    adds a floor under the model while baking so its base gets contact
    shadows (default: when the model stands on z=0), `ao_distance` is how far
    ambient occlusion reaches (default scales with the model).
    """
    default_out, default_preview = parse_args()
    out_dir = out_dir or default_out
    preview_dir = preview_dir or default_preview
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".glb")
    if bake and os.environ.get("NO_BAKE") != "1":
        bake_textures(name, tex=tex, ground=ground, ao_distance=ao_distance)
    bpy.ops.object.select_all(action="DESELECT")
    animated = any(o.animation_data and o.animation_data.nla_tracks for o in bpy.context.scene.objects)
    bpy.context.scene.render.fps = FPS
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_animations=animated,
        export_animation_mode="NLA_TRACKS",
        export_force_sampling=False,
        export_optimize_animation_size=True,
        export_skins=True,
        export_def_bones=True,
        export_lights=False,
        export_cameras=False,
        export_materials="EXPORT",
        export_image_format="JPEG",
        export_normals=True,
        export_texcoords=True,
    )
    tris = sum(len(o.data.polygons) for o in all_meshes())
    clips = sorted({t.name for o in bpy.context.scene.objects if o.animation_data for t in o.animation_data.nla_tracks})
    print("EXPORTED %s (%d faces, %d bytes, clips=%s)" % (path, tris, os.path.getsize(path), ",".join(clips) or "-"))
    if preview_dir:
        render_preview(name, preview_dir)


# ------------------------------------------------------------------ baking --
def _bakeable(m):
    return m is not None and m.use_nodes and bool(m.get("bake", False))


def _principled(m):
    for n in m.node_tree.nodes:
        if n.type == "BSDF_PRINCIPLED":
            return n
    return None


def _output(m):
    for n in m.node_tree.nodes:
        if n.type == "OUTPUT_MATERIAL" and n.is_active_output:
            return n
    return None


def _source(nt, socket):
    """The socket feeding `socket`, or a constant node carrying its value."""
    if socket.is_linked:
        return socket.links[0].from_socket
    if socket.type == "RGBA":
        n = nt.nodes.new("ShaderNodeRGB")
        n.outputs[0].default_value = tuple(socket.default_value)
        n["_tmp"] = True
        return n.outputs[0]
    n = nt.nodes.new("ShaderNodeValue")
    n.outputs[0].default_value = socket.default_value
    n["_tmp"] = True
    return n.outputs[0]


def _default_tex(lo, hi):
    size = max((hi - lo).x, (hi - lo).y, (hi - lo).z)
    if size < 0.5:
        return 256
    if size < 2.2:
        return 512
    if size < 7.0:
        return 1024
    return 2048


def bake_textures(name, tex=None, ground=None, ao_distance=None):
    """Bake every material flagged `bake` into one texture atlas per model:
    <name>_albedo (sRGB colour with crevice grime), <name>_orm (R = ambient
    occlusion, G = roughness, B = metallic, the glTF layout) and
    <name>_normal (tangent space: rounded edges, bumps, grain). The baked
    material replaces them all; neon/glass materials are left as they are.
    """
    scn = bpy.context.scene
    meshes = [o for o in all_meshes() if any(_bakeable(s.material) for s in o.material_slots)]
    if not meshes:
        return
    lo, hi = scene_bounds()
    size = tex or int(os.environ.get("BAKE_TEX", 0)) or _default_tex(lo, hi)
    extent = max((hi - lo).x, (hi - lo).y, (hi - lo).z)
    ao_dist = ao_distance or max(0.05, min(0.6, extent * 0.12))
    if ground is None:
        ground = abs(lo.z) < 0.05 and extent > 0.3

    # 1. Real geometry: apply modifiers so the bevels get their own UVs.
    # Armature modifiers stay: applying one would freeze a character's pose.
    for o in meshes:
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        for md in list(o.modifiers):
            if md.type != "ARMATURE":
                bpy.ops.object.modifier_apply(modifier=md.name)
    for o in meshes:
        o.data.materials  # noqa
        if o.matrix_world.determinant() < 0 and not o.children and not o.animation_data:
            bpy.ops.object.select_all(action="DESELECT")
            o.select_set(True)
            bpy.context.view_layer.objects.active = o
            bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)

    # 2. One shared UV atlas over all bakeable faces of all objects.
    for o in meshes:
        me = o.data
        while me.uv_layers:
            me.uv_layers.remove(me.uv_layers[0])
        me.uv_layers.new(name="UVMap")
        flags = [_bakeable(o.material_slots[p.material_index].material) if o.material_slots else False for p in me.polygons]
        for p, f in zip(me.polygons, flags):
            p.select = f
    bpy.ops.object.select_all(action="DESELECT")
    for o in meshes:
        o.select_set(True)
    bpy.context.view_layer.objects.active = meshes[0]
    bpy.ops.object.mode_set(mode="EDIT")
    scn.tool_settings.use_uv_select_sync = True
    bpy.ops.uv.smart_project(angle_limit=math.radians(60), island_margin=0.0, area_weight=0.0, correct_aspect=True, scale_to_bounds=False)
    bpy.ops.uv.average_islands_scale()
    bpy.ops.uv.pack_islands(rotate=True, margin=2.5 / size * 4)
    bpy.ops.object.mode_set(mode="OBJECT")

    # 3. Target images.
    def image(suffix, colour):
        img = bpy.data.images.new("%s_%s" % (name, suffix), size, size, alpha=False)
        img.colorspace_settings.name = "sRGB" if colour else "Non-Color"
        return img
    albedo, orm, normal = image("albedo", True), image("orm", False), image("normal", False)

    # 4. Per material: sources for the three passes and a target image node.
    mats = {s.material for o in meshes for s in o.material_slots if _bakeable(s.material)}
    info = {}
    for m in mats:
        nt = m.node_tree
        bsdf = _principled(m)
        out = _output(m)
        img_node = nt.nodes.new("ShaderNodeTexImage")
        img_node["_tmp"] = True
        nt.nodes.active = img_node
        emis = nt.nodes.new("ShaderNodeEmission")
        emis["_tmp"] = True
        ao = nt.nodes.new("ShaderNodeAmbientOcclusion")
        ao["_tmp"] = True
        ao.samples = 16
        ao.inputs["Distance"].default_value = ao_dist
        comb = nt.nodes.new("ShaderNodeCombineColor")
        comb["_tmp"] = True
        nt.links.new(ao.outputs["AO"], comb.inputs[0])
        nt.links.new(_source(nt, bsdf.inputs["Roughness"]), comb.inputs[1])
        nt.links.new(_source(nt, bsdf.inputs["Metallic"]), comb.inputs[2])
        info[m] = dict(nt=nt, bsdf=bsdf, out=out, img=img_node, emis=emis, comb=comb,
                       base=_source(nt, bsdf.inputs["Base Color"]), surface=out.inputs["Surface"].links[0].from_socket)

    floor = None
    if ground:
        bpy.ops.mesh.primitive_plane_add(size=max(4.0, extent * 4), location=((lo.x + hi.x) / 2, (lo.y + hi.y) / 2, lo.z))
        floor = bpy.context.object
        floor.name = "_bake_floor"

    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    # Without OpenImageDenoise in this Blender build, a denoise request makes
    # Cycles abort the bake silently and leave every map empty.
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
    if floor is not None:
        bpy.data.objects.remove(floor, do_unlink=True)
    dump = os.environ.get("BAKE_DUMP")
    for img in (albedo, orm, normal):
        if dump:
            os.makedirs(dump, exist_ok=True)
            img.filepath_raw = os.path.join(dump, img.name + ".png")
            img.file_format = "PNG"
            img.save()
        img.pack()

    # 5. One baked material replaces every bakeable one.
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
        # Merge the slots that now share the baked material.
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        _merge_slots(o)
    print("BAKED %s %dpx ao=%.2fm objects=%d" % (name, size, ao_dist, len(meshes)))


def _merge_slots(o):
    """Collapse duplicate material slots so each material is one surface."""
    me = o.data
    first = {}
    remap = []
    for i, s in enumerate(o.material_slots):
        m = s.material
        if m not in first:
            first[m] = len(first)
        remap.append(first[m])
    if len(first) == len(o.material_slots):
        return
    idx = [0] * len(me.polygons)
    me.polygons.foreach_get("material_index", idx)
    idx = [remap[i] if i < len(remap) else 0 for i in idx]
    order = list(first.keys())
    me.materials.clear()
    for m in order:
        me.materials.append(m)
    me.polygons.foreach_set("material_index", idx)
    me.update()


def render_preview(name, preview_dir, size=384, samples=40):
    """Frame the scene from the front-right, three neon-ish lights, Cycles CPU."""
    os.makedirs(preview_dir, exist_ok=True)
    lo, hi = scene_bounds()
    centre = (lo + hi) / 2.0
    radius = max((hi - lo).length / 2.0, 0.3)
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    scn.cycles.use_denoising = False   # this Blender build has no OpenImageDenoise
    scn.render.resolution_x = size
    scn.render.resolution_y = size
    scn.render.film_transparent = False
    cam_data = bpy.data.cameras.new("preview_cam")
    cam_data.lens = 45
    cam = _link(bpy.data.objects.new("preview_cam", cam_data))
    direction = mathutils.Vector((0.75, -1.0, 0.55)).normalized()
    cam.location = centre + direction * radius * 2.6
    cam.rotation_euler = (centre - cam.location).to_track_quat("-Z", "Y").to_euler()
    scn.camera = cam
    for (pos, colour, energy) in (
        ((1.0, -1.2, 1.4), (1.0, 0.9, 0.95), 900),
        ((-1.4, -0.6, 0.8), (0.55, 0.85, 1.0), 400),
        ((0.3, 1.2, 1.0), (1.0, 0.45, 0.9), 300),
    ):
        ld = bpy.data.lights.new("preview_light", "POINT")
        ld.energy = energy * radius * radius
        ld.color = colour
        ld.shadow_soft_size = radius * 0.4
        lo_ = _link(bpy.data.objects.new("preview_light", ld))
        lo_.location = centre + mathutils.Vector(pos) * radius * 2.2
    scn.world = scn.world or bpy.data.worlds.new("w")
    scn.world.use_nodes = True
    scn.world.node_tree.nodes["Background"].inputs[0].default_value = (0.03, 0.015, 0.045, 1.0)
    scn.render.filepath = os.path.join(preview_dir, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("PREVIEW %s" % scn.render.filepath)
