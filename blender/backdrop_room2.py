# Backdrop for the Hotel Electra staff dorm (room2): where the night shift
# sleeps.  A stacked washer/dryer with laundry tumbling behind the glass and
# a basket of clothes; a black steel bunk bed under the big window with
# rumpled wool blankets, a towel, a backpack, taped posters and twinkling
# fairy lights; a bank of teal lockers (one ajar, padlocks, name plates)
# behind a worn oxblood sofa patched with tape; a cork notice board with
# pinned notes fluttering in the draught; a glowing snack vending machine
# with a chasing marquee; a kitchenette with a steaming kettle and a
# microwave clock; up top roller blinds, an oscillating wall fan, a TV,
# a clock and exposed pipes.
#   blender -b --python blender/backdrop_room2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
WINDOWS = [(3.0, 4.7, 4.0, 1.9), (1.1, 7.6, 2.6, 1.1), (6.2, 7.6, 2.6, 1.1), (11.3, 7.6, 2.6, 1.1)]
THEME = dict(wall=(0.05, 0.07, 0.21), trim=(0.4, 0.55, 1.0), floor=(0.04, 0.05, 0.14))

# ------------------------------------------------------------ materials --
ENAMEL = M("paint", (0.62, 0.64, 0.66), rough=0.3, wear=0.3)
STEEL_BLK = M("paint", (0.02, 0.02, 0.025), rough=0.4, wear=0.8)
CHROME = M("chrome", (0.7, 0.72, 0.78))
STEEL = M("metal", (0.5, 0.52, 0.55))
LOCKER = M("paint", (0.03, 0.17, 0.19), rough=0.45, wear=0.8, grime=0.7)
LOCKER_DK = M("paint", (0.01, 0.05, 0.06), rough=0.6)
BRASS = M("gold", (0.8, 0.55, 0.22))
MATTRESS = M("fabric", (0.55, 0.56, 0.6), color2=(0.45, 0.46, 0.5))
BLANKET_N = pattern("fabric", (0.03, 0.05, 0.14), "stripes", size=(1.6, 1.0), line_col=(0.55, 0.38, 0.08), duty=0.08, plane="XZ")
BLANKET_G = M("fabric", (0.2, 0.2, 0.22), color2=(0.14, 0.14, 0.16))
PILLOW = M("fabric", (0.66, 0.66, 0.7))
OXBLOOD = M("leather", (0.1, 0.018, 0.014), wear=0.8, grime=0.6)
TAPE = M("plastic", (0.35, 0.35, 0.36), rough=0.7)
MUSTARD = M("fabric", (0.5, 0.32, 0.04))
CORK = M("concrete", (0.32, 0.18, 0.08), grime=0.2, bump=0.9)
ALU = M("metal", (0.6, 0.62, 0.65))
PAPER = [M("plastic", c, rough=0.9) for c in ((0.85, 0.75, 0.2), (0.9, 0.35, 0.55), (0.3, 0.75, 0.85), (0.8, 0.8, 0.78))]
PIN = [M("plastic", c, rough=0.3) for c in ((0.8, 0.05, 0.05), (0.05, 0.2, 0.8), (0.05, 0.6, 0.1))]
LAMINATE = M("plastic", (0.45, 0.55, 0.5), rough=0.35, wear=0.4)
BUTCHER = M("wood", (0.35, 0.2, 0.09), color2=(0.26, 0.14, 0.06), rough=0.4)
BLACK = M("plastic", (0.012, 0.012, 0.015), rough=0.35)
VEND = M("paint", (0.02, 0.02, 0.03), rough=0.25, wear=0.5)
RUBBER = M("rubber", (0.02, 0.02, 0.025))
WICKER = pattern("plastic", (0.35, 0.25, 0.12), "tiles", size=(0.12, 0.08), line=0.02, plane="XZ", offset=0.5)
CLOTH = [M("fabric", c) for c in ((0.5, 0.05, 0.2), (0.05, 0.25, 0.45), (0.7, 0.7, 0.7), (0.1, 0.4, 0.2), (0.6, 0.35, 0.05))]
PLANT_G = M("plastic", (0.03, 0.14, 0.05), rough=0.5)
TERRACOTTA = M("ceramic", (0.35, 0.1, 0.04), rough=0.6)

VEND_LIGHT = glow((0.75, 0.9, 1.0), 2.6, base=(0.6, 0.7, 0.8))
MARQ = marquee((1.0, 0.25, 0.7), 3.0)
RED_LED = glow((1.0, 0.1, 0.08), 4.0)
GREEN_LED = glow((0.2, 1.0, 0.35), 4.0)
FAIRY_A = glow((1.0, 0.75, 0.35), 5.0)
FAIRY_B = glow((1.0, 0.35, 0.7), 5.0)
CLIP_LAMP = glow((1.0, 0.85, 0.6), 2.5)
TV = screen((0.45, 0.55, 1.0), 1.6)
GLASS = glass((0.6, 0.75, 0.9), alpha=0.25)
STEAM = glass((0.9, 0.92, 1.0), alpha=0.35, rough=0.6)
POSTER_A = glow((1.0, 0.3, 0.6), 0.6, base=(0.5, 0.1, 0.3))

# ------------------------------------------------------- walls and trims --
moulding(0.0, 15.0, 0.0, [(0.0, 0.0), (0.04, 0.0), (0.04, 0.16), (0.0, 0.2)], RUBBER)
moulding(0.0, 15.0, 2.25, [(0.0, 0.0), (0.06, 0.02), (0.06, 0.14), (0.0, 0.16)], M("plastic", (0.12, 0.14, 0.2)), avoid=WINDOWS)
moulding(0.0, 15.0, 9.25, [(0.0, 0.0), (0.12, 0.0), (0.12, 0.25), (0.0, 0.25)], M("paint", (0.1, 0.12, 0.25)))

# ------------------------------------------------------ laundry corner --
LX = 1.0
for k, (z0, turns) in enumerate(((0.06, 2), (2.2, 1))):
    fbox((1.55, 1.45, 2.08), (LX, 1.2, z0), ENAMEL, bev=0.06, seg=2)
    box((1.45, 0.03, 0.3), (LX, 0.465, z0 + 1.82), M("plastic", (0.08, 0.09, 0.1)))
    box((0.3, 0.02, 0.1), (LX + 0.4, 0.45, z0 + 1.82), glow((0.3, 0.9, 1.0), 2.5))
    for dx in (-0.45, -0.2):
        cyl(0.07, 0.05, (LX + dx, 0.45, z0 + 1.82), CHROME, rot=(math.pi / 2, 0, 0), verts=10, bevel=0)
    cz = z0 + 0.95
    torus(0.52, 0.07, (LX, 0.44, cz), CHROME, rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=5)
    cyl(0.5, 0.02, (LX, 0.5, cz), M("rubber", (0.01, 0.01, 0.012)), rot=(math.pi / 2, 0, 0), verts=20, bevel=0)
    drum = pivot("drum_%d" % k, (LX, 0.55, cz))
    for j in range(5):
        a = j / 5 * math.tau
        ball(0.2 + 0.04 * (j % 2), (LX + math.cos(a) * 0.24, 0.6, cz + math.sin(a) * 0.24), CLOTH[(j + k) % 5],
             scale=(1.2, 0.6, 0.8), seg=8, rings=6, parent=drum)
    spin_idle(drum, "Y", turns)
    cyl(0.46, 0.02, (LX, 0.42, cz), GLASS, rot=(math.pi / 2, 0, 0), verts=20, bevel=0)
    box((0.12, 0.06, 0.25), (LX + 0.55, 0.4, cz), CHROME, bev=0.02)
for dx in (-0.6, 0.6):
    cyl(0.07, 0.06, (LX + dx, 0.6, 0.03), RUBBER, verts=8, bevel=0)
bottle(LX - 0.35, 1.2, 4.28, 0.7, M("plastic", (0.8, 0.3, 0.02), rough=0.3), cap=M("plastic", (0.05, 0.1, 0.5)), r=0.2)
bottle(LX + 0.25, 1.3, 4.28, 0.55, M("plastic", (0.05, 0.25, 0.7), rough=0.3), cap=BLACK, r=0.16)
# a wall shelf of clean linen above the machines
box((2.5, 0.6, 0.06), (1.35, WALL - 0.3, 5.3), M("wood", (0.3, 0.2, 0.1), color2=(0.22, 0.14, 0.07)), bev=0.01)
for x in (0.35, 2.35):
    box((0.05, 0.4, 0.3), (x, WALL - 0.2, 5.12), STEEL)
TOWEL_W = M("fabric", (0.75, 0.75, 0.78))
TOWEL_T = M("fabric", (0.03, 0.3, 0.35))
for k, (x, n, m) in enumerate(((0.6, 4, TOWEL_W), (1.25, 3, TOWEL_T), (1.9, 5, TOWEL_W))):
    for j in range(n):
        pill((0.55, 0.5, 0.14), (x + 0.02 * (j % 2), WALL - 0.32, 5.4 + j * 0.14), m, seg=2, round_=0.05)
# a wicker basket of laundry in front
lathe([(0.42, 0.0), (0.5, 0.75)], (1.75, 0.35, 0.0), WICKER, verts=14, cap_top=False, cap_bottom=True)
for j, (dx, dz) in enumerate(((-0.2, 0.75), (0.15, 0.8), (0.0, 0.9), (0.3, 0.7))):
    ball(0.28, (1.75 + dx, 0.35, dz), CLOTH[j], scale=(1.1, 0.8, 0.55), seg=8, rings=6)
box((0.15, 0.04, 0.9), (1.95, 0.08, 0.5), CLOTH[2], rot=(0, 0.2, 0))   # a sleeve hanging out

# ------------------------------------------------------------ bunk bed --
BX0, BX1 = 2.35, 7.05
for x in (BX0, BX1):
    for y in (0.3, 1.8):
        fbox((0.1, 0.1, 4.3), (x, y, 0.0), STEEL_BLK, bev=0.015)
for z in (0.55, 2.6):
    for y in (0.3, 1.8):
        box((BX1 - BX0, 0.08, 0.14), ((BX0 + BX1) / 2, y, z), STEEL_BLK, bev=0.01)
    pill((BX1 - BX0 - 0.1, 1.45, 0.42), ((BX0 + BX1) / 2, 1.05, z + 0.3), MATTRESS, round_=0.1)
# guard rail on the top bunk, open at the ladder
for z in (3.45, 3.95):
    box((BX1 - BX0 - 1.0, 0.06, 0.06), ((BX0 + BX1 - 1.0) / 2, 0.3, z), STEEL_BLK)
fbox((0.06, 0.06, 1.4), (BX1 - 1.0, 0.3, 2.6), STEEL_BLK)
# ladder
for x in (BX1 - 0.45, BX1 - 0.05):
    rod((x, 0.2, 0.0), (x, 0.2, 3.9), 0.03, STEEL_BLK, verts=6)
for k in range(6):
    rod((BX1 - 0.45, 0.2, 0.45 + k * 0.6), (BX1 - 0.05, 0.2, 0.45 + k * 0.6), 0.025, STEEL, verts=6)
# lower bunk: navy blanket pulled half off, a pillow and a phone glow
box((3.3, 1.2, 0.2), (3.9, 0.95, 1.18), BLANKET_N, bev=0.08, seg=2)
box((3.3, 0.1, 0.8), (3.9, 0.3, 0.9), BLANKET_N, bev=0.04, rot=(0, 0.04, 0))
for j, (dx, s) in enumerate(((-0.8, 0.3), (0.2, 0.25), (1.1, 0.35))):
    ball(s, (3.9 + dx, 0.95, 1.25), BLANKET_N, scale=(2.0, 1.6, 0.6), seg=10, rings=6)
pill((1.1, 0.55, 0.35), (6.1, 1.35, 1.3), PILLOW, rot=(0, 0.1, 0))
box((0.2, 0.35, 0.03), (5.3, 0.9, 1.3), glow((0.5, 0.8, 1.0), 2.0))
# top bunk: grey blanket bunched at the foot, a pillow, a clip lamp
box((2.2, 1.2, 0.22), (3.5, 1.0, 3.25), BLANKET_G, bev=0.09, seg=2)
ball(0.5, (2.9, 0.95, 3.35), BLANKET_G, scale=(1.6, 1.3, 0.6), seg=10, rings=6)
pill((1.1, 0.55, 0.35), (5.9, 1.35, 3.35), PILLOW, rot=(0, -0.1, 0))
box((0.12, 0.15, 0.2), (BX0 + 0.1, 0.25, 3.9), BLACK, bev=0.03)
tube_path([(BX0 + 0.1, 0.25, 4.0), (BX0 + 0.3, 0.2, 4.35), (BX0 + 0.55, 0.2, 4.3)], 0.02, BLACK, verts=5)
lathe([(0.18, 0.0), (0.08, 0.2)], (BX0 + 0.62, 0.2, 4.05), BLACK, verts=12, cap_top=True)
cyl(0.17, 0.01, (BX0 + 0.62, 0.2, 4.055), CLIP_LAMP, verts=12, bevel=0)
# a towel over the guard rail (drifting) and a backpack on the ladder
towel = pivot("towel", (4.6, 0.28, 3.95))
box((0.8, 0.05, 0.9), (4.6, 0.24, 3.55), M("fabric", (0.02, 0.35, 0.4)), bev=0.02, parent=towel)
box((0.8, 0.05, 0.4), (4.6, 0.33, 3.8), M("fabric", (0.02, 0.35, 0.4)), bev=0.02, parent=towel)
swing(towel, "X", amp=0.05)
bag = pivot("backpack", (BX1 - 0.25, 0.15, 2.35))
pill((0.7, 0.35, 0.9), (BX1 - 0.25, 0.05, 1.85), M("fabric", (0.35, 0.05, 0.08)), parent=bag)
pill((0.5, 0.15, 0.4), (BX1 - 0.25, -0.1, 1.7), M("fabric", (0.25, 0.03, 0.05)), parent=bag)
swing(bag, "Y", amp=0.04, phase=1.0)
# sneakers and a storage bin under the bunk
for dx in (0.0, 0.42):
    pill((0.38, 0.8, 0.22), (2.9 + dx, 0.9, 0.12), M("fabric", (0.75, 0.75, 0.78)), rot=(0, 0, 0.2))
fbox((1.4, 1.0, 0.45), (4.9, 1.1, 0.0), M("plastic", (0.05, 0.2, 0.45), rough=0.3), bev=0.03)
# posters taped on the wall between the bunks, and fairy lights
box((1.1, 0.02, 1.5), (3.2, WALL - 0.01, 1.85 + 0.05), POSTER_A, rot=(0, 0.04, 0))
box((0.9, 0.02, 1.2), (5.6, WALL - 0.01, 1.8), M("plastic", (0.1, 0.3, 0.55), rough=0.8), rot=(0, -0.05, 0))
ball(0.3, (5.6, WALL - 0.03, 1.9), M("plastic", (0.9, 0.5, 0.1), rough=0.8), scale=(1, 0.1, 1), seg=10, rings=6)
for k in range(2):
    fl = pivot("fairy_%d" % k, (4.7, WALL - 0.05, 4.2))
    pts = catenary((BX0 + 0.1, WALL - 0.05, 4.25), (BX1 - 0.1, WALL - 0.05, 4.25), 0.45, n=16)
    for j, p in enumerate(pts):
        if j % 2 == k:
            ball(0.05, p, FAIRY_A if k else FAIRY_B, seg=6, rings=4, parent=fl)
    blink(fl, [(0, 30), (60, 90)] if k else [(30, 60), (90, 120)])
cable((BX0 + 0.1, WALL - 0.04, 4.25), (BX1 - 0.1, WALL - 0.04, 4.25), 0.45, r=0.01, m=BLACK, n=16, verts=4)

# ------------------------------------------ lockers, sofa, notice board --
LK0 = 7.35
for i in range(4):
    x = LK0 + 0.375 + i * 0.75
    fbox((0.74, 0.62, 4.35), (x, 1.6, 0.15), LOCKER, bev=0.015)
    ajar = i == 2
    if ajar:
        box((0.64, 0.05, 4.1), (x, 1.3, 2.35), LOCKER_DK)          # dark inside
        box((0.5, 0.3, 1.2), (x, 1.5, 3.3), M("fabric", (0.6, 0.6, 0.62)), bev=0.05)   # uniform
        rod((x - 0.3, 1.45, 3.95), (x + 0.3, 1.45, 3.95), 0.02, STEEL, verts=6)
        th = 1.0
        hx, hy = x - 0.35, 1.27
        box((0.7, 0.04, 4.15), (hx + math.cos(th) * 0.35, hy - math.sin(th) * 0.35, 2.35), LOCKER, rot=(0, 0, -th), bev=0.01)
        for zz in (4.1, 0.55):
            for j in range(4):
                box((0.4, 0.03, 0.03), (hx + math.cos(th) * 0.35 - 0.02, hy - math.sin(th) * 0.35 - 0.03, zz + j * 0.08), LOCKER_DK, rot=(0, 0, -th))
        continue
    box((0.7, 0.04, 4.15), (x, 1.27, 2.35), LOCKER, bev=0.01)
    for zz in (4.1, 0.55):
        for j in range(4):
            box((0.4, 0.03, 0.03), (x, 1.245, zz + j * 0.08), LOCKER_DK)
    box((0.06, 0.06, 0.3), (x + 0.25, 1.23, 2.4), CHROME, bev=0.01)
    box((0.22, 0.02, 0.1), (x, 1.24, 3.5), M("plastic", (0.7, 0.7, 0.65)))
    if i in (0, 3):
        box((0.12, 0.05, 0.14), (x + 0.25, 1.19, 2.15), BRASS, bev=0.02)
        torus(0.05, 0.012, (x + 0.25, 1.19, 2.25), STEEL, rot=(math.pi / 2, 0, 0), major_segments=8, minor_segments=4)
fbox((3.0, 0.62, 0.15), (LK0 + 1.5, 1.6, 0.0), LOCKER_DK)
fbox((0.9, 0.6, 0.5), (LK0 + 0.6, 1.6, 4.5), M("plastic", (0.4, 0.28, 0.14), rough=0.8), bev=0.02)  # cardboard box
ball(0.32, (LK0 + 2.3, 1.6, 4.8), M("plastic", (0.6, 0.05, 0.1), rough=0.15), scale=(1.2, 1.2, 0.9), seg=12, rings=8)  # helmet
# worn oxblood sofa with a taped cushion and a mustard throw
SX = 8.9
fbox((3.4, 0.95, 0.75), (SX, 0.65, 0.15), OXBLOOD, bev=0.06, seg=2)
for dx in (-0.78, 0.78):
    pill((1.5, 0.9, 0.36), (SX + dx, 0.62, 1.07), OXBLOOD, seg=2, round_=0.12)
    pill((1.5, 0.36, 0.95), (SX + dx, 1.02, 1.62), OXBLOOD, rot=(-0.18, 0, 0), seg=2, round_=0.14)
for s in (-1, 1):
    pill((0.36, 1.05, 1.25), (SX + s * 1.72, 0.66, 0.78), OXBLOOD, seg=2, round_=0.12)
    for dy in (0.3, 1.0):
        rod((SX + s * 1.6, dy, 0.0), (SX + s * 1.6, dy, 0.16), 0.04, M("wood", (0.1, 0.05, 0.02)), r2=0.03, verts=6)
box((0.4, 0.5, 0.02), (SX - 0.6, 0.55, 1.26), TAPE, rot=(0, 0, 0.5))
box((0.35, 0.02, 0.4), (SX + 0.9, 0.85, 1.7), TAPE, rot=(-0.18, 0.3, 0))
box((0.55, 1.1, 0.6), (SX + 1.72, 0.62, 1.35), MUSTARD, bev=0.1, seg=2, rot=(0, 0.1, 0))
box((0.5, 0.08, 0.8), (SX + 1.95, 0.25, 1.0), MUSTARD, bev=0.03)
box((0.5, 0.3, 0.06), (SX - 0.3, 0.45, 1.27), M("plastic", (0.05, 0.05, 0.06)), bev=0.03, rot=(0, 0, 0.3))  # controller
# cork notice board above the lockers, notes pinned (two flutter)
NBX, NBZ, NBW, NBH = 8.85, 5.7, 2.7, 1.45
box((NBW, 0.06, NBH), (NBX, WALL - 0.03, NBZ), ALU, bev=0.02)
box((NBW - 0.1, 0.02, NBH - 0.1), (NBX, WALL - 0.065, NBZ), CORK)
rnd = [0.13, 0.71, 0.42, 0.9, 0.27, 0.58, 0.05, 0.83, 0.36, 0.64, 0.19, 0.51]
notes = [(-1.0, 0.3), (-0.55, 0.25), (-0.05, 0.35), (0.5, 0.3), (1.0, 0.25), (-0.85, -0.3), (-0.3, -0.25), (0.25, -0.35), (0.85, -0.25)]
for i, (dx, dz) in enumerate(notes):
    px, pz = NBX + dx, NBZ + dz
    w, h = 0.36 + 0.1 * rnd[i], 0.42 + 0.1 * rnd[i + 1]
    flutter = i in (2, 7)
    par = pivot("note_%d" % i, (px, WALL - 0.09, pz + h / 2 - 0.04)) if flutter else None
    rz = (rnd[i] - 0.5) * 0.25
    box((w, 0.012, h), (px, WALL - 0.078, pz), PAPER[i % 4], rot=(0, rz, 0), parent=par)
    if i == 4:
        for j in range(5):
            box((w * 0.7, 0.01, 0.025), (px, WALL - 0.086, pz + 0.12 - j * 0.07), BLACK, parent=par)
    ball(0.035, (px, WALL - 0.1, pz + h / 2 - 0.04), PIN[i % 3], seg=6, rings=4)
    if par is not None:
        swing(par, "Y", amp=0.12, cycles=2, phase=i)
box((0.5, 0.012, 0.6), (NBX + 0.05, WALL - 0.08, NBZ - 0.05), M("plastic", (0.8, 0.8, 0.8), rough=0.4))   # polaroid
box((0.42, 0.01, 0.4), (NBX + 0.05, WALL - 0.087, NBZ + 0.0), M("plastic", (0.2, 0.1, 0.35), rough=0.4))

# ------------------------------------------------------ vending machine --
VX, VW = 11.85, 2.2
fbox((VW, 1.2, 4.6), (VX, 1.3, 0.0), VEND, bev=0.04)
for s in (-1, 1):
    box((0.04, 1.1, 4.3), (VX + s * (VW / 2 + 0.005), 1.3, 2.35), glow((1.0, 0.2, 0.6), 1.5))
GX0, GX1 = VX - VW / 2 + 0.12, VX + 0.35
box((GX1 - GX0, 0.05, 2.7), ((GX0 + GX1) / 2, 0.95, 2.9), VEND_LIGHT)
for r in range(5):
    zz = 1.7 + r * 0.52
    box((GX1 - GX0, 0.45, 0.03), ((GX0 + GX1) / 2, 0.85, zz), STEEL)
    for c in range(6):
        cx = GX0 + 0.12 + c * (GX1 - GX0 - 0.24) / 5
        col = CLOTH[(r * 2 + c) % 5] if (r + c) % 3 else M("plastic", (0.9, 0.7, 0.1), rough=0.3)
        if r % 2:
            bottle(cx, 0.8, zz + 0.02, 0.4, col, cap=BLACK, r=0.07)
        else:
            box((0.16, 0.2, 0.34), (cx, 0.8, zz + 0.19), col, rot=(0, 0, 0.1 * (c % 2)))
box((GX1 - GX0 + 0.06, 0.03, 2.8), ((GX0 + GX1) / 2, 0.69, 2.9), GLASS)
for zz in (1.52, 4.28):
    box((GX1 - GX0 + 0.1, 0.06, 0.06), ((GX0 + GX1) / 2, 0.68, zz), CHROME)
# keypad column
box((0.55, 0.03, 0.3), (VX + 0.72, 0.68, 3.9), glow((1.0, 0.15, 0.1), 2.0, base=(0.1, 0.01, 0.01)))
for r in range(4):
    for c in range(3):
        box((0.1, 0.04, 0.08), (VX + 0.58 + c * 0.14, 0.68, 3.35 - r * 0.14), CHROME)
box((0.1, 0.05, 0.25), (VX + 0.72, 0.68, 2.5), BLACK)
box((0.35, 0.05, 0.12), (VX + 0.72, 0.68, 2.1), BLACK)
box((1.3, 0.1, 0.5), (VX - 0.35, 0.72, 0.75), BLACK, bev=0.02)
box((VW - 0.2, 0.04, 0.32), (VX, 0.68, 4.42), MARQ)
light = pivot("vend_light", (VX - 0.35, 0.93, 2.9))
box((GX1 - GX0 - 0.1, 0.02, 0.05), ((GX0 + GX1) / 2, 0.93, 4.2), glow((0.9, 0.95, 1.0), 6.0), parent=light)
flicker(light, seed=41, bursts=2)

# ---------------------------------------------------------- kitchenette --
KX0, KX1 = 13.1, 14.95
fbox((KX1 - KX0, 1.05, 2.12), ((KX0 + KX1) / 2, 1.38, 0.1), LAMINATE, bev=0.02)
fbox((KX1 - KX0 - 0.1, 0.9, 0.1), ((KX0 + KX1) / 2, 1.4, 0.0), BLACK)
for k in range(2):
    x = KX0 + 0.46 + k * 0.92
    box((0.86, 0.04, 1.8), (x, 0.84, 1.15), LAMINATE, bev=0.015)
    box((0.04, 0.05, 0.35), (x + (0.34 if k == 0 else -0.34), 0.8, 1.7), CHROME, bev=0.01)
box((KX1 - KX0 + 0.08, 1.15, 0.1), ((KX0 + KX1) / 2, 1.36, 2.27), BUTCHER, bev=0.02)
# kettle with steam, mugs, microwave with a blinking clock
KT = (13.55, 1.2, 2.32)
lathe([(0.25, 0.0), (0.28, 0.12), (0.26, 0.45), (0.18, 0.6), (0.06, 0.62)], KT, CHROME, verts=14)
tube_path([(KT[0] + 0.25, KT[1], KT[2] + 0.2), (KT[0] + 0.38, KT[1], KT[2] + 0.35), (KT[0] + 0.38, KT[1], KT[2] + 0.5),
           (KT[0] + 0.18, KT[1], KT[2] + 0.6)], 0.035, BLACK, verts=6)
tube_path([(KT[0] - 0.24, KT[1], KT[2] + 0.35), (KT[0] - 0.42, KT[1], KT[2] + 0.55)], 0.045, CHROME, verts=6)
cyl(0.27, 0.06, (KT[0], KT[1], KT[2] - 0.0), BLACK, verts=14, bevel=0)
box((0.06, 0.02, 0.04), (KT[0], KT[1] - 0.27, KT[2] + 0.03), glow((0.3, 0.6, 1.0), 4.0))
for j in range(3):
    st = pivot("steam_%d" % j, (KT[0] - 0.44, KT[1], KT[2] + 0.6))
    ball(0.12, (KT[0] - 0.44, KT[1], KT[2] + 0.6), STEAM, seg=8, rings=6, parent=st)
    puff(st, rise=0.9, grow=2.6, start=j * 40, life=80, drift=-0.15)
for j, x in enumerate((14.0, 14.2)):
    cyl(0.1, 0.22, (x, 1.0, 2.43), M("ceramic", [(0.6, 0.1, 0.2), (0.7, 0.7, 0.7)][j]), verts=10, bevel=0.01)
MW = (14.4, 1.4, 2.32)
fbox((0.95, 0.9, 0.62), MW, M("paint", (0.12, 0.12, 0.13), wear=0.4), bev=0.03)
box((0.6, 0.02, 0.45), (MW[0] - 0.12, 0.94, MW[2] + 0.31), glass((0.1, 0.12, 0.1), alpha=0.7))
box((0.18, 0.02, 0.07), (MW[0] + 0.33, 0.94, MW[2] + 0.48), glow((0.2, 1.0, 0.4), 3.0, base=(0.02, 0.1, 0.03)))
mwc = pivot("mw_colon", (MW[0] + 0.33, 0.93, MW[2] + 0.48))
box((0.012, 0.01, 0.05), (MW[0] + 0.33, 0.925, MW[2] + 0.48), glow((0.2, 1.0, 0.4), 6.0), parent=mwc)
blink(mwc, [(15, 30), (45, 60), (75, 90), (105, 120)])
# wall cabinet with a little plant on top
fbox((KX1 - KX0, 0.7, 1.55), ((KX0 + KX1) / 2, WALL - 0.35, 3.7), LAMINATE, bev=0.02)
for k in range(2):
    box((0.86, 0.04, 1.45), (KX0 + 0.46 + k * 0.92, WALL - 0.72, 4.47), LAMINATE, bev=0.015)
lathe([(0.18, 0.0), (0.24, 0.35)], (14.3, 1.5, 5.25), TERRACOTTA, verts=12)
for k in range(7):
    leaf(14.3, 1.45, 5.55, 0.55, 0.15, (k / 7) * math.tau, 0.3 + 0.15 * (k % 3), PLANT_G, roll=1.2 if math.cos(k / 7 * math.tau) > 0 else -1.2)

# ------------------------------------------------------------ upper wall --
for (rx, rz, rw, rh) in WINDOWS[1:]:
    box((rw + 0.3, 0.2, 0.26), (rx + rw / 2, WALL - 0.1, rz + rh + 0.3), ALU, bev=0.02)     # roller blind box
    box((rw + 0.1, 0.02, 0.04), (rx + rw / 2, WALL - 0.21, rz + rh + 0.19), M("plastic", (0.6, 0.6, 0.62)))
    tube_path([(rx + rw - 0.1, WALL - 0.21, rz + rh + 0.18), (rx + rw - 0.1, WALL - 0.22, rz + rh - 0.3)], 0.008, STEEL, verts=4)
# red sprinkler main and grey conduit along the top
tube_path([(0.0, WALL - 0.15, 9.05), (15.0, WALL - 0.15, 9.05)], 0.08, M("paint", (0.45, 0.02, 0.02), wear=0.5), verts=8)
tube_path([(0.0, WALL - 0.06, 8.95), (0.6, WALL - 0.06, 8.95), (0.6, WALL - 0.06, 7.0)], 0.035, M("paint", (0.3, 0.32, 0.35)), verts=6)
box((0.35, 0.12, 0.35), (0.6, WALL - 0.06, 6.85), M("paint", (0.3, 0.32, 0.35)), bev=0.02)
# oscillating wall fan between the first two high windows
FX, FZ = 4.95, 8.1
box((0.3, 0.08, 0.4), (FX, WALL - 0.04, FZ - 0.1), M("plastic", (0.6, 0.6, 0.62)), bev=0.03)
rod((FX, WALL - 0.08, FZ), (FX, WALL - 0.4, FZ), 0.04, M("plastic", (0.6, 0.6, 0.62)), verts=8)
osc = pivot("fan_head", (FX, WALL - 0.4, FZ))
ball(0.2, (FX, WALL - 0.45, FZ), M("plastic", (0.6, 0.6, 0.62)), scale=(1, 1.4, 1), seg=12, rings=8, parent=osc)
for yy in (WALL - 0.6, WALL - 0.82):
    torus(0.55, 0.015, (FX, yy, FZ), CHROME, rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=4, parent=osc)
for k in range(8):
    a = k / 8 * math.tau
    rod((FX, WALL - 0.85, FZ), (FX + math.cos(a) * 0.55, WALL - 0.82, FZ + math.sin(a) * 0.55), 0.008, CHROME, verts=4, parent=osc)
blades = pivot("fan_blades", (FX, WALL - 0.7, FZ), parent=osc)
for k in range(3):
    a = k / 3 * math.tau
    box((0.45, 0.02, 0.2), (FX + math.cos(a) * 0.28, WALL - 0.7, FZ + math.sin(a) * 0.28), M("plastic", (0.15, 0.45, 0.7), rough=0.3),
        rot=(0.3, -a, 0), parent=blades)
spin_idle(blades, "Y", 8)
swing(osc, "Z", amp=0.5)
# the dorm TV between the second and third windows, cable dangling
TVX, TVZ = 10.05, 8.15
box((0.3, 0.2, 0.3), (TVX, WALL - 0.1, TVZ), BLACK)
box((1.95, 0.08, 1.12), (TVX, WALL - 0.24, TVZ), BLACK, bev=0.02)
box((1.85, 0.02, 1.02), (TVX, WALL - 0.285, TVZ), TV)
cable((TVX + 0.6, WALL - 0.2, TVZ - 0.56), (TVX + 1.0, WALL - 0.05, 7.0), 0.3, r=0.02, m=BLACK)
box((0.2, 0.05, 0.3), (TVX + 1.0, WALL - 0.025, 6.9), M("plastic", (0.7, 0.7, 0.68)))
# wall clock, top right
cyl(0.42, 0.08, (14.45, WALL - 0.04, 8.15), BLACK, rot=(math.pi / 2, 0, 0), verts=24, bevel=0.01)
cyl(0.37, 0.02, (14.45, WALL - 0.09, 8.15), M("plastic", (0.8, 0.8, 0.76)), rot=(math.pi / 2, 0, 0), verts=24, bevel=0)
box((0.03, 0.02, 0.26), (14.45, WALL - 0.105, 8.25), BLACK, rot=(0, 0.6, 0))
box((0.03, 0.02, 0.18), (14.45, WALL - 0.105, 8.1), BLACK, rot=(0, -1.4, 0))
box((0.012, 0.01, 0.3), (14.45, WALL - 0.115, 8.2), M("plastic", (0.7, 0.05, 0.05)), rot=(0, 2.2, 0))
# STAFF ONLY plaque over the kitchenette
box((1.6, 0.04, 0.4), (14.0, WALL - 0.02, 6.4), M("plastic", (0.6, 0.6, 0.62)))
neon_text("STAFF ONLY", 13.32, 6.3, 0.2, BLACK, y=WALL - 0.045, r=0.018, gap=0.25)

finish("backdrop_room2", windows=WINDOWS, theme=THEME)
