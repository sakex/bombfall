# Backdrop for the penthouse lounge (rich1), Neon Palace: a walnut-panelled
# double-height salon with marble columns carrying a mezzanine behind a
# glass balustrade.  Downstairs: a buttoned oxblood Chesterfield under the
# panoramic window between velvet drapes, a marble fireplace with a live
# fire, wingback chairs, a black grand piano with a ticking metronome in
# front of a lit library wall, palms.  Upstairs: a gold neon "PALACE" sign
# with a crown, paintings, a record player spinning on a credenza and a
# grandfather clock whose pendulum swings.  15 m wide.
#   blender -b --python blender/backdrop_rich1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
WINDOWS = [(1.7, 2.0, 4.6, 2.6), (1.5, 7.7, 2.2, 1.2), (11.3, 7.7, 2.2, 1.2)]
MEZZ = 5.2           # underside of the mezzanine
MZ = 5.55            # its floor
SILK = pbr("fabric", (0.36, 0.15, 0.22), color2=(0.44, 0.2, 0.27), bump=0.3, name="silk")
BOOKS = [M.leather_ox, M.leather_tan, M.leather_black, M.velvet_teal, M.velvet_navy, M.mahogany, M.paper, M.velvet_red]
LED_WARM = neon_mat((1.0, 0.62, 0.3), 1.6, "led_warm")

# ------------------------------------------------------------ architecture --
slab_at(0.0, 15.0, 0.0, WALL, 0.0, 0.02, M.walnut)                        # parquet
wainscot(0.0, 15.0, WINDOWS, M.walnut, M.gold, h=1.05)
# silk boiserie between the windows, the chimney breast and the library
LOWER_SKIP = [(7.3, 1.0, 2.7, 4.5), (10.55, 0.0, 4.1, 5.5)]
boiserie(0.0, 15.0, 1.25, MEZZ - 0.1, WINDOWS + LOWER_SKIP, M.gold, SILK, pitch=1.2)
box((4.4, 0.012, 0.6), (4.0, WALL - 0.007, 1.55), SILK)
moulding_frame(1.9, 6.1, 1.28, 1.85, WALL - 0.02, M.gold)
# columns carrying the mezzanine
for cx in (1.05, 7.0, 10.3, 14.6):
    column(cx, 1.62, MEZZ, M.marble_white, M.gold, r=0.19)
# mezzanine: walnut fascia with gold beads and a warm cove light below
slab_at(0.0, 15.0, 1.02, WALL, MEZZ, MZ, M.walnut, bevel=0.02)
box((15.0, 0.03, 0.03), (7.5, 1.0, MEZZ + 0.08), M.gold)
box((15.0, 0.03, 0.03), (7.5, 1.0, MZ - 0.06), M.gold)
slab_at(0.0, 15.0, 1.0, 1.1, MZ, MZ + 0.03, M.gold)
tube([(0.1, 1.12, MEZZ - 0.03), (14.9, 1.12, MEZZ - 0.03)], 0.018, M.n_amber, verts=5)
glass_rail(0.05, 14.95, 1.1, MZ + 0.03, h=0.95, m_rail=M.gold, post_pitch=1.25)
boiserie(0.0, 15.0, MZ + 0.15, 9.1, WINDOWS + [(5.4, 6.4, 4.2, 2.3)], M.gold, SILK, pitch=1.3)
box((15.0, 0.08, 0.12), (7.5, WALL - 0.04, 9.15), M.walnut, bevel=0.01)       # cornice
box((15.0, 0.1, 0.04), (7.5, WALL - 0.05, 9.05), M.gold)

mark("arch")
# ------------------------------------------------------------- the window --
tube([(1.2, 1.72, 4.95), (6.8, 1.72, 4.95)], 0.025, M.brass, verts=8)
for fx in (1.18, 6.82):
    lathe([(0.0, 0), (0.04, 0.02), (0.05, 0.05), (0.0, 0.1)], (fx, 1.72, 4.95), M.brass, segs=8, rot=(0, math.pi / 2 * (1 if fx > 4 else -1), 0))
for (a, b, s) in ((1.18, 1.66, 1), (6.34, 6.82, -1)):
    p = pivot("drape_%s" % ("l" if s > 0 else "r"), ((a + b) / 2, 1.8, 4.92))
    c = curtain(a, b, 4.92, 1.72, M.velvet_plum, folds=3, depth=0.12)
    attach(c, p)
    tb = tube([((a + b) / 2 - 0.25 * s, 1.68, 1.2), ((a + b) / 2, 1.66, 1.12), ((a + b) / 2 + 0.25 * s, 1.72, 1.2)], 0.018, M.gold, verts=5)
    wobble(p, "idle", "rotation_euler", 0, 0.018, seconds=4, phase=0.0 if s > 0 else 1.3)
    wobble(p, "idle", "rotation_euler", 1, 0.01, seconds=4, phase=0.7)

mark("window")
# -------------------------------------------------------------- the salon --
potted_palm(0.55, 0.85, h=2.3, fronds=9, seed=4)
rug(2.1, 5.9, 0.03, 1.72, M.carpet_navy, M.carpet_red, M.carpet_gold)
chesterfield(4.0, 0.64, w=2.8, m=M.leather_tan, d=0.95, h=0.8, cushions=3)
for i, (px, pz) in enumerate(((3.2, 0.62), (4.8, 0.62))):
    pillow(px - 0.22, px + 0.22, pz, pz + 0.38, 1.3, 0.07, [M.velvet_gold, M.velvet_teal][i], nx=3, nz=3)
side_table(2.05, 1.2, 0.6)
side_table(5.95, 1.2, 0.6)
table_lamp(2.05, 1.2, 0.6, h=0.66)
table_lamp(5.95, 1.2, 0.6, h=0.66)
coffee_table(4.0, 0.04, w=1.5, d=0.52, h=0.42)
# on the coffee table: a champagne bucket, books, a bowl
lathe([(0.08, 0), (0.1, 0.02), (0.11, 0.2), (0.12, 0.22), (0.1, 0.22)], (3.55, 0.3, 0.42), M.chrome, segs=12, cap=False)
bottle(3.57, 0.3, 0.5, kind=3, m=M.glass_bottle_green)
box((0.32, 0.24, 0.05), (4.25, 0.3, 0.445), M.leather_ox)
box((0.28, 0.2, 0.04), (4.25, 0.3, 0.49), M.paper)
lathe([(0.03, 0), (0.12, 0.04), (0.14, 0.07), (0.13, 0.07), (0.0, 0.03)], (4.62, 0.28, 0.42), M.gold, segs=14)

mark("salon")
# ---------------------------------------------------------- the fireplace --
FX = 8.65
slab_at(7.35, 9.95, WALL - 0.25, WALL, 1.36, MEZZ, M.marble_white, bevel=0.01)      # chimney breast
moulding_frame(7.5, 9.8, 1.5, MEZZ - 0.15, WALL - 0.26, M.gold, t=0.035)
slab_at(7.2, 10.1, 0.95, WALL, 0.0, 0.05, M.marble_black, bevel=0.01)             # hearth
# surround: pilasters, frieze, a moulded shelf and corbels
for sx in (-1, 1):
    px = FX + sx * 0.98
    slab_at(px - 0.17, px + 0.17, 1.5, WALL, 0.05, 1.12, M.marble_white, bevel=0.012)
    slab_at(px - 0.2, px + 0.2, 1.46, WALL, 0.05, 0.16, M.marble_white, bevel=0.012)
    lathe([(0.0, 0), (0.07, 0.0), (0.05, 0.12), (0.08, 0.18), (0.0, 0.2)], (px, 1.49, 0.92), M.marble_white, segs=4, rot=(0, 0, math.pi / 4), scale=(1.1, 0.5, 1))
slab_at(FX - 1.18, FX + 1.18, 1.52, WALL, 1.1, 1.3, M.marble_white, bevel=0.012)
box((1.2, 0.02, 0.1), (FX, 1.51, 1.2), M.gold)
slab_at(FX - 1.3, FX + 1.3, 1.4, WALL, 1.3, 1.37, M.marble_white, bevel=0.02)
# the firebox: soot-black recess with a brass rim
slab_at(FX - 0.8, FX + 0.8, 1.9, WALL, 0.05, 1.1, M.rock)
prism([(FX - 0.81, 0.05), (FX + 0.81, 0.05), (FX + 0.81, 1.11), (FX - 0.81, 1.11), (FX - 0.81, 0.05),
       (FX - 0.74, 0.05), (FX - 0.74, 1.04), (FX + 0.74, 1.04), (FX + 0.74, 0.05)], 1.49, 1.52, M.brass, plane="xz")
for sx in (-1, 1):
    prism([(FX + sx * 0.74, 1.52), (FX + sx * 0.8, 1.52), (FX + sx * 0.8, 1.9), (FX + sx * 0.55, 1.9)], 0.05, 1.04, M.black_metal, plane="xy")
slab_at(FX - 0.8, FX + 0.8, 1.52, 1.9, 1.02, 1.1, M.black_metal)
for sx in (-1, 1):                                                                    # andirons
    tube([(FX + sx * 0.45, 1.6, 0.05), (FX + sx * 0.45, 1.6, 0.3)], 0.02, M.brass, verts=6)
    sphere(0.045, (FX + sx * 0.45, 1.6, 0.33), M.brass, segments=6, rings=4)
tube([(FX - 0.45, 1.66, 0.14), (FX + 0.45, 1.66, 0.14)], 0.015, M.black_metal, verts=5)
for (a, b, zz) in (((-0.4, 1.7), (0.35, 1.78), 0.19), ((-0.3, 1.78), (0.42, 1.7), 0.27), ((-0.05, 1.65), (0.2, 1.82), 0.34)):
    tube([(FX + a[0], a[1], zz), (FX + b[0], b[1], zz)], 0.055, M.mahogany, verts=8)
box((1.0, 0.25, 0.04), (FX, 1.74, 0.13), M.ember)
fp = pivot("glow_embers", (FX, 1.74, 0.13))
box((0.9, 0.2, 0.05), (FX, 1.74, 0.15), M.fire_outer, parent=fp)
keys_loop(fp, "scale", [(1, 1, 1), (0.96, 1, 1.4), (1, 1, 0.8), (0.98, 1, 1.25), (1, 1, 1.1), (1, 1, 0.9)], interp="BEZIER")
rnd = rng(11)
for i in range(6):
    t = (i + 0.5) / 6
    fx = FX - 0.5 + t
    p = pivot("flame_%d" % i, (fx, 1.72 - (i % 2) * 0.05, 0.2))
    fh = 0.38 + rnd() * 0.25
    lathe([(0.0, 0), (0.1, 0.05), (0.11, fh * 0.35), (0.06, fh * 0.75), (0.0, fh)], (fx, 1.72 - (i % 2) * 0.05, 0.2), M.fire_outer,
          segs=6, scale=(1.0, 0.45, 1.0), parent=p)
    lathe([(0.0, 0), (0.06, 0.04), (0.06, fh * 0.28), (0.0, fh * 0.6)], (fx, 1.67 - (i % 2) * 0.05, 0.2), M.fire_core,
          segs=5, scale=(1.0, 0.4, 1.0), parent=p)
    merge_children(p, "flame_%d_mesh" % i)
    flicker(p, seed=i + 3, amp=0.3, steps=12)
    wobble(p, "idle", "rotation_euler", 1, 0.08, seconds=4, phase=i * 1.1)
# on the mantel: a gilt clock, a candelabra with flickering candles, urns
slab_at(FX - 0.16, FX + 0.16, 1.55, 1.75, 1.37, 1.62, M.gold, bevel=0.02)
lathe([(0.1, 0), (0.1, 0.02), (0.0, 0.02)], (FX, 1.545, 1.5), M.ceramic, segs=14, rot=(math.pi / 2, 0, 0))
for cx in (FX - 0.75, FX + 0.75):
    lathe([(0.07, 0), (0.07, 0.03), (0.03, 0.08), (0.02, 0.2), (0.02, 0.24)], (cx, 1.62, 1.37), M.gold, segs=10)
    for dx in (-0.14, 0.0, 0.14):
        if dx:
            tube([(cx, 1.62, 1.57), (cx + dx * 0.7, 1.62, 1.56), (cx + dx, 1.62, 1.62)], 0.01, M.gold, verts=5)
        top = 1.62 + (0.04 if dx == 0 else 0.0)
        lathe([(0.018, 0), (0.018, 0.16)], (cx + dx, 1.62, top), M.ceramic, segs=8)
        cp = pivot("candle_%d" % int((cx + dx) * 100), (cx + dx, 1.62, top + 0.16))
        lathe([(0.0, 0), (0.015, 0.02), (0.0, 0.06)], (cx + dx, 1.62, top + 0.16), M.fire_core, segs=6, parent=cp)
        flicker(cp, seed=int(cx * 10 + dx * 100), amp=0.35, steps=8)
for ux in (FX - 1.15, FX + 1.15):
    lathe([(0.05, 0), (0.07, 0.03), (0.1, 0.14), (0.06, 0.26), (0.05, 0.3), (0.07, 0.33)], (ux, 1.6, 1.37), M.ceramic_black, segs=8)
picture(FX, 3.2, 1.5, 1.9, art="sunset", y=WALL - 0.25)
sconce(7.6, 3.0, WALL - 0.25, arms=1)
sconce(9.7, 3.0, WALL - 0.25, arms=1)
armchair(6.95, 0.22, m=M.velvet_teal, turn=-0.4)
armchair(10.35, 0.22, m=M.velvet_teal, turn=0.4)
side_table(6.3, 0.5, 0.55, r=0.2)

mark("fireplace")
# ------------------------------------------------------- library and piano --
LX0, LX1 = 10.65, 14.35
slab_at(LX0, LX1, 1.52, WALL, 0.0, 0.9, M.walnut, bevel=0.01)                    # cupboards
for i in range(6):
    a = LX0 + 0.06 + i * (LX1 - LX0 - 0.12) / 6
    b = a + (LX1 - LX0 - 0.12) / 6
    moulding_frame(a + 0.06, b - 0.06, 0.15, 0.78, 1.51, M.gold, t=0.02)
    box((0.015, 0.02, 0.1), (b - 0.12 if i % 2 == 0 else a + 0.12, 1.5, 0.5), M.brass)
slab_at(LX0 - 0.03, LX1 + 0.03, 1.48, WALL, 0.9, 0.95, M.walnut)
slab_at(LX0, LX1, WALL - 0.03, WALL, 0.95, 4.8, M.backlight)                      # glowing back
bays = 3
bw = (LX1 - LX0) / bays
for i in range(bays + 1):
    slab_at(LX0 + i * bw - 0.035, LX0 + i * bw + 0.035, 1.55, WALL, 0.95, 4.8, M.walnut)
shelf_z = [0.95 + k * 0.77 for k in range(5)]
for k, sz in enumerate(shelf_z):
    slab_at(LX0, LX1, 1.58, WALL, sz, sz + 0.04, M.walnut)
    for i in range(bays):
        a, b = LX0 + i * bw + 0.05, LX0 + (i + 1) * bw - 0.05
        if (i + k) % 3 == 1:
            book_row(a, a + (b - a) * 0.55, 1.64, sz + 0.04, BOOKS, seed=k * 7 + i, h_range=(0.2, 0.3))
            lathe([(0.04, 0), (0.08, 0.08), (0.06, 0.2), (0.03, 0.26), (0.05, 0.3)], (b - 0.25, 1.75, sz + 0.04), [M.ceramic, M.gold, M.ceramic_black][k % 3], segs=7)
        elif (i + k) % 3 == 2:
            book_row(a + 0.3, b, 1.64, sz + 0.04, BOOKS, seed=k * 5 + i + 1, h_range=(0.22, 0.32))
            for j in range(3):
                box((0.24, 0.18, 0.04), (a + 0.14, 1.75, sz + 0.06 + j * 0.042), BOOKS[(j + k) % len(BOOKS)])
        else:
            book_row(a, b, 1.64, sz + 0.04, BOOKS, seed=k * 3 + i + 2, h_range=(0.2, 0.33))
slab_at(LX0 - 0.06, LX1 + 0.06, 1.5, WALL, 4.8, 4.9, M.walnut, bevel=0.015)
slab_at(LX0 - 0.1, LX1 + 0.1, 1.46, WALL, 4.9, 4.97, M.walnut, bevel=0.015)
box((LX1 - LX0, 0.02, 0.03), ((LX0 + LX1) / 2, 1.5, 4.85), M.gold)
tube([(LX0, 1.47, 4.45), (LX1, 1.47, 4.45)], 0.015, M.brass, verts=6)                 # ladder rail
for dx in (0.0, 0.42):
    tube([(13.55 + dx, 1.47, 4.45), (13.55 + dx - 0.05, 0.95, 0.0)], 0.022, M.oak, verts=6)
for k in range(10):
    t = (k + 0.5) / 10.5
    y = 1.47 + (0.95 - 1.47) * t
    z = 4.45 * (1 - t)
    box((0.42, 0.03, 0.025), (13.76 - 0.05 * t, y, z), M.oak)

mark("library")
# the grand piano, seen from the audience side with its lid up
PX, PY = 11.62, 0.3
OUT = [(0, 0), (0.55, 0), (0.8, 0.04), (1.02, 0.16), (1.22, 0.36), (1.42, 0.58), (1.62, 0.78), (1.8, 0.98), (1.9, 1.18),
       (1.9, 1.32), (1.82, 1.42), (1.7, 1.45), (0, 1.45)]
OUTLINE = [(PX + u, PY + v) for u, v in OUT]
prism(OUTLINE, 0.62, 0.98, M.ebony, plane="xy", bevel=0.012)
inner = [(PX + 0.06 + u * 0.93, PY + 0.05 + v * 0.93) for u, v in OUT]
prism(inner, 0.975, 0.99, M.gold, plane="xy")
for k in range(9):                                                                # strings
    tube([(PX + 0.15, PY + 0.15 + k * 0.13, 0.995), (PX + 0.4 + k * 0.16, PY + 0.2 + k * 0.13, 0.995)], 0.004, M.steel, verts=3, caps=False)
hinge = (PX, PY + 1.45, 0.99)
lid = prism([(u, v - 1.45) for u, v in OUT], 0.0, 0.022, M.ebony, plane="xy", bevel=0.006)
for vv in lid.data.vertices:
    vv.co.x += 0.0
lid.location = hinge
lid.rotation_euler = (-0.62, 0, 0)
tube([(PX + 1.15, PY + 0.35, 0.99), (PX + 1.12, PY + 0.52, 1.72)], 0.012, M.ebony, verts=5)   # prop stick
for (u, v) in ((0.12, 0.12), (0.12, 1.33), (1.7, 1.3)):
    lathe([(0.03, 0), (0.045, 0.04), (0.06, 0.42), (0.07, 0.55), (0.08, 0.62)], (PX + u, PY + v, 0.0), M.ebony, segs=8)
    lathe([(0.03, 0), (0.032, 0.03), (0.0, 0.035)], (PX + u, PY + v, 0.0), M.brass, segs=8)
slab_at(PX - 0.2, PX, PY + 0.08, PY + 1.37, 0.66, 0.74, M.ebony, bevel=0.01)            # key bed
slab_at(PX - 0.19, PX - 0.02, PY + 0.12, PY + 1.33, 0.74, 0.765, M.lacquer_white)       # keys
for k in range(14):
    box((0.09, 0.012, 0.018), (PX - 0.07, PY + 0.16 + k * 0.083, 0.775), M.ebony)
for yy in (PY + 0.08, PY + 1.37):
    slab_at(PX - 0.21, PX, yy - 0.03, yy + 0.03, 0.66, 0.82, M.ebony, bevel=0.01)
slab_at(PX + 0.02, PX + 0.08, PY + 0.1, PY + 1.35, 0.98, 1.06, M.ebony)                 # fallboard
prism([(PX + 0.16, 0.99), (PX + 0.2, 0.99), (PX + 0.08, 1.32), (PX + 0.05, 1.32)], PY + 0.35, PY + 1.1, M.ebony, plane="xz")
prism([(PX + 0.1, 1.06), (PX + 0.13, 1.06), (PX + 0.04, 1.3), (PX + 0.01, 1.3)], PY + 0.45, PY + 1.0, M.paper, plane="xz")
tube([(PX + 0.3, PY + 0.7, 0.0), (PX + 0.3, PY + 0.7, 0.62)], 0.018, M.ebony, verts=5)   # lyre
for dy in (-0.06, 0.0, 0.06):
    box((0.12, 0.025, 0.012), (PX + 0.25, PY + 0.7 + dy, 0.05), M.brass)
# metronome on the case, ticking
MX, MY = PX + 0.35, PY + 0.2
prism([(MX - 0.07, 0.99), (MX + 0.07, 0.99), (MX + 0.03, 1.22), (MX - 0.03, 1.22)], MY - 0.05, MY + 0.05, M.walnut, plane="xz", bevel=0.005)
mp = pivot("metronome", (MX, MY - 0.055, 1.02))
tube([(MX, MY - 0.055, 1.02), (MX, MY - 0.055, 1.24)], 0.004, M.steel, verts=4, parent=mp)
box((0.025, 0.012, 0.03), (MX, MY - 0.055, 1.17), M.brass, parent=mp)
merge_children(mp, "metronome_mesh")
key(mp, "idle", "rotation_euler", [(f, (0, 0.38 if (f // 15) % 2 == 0 else -0.38, 0)) for f in range(0, LOOP + 1, 15)], interp="BEZIER")
# bench
slab_at(PX - 0.72, PX - 0.32, PY + 0.4, PY + 1.1, 0.4, 0.5, M.ebony, bevel=0.01)
pillow(PX - 0.7, PX - 0.34, PY + 0.42, PY + 1.08, 0.56, 0.06, M.leather_black, nx=3, nz=4, facing="up", tuft=0.02, tuft_nx=2, tuft_nz=3)
for (u, v) in ((-0.68, 0.45), (-0.36, 0.45), (-0.68, 1.05), (-0.36, 1.05)):
    lathe([(0.02, 0), (0.03, 0.3), (0.025, 0.4)], (PX + u, PY + v, 0.0), M.ebony, segs=6)
mark("piano")
fig_tree(14.55, 0.8, h=1.9, m_pot=M.ceramic)

mark("fig")
# ---------------------------------------------------------- the mezzanine --
# PALACE neon with a crown on a black marble panel
sign_board(7.5, 7.45, WALL - 0.08, 4.5, 1.55, M.marble_black, M.gold, depth=0.06)
neon_text("PALACE", 7.5, 7.0, WALL - 0.12, 0.72, M.n_gold, r=0.03, align="center", spacing=1.5, verts=4)
crown = [(6.95, 8.0), (6.9, 8.55), (7.2, 8.25), (7.5, 8.68), (7.8, 8.25), (8.1, 8.55), (8.05, 8.0), (6.95, 8.0)]
tube([(x, WALL - 0.12, z) for x, z in crown], 0.03, M.n_pink, verts=5)
for x, z in ((6.9, 8.55), (7.5, 8.68), (8.1, 8.55)):
    ico(0.05, (x, WALL - 0.12, z + 0.06), M.n_pink, subdiv=1)
# paintings, sconces and pampas urns either side
picture(4.75, 7.45, 0.95, 1.25, art="portrait", y=WALL)
picture(10.25, 7.45, 0.95, 1.25, art="abstract", y=WALL)
for ux in (4.0, 11.0):
    lathe([(0.12, 0), (0.18, 0.2), (0.2, 0.45), (0.1, 0.7), (0.12, 0.78)], (ux, 1.6, MZ + 0.03), M.ceramic_black, segs=8)
    for k in range(6):
        a = k * 1.05
        top = (ux + math.cos(a) * 0.35, 1.6 + math.sin(a) * 0.15, MZ + 1.6 + (k % 3) * 0.15)
        tube([(ux, 1.6, MZ + 0.7), (ux + math.cos(a) * 0.15, 1.6, MZ + 1.2), top], 0.006, M.oak, verts=3, caps=False)
        lathe([(0.0, 0), (0.035, 0.08), (0.03, 0.25), (0.0, 0.34)], top, M.velvet_gold, segs=6)
# credenzas under the upper windows
for (a, b) in ((1.4, 3.8), (11.2, 13.6)):
    slab_at(a, b, 1.45, WALL, MZ + 0.2, MZ + 0.85, M.walnut, bevel=0.01)
    for i in range(3):
        c0 = a + 0.05 + i * (b - a - 0.1) / 3
        moulding_frame(c0 + 0.06, c0 + (b - a - 0.1) / 3 - 0.06, MZ + 0.28, MZ + 0.77, 1.44, M.gold, t=0.02)
    for fx in (a + 0.08, b - 0.08):
        lathe([(0.03, 0), (0.02, 0.2)], (fx, 1.6, MZ + 0.03), M.gold, segs=6)
table_lamp(1.8, 1.7, MZ + 0.85, h=0.55)
book_row(2.2, 2.8, 1.6, MZ + 0.85, BOOKS, seed=21, h_range=(0.2, 0.26))
# record player on the left credenza: its platter spins
slab_at(3.0, 3.6, 1.5, 1.9, MZ + 0.85, MZ + 0.95, M.walnut, bevel=0.01)
lathe([(0.17, 0), (0.17, 0.012), (0.0, 0.012)], (3.25, 1.7, MZ + 0.95), M.rubber, segs=12)
rp = pivot("spin_record", (3.25, 1.7, MZ + 0.962))
lathe([(0.15, 0), (0.15, 0.008), (0.05, 0.008), (0.05, 0.01), (0.0, 0.01)], (3.25, 1.7, MZ + 0.962), M.plastic_black, segs=14, parent=rp)
lathe([(0.05, 0), (0.05, 0.004), (0.0, 0.004)], (3.25, 1.7, MZ + 0.971), M.plastic_red, segs=10, parent=rp)
box((0.02, 0.1, 0.004), (3.33, 1.7, MZ + 0.972), M.paper, parent=rp)
merge_children(rp, "spin_record_mesh")
tube([(3.5, 1.82, MZ + 0.97), (3.5, 1.82, MZ + 1.01), (3.42, 1.66, MZ + 1.0), (3.33, 1.62, MZ + 0.98)], 0.006, M.chrome, verts=4)
table_lamp(13.2, 1.7, MZ + 0.85, h=0.55)
lathe([(0.05, 0), (0.12, 0.1), (0.1, 0.25), (0.04, 0.35)], (11.7, 1.7, MZ + 0.85), M.gold, segs=10)
# grandfather clock with a swinging pendulum
GX = 14.3
slab_at(GX - 0.28, GX + 0.28, 1.55, WALL, MZ + 0.03, MZ + 0.45, M.mahogany, bevel=0.015)
slab_at(GX - 0.22, GX + 0.22, 1.6, WALL, MZ + 0.45, MZ + 1.55, M.mahogany, bevel=0.012)
box((0.3, 0.02, 0.85), (GX, 1.595, MZ + 1.0), M.glass_dark)
slab_at(GX - 0.3, GX + 0.3, 1.52, WALL, MZ + 1.55, MZ + 2.15, M.mahogany, bevel=0.015)
lathe([(0.22, 0), (0.22, 0.02), (0.0, 0.02)], (GX, 1.52, MZ + 1.85), M.gold, segs=12, rot=(math.pi / 2, 0, 0))
lathe([(0.19, 0), (0.19, 0.01), (0.0, 0.01)], (GX, 1.505, MZ + 1.85), M.ceramic, segs=12, rot=(math.pi / 2, 0, 0))
box((0.012, 0.01, 0.13), (GX, 1.49, MZ + 1.9), M.black_metal, rot=(0, 0.5, 0))
box((0.012, 0.01, 0.09), (GX, 1.49, MZ + 1.87), M.black_metal, rot=(0, -1.2, 0))
prism([(GX - 0.34, MZ + 2.15), (GX + 0.34, MZ + 2.15), (GX + 0.2, MZ + 2.3), (GX, MZ + 2.38), (GX - 0.2, MZ + 2.3)], 1.5, WALL, M.mahogany, plane="xz", bevel=0.01)
pp = pivot("pendulum", (GX, 1.64, MZ + 1.5))
tube([(GX, 1.64, MZ + 1.5), (GX, 1.64, MZ + 0.75)], 0.008, M.brass, verts=4, parent=pp)
lathe([(0.0, 0), (0.08, 0), (0.08, 0.015), (0.0, 0.015)], (GX, 1.645, MZ + 0.72), M.gold, segs=10, rot=(math.pi / 2, 0, 0), parent=pp)
merge_children(pp, "pendulum_mesh")
key(pp, "idle", "rotation_euler", [(f, (0, 0.16 if (f // 30) % 2 == 0 else -0.16, 0)) for f in range(0, LOOP + 1, 30)], interp="BEZIER")

mark("mezz")
finish("backdrop_rich1", 2048, 14000, windows=WINDOWS, wall=(0.15, 0.06, 0.21))
