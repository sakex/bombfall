# Backdrop for the casino, Neon Palace: red damask walls in gilt frames over
# a black marble dado, black-and-gold columns.  A bank of five slot
# machines whose reels spin and stop under chasing marquee toppers and a
# giant bulb-framed "JACKPOT" with a progressive meter; a roulette table
# whose wheel turns (spin_) while the ball orbits the other way; a
# half-moon blackjack table with cards and chips; a brass-barred cashier
# cage behind velvet ropes; neon card suits.  Up top: a Big Six money
# wheel that spins and clicks to a stop, and a bulb-lit "CASINO" sign.
#   blender -b --python blender/backdrop_casino.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
WINDOWS = [(5.6, 5.85, 4.4, 1.05), (11.0, 6.0, 3.0, 0.9)]
DAMASK = pbr("fabric", (0.30, 0.02, 0.05), color2=(0.42, 0.06, 0.08), bump=0.4, name="damask")
BULBS = anim_neon((1.0, 0.8, 0.4), "marquee", 3.0)
RED_P = pbr("plastic", (0.55, 0.02, 0.03), rough=0.3, name="chip_red")
BLACK_P = pbr("plastic", (0.02, 0.02, 0.025), rough=0.3, name="chip_black")
WHITE_P = pbr("plastic", (0.8, 0.8, 0.8), rough=0.3, name="chip_white")
BLUE_P = pbr("plastic", (0.05, 0.12, 0.6), rough=0.3, name="chip_blue")
GREEN_P = pbr("plastic", (0.02, 0.35, 0.1), rough=0.3, name="chip_green")
CHIPS = [RED_P, BLACK_P, WHITE_P, BLUE_P, GREEN_P]

# ------------------------------------------------------------ architecture --
slab_at(0.0, 15.0, 0.0, WALL, 0.0, 0.02, M.carpet_red)
flat_dots([(0.5 + i * 1.0 + (j % 2) * 0.5, 0.25 + j * 0.5) for i in range(15) for j in range(4)], 0.021, 0.18, M.carpet_gold)
slab_at(0.0, 15.0, WALL - 0.04, WALL, 0.0, 0.9, M.marble_black)
box((15.0, 0.06, 0.05), (7.5, WALL - 0.05, 0.9), M.gold)
boiserie(0.0, 15.0, 1.0, 5.62, WINDOWS + [(11.8, 0.0, 3.2, 3.6)], M.gold, DAMASK, pitch=1.5, inset=0.1)
box((15.0, 0.06, 0.07), (7.5, WALL - 0.05, 5.75), M.gold)
boiserie(0.0, 15.0, 5.85, 9.2, WINDOWS, M.gold, DAMASK, pitch=1.6, inset=0.1)
for cx in (4.75, 11.55):
    column(cx, 1.62, 5.75, M.marble_black, M.gold, r=0.18)
    for zz in (1.6, 3.2, 4.8):
        torus(0.19, 0.02, (cx, 1.62, zz), M.gold, major_segments=10, minor_segments=3)


# -------------------------------------------------------- slot machines --
REEL_MATS = [pbr("plastic", c, rough=0.4, name=n) for c, n in (((0.85, 0.82, 0.75), "reel_white"), ((0.7, 0.02, 0.03), "reel_seven"),
                                                               ((0.85, 0.82, 0.75), "reel_white"), ((0.9, 0.6, 0.05), "reel_bell"))]


def slot_machine(x, k):
    """An upright slot: lacquer cabinet, lit belly glass, button deck, a
    reel window with three drums that spin then stop, a chasing topper."""
    y = 1.05
    body = [M.lacquer_red, M.lacquer_plum, pbr("plastic", (0.02, 0.08, 0.25), rough=0.15, name="lacquer_blue")][k % 3]
    edge = ["pink", "cyan", "gold"][k % 3]
    slab_at(x - 0.36, x + 0.36, y, y + 0.7, 0.0, 0.85, body)
    slab_at(x - 0.32, x + 0.32, y - 0.03, y, 0.05, 0.7, M.black_metal)
    box((0.5, 0.02, 0.35), (x, y - 0.04, 0.45), anim_neon(["red", "violet", "orange"][k % 3], "screen", 1.2))
    slab_at(x - 0.28, x + 0.28, y - 0.06, y + 0.05, 0.78, 0.84, M.chrome)                     # coin tray
    prism([(y - 0.2, 0.85), (y + 0.2, 0.85), (y + 0.2, 1.0), (y - 0.08, 1.0)], x - 0.36, x + 0.36, M.black_metal, plane="yz")
    quad_dots([(x - 0.2 + i * 0.1, 0.94) for i in range(5)], y - 0.15, 0.05, [M.n_red, M.n_amber, M.n_green, M.n_amber, M.n_cyan][k % 5])
    # upper cabinet around a recessed reel window
    slab_at(x - 0.36, x + 0.36, y + 0.05, y + 0.7, 0.85, 1.14, body)
    slab_at(x - 0.36, x + 0.36, y + 0.05, y + 0.7, 1.58, 1.85, body)
    slab_at(x - 0.36, x - 0.29, y + 0.05, y + 0.7, 1.14, 1.58, body)
    slab_at(x + 0.29, x + 0.36, y + 0.05, y + 0.7, 1.14, 1.58, body)
    slab_at(x - 0.29, x + 0.29, y + 0.6, y + 0.7, 1.14, 1.58, M.black_metal)
    for j in range(3):
        rx = x - 0.17 + j * 0.17
        p = pivot("reel_%d_%d" % (k, j), (rx, y + 0.3, 1.36))
        # an octagonal drum with a symbol colour per face
        vs, fs, fm = [], [], []
        for s in range(8):
            a = TAU * s / 8
            vs += [(rx - 0.07, y + 0.3 + math.cos(a) * 0.2, 1.36 + math.sin(a) * 0.2), (rx + 0.07, y + 0.3 + math.cos(a) * 0.2, 1.36 + math.sin(a) * 0.2)]
        for s in range(8):
            a0, a1 = 2 * s, 2 * ((s + 1) % 8)
            fs.append((a0, a1, a1 + 1, a0 + 1))
            fm.append(s % 4)
        mesh_obj(vs, fs, REEL_MATS, "reel", False, parent=p, closed=False, face_mats=fm)
        stop = 36 + j * 12 + (k * 7) % 10
        key(p, "idle", "rotation_euler", [(0, (0, 0, 0)), (stop * 0.35, (TAU * 1.5, 0, 0)), (stop * 0.7, (TAU * 2.5, 0, 0)), (stop, (TAU * 3, 0, 0)),
                                          (LOOP, (TAU * 3, 0, 0))], interp="LINEAR")
    box((0.56, 0.02, 0.42), (x, y + 0.06, 1.36), M.glass)
    moulding_frame(x - 0.29, x + 0.29, 1.14, 1.58, y + 0.04, M.chrome, t=0.03)
    box((0.5, 0.02, 0.1), (x, y + 0.04, 1.72), anim_neon(edge, "screen", 1.5))
    # topper: a rounded lightbox ringed with chasing bulbs
    slab_at(x - 0.34, x + 0.34, y + 0.1, y + 0.6, 1.85, 2.3, body)
    prism(circle_pts(x, 2.3, 0.34, 10, 0.0, math.pi, ry=0.22), y + 0.1, y + 0.6, body, plane="xz")
    box((0.5, 0.02, 0.28), (x, y + 0.09, 2.12), anim_neon(["gold", "pink", "cyan"][k % 3], "screen", 1.8))
    quad_dots([(x + math.cos(a) * 0.36, 2.3 + math.sin(a) * 0.24) for a in [math.pi * i / 10 for i in range(11)]] +
              [(x - 0.36, 1.9 + i * 0.1) for i in range(4)] + [(x + 0.36, 1.9 + i * 0.1) for i in range(4)], y + 0.07, 0.045, BULBS)
    for sx in (-1, 1):
        tube([(x + sx * 0.365, y + 0.02, 0.05), (x + sx * 0.365, y + 0.02, 2.28)], 0.012, getattr(M, "n_" + edge), verts=4)
    # lever
    lathe([(0.04, 0), (0.04, 0.05)], (x + 0.39, y + 0.35, 1.25), M.chrome, segs=8, rot=(0, math.pi / 2, 0))
    tube([(x + 0.43, y + 0.35, 1.25), (x + 0.44, y + 0.3, 1.62)], 0.012, M.chrome, verts=5)
    ico(0.04, (x + 0.44, y + 0.3, 1.66), M.plastic_red, subdiv=1)


for k in range(5):
    slot_machine(0.7 + k * 0.78, k)
    lathe([(0.12, 0), (0.12, 0.02), (0.03, 0.05), (0.025, 0.55)], (0.7 + k * 0.78, 0.45, 0), M.chrome, segs=8, cap=False)
    lathe([(0.0, 0), (0.17, 0.0), (0.18, 0.05), (0.16, 0.09), (0.0, 0.1)], (0.7 + k * 0.78, 0.45, 0.55), M.velvet_red, segs=10)
# JACKPOT: bulb-framed marquee and a progressive meter
sign_board(2.3, 3.55, WALL - 0.08, 4.1, 1.55, M.black_metal, M.gold)
neon_text("JACKPOT", 2.3, 3.55, WALL - 0.12, 0.7, anim_neon("gold", "marquee", 3.5), r=0.035, align="center", verts=4)
quad_dots(rect_pts(0.35, 4.25, 2.85, 4.25, 0.14), WALL - 0.12, 0.06, BULBS)
slab_at(0.9, 3.7, WALL - 0.14, WALL - 0.08, 2.92, 3.38, M.plastic_black)
neon_text("$1000000", 2.3, 3.0, WALL - 0.16, 0.3, M.n_red, r=0.016, align="center", verts=4)

# ---------------------------------------------------------------- roulette --
RX, RY = 6.75, 0.95
prism(rounded_rect(3.0, 1.1, 0.4, 3, RX, RY), 0.0, 0.1, M.black_metal, plane="xy")
prism(rounded_rect(2.8, 0.95, 0.35, 3, RX, RY), 0.1, 0.8, M.mahogany, plane="xy")
prism(rounded_rect(2.9, 1.02, 0.38, 3, RX, RY), 0.8, 0.86, M.felt_green, plane="xy")
tube([(p[0], p[1], 0.87) for p in rounded_rect(2.94, 1.06, 0.4, 3, RX, RY)], 0.045, M.leather_black, verts=6, closed=True)
# betting layout on the felt: numbers grid, zero, dozens
lay = [(RX - 0.35 + c * 0.13, RY - 0.2 + r * 0.14) for c in range(12) for r in range(3)]
flat_dots([p for i, p in enumerate(lay) if (i + i // 3) % 2 == 0], 0.865, 0.1, RED_P)
flat_dots([p for i, p in enumerate(lay) if (i + i // 3) % 2 == 1], 0.865, 0.1, BLACK_P)
flat_dots([(RX - 0.5, RY)], 0.865, 0.12, GREEN_P)
for i in range(3):
    box((0.5, 0.1, 0.004), (RX - 0.1 + i * 0.52, RY + 0.34, 0.866), M.felt_green)
    box((0.48, 0.005, 0.005), (RX - 0.1 + i * 0.52, RY + 0.29, 0.867), M.gold)
for i, (cx, cy, n) in enumerate(((RX - 0.1, RY - 0.06, 6), (RX + 0.3, RY + 0.08, 9), (RX + 0.6, RY - 0.2, 4), (RX + 0.9, RY + 0.1, 12), (RX + 1.1, RY - 0.1, 7))):
    chip_stack(cx, cy, 0.865, n, CHIPS[i % 5])
# the wheel: a mahogany bowl, spinning head, and a ball orbiting against it
WX = RX - 1.05
lathe([(0.0, 0.0), (0.46, 0.0), (0.47, 0.1), (0.44, 0.14), (0.38, 0.1), (0.0, 0.08)], (WX, RY, 0.82), M.mahogany, segs=18)
sp = pivot("spin_roulette", (WX, RY, 0.9))
ring_segments(WX, RY, 0.925, 0.2, 0.33, 36, [RED_P, BLACK_P], "pockets", parent=sp)
ring_segments(WX, RY, 0.93, 0.28, 0.32, 36, [M.gold, M.gold], "frets", parent=sp)
lathe([(0.2, 0), (0.12, 0.05), (0.04, 0.07), (0.02, 0.14), (0.035, 0.16), (0.0, 0.17)], (WX, RY, 0.925), M.gold, segs=10, parent=sp)
for a in range(4):
    ang = a * math.pi / 2
    tube([(WX, RY, 1.06), (WX + math.cos(ang) * 0.1, RY + math.sin(ang) * 0.1, 1.06)], 0.008, M.gold, verts=4, parent=sp)
    ico(0.014, (WX + math.cos(ang) * 0.1, RY + math.sin(ang) * 0.1, 1.06), M.gold, subdiv=1, parent=sp)
merge_children(sp, "spin_roulette_mesh")
bp = pivot("roulette_ball", (WX, RY, 0.95))
ico(0.017, (WX + 0.37, RY, 0.95), WHITE_P, subdiv=1, parent=bp)
spin(bp, "idle", "Z", seconds=4, turns=-4)

# ------------------------------------------------------------- blackjack --
JX, JY = 10.1, 1.35
half = circle_pts(JX, JY, 1.1, 14, math.pi, TAU)
prism(half, 0.0, 0.1, M.black_metal, plane="xy")
prism(circle_pts(JX, JY, 1.0, 14, math.pi, TAU), 0.1, 0.8, M.mahogany, plane="xy")
prism(circle_pts(JX, JY, 1.08, 14, math.pi, TAU), 0.8, 0.86, M.felt_blue, plane="xy")
tube([(p[0], p[1], 0.87) for p in circle_pts(JX, JY, 1.12, 14, math.pi, TAU)], 0.05, M.leather_black, verts=6)
slab_at(JX - 0.35, JX + 0.35, JY - 0.2, JY - 0.05, 0.86, 0.9, M.black_metal)                   # chip tray
for i in range(6):
    chip_stack(JX - 0.3 + i * 0.12, JY - 0.12, 0.88, 8, CHIPS[i % 5], r=0.022)
slab_at(JX + 0.55, JX + 0.75, JY - 0.25, JY - 0.1, 0.86, 0.98, BLACK_P)                        # shoe
prism(circle_pts(JX, JY, 0.75, 14, math.pi * 1.1, math.pi * 1.9), 0.861, 0.8615, M.gold, plane="xy")
for i in range(5):
    a = math.pi * (1.15 + 0.7 * i / 4)
    cx, cy = JX + math.cos(a) * 0.72, JY + math.sin(a) * 0.72
    for c in range(2):
        box((0.06, 0.09, 0.003), (cx + c * 0.035, cy, 0.863 + c * 0.001), M.paper, rot=(0, 0, a + math.pi / 2 + c * 0.2))
    chip_stack(cx, cy + 0.14, 0.86, 3 + i * 2, CHIPS[i % 5])
for i in range(3):
    a = math.pi * (1.25 + 0.25 * i)
    lathe([(0.12, 0), (0.03, 0.05), (0.025, 0.6)], (JX + math.cos(a) * 1.35, JY + math.sin(a) * 1.0, 0), M.brass, segs=8, cap=False)
    lathe([(0.0, 0), (0.17, 0.0), (0.18, 0.05), (0.0, 0.1)], (JX + math.cos(a) * 1.35, JY + math.sin(a) * 1.0, 0.6), M.velvet_red, segs=10)

# ---------------------------------------------------------- cashier cage --
CX0, CX1 = 12.0, 14.85
slab_at(CX0, CX1, 1.25, WALL, 0.0, 1.1, M.marble_black)
for i in range(4):
    a = CX0 + 0.1 + i * (CX1 - CX0 - 0.2) / 4
    moulding_frame(a + 0.06, a + (CX1 - CX0 - 0.2) / 4 - 0.06, 0.15, 0.95, 1.24, M.gold, t=0.02)
slab_at(CX0 - 0.05, CX1 + 0.05, 1.2, WALL, 1.1, 1.16, M.gold)
slab_at(CX0, CX1, WALL - 0.03, WALL, 1.16, 2.7, M.backlight)
for i in range(25):
    bx = CX0 + 0.05 + i * (CX1 - CX0 - 0.1) / 24
    tube([(bx, 1.35, 1.16), (bx, 1.35, 2.7)], 0.01, M.brass, verts=4, caps=False)
for zz in (1.5, 2.2):
    box((CX1 - CX0, 0.03, 0.025), ((CX0 + CX1) / 2, 1.35, zz), M.brass)
for wx in (12.7, 14.15):
    prism(arch_outline(wx, 1.16, 0.55, 0.8, 8), 1.33, 1.37, M.glass, plane="xz")
    tube([(p[0], 1.33, p[1]) for p in arch_outline(wx, 1.16, 0.58, 0.83, 8)][1:] + [(wx - 0.29, 1.33, 1.16)], 0.02, M.gold, verts=4)
    for j in range(3):
        slab_at(wx - 0.2 + j * 0.13, wx - 0.1 + j * 0.13, 1.7, 1.85, 1.16, 1.19 + j * 0.02, GREEN_P)
slab_at(CX0 - 0.08, CX1 + 0.08, 1.25, WALL, 2.7, 2.85, M.gold)
sign_board((CX0 + CX1) / 2, 3.3, WALL - 0.06, 2.7, 0.62, M.black_metal, M.gold)
neon_text("CASHIER", (CX0 + CX1) / 2, 3.1, WALL - 0.1, 0.4, M.n_green, r=0.02, align="center", verts=4)
stanchions([(11.9, 0.35), (13.1, 0.3), (14.3, 0.35)])
stanchions([(4.35, 0.3), (5.1, 0.25)])

# ------------------------------------------------------- neon card suits --
def suit(kind, x, z, s, m):
    y = WALL - 0.06
    if kind == "heart":
        pts = [(x, z - s)] + [(x + s * 0.5 + math.cos(a) * s * 0.5, z + s * 0.35 + math.sin(a) * s * 0.5) for a in [math.pi * (-0.25 + 1.25 * i / 8) for i in range(9)]]
        pts += [(x - s * 0.5 + math.cos(a) * s * 0.5, z + s * 0.35 + math.sin(a) * s * 0.5) for a in [math.pi * (0.0 + 1.25 * i / 8) for i in range(9)]] + [(x, z - s)]
        tube([(px, y, pz) for px, pz in pts], 0.03, m, verts=4)
    elif kind == "diamond":
        tube([(x, y, z - s), (x + s * 0.7, y, z), (x, y, z + s), (x - s * 0.7, y, z), (x, y, z - s)], 0.03, m, verts=4)
    elif kind == "spade":
        pts = [(x, z + s)] + [(x + s * 0.5 + math.cos(a) * s * 0.5, z - s * 0.2 + math.sin(a) * s * 0.5) for a in [math.pi * (0.75 - 1.25 * i / 8) for i in range(9)]]
        pts += [(x, z - s * 0.4)] + [(x - s * 0.5 + math.cos(a) * s * 0.5, z - s * 0.2 + math.sin(a) * s * 0.5) for a in [math.pi * (1.5 - 1.25 * i / 8) for i in range(9)]] + [(x, z + s)]
        tube([(px, y, pz) for px, pz in pts], 0.03, m, verts=4)
        tube([(x, y, z - s * 0.4), (x - s * 0.3, y, z - s), (x + s * 0.3, y, z - s), (x, y, z - s * 0.4)], 0.03, m, verts=4)
    else:
        for (dx, dz) in ((0, 0.45), (-0.45, -0.1), (0.45, -0.1)):
            tube([(x + dx * s + math.cos(a) * s * 0.33, y, z + dz * s + math.sin(a) * s * 0.33) for a in [TAU * i / 10 for i in range(11)]], 0.03, m, verts=4)
        tube([(x, y, z - s * 0.1), (x - s * 0.3, y, z - s), (x + s * 0.3, y, z - s), (x, y, z - s * 0.1)], 0.03, m, verts=4)


for i, (kind, m) in enumerate((("spade", M.n_white), ("heart", M.n_pink), ("club", M.n_white), ("diamond", M.n_pink))):
    suit(kind, 6.0 + i * 1.3, 4.3, 0.42, m)

# ---------------------------------------------------------- upper gallery --
# Big Six money wheel: segments, gold spokes, a bulb rim; it spins then
# clicks to a stop against a leather flapper.
BX, BZ, BR = 2.6, 7.95, 0.88
lathe([(BR + 0.12, 0.0), (BR + 0.12, 0.08), (0.0, 0.08)], (BX, WALL - 0.02, BZ), M.mahogany, segs=24, rot=(math.pi / 2, 0, 0))
bp = pivot("bigsix", (BX, WALL - 0.12, BZ))
seg = ring_segments(BX, BZ, WALL - 0.1, 0.18, BR, 24, [M.lacquer_red, M.lacquer_white, pbr("plastic", (0.05, 0.1, 0.45), rough=0.2, name="big6_blue"),
                                                          M.lacquer_white, pbr("plastic", (0.9, 0.6, 0.05), rough=0.2, name="big6_gold"), M.lacquer_white],
                    "bigsix_face", parent=bp, upright=True)
for k in range(24):
    a = TAU * k / 24
    tube([(BX + math.cos(a) * 0.18, WALL - 0.12, BZ + math.sin(a) * 0.18), (BX + math.cos(a) * BR, WALL - 0.12, BZ + math.sin(a) * BR)], 0.008, M.gold, verts=3, caps=False, parent=bp)
lathe([(0.2, 0), (0.2, 0.04), (0.08, 0.07), (0.0, 0.07)], (BX, WALL - 0.12, BZ), M.gold, segs=12, rot=(math.pi / 2, 0, 0), parent=bp)
merge_children(bp, "bigsix_mesh")
key(bp, "idle", "rotation_euler", [(0, (0, 0, 0)), (30, (0, -TAU * 1.2, 0)), (60, (0, -TAU * 1.85, 0)), (80, (0, -TAU * 2.0, 0)), (LOOP, (0, -TAU * 2.0, 0))], interp="LINEAR")
quad_dots([(BX + math.cos(TAU * i / 32) * (BR + 0.07), BZ + math.sin(TAU * i / 32) * (BR + 0.07)) for i in range(32)], WALL - 0.1, 0.05, BULBS)
prism([(BX - 0.05, BZ + BR + 0.18), (BX + 0.05, BZ + BR + 0.18), (BX, BZ + BR - 0.05)], WALL - 0.16, WALL - 0.08, M.leather_black, plane="xz")
# CASINO in bulb-framed neon between the upper windows
sign_board(8.3, 7.95, WALL - 0.08, 5.6, 1.5, M.black_metal, M.gold)
neon_text("CASINO", 8.3, 7.45, WALL - 0.12, 0.95, M.n_pink, r=0.04, align="center", verts=4)
quad_dots(rect_pts(5.6, 11.0, 7.3, 8.6, 0.16), WALL - 0.12, 0.07, BULBS)
# dice
for (dx, dz, rot) in ((13.1, 7.8, 0.3), (13.95, 7.95, -0.2)):
    box((0.55, 0.1, 0.55), (dx, WALL - 0.1, dz), M.lacquer_red, rot=(0, rot, 0))
    for (ox, oz) in ((-0.15, -0.15), (0.15, 0.15), (0.0, 0.0), (0.15, -0.15), (-0.15, 0.15)):
        c, s = math.cos(-rot), math.sin(-rot)
        quad_dots([(dx + ox * c - oz * s, dz + ox * s + oz * c)], WALL - 0.16, 0.08, M.n_white, diamond=True)

finish("backdrop_casino", 2048, 14000, windows=WINDOWS, wall=(0.19, 0.04, 0.15))
