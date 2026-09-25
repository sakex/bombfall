# Backdrop for the Hotel Electra washroom (toilet1): glossy lavender tiles
# to shoulder height with a magenta/cyan mosaic border and a black-and-white
# checker floor; three magenta laminate stalls on chrome pilasters (someone's
# sneakers under the middle door, the last door ajar on a toilet) under
# old high-level cisterns whose pull chains swing; three wall-hung urinals
# with blinking sensor eyes and privacy screens under the window; a marble
# vanity with vessel basins, gooseneck taps (one drips) and backlit mirrors
# under a flickering tube light; a hand dryer, a pedal bin, a mop bucket and
# a wet-floor sign; up top copper pipes, a pictogram neon, a spinning
# extractor fan and an air freshener that puffs.
#   blender -b --python blender/backdrop_toilet1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
WINDOWS = [(7.0, 3.2, 3.6, 1.6), (2.0, 7.9, 2.0, 1.0), (6.5, 7.9, 2.0, 1.0), (11.0, 7.9, 2.0, 1.0)]
THEME = dict(wall=(0.06, 0.09, 0.21), trim=(0.35, 0.9, 1.0), floor=(0.05, 0.08, 0.16))

# ------------------------------------------------------------ materials --
TILE = pattern("ceramic", (0.3, 0.3, 0.4), "tiles", size=(0.3, 0.3), line=0.022, line_col=(0.12, 0.12, 0.16), plane="XZ")
MOSAIC = pattern("ceramic", (0.5, 0.04, 0.32), "checker", size=(0.1, 0.1), line=0.012, line_col=(0.02, 0.35, 0.42), plane="XZ")
FLOOR = pattern("ceramic", (0.62, 0.62, 0.66), "checker", size=(0.45, 0.45), line=0.015, line_col=(0.03, 0.03, 0.04), plane="XY")
PORCELAIN = M("ceramic", (0.78, 0.8, 0.84))
CHROME = M("chrome", (0.72, 0.74, 0.8))
STEEL = M("metal", (0.5, 0.52, 0.56))
LAMINATE = M("plastic", (0.2, 0.02, 0.15), rough=0.35, wear=0.35, grime=0.6)
MARBLE = M("marble", (0.08, 0.08, 0.1), color2=(0.5, 0.5, 0.55))
COPPER = M("metal", (0.55, 0.25, 0.12), rough=0.35)
IRON = M("paint", (0.03, 0.03, 0.035), wear=0.8)
YELLOW = M("plastic", (0.75, 0.55, 0.02), rough=0.35, wear=0.4)
BLACK = M("plastic", (0.015, 0.015, 0.02), rough=0.3)
MIRROR = M("chrome", (0.1, 0.13, 0.18), rough=0.03)
MOP = M("fabric", (0.55, 0.52, 0.45), grime=1.0)

SENSOR = glow((1.0, 0.1, 0.1), 5.0)
MIRROR_HALO = glow((0.3, 0.9, 1.0), 3.0)
TUBE = glow((0.85, 0.95, 1.0), 4.0)
OCC_RED = glow((1.0, 0.1, 0.1), 3.0)
OCC_GREEN = glow((0.2, 1.0, 0.3), 3.0)
NEON_C = glow((0.3, 0.9, 1.0), 4.0)
NEON_P = glow((1.0, 0.25, 0.65), 4.0)
SHEEN = glow((0.75, 0.85, 1.0), 0.35, base=(0.3, 0.33, 0.38))
WATER = glass((0.6, 0.85, 1.0), alpha=0.5)
MIST = glass((0.85, 1.0, 0.9), alpha=0.3, rough=0.6)
PUCK = M("plastic", (0.05, 0.3, 0.8), rough=0.5)

# ------------------------------------------------- tiles, floor, borders --
TILE_TOP = 5.3
for (x, z, w, h) in wall_rects(15.0, TILE_TOP, [(7.0 - 0.13, 3.2 - 0.13, 3.86, 1.86)]):
    box((w, 0.03, h), (x + w / 2, WALL - 0.015, z + h / 2), TILE)
for (x, z, w, h) in wall_rects(15.0, 0.25, []):
    box((w, 0.03, h), (x + w / 2, WALL - 0.015, TILE_TOP + h / 2), MOSAIC)
moulding(0.0, 15.0, TILE_TOP + 0.25, [(0.0, 0.0), (0.04, 0.0), (0.04, 0.05), (0.0, 0.07)], CHROME)
moulding(0.0, 15.0, TILE_TOP - 0.02, [(0.0, 0.0), (0.04, 0.0), (0.04, 0.03), (0.0, 0.04)], CHROME)
box((15.0, 1.93, 0.02), (7.5, 0.965, 0.01), FLOOR)
moulding(0.0, 15.0, 0.0, [(0.0, 0.0), (0.06, 0.0), (0.06, 0.1), (0.0, 0.25)], M("ceramic", (0.1, 0.1, 0.12)))

# ---------------------------------------------------------------- stalls --
PIL = [0.15, 2.4, 4.65, 6.9]
for x in PIL:
    fbox((0.14, 0.14, 4.95), (x, 0.24, 0.05), CHROME, bev=0.01)
    fbox((0.2, 0.2, 0.08), (x, 0.24, 0.0), CHROME, bev=0.01)
    fbox((0.05, 1.6, 4.55), (x, 1.08, 0.45), LAMINATE, bev=0.01)          # partition, seen edge on
box((PIL[-1] - PIL[0] + 0.1, 0.1, 0.08), ((PIL[0] + PIL[-1]) / 2, 0.24, 5.02), CHROME)   # headrail
for i in range(3):
    x0, x1 = PIL[i] + 0.07, PIL[i + 1] - 0.07
    cx = (x0 + x1) / 2
    # toilet at the back (its pedestal shows in the gap under the door)
    lathe([(0.3, 0.0), (0.26, 0.3), (0.34, 0.8), (0.42, 1.05)], (cx - 0.2 if i == 2 else cx, 1.35, 0.02), PORCELAIN, verts=14)
    fbox((0.9, 0.35, 0.9), (cx - 0.2 if i == 2 else cx, 1.75, 1.0), PORCELAIN, bev=0.05)
    # cistern high on the wall with a chain that swings
    cz = 6.25
    fbox((1.05, 0.45, 0.55), (cx, WALL - 0.25, cz), PORCELAIN, bev=0.05, seg=2)
    for s in (-1, 1):
        tube_path([(cx + s * 0.4, WALL - 0.02, cz + 0.1), (cx + s * 0.4, WALL - 0.4, cz + 0.02)], 0.03, IRON, verts=5)
    rod((cx - 0.3, WALL - 0.2, cz), (cx - 0.3, WALL - 0.2, 5.1), 0.045, CHROME, verts=8)
    rod((cx + 0.5, WALL - 0.35, cz + 0.45), (cx + 0.75, WALL - 0.35, cz + 0.45), 0.02, IRON, verts=6)
    ch = pivot("chain_%d" % i, (cx + 0.75, WALL - 0.35, cz + 0.45))
    for k in range(9):
        z = cz + 0.42 - k * 0.2
        torus(0.04, 0.01, (cx + 0.75, WALL - 0.35, z), CHROME, rot=(math.pi / 2, 0, (k % 2) * math.pi / 2),
              major_segments=6, minor_segments=3, parent=ch)
    lathe([(0.04, 0.0), (0.07, 0.1), (0.06, 0.22), (0.02, 0.26)], (cx + 0.75, WALL - 0.35, cz + 0.45 - 2.1), PORCELAIN,
          verts=8, parent=ch)
    swing(ch, "Y", amp=0.06 + 0.02 * i, phase=i * 1.9)
    if i == 2:
        # door ajar, swung into the stall, hinged at the right pilaster
        th = 0.8
        hx = x1 - 0.02
        door = box((x1 - x0, 0.05, 4.3), (hx - math.cos(th) * (x1 - x0) / 2, 0.3 + math.sin(th) * (x1 - x0) / 2, 2.6),
                   LAMINATE, rot=(0, 0, th), bev=0.02)
        cyl(0.12, 0.08, (cx - 0.55, 1.5, 3.2), CHROME, rot=(math.pi / 2, 0, 0), verts=10, bevel=0)   # paper holder
        cyl(0.1, 0.25, (cx - 0.55, 1.38, 3.1), M("fabric", (0.8, 0.8, 0.8)), rot=(0, math.pi / 2, 0), verts=10, bevel=0)
        box((0.3, 0.02, 0.1), (cx, 0.18, 4.65), OCC_GREEN)
        continue
    box((x1 - x0, 0.05, 4.3), (cx, 0.3, 2.6), LAMINATE, bev=0.02)
    for zz in (1.1, 4.0):
        box((0.06, 0.08, 0.3), (x1 - 0.1, 0.25, zz), CHROME, bev=0.01)      # hinges
    box((0.25, 0.06, 0.12), (x0 + 0.22, 0.25, 2.5), CHROME, bev=0.02)         # latch
    box((0.3, 0.02, 0.1), (cx, 0.26, 4.65), OCC_RED if i == 1 else OCC_GREEN)
    ball(0.06, (cx + 0.5, 0.26, 4.35), CHROME, seg=8, rings=6)                  # coat hook knob
    if i == 1:
        for dx in (-0.25, 0.25):
            pill((0.3, 0.75, 0.22), (cx + dx, 0.75, 0.11), M("fabric", (0.85, 0.2, 0.3)), rot=(0, 0, dx * 0.4))

# ---------------------------------------------------- urinals and screens --
for i, ux in enumerate((7.65, 8.85, 10.05)):
    pill((0.85, 0.6, 1.5), (ux, WALL - 0.3, 1.95), PORCELAIN, seg=3, round_=0.22)
    ball(0.3, (ux, WALL - 0.55, 1.75), M("ceramic", (0.3, 0.32, 0.36)), scale=(1, 0.3, 1.6), seg=12, rings=8)
    ball(0.08, (ux, WALL - 0.5, 1.35), PUCK, scale=(1.2, 1.0, 0.5), seg=8, rings=4)
    fbox((0.4, 0.2, 0.22), (ux, WALL - 0.12, 2.78), CHROME, bev=0.03)
    eye = pivot("urinal_eye_%d" % i, (ux, WALL - 0.225, 2.9))
    ball(0.03, (ux, WALL - 0.225, 2.9), SENSOR, seg=6, rings=4, parent=eye)
    blink(eye, [(10 + 30 * i, 20 + 30 * i)] if i != 1 else [(0, 100)])
    tube_path([(ux, WALL - 0.25, 1.22), (ux, WALL - 0.25, 1.0), (ux, WALL - 0.05, 0.85)], 0.05, CHROME, verts=8)
for sx in (8.25, 9.45):
    fbox((0.06, 0.95, 2.25), (sx, WALL - 0.5, 0.8), LAMINATE, bev=0.02)
    for zz in (1.1, 2.8):
        box((0.1, 0.1, 0.1), (sx, WALL - 0.05, zz), CHROME)

# ------------------------------------------------------------- vanity --
VX0, VX1 = 11.0, 14.05
box((VX1 - VX0, 1.1, 0.12), ((VX0 + VX1) / 2, WALL - 0.55, 2.1), MARBLE, bev=0.02)
box((VX1 - VX0, 0.06, 0.35), ((VX0 + VX1) / 2, WALL - 1.1, 1.9), MARBLE, bev=0.01)
for x in (VX0 + 0.3, VX1 - 0.3):
    box((0.08, 0.6, 0.08), (x, WALL - 0.3, 1.8), CHROME)
for i, bx in enumerate((11.75, 13.3)):
    lathe([(0.12, 0.0), (0.38, 0.1), (0.5, 0.3), (0.5, 0.36), (0.46, 0.36)], (bx, WALL - 0.6, 2.16), PORCELAIN, verts=18)
    cyl(0.45, 0.02, (bx, WALL - 0.6, 2.46), M("ceramic", (0.3, 0.32, 0.36)), verts=16, bevel=0)
    tube_path([(bx, WALL - 0.2, 2.16), (bx, WALL - 0.2, 3.0), (bx, WALL - 0.3, 3.12), (bx, WALL - 0.5, 3.1),
               (bx, WALL - 0.52, 2.9)], 0.035, CHROME, verts=8)
    box((0.08, 0.05, 0.14), (bx + 0.16, WALL - 0.2, 2.35), CHROME, bev=0.01)
    tube_path([(bx, WALL - 0.6, 2.16), (bx, WALL - 0.6, 1.3), (bx, WALL - 0.4, 1.15), (bx, WALL - 0.02, 1.15)],
              0.045, CHROME, verts=8)
    # backlit mirror
    box((1.35, 0.01, 2.05), (bx, WALL - 0.005, 3.95), MIRROR_HALO)
    box((1.25, 0.05, 1.95), (bx, WALL - 0.04, 3.95), BLACK, bev=0.03)
    box((1.2, 0.02, 1.9), (bx, WALL - 0.07, 3.95), MIRROR)
    box((0.05, 0.01, 1.3), (bx - 0.2, WALL - 0.085, 4.0), SHEEN, rot=(0, 0.5, 0))
    # soap pump
    lathe([(0.09, 0.0), (0.09, 0.25), (0.03, 0.3)], (bx + 0.55, WALL - 0.45, 2.16), M("plastic", (0.6, 0.1, 0.35), rough=0.1), verts=10)
    rod((bx + 0.55, WALL - 0.45, 2.46), (bx + 0.55, WALL - 0.6, 2.5), 0.015, CHROME, verts=4)
# a drip from the first tap
for k in range(2):
    d = pivot("drip_%d" % k, (11.75, WALL - 0.52, 2.86))
    ball(0.035, (11.75, WALL - 0.52, 2.86), WATER, scale=(1, 1, 1.3), seg=6, rings=4, parent=d)
    puff(d, rise=-0.35, grow=1.0, start=k * 60, life=22)
# flickering tube light over the mirrors
box((VX1 - VX0, 0.2, 0.12), ((VX0 + VX1) / 2, WALL - 0.1, 5.1), STEEL, bev=0.015)
tl = pivot("vanity_tube", ((VX0 + VX1) / 2, WALL - 0.22, 5.08))
rod((VX0 + 0.1, WALL - 0.22, 5.06), (VX1 - 0.1, WALL - 0.22, 5.06), 0.035, TUBE, verts=6, parent=tl)
flicker(tl, seed=7, bursts=3)
# hand dryer, pedal bin
fbox((0.75, 0.5, 0.95), (14.55, WALL - 0.25, 2.6), CHROME, bev=0.1, seg=2)
box((0.4, 0.2, 0.06), (14.55, WALL - 0.45, 2.62), BLACK, bev=0.02)
box((0.1, 0.02, 0.04), (14.55, WALL - 0.505, 3.3), glow((0.2, 0.6, 1.0), 4.0))
lathe([(0.35, 0.0), (0.38, 1.3), (0.36, 1.4)], (14.55, 1.2, 0.0), M("metal", (0.55, 0.56, 0.6)), verts=16)
lathe([(0.38, 0.0), (0.32, 0.1), (0.0, 0.12)], (14.55, 1.2, 1.4), M("metal", (0.55, 0.56, 0.6)), verts=16)
box((0.3, 0.2, 0.05), (14.55, 0.78, 0.05), IRON)

# ------------------------------------------- mop bucket and wet floor sign --
MB = (6.2, 0.45)
fbox((1.2, 0.8, 0.8), (MB[0], MB[1], 0.18), YELLOW, bev=0.08, seg=2)
box((1.05, 0.65, 0.04), (MB[0], MB[1], 0.96), M("plastic", (0.25, 0.3, 0.2), rough=0.05))
for dx in (-0.45, 0.45):
    cyl(0.09, 0.07, (MB[0] + dx, MB[1] - 0.3, 0.09), BLACK, rot=(0, math.pi / 2, 0), verts=8, bevel=0)
fbox((0.5, 0.4, 0.5), (MB[0] + 0.25, MB[1] + 0.05, 0.98), M("plastic", (0.5, 0.05, 0.05), rough=0.4), bev=0.04)
rod((MB[0] + 0.5, MB[1] + 0.05, 1.3), (MB[0] + 0.9, MB[1] + 0.05, 1.9), 0.03, CHROME, verts=6)
rod((MB[0] - 0.2, MB[1] + 0.1, 0.9), (MB[0] - 0.6, MB[1] + 0.3, 3.4), 0.035, M("plastic", (0.1, 0.3, 0.7), rough=0.3), verts=6)
for k in range(7):
    a = (k / 7 - 0.5) * 1.6
    rod((MB[0] - 0.18, MB[1] + 0.1, 0.95), (MB[0] - 0.18 + math.sin(a) * 0.3, MB[1] + 0.05, 0.62), 0.04, MOP, verts=4)
# A-frame wet-floor sign
WS = (7.4, 0.4)
for s in (-1, 1):
    box((0.8, 0.05, 1.6), (WS[0], WS[1] + s * 0.15, 0.78), YELLOW, rot=(s * 0.2, 0, 0), bev=0.03)
box((0.5, 0.02, 0.35), (WS[0], WS[1] - 0.18, 1.0), BLACK, rot=(-0.2, 0, 0))
extrude_xz([(WS[0] - 0.12, 1.3), (WS[0] + 0.12, 1.3), (WS[0], 1.52)], WS[1] - 0.2, WS[1] - 0.16, BLACK)

# ------------------------------------------------------------ upper wall --
# copper pipes with valves
tube_path([(0.0, WALL - 0.12, 7.35), (15.0, WALL - 0.12, 7.35)], 0.07, COPPER, verts=8)
tube_path([(0.0, WALL - 0.3, 7.55), (15.0, WALL - 0.3, 7.55)], 0.05, COPPER, verts=8)
for x in (1.28, 3.53, 5.78):
    tube_path([(x, WALL - 0.3, 7.55), (x, WALL - 0.3, 6.8)], 0.035, COPPER, verts=6)
for x in (0.8, 5.0, 14.2):
    cyl(0.1, 0.18, (x, WALL - 0.12, 7.35), COPPER, rot=(0, math.pi / 2, 0), verts=10, bevel=0.01)
    torus(0.14, 0.025, (x, WALL - 0.12, 7.62), M("paint", (0.6, 0.05, 0.05)), major_segments=10, minor_segments=4)
    rod((x, WALL - 0.12, 7.35), (x, WALL - 0.12, 7.62), 0.02, COPPER, verts=4)
# restroom pictogram neon between the first high windows
PX, PZ = 5.25, 8.3
torus(0.12, 0.022, (PX - 0.45, WALL - 0.06, PZ + 0.45), NEON_C, rot=(math.pi / 2, 0, 0), major_segments=12, minor_segments=4)
tube_path([(PX - 0.7, WALL - 0.06, PZ + 0.1), (PX - 0.45, WALL - 0.06, PZ + 0.28), (PX - 0.2, WALL - 0.06, PZ + 0.1)], 0.022, NEON_C, verts=5, cap=False)
tube_path([(PX - 0.45, WALL - 0.06, PZ + 0.28), (PX - 0.45, WALL - 0.06, PZ - 0.1), (PX - 0.6, WALL - 0.06, PZ - 0.45)], 0.022, NEON_C, verts=5, cap=False)
tube_path([(PX - 0.45, WALL - 0.06, PZ - 0.1), (PX - 0.3, WALL - 0.06, PZ - 0.45)], 0.022, NEON_C, verts=5, cap=False)
tube_path([(PX, WALL - 0.06, PZ + 0.65), (PX, WALL - 0.06, PZ - 0.5)], 0.015, glow((0.9, 0.9, 1.0), 3.0), verts=5, cap=False)
wm = pivot("neon_woman", (PX + 0.45, WALL - 0.06, PZ))
torus(0.12, 0.022, (PX + 0.45, WALL - 0.06, PZ + 0.45), NEON_P, rot=(math.pi / 2, 0, 0), major_segments=12, minor_segments=4, parent=wm)
tube_path([(PX + 0.45, WALL - 0.06, PZ + 0.3), (PX + 0.2, WALL - 0.06, PZ - 0.15), (PX + 0.7, WALL - 0.06, PZ - 0.15),
           (PX + 0.45, WALL - 0.06, PZ + 0.3)], 0.022, NEON_P, verts=5, cap=False, parent=wm)
tube_path([(PX + 0.38, WALL - 0.06, PZ - 0.15), (PX + 0.38, WALL - 0.06, PZ - 0.45)], 0.022, NEON_P, verts=5, cap=False, parent=wm)
tube_path([(PX + 0.52, WALL - 0.06, PZ - 0.15), (PX + 0.52, WALL - 0.06, PZ - 0.45)], 0.022, NEON_P, verts=5, cap=False, parent=wm)
flicker(wm, seed=13, bursts=2)
# extractor fan in a round grille
EX, EZ = 9.75, 8.35
cyl(0.62, 0.12, (EX, WALL - 0.06, EZ), STEEL, rot=(math.pi / 2, 0, 0), verts=20, bevel=0.02)
cyl(0.55, 0.02, (EX, WALL - 0.1, EZ), BLACK, rot=(math.pi / 2, 0, 0), verts=20, bevel=0)
fanp = pivot("extractor", (EX, WALL - 0.14, EZ))
for k in range(5):
    a = k / 5 * math.tau
    box((0.5, 0.02, 0.2), (EX + math.cos(a) * 0.28, WALL - 0.14, EZ + math.sin(a) * 0.28), STEEL, rot=(0.35, -a, 0), parent=fanp)
spin_idle(fanp, "Y", 6)
for k in range(5):
    torus(0.12 + k * 0.11, 0.012, (EX, WALL - 0.2, EZ), CHROME, rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=3)
rod((EX - 0.6, WALL - 0.2, EZ), (EX + 0.6, WALL - 0.2, EZ), 0.012, CHROME, verts=4)
rod((EX, WALL - 0.2, EZ - 0.6), (EX, WALL - 0.2, EZ + 0.6), 0.012, CHROME, verts=4)
# air freshener that puffs a little mist
AF = (14.1, 8.1)
fbox((0.4, 0.25, 0.6), (AF[0], WALL - 0.13, AF[1] - 0.3), M("plastic", (0.75, 0.75, 0.78), rough=0.3), bev=0.06)
box((0.06, 0.02, 0.06), (AF[0] + 0.1, WALL - 0.26, AF[1] - 0.2), glow((0.2, 1.0, 0.4), 4.0))
for k in range(2):
    mp = pivot("mist_%d" % k, (AF[0], WALL - 0.3, AF[1] + 0.25))
    ball(0.1, (AF[0], WALL - 0.3, AF[1] + 0.25), MIST, seg=8, rings=6, parent=mp)
    puff(mp, rise=0.5, grow=3.0, start=10 + k * 8, life=40, drift=-0.3)

# a no-smoking sign over the urinals and a CCTV camera panning from the corner
box((0.9, 0.04, 0.9), (8.85, WALL - 0.02, 6.1), M("plastic", (0.8, 0.8, 0.8), rough=0.4), bev=0.02)
torus(0.33, 0.04, (8.85, WALL - 0.05, 6.1), M("plastic", (0.7, 0.03, 0.03), rough=0.4), rot=(math.pi / 2, 0, 0), major_segments=20, minor_segments=4)
box((0.5, 0.02, 0.1), (8.85, WALL - 0.05, 6.1), BLACK)
box((0.66, 0.02, 0.07), (8.85, WALL - 0.06, 6.1), M("plastic", (0.7, 0.03, 0.03), rough=0.4), rot=(0, 0.785, 0))
box((0.3, 0.3, 0.1), (14.6, WALL - 0.15, 6.95), BLACK)
rod((14.6, WALL - 0.2, 6.95), (14.6, WALL - 0.45, 6.85), 0.04, BLACK, verts=6)
cam = pivot("cctv", (14.6, WALL - 0.45, 6.85))
box((0.25, 0.6, 0.25), (14.6, WALL - 0.7, 6.8), M("plastic", (0.7, 0.7, 0.72), rough=0.35), rot=(0.25, 0, 0), bev=0.04, parent=cam)
ball(0.03, (14.55, WALL - 1.0, 6.9), SENSOR, seg=6, rings=4, parent=cam)
cam.rotation_euler = (0, 0, -0.5)
swing(cam, "Z", amp=0.5)

finish("backdrop_toilet1", windows=WINDOWS, theme=THEME)
