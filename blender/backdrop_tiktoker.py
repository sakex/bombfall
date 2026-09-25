# Backdrop for the streamer studio (tiktoker), Neon Palace: a pastel loft
# on a pale oak floor.  Left: the streaming battlestation - a white desk
# with three screens on a chrome arm, an RGB PC whose fans spin, a boom
# mic, a lava lamp with rising blobs, a racing chair (back to us) that
# swivels, honeycomb LED panels, shelves of collectibles and award plaques
# under an "@NEO" neon.  Centre: a velvet bed under the window with a
# glowing headboard halo, fairy lights, plush and a cat whose tail flicks,
# a big ring light, a camera on a tripod panning.  Right: a clothes rail,
# a Hollywood vanity, a monstera, and the blinking "LIVE" sign with hearts
# floating up.  Above: neon clouds, a moon and twinkling stars.
#   blender -b --python blender/backdrop_tiktoker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
WINDOWS = [(5.0, 4.0, 4.0, 2.2), (9.6, 4.6, 2.2, 1.6)]
PASTEL = pbr("paint", (0.42, 0.22, 0.40), rough=0.7, wear=0.1, name="pastel_wall")
TWINKLE = anim_neon((1.0, 0.85, 0.9), "marquee", 2.5)
FAIRY = anim_neon((1.0, 0.75, 0.45), "marquee", 2.5)

# ------------------------------------------------------------ architecture --
slab_at(0.0, 15.0, 0.0, WALL, 0.0, 0.02, M.oak)
wall_cover(WINDOWS, 0.0, 9.3, PASTEL)
tube([(0.05, WALL - 0.04, 0.1), (14.95, WALL - 0.04, 0.1)], 0.018, M.n_pink, verts=4)
box((15.0, 0.04, 0.12), (7.5, WALL - 0.03, 0.06), M.lacquer_white)
# shaggy round rug and a pink runner
lathe([(0.0, 0.03), (1.1, 0.02), (1.15, 0.0)], (2.3, 0.75, 0.0), M.plush_white, segs=18, cap=False, scale=(1.0, 0.55, 1.0))
slab_at(5.3, 8.8, 0.05, 0.3, 0.0, 0.025, M.carpet_plum)

# ------------------------------------------------------- battle station --
slab_at(0.5, 4.2, 0.95, 1.75, 0.72, 0.77, M.lacquer_white)
for lx in (0.55, 4.15):
    slab_at(lx - 0.03, lx + 0.03, 1.0, 1.7, 0.0, 0.72, M.lacquer_white)
box((3.6, 0.02, 0.02), (2.35, 0.94, 0.7), anim_neon("pink", "marquee", 3.0))
tube([(2.35, 1.72, 0.77), (2.35, 1.72, 1.3)], 0.025, M.chrome, verts=6)
tube([(1.3, 1.62, 1.12), (3.4, 1.62, 1.12)], 0.02, M.chrome, verts=6)
for (mx, mz, mw, mh, rz, col) in ((2.35, 1.22, 0.92, 0.52, 0.0, (0.35, 0.1, 0.8)), (1.35, 1.12, 0.6, 0.36, -0.35, (0.9, 0.2, 0.5)),
                                  (3.35, 1.12, 0.6, 0.36, 0.35, (0.1, 0.7, 0.9))):
    my = 1.5
    box((mw, 0.04, mh), (mx, my, mz), M.plastic_black, rot=(0, 0, rz))
    box((mw - 0.04, 0.01, mh - 0.04), (mx - math.sin(-rz) * 0.0, my - 0.025, mz), anim_neon(col, "screen", 1.5), rot=(0, 0, rz))
# game on the main screen: a mountain range and a sun
prism([(1.95, 1.0), (2.15, 1.18), (2.3, 1.08), (2.5, 1.3), (2.75, 1.0)], 1.465, 1.47, M.n_violet, plane="xz")
prism(circle_pts(2.45, 1.26, 0.09, 10, 0, math.pi), 1.466, 1.468, M.n_orange, plane="xz")
for k in range(4):                                                               # chat lines
    box((0.3 - k * 0.05, 0.005, 0.025), (1.33 - k * 0.02, 1.47, 1.0 + k * 0.06), [M.n_white, M.n_pink][k % 2], rot=(0, 0, -0.35))
slab_at(1.7, 2.9, 1.05, 1.3, 0.77, 0.79, M.plastic_black)                          # keyboard
flat_dots([(1.75 + i * 0.075, 1.12 + j * 0.06) for i in range(16) for j in range(3)], 0.795, 0.05, anim_neon("cyan", "marquee", 2.0))
lathe([(0.035, 0), (0.035, 0.02), (0.0, 0.025)], (3.1, 1.2, 0.77), M.plastic_black, segs=8, scale=(0.8, 1.2, 1))
# PC with a glass front and spinning RGB fans
slab_at(3.62, 4.05, 1.1, 1.65, 0.77, 1.42, M.black_metal)
box((0.36, 0.01, 0.6), (3.835, 1.095, 1.095), M.glass_dark)
for k, fz in enumerate((0.93, 1.1, 1.27)):
    torus(0.07, 0.012, (3.835, 1.105, fz), [M.n_pink, M.n_cyan, M.n_violet][k], rot=(math.pi / 2, 0, 0), major_segments=12, minor_segments=3)
    fp = pivot("fan_%d" % k, (3.835, 1.11, fz))
    for b in range(5):
        a = TAU * b / 5
        prism([(3.835, fz), (3.835 + math.cos(a) * 0.065, fz + math.sin(a) * 0.065), (3.835 + math.cos(a + 0.8) * 0.06, fz + math.sin(a + 0.8) * 0.06)],
              1.105, 1.112, M.plastic_white, plane="xz", parent=fp)
    merge_children(fp, fp.name + "_mesh")
    spin(fp, "idle", "Y", seconds=4, turns=-8)
# boom mic
tube([(0.75, 1.65, 0.77), (0.75, 1.62, 1.35), (1.25, 1.3, 1.5), (1.55, 1.15, 1.32)], 0.012, M.black_metal, verts=4)
lathe([(0.03, 0), (0.035, 0.05), (0.035, 0.14), (0.0, 0.16)], (1.55, 1.12, 1.2), M.plastic_black, segs=8)
torus(0.07, 0.006, (1.6, 1.0, 1.28), M.black_metal, rot=(math.pi / 2, 0, 0.3), major_segments=12, minor_segments=3)
# lava lamp with blobs drifting up and down
LX = 0.8
lathe([(0.06, 0), (0.04, 0.08), (0.05, 0.1)], (LX, 1.2, 0.77), M.chrome, segs=8, cap=False)
lathe([(0.05, 0), (0.07, 0.1), (0.045, 0.3), (0.0, 0.3)], (LX, 1.2, 0.87), anim_neon((0.9, 0.25, 0.6), "screen", 0.7), segs=8)
lathe([(0.045, 0), (0.035, 0.05), (0.0, 0.06)], (LX, 1.2, 1.17), M.chrome, segs=8)
for i in range(3):
    bp = pivot("lava_%d" % i, (LX, 1.18, 0.95))
    ico(0.024 + 0.01 * (i % 2), (LX + (i - 1) * 0.012, 1.14, 0.95), neon_mat((1.0, 0.55, 0.1), 2.2, "lava"), subdiv=1, parent=bp)
    key(bp, "idle", "location", [(0, (LX, 1.18, 0.9 + i * 0.07)), (40 + i * 10, (LX, 1.18, 1.1 - i * 0.03)), (LOOP, (LX, 1.18, 0.9 + i * 0.07))], interp="BEZIER")
    key(bp, "idle", "scale", [(0, (1, 1, 1)), (30, (0.8, 0.8, 1.4)), (80, (1.2, 1.2, 0.8)), (LOOP, (1, 1, 1))], interp="BEZIER")
# racing chair, back to the camera; it swivels a little
cp = pivot("chair_swivel", (2.35, 0.55, 0.0))
for k in range(5):
    a = TAU * k / 5 + 0.3
    tube([(2.35, 0.55, 0.1), (2.35 + math.cos(a) * 0.3, 0.55 + math.sin(a) * 0.3, 0.07)], 0.02, M.black_metal, verts=4, parent=cp)
    ico(0.03, (2.35 + math.cos(a) * 0.3, 0.55 + math.sin(a) * 0.3, 0.03), M.rubber, subdiv=1, parent=cp)
tube([(2.35, 0.55, 0.1), (2.35, 0.55, 0.45)], 0.03, M.chrome, verts=6, parent=cp)
slab_at(2.1, 2.6, 0.35, 0.8, 0.45, 0.55, M.plastic_black, parent=cp)
pillow(2.08, 2.62, 0.3, 0.82, 0.62, 0.07, M.leather_white, nx=2, nz=2, facing="up", parent=cp)
pillow(2.1, 2.6, 0.62, 1.45, 0.24, 0.08, M.leather_white, nx=2, nz=3, parent=cp, back=True)
for sx in (-1, 1):
    tube([(2.35 + sx * 0.25, 0.28, 0.62), (2.35 + sx * 0.26, 0.26, 1.25), (2.35 + sx * 0.2, 0.26, 1.4)], 0.055, M.plastic_pink, verts=6, parent=cp)
    tube([(2.35 + sx * 0.29, 0.4, 0.55), (2.35 + sx * 0.29, 0.4, 0.75), (2.35 + sx * 0.29, 0.65, 0.75)], 0.02, M.black_metal, verts=4, parent=cp)
slab_at(2.12, 2.58, 0.22, 0.28, 0.66, 1.43, M.plastic_pink, parent=cp)
pillow(2.22, 2.48, 1.46, 1.66, 0.22, 0.05, M.leather_white, nx=2, nz=2, parent=cp)
heart_pts = [(2.35 + 0.06 * 16 * math.sin(t) ** 3 / 16, 1.05 + 0.06 * (13 * math.cos(t) - 5 * math.cos(2 * t) - 2 * math.cos(3 * t) - math.cos(4 * t)) / 16)
             for t in [TAU * i / 16 for i in range(16)]]
tube([(px, 0.21, pz) for px, pz in heart_pts + heart_pts[:1]], 0.012, M.n_pink, verts=4, parent=cp)
merge_children(cp, "chair_mesh")
key(cp, "idle", "rotation_euler", [(0, (0, 0, -0.18)), (60, (0, 0, 0.18)), (LOOP, (0, 0, -0.18))], interp="BEZIER")
# honeycomb LED panels
HX, HZ, HR = 2.3, 2.6, 0.27
cells = [(0, 0), (1, 0), (-1, 0), (0.5, 1), (-0.5, 1), (1.5, 1), (0.5, -1), (2, 0), (-1.5, -1)]
cols = ["pink", "violet", "cyan", "magenta", "pink", "violet", "cyan", "magenta", "pink"]
for (cx, cz), c in zip(cells, cols):
    px, pz = HX + cx * HR * 1.75, HZ + cz * HR * 1.52
    hexa = [(px + math.cos(math.pi / 6 + TAU * i / 6) * HR * 0.95, pz + math.sin(math.pi / 6 + TAU * i / 6) * HR * 0.95) for i in range(6)]
    prism(hexa, WALL - 0.06, WALL - 0.02, anim_neon(c, "marquee", 1.8), plane="xz")
    tube([(a, WALL - 0.065, b) for a, b in hexa + hexa[:1]], 0.012, M.lacquer_white, verts=3)
# floating shelves with collectibles and award plaques
for sz in (3.5, 4.1):
    slab_at(0.4, 1.35, 1.65, WALL, sz, sz + 0.035, M.lacquer_white)
for i, sz in enumerate((3.535, 4.135)):
    for j in range(3):
        fx = 0.55 + j * 0.3
        [lambda: plush(fx, 1.8, sz, 0.45, [M.plush_pink, M.plush_blue, M.plush_yellow][j], j),
         lambda: lathe([(0.05, 0), (0.05, 0.12), (0.0, 0.14)], (fx, 1.8, sz), [M.n_cyan, M.plastic_pink, M.gold][j], segs=6)][(i + j) % 2]()
for i, (px, m) in enumerate(((3.3, M.chrome), (3.95, M.gold), (4.6, crystal_mat()))):
    slab_at(px - 0.25, px + 0.25, WALL - 0.04, WALL, 3.55, 4.25, M.plastic_black)
    moulding_frame(px - 0.25, px + 0.25, 3.55, 4.25, WALL - 0.045, M.gold, t=0.025)
    lathe([(0.15, 0), (0.15, 0.015), (0.05, 0.02), (0.0, 0.02)], (px, WALL - 0.045, 3.95), [M.steel, M.gold, M.lacquer_white][i], segs=14, rot=(math.pi / 2, 0, 0))
    prism([(px - 0.04, 3.9), (px + 0.06, 3.95), (px - 0.04, 4.0)], WALL - 0.07, WALL - 0.065, M.lacquer_white, plane="xz")
neon_text("@NEO", 0.7, 4.55, WALL - 0.05, 0.62, M.n_pink, r=0.03, verts=4)
tube([(px, WALL - 0.05, pz) for px, pz in [(3.6 + (x0 - 2.35) * 3.5, 4.85 + (z0 - 1.05) * 3.5) for x0, z0 in heart_pts + heart_pts[:1]]], 0.03, M.n_red, verts=4)

# ------------------------------------------------------------------- bed --
BX0, BX1 = 5.55, 8.45
slab_at(BX0 - 0.05, BX1 + 0.05, 0.2, 1.88, 0.0, 0.28, M.lacquer_white)
box((BX1 - BX0, 0.02, 0.02), ((BX0 + BX1) / 2, 0.19, 0.05), anim_neon("violet", "marquee", 2.5))
slab_at(BX0, BX1, 0.25, 1.85, 0.28, 0.5, M.linen)
pillow(BX0 - 0.06, BX1 + 0.06, 0.18, 1.45, 0.62, 0.14, M.velvet_rose, nx=6, nz=4, facing="up", sag=0.02)
box((BX1 - BX0 + 0.14, 0.02, 0.3), ((BX0 + BX1) / 2, 0.18, 0.42), M.velvet_rose)
pillow(BX0 - 0.06, BX1 + 0.06, 0.3, 0.8, 0.66, 0.06, M.plush_lilac, nx=6, nz=2, facing="up")                # throw
pillow(BX0 + 0.1, BX1 - 0.1, 0.5, 1.5, 1.86, 0.1, M.velvet_rose, tuft=0.04, tuft_nx=6, tuft_nz=3)           # headboard
tube([(BX0 - 0.05, 1.92, 0.5), (BX0 - 0.05, 1.92, 1.55), (BX1 + 0.05, 1.92, 1.55), (BX1 + 0.05, 1.92, 0.5)], 0.025, M.n_pink, verts=4)
for i, (px, m) in enumerate(((5.95, M.linen), (6.7, M.linen), (7.4, M.linen), (8.1, M.linen))):
    pillow(px - 0.33, px + 0.33, 0.6, 1.02, 1.55, 0.1, m, nx=2, nz=2)
for i, (px, m) in enumerate(((6.3, M.velvet_teal), (7.75, M.velvet_gold))):
    pillow(px - 0.2, px + 0.2, 0.62, 0.95, 1.35, 0.08, m, nx=2, nz=2)
plush(6.95, 1.2, 0.6, 1.3, M.plush_brown, 0)
plush(8.0, 1.05, 0.62, 1.0, M.plush_white, 1)
# the cat, curled, tail flicking
CX, CY = 5.95, 0.8
sphere(0.16, (CX, CY, 0.72), M.plastic_grey, scale=(1.4, 0.9, 0.6), segments=8, rings=5)
sphere(0.09, (CX + 0.18, CY - 0.05, 0.78), M.plastic_grey, segments=8, rings=5)
for sx in (-1, 1):
    prism([(CX + 0.18 + sx * 0.03, 0.83), (CX + 0.18 + sx * 0.08, 0.83), (CX + 0.18 + sx * 0.06, 0.92)], CY - 0.07, CY - 0.03, M.plastic_grey, plane="xz")
quad_dots([(CX + 0.15, 0.79), (CX + 0.22, 0.79)], CY - 0.14, 0.022, M.n_green)
tp = pivot("cat_tail", (CX - 0.2, CY, 0.72))
tube([(CX - 0.2, CY, 0.72), (CX - 0.33, CY - 0.05, 0.74), (CX - 0.4, CY - 0.1, 0.82), (CX - 0.38, CY - 0.12, 0.9)], 0.025, M.plastic_grey, verts=5, parent=tp)
key(tp, "idle", "rotation_euler", [(0, (0, 0, 0)), (20, (0, 0.5, 0.3)), (30, (0, 0, 0)), (70, (0, 0, 0)), (85, (0, 0.4, -0.2)), (100, (0, 0, 0)), (LOOP, (0, 0, 0))],
    interp="BEZIER")
# nightstands: a heart lamp and a moon lamp
for nx_, lamp in ((5.1, "heart"), (8.9, "moon")):
    slab_at(nx_ - 0.22, nx_ + 0.22, 1.3, 1.8, 0.0, 0.55, M.lacquer_white)
    box((0.3, 0.01, 0.02), (nx_, 1.295, 0.4), M.gold)
    if lamp == "heart":
        tube([(nx_ + (x0 - 2.35) * 1.6, 1.55, 0.8 + (z0 - 1.05) * 1.6) for x0, z0 in heart_pts + heart_pts[:1]], 0.02, M.n_pink, verts=4)
        tube([(nx_, 1.55, 0.55), (nx_, 1.55, 0.68)], 0.01, M.chrome, verts=4)
    else:
        sphere(0.13, (nx_, 1.55, 0.7), anim_neon((1.0, 0.9, 0.7), "screen", 1.4), segments=10, rings=6)
# fairy lights drooping below the window
pts = []
for i in range(40):
    t = i / 39
    pts.append((5.1 + 3.8 * t, 3.85 - 0.25 * abs(math.sin(t * math.pi * 3))))
tube([(px, 1.9, pz) for px, pz in pts], 0.004, M.black_metal, verts=3, caps=False)
quad_dots(pts, 1.88, 0.05, FAIRY, diamond=True)
# ring light on a stand, facing us
RX, RZ = 4.75, 1.85
for a in (0.4, 2.5, 4.6):
    tube([(RX, 0.7, 0.4), (RX + math.cos(a) * 0.3, 0.7 + math.sin(a) * 0.3, 0.0)], 0.012, M.black_metal, verts=4)
tube([(RX, 0.7, 0.35), (RX, 0.7, RZ - 0.5)], 0.016, M.black_metal, verts=5)
torus(0.5, 0.05, (RX, 0.7, RZ), M.n_white, rot=(math.pi / 2, 0, 0), major_segments=28, minor_segments=5)
torus(0.52, 0.02, (RX, 0.72, RZ), M.plastic_white, rot=(math.pi / 2, 0, 0), major_segments=28, minor_segments=3)
slab_at(RX - 0.04, RX + 0.04, 0.66, 0.7, RZ - 0.1, RZ + 0.08, M.plastic_black)
box((0.06, 0.005, 0.13), (RX, 0.655, RZ - 0.01), anim_neon("pink", "screen", 1.2))
# camera on a tripod, panning
TX, TY = 9.35, 0.35
for a in (0.6, 2.7, 4.8):
    tube([(TX, TY, 1.15), (TX + math.cos(a) * 0.35, TY + math.sin(a) * 0.35, 0.0)], 0.014, M.black_metal, verts=4)
tube([(TX, TY, 1.15), (TX, TY, 1.3)], 0.02, M.black_metal, verts=5)
cam = pivot("camera_pan", (TX, TY, 1.32))
slab_at(TX - 0.08, TX + 0.08, TY - 0.06, TY + 0.06, 1.3, 1.42, M.plastic_black, parent=cam)
lathe([(0.045, 0), (0.045, 0.14), (0.05, 0.15), (0.0, 0.15)], (TX - 0.08, TY, 1.37), M.plastic_black, segs=10, rot=(0, -math.pi / 2, 0), parent=cam)
lathe([(0.0, 0), (0.035, 0.0)], (TX - 0.235, TY, 1.37), M.glass_dark, segs=10, rot=(0, -math.pi / 2, 0), parent=cam, cap=False)
box((0.02, 0.02, 0.02), (TX + 0.05, TY - 0.07, 1.4), M.n_red, parent=cam)
merge_children(cam, "camera_mesh")
key(cam, "idle", "rotation_euler", [(0, (0, 0, -0.25)), (60, (0, 0, 0.2)), (LOOP, (0, 0, -0.25))], interp="BEZIER")

# ------------------------------------------------------------- dressing --
tube([(9.95, 1.3, 0.0), (9.95, 1.3, 1.75), (11.55, 1.3, 1.75), (11.55, 1.3, 0.0)], 0.018, M.chrome, verts=6)
for fx in (9.95, 11.55):
    tube([(fx, 1.05, 0.02), (fx, 1.55, 0.02)], 0.018, M.chrome, verts=6)
GARMENTS = [M.velvet_rose, M.plush_white, M.velvet_navy, M.plush_lilac, M.leather_black, M.velvet_gold, M.plush_pink]
for i in range(7):
    gx = 10.2 + i * 0.2
    tube([(gx, 1.3, 1.76), (gx, 1.3, 1.68), (gx - 0.14, 1.3, 1.6), (gx + 0.14, 1.3, 1.6), (gx, 1.3, 1.68)], 0.006, M.chrome, verts=3)
    long_ = i % 3 == 0
    prism([(gx - 0.15, 1.6), (gx + 0.15, 1.6), (gx + (0.24 if long_ else 0.17), 0.55 if long_ else 0.95), (gx - (0.24 if long_ else 0.17), 0.55 if long_ else 0.95)],
          1.25 + i * 0.012, 1.33 + i * 0.012, GARMENTS[i], plane="xz")
# Hollywood vanity
VX = 13.05
slab_at(VX - 0.75, VX + 0.75, 1.35, 1.85, 0.72, 0.77, M.lacquer_white)
for sx in (-1, 1):
    slab_at(VX + sx * 0.72 - 0.03, VX + sx * 0.72 + 0.03, 1.38, 1.82, 0.0, 0.72, M.lacquer_white)
slab_at(VX - 0.55, VX + 0.55, WALL - 0.04, WALL, 0.85, 1.85, M.lacquer_white)
box((1.0, 0.01, 0.9), (VX, WALL - 0.045, 1.35), M.mirror)
quad_dots(rect_pts(VX - 0.5, VX + 0.5, 0.9, 1.8, 0.17), WALL - 0.06, 0.07, M.bulb)
for i in range(5):
    lathe([(0.025, 0), (0.025, 0.08 + i % 2 * 0.05), (0.0, 0.09 + i % 2 * 0.05)], (VX - 0.4 + i * 0.12, 1.6, 0.77), [M.gold, M.plastic_pink, M.lacquer_white, M.plastic_black, M.chrome][i], segs=6)
pillow(VX - 0.25, VX + 0.25, 0.6, 1.1, 0.48, 0.12, M.plush_pink, nx=2, nz=2, facing="up")
slab_at(VX - 0.22, VX + 0.22, 0.62, 1.08, 0.0, 0.36, M.plush_pink)
fig_tree(14.45, 1.1, h=1.8, m_pot=M.lacquer_white, seed=9, leaves=20)
# LIVE sign, blinking, with hearts floating up from it
LXc, LZ = 13.3, 4.7
lv = pivot("blink_live", (LXc, WALL - 0.05, LZ))
tube([(p[0], WALL - 0.06, p[1]) for p in rounded_rect(1.9, 0.9, 0.25, 3, LXc, LZ)] + [(LXc, WALL - 0.06, LZ - 0.45)], 0.035, M.n_red, verts=4, parent=lv)
neon_text("LIVE", LXc + 0.18, LZ - 0.25, WALL - 0.06, 0.5, M.n_red, r=0.03, align="center", verts=4, parent=lv)
ico(0.09, (LXc - 0.6, WALL - 0.06, LZ), M.n_red, subdiv=1, parent=lv)
merge_children(lv, "blink_live_mesh")
blink(lv, "1111111111101110")
slab_at(LXc - 1.02, LXc + 1.02, WALL - 0.03, WALL, LZ - 0.52, LZ + 0.52, M.black_metal)
for i in range(5):
    hp = pivot("heart_%d" % i, (LXc + 0.7 + (i % 2) * 0.1, WALL - 0.1, LZ + 0.3))
    s = 0.7 + (i % 3) * 0.25
    prism([(LXc + 0.7 + (x0 - 2.35) * s, LZ + 0.3 + (z0 - 1.05) * s) for x0, z0 in heart_pts], WALL - 0.11, WALL - 0.09,
          [M.n_pink, M.n_red, M.n_magenta][i % 3], plane="xz", parent=hp)
    ph = i / 5.0
    f_top = (1.0 - ph) * LOOP
    x0 = LXc + 0.7 + (i % 2) * 0.1
    ks = [(0, (x0 + math.sin(ph * 6) * 0.1, WALL - 0.1, LZ + 0.3 + 1.4 * ph)), (f_top, (x0 + 0.15, WALL - 0.1, LZ + 1.7)),
          (min(f_top + 1, LOOP), (x0, WALL - 0.1, LZ + 0.3)), (LOOP, (x0 + math.sin(ph * 6) * 0.1, WALL - 0.1, LZ + 0.3 + 1.4 * ph))]
    key(hp, "idle", "location", sorted({f: v for f, v in ks}.items()), interp="LINEAR")
    sc = [(0, (1 - ph * 0.8,) * 3), (f_top, (0.2, 0.2, 0.2)), (min(f_top + 1, LOOP), (1, 1, 1)), (LOOP, (1 - ph * 0.8,) * 3)]
    key(hp, "idle", "scale", sorted({f: v for f, v in sc}.items()), interp="LINEAR")

# foil balloons tied to the nightstand, bobbing
for i, (bx, bz, kind, m) in enumerate(((9.15, 2.3, "heart", M.n_pink), (9.55, 2.6, "star", M.gold), (8.85, 2.75, "heart", M.n_magenta))):
    bp = pivot("balloon_%d" % i, (bx, 1.5, bz))
    if kind == "heart":
        prism([(bx + (x0 - 2.35) * 4.6, bz + (z0 - 1.05) * 4.6) for x0, z0 in heart_pts], 1.48, 1.56, pbr("chrome", (0.95, 0.35, 0.6), rough=0.15, name="foil_pink"),
              plane="xz", parent=bp)
    else:
        prism([(bx + math.cos(math.pi / 2 + TAU * k / 10) * (0.34 if k % 2 == 0 else 0.15), bz + math.sin(math.pi / 2 + TAU * k / 10) * (0.34 if k % 2 == 0 else 0.15))
               for k in range(10)], 1.48, 1.56, M.gold, plane="xz", parent=bp)
    tube([(bx, 1.52, bz - 0.2), (bx - 0.05, 1.52, (bz + 0.55) / 2), (8.9, 1.55, 0.55)], 0.003, M.plastic_white, verts=3, caps=False, parent=bp)
    merge_children(bp, bp.name + "_mesh")
    wobble(bp, "idle", "location", 2, 0.06, seconds=4, phase=i * 2.1)
    wobble(bp, "idle", "rotation_euler", 1, 0.08, seconds=4, phase=i * 1.3)
# a beanbag by the ring light, sneakers under the rail, a controller
pillow(3.95, 4.55, 0.1, 0.7, 0.45, 0.4, M.velvet_teal, nx=3, nz=3, facing="up", soft=0.8)
for i in range(3):
    sx = 10.2 + i * 0.45
    prism([(sx - 0.14, 0.0), (sx + 0.13, 0.0), (sx + 0.14, 0.05), (sx - 0.02, 0.09), (sx - 0.12, 0.13), (sx - 0.15, 0.06)], 1.55, 1.65,
          [M.plastic_white, M.plastic_pink, M.plastic_cyan][i], plane="xz")
slab_at(2.9, 3.1, 1.3, 1.42, 0.77, 0.8, M.plastic_black)
# framed prints on the upper wall
picture(1.0, 5.95, 0.7, 0.95, art="sunset", y=WALL, m_frame=M.lacquer_white, light=False, frame_w=0.05)
picture(12.6, 6.35, 0.8, 0.6, art="waves", y=WALL, m_frame=M.lacquer_white, light=False, frame_w=0.05)

# ------------------------------------------------------------ upper band --
def cloud(x, z, s, m):
    pts = []
    for (cx, cz, r, a0, a1) in ((-0.9, 0.0, 0.35, math.pi * 0.5, math.pi * 1.5), (-0.4, 0.3, 0.42, math.pi * 0.85, math.pi * 0.15),
                                (0.35, 0.25, 0.5, math.pi * 0.9, math.pi * 0.1), (0.95, -0.02, 0.33, math.pi * 0.5, -math.pi * 0.5)):
        n = 6
        for i in range(n + 1):
            a = a0 + (a1 - a0) * i / n if a1 > a0 or a0 - a1 < math.pi else a0 - (a0 - a1) * i / n
            pts.append((x + (cx + math.cos(a) * r) * s, z + (cz + math.sin(a) * r) * s))
    pts.append(pts[0])
    tube([(px, WALL - 0.05, pz) for px, pz in pts], 0.03, m, verts=4)


cloud(2.3, 7.2, 1.1, M.n_white)
cloud(12.6, 7.6, 0.9, M.n_pink)
tube([(7.3 + math.cos(a) * 0.6, WALL - 0.05, 7.6 + math.sin(a) * 0.6) for a in [math.pi * (0.35 + 1.3 * i / 16) for i in range(17)]] +
     [(7.3 + 0.2 + math.cos(a) * 0.45, WALL - 0.05, 7.6 + 0.05 + math.sin(a) * 0.45) for a in [math.pi * (1.55 - 1.1 * i / 12) for i in range(13)]],
     0.03, M.n_amber, verts=4)
star_pts = [(0.3 + i * 0.37 % 14.4, 6.6 + ((i * 7) % 11) * 0.22) for i in range(40)]
star_pts = [p for p in star_pts if not in_window(WINDOWS, p[0] - 0.05, p[0] + 0.05, p[1] - 0.05, p[1] + 0.05)]
quad_dots(star_pts, WALL - 0.04, 0.06, TWINKLE, diamond=True)
ob = pivot("blink_onair", (4.0, WALL - 0.06, 6.0))
slab_at(3.2, 4.8, WALL - 0.06, WALL - 0.02, 5.7, 6.3, M.black_metal)
box((1.45, 0.01, 0.48), (4.0, WALL - 0.065, 6.0), neon_mat((1.0, 0.1, 0.12), 2.2, "onair"), parent=ob)
merge_children(ob, "blink_onair_mesh")
neon_text("ON AIR", 4.0, 5.85, WALL - 0.075, 0.3, M.n_white, r=0.014, align="center", verts=3)
blink(ob, "1111111111111100")

finish("backdrop_tiktoker", 2048, 14000, windows=WINDOWS, wall=(0.17, 0.04, 0.19))
