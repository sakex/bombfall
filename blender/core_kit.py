# Helpers shared by the core gameplay objects (bomb, coin, tiles, pickups,
# pedestal, plasma bullet, boss block and heart). Built on common.py:
#
#   lathe(profile, m, ...)      revolve an (r, z) profile: machined parts
#   tube(points, r, m, ...)     a swept tube along a polyline: cables, pipes
#   smooth_path(points, n)      Catmull-Rom resample of a polyline
#   text_mesh(text, ...)        extruded text geometry (low resolution)
#   decal_image(name, w, h, fn) a PIL-drawn RGBA image loaded into Blender
#   decal_pbr(kind, col, decals, name=...)
#                               a pbr() material with image decals projected
#                               in object space: labels, stencils, stripes and
#                               embossing, all baked into the model's atlas
#   glow_glass(col, alpha, strength)  a transparent emissive shell
#   bolt(loc, axis, r, h, m)    a low-poly hex bolt head
#   tri_report(label)           prints the triangle count after modifiers
#   sheet(name, dir)            multi-angle Cycles contact sheet for review
import math
import os
import tempfile

import bpy
import bmesh
import mathutils
from mathutils import Vector

from common import *  # noqa: F401,F403
from common import _finish, _node, _feed, _link  # noqa: F401

FONT_DIRS = ("/usr/share/fonts/truetype/dejavu", "/usr/share/fonts/truetype/freefont",
             "/usr/share/fonts/truetype/liberation")
FONTS = {
    "bold": ("DejaVuSansCondensed-Bold.ttf", "FreeSansBold.ttf", "LiberationSans-Bold.ttf"),
    "wide": ("DejaVuSans-Bold.ttf", "FreeSansBold.ttf"),
    "mono": ("DejaVuSansMono-Bold.ttf", "FreeMonoBold.ttf", "LiberationMono-Bold.ttf"),
    "serif": ("DejaVuSerif-Bold.ttf", "FreeSerifBold.ttf"),
}


def font_path(kind="bold"):
    for f in FONTS.get(kind, FONTS["bold"]):
        for d in FONT_DIRS:
            p = os.path.join(d, f)
            if os.path.exists(p):
                return p
    return None


def pil_font(size, kind="bold"):
    from PIL import ImageFont
    p = font_path(kind)
    if p:
        return ImageFont.truetype(p, size)
    return ImageFont.load_default()


# ---------------------------------------------------------------- geometry --
def _mesh_object(bm, name):
    me = bpy.data.meshes.new(name or "mesh")
    bm.to_mesh(me)
    bm.free()
    o = bpy.data.objects.new(name or "mesh", me)
    _link(o)
    # attach() reads the parent's matrix_world, which is stale until the view
    # layer updates (bpy.ops calls do that implicitly; direct creation not).
    bpy.context.view_layer.update()
    return o


def _place(o, loc, rot, scale=(1, 1, 1)):
    o.location = loc
    o.rotation_euler = rot
    o.scale = scale
    return o


def lathe(profile, m, segments=24, loc=(0, 0, 0), rot=(0, 0, 0), name=None, smooth=True, angle=38.0,
          parent=None, scale=(1, 1, 1), phase=0.0):
    """Revolve an (r, z) profile about the local Z axis.

    The profile runs from the bottom (usually r = 0 on the axis) outwards,
    up the outside and back in to the top, so the normals face out. A point
    with r = 0 becomes a single pole vertex (a closed cap). Hard edges come
    from the auto-smooth `angle`.
    """
    bm = bmesh.new()
    rings = []
    for r, z in profile:
        if r < 1e-6:
            rings.append([bm.verts.new((0.0, 0.0, z))])
        else:
            rings.append([bm.verts.new((r * math.cos(phase + math.tau * i / segments),
                                        r * math.sin(phase + math.tau * i / segments), z))
                          for i in range(segments)])
    for A, B in zip(rings, rings[1:]):
        if len(A) == 1 and len(B) == 1:
            continue
        for i in range(segments):
            j = (i + 1) % segments
            if len(A) == 1:
                bm.faces.new((A[0], B[j], B[i]))
            elif len(B) == 1:
                bm.faces.new((A[i], A[j], B[0]))
            else:
                bm.faces.new((A[i], A[j], B[j], B[i]))
    o = _mesh_object(bm, name)
    _place(o, loc, rot, scale)
    return _finish(o, m, 0, smooth, name, parent, smooth_angle=angle)


def smooth_path(points, n=4, closed=False):
    """Catmull-Rom resample: n segments between every pair of points."""
    P = [Vector(p) for p in points]
    if len(P) < 3:
        return P
    out = []
    count = len(P) if closed else len(P) - 1
    for k in range(count):
        p0 = P[(k - 1) % len(P)] if closed else P[max(k - 1, 0)]
        p1 = P[k]
        p2 = P[(k + 1) % len(P)]
        p3 = P[(k + 2) % len(P)] if closed else P[min(k + 2, len(P) - 1)]
        for s in range(n):
            t = s / n
            t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    if not closed:
        out.append(P[-1])
    return out


def tube(points, radius, m, sides=8, name=None, parent=None, caps=True, closed=False, smooth=True,
         up=(0, 0, 1), twist=0.0, phase=0.0):
    """A tube swept along a polyline (parallel-transport frames).
    `radius` is a number or a per-point list (tapers)."""
    P = [Vector(p) for p in points]
    n = len(P)
    radii = list(radius) if isinstance(radius, (list, tuple)) else [radius] * n
    bm = bmesh.new()
    rings = []
    prev_n = None
    for i, p in enumerate(P):
        if closed:
            t = (P[(i + 1) % n] - P[(i - 1) % n]).normalized()
        elif i == 0:
            t = (P[1] - P[0]).normalized()
        elif i == n - 1:
            t = (P[-1] - P[-2]).normalized()
        else:
            t = (P[i + 1] - P[i - 1]).normalized()
        if prev_n is None:
            u = Vector(up)
            if abs(u.dot(t)) > 0.95:
                u = Vector((1, 0, 0)) if abs(t.x) < 0.9 else Vector((0, 1, 0))
            nn = (u - t * u.dot(t)).normalized()
        else:
            nn = (prev_n - t * prev_n.dot(t)).normalized()
        prev_n = nn
        b = t.cross(nn)
        ring = []
        for s in range(sides):
            a = math.tau * s / sides + twist * i + phase
            ring.append(bm.verts.new(p + radii[i] * (math.cos(a) * nn + math.sin(a) * b)))
        rings.append(ring)
    pairs = list(zip(rings, rings[1:]))
    if closed:
        pairs.append((rings[-1], rings[0]))
    for A, B in pairs:
        for s in range(sides):
            j = (s + 1) % sides
            bm.faces.new((A[s], A[j], B[j], B[s]))
    if caps and not closed:
        bm.faces.new(list(reversed(rings[0])))
        bm.faces.new(rings[-1])
    o = _mesh_object(bm, name)
    return _finish(o, m, 0, True, name, parent, smooth_angle=60.0 if smooth else 30.0)


def text_mesh(text, size, loc, m, rot=(math.pi / 2, 0, 0), depth=0.01, kind="bold", name=None,
              parent=None, resolution=2, align="CENTER", spacing=1.0, bevel=0.0):
    """Extruded text converted to a mesh. Default rotation faces -Y."""
    cu = bpy.data.curves.new(name or "text", "FONT")
    cu.body = text
    p = font_path(kind)
    if p:
        cu.font = bpy.data.fonts.load(p, check_existing=True)
    cu.size = size
    cu.extrude = depth
    cu.resolution_u = resolution
    cu.align_x = align
    cu.align_y = "CENTER"
    cu.space_character = spacing
    cu.bevel_depth = bevel
    o = bpy.data.objects.new(name or "text", cu)
    _link(o)
    o.location = loc
    o.rotation_euler = rot
    bpy.ops.object.select_all(action="DESELECT")
    o.select_set(True)
    bpy.context.view_layer.objects.active = o
    bpy.ops.object.convert(target="MESH")
    o = bpy.context.object
    # Limited dissolve keeps the letter outlines but drops the fan clutter.
    bm = bmesh.new()
    bm.from_mesh(o.data)
    bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=0.0005)
    bmesh.ops.dissolve_limit(bm, angle_limit=math.radians(2), verts=bm.verts, edges=bm.edges)
    bmesh.ops.triangulate(bm, faces=[f for f in bm.faces if len(f.verts) > 4])
    bm.to_mesh(o.data)
    bm.free()
    return _finish(o, m, 0, False, name, parent)


def bolt(loc, axis, r, h, m, sides=6, name=None, parent=None, spin=0.0, dome=0.0):
    """A bolt head standing on a surface, pointing along `axis`: a prism
    without a bottom (it sits on something). `dome` > 0 adds a raised centre
    (rivets, button heads)."""
    a = Vector(axis).normalized()
    q = a.to_track_quat("Z", "Y") @ mathutils.Quaternion((0, 0, 1), spin)
    bm = bmesh.new()
    lo = [bm.verts.new((r * math.cos(math.tau * i / sides), r * math.sin(math.tau * i / sides), 0.0)) for i in range(sides)]
    hi = [bm.verts.new((r * math.cos(math.tau * i / sides), r * math.sin(math.tau * i / sides), h)) for i in range(sides)]
    for i in range(sides):
        j = (i + 1) % sides
        bm.faces.new((lo[i], lo[j], hi[j], hi[i]))
    if dome > 0:
        c = bm.verts.new((0, 0, h + dome))
        for i in range(sides):
            bm.faces.new((hi[i], hi[(i + 1) % sides], c))
    else:
        bm.faces.new(hi)
    for v in bm.verts:
        v.co = q @ v.co + Vector(loc)
    o = _mesh_object(bm, name or "bolt")
    return _finish(o, m, 0, dome > 0, name, parent, smooth_angle=50.0)


def box_mesh(size, loc, m, rot=(0, 0, 0), chamfer=0.0, name=None, parent=None, segments=1, smooth=False):
    """A box with an optional real chamfer (bevel applied as geometry now, so
    the triangle count is known and adjacent tiles line up exactly)."""
    o = cube(size, loc, m, rot=rot, bevel=0.0, smooth=smooth, name=name, parent=parent)
    if chamfer > 0:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        # Scale is on the object; bevel in mesh space must be divided by it.
        s = min(size)
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=chamfer / s, segments=segments, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
        bm.to_mesh(o.data)
        bm.free()
        bpy.ops.object.select_all(action="DESELECT")
        o.select_set(True)
        bpy.context.view_layer.objects.active = o
        bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    return o


def bm_box(size, loc, m, chamfer=0.0, segments=1, name=None, parent=None, rot=(0, 0, 0), smooth_angle=None):
    """A chamfered box built directly in metres (no object scale)."""
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * size[0], v.co.y * size[1], v.co.z * size[2]))
    if chamfer > 0:
        bmesh.ops.bevel(bm, geom=list(bm.edges), offset=chamfer, segments=segments, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    o = _mesh_object(bm, name)
    _place(o, loc, rot)
    smooth = smooth_angle is not None
    return _finish(o, m, 0, smooth, name, parent, smooth_angle=smooth_angle or 40.0)


def tile_block(side, top=None, front=None, bottom=None, chamfer=0.03, size=(1.0, 2.0, 1.0), name="tile",
               drop_back=True, front_only=False):
    """The 1 x 2 x 1 m cell body (front at -Y, walkable top at +Z), with
    chamfered edges, per-face materials and no back face (never seen)."""
    sx, sy, sz = size
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * sx, v.co.y * sy, v.co.z * sz))
    if chamfer > 0:
        edges = list(bm.edges)
        if front_only:      # only the front outline: tops and sides stay continuous
            edges = [e for e in edges if all(v.co.y < -sy / 2 + 1e-4 for v in e.verts)]
        bmesh.ops.bevel(bm, geom=edges, offset=chamfer, segments=1, profile=0.5,
                        affect="EDGES", clamp_overlap=True)
    bm.normal_update()
    if drop_back:
        back = [f for f in bm.faces if f.normal.y > 0.99]
        bmesh.ops.delete(bm, geom=back, context="FACES")
    mats = [side, top or side, front or side, bottom or side]
    for f in bm.faces:
        n = f.normal
        if n.z > 0.99:
            f.material_index = 1
        elif n.y < -0.99:
            f.material_index = 2
        elif n.z < -0.99:
            f.material_index = 3
        else:
            f.material_index = 0
    o = _mesh_object(bm, name)
    for m in mats:
        o.data.materials.append(mat(m))
    return o


# --------------------------------------------------------------- materials --
_DECAL_DIR = None


def decal_image(name, w, h, draw, mode="RGBA"):
    """Draw an RGBA image with PIL (`draw(img, ImageDraw)`) and load it."""
    global _DECAL_DIR
    from PIL import Image, ImageDraw
    if _DECAL_DIR is None:
        _DECAL_DIR = tempfile.mkdtemp(prefix="bf_decals_")
    img = Image.new(mode, (w, h), (0, 0, 0, 0))
    draw(img, ImageDraw.Draw(img))
    path = os.path.join(_DECAL_DIR, name + ".png")
    img.save(path)
    bi = bpy.data.images.load(path, check_existing=False)
    bi.name = "decal_" + name
    bi.colorspace_settings.name = "sRGB"
    bi.pack()
    return bi


def _sock(nt, inp):
    if inp.is_linked:
        return inp.links[0].from_socket
    n = nt.nodes.new("ShaderNodeValue")
    n.outputs[0].default_value = inp.default_value if not hasattr(inp.default_value, "__len__") else inp.default_value[0]
    return n.outputs[0]


def _vmath(nt, op, a, b=None):
    n = _node(nt, "ShaderNodeVectorMath", operation=op)
    _feed(nt, n.inputs[0], a)
    if b is not None:
        _feed(nt, n.inputs[1], b)
    return n.outputs["Value"] if op in ("DOT_PRODUCT", "LENGTH", "DISTANCE") else n.outputs["Vector"]


def _m(nt, op, a, b=None, clamp=False):
    n = _node(nt, "ShaderNodeMath", operation=op, use_clamp=clamp)
    _feed(nt, n.inputs[0], a)
    if b is not None:
        _feed(nt, n.inputs[1], b)
    return n.outputs[0]


def _mix(nt, fac, a, b, blend="MIX"):
    n = _node(nt, "ShaderNodeMix", data_type="RGBA", blend_type=blend, clamp_result=True)
    _feed(nt, n.inputs["Factor"], fac)
    _feed(nt, n.inputs[6], a)
    _feed(nt, n.inputs[7], b)
    return n.outputs[2]


def _mixf(nt, fac, a, b):
    n = _node(nt, "ShaderNodeMix", data_type="FLOAT")
    _feed(nt, n.inputs["Factor"], fac)
    _feed(nt, n.inputs[2], a)
    _feed(nt, n.inputs[3], b)
    return n.outputs[0]


def decal_pbr(kind, color, decals, name, emboss_distance=0.004, **opts):
    """pbr() plus decals. Each decal is a dict:
        image    bpy image (RGBA; alpha is the coverage)
        origin   centre of the decal (object space of the mesh it is on)
        u, v     unit axes of the image's x (right) and y (up)
        size     (width, height) in metres
        depth    how far off the plane it still applies (default 0.05)
        facing   minimum dot(normal, u x v) (default 0.35; -1 = wraps)
        mode     "mix" (paint/sticker) or "multiply" (grime, stains)
        rough, metal   surface values under the decal (optional)
        emboss   height of the decal alpha in the normal map (+ raised, - engraved)
        cyl      (axis_point, axis_dir, radius): wrap the u axis around a
                 cylinder (labels on a drum); u then runs along the arc.
        repeat   tile the image along u (stripes)
    """
    m = pbr(kind, color, name=name, **opts)
    nt = m.node_tree
    bsdf = nt.nodes["Principled BSDF"]
    base = bsdf.inputs["Base Color"].links[0].from_socket
    rough = _sock(nt, bsdf.inputs["Roughness"])
    metal = _sock(nt, bsdf.inputs["Metallic"])
    nrm = bsdf.inputs["Normal"].links[0].from_socket if bsdf.inputs["Normal"].is_linked else None
    tc = _node(nt, "ShaderNodeTexCoord")
    P = tc.outputs["Object"]
    NRM = tc.outputs["Normal"]
    height = None
    for d in decals:
        o = Vector(d["origin"])
        U = Vector(d.get("u", (1, 0, 0))).normalized()
        V = Vector(d.get("v", (0, 0, 1))).normalized()
        N = U.cross(V).normalized()
        w, h = d["size"]
        rel = _vmath(nt, "SUBTRACT", P, tuple(o))
        if "cyl" in d:
            # u = arc length around the cylinder axis, measured from `origin`.
            ap, ad, rad = d["cyl"]
            ad = Vector(ad).normalized()
            rp = _vmath(nt, "SUBTRACT", P, tuple(ap))
            ref = (o - Vector(ap))
            ref = (ref - ad * ref.dot(ad)).normalized()
            side = ad.cross(ref)
            x = _vmath(nt, "DOT_PRODUCT", rp, tuple(ref))
            y = _vmath(nt, "DOT_PRODUCT", rp, tuple(side))
            ang = _m(nt, "ARCTAN2", y, x)
            u = _m(nt, "ADD", _m(nt, "MULTIPLY", ang, rad / w * (-1 if d.get("flip_u") else 1)), 0.5)
            v = _m(nt, "ADD", _vmath(nt, "DOT_PRODUCT", rel, tuple(V / h)), 0.5)
            sc = _node(nt, "ShaderNodeVectorMath", operation="SCALE")
            sc.inputs[0].default_value = tuple(ad)
            nt.links.new(_vmath(nt, "DOT_PRODUCT", rp, tuple(ad)), sc.inputs["Scale"])
            rlen = _vmath(nt, "LENGTH", _vmath(nt, "SUBTRACT", rp, sc.outputs["Vector"]))
            depth_mask = _m(nt, "LESS_THAN", _m(nt, "ABSOLUTE", _m(nt, "SUBTRACT", rlen, rad)), d.get("depth", 0.05))
            face_mask = 1.0
        else:
            u = _m(nt, "ADD", _vmath(nt, "DOT_PRODUCT", rel, tuple(U / w)), 0.5)
            v = _m(nt, "ADD", _vmath(nt, "DOT_PRODUCT", rel, tuple(V / h)), 0.5)
            dist = _m(nt, "ABSOLUTE", _vmath(nt, "DOT_PRODUCT", rel, tuple(N)))
            depth_mask = _m(nt, "LESS_THAN", dist, d.get("depth", 0.05))
            face_mask = _m(nt, "GREATER_THAN", _vmath(nt, "DOT_PRODUCT", NRM, tuple(N)), d.get("facing", 0.35))
        vmask = None
        if d.get("repeat"):
            u = _m(nt, "FRACT", u)
            vmask = _m(nt, "MULTIPLY", _m(nt, "GREATER_THAN", v, 0.0), _m(nt, "LESS_THAN", v, 1.0))
        comb = _node(nt, "ShaderNodeCombineXYZ")
        _feed(nt, comb.inputs[0], u)
        _feed(nt, comb.inputs[1], v)
        tex = _node(nt, "ShaderNodeTexImage", extension="REPEAT" if d.get("repeat") else "CLIP", interpolation="Linear")
        tex.image = d["image"]
        nt.links.new(comb.outputs[0], tex.inputs["Vector"])
        mask = _m(nt, "MULTIPLY", tex.outputs["Alpha"], depth_mask)
        mask = _m(nt, "MULTIPLY", mask, face_mask)
        if vmask is not None:
            mask = _m(nt, "MULTIPLY", mask, vmask)
        if d.get("opacity", 1.0) != 1.0:
            mask = _m(nt, "MULTIPLY", mask, d["opacity"])
        if d.get("mode") == "multiply":
            base = _mix(nt, mask, base, tex.outputs["Color"], blend="MULTIPLY")
        elif d.get("mode") != "none":
            base = _mix(nt, mask, base, tex.outputs["Color"])
        if "rough" in d:
            rough = _mixf(nt, mask, rough, d["rough"])
        if "metal" in d:
            metal = _mixf(nt, mask, metal, d["metal"])
        if d.get("emboss"):
            hgt = _m(nt, "MULTIPLY", mask, d["emboss"])
            height = hgt if height is None else _m(nt, "ADD", height, hgt)
    nt.links.new(base, bsdf.inputs["Base Color"])
    nt.links.new(rough, bsdf.inputs["Roughness"])
    nt.links.new(metal, bsdf.inputs["Metallic"])
    if height is not None:
        bmp = _node(nt, "ShaderNodeBump")
        bmp.inputs["Strength"].default_value = 1.0
        bmp.inputs["Distance"].default_value = emboss_distance
        nt.links.new(height, bmp.inputs["Height"])
        if nrm is not None:
            nt.links.new(nrm, bmp.inputs["Normal"])
        nt.links.new(bmp.outputs["Normal"], bsdf.inputs["Normal"])
    return m


def glow_glass(color, alpha=0.4, strength=2.0, base=None, name=None, rough=0.1):
    """A transparent shell that also glows (plasma, holograms, energy)."""
    m = pbr("neon", base or tuple(c * 0.4 for c in color), emit=color, strength=strength, rough=rough,
            name=name or "glowglass_%d" % len(bpy.data.materials))
    bsdf = m.node_tree.nodes["Principled BSDF"]
    bsdf.inputs["Alpha"].default_value = alpha
    m.blend_method = "BLEND"
    m.shadow_method = "NONE"
    m.use_backface_culling = True
    return m


def glass(color, alpha=0.3, rough=0.05, name=None):
    m = pbr("glass", color, alpha=alpha, rough=rough, name=name or "glass_%d" % len(bpy.data.materials))
    m.use_backface_culling = True
    return m


def freeze_static(keep=()):
    """Apply location/rotation/scale of every top-level static mesh, so the
    joined body's object space is world space (decal origins and procedural
    texture scales are given in world coordinates)."""
    keep = set(keep)
    objs = [o for o in all_meshes() if o.parent is None and o.name not in keep and not o.children]
    if not objs:
        return
    bpy.ops.object.select_all(action="DESELECT")
    for o in objs:
        o.select_set(True)
    bpy.context.view_layer.objects.active = objs[0]
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)


def fix_scratches():
    """common.pbr() stretches its scratch noise along object Y only, so on
    faces square to Y (every front face) the "scratches" become blotches.
    Tilt that stretch off all three axes so every face gets thin lines."""
    for m in bpy.data.materials:
        if not m.use_nodes:
            continue
        for n in m.node_tree.nodes:
            if n.type == "MAPPING" and tuple(round(v) for v in n.inputs["Scale"].default_value) in ((1, 40, 1),) \
                    and not n.get("_tilted"):
                # Mapping scales before it rotates: rotate in a node of its own first.
                nt = m.node_tree
                rot = nt.nodes.new("ShaderNodeMapping")
                rot.inputs["Rotation"].default_value = (0.62, 0.35, 0.78)
                src = n.inputs["Vector"].links[0].from_socket if n.inputs["Vector"].is_linked else None
                if src is not None:
                    nt.links.new(src, rot.inputs["Vector"])
                nt.links.new(rot.outputs[0], n.inputs["Vector"])
                n["_tilted"] = True
                # Sparser and shorter than a rain of parallel lines.
                n.inputs["Scale"].default_value = (1, 18, 1)
                for l in n.outputs[0].links:
                    for l2 in l.to_node.outputs["Fac"].links:
                        if l2.to_node.type == "MAP_RANGE":
                            mr = l2.to_node
                            mr.inputs["From Min"].default_value = 0.69
                            mr.inputs["From Max"].default_value = 0.71
                            for l3 in mr.outputs["Result"].links:     # fainter, too
                                if l3.to_node.type == "MATH" and l3.to_node.operation == "MULTIPLY":
                                    l3.to_node.inputs[1].default_value *= 0.45


def finish(name, keep=(), body="body"):
    """fix_scratches + freeze_static + join_static."""
    fix_scratches()
    freeze_static(keep)
    return join_static(body, keep=keep)


def tri_breakdown():
    dg = bpy.context.evaluated_depsgraph_get()
    for o in all_meshes():
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        me.calc_loop_triangles()
        print("  %-20s %5d" % (o.name, len(me.loop_triangles)))
        e.to_mesh_clear()


# --------------------------------------------------------------- reporting --
def tri_count():
    dg = bpy.context.evaluated_depsgraph_get()
    total = 0
    for o in all_meshes():
        e = o.evaluated_get(dg)
        me = e.to_mesh()
        me.calc_loop_triangles()
        total += len(me.loop_triangles)
        e.to_mesh_clear()
    return total


def tri_report(label):
    n = tri_count()
    print("TRIS %s %d" % (label, n))
    return n


def sheet(name, out_dir=None, views=None, size=360, samples=24, zoom=1.0, frame=None, centre=None):
    """Render several views (az, el in degrees; 0,0 = the game's front view)
    side by side into <out_dir>/<name>_sheet.png. Uses SHEET_DIR if unset."""
    out_dir = out_dir or os.environ.get("SHEET_DIR")
    if not out_dir:
        return
    from PIL import Image
    os.makedirs(out_dir, exist_ok=True)
    views = views or [(0, 0), (35, 22), (-60, 35), (160, 15)]
    env = os.environ
    if env.get("SHEET_VIEWS"):
        views = [tuple(float(x) for x in v.split(",")) for v in env["SHEET_VIEWS"].split(";")]
    zoom = float(env.get("SHEET_ZOOM", zoom))
    if env.get("SHEET_CENTRE"):
        centre = tuple(float(x) for x in env["SHEET_CENTRE"].split(","))
    if env.get("SHEET_FRAME"):
        frame = int(env["SHEET_FRAME"])
    size = int(env.get("SHEET_SIZE", size))
    samples = int(env.get("SHEET_SAMPLES", samples))
    if frame is not None:
        bpy.context.scene.frame_set(frame)
    lo, hi = scene_bounds()
    c = (lo + hi) / 2.0 if centre is None else Vector(centre)
    radius = max((hi - lo).length / 2.0, 0.3) / zoom
    scn = bpy.context.scene
    scn.render.engine = "CYCLES"
    scn.cycles.device = "CPU"
    scn.cycles.samples = samples
    scn.cycles.use_denoising = False
    scn.render.resolution_x = size
    scn.render.resolution_y = size
    scn.render.film_transparent = False
    cam_data = bpy.data.cameras.new("sheet_cam")
    cam_data.lens = 50
    cam = _link(bpy.data.objects.new("sheet_cam", cam_data))
    scn.camera = cam
    for (pos, colour, energy) in (
        ((1.0, -1.2, 1.4), (1.0, 0.92, 0.95), 900),
        ((-1.4, -0.6, 0.8), (0.55, 0.85, 1.0), 380),
        ((0.3, 1.2, 1.0), (1.0, 0.45, 0.9), 320),
        ((0.0, -0.4, -1.4), (0.5, 0.3, 0.8), 150),
    ):
        ld = bpy.data.lights.new("sheet_light", "POINT")
        ld.energy = energy * radius * radius
        ld.color = colour
        ld.shadow_soft_size = radius * 0.4
        lo_ = _link(bpy.data.objects.new("sheet_light", ld))
        lo_.location = c + Vector(pos) * radius * 2.2
    # A dim synthwave sky (like the game's) so metals have something to reflect.
    scn.world = scn.world or bpy.data.worlds.new("w")
    scn.world.use_nodes = True
    wnt = scn.world.node_tree
    bg = wnt.nodes["Background"]
    tcw = wnt.nodes.new("ShaderNodeTexCoord")
    sep = wnt.nodes.new("ShaderNodeSeparateXYZ")
    wnt.links.new(tcw.outputs["Generated"], sep.inputs[0])
    ramp = wnt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].position = 0.35
    ramp.color_ramp.elements[0].color = (0.03, 0.05, 0.08, 1)
    ramp.color_ramp.elements[1].position = 0.75
    ramp.color_ramp.elements[1].color = (0.1, 0.04, 0.2, 1)
    mid = ramp.color_ramp.elements.new(0.5)
    mid.color = (0.45, 0.15, 0.4, 1)
    rng = wnt.nodes.new("ShaderNodeMapRange")
    rng.inputs["From Min"].default_value = -1.0
    rng.inputs["From Max"].default_value = 1.0
    wnt.links.new(sep.outputs["Z"], rng.inputs["Value"])
    wnt.links.new(rng.outputs["Result"], ramp.inputs["Fac"])
    wnt.links.new(ramp.outputs["Color"], bg.inputs[0])
    bg.inputs[1].default_value = 1.0
    tiles = []
    for i, (az, el) in enumerate(views):
        a, e = math.radians(az), math.radians(el)
        d = Vector((math.sin(a) * math.cos(e), -math.cos(a) * math.cos(e), math.sin(e)))
        cam.location = c + d * radius * 2.5
        cam.rotation_euler = (c - cam.location).to_track_quat("-Z", "Y").to_euler()
        path = os.path.join(out_dir, "_%s_%d.png" % (name, i))
        scn.render.filepath = path
        bpy.ops.render.render(write_still=True)
        tiles.append(Image.open(path).convert("RGB"))
    W = Image.new("RGB", (size * len(tiles), size))
    for i, t in enumerate(tiles):
        W.paste(t, (i * size, 0))
    out = os.path.join(out_dir, name + "_sheet.png")
    W.save(out)
    for i in range(len(tiles)):
        os.remove(os.path.join(out_dir, "_%s_%d.png" % (name, i)))
    print("SHEET %s" % out)
