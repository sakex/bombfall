# Backdrop for the Hotel Electra bedroom (room1): a lived-in luxury suite.
# A king bed with a quilted plum cover, stacked pillows and a striped throw
# against a wide teal channel-tufted headboard glowing pink from behind;
# walnut nightstands with ceramic lamps and an alarm clock; a marble-topped
# minibar console with a lit fridge under the big window, framed by satin
# drapes on a brass rod; a synthwave sunset print with a picture light; a
# monstera in a planter; a walnut wardrobe with a mirror door and a suitcase
# on top; crown moulding, skirting and a picture rail; up top the high
# windows with drapes and pelmets, the hotel's ELECTRA neon and a split AC.
# Moving: every drape drifts, the AC louvre sweeps, the plant nods, the
# neon's R and bolt stutter, the clock's colon blinks.
#   blender -b --python blender/backdrop_room1.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_electra import *  # noqa: F401,F403

clean_scene()
WINDOWS = [(0.9, 2.1, 3.4, 2.6), (1.1, 7.4, 3.0, 1.5), (8.9, 7.4, 3.0, 1.5)]
THEME = dict(wall=(0.12, 0.05, 0.23), trim=(0.7, 0.3, 1.0), floor=(0.09, 0.04, 0.16))

# ------------------------------------------------------------ materials --
WALNUT = M("wood", (0.24, 0.1, 0.045), color2=(0.16, 0.065, 0.03), rough=0.32)
WALNUT_DK = M("wood", (0.08, 0.035, 0.022), color2=(0.05, 0.022, 0.014), rough=0.4)
BRASS = M("gold", (0.85, 0.58, 0.25), rough=0.25)
SATIN = M("fabric", (0.42, 0.035, 0.17), color2=(0.3, 0.02, 0.12), rough=0.55)
LINEN = M("fabric", (0.82, 0.78, 0.74), color2=(0.7, 0.66, 0.63))
QUILT_TOP = pattern("fabric", (0.27, 0.07, 0.45), "quilt", size=(0.34, 0.34), plane="XY", depth=1.0)
QUILT_FRONT = pattern("fabric", (0.27, 0.07, 0.45), "quilt", size=(0.34, 0.34), plane="XZ", depth=1.0)
HEADBOARD = pattern("fabric", (0.5, 0.17, 0.27), "channels", size=(0.36, 1.0), plane="XZ", rough=0.6, depth=1.0)
TEAL = M("fabric", (0.55, 0.36, 0.08), rough=0.6)
ROSE = M("fabric", (0.6, 0.05, 0.35), rough=0.7)
THROW = pattern("fabric", (0.05, 0.26, 0.3), "stripes", size=(0.3, 1.0), plane="XZ", line_col=(0.6, 0.4, 0.12), duty=0.15)
THROW_TOP = pattern("fabric", (0.05, 0.26, 0.3), "stripes", size=(0.3, 1.0), plane="XY", line_col=(0.6, 0.4, 0.12), duty=0.15)
MARBLE = M("marble", (0.75, 0.72, 0.78), color2=(0.3, 0.27, 0.34))
LAMP_BASE = M("ceramic", (0.05, 0.35, 0.38))
BLACK = M("plastic", (0.015, 0.014, 0.018), rough=0.3)
IVORY = M("plastic", (0.62, 0.6, 0.56), rough=0.45)
GREEN = M("plastic", (0.06, 0.3, 0.09), rough=0.5)
STEM = M("plastic", (0.05, 0.12, 0.04), rough=0.6)
POT = M("ceramic", (0.05, 0.04, 0.06), rough=0.2)
SUITCASE = M("plastic", (0.6, 0.3, 0.05), rough=0.3)
RUG = M("carpet", (0.25, 0.05, 0.16), color2=(0.18, 0.03, 0.12))
RUG_EDGE = M("carpet", (0.5, 0.34, 0.12))
AC_BODY = M("plastic", (0.55, 0.55, 0.58), rough=0.4, grime=0.8)
AC_DARK = M("plastic", (0.03, 0.03, 0.035), rough=0.6)

SHADE = glow((1.0, 0.6, 0.3), 1.8, base=(0.85, 0.62, 0.45))
WARM = glow((1.0, 0.7, 0.4), 3.0)
HALO = glow((1.0, 0.25, 0.65), 2.6)
UNDERGLOW = glow((0.6, 0.25, 1.0), 3.0)
FRIDGE = glow((1.0, 0.86, 0.72), 1.3, base=(0.6, 0.55, 0.5))
CLOCK_RED = glow((1.0, 0.1, 0.12), 3.0)
NEON_PINK_ = glow((1.0, 0.22, 0.62), 4.0)
NEON_ICE_ = glow((0.3, 0.9, 1.0), 4.0)
AC_LED = glow((0.3, 0.6, 1.0), 3.0)
SUN_A = glow((1.0, 0.75, 0.25), 1.2, base=(0.9, 0.6, 0.2))
SUN_B = glow((1.0, 0.3, 0.35), 1.2, base=(0.9, 0.25, 0.3))
SHEEN = glow((0.75, 0.8, 1.0), 0.7, base=(0.5, 0.5, 0.6))
GLASS = glass((0.7, 0.85, 0.95), alpha=0.22)

# ------------------------------------------------------------- the shell --
# Skirting, picture rail and crown moulding along the wall.
moulding(0.0, 15.0, 0.0, SKIRT, WALNUT_DK)
moulding(0.0, 15.0, 6.85, RAIL, BRASS, avoid=WINDOWS)
moulding(0.0, 15.0, 9.2, CROWN, IVORY)
# A little gallery of framed prints above the big window's drapes.
for k, (px, pw, ph, c1, c2) in enumerate(((1.3, 0.8, 1.0, (0.6, 0.12, 0.3), (0.05, 0.2, 0.3)),
                                         (2.6, 1.2, 0.8, (0.05, 0.18, 0.25), (0.8, 0.45, 0.1)),
                                         (3.85, 0.8, 1.0, (0.1, 0.03, 0.2), (0.9, 0.3, 0.45)))):
    pz = 6.05 + (0.05 if k % 2 else 0.0)
    box((pw, 0.05, ph), (px, WALL - 0.025, pz), BRASS if k == 1 else BLACK, bev=0.015)
    box((pw - 0.14, 0.02, ph - 0.14), (px, WALL - 0.055, pz), IVORY)
    box((pw - 0.3, 0.02, ph - 0.3), (px, WALL - 0.065, pz), M("plastic", c1, rough=0.8))
    ball(min(pw, ph) * 0.18, (px + 0.05, WALL - 0.07, pz + 0.05), M("plastic", c2, rough=0.8), scale=(1, 0.1, 1), seg=12, rings=6)

# ------------------------------------------------ big window: drapes, bar --
curtain_rod(0.08, 5.3, 5.3, 1.8, BRASS)
curtain(0.1, 0.88, 0.04, 5.2, 1.8, SATIN, folds=4, amp=0.1, name="drape_l", seed=2)
curtain(4.34, 5.22, 0.04, 5.2, 1.8, SATIN, folds=4, amp=0.1, name="drape_r", seed=5, phase=1.7)

# Minibar console under the sill: fridge with a glass door on the left,
# drawers and a cupboard on the right, marble top, brass legs.
CX0, CX1, CY0, CY1 = 0.95, 4.25, 1.0, 1.9
for x in (CX0 + 0.1, CX1 - 0.1):
    for y in (CY0 + 0.1, CY1 - 0.1):
        rod((x, y, 0.0), (x, y, 0.2), 0.03, BRASS, r2=0.02, verts=6)
box((CX1 - CX0 - 1.2, CY1 - CY0, 1.72), ((CX0 + 1.2 + CX1) / 2, (CY0 + CY1) / 2, 0.2 + 0.86), WALNUT, bev=0.02)
# fridge: hollow cabinet with a lit back and bottles on two shelves
box((1.2, 0.06, 1.72), (CX0 + 0.6, CY1 - 0.03, 1.06), FRIDGE)
box((0.06, CY1 - CY0, 1.72), (CX0 + 0.03, (CY0 + CY1) / 2, 1.06), WALNUT, bev=0.01)
box((1.2, CY1 - CY0, 0.08), (CX0 + 0.6, (CY0 + CY1) / 2, 0.24), WALNUT)
box((1.2, CY1 - CY0, 0.08), (CX0 + 0.6, (CY0 + CY1) / 2, 1.88), WALNUT)
for z in (0.95,):
    box((1.12, 0.7, 0.02), (CX0 + 0.6, 1.45, z), GLASS)
BOTTLE_M = [M("plastic", (0.04, 0.18, 0.06), rough=0.1), M("plastic", (0.35, 0.16, 0.03), rough=0.1),
            M("plastic", (0.5, 0.06, 0.2), rough=0.1), M("plastic", (0.5, 0.5, 0.55), rough=0.1)]
for i, x in enumerate((1.18, 1.42, 1.68, 1.92)):
    bottle(x, 1.5, 0.96, 0.5 + 0.08 * (i % 2), BOTTLE_M[i % 4], cap=BRASS)
    bottle(x + 0.1, 1.45, 0.28, 0.42 + 0.1 * ((i + 1) % 2), BOTTLE_M[(i + 2) % 4], cap=BLACK)
# glass door with a black frame and a brass pull
for (sx, sz, px, pz) in ((1.2, 0.07, CX0 + 0.6, 0.23), (1.2, 0.07, CX0 + 0.6, 1.88), (0.07, 1.72, CX0 + 0.035, 1.06),
                         (0.07, 1.72, CX0 + 1.165, 1.06)):
    box((sx, 0.05, sz), (px, CY0 - 0.02, pz), BLACK)
box((1.1, 0.02, 1.6), (CX0 + 0.6, CY0 - 0.02, 1.06), GLASS)
box((0.04, 0.05, 0.5), (CX0 + 1.08, CY0 - 0.07, 1.2), BRASS, bev=0.01)
# drawers and cupboard fronts
for i in range(2):
    box((0.95, 0.04, 0.8), (2.72, CY0 - 0.02, 0.65 + i * 0.85), WALNUT, bev=0.015)
    box((0.3, 0.05, 0.04), (2.72, CY0 - 0.06, 0.85 + i * 0.85), BRASS, bev=0.01)
box((0.95, 0.04, 1.65), (3.75, CY0 - 0.02, 1.06), WALNUT, bev=0.015)
box((0.8, 0.02, 1.45), (3.75, CY0 - 0.045, 1.06), WALNUT_DK)
ball(0.05, (3.4, CY0 - 0.08, 1.15), BRASS, seg=8, rings=6)
box((CX1 - CX0 + 0.12, CY1 - CY0 + 0.06, 0.07), ((CX0 + CX1) / 2, (CY0 + CY1) / 2 - 0.02, 1.955), MARBLE, bev=0.02)
# tray, two tumblers, a phone
box((0.9, 0.5, 0.03), (3.4, 1.4, 2.005), BRASS, bev=0.01)
for x in (3.2, 3.45):
    cyl(0.07, 0.08, (x, 1.4, 2.06), GLASS, verts=10, bevel=0)
box((0.45, 0.35, 0.07), (1.7, 1.35, 2.025), BLACK, bev=0.02)

# ------------------------------------------------------- bed and headboard --
BX, BW = 8.75, 4.3
# wide channel-tufted headboard with a pink halo behind it
box((6.9, 0.2, 2.7), (BX, 1.83, 2.35), HEADBOARD, bev=0.07, seg=2)
box((7.0, 0.25, 0.1), (BX, 1.82, 3.74), WALNUT, bev=0.02)
box((7.15, 0.01, 2.95), (BX, 1.94, 2.37), HALO)
# floating plinth with a violet under-glow
fbox((BW - 0.3, 1.3, 0.14), (BX, 0.95, 0.0), WALNUT_DK)
box((BW - 0.4, 0.03, 0.04), (BX, 0.29, 0.08), UNDERGLOW)
box((BW + 0.1, 1.55, 0.42), (BX, 0.93, 0.35), WALNUT, bev=0.03)
pill((BW, 1.5, 0.52), (BX, 0.93, 0.82), LINEN, seg=3, round_=0.1)
# quilted cover: top and a front skirt hanging over the foot
duvet = box((BW + 0.15, 1.2, 0.22), (BX, 0.72, 1.2), QUILT_FRONT, bev=0.09, seg=3)
by_normal(duvet, QUILT_TOP, QUILT_FRONT)
box((BW + 0.15, 0.12, 0.8), (BX, 0.14, 0.95), QUILT_FRONT, bev=0.05, seg=2)
box((BW + 0.05, 0.3, 0.12), (BX, 1.38, 1.3), LINEN, bev=0.05, seg=2)   # turned-down sheet
# striped throw across the foot
t = box((BW + 0.25, 0.6, 0.05), (BX, 0.42, 1.34), THROW, bev=0.02)
by_normal(t, THROW_TOP, THROW)
box((BW + 0.25, 0.05, 0.4), (BX, 0.06, 1.16), THROW, bev=0.02)
# pillows: sleeping pillows, teal shams, a lumbar and two rose cushions
for x in (BX - 1.05, BX + 1.05):
    pill((1.9, 0.42, 0.9), (x, 1.52, 1.75), LINEN, rot=(-0.35, 0, 0), seg=3)
    pill((1.7, 0.32, 0.78), (x, 1.28, 1.64), TEAL, rot=(-0.25, 0, 0), seg=3)
pill((1.5, 0.28, 0.42), (BX, 1.02, 1.52), THROW, rot=(-0.15, 0, 0), seg=2)
for s in (-1, 1):
    pill((0.62, 0.26, 0.62), (BX + s * 1.3, 1.02, 1.6), ROSE, rot=(-0.2, s * 0.25, 0), seg=2)
# rug
box((5.8, 1.5, 0.025), (BX, 0.72, 0.0125), RUG_EDGE)
box((5.5, 1.3, 0.03), (BX, 0.72, 0.015), RUG)

# nightstands with lamps; a clock and a book
for i, nx in enumerate((5.9, 11.6)):
    for sx in (-1, 1):
        for y in (0.85, 1.6):
            rod((nx + sx * 0.45, y, 0.0), (nx + sx * 0.45, y, 0.2), 0.025, BRASS, r2=0.015, verts=6)
    box((1.1, 0.95, 1.18), (nx, 1.22, 0.79), WALNUT, bev=0.02)
    box((0.98, 0.04, 0.42), (nx, 0.735, 1.08), WALNUT, bev=0.012)
    box((0.3, 0.05, 0.04), (nx, 0.7, 1.1), BRASS, bev=0.01)
    box((0.95, 0.02, 0.42), (nx, 0.745, 0.55), WALNUT_DK)
    books(nx - 0.4, 0.95, 0.35, 5, 0.38, seed=4 + i, depth=0.4)
    box((1.18, 1.0, 0.05), (nx, 1.22, 1.405), MARBLE, bev=0.015)
    table_lamp(nx + (0.1 if i else -0.1), 1.3, 1.43, LAMP_BASE, SHADE, BRASS, h=0.95, shade_r=0.34, bulb=WARM)
# alarm clock with a blinking colon
box((0.36, 0.16, 0.17), (11.88, 0.98, 1.515), BLACK, bev=0.03)
box((0.28, 0.02, 0.09), (11.88, 0.9, 1.515), glow((0.25, 0.02, 0.03), 1.0))
for k, dx in enumerate((-0.11, -0.05, 0.05, 0.11)):
    box((0.035, 0.01, 0.07), (11.88 + dx, 0.885, 1.515), CLOCK_RED)
colon = pivot("clock_colon", (11.88, 0.885, 1.515))
for dz in (-0.018, 0.018):
    box((0.012, 0.01, 0.012), (11.88, 0.885, 1.515 + dz), CLOCK_RED, parent=colon)
blink(colon, [(15, 30), (45, 60), (75, 90), (105, 120)])
box((0.5, 0.36, 0.06), (6.1, 0.98, 1.46), M("plastic", (0.35, 0.05, 0.08), rough=0.6), bev=0.01)   # book
cyl(0.07, 0.22, (5.55, 0.95, 1.54), GLASS, verts=10, bevel=0)                                   # water glass

# The sunset print above the bed, with a brass picture light.
AX, AZ, AW, AH = BX, 5.35, 3.6, 2.1
box((AW, 0.08, AH), (AX, WALL - 0.04, AZ), BLACK, bev=0.02)
box((AW - 0.2, 0.09, AH - 0.2), (AX, WALL - 0.045, AZ), BRASS, bev=0.01)
cw, ch = AW - 0.34, AH - 0.34
band_cols = [(0.05, 0.02, 0.12), (0.12, 0.03, 0.22), (0.35, 0.05, 0.35), (0.7, 0.15, 0.35)]
for k, c in enumerate(band_cols):
    bh = ch * 0.62 / len(band_cols)
    box((cw, 0.02, bh), (AX, WALL - 0.095, AZ + ch / 2 - bh * (k + 0.5)), M("plastic", c, rough=0.8))
box((cw, 0.02, ch * 0.38), (AX, WALL - 0.095, AZ - ch / 2 + ch * 0.19), M("plastic", (0.03, 0.01, 0.06), rough=0.8))
cyl(0.55, 0.02, (AX, WALL - 0.105, AZ - ch / 2 + ch * 0.38 + 0.25), SUN_A, rot=(math.pi / 2, 0, 0), verts=24, bevel=0)
for k in range(3):
    box((1.2, 0.02, 0.045 + 0.02 * k), (AX, WALL - 0.115, AZ - ch / 2 + ch * 0.38 + 0.02 + k * 0.14), M("plastic", (0.35, 0.05, 0.35), rough=0.8))
extrude_xz([(AX - cw / 2, AZ - ch / 2 + ch * 0.38), (AX - 0.9, AZ + 0.1), (AX - 0.45, AZ - 0.2), (AX + 0.1, AZ - ch / 2 + ch * 0.38)],
           WALL - 0.13, WALL - 0.12, M("plastic", (0.08, 0.02, 0.12), rough=0.8))
extrude_xz([(AX + 0.2, AZ - ch / 2 + ch * 0.38), (AX + 0.95, AZ + 0.02), (AX + cw / 2, AZ - 0.25), (AX + cw / 2, AZ - ch / 2 + ch * 0.38)],
           WALL - 0.13, WALL - 0.12, M("plastic", (0.06, 0.015, 0.1), rough=0.8))
for k in range(5):
    zz = AZ - ch / 2 + ch * 0.38 * (1 - (k / 5) ** 1.6)
    box((cw, 0.02, 0.02), (AX, WALL - 0.12, zz - 0.02), SUN_B)
for k in range(-3, 4):
    rod((AX + k * 0.5, WALL - 0.12, AZ - ch / 2), (AX + k * 0.15, WALL - 0.12, AZ - ch / 2 + ch * 0.38), 0.01, SUN_B, verts=4)
rod((AX, WALL - 0.02, AZ + AH / 2 + 0.05), (AX, WALL - 0.25, AZ + AH / 2 + 0.2), 0.02, BRASS, verts=6)
box((1.6, 0.14, 0.08), (AX, WALL - 0.3, AZ + AH / 2 + 0.2), BRASS, bev=0.02)
box((1.5, 0.05, 0.02), (AX, WALL - 0.3, AZ + AH / 2 + 0.155), WARM)

# ----------------------------------------------------------------- right --
monstera(12.66, 0.62, POT, GREEN, STEM, h=3.7, seed=7, n=12, name="palm", reach=(0.3, 0.8), bias=0.35)
# wardrobe: plinth, carcass, cornice, two doors (one mirrored), brass bars
WX, WW, WY0 = 13.98, 1.85, 0.95
fbox((WW - 0.1, 0.9, 0.18), (WX, 1.44, 0.0), WALNUT_DK)
fbox((WW, WALL - WY0, 4.82), (WX, (WY0 + WALL) / 2, 0.18), WALNUT, bev=0.02)
box((WW + 0.16, WALL - WY0 + 0.08, 0.14), (WX, (WY0 + WALL) / 2 - 0.04, 5.07), WALNUT, bev=0.02)
box((WW + 0.26, WALL - WY0 + 0.13, 0.12), (WX, (WY0 + WALL) / 2 - 0.065, 5.2), WALNUT_DK, bev=0.02)
for s in (-1, 1):
    dx = WX + s * WW / 4
    box((WW / 2 - 0.05, 0.04, 4.6), (dx, WY0 - 0.02, 2.6), WALNUT, bev=0.015)
    box((0.62, 0.035, 1.3), (dx, WY0 - 0.05, 1.05), WALNUT, bev=0.03)
    if s < 0:
        mirror_panel(dx, 3.35, 0.66, 2.55, WALNUT, y=WY0 - 0.035, sheen=SHEEN, depth=0.03)
    else:
        box((0.62, 0.035, 2.5), (dx, WY0 - 0.05, 3.35), WALNUT, bev=0.03)
    box((0.04, 0.06, 0.8), (WX + s * 0.1, WY0 - 0.08, 2.35), BRASS, bev=0.01)
# suitcase on top of the wardrobe
box((1.4, 0.75, 0.46), (WX - 0.05, 1.45, 5.26 + 0.23), SUITCASE, bev=0.1, seg=2)
for k in (-0.3, 0.0, 0.3):
    box((0.07, 0.05, 0.44), (WX - 0.05 + k, 1.07, 5.49), SUITCASE, bev=0.02)
box((0.4, 0.06, 0.06), (WX - 0.05, 1.05, 5.62), BLACK, bev=0.02)

# ------------------------------------------------------------ upper wall --
for (rx, rz, rw, rh) in WINDOWS[1:]:
    curtain(rx - 0.62, rx - 0.04, rz - 0.35, 9.0, 1.82, SATIN, folds=3, amp=0.08, name="drape_%d_l" % int(rx),
            seed=int(rx), sway=0.03)
    curtain(rx + rw + 0.04, rx + rw + 0.62, rz - 0.35, 9.0, 1.82, SATIN, folds=3, amp=0.08,
            name="drape_%d_r" % int(rx), seed=int(rx) + 3, phase=2.0, sway=0.03)
    box((rw + 1.45, 0.24, 0.3), (rx + rw / 2, WALL - 0.12, 9.12), SATIN, bev=0.04)
    box((rw + 1.45, 0.02, 0.03), (rx + rw / 2, WALL - 0.25, 9.0), BRASS)
# ELECTRA in pink tubes with a cyan bolt; the R and the bolt stutter.
w = neon_text("ELECTRA", 5.05, 7.65, 0.55, NEON_PINK_, flicker_idx=(5,), seed=11)
bolt = pivot("neon_bolt", (6.5, WALL - 0.06, 8.6))
pts = [(5.2, 8.55), (5.9, 8.75), (6.35, 8.45), (6.95, 8.8), (7.4, 8.5), (7.95, 8.65)]
tube_path([(x, WALL - 0.06, z) for x, z in pts], 0.03, NEON_ICE_, verts=6, parent=bolt, cap=False)
flicker(bolt, seed=23, bursts=2)
tube_path([(5.05, WALL - 0.06, 7.5), (5.05 + w, WALL - 0.06, 7.5)], 0.02, NEON_ICE_, verts=6, cap=False)
for x in (5.1, 5.05 + w - 0.05):
    box((0.06, 0.06, 0.06), (x, WALL - 0.03, 7.5), BLACK)
# split air conditioner, top right
ac_split(13.9, 8.0, AC_BODY, AC_DARK, led=AC_LED)

finish("backdrop_room1", windows=WINDOWS, theme=THEME)
