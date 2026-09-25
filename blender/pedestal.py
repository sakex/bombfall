# The pick-up pedestal: a holo-projector plinth 1.5 m wide, 1.4 m tall
# (origin at the bottom centre), with a tractor beam rising above it where
# the item floats (pickup.gd bobs and spins the item at 2.1 m). A stepped,
# chamfered base with chrome kick plates and rubber feet, a lacquered
# column with neon inlays and brass rings, and a projector head: three
# emitter prongs round a glowing lens. Idle: the prong collar turns and two
# light rings climb the beam. The beam mesh is `beam`.
#   blender -b --python blender/pedestal.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()


def draw_plate(img, d):
    w, h = img.size
    d.rounded_rectangle((2, 2, w - 3, h - 3), radius=10, fill=(24, 22, 34, 255), outline=(200, 160, 80, 255), width=4)
    f = pil_font(int(h * 0.42))
    d.text((w / 2, h * 0.5), "GRAND BOMBFALL HOTEL", font=f, fill=(220, 190, 120, 255), anchor="mm")


plate_img = decal_image("ped_plate", 512, 64, draw_plate)

BASE = decal_pbr("paint", (0.05, 0.045, 0.08), [
    dict(image=plate_img, origin=(0, -0.6, 0.17), size=(0.9, 0.11), depth=0.03, rough=0.3, emboss=0.3),
], name="ped_base", wear=0.6, grime=0.5)
LACQUER = pbr("plastic", (0.12, 0.03, 0.16), rough=0.18, name="ped_lacquer", wear=0.2)
CHROME_M = pbr("chrome", (0.7, 0.7, 0.75), name="ped_chrome")
BRASS_M = pbr("gold", (0.7, 0.48, 0.16), rough=0.28, name="ped_brass")
RUBBER = pbr("rubber", (0.03, 0.03, 0.035), name="ped_rubber")
DARKM = pbr("metal", (0.14, 0.15, 0.18), rough=0.4, name="ped_dark")
NEON = pbr("neon", (0.02, 0.2, 0.25), emit=CYAN, strength=3.0, name="ped_neon")
LENS = pbr("neon", (0.3, 0.8, 0.9), emit=(0.5, 0.95, 1.0), strength=5.0, name="ped_lens")
BEAM = glow_glass((0.25, 0.85, 1.0), alpha=0.16, strength=1.4, name="ped_beam")
HALO = pbr("neon", (0.1, 0.4, 0.5), emit=(0.4, 0.95, 1.0), strength=3.5, name="ped_halo")

# Stepped base: a wide chamfered plinth, a second step, chrome kick plates.
bm_box((1.5, 1.2, 0.26), (0, 0, 0.16), BASE, chamfer=0.05)
bm_box((1.26, 0.98, 0.14), (0, 0, 0.35), BASE, chamfer=0.04)
bm_box((1.54, 1.24, 0.05), (0, 0, 0.045), CHROME_M, chamfer=0.015)
for sx in (-1, 1):
    for sy in (-1, 1):
        cyl(0.07, 0.03, (sx * 0.62, sy * 0.47, 0.015), RUBBER, verts=8, bevel=0.0)
        bolt((sx * 0.56, sy * 0.42, 0.42), (0, 0, 1), 0.03, 0.012, CHROME_M, spin=0.3)

# Column: lathe with a brass ring at the foot and the neck.
lathe([(0.42, 0.42), (0.44, 0.47), (0.36, 0.52), (0.34, 1.08), (0.4, 1.14), (0.4, 1.18)],
      LACQUER, segments=20, name="column", angle=35)
lathe([(0.45, 0.42), (0.47, 0.45), (0.47, 0.49), (0.44, 0.52)], BRASS_M, segments=20, name="ring_foot")
for i in range(4):          # neon inlays down the column
    a = i / 4 * math.tau + math.pi / 4
    cube((0.05, 0.03, 0.5), (math.cos(a) * 0.345, math.sin(a) * 0.345, 0.8), NEON, rot=(0, 0, a + math.pi / 2),
         bevel=0.0)

# Projector head: a dished cap with a chrome rim and the glowing lens.
lathe([(0.4, 1.16), (0.56, 1.22), (0.58, 1.3), (0.54, 1.34), (0.46, 1.33), (0.3, 1.3), (0.0, 1.3)],
      DARKM, segments=24, name="head", angle=35)
lathe([(0.57, 1.28), (0.6, 1.31), (0.58, 1.36), (0.53, 1.36), (0.52, 1.32)], CHROME_M, segments=24, name="rim")
torus(0.5, 0.018, (0, 0, 1.35), NEON, major_segments=28, minor_segments=4)
lathe([(0.24, 1.3), (0.24, 1.34), (0.18, 1.37), (0.0, 1.38)], LENS, segments=16, name="lens")

# Collar of three emitter prongs, turning slowly.
collar = pivot("collar", (0, 0, 1.34))
for i in range(3):
    a = i / 3 * math.tau + math.pi / 2
    x, y = math.cos(a), math.sin(a)
    tube(smooth_path([(x * 0.44, y * 0.44, 1.33), (x * 0.47, y * 0.47, 1.45), (x * 0.4, y * 0.4, 1.56)], 2),
         [0.045, 0.04, 0.03, 0.03, 0.025], DARKM, sides=6, name="prong%d" % i, parent=collar)
    sphere(0.035, (x * 0.4, y * 0.4, 1.58), LENS, segments=8, rings=5, parent=collar)
spin(collar, "idle", "Z", seconds=4.0, turns=1.0 / 3.0)

# The tractor beam (a faint glowing cone), and two light rings climbing it.
cyl(0.36, 1.3, (0, 0, 2.03), BEAM, r2=0.26, verts=20, bevel=0.0, name="beam")
Z0, RISE = 1.4, 1.2
for k in range(2):
    p = pivot("halo_%d" % (k + 1), (0, 0, Z0))
    torus(0.34, 0.012, (0, 0, Z0), HALO, major_segments=24, minor_segments=3, parent=p)
    # Each ring rises 1.2 m over 4 s, shrinking, vanishes at the top and
    # restarts at the lens; the second ring runs half a cycle behind.
    off = k * 60
    marks = [(0.0, 1.0), (0.9, 0.62), (0.99, 0.001)]
    keys_z, keys_s = [], []
    for cycle in (-1, 0):
        for t, sc in marks:
            f = off + (cycle * 120) + t * 120
            f2 = f + 120 if f < 0 else f
            if 0 <= f2 <= 120:
                keys_z.append((f2, (0, 0, Z0 + RISE * t)))
                keys_s.append((f2, (sc, sc, 1.0 if sc > 0.01 else 0.001)))
    # Loop ends must match: evaluate the cycle at frames 0 and 120.
    t0 = ((0 - off) % 120) / 120.0
    sc0 = 1.0 - 0.42 * t0 if t0 < 0.9 else 0.001
    for f in (0, 120):
        keys_z.append((f, (0, 0, Z0 + RISE * t0)))
        keys_s.append((f, (sc0, sc0, 1.0)))
    keys_z.sort(key=lambda kv: kv[0])
    keys_s.sort(key=lambda kv: kv[0])
    key(p, "idle", "location", keys_z, interp="LINEAR")
    key(p, "idle", "scale", keys_s, interp="LINEAR")

finish("pedestal", keep=("beam",))
tri_report("pedestal")
export("pedestal", tex=512)
sheet("pedestal", views=[(0, 0), (35, 25), (0, 70)])
