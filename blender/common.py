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
    """A copy of `spec` named `anim_<kind>`: the game swaps every material
    whose name starts with that prefix for an animated shader at load time
    (see Backdrop._animate_materials). Kinds: screen, marquee."""
    return mat(spec, name="anim_" + kind)


def mat(spec, rough=0.6, metal=0.0, emit=None, strength=3.0, name=None):
    """Return a cached Principled material.

    `spec` may be an (r, g, b) base colour or a tuple
    (base, roughness, metallic[, emission, strength]) such as NEON_CYAN.
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
    key = (tuple(base), round(rough, 3), round(metal, 3), tuple(emit) if emit else None, round(strength, 3), name)
    if key in _MATS:
        return _MATS[key]
    m = bpy.data.materials.new(name or "m%02d" % len(_MATS))
    m.use_nodes = True
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Base Color"].default_value = (*base, 1.0)
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit:
        bsdf.inputs["Emission Color"].default_value = (*emit, 1.0)
        bsdf.inputs["Emission Strength"].default_value = strength
    else:
        bsdf.inputs["Emission Strength"].default_value = 0.0
    _MATS[key] = m
    return m


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


def export(name, out_dir=None, preview_dir=None):
    """Export the whole scene as `<name>.glb` and optionally render a preview."""
    default_out, default_preview = parse_args()
    out_dir = out_dir or default_out
    preview_dir = preview_dir or default_preview
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name + ".glb")
    bpy.ops.object.select_all(action="DESELECT")
    bpy.ops.export_scene.gltf(
        filepath=path,
        export_format="GLB",
        export_yup=True,
        export_apply=True,
        export_animations=False,
        export_skins=False,
        export_lights=False,
        export_cameras=False,
        export_materials="EXPORT",
        export_normals=True,
        export_texcoords=True,
    )
    tris = sum(len(o.data.polygons) for o in all_meshes())
    print("EXPORTED %s (%d faces, %d bytes)" % (path, tris, os.path.getsize(path)))
    if preview_dir:
        render_preview(name, preview_dir)


def render_preview(name, preview_dir, size=384, samples=24):
    """Frame the scene from the front-right, three neon-ish lights, Cycles CPU."""
    os.makedirs(preview_dir, exist_ok=True)
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
