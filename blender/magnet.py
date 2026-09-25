# magnet: a horseshoe electromagnet 0.8 m wide, 1.1 m tall, poles up,
# centred (it floats and spins above the pedestal; pickup.gd owns that
# motion). A square-section red lacquered horseshoe with ground chrome pole
# shoes stamped N and S, copper field coils wound round both legs with brass
# end plates, and arcs of field light jumping between the poles. Idle: the
# field arcs pulse and climb.
#   blender -b --python blender/magnet.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
LEG = 0.34         # leg centre x
TOP = 0.22         # where the pole shoes start
W = 0.2            # section size


def draw_windings(img, d):
    w, h = img.size
    for y in range(0, h, 4):
        d.rectangle((0, y, w, y + 1), fill=(255, 255, 255, 255))


def draw_pole(img, d, letter):
    w, h = img.size
    f = pil_font(int(h * 0.8))
    d.text((w / 2, h / 2), letter, font=f, fill=(40, 30, 40, 255), anchor="mm")


windings = decal_image("mag_windings", 16, 128, draw_windings)
n_img = decal_image("mag_n", 64, 64, lambda i, d: draw_pole(i, d, "N"))
s_img = decal_image("mag_s", 64, 64, lambda i, d: draw_pole(i, d, "S"))

RED_M = pbr("paint", (0.62, 0.04, 0.05), rough=0.22, name="mag_red", wear=0.5)
POLE = decal_pbr("chrome", (0.75, 0.76, 0.8), [
    dict(image=n_img, origin=(-LEG, -W / 2 - 0.005, TOP + 0.1), size=(0.16, 0.16), depth=0.02, mode="multiply",
         rough=0.5, emboss=-0.5),
    dict(image=s_img, origin=(LEG, -W / 2 - 0.005, TOP + 0.1), size=(0.16, 0.16), depth=0.02, mode="multiply",
         rough=0.5, emboss=-0.5),
], name="mag_pole")
COPPER = decal_pbr("gold", (0.72, 0.32, 0.16), [
    dict(image=windings, origin=(-LEG, -0.15, -0.1), size=(0.3, 0.34), repeat=True,
         cyl=((-LEG, 0, 0), (0, 0, 1), 0.15), depth=0.03, mode="none", emboss=1.0),
    dict(image=windings, origin=(LEG, -0.15, -0.1), size=(0.3, 0.34), repeat=True,
         cyl=((LEG, 0, 0), (0, 0, 1), 0.15), depth=0.03, mode="none", emboss=1.0),
], name="mag_copper", rough=0.3, emboss_distance=0.004)
BRASS_M = pbr("gold", (0.7, 0.5, 0.18), rough=0.3, name="mag_brass")
DARKM = pbr("rubber", (0.04, 0.04, 0.05), name="mag_rubber")
ARC = pbr("neon", (0.1, 0.35, 0.5), emit=(0.45, 0.9, 1.0), strength=5.0, name="mag_arc")
SPARK = pbr("neon", (0.6, 0.9, 1.0), emit=(0.85, 0.97, 1.0), strength=8.0, name="mag_spark")

# The horseshoe: a square section swept round a U.
path = [(-LEG, 0, TOP)]
path += [(-LEG, 0, -0.2)]
for i in range(1, 12):
    a = math.pi + math.pi * i / 12
    path.append((LEG * math.cos(a), 0, -0.2 + LEG * math.sin(a)))
path += [(LEG, 0, -0.2), (LEG, 0, TOP)]
tube(path, W * 0.7071, RED_M, sides=4, name="horseshoe", up=(0, 1, 0), twist=0.0, phase=math.pi / 4, smooth=False)
# Chrome pole shoes.
for s in (-1, 1):
    bm_box((W + 0.02, W + 0.02, 0.2), (s * LEG, 0, TOP + 0.1), POLE, chamfer=0.02)
# Field coils on both legs, with brass end plates.
for s in (-1, 1):
    lathe([(0.15, -0.27), (0.15, 0.07)], COPPER, segments=16, loc=(s * LEG, 0, 0))
    for z in (-0.28, 0.08):
        lathe([(0.0, -0.015), (0.17, -0.015), (0.17, 0.015), (0.0, 0.015)], BRASS_M, segments=16,
              loc=(s * LEG, 0, z))
# Cable from the coils to a little junction on the bend.
tube(smooth_path([(-LEG + 0.12, -0.1, -0.24), (-0.18, -0.16, -0.42), (0.0, -0.13, -0.48), (0.18, -0.16, -0.42),
                  (LEG - 0.12, -0.1, -0.24)], 2), 0.018, DARKM, sides=5, name="lead")
bm_box((0.12, 0.05, 0.08), (0, -0.14, -0.5), BRASS_M, chamfer=0.01)

# Field arcs between the poles: nested half-loops of light that pulse up.
field = pivot("field", (0, 0, TOP + 0.2))
for k, r in enumerate((LEG, LEG * 0.72)):
    pts = []
    for i in range(15):
        a = math.pi * i / 14
        j = 0.0 if i in (0, 14) else (0.035 if i % 2 else -0.03) * (1 + k)   # an electric zig-zag
        pts.append(((r + j) * math.cos(a), 0.0, TOP + 0.2 + (r + j) * 0.75 * math.sin(a)))
    tube(pts, 0.014 - k * 0.003, ARC, sides=4, name="arc%d" % k, parent=field)
for s in (-1, 1):
    sphere(0.045, (s * LEG, 0, TOP + 0.21), SPARK, segments=8, rings=5, parent=field)
key(field, "idle", "scale", [(0, (1, 1, 1)), (10, (1.06, 1, 1.25)), (20, (0.96, 1, 0.85)), (30, (1.03, 1, 1.12)),
                             (45, (1, 1, 1)), (60, (1, 1, 1))])

finish("magnet")
scale_all(0.88)      # fits the float height over the pedestal
tri_report("magnet")
export("magnet", tex=512)
sheet("magnet", views=[(0, 0), (35, 20), (80, 10)])
