# Backdrop for the arcade, Neon Palace: a blacklight carpet glowing with
# confetti, a row of six classic upright cabinets (anim screens with pixel
# sprites, chasing marquees, neon T-moulding, glowing coin doors) under a
# jumbotron where invaders march and a chomper crosses; a claw machine
# whose claw travels, drops and lifts over a pile of plush; an air-hockey
# table with a bouncing puck and mallets; a prize counter with glass cases
# and shelves of giant plush under a "PRIZES" neon; "INSERT COIN" and "GAME
# OVER" blinking.  Up top: a bulb-framed "ARCADE" sign and a high-score
# board.  15 m wide.
#   blender -b --python blender/backdrop_arcade.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
WINDOWS = [(0.5, 5.6, 3.2, 1.6), (10.3, 5.6, 3.8, 1.6), (4.6, 6.0, 5.4, 1.3)]
BULBS = anim_neon((1.0, 0.8, 0.4), "marquee", 3.0)
WALLPAINT = pbr("paint", (0.05, 0.02, 0.12), rough=0.6, wear=0.2, name="arcade_wall")
PANEL_BLACK = pbr("plastic", (0.02, 0.02, 0.03), rough=0.35, name="cab_black")
CAB_COLOURS = [pbr("plastic", c, rough=0.3, name=n) for c, n in (((0.6, 0.03, 0.25), "cab_pink"), ((0.02, 0.15, 0.5), "cab_blue"),
                                                                 ((0.35, 0.06, 0.6), "cab_violet"), ((0.02, 0.35, 0.3), "cab_teal"),
                                                                 ((0.7, 0.3, 0.02), "cab_orange"), ((0.5, 0.02, 0.03), "cab_red"))]
NEONS = ["pink", "cyan", "violet", "mint", "orange", "red"]

INVADER = ["00100000100", "00010001000", "00111111100", "01101110110", "11111111111", "10111111101", "10100000101", "00011011000"]
GHOST = ["0011100", "0111110", "1101011", "1111111", "1111111", "1010101"]
CHOMP = ["0011100", "0111110", "1111000", "1110000", "1111000", "0111110", "0011100"]


def sprite(rows, x, z, y, px, m):
    """Pixel art as camera-facing squares, centred at (x, z)."""
    h, w = len(rows), len(rows[0])
    pts = [(x + (c - w / 2 + 0.5) * px, z + (h / 2 - r - 0.5) * px) for r, row in enumerate(rows) for c, ch in enumerate(row) if ch == "1"]
    return quad_dots(pts, y, px * 0.9, m)


# ------------------------------------------------------------ architecture --
slab_at(0.0, 15.0, 0.0, WALL, 0.0, 0.02, M.carpet_navy)
rnd = rng(3)
conf = [neon_mat(c, 1.4, "confetti") for c in ((1.0, 0.2, 0.7), (0.2, 0.9, 1.0), (1.0, 0.85, 0.2), (0.5, 0.3, 1.0))]
for k in range(4):
    pts = [(0.2 + rnd() * 14.6, 0.1 + rnd() * 1.75) for _ in range(40)]
    flat_dots(pts, 0.022, 0.07, conf[k])
wall_cover(WINDOWS, 0.0, 9.3, WALLPAINT)
# a chevron dado and a neon skirting
tube([(0.05, WALL - 0.05, 0.06), (14.95, WALL - 0.05, 0.06)], 0.02, M.n_violet, verts=4)
tube([(0.05, WALL - 0.05, 5.5), (14.95, WALL - 0.05, 5.5)], 0.02, M.n_pink, verts=4)

# ---------------------------------------------------------------- cabinets --
PROFILE = [(0.0, 0.0), (0.72, 0.0), (0.72, 1.95), (0.16, 1.95), (0.08, 1.9), (0.08, 1.7), (0.16, 1.68), (0.3, 1.22), (0.06, 1.05),
           (0.0, 1.0)]


def cabinet(x, k, y=1.12, w=0.68):
    col = CAB_COLOURS[k % len(CAB_COLOURS)]
    edge = getattr(M, "n_" + NEONS[k % len(NEONS)])
    prism([(y + a, b) for a, b in PROFILE], x - w / 2, x - w / 2 + 0.03, col, plane="yz")          # side art panels
    prism([(y + a, b) for a, b in PROFILE], x + w / 2 - 0.03, x + w / 2, col, plane="yz")
    prism([(y + a + 0.02, b) for a, b in PROFILE[:3]] + [(y + 0.18, 1.95), (y + 0.1, 1.9), (y + 0.1, 1.7), (y + 0.18, 1.68), (y + 0.32, 1.22),
                                                         (y + 0.08, 1.05), (y + 0.02, 1.0)], x - w / 2 + 0.03, x + w / 2 - 0.03, PANEL_BLACK, plane="yz")
    for sx in (-1, 1):                                                                           # neon T-moulding
        tube([(x + sx * (w / 2 + 0.005), y + a, b) for a, b in PROFILE[3:] + [PROFILE[0]]], 0.012, edge, verts=4)
    # coin door with glowing slots
    slab_at(x - 0.17, x + 0.17, y - 0.02, y + 0.02, 0.35, 0.8, M.steel)
    for sx in (-0.07, 0.07):
        box((0.03, 0.02, 0.06), (x + sx, y - 0.025, 0.65), M.n_red)
    box((0.1, 0.02, 0.03), (x, y - 0.025, 0.45), M.black_metal)
    # control panel: joystick and buttons on the slanted deck
    prism([(y - 0.12, 0.95), (y + 0.06, 0.95), (y + 0.06, 1.08), (y - 0.1, 1.02)], x - w / 2 + 0.01, x + w / 2 - 0.01, col, plane="yz")
    tube([(x - 0.15, y - 0.04, 1.04), (x - 0.15, y - 0.04, 1.14)], 0.008, M.chrome, verts=4)
    ico(0.03, (x - 0.15, y - 0.04, 1.15), [M.plastic_red, M.plastic_yellow, M.plastic_cyan][k % 3], subdiv=1)
    for j in range(3):
        box((0.035, 0.035, 0.02), (x + 0.0 + j * 0.07, y - 0.03, 1.04 + j * 0.005), [M.n_red, M.n_amber, M.n_cyan][(j + k) % 3])
    # screen on the slanted face, with sprites
    z0, z1 = 1.25, 1.66
    tilt = math.atan2(0.14, 0.46)
    cy = y + 0.23
    box((w - 0.12, 0.02, 0.44), (x, cy - 0.005, 1.45), PANEL_BLACK, rot=(-tilt, 0, 0))
    box((w - 0.18, 0.02, 0.36), (x, cy - 0.015, 1.45), anim_neon([(0.1, 0.2, 0.6), (0.3, 0.05, 0.25), (0.05, 0.25, 0.2)][k % 3], "screen", 1.0),
        rot=(-tilt, 0, 0))
    art = [INVADER, GHOST, CHOMP][k % 3]
    sprite(art, x, 1.45, cy - 0.06, 0.026, [M.n_green, M.n_cyan, M.n_amber][k % 3])
    # marquee lightbox
    box((w - 0.08, 0.02, 0.18), (x, y + 0.075, 1.8), anim_neon(NEONS[k % len(NEONS)], "marquee", 2.2))
    box((w, 0.08, 0.03), (x, y + 0.12, 1.955), col)


for k in range(6):
    cabinet(0.62 + k * 0.78, k)
# "INSERT COIN" blinking over the cabinets
ic = pivot("blink_insert", (2.6, WALL - 0.08, 2.35))
neon_text("INSERT COIN", 2.6, 2.2, WALL - 0.08, 0.3, M.n_amber, r=0.016, align="center", verts=4, parent=ic)
merge_children(ic, "blink_insert_mesh")
blink(ic, "1111000011110000")

# ----------------------------------------------------- jumbotron over them --
JX, JZ, JW, JH = 2.6, 4.0, 4.7, 2.4
slab_at(JX - JW / 2 - 0.1, JX + JW / 2 + 0.1, WALL - 0.12, WALL, JZ - JH / 2 - 0.1, JZ + JH / 2 + 0.1, M.black_metal)
box((JW, 0.02, JH), (JX, WALL - 0.13, JZ), anim_neon((0.08, 0.05, 0.3), "screen", 1.0))
quad_dots(rect_pts(JX - JW / 2 - 0.05, JX + JW / 2 + 0.05, JZ - JH / 2 - 0.05, JZ + JH / 2 + 0.05, 0.15), WALL - 0.13, 0.05, BULBS)
inv = pivot("invaders", (JX, WALL - 0.15, JZ + 0.6))
for r in range(2):
    for c in range(5):
        o = sprite(INVADER, JX - 1.6 + c * 0.8, JZ + 0.9 - r * 0.55, WALL - 0.15, 0.04, [M.n_green, M.n_magenta][r])
        attach(o, inv)
merge_children(inv, "invaders_mesh")
key(inv, "idle", "location", [(0, (JX - 0.35, WALL - 0.15, JZ + 0.6)), (30, (JX + 0.35, WALL - 0.15, JZ + 0.6)), (31, (JX + 0.35, WALL - 0.15, JZ + 0.5)),
                              (60, (JX - 0.35, WALL - 0.15, JZ + 0.5)), (61, (JX - 0.35, WALL - 0.15, JZ + 0.4)), (90, (JX + 0.35, WALL - 0.15, JZ + 0.4)),
                              (91, (JX + 0.35, WALL - 0.15, JZ + 0.5)), (LOOP, (JX - 0.35, WALL - 0.15, JZ + 0.6))], interp="LINEAR")
ship = pivot("ship", (JX, WALL - 0.15, JZ - 0.95))
attach(sprite(["0001000", "0011100", "1111111", "1111111"], JX, JZ - 0.95, WALL - 0.15, 0.05, M.n_cyan), ship)
key(ship, "idle", "location", [(0, (JX - 1.6, WALL - 0.15, JZ - 0.95)), (60, (JX + 1.6, WALL - 0.15, JZ - 0.95)), (LOOP, (JX - 1.6, WALL - 0.15, JZ - 0.95))], interp="BEZIER")
chomp = pivot("chomper", (JX - 2.1, WALL - 0.15, JZ - 0.35))
attach(sprite(CHOMP, JX - 2.1, JZ - 0.35, WALL - 0.15, 0.05, M.n_amber), chomp)
for i in range(8):
    quad_dots([(JX - 1.8 + i * 0.5, JZ - 0.35)], WALL - 0.14, 0.05, M.n_white)
key(chomp, "idle", "location", [(0, (JX - 2.1, WALL - 0.15, JZ - 0.35)), (LOOP, (JX + 2.1, WALL - 0.15, JZ - 0.35))], interp="LINEAR")
key(chomp, "idle", "scale", [(LOOP * k / 16, (1.0, 1.0, 1.0 if k % 2 else 0.75)) for k in range(17)], interp="CONSTANT")

# ------------------------------------------------------------ air hockey --
HX, HY = 6.55, 0.55
slab_at(HX - 1.05, HX + 1.05, HY - 0.4, HY + 0.4, 0.0, 0.1, M.black_metal)
slab_at(HX - 1.0, HX + 1.0, HY - 0.36, HY + 0.36, 0.1, 0.72, CAB_COLOURS[1])
box((1.9, 0.02, 0.05), (HX, HY - 0.37, 0.6), anim_neon("cyan", "marquee", 2.5))
box((1.9, 0.02, 0.05), (HX, HY - 0.37, 0.2), anim_neon("pink", "marquee", 2.5))
slab_at(HX - 1.02, HX + 1.02, HY - 0.38, HY + 0.38, 0.72, 0.76, M.lacquer_white)
for sy in (-1, 1):
    tube([(HX - 1.02, HY + sy * 0.38, 0.79), (HX + 1.02, HY + sy * 0.38, 0.79)], 0.03, M.n_cyan if sy < 0 else M.n_pink, verts=4)
for sx in (-1, 1):
    tube([(HX + sx * 1.02, HY - 0.38, 0.79), (HX + sx * 1.02, HY - 0.12, 0.79)], 0.03, M.n_violet, verts=4)
    tube([(HX + sx * 1.02, HY + 0.12, 0.79), (HX + sx * 1.02, HY + 0.38, 0.79)], 0.03, M.n_violet, verts=4)
box((0.01, 0.7, 0.002), (HX, HY, 0.762), M.n_pink)
torus(0.16, 0.006, (HX, HY, 0.762), M.n_pink, major_segments=14, minor_segments=3)
puck = pivot("puck", (HX, HY, 0.77))
lathe([(0.04, 0), (0.04, 0.015), (0.0, 0.015)], (HX, HY, 0.763), PANEL_BLACK, segs=10, parent=puck)
path = [(HX - 0.8, HY - 0.2), (HX - 0.2, HY + 0.3), (HX + 0.5, HY - 0.3), (HX + 0.85, HY + 0.1), (HX + 0.2, HY + 0.3), (HX - 0.5, HY - 0.25)]
key(puck, "idle", "location", [(LOOP * i / len(path), (px, py, 0.77)) for i, (px, py) in enumerate(path)] + [(LOOP, (path[0][0], path[0][1], 0.77))], interp="LINEAR")
for sx, m in ((-1, M.plastic_red), (1, M.plastic_cyan)):
    mp = pivot("mallet_%s" % ("l" if sx < 0 else "r"), (HX + sx * 0.8, HY, 0.77))
    lathe([(0.07, 0), (0.07, 0.03), (0.03, 0.04), (0.025, 0.1), (0.035, 0.12), (0.0, 0.13)], (HX + sx * 0.8, HY, 0.763), m, segs=10, parent=mp)
    merge_children(mp, mp.name + "_mesh")
    ks = []
    for i, (px, py) in enumerate(path):
        near = (px - HX) * sx > 0.3
        ks.append((LOOP * i / len(path), (HX + sx * (0.95 if not near else abs(px - HX) + 0.12), py if near else HY + (py - HY) * 0.4, 0.77)))
    ks.append((LOOP, ks[0][1]))
    key(mp, "idle", "location", ks, interp="BEZIER")
# a scoreboard on a post
tube([(HX, HY + 0.4, 0.1), (HX, HY + 0.4, 1.45)], 0.03, M.chrome, verts=6)
slab_at(HX - 0.4, HX + 0.4, HY + 0.34, HY + 0.46, 1.45, 1.75, PANEL_BLACK)
neon_text("7", HX - 0.25, 1.5, HY + 0.33, 0.2, M.n_red, r=0.012, verts=4)
neon_text("5", HX + 0.15, 1.5, HY + 0.33, 0.2, M.n_cyan, r=0.012, verts=4)

# ----------------------------------------------------------- claw machine --
KX, KY = 8.55, 0.9
PLUSH = [M.plush_pink, M.plush_blue, M.plush_yellow, M.plush_white, M.plush_lilac, M.plush_brown]
slab_at(KX - 0.6, KX + 0.6, KY - 0.45, KY + 0.45, 0.0, 0.85, M.lacquer_plum)
box((1.1, 0.02, 0.05), (KX, KY - 0.46, 0.8), anim_neon("pink", "marquee", 2.5))
slab_at(KX + 0.2, KX + 0.5, KY - 0.47, KY - 0.44, 0.15, 0.55, M.black_metal)                   # prize flap
slab_at(KX - 0.45, KX - 0.05, KY - 0.5, KY - 0.4, 0.8, 0.88, M.plastic_black)                   # control deck
tube([(KX - 0.35, KY - 0.46, 0.88), (KX - 0.35, KY - 0.46, 0.98)], 0.008, M.chrome, verts=4)
ico(0.03, (KX - 0.35, KY - 0.46, 1.0), M.plastic_red, subdiv=1)
box((0.05, 0.05, 0.02), (KX - 0.17, KY - 0.46, 0.89), M.n_green)
for (a, b) in ((KX - 0.6, KY - 0.45), (KX + 0.6, KY - 0.45), (KX - 0.6, KY + 0.45), (KX + 0.6, KY + 0.45)):
    slab_at(a - 0.03, a + 0.03, b - 0.03, b + 0.03, 0.85, 2.0, M.chrome)
box((1.2, 0.02, 1.15), (KX, KY - 0.45, 1.43), M.glass)
box((0.02, 0.9, 1.15), (KX - 0.6, KY, 1.43), M.glass)
box((0.02, 0.9, 1.15), (KX + 0.6, KY, 1.43), M.glass)
slab_at(KX - 0.58, KX + 0.58, KY + 0.4, KY + 0.44, 0.85, 2.0, anim_neon((0.5, 0.2, 0.9), "screen", 0.9))
slab_at(KX + 0.2, KX + 0.55, KY - 0.42, KY - 0.1, 0.85, 1.1, M.glass)                          # chute
rnd = rng(12)
for i in range(16):
    px = KX - 0.5 + rnd() * 0.65
    py = KY - 0.3 + rnd() * 0.65
    pz = 0.95 + rnd() * 0.18 + (0.08 if abs(px - KX + 0.15) < 0.25 else 0.0)
    o = ico(0.07 + rnd() * 0.03, (px, py, pz), PLUSH[i % len(PLUSH)], subdiv=1)
    quad_dots([(px - 0.02, pz + 0.03), (px + 0.02, pz + 0.03)], py - 0.09, 0.02, M.plastic_black)
slab_at(KX - 0.62, KX + 0.62, KY - 0.47, KY + 0.47, 2.0, 2.38, M.lacquer_plum)
quad_dots(rect_pts(KX - 0.58, KX + 0.58, 2.04, 2.34, 0.1), KY - 0.48, 0.045, BULBS)
neon_text("CLAW", KX, 2.12, KY - 0.49, 0.16, M.n_cyan, r=0.012, align="center", verts=4)
tube([(KX - 0.55, KY - 0.2, 1.95), (KX + 0.55, KY - 0.2, 1.95)], 0.012, M.chrome, verts=4)
tube([(KX - 0.55, KY + 0.2, 1.95), (KX + 0.55, KY + 0.2, 1.95)], 0.012, M.chrome, verts=4)
cx = pivot("claw_carriage", (KX, KY, 1.93))
slab_at(KX - 0.07, KX + 0.07, KY - 0.25, KY + 0.25, 1.92, 1.96, M.steel, parent=cx)
merge_children(cx, "claw_carriage_mesh")
cable = pivot("claw_cable", (KX, KY, 1.92), parent=cx)
tube([(KX, KY, 1.92), (KX, KY, 1.62)], 0.005, M.steel, verts=3, parent=cable)
claw = pivot("claw", (KX, KY, 1.6), parent=cx)
lathe([(0.0, 0.0), (0.05, 0.0), (0.05, 0.05), (0.0, 0.06)], (KX, KY, 1.58), M.chrome, segs=8, parent=claw)
for a in range(3):
    ang = TAU * a / 3
    tube([(KX + math.cos(ang) * 0.04, KY + math.sin(ang) * 0.04, 1.58), (KX + math.cos(ang) * 0.1, KY + math.sin(ang) * 0.1, 1.5),
          (KX + math.cos(ang) * 0.06, KY + math.sin(ang) * 0.06, 1.42)], 0.008, M.chrome, verts=4, parent=claw)
merge_children(claw, "claw_mesh")
# travel: right-back, drop, grab, lift, return to the chute, open
T = [(0, (KX + 0.35, KY + 0.1)), (25, (KX - 0.2, KY + 0.15)), (65, (KX - 0.2, KY + 0.15)), (95, (KX + 0.35, KY - 0.25)), (LOOP, (KX + 0.35, KY + 0.1))]
key(cx, "idle", "location", [(f, (px, py, 1.93)) for f, (px, py) in T], interp="BEZIER")
drop = [(0, 0.0), (28, 0.0), (40, -0.45), (48, -0.45), (60, 0.0), (LOOP, 0.0)]
key(claw, "idle", "location", [(f, (KX, KY, 1.6 + d)) for f, d in drop], interp="BEZIER")
key(cable, "idle", "scale", [(f, (1, 1, 1.0 - d / 0.3)) for f, d in drop], interp="BEZIER")

# ----------------------------------------------------------- prize counter --
PX0, PX1 = 10.2, 14.85
slab_at(PX0, PX1, WALL - 0.03, WALL, 0.3, 2.85, anim_neon((0.45, 0.1, 0.5), "screen", 0.8))
for sx in (PX0, PX1):
    slab_at(sx - 0.05, sx + 0.05, 1.45, WALL, 0.0, 2.9, M.black_metal)
slab_at(PX0 - 0.05, PX1 + 0.05, 1.45, WALL, 2.85, 2.92, M.black_metal)
slab_at(PX0, PX1, 1.45, WALL, 0.0, 0.3, M.black_metal)
for sz in (0.95, 1.9):
    slab_at(PX0 + 0.05, PX1 - 0.05, 1.5, WALL, sz, sz + 0.04, M.lacquer_white)
    tube([(PX0 + 0.05, 1.5, sz + 0.02), (PX1 - 0.05, 1.5, sz + 0.02)], 0.012, M.n_pink, verts=4)


k = 0
for sz, n, s in ((0.99, 6, 1.2), (1.94, 5, 1.45)):
    for i in range(n):
        plush(PX0 + 0.45 + i * (PX1 - PX0 - 0.9) / (n - 1), 1.7, sz, s, PLUSH[k % len(PLUSH)], k % 3)
        k += 1
plush(PX0 + 0.5, 1.7, 2.9, 1.9, M.plush_pink, 0)
plush(PX1 - 0.5, 1.7, 2.9, 1.9, M.plush_blue, 1)
# glass display counter with small prizes
slab_at(PX0 + 0.1, PX1 - 0.1, 0.55, 1.2, 0.0, 0.5, M.lacquer_plum)
box((PX1 - PX0 - 0.2, 0.02, 0.04), ((PX0 + PX1) / 2, 0.54, 0.45), anim_neon("violet", "marquee", 2.5))
box((PX1 - PX0 - 0.2, 0.65, 0.02), ((PX0 + PX1) / 2, 0.875, 0.5), M.lacquer_white)
box((PX1 - PX0 - 0.2, 0.02, 0.45), ((PX0 + PX1) / 2, 0.56, 0.74), M.glass)
box((PX1 - PX0 - 0.2, 0.65, 0.02), ((PX0 + PX1) / 2, 0.875, 0.97), M.glass)
for i in range(9):
    px = PX0 + 0.35 + i * 0.47
    [lambda: ico(0.07, (px, 0.85, 0.58), PLUSH[i % 6], subdiv=1),
     lambda: slab_at(px - 0.06, px + 0.06, 0.8, 0.9, 0.51, 0.66, CAB_COLOURS[i % 6]),
     lambda: lathe([(0.05, 0), (0.05, 0.14), (0.0, 0.16)], (px, 0.85, 0.51), [M.n_pink, M.n_cyan, M.n_amber][i % 3], segs=6)][i % 3]()
slab_at(PX0 + 0.3, PX0 + 0.8, 0.8, 1.1, 0.99, 1.25, M.steel)                                   # ticket counter
box((0.3, 0.02, 0.1), (PX0 + 0.55, 0.79, 1.15), anim_neon("red", "screen", 1.5))
sign_board((PX0 + PX1) / 2, 3.35, WALL - 0.06, 3.0, 0.72, M.black_metal, M.gold)
neon_text("PRIZES", (PX0 + PX1) / 2, 3.1, WALL - 0.1, 0.5, anim_neon("pink", "marquee", 3.5), r=0.025, align="center", verts=4)
# token changer between the claw and the prizes
slab_at(9.45, 9.95, 1.3, 1.8, 0.0, 1.7, M.steel)
box((0.34, 0.02, 0.22), (9.7, 1.29, 1.35), anim_neon("green", "screen", 1.4))
box((0.2, 0.02, 0.06), (9.7, 1.29, 1.0), M.n_amber)
slab_at(9.55, 9.85, 1.25, 1.3, 0.55, 0.7, M.chrome)

# ------------------------------------------- neon joystick art mid-wall --
JSX, JSZ = 7.3, 3.4
tube([(JSX + math.cos(a) * 0.75, WALL - 0.05, JSZ + math.sin(a) * 0.22) for a in [TAU * i / 20 for i in range(21)]], 0.03, M.n_violet, verts=4)
tube([(JSX, WALL - 0.05, JSZ + 0.05), (JSX + 0.25, WALL - 0.05, JSZ + 1.0)], 0.05, M.n_cyan, verts=4)
tube([(JSX + 0.25 + math.cos(a) * 0.22, WALL - 0.05, JSZ + 1.15 + math.sin(a) * 0.22) for a in [TAU * i / 16 for i in range(17)]], 0.035, M.n_pink, verts=4)
for i, m in enumerate((M.n_red, M.n_amber, M.n_mint)):
    bx = JSX + 1.2 + i * 0.5
    tube([(bx + math.cos(a) * 0.17, WALL - 0.05, JSZ + 0.2 + math.sin(a) * 0.17) for a in [TAU * j / 12 for j in range(13)]], 0.03, m, verts=4)
ps = pivot("blink_start", (JSX + 0.6, WALL - 0.08, 2.55))
neon_text("PUSH START", JSX + 0.6, 2.45, WALL - 0.06, 0.28, M.n_cyan, r=0.015, align="center", verts=3, parent=ps)
merge_children(ps, "blink_start_mesh")
blink(ps, "0000111100001111")
for i in range(7):
    a = -0.9 + i * 0.3
    tube([(JSX + 0.25 + math.cos(a + 1.57) * 0.35, WALL - 0.05, JSZ + 1.15 + math.sin(a + 1.57) * 0.35),
          (JSX + 0.25 + math.cos(a + 1.57) * 0.55, WALL - 0.05, JSZ + 1.15 + math.sin(a + 1.57) * 0.55)], 0.02, M.n_amber, verts=4)

# ------------------------------------------------------------ upper band --
sign_board(7.3, 8.25, WALL - 0.08, 5.2, 1.5, M.black_metal, M.chrome)
neon_text("ARCADE", 7.3, 7.75, WALL - 0.12, 0.95, anim_neon("cyan", "marquee", 3.5), r=0.042, align="center", verts=4)
quad_dots(rect_pts(4.8, 9.8, 7.6, 8.9, 0.16), WALL - 0.12, 0.07, BULBS)
go = pivot("blink_gameover", (12.2, WALL - 0.08, 8.0))
neon_text("GAME OVER", 12.2, 7.85, WALL - 0.08, 0.36, M.n_red, r=0.018, align="center", verts=4, parent=go)
merge_children(go, "blink_gameover_mesh")
blink(go, "1111111100110011")
slab_at(0.4, 3.9, WALL - 0.06, WALL, 7.45, 9.05, M.black_metal)
box((3.3, 0.02, 1.45), (2.15, WALL - 0.07, 8.25), anim_neon((0.05, 0.1, 0.25), "screen", 1.0))
neon_text("HI SCORE", 2.15, 8.7, WALL - 0.09, 0.22, M.n_amber, r=0.011, align="center", verts=4)
for r in range(3):
    neon_text("%d" % (9990 - r * 1357), 1.3, 8.35 - r * 0.24, WALL - 0.09, 0.14, [M.n_cyan, M.n_pink, M.n_green, M.n_violet][r], r=0.008, verts=3)
    neon_text(["ACE", "ZAP", "NEO", "BOB"][r], 2.6, 8.35 - r * 0.24, WALL - 0.09, 0.14, M.n_white, r=0.008, verts=3)
sprite(GHOST, 13.9, 8.6, WALL - 0.08, 0.07, M.n_cyan)

finish("backdrop_arcade", 2048, 14000, windows=WINDOWS, wall=(0.10, 0.04, 0.23))
