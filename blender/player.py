# The player: a chibi astronaut in a coral pressure suit with an oversized
# glossy black helmet, two huge glowing eyes with sparkle highlights, blushing
# cheeks, a smile, headphone cups and a bobbing antenna. ~1.5 m tall, origin
# between the feet, facing -Y. Limbs hang from pivots the game swings while
# running: arm_l / arm_r at the shoulders, leg_l / leg_r at the hips.
#   blender -b --python blender/player.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403

clean_scene()
SUIT = (CORAL, 0.55, 0.0)
SUIT_DARK = ((0.58, 0.12, 0.20), 0.6, 0.0)
SUIT_LIGHT = ((1.0, 0.45, 0.50), 0.55, 0.0)
GLOVE = ((0.05, 0.04, 0.06), 0.5, 0.0)
HELMET = ((0.012, 0.012, 0.018), 0.12, 0.35)
EYE = neon((0.35, 0.95, 1.0), 6.0, (0.1, 0.5, 0.6))
SPARK = neon(WHITE, 8.0, (0.8, 0.8, 0.8))
BLUSH = neon((1.0, 0.35, 0.55), 1.2, (0.35, 0.10, 0.18))
SMILE = neon((0.35, 0.95, 1.0), 4.0, (0.1, 0.5, 0.6))
ANTENNA = neon(PINK, 6.0)
VENT = neon(CYAN, 3.0)

HIP = 0.38
SHOULDER = 0.78
HEAD_Z = 1.02
HEAD_R = 0.42

# Legs: short and stubby, from hip pivots.
for side, name in ((-1, "leg_l"), (1, "leg_r")):
    x = side * 0.13
    p = pivot(name, (x, 0.0, HIP))
    cyl(0.095, 0.24, (x, 0.0, HIP - 0.13), SUIT, verts=12, parent=p)
    sphere(0.10, (x, 0.0, HIP - 0.26), SUIT_DARK, segments=10, rings=8, parent=p)   # knee ball
    cube((0.21, 0.30, 0.15), (x, -0.03, 0.075), GLOVE, bevel=0.05, parent=p)         # rounded boot
    cube((0.16, 0.10, 0.03), (x, -0.16, 0.07), VENT, bevel=0.01, parent=p)           # boot light

# Body: a round belly with a belt and a chest badge.
sphere(0.33, (0, 0, 0.62), SUIT, scale=(0.95, 0.80, 0.82), segments=20, rings=14)
torus(0.29, 0.035, (0, 0, 0.50), SUIT_DARK, scale=(1.0, 0.85, 1.0))                  # belt
sphere(0.05, (0, -0.25, 0.50), METAL_CHROME, segments=8, rings=6)                      # buckle
sphere(0.06, (0, -0.31, 0.68), SPARK, scale=(1.0, 0.4, 1.0), segments=10, rings=8)    # chest light
cube((0.36, 0.16, 0.30), (0, 0.27, 0.66), GLOVE, bevel=0.05)                          # backpack
for s in (-1, 1):
    cube((0.06, 0.03, 0.16), (s * 0.10, 0.36, 0.68), VENT, bevel=0.005)               # backpack vents

# Arms: short, ending in mitten spheres.
for side, name in ((-1, "arm_l"), (1, "arm_r")):
    x = side * 0.32
    p = pivot(name, (x, 0.0, SHOULDER))
    sphere(0.09, (x, 0.0, SHOULDER), SUIT_DARK, segments=10, rings=8, parent=p)
    rod((x, 0.0, SHOULDER - 0.02), (x + side * 0.06, -0.02, SHOULDER - 0.30), 0.07, SUIT, parent=p)
    sphere(0.10, (x + side * 0.07, -0.03, SHOULDER - 0.34), GLOVE, segments=10, rings=8, parent=p)

# Helmet: the big glossy dome, slightly wider than tall.
cyl(0.17, 0.10, (0, 0, 0.90), GLOVE, verts=14)                                        # neck ring
sphere(HEAD_R, (0, 0, HEAD_Z + HEAD_R * 0.55), HELMET, scale=(1.06, 1.0, 1.0), segments=24, rings=16, name="helmet")
HZ = HEAD_Z + HEAD_R * 0.55
# Eyes: huge, slightly tilted outward, with a white sparkle each.
for s in (-1, 1):
    ex = s * 0.17
    ey = -HEAD_R * 0.86
    ez = HZ + 0.06
    e = sphere(0.135, (ex, ey, ez), EYE, scale=(1.0, 0.35, 1.25), segments=14, rings=10)
    e.rotation_euler = (0, s * 0.18, 0)
    sphere(0.045, (ex - s * 0.045, ey - 0.05, ez + 0.07), SPARK, segments=8, rings=6)
    sphere(0.022, (ex + s * 0.05, ey - 0.05, ez - 0.05), SPARK, segments=8, rings=6)
    # Blush.
    sphere(0.07, (s * 0.32, -HEAD_R * 0.78, HZ - 0.12), BLUSH, scale=(1.0, 0.3, 0.7), segments=10, rings=6)
# Smile: the lower half of a thin ring.
arc = torus(0.085, 0.014, (0, -HEAD_R * 0.98, HZ - 0.12), SMILE, rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=6)
bpy.ops.object.select_all(action="DESELECT")
arc.select_set(True)
bpy.context.view_layer.objects.active = arc
bpy.ops.object.mode_set(mode="EDIT")
bpy.ops.mesh.select_all(action="SELECT")
bpy.ops.mesh.bisect(plane_co=(0, -HEAD_R * 0.98, HZ - 0.12), plane_no=(0, 0, -1), clear_inner=True)
bpy.ops.object.mode_set(mode="OBJECT")
# Headphone cups and band.
for s in (-1, 1):
    cyl(0.13, 0.09, (s * HEAD_R * 1.02, 0.0, HZ), SUIT, rot=(0, math.pi / 2, 0), verts=14, bevel=0.02)
    cyl(0.07, 0.03, (s * (HEAD_R * 1.02 + 0.05), 0.0, HZ), VENT, rot=(0, math.pi / 2, 0), verts=12)
torus(HEAD_R * 1.03, 0.028, (0, 0, HZ), SUIT_DARK, rot=(0, math.pi / 2, 0), scale=(1.0, 0.55, 1.0), major_segments=28)
# Antenna with a glowing tip.
rod((0.12, 0.05, HZ + HEAD_R * 0.92), (0.22, 0.05, HZ + HEAD_R + 0.20), 0.018, GLOVE)
sphere(0.055, (0.22, 0.05, HZ + HEAD_R + 0.22), ANTENNA, segments=10, rings=8)

join_static("body")
export("player")
