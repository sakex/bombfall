# The player: a chibi astronaut in a coral pressure suit with an oversized
# glossy black bomb head inside a coral full-face biker helmet with a
# flipped-up visor, two huge glowing eyes with sparkle highlights,
# blushing cheeks, a smile, headphone cups, a bobbing antenna, a little
# jet pack and a cyan scarf. ~1.5 m tall, origin between the feet, facing
# -Y. Pivots the game animates:
#   arm_l / arm_r (shoulders), leg_l / leg_r (hips), eye_l / eye_r (blink),
#   antenna (wobble), scarf (flutter), jet_l / jet_r (thruster flames).
#   blender -b --python blender/player.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
SUIT = (CORAL, 0.55, 0.0)
SUIT_DARK = ((0.58, 0.12, 0.20), 0.6, 0.0)
SUIT_LIGHT = ((1.0, 0.55, 0.58), 0.55, 0.0)
GLOVE = ((0.05, 0.04, 0.06), 0.5, 0.0)
HELMET = ((0.012, 0.012, 0.018), 0.10, 0.4)
EYE = neon((0.35, 0.95, 1.0), 6.0, (0.1, 0.5, 0.6))
SPARK = neon(WHITE, 8.0, (0.8, 0.8, 0.8))
SHEEN = neon((0.8, 0.9, 1.0), 1.4, (0.5, 0.55, 0.65))
BLUSH = neon((1.0, 0.35, 0.55), 1.2, (0.35, 0.10, 0.18))
SMILE = neon((0.35, 0.95, 1.0), 4.0, (0.1, 0.5, 0.6))
ANTENNA = neon(PINK, 6.0)
VENT = neon(CYAN, 3.0)
SCARF = ((0.15, 0.85, 0.95), 0.7, 0.0)
SHELL = ((0.98, 0.42, 0.50), 0.28, 0.0)
VISOR = ((0.03, 0.03, 0.05), 0.08, 0.5)
STRIPE = ((0.97, 0.97, 1.0), 0.45, 0.0)
FLAME = neon((1.0, 0.6, 0.15), 6.0, (1.0, 0.4, 0.1))

HIP = 0.38
SHOULDER = 0.78
HEAD_Z = 1.02
HEAD_R = 0.42
HZ = HEAD_Z + HEAD_R * 0.55

# Legs: short and stubby, from hip pivots, with knee pads and lit soles.
for side, name in ((-1, "leg_l"), (1, "leg_r")):
    x = side * 0.13
    p = pivot(name, (x, 0.0, HIP))
    cyl(0.095, 0.24, (x, 0.0, HIP - 0.13), SUIT, verts=12, parent=p)
    sphere(0.105, (x, -0.02, HIP - 0.26), SUIT_DARK, segments=10, rings=8, parent=p)   # knee pad
    cube((0.21, 0.30, 0.15), (x, -0.03, 0.075), GLOVE, bevel=0.05, parent=p)          # rounded boot
    cube((0.23, 0.32, 0.03), (x, -0.03, 0.015), SUIT_DARK, bevel=0.01, parent=p)       # sole
    cube((0.16, 0.10, 0.03), (x, -0.16, 0.07), VENT, bevel=0.01, parent=p)            # boot light

# Body: a round belly, a belt with pouches, a chest badge and side stripes.
sphere(0.33, (0, 0, 0.62), SUIT, scale=(0.95, 0.80, 0.82), segments=16, rings=10)
torus(0.29, 0.035, (0, 0, 0.50), SUIT_DARK, scale=(1.0, 0.85, 1.0))
sphere(0.05, (0, -0.25, 0.50), METAL_CHROME, segments=8, rings=6)
for s in (-1, 1):
    cube((0.09, 0.07, 0.08), (s * 0.2, -0.17, 0.50), GLOVE, bevel=0.02)                 # pouches
    cube((0.03, 0.02, 0.34), (s * 0.30, -0.10, 0.64), SUIT_LIGHT, bevel=0.0)           # stripes
# Lightning-bolt badge.
cube((0.05, 0.02, 0.09), (0.01, -0.315, 0.71), VENT, rot=(0, 0.5, 0), bevel=0.0)
cube((0.05, 0.02, 0.09), (-0.02, -0.315, 0.63), VENT, rot=(0, 0.5, 0), bevel=0.0)
cube((0.36, 0.16, 0.30), (0, 0.27, 0.66), GLOVE, bevel=0.05)                            # backpack
for s in (-1, 1):
    cube((0.06, 0.03, 0.16), (s * 0.10, 0.36, 0.68), VENT, bevel=0.005)
    j = pivot("jet_l" if s < 0 else "jet_r", (s * 0.10, 0.30, 0.50))
    cyl(0.05, 0.08, (s * 0.10, 0.30, 0.50), METAL_DARK, r2=0.035, verts=10, parent=j)
    cone(0.045, 0.22, (s * 0.10, 0.30, 0.36), FLAME, rot=(math.pi, 0, 0), verts=8, name="flame_l" if s < 0 else "flame_r", parent=j)

# Scarf: a flat band around the neck and a tail flapping behind.
torus(0.19, 0.045, (0, 0, 0.92), SCARF, scale=(1, 1, 0.6))
sc = pivot("scarf", (0, 0.18, 0.9))
cube((0.14, 0.42, 0.03), (0, 0.42, 0.86), SCARF, rot=(0.35, 0, 0), bevel=0.01, parent=sc)
cube((0.10, 0.3, 0.03), (0.05, 0.60, 0.78), SCARF, rot=(0.7, 0, 0.2), bevel=0.01, parent=sc)

# Arms: short, ending in mitten spheres, with a stripe on the shoulder.
for side, name in ((-1, "arm_l"), (1, "arm_r")):
    x = side * 0.32
    p = pivot(name, (x, 0.0, SHOULDER))
    sphere(0.09, (x, 0.0, SHOULDER), SUIT_DARK, segments=10, rings=8, parent=p)
    rod((x, 0.0, SHOULDER - 0.02), (x + side * 0.06, -0.02, SHOULDER - 0.30), 0.07, SUIT, parent=p)
    torus(0.075, 0.012, (x + side * 0.02, -0.01, SHOULDER - 0.12), SUIT_LIGHT, rot=(0.15, side * 0.2, 0), parent=p)
    sphere(0.10, (x + side * 0.07, -0.03, SHOULDER - 0.34), GLOVE, segments=10, rings=8, parent=p)

# Head: the big glossy black bomb dome.
cyl(0.17, 0.10, (0, 0, 0.90), GLOVE, verts=14)
sphere(HEAD_R, (0, 0, HZ), HELMET, scale=(1.06, 1.0, 1.0), segments=18, rings=12, name="helmet")


def keep_above(obj, co, no):
    """Cut `obj` by a plane and keep the side the normal points to."""
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=co, plane_no=no, clear_inner=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    return obj


def cut_out(obj, size, loc):
    """Subtract a box from `obj` (boolean difference, applied)."""
    bpy.ops.mesh.primitive_cube_add(size=1.0, location=loc)
    cutter = bpy.context.active_object
    cutter.scale = size
    mod = obj.modifiers.new("cut", "BOOLEAN")
    mod.operation = "DIFFERENCE"
    mod.solver = "EXACT"
    mod.object = cutter
    bpy.ops.object.select_all(action="DESELECT")
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj
    bpy.ops.object.modifier_apply(modifier=mod.name)
    bpy.data.objects.remove(cutter, do_unlink=True)
    return obj


# Biker helmet: a full-face coral shell around the whole head with a wide
# face opening for the eyes and smile, a chin bar with vents, a flipped-up
# smoked visor on chrome hinges, racing stripes and a glowing tail light.
SHELL_R = HEAD_R + 0.06
SHELL_SX = 1.06
OPEN_LO = HZ - 0.24      # bottom of the face opening (above the chin bar)
OPEN_HI = HZ + 0.30      # top of the face opening (under the visor)
shell = sphere(SHELL_R, (0, 0, HZ), SHELL, scale=(SHELL_SX, 1.0, 1.04), segments=24, rings=14)
keep_above(shell, (0, 0, HZ - 0.40), (0, 0, 1))                                      # open at the neck
cut_out(shell, (0.80, 0.70, OPEN_HI - OPEN_LO), (0, -SHELL_R - 0.05, (OPEN_HI + OPEN_LO) / 2))
# Rim around the face opening and the chin bar.
for z in (OPEN_LO, OPEN_HI):
    cube((0.80, 0.05, 0.035), (0, -SHELL_R * 0.86, z), SUIT_DARK, bevel=0.01)
cube((0.62, 0.05, 0.02), (0, -SHELL_R * 0.90, OPEN_LO - 0.005), VENT, bevel=0.0)      # neon lip
for i in range(3):
    cube((0.10, 0.06, 0.05), (-0.16 + i * 0.16, -SHELL_R * 0.97, HZ - 0.33), GLOVE, bevel=0.005)   # chin vents
torus(SHELL_R * 0.84, 0.03, (0, 0, HZ - 0.40), SUIT_DARK, scale=(SHELL_SX, 1.0, 1.0), major_segments=24, minor_segments=5)  # neck roll
# Visor: a smoked band lifted up onto the forehead.
visor = sphere(SHELL_R + 0.035, (0, 0, HZ), VISOR, scale=(SHELL_SX, 1.0, 1.04), segments=24, rings=14)
keep_above(visor, (0, 0, OPEN_HI + 0.01), (0, 0, 1))
keep_above(visor, (0, 0, OPEN_HI + 0.24), (0, 0, -1))
keep_above(visor, (0, -0.08, HZ), (0, -1, 0))
vrim = torus(SHELL_R + 0.04, 0.015, (0, 0, OPEN_HI + 0.02), METAL_CHROME, scale=(SHELL_SX, 1.0, 1.0), major_segments=24, minor_segments=4)
keep_above(vrim, (0, -0.08, HZ), (0, -1, 0))
for s in (-1, 1):
    hx = s * (SHELL_R * SHELL_SX + 0.015)
    cyl(0.085, 0.05, (hx, -0.02, HZ + 0.10), METAL_CHROME, rot=(0, math.pi / 2, 0), verts=14)   # visor hinge
    cyl(0.035, 0.03, (hx + s * 0.03, -0.02, HZ + 0.10), VENT, rot=(0, math.pi / 2, 0), verts=10)
# Racing stripes over the top: white centre, cyan either side.
for x, m, w in ((0.0, STRIPE, 0.028), (-0.10, VENT, 0.012), (0.10, VENT, 0.012)):
    r = math.sqrt(SHELL_R ** 2 - (x / SHELL_SX) ** 2) + 0.006
    st = torus(r, w, (x, 0, HZ), m, rot=(0, math.pi / 2, 0), scale=(1.0, 1.0, 1.04), major_segments=24, minor_segments=4)
    keep_above(st, (0, 0, HZ + 0.30), (0, 0, 1))
    keep_above(st, (0, 0.30, HZ), (0, 1, 0))                                          # back half only
# Tail light: a glowing band around the back.
tail = torus(SHELL_R + 0.004, 0.014, (0, 0, HZ - 0.02), ANTENNA, scale=(SHELL_SX, 1.0, 1.0), major_segments=24, minor_segments=4)
keep_above(tail, (0, 0.22, HZ), (0, 1, 0))
# Sheen: a crescent highlight on the shell.
sheen = torus(SHELL_R * 0.80, 0.02, (0, -0.02, HZ + 0.12), SHEEN, rot=(0.9, 0.3, 0.4), scale=(1.0, 1.0, 0.7), major_segments=24, minor_segments=5)
keep_above(sheen, (0, -0.02, HZ + 0.12), (0.5, 0.2, -1.0))
# Eyes: huge, slightly tilted outward, on pivots so they can blink.
for s in (-1, 1):
    ex = s * 0.17
    ey = -HEAD_R * 0.86
    ez = HZ + 0.06
    ep = pivot("eye_l" if s < 0 else "eye_r", (ex, ey, ez))
    e = sphere(0.135, (ex, ey, ez), EYE, scale=(1.0, 0.35, 1.25), segments=12, rings=8, parent=ep)
    e.rotation_euler = (0, s * 0.18, 0)
    sphere(0.045, (ex - s * 0.045, ey - 0.05, ez + 0.07), SPARK, segments=6, rings=4, parent=ep)
    sphere(0.022, (ex + s * 0.05, ey - 0.05, ez - 0.05), SPARK, segments=6, rings=4, parent=ep)
    sphere(0.065, (s * 0.29, -HEAD_R * 0.80, HZ - 0.11), BLUSH, scale=(1.0, 0.3, 0.7), segments=10, rings=6)
arc = torus(0.085, 0.014, (0, -HEAD_R * 0.98, HZ - 0.12), SMILE, rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=6)
bpy.ops.object.select_all(action="DESELECT")
arc.select_set(True)
bpy.context.view_layer.objects.active = arc
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.bisect(plane_co=(0, -HEAD_R * 0.98, HZ - 0.12), plane_no=(0, 0, -1), clear_inner=True)
bpy.ops.object.mode_set(mode="OBJECT")
# Antenna with a glowing tip, on a pivot at its base.
ANT_Z = HZ + math.sqrt(SHELL_R ** 2 - 0.12 ** 2 - 0.05 ** 2)
ap = pivot("antenna", (0.12, 0.05, ANT_Z))
sphere(0.035, (0.12, 0.05, ANT_Z), GLOVE, segments=8, rings=6, parent=ap)
rod((0.12, 0.05, ANT_Z), (0.22, 0.05, HZ + SHELL_R + 0.20), 0.018, GLOVE, parent=ap)
sphere(0.055, (0.22, 0.05, HZ + SHELL_R + 0.22), ANTENNA, segments=10, rings=8, parent=ap)

join_static("body")
export("player")
