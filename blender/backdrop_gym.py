# Backdrop for the Hotel Electra gym: a night-owl fitness room.  Two heavy
# bags on a steel wall arm swing by the left windows (gloves and a jump rope
# hang between them); a mirror wall under the panoramic window with a
# two-tier hex dumbbell rack, kettlebells and medicine balls; a treadmill
# in front with its belt running and its console glowing; an adjustable
# bench; a black power rack with a loaded barbell and bumper plates; rubber
# floor tiles; up top the NO PAIN NO GAIN neon, BEAST MODE, and an interval
# timer counting with a blinking colon.
#   blender -b --python blender/backdrop_gym.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
WINDOWS = [(0.2, 7.6, 1.6, 1.3), (13.2, 7.6, 1.6, 1.3), (4.2, 4.6, 6.6, 2.2)]
THEME = dict(wall=(0.05, 0.09, 0.17), trim=(0.25, 1.0, 0.75), floor=(0.06, 0.10, 0.18))

# ------------------------------------------------------------ materials --
STEEL_BLK = M("paint", (0.03, 0.03, 0.035), rough=0.45, wear=0.9)
CHROME = M("chrome", (0.72, 0.74, 0.8))
KNURL = M("metal", (0.55, 0.56, 0.6), rough=0.45, bump=1.0)
IRON = M("paint", (0.05, 0.05, 0.06), rough=0.55, wear=0.7)
RUBBER = M("rubber", (0.025, 0.025, 0.03))
FLOOR = pattern("rubber", (0.05, 0.05, 0.06), "tiles", size=(1.0, 1.0), line=0.015, line_col=(0.01, 0.01, 0.012), plane="XY")
BAG = M("leather", (0.5, 0.04, 0.08), wear=0.7, grime=0.5)
BAG2 = M("leather", (0.04, 0.04, 0.05), wear=0.8)
STRAP = M("leather", (0.06, 0.05, 0.05))
GLOVE = M("leather", (0.6, 0.05, 0.1), rough=0.3)
MIRROR = M("chrome", (0.12, 0.15, 0.2), rough=0.03)
VINYL = M("leather", (0.04, 0.04, 0.05), rough=0.35)
PLATE_C = [M("rubber", c) for c in ((0.5, 0.04, 0.05), (0.04, 0.12, 0.5), (0.55, 0.45, 0.05), (0.05, 0.35, 0.1))]
KB = M("paint", (0.02, 0.02, 0.025), wear=0.9)
MED = [M("rubber", c) for c in ((0.45, 0.1, 0.02), (0.05, 0.25, 0.4), (0.3, 0.05, 0.35))]
PLASTIC = M("plastic", (0.08, 0.08, 0.09), rough=0.35)
TOWEL = M("fabric", (0.02, 0.4, 0.3))

SHEEN = glow((0.7, 0.85, 1.0), 0.35, base=(0.3, 0.33, 0.38))
MINT = glow((0.3, 1.0, 0.75), 4.0)
PINK = glow((1.0, 0.2, 0.6), 4.0)
ORANGE = glow((1.0, 0.45, 0.1), 4.0)
RED = glow((1.0, 0.08, 0.05), 5.0)
RED_DIM = glow((0.25, 0.02, 0.02), 1.0)
CONSOLE = screen((0.2, 0.7, 1.0), 1.1)

# --------------------------------------------------------- floor, trims --
box((15.0, 1.93, 0.03), (7.5, 0.965, 0.015), FLOOR)
moulding(0.0, 15.0, 0.0, [(0.0, 0.0), (0.05, 0.0), (0.05, 0.3), (0.0, 0.32)], RUBBER)

# ------------------------------------------------------- heavy bags --
tube_path([(0.2, WALL - 0.05, 7.05), (3.9, WALL - 0.05, 7.05)], 0.07, STEEL_BLK, verts=6)
for bx, m in ((1.2, BAG), (3.0, BAG2)):
    box((0.18, WALL - 0.75, 0.22), (bx, (WALL + 0.75) / 2, 7.05), STEEL_BLK, bev=0.02)
    box((0.35, 0.06, 0.5), (bx, WALL - 0.03, 7.05), STEEL_BLK, bev=0.02)
    p = pivot("bag_%d" % int(bx), (bx, 0.85, 6.95))
    torus(0.06, 0.015, (bx, 0.85, 6.9), CHROME, rot=(math.pi / 2, 0, 0), major_segments=8, minor_segments=4, parent=p)
    rod((bx, 0.85, 6.85), (bx, 0.85, 5.95), 0.02, CHROME, verts=5, parent=p)
    cyl(0.06, 0.12, (bx, 0.85, 5.9), CHROME, verts=8, bevel=0, parent=p)
    for k in range(4):
        a = k / 4 * math.tau + 0.4
        rod((bx, 0.85, 5.85), (bx + math.cos(a) * 0.4, 0.85 + math.sin(a) * 0.3, 5.15), 0.012, CHROME, verts=4, parent=p)
    lathe([(0.3, 0.0), (0.42, 0.05), (0.46, 0.3), (0.46, 2.9), (0.42, 3.05), (0.2, 3.1)], (bx, 0.85, 2.0), m,
          verts=16, parent=p)
    for zz in (2.4, 4.6):
        cyl(0.47, 0.12, (bx, 0.85, zz), STRAP, verts=16, bevel=0, parent=p)
    swing(p, "X", amp=0.035, phase=bx)
    swing(p, "Y", amp=0.05, phase=bx * 2.0)
# gloves and a jump rope on hooks between the bags
for dx in (-0.12, 0.18):
    ball(0.22, (2.1 + dx, WALL - 0.2, 4.4 - abs(dx)), GLOVE, scale=(0.9, 0.8, 1.2), seg=10, rings=6)
    cyl(0.15, 0.22, (2.1 + dx, WALL - 0.2, 4.05 - abs(dx)), M("fabric", (0.8, 0.8, 0.8)), verts=10, bevel=0)
rod((2.1, WALL, 4.75), (2.1, WALL - 0.25, 4.8), 0.02, CHROME, verts=4)
rope = pivot("jump_rope", (2.1, WALL - 0.12, 6.0))
rod((2.1, WALL - 0.02, 6.0), (2.1, WALL - 0.14, 6.02), 0.02, CHROME, verts=4)
tube_path(catenary((2.0, WALL - 0.12, 6.0), (2.2, WALL - 0.12, 6.0), 1.4, n=8), 0.015, M("plastic", (0.9, 0.2, 0.5)), verts=4, parent=rope)
for dx in (-0.12, 0.12):
    cyl(0.04, 0.35, (2.1 + dx, WALL - 0.12, 5.75), PLASTIC, verts=6, bevel=0, parent=rope)
swing(rope, "Y", amp=0.05, phase=0.5)

# ------------------------------------------ mirror wall and dumbbells --
MX0, MX1 = 4.0, 11.1
for k in range(4):
    w = (MX1 - MX0) / 4
    cx = MX0 + w * (k + 0.5)
    box((w - 0.04, 0.02, 3.9), (cx, WALL - 0.02, 2.45), MIRROR)
    box((0.05, 0.01, 2.2), (cx - 0.25, WALL - 0.035, 2.6), SHEEN, rot=(0, 0.45, 0))
    for zz in (0.5, 4.4):
        box((0.12, 0.04, 0.06), (MX0 + w * k + 0.02, WALL - 0.03, zz), CHROME)
box((MX1 - MX0, 0.05, 0.05), ((MX0 + MX1) / 2, WALL - 0.03, 4.42), CHROME)
box((MX1 - MX0, 0.05, 0.05), ((MX0 + MX1) / 2, WALL - 0.03, 0.48), CHROME)
# two-tier hex dumbbell rack along the wall under the bags
RX0, RX1 = 0.3, 3.85
for x in (RX0 + 0.1, (RX0 + RX1) / 2, RX1 - 0.1):
    for y in (1.3, 1.85):
        fbox((0.1, 0.1, 1.8 if y > 1.5 else 1.2), (x, y, 0.0), STEEL_BLK, bev=0.01)
for (y, z, tilt) in ((1.35, 1.05, 0.25), (1.75, 1.75, 0.25)):
    box((RX1 - RX0, 0.5, 0.06), ((RX0 + RX1) / 2, y, z), STEEL_BLK, rot=(tilt, 0, 0), bev=0.01)
n = 6
for tier, (y, z) in enumerate(((1.3, 1.25), (1.72, 1.95))):
    for i in range(n):
        x = RX0 + 0.35 + i * (RX1 - RX0 - 0.7) / (n - 1)
        r = 0.13 + 0.016 * i + tier * 0.03
        ln = 0.52
        for sgn in (-1, 1):
            cyl(r, 0.14 + 0.01 * i, (x + sgn * (ln / 2 - 0.02), y, z + r), IRON, rot=(0, math.pi / 2, 0), verts=6, bevel=0)
        rod((x - ln / 2, y, z + r), (x + ln / 2, y, z + r), 0.035, KNURL, verts=6)
# kettlebells in front of the rack, medicine balls by the bench
for i, x in enumerate((0.7, 1.45, 2.3, 3.2)):
    sc = 0.8 + i * 0.12
    ball(0.28 * sc, (x, 0.75, 0.28 * sc), KB, scale=(1, 1, 0.92), seg=10, rings=6)
    torus(0.15 * sc, 0.045 * sc, (x, 0.75, 0.52 * sc + 0.1), KB, rot=(math.pi / 2, 0, 0), major_segments=10, minor_segments=4)
for i, x in enumerate((11.0, 10.2)):
    ball(0.36, (x, 1.45 - i * 0.2, 0.36), MED[i], seg=12, rings=8)
    torus(0.36, 0.02, (x, 1.45 - i * 0.2, 0.36), M("rubber", (0.6, 0.55, 0.1)), rot=(math.pi / 2, 0, 0.3), major_segments=12, minor_segments=3)

# ------------------------------------------------------------ treadmill --
TX0, TX1, TY = 4.2, 7.9, 0.8     # deck from TX0 (back end) to TX1 (motor hood)
box((TX1 - TX0, 0.9, 0.32), ((TX0 + TX1) / 2, TY + 0.1, 0.3), STEEL_BLK, bev=0.04)
box((TX1 - TX0 - 0.7, 0.8, 0.06), ((TX0 + TX1) / 2 - 0.2, TY + 0.1, 0.47), RUBBER)
for x in (TX0 + 0.15, TX1 - 0.3):
    box((0.25, 0.9, 0.12), (x, TY + 0.1, 0.06), RUBBER, bev=0.02)
fbox((0.8, 0.95, 0.55), (TX1 - 0.25, TY + 0.1, 0.18), M("plastic", (0.08, 0.08, 0.09), rough=0.3), bev=0.08, seg=2)
cyl(0.1, 0.95, (TX0 + 0.05, TY + 0.1, 0.36), CHROME, rot=(math.pi / 2, 0, 0), verts=10, bevel=0)
box((TX1 - TX0 - 0.7, 0.02, 0.03), ((TX0 + TX1) / 2 - 0.2, TY - 0.36, 0.2), MINT)
belt = pivot("belt", ((TX0 + TX1) / 2, TY - 0.35, 0.4))
pitch = 0.3
for k in range(int((TX1 - TX0 - 0.9) / pitch)):
    x = TX0 + 0.2 + k * pitch
    box((0.08, 0.04, 0.07), (x, TY - 0.33, 0.43), M("rubber", (0.12, 0.12, 0.13)), parent=belt)
    box((0.06, 0.78, 0.015), (x, TY + 0.1, 0.505), M("rubber", (0.1, 0.1, 0.11)), parent=belt)
slide_loop(belt, "X", -pitch, cycles=8)
# uprights, handrails and the console
for y in (TY - 0.35, TY + 0.55):
    tube_path([(TX1 - 0.3, y, 0.5), (TX1 - 0.55, y, 2.4), (TX1 - 0.6, y, 3.1)], 0.07, STEEL_BLK, verts=8)
    tube_path([(TX1 - 0.6, y, 2.35), (TX1 - 1.6, y, 2.35), (TX1 - 1.7, y, 2.2)], 0.05, RUBBER, verts=6)
box((1.1, 1.05, 0.5), (TX1 - 0.62, TY + 0.1, 3.25), M("plastic", (0.08, 0.08, 0.09), rough=0.3), rot=(0, 0.35, 0), bev=0.06, seg=2)
box((0.75, 0.02, 0.32), (TX1 - 0.72, TY - 0.45, 3.32), CONSOLE, rot=(0, 0.35, 0))
for k in range(3):
    box((0.1, 0.02, 0.05), (TX1 - 0.95 + k * 0.18, TY - 0.46, 3.06 + k * 0.065), [MINT, PINK, ORANGE][k], rot=(0, 0.35, 0))
twl = pivot("treadmill_towel", (TX1 - 1.2, TY - 0.38, 2.4))
box((0.45, 0.05, 0.9), (TX1 - 1.2, TY - 0.4, 2.0), TOWEL, bev=0.02, parent=twl)
swing(twl, "X", amp=0.08, cycles=2)

# ------------------------------------------------------------- bench --
BX = 10.1
box((1.9, 0.45, 0.14), (BX, 0.7, 1.12), VINYL, bev=0.05, seg=2, rot=(0, 0.12, 0))
box((0.9, 0.45, 0.14), (BX - 1.25, 0.7, 1.4), VINYL, bev=0.05, seg=2, rot=(0, 0.55, 0))
box((1.9, 0.2, 0.12), (BX, 0.7, 0.95), STEEL_BLK, bev=0.02, rot=(0, 0.12, 0))
for x, h in ((BX - 0.8, 1.0), (BX + 0.85, 0.85)):
    fbox((0.1, 0.1, h), (x, 0.7, 0.0), STEEL_BLK)
    box((0.1, 0.9, 0.08), (x, 0.7, 0.04), STEEL_BLK, bev=0.02)
cyl(0.1, 0.12, (BX + 0.85, 0.3, 0.1), RUBBER, rot=(0, math.pi / 2, 0), verts=10, bevel=0)

# ------------------------------------------------------------ power rack --
PX0, PX1 = 11.5, 14.4
for x in (PX0, PX1):
    for y in (0.35, 1.8):
        fbox((0.14, 0.14, 5.6), (x, y, 0.0), STEEL_BLK, bev=0.01)
        for k in range(18):
            box((0.05, 0.02, 0.05), (x, y - 0.075, 1.0 + k * 0.22), RUBBER)
    box((0.14, 1.6, 0.14), (x, 1.07, 5.55), STEEL_BLK, bev=0.01)
    box((0.14, 1.6, 0.14), (x, 1.07, 0.07), STEEL_BLK, bev=0.01)
for y in (0.35, 1.8):
    box((PX1 - PX0, 0.14, 0.14), ((PX0 + PX1) / 2, y, 5.55), STEEL_BLK, bev=0.01)
rod((PX0 - 0.1, 0.25, 5.35), (PX1 + 0.1, 0.25, 5.35), 0.05, KNURL, verts=8)          # pull-up bar
for x in (PX0, PX1):
    box((0.14, 0.9, 0.08), (x, 0.9, 1.6), CHROME)                               # safety arms
    box((0.2, 0.25, 0.2), (x, 0.25, 3.05), STEEL_BLK, bev=0.02)                  # J-hooks
# loaded barbell on the hooks
BZ = 3.2
rod((PX0 - 0.95, 0.25, BZ), (PX1 + 0.95, 0.25, BZ), 0.05, KNURL, verts=8)
for s in (-1, 1):
    xe = (PX0 if s < 0 else PX1) + s * 0.3
    for k, (r, m) in enumerate(((0.56, PLATE_C[0]), (0.56, PLATE_C[1]), (0.42, PLATE_C[2]))):
        cyl(r, 0.14, (xe + s * (k * 0.16), 0.25, BZ), m, rot=(0, math.pi / 2, 0), verts=20, bevel=0.02)
        cyl(0.12, 0.15, (xe + s * (k * 0.16), 0.25, BZ), CHROME, rot=(0, math.pi / 2, 0), verts=10, bevel=0)
    cyl(0.1, 0.12, (xe + s * 0.5, 0.25, BZ), CHROME, rot=(0, math.pi / 2, 0), verts=10, bevel=0)   # collar
# plate storage pegs on the back uprights
for x in (PX0 + 0.3, PX1 - 0.3):
    for k, (z, r, m) in enumerate(((0.62, 0.56, PLATE_C[3]), (0.62, 0.42, PLATE_C[2]), (0.62, 0.3, PLATE_C[1]))):
        cyl(r, 0.12, (x, 1.6 - k * 0.14, z), m, rot=(math.pi / 2, 0, 0), verts=20, bevel=0.02)
    rod((x, 1.8, 0.62), (x, 1.15, 0.62), 0.05, CHROME, verts=6)

# ------------------------------------------------------------ upper wall --
w = neon_text("NO PAIN NO GAIN", 3.35, 7.75, 0.62, PINK, flicker_idx=(5,), seed=17, aspect=0.55, gap=0.26)
tube_path([(3.35, WALL - 0.06, 7.55), (3.35 + w, WALL - 0.06, 7.55)], 0.025, MINT, verts=6, cap=False)
for i in range(3):
    tube_path([(3.35 + w * 0.05 + i * 0.3, WALL - 0.06, 8.65), (3.35 + w * 0.05 + i * 0.3 + 0.2, WALL - 0.06, 8.85)], 0.025, MINT, verts=5, cap=False)
    tube_path([(3.35 + w * 0.95 - i * 0.3, WALL - 0.06, 8.65), (3.35 + w * 0.95 - i * 0.3 - 0.2, WALL - 0.06, 8.85)], 0.025, MINT, verts=5, cap=False)
# BEAST MODE on a dark board above the rack
box((3.0, 0.05, 0.75), (12.95, WALL - 0.025, 6.55), M("paint", (0.02, 0.02, 0.03)), bev=0.02)
neon_text("BEAST MODE", 11.62, 6.37, 0.36, ORANGE, flicker_idx=(3,), seed=29, aspect=0.55, gap=0.25, r=0.02)
# interval timer: red digits and a blinking colon
TXC, TZC = 12.2, 8.3
box((1.9, 0.18, 0.8), (TXC, WALL - 0.09, TZC), M("paint", (0.03, 0.03, 0.035)), bev=0.03)
box((1.7, 0.02, 0.55), (TXC, WALL - 0.19, TZC), RED_DIM)
for k, dx in enumerate((-0.6, -0.3, 0.3, 0.6)):
    neon_text("0145"[k], TXC + dx - 0.1, TZC - 0.2, 0.4, RED, y=WALL - 0.2, r=0.018, aspect=0.5)
col = pivot("timer_colon", (TXC, WALL - 0.2, TZC))
for dz in (-0.1, 0.1):
    box((0.06, 0.02, 0.06), (TXC, WALL - 0.2, TZC + dz), RED, parent=col)
blink(col, [(15, 30), (45, 60), (75, 90), (105, 120)])
for k in range(2):
    box((0.12, 0.02, 0.06), (TXC - 0.7 + k * 1.4, WALL - 0.2, TZC + 0.33), [MINT, PINK][k])
# a wall speaker on each side of the neon
for x in (2.7, 11.0):
    box((0.45, 0.35, 0.65), (x, WALL - 0.2, 8.6), PLASTIC, bev=0.05)
    cyl(0.15, 0.02, (x, WALL - 0.38, 8.5), RUBBER, rot=(math.pi / 2, 0, 0), verts=12, bevel=0)
    cyl(0.07, 0.02, (x, WALL - 0.38, 8.78), RUBBER, rot=(math.pi / 2, 0, 0), verts=10, bevel=0)

finish("backdrop_gym", windows=WINDOWS, theme=THEME)
