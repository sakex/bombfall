# Backdrop for the Hotel Electra hacker den: a converted suite that never
# sleeps.  Two open server racks full of blinking servers, switches and a
# patch panel spilling coloured cables; a battle station under the right
# window with five screens on arms, an RGB keyboard, a gaming chair that
# swivels and a glass-sided PC whose fans spin; a hologram table turning a
# wireframe globe under a 2x2 wall of screens; a workbench under the left
# window with an oscilloscope, a swing-arm lamp, a mini fridge of energy
# drinks, a can pyramid and a stack of pizza boxes; cable spaghetti on the
# floor, a wire cable tray with drooping bundles, a ROOT ACCESS neon and a
# dot-matrix world map where attacks blink.
#   blender -b --python blender/backdrop_hacker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
WINDOWS = [(10.6, 4.2, 3.6, 2.0), (0.3, 4.4, 3.0, 1.6)]
THEME = dict(wall=(0.03, 0.06, 0.11), trim=(0.25, 1.0, 0.45), floor=(0.03, 0.05, 0.09))

# ------------------------------------------------------------ materials --
RACK = M("paint", (0.03, 0.03, 0.035), rough=0.45, wear=0.7)
SERVER = pattern("paint", (0.1, 0.1, 0.11), "tiles", size=(0.16, 0.07), line=0.012, line_col=(0.02, 0.02, 0.025), plane="XZ", wear=0.3)
SERVER_B = pattern("metal", (0.4, 0.42, 0.45), "grille", size=(0.05, 0.05), plane="XZ")
SWITCH = M("plastic", (0.05, 0.06, 0.07), rough=0.4)
DESK = M("wood", (0.06, 0.05, 0.05), color2=(0.03, 0.025, 0.025), rough=0.4)
STEEL_BLK = M("paint", (0.02, 0.02, 0.025), wear=0.8)
PLASTIC = M("plastic", (0.03, 0.03, 0.035), rough=0.35)
GREY = M("plastic", (0.35, 0.36, 0.38), rough=0.5)
CHROME = M("chrome", (0.7, 0.72, 0.78))
BENCH = M("wood", (0.3, 0.2, 0.1), color2=(0.22, 0.14, 0.07), rough=0.55)
CARDBOARD = M("plastic", (0.45, 0.3, 0.14), rough=0.9, grime=0.8)
PIZZA = M("plastic", (0.7, 0.45, 0.12), rough=0.7)
PEPPERONI = M("plastic", (0.5, 0.06, 0.04), rough=0.6)
CHAIR = M("leather", (0.02, 0.02, 0.025), rough=0.4)
CHAIR_G = M("leather", (0.1, 0.6, 0.25), rough=0.4)
CAN = [M("metal", c, rough=0.25) for c in ((0.1, 0.8, 0.2), (0.85, 0.1, 0.4), (0.1, 0.3, 0.9), (0.9, 0.7, 0.05))]
CABLE = [M("rubber", c) for c in ((0.02, 0.02, 0.025), (0.5, 0.05, 0.05), (0.05, 0.2, 0.6), (0.6, 0.5, 0.05), (0.05, 0.45, 0.15), (0.5, 0.2, 0.5))]
TRAY = M("metal", (0.5, 0.52, 0.55), rough=0.4)

G_SCR = screen((0.15, 1.0, 0.35), 1.1)
C_SCR = screen((0.1, 0.6, 1.0), 1.1)
P_SCR = screen((1.0, 0.15, 0.6), 1.1)
A_SCR = screen((1.0, 0.5, 0.05), 1.1)
LED_G = glow((0.2, 1.0, 0.35), 5.0)
LED_A = glow((1.0, 0.55, 0.1), 5.0)
LED_B = glow((0.25, 0.6, 1.0), 5.0)
LED_R = glow((1.0, 0.08, 0.06), 6.0)
NEON_G = glow((0.25, 1.0, 0.45), 4.0)
NEON_P = glow((1.0, 0.2, 0.65), 4.0)
HOLO = glow((0.3, 0.9, 1.0), 3.0)
RGB = [glow(c, 4.0) for c in ((1.0, 0.2, 0.6), (0.3, 0.9, 1.0), (0.6, 0.3, 1.0))]
FRIDGE = glow((0.8, 0.95, 1.0), 1.4, base=(0.6, 0.7, 0.8))
LAMP = glow((1.0, 0.85, 0.6), 3.0)
GLASS = glass((0.5, 0.7, 0.8), alpha=0.25)
SMOKE = glass((0.8, 0.85, 0.9), alpha=0.3, rough=0.7)

moulding(0.0, 15.0, 0.0, [(0.0, 0.0), (0.04, 0.0), (0.04, 0.2), (0.0, 0.22)], STEEL_BLK)
box((15.0, 1.93, 0.02), (7.5, 0.965, 0.01), pattern("plastic", (0.05, 0.055, 0.065), "tiles", size=(0.9, 0.9), line=0.02,
                                                     line_col=(0.02, 0.02, 0.025), plane="XY", rough=0.5))

# ---------------------------------------------------------- server racks --
LED_GROUPS = [pivot("leds_%d" % k, (5.05, 0.68, 2.5)) for k in range(6)]
PATTERNS = [[(5, 12), (40, 44), (70, 90)], [(0, 6), (30, 40), (60, 64), (100, 110)], [(15, 22), (50, 52), (85, 98)],
            [(8, 10), (20, 24), (64, 80), (110, 114)], [(33, 50), (90, 92)], [(0, 3), (12, 15), (24, 27), (36, 39), (48, 51), (60, 63), (72, 75), (84, 87), (96, 99), (108, 111)]]
for p, pat in zip(LED_GROUPS, PATTERNS):
    blink(p, pat)
led_i = 0


def led(x, z, m, y=0.69):
    global led_i
    g = LED_GROUPS[led_i % len(LED_GROUPS)]
    led_i += 1
    box((0.035, 0.02, 0.03), (x, y, z), m, parent=g)


for r, rx in enumerate((4.25, 5.85)):
    fbox((1.5, 1.2, 0.12), (rx, 1.3, 0.0), RACK)
    fbox((1.5, 1.2, 0.12), (rx, 1.3, 4.95), RACK)
    for s in (-1, 1):
        fbox((0.1, 1.2, 5.07), (rx + s * 0.7, 1.3, 0.0), RACK, bev=0.01)
        fbox((0.06, 0.06, 4.83), (rx + s * 0.6, 0.75, 0.12), CHROME)          # rails
    z = 0.25
    k = 0
    seq = [0, 1, 0, 3, 1, 2, 0, 0, 1, 3, 0, 1, 0] if r == 0 else [3, 0, 1, 0, 0, 2, 1, 3, 0, 1, 0, 0, 1]
    while z < 4.8:
        kind = seq[k % len(seq)]
        if kind in (0, 3):                       # 2U server with drive bays
            h = 0.24
            box((1.18, 1.0, h - 0.02), (rx, 1.25, z + h / 2), SERVER)
            for j in range(4):
                led(rx - 0.5 + j * 0.06, z + 0.06, LED_G if (j + k) % 3 else LED_A)
            box((0.05, 0.03, 0.12), (rx + 0.52, 0.73, z + h / 2), CHROME)
        elif kind == 1:                          # switch with port LEDs
            h = 0.12
            box((1.18, 0.9, h - 0.02), (rx, 1.2, z + h / 2), SWITCH)
            for j in range(10):
                if (j + k) % 2:
                    led(rx - 0.45 + j * 0.1, z + h / 2, LED_G if j % 3 else LED_B, y=0.71)
        elif kind == 2:                          # patch panel spilling cables
            h = 0.12
            box((1.18, 0.4, h - 0.02), (rx, 0.95, z + h / 2), SWITCH)
            for j in range(6):
                x0 = rx - 0.45 + j * 0.18
                side = 1 if j > 2 else -1
                tube_path(catenary((x0, 0.7, z + 0.05), (rx + side * 0.62, 0.7, z - 0.4 - j * 0.05), 0.25, n=5),
                          0.018, CABLE[j % 6], verts=4)
        else:                                    # 4U storage with a perforated face
            h = 0.46
            box((1.18, 1.0, h - 0.02), (rx, 1.25, z + h / 2), SERVER_B)
            for j in range(3):
                led(rx + 0.4 + j * 0.06, z + h - 0.08, LED_B if j else LED_A)
        z += h + 0.03
        k += 1
    box((0.9, 0.05, 0.12), (rx, 0.72, 4.9), glow((0.25, 1.0, 0.45), 2.0))    # rack label light
# static always-on power LEDs
for rx in (4.25, 5.85):
    for j in range(8):
        box((0.03, 0.02, 0.03), (rx + 0.45, 0.69, 0.4 + j * 0.55), LED_G)
# cable drops from the tray into the racks
for x, m in ((4.0, CABLE[0]), (4.5, CABLE[2]), (5.6, CABLE[1]), (6.1, CABLE[4])):
    tube_path([(x, 1.55, 7.35), (x, 1.5, 6.4), (x, 1.45, 5.1)], 0.035, m, verts=5)

# ------------------------------------------------------ battle station --
DX0, DX1 = 10.4, 14.7
box((DX1 - DX0, 1.1, 0.09), ((DX0 + DX1) / 2, 1.3, 1.9), DESK, bev=0.02)
box((DX1 - DX0 - 0.1, 0.02, 0.03), ((DX0 + DX1) / 2, 0.74, 1.84), NEON_G)
for x in (DX0 + 0.15, DX1 - 0.15):
    fbox((0.1, 0.9, 0.08), (x, 1.3, 0.0), STEEL_BLK)
    fbox((0.1, 0.1, 1.86), (x, 1.3, 0.0), STEEL_BLK)
box((DX1 - DX0 - 0.3, 0.08, 0.1), ((DX0 + DX1) / 2, 1.7, 1.6), STEEL_BLK)
# monitors on arms: three below, two above
MON = [(12.55, 2.72, 1.55, 0.92, 0.0, C_SCR), (11.05, 2.66, 1.3, 0.8, 0.35, G_SCR), (14.05, 2.66, 1.3, 0.8, -0.35, P_SCR),
       (11.85, 3.62, 1.2, 0.68, 0.12, A_SCR), (13.25, 3.62, 1.2, 0.68, -0.12, G_SCR)]
rod((12.55, 1.75, 1.95), (12.55, 1.75, 3.7), 0.05, CHROME, verts=8)
for (mx, mz, mw, mh, yaw, scr) in MON:
    my = 1.35
    box((mw, 0.07, mh), (mx, my, mz), PLASTIC, rot=(0, 0, yaw), bev=0.02)
    box((mw - 0.07, 0.02, mh - 0.07), (mx - math.sin(yaw) * 0.0, my - 0.045, mz), scr, rot=(0, 0, yaw))
    rod((mx, my + 0.05, mz), (12.55, 1.75, min(mz, 3.6)), 0.03, CHROME, verts=6)
# lines of code on the centre screen and a radar sweep on the left one
for j in range(6):
    box((0.3 + 0.12 * (j % 3), 0.01, 0.035), (12.1 + 0.08 * (j % 2), 1.3 - 0.06, 3.0 - j * 0.11), glow((0.8, 1.0, 1.0), 3.0))
sweep = pivot("radar_sweep", (11.05, 1.28, 2.66))
box((0.34, 0.01, 0.02), (11.05 + 0.17, 1.28, 2.66), glow((0.6, 1.0, 0.6), 5.0), parent=sweep)
sweep.rotation_euler = (0, 0, 0.35)
spin_idle(sweep, "Y", 2)
# keyboard, mouse, headset, cans, a mug
box((1.05, 0.38, 0.06), (12.4, 1.0, 1.98), PLASTIC, bev=0.02)
box((0.98, 0.02, 0.02), (12.4, 0.8, 1.98), RGB[0])
box((0.98, 0.3, 0.01), (12.4, 1.0, 2.015), pattern("plastic", (0.12, 0.12, 0.14), "tiles", size=(0.07, 0.07), line=0.012, plane="XY"))
ball(0.08, (13.25, 0.95, 1.99), PLASTIC, scale=(0.8, 1.3, 0.5), seg=8, rings=6)
box((0.02, 0.2, 0.01), (13.25, 0.95, 2.03), RGB[1])
torus(0.22, 0.04, (14.35, 1.5, 2.55), PLASTIC, rot=(math.pi / 2, 0, 0), major_segments=12, minor_segments=5)
for s in (-1, 1):
    ball(0.1, (14.35 + s * 0.22, 1.5, 2.35), PLASTIC, scale=(0.6, 1, 1), seg=8, rings=6)
rod((14.35, 1.5, 1.95), (14.35, 1.5, 2.5), 0.02, CHROME, verts=6)
for j, (cx, cy) in enumerate(((10.8, 1.0), (11.05, 1.15), (10.95, 0.9))):
    cyl(0.1, 0.32, (cx, cy, 2.1), CAN[j % 4], verts=10, bevel=0.005)
cyl(0.1, 0.32, (11.35, 0.95, 1.99), CAN[1], rot=(0, math.pi / 2, 0.4), verts=10, bevel=0.005)   # empty, on its side
# gaming chair (rear three-quarter) that swivels a little
ch = pivot("chair", (13.3, 0.55, 0.0))
for k in range(5):
    a = k / 5 * math.tau
    rod((13.3, 0.55, 0.15), (13.3 + math.cos(a) * 0.6, 0.55 + math.sin(a) * 0.35, 0.08), 0.04, CHROME, verts=5, parent=ch)
    ball(0.07, (13.3 + math.cos(a) * 0.6, 0.55 + math.sin(a) * 0.35, 0.07), PLASTIC, seg=6, rings=4, parent=ch)
cyl(0.07, 0.9, (13.3, 0.55, 0.6), CHROME, verts=8, bevel=0, parent=ch)
pill((1.1, 0.9, 0.28), (13.3, 0.55, 1.15), CHAIR, parent=ch, round_=0.1)
pill((1.05, 0.28, 2.1), (13.3, 0.62, 2.35), CHAIR, rot=(-0.12, 0, 0), parent=ch, round_=0.12)
for s in (-1, 1):
    box((0.12, 0.05, 1.9), (13.3 + s * 0.3, 0.46, 2.3), CHAIR_G, rot=(-0.12, 0, 0), parent=ch)
pill((0.6, 0.2, 0.3), (13.3, 0.55, 3.3), CHAIR, parent=ch)
ch.rotation_euler = (0, 0, -0.35)
swing(ch, "Z", amp=0.18)
# glass-sided PC tower with spinning RGB fans
PC = (14.1, 1.1, 0.12)
fbox((0.55, 1.1, 1.3), PC, PLASTIC, bev=0.03)
box((0.03, 1.0, 1.2), (PC[0] - 0.285, PC[1], 0.77), GLASS)
for k, zc in enumerate((0.45, 1.05)):
    torus(0.2, 0.025, (PC[0] - 0.26, PC[1] + 0.1, zc), RGB[k], rot=(0, math.pi / 2, 0), major_segments=14, minor_segments=4)
    f = pivot("pc_fan_%d" % k, (PC[0] - 0.25, PC[1] + 0.1, zc))
    for j in range(5):
        a = j / 5 * math.tau
        box((0.03, 0.18, 0.08), (PC[0] - 0.25, PC[1] + 0.1 + math.cos(a) * 0.1, zc + math.sin(a) * 0.1), GREY, rot=(a, 0, 0), parent=f)
    spin_idle(f, "X", 6)
box((0.03, 0.9, 0.04), (PC[0] - 0.29, PC[1], 1.35), RGB[2])

# -------------------------------------------- hologram table, screen wall --
HX = 8.5
for k, (sx, sz, scr) in enumerate(((7.65, 5.1, G_SCR), (9.35, 5.1, P_SCR), (7.65, 6.45, C_SCR), (9.35, 6.45, A_SCR))):
    box((1.62, 0.08, 1.28), (sx, WALL - 0.04, sz), PLASTIC, bev=0.02)
    box((1.54, 0.02, 1.2), (sx, WALL - 0.09, sz), scr)
    for j in range(3):
        box((0.9 - 0.2 * j, 0.01, 0.05), (sx - 0.2 + 0.1 * j, WALL - 0.1, sz + 0.3 - j * 0.2), glow((0.9, 1.0, 1.0), 2.5))
lathe([(0.35, 0.0), (0.2, 0.1), (0.14, 1.2), (0.55, 1.35), (0.6, 1.5)], (HX, 0.9, 0.0), STEEL_BLK, verts=16)
torus(0.55, 0.03, (HX, 0.9, 1.52), HOLO, major_segments=18, minor_segments=4)
cyl(0.4, 0.02, (HX, 0.9, 1.53), glow((0.3, 0.9, 1.0), 1.5), verts=16, bevel=0)
holo = pivot("holo_globe", (HX, 0.9, 2.45))
for k in range(3):
    torus(0.7, 0.018, (HX, 0.9, 2.45), HOLO, rot=(math.pi / 2, 0, k * math.pi / 3), major_segments=20, minor_segments=3, parent=holo)
for z, r in ((2.45, 0.7), (2.8, 0.6), (2.1, 0.6)):
    torus(r, 0.015, (HX, 0.9, z), HOLO, major_segments=18, minor_segments=3, parent=holo)
for k in range(5):
    a = k / 5 * math.tau
    ball(0.05, (HX + math.cos(a) * 0.55, 0.9 + math.sin(a) * 0.55, 2.45 + 0.3 * math.sin(3 * a)), glow((1.0, 0.3, 0.6), 5.0),
         seg=6, rings=4, parent=holo)
spin_idle(holo, "Z", 1)
ring = pivot("holo_ring", (HX, 0.9, 2.45))
torus(1.0, 0.012, (HX, 0.9, 2.45), glow((1.0, 0.3, 0.7), 3.0), rot=(0.4, 0, 0), major_segments=24, minor_segments=3, parent=ring)
spin_idle(ring, "Z", -1)

# ------------------------------------------------------------- workbench --
WB0, WB1 = 0.35, 3.3
box((WB1 - WB0, 1.05, 0.1), ((WB0 + WB1) / 2, 1.35, 1.85), BENCH, bev=0.02)
for x in (WB0 + 0.1, WB1 - 0.1):
    fbox((0.1, 1.0, 1.8), (x, 1.35, 0.0), STEEL_BLK)
# mini fridge of energy drinks under the bench
fbox((1.2, 0.95, 1.4), (1.0, 1.4, 0.05), PLASTIC, bev=0.03)
box((1.0, 0.02, 1.15), (1.0, 0.92, 0.77), FRIDGE)
for r in range(2):
    for c in range(4):
        cyl(0.09, 0.3, (0.7 + c * 0.2, 1.05, 0.28 + r * 0.55), CAN[(r + c) % 4], verts=8, bevel=0)
box((1.05, 0.02, 1.2), (1.0, 0.9, 0.77), GLASS)
# oscilloscope, swing-arm lamp, soldering smoke, a can pyramid
fbox((1.1, 0.8, 0.75), (1.1, 1.45, 1.9), GREY, bev=0.04)
box((0.6, 0.02, 0.45), (0.95, 1.04, 2.3), G_SCR)
wave = [(0.7 + 0.5 * i / 12, 1.02, 2.3 + 0.12 * math.sin(i * 1.2)) for i in range(13)]
tube_path(wave, 0.01, glow((0.6, 1.0, 0.7), 5.0), verts=4, cap=False)
for j in range(3):
    cyl(0.04, 0.03, (1.45 + (j % 2) * 0.12, 1.04, 2.1 + j * 0.13), CHROME, rot=(math.pi / 2, 0, 0), verts=8, bevel=0)
tube_path([(2.3, 1.7, 1.95), (2.25, 1.6, 2.9), (2.65, 1.3, 3.5), (2.95, 1.2, 3.3)], 0.03, STEEL_BLK, verts=6)
lathe([(0.22, 0.0), (0.1, 0.25), (0.06, 0.3)], (2.95, 1.2, 3.02), STEEL_BLK, verts=12, cap_top=True)
cyl(0.2, 0.01, (2.95, 1.2, 3.03), LAMP, verts=12, bevel=0)
fbox((0.4, 0.4, 0.12), (2.2, 1.1, 1.9), STEEL_BLK, bev=0.02)
rod((2.3, 1.1, 2.02), (2.55, 1.0, 2.2), 0.02, CHROME, verts=4)
for j in range(2):
    sm = pivot("solder_smoke_%d" % j, (2.56, 1.0, 2.22))
    ball(0.05, (2.56, 1.0, 2.22), SMOKE, seg=6, rings=4, parent=sm)
    puff(sm, rise=0.7, grow=2.5, start=j * 60, life=60, drift=0.15)
for row, n in enumerate((3, 2, 1)):
    for c in range(n):
        cyl(0.1, 0.32, (2.75 + c * 0.21 + row * 0.105, 1.55, 1.9 + 0.16 + row * 0.33), CAN[(row + c) % 4], verts=8, bevel=0.005)
# pizza boxes on the floor, the top one open
PZ = (2.3, 0.65)
for k in range(3):
    box((1.1, 1.0, 0.1), (PZ[0] + 0.03 * (k % 2), PZ[1], 0.05 + k * 0.1), CARDBOARD, rot=(0, 0, 0.05 * (k - 1)), bev=0.01)
box((1.1, 1.0, 0.03), (PZ[0], PZ[1], 0.3), CARDBOARD)
box((1.1, 0.03, 1.0), (PZ[0], PZ[1] + 0.52, 0.8), CARDBOARD, rot=(-0.2, 0, 0))
cyl(0.45, 0.03, (PZ[0], PZ[1], 0.33), PIZZA, verts=16, bevel=0)
for k in range(5):
    a = k * 1.3
    cyl(0.07, 0.01, (PZ[0] + math.cos(a) * 0.25, PZ[1] + math.sin(a) * 0.25, 0.35), PEPPERONI, verts=8, bevel=0)
# cans and crushed cans around the chair
for k, (cx, cy, rot) in enumerate(((9.9, 0.4, 0), (10.2, 0.25, 1.4), (3.4, 0.35, 0), (7.1, 0.3, 1.2))):
    cyl(0.1, 0.32 if rot == 0 else 0.2, (cx, cy, 0.16 if rot == 0 else 0.1), CAN[k % 4], rot=(0, rot, 0.5 * k), verts=8, bevel=0.005)

# ------------------------------------------------------ floor cables --
for k in range(7):
    x0 = 3.8 + 0.25 * k
    x1 = [12.0, 8.5, 1.5, 14.0, 10.8, 2.8, 8.9][k]
    y0 = 0.9 + 0.05 * k
    pts = [(x0, y0, 0.5), (x0 + 0.1, y0 - 0.2, 0.04)]
    steps = 5
    for i in range(1, steps + 1):
        t = i / steps
        pts.append((x0 + (x1 - x0) * t, 0.35 + 0.35 * math.sin(k * 1.7 + t * 5.0) + 0.1 * k / 7, 0.04))
    pts.append((x1, 0.9, 0.3))
    tube_path(pts, 0.03, CABLE[k % 6], verts=4)
fbox((0.9, 0.2, 0.08), (7.2, 0.7, 0.0), PLASTIC, bev=0.02)                         # power strip
for j in range(5):
    box((0.06, 0.02, 0.03), (6.9 + j * 0.15, 0.59, 0.05), LED_R if j == 0 else PLASTIC)

# ------------------------------------------------------------ upper wall --
# wire cable tray with drooping bundles
TZ = 7.35
for y in (1.55, 1.95 - 0.02):
    rod((0.2, y, TZ), (14.8, y, TZ), 0.02, TRAY, verts=4)
rod((0.2, 1.55, TZ - 0.12), (14.8, 1.55, TZ - 0.12), 0.02, TRAY, verts=4)
for k in range(15):
    x = 0.4 + k * 1.0
    rod((x, 1.55, TZ - 0.12), (x, 1.55, TZ), 0.015, TRAY, verts=4)
    rod((x, 1.55, TZ - 0.12), (x, WALL, TZ - 0.12), 0.015, TRAY, verts=4)
for k in range(5):
    tube_path([(0.2, 1.7 + 0.04 * k, TZ - 0.06 + 0.03 * k), (14.8, 1.7 + 0.04 * k, TZ - 0.06 + 0.03 * k)], 0.03, CABLE[k], verts=4, cap=False)
for k, (x0, x1, sag) in enumerate(((1.0, 3.6, 0.7), (6.8, 9.8, 0.9), (10.4, 12.2, 0.5))):
    sw = pivot("cable_%d" % k, ((x0 + x1) / 2, 1.5, TZ))
    for j in range(2):
        tube_path(catenary((x0, 1.5 - 0.05 * j, TZ - 0.1), (x1, 1.5 - 0.05 * j, TZ - 0.1), sag + 0.12 * j, n=8), 0.03,
                  CABLE[(k + j) % 6], verts=4, parent=sw)
    swing(sw, "X", amp=0.12, phase=k * 2.0)
# ROOT ACCESS neon with a flickering letter, and a 404 in pink
w = neon_text("ROOT ACCESS", 0.8, 8.05, 0.58, NEON_G, flicker_idx=(2, 8), seed=31, aspect=0.55, gap=0.25)
tube_path([(0.6, WALL - 0.06, 7.85), (0.8 + w + 0.2, WALL - 0.06, 7.85)], 0.02, NEON_G, verts=5, cap=False)
neon_text("<>", 0.8 + w + 0.4, 8.05, 0.58, NEON_P, aspect=0.5)
# dot-matrix world map with blinking attack points
MX0, MZ0 = 8.9, 7.85
box((5.8, 0.05, 1.5), (MX0 + 2.9, WALL - 0.025, MZ0 + 0.7), M("paint", (0.02, 0.025, 0.03), rough=0.8), bev=0.02)
land = ["..XXX.....XX.XXXX..", ".XXXXX...XXXXXXXXX.", "..XXX....XXXXXXXX..", "...XX....XXX..XXX..", "....X.....X....X.XX", "..........X.....XX."]
DOT = glow((0.2, 0.7, 0.4), 2.0)
for r, row in enumerate(land):
    for c, ch_ in enumerate(row):
        if ch_ == "X":
            box((0.12, 0.02, 0.12), (MX0 + 0.3 + c * 0.28, WALL - 0.06, MZ0 + 1.25 - r * 0.2), DOT)
atk = pivot("attacks", (MX0 + 2.9, WALL - 0.07, MZ0 + 0.7))
for (c, r) in ((3, 1), (11, 2), (15, 1), (16, 4)):
    ball(0.1, (MX0 + 0.3 + c * 0.28, WALL - 0.08, MZ0 + 1.25 - r * 0.2), LED_R, seg=6, rings=4, parent=atk)
blink(atk, [(10, 20), (40, 45), (70, 90), (100, 105)])
finish("backdrop_hacker", windows=WINDOWS, theme=THEME)
