# The skybridge between the two towers of the Neon Palace: a 53 m
# cable-stayed deck in steel and glass.  The game lays the deck cells
# (x 0..53, y -1..1, z -1..0), the gaps and the hazards; this model is
# everything around them: a steel box girder under each span that ends in
# torn, sparking stubs with dangling cables at the three gaps, glass
# parapets with neon handrails, neon gate arches carrying holo-ads, lamp
# posts, a pylon with stay cables and a spinning holo-logo, a signal
# gantry holding the wall gun, and the far tower: a lit lobby behind a
# revolving door, a "NEON PALACE" blade sign and searchlights sweeping
# from its crown.
# Origin: x = 0 at the first deck cell, z = 0 at the deck top, +Y deeper.
#   blender -b --python blender/skybridge.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
L = 53.0
GAPS = [(8, 3), (19, 3), (31, 4)]                 # SkyBridge.GAPS: first cell, width
SPANS = [(0.0, 8.0), (11.0, 19.0), (22.0, 31.0), (35.0, L)]
STEEL = pbr("paint", (0.05, 0.05, 0.07), rough=0.45, name="bridge_steel")
STEEL_LIGHT = pbr("paint", (0.25, 0.26, 0.3), rough=0.4, name="bridge_steel_light")
HAZARD = [pbr("paint", (0.8, 0.55, 0.02), rough=0.5, name="hazard_yellow"), pbr("paint", (0.02, 0.02, 0.02), rough=0.5, name="hazard_black")]
FACADE = pbr("concrete", (0.08, 0.06, 0.12), grime=0.4, name="tower_stone")
SPARK = neon_mat((1.0, 0.8, 0.4), 6.0, "spark")
WIN_MATS = [neon_mat((1.0, 0.6, 0.8), 1.3, "win_pink"), neon_mat((0.4, 0.85, 1.0), 1.3, "win_cyan"), neon_mat((1.0, 0.8, 0.5), 1.3, "win_warm")]


def in_gap(x0, x1):
    return any(x1 > g and x0 < g + w for g, w in GAPS)


# ------------------------------------------------------------ deck girder --
for (a, b) in SPANS:
    slab_at(a, b, -1.08, 1.08, -1.6, -1.0, STEEL)                                   # box girder
    slab_at(a, b, -1.12, -1.06, -1.55, -1.05, STEEL_LIGHT)                          # fascia plate
    tube([(a + 0.05, -1.14, -1.58), (b - 0.05, -1.14, -1.58)], 0.025, M.n_violet, verts=4)   # underglow
    tube([(a + 0.05, -1.14, -1.02), (b - 0.05, -1.14, -1.02)], 0.012, M.n_cyan, verts=4)
    n = int(b - a)
    for i in range(n + 1):
        box((0.06, 0.05, 0.5), (a + (b - a) * i / max(n, 1), -1.14, -1.3), STEEL)            # stiffeners
    for i in range(n):
        x = a + (b - a) * (i + 0.5) / n
        tube([(x - 0.45, 1.1, -1.6), (x, 1.1, -2.3), (x + 0.45, 1.1, -1.6)], 0.03, STEEL, verts=4)     # back truss
    tube([(a, 1.1, -2.3), (b, 1.1, -2.3)], 0.04, STEEL, verts=5)
# pendant work lights under each span
for (a, b) in SPANS:
    for i in range(int((b - a) / 4.0)):
        hx = a + 2.0 + i * 4.0
        tube([(hx, 0.3, -1.6), (hx, 0.3, -2.6)], 0.008, M.black_metal, verts=3, caps=False)
        lathe([(0.0, 0.05), (0.14, 0.0), (0.12, -0.06)], (hx, 0.3, -2.65), STEEL_LIGHT, segs=8, cap=False)
        lathe([(0.0, 0.0), (0.1, 0.0)], (hx, 0.3, -2.68), M.bulb, segs=8, rot=(math.pi, 0, 0), cap=False)
# torn ends at the gaps: bent beams, dangling cables, sparks, hazard lights
k = 0
for (g, w) in GAPS:
    for side, ex in ((-1, float(g)), (1, float(g + w))):
        # jagged torn plate
        prism([(ex, -1.6), (ex, -1.0), (ex - side * 0.25, -1.0), (ex - side * 0.1, -1.2), (ex - side * 0.3, -1.35), (ex - side * 0.12, -1.6)],
              -1.1, 1.1, STEEL, plane="xz")
        for j, yy in enumerate((-0.8, 0.0, 0.8)):
            tip = (ex + side * (0.35 + 0.15 * j), yy + 0.1 * side, -1.2 - 0.35 * (j % 2))
            tube([(ex - side * 0.2, yy, -1.3), (ex + side * 0.05, yy, -1.3), tip], 0.035, STEEL_LIGHT, verts=4)
        # hazard stripes on the stub face
        for s in range(4):
            box((0.03, 0.1, 0.12), (ex - side * 0.02, -1.13, -1.1 - s * 0.13), HAZARD[s % 2])
        # dangling cable, swinging
        cp = pivot("cable_%d" % k, (ex + side * 0.1, -0.2, -1.3))
        tube([(ex + side * 0.1, -0.2, -1.3), (ex + side * 0.25, -0.25, -2.0), (ex + side * 0.2, -0.2, -2.8)], 0.02, M.rubber, verts=4, parent=cp)
        ico(0.06, (ex + side * 0.2, -0.2, -2.85), SPARK, subdiv=1, parent=cp)
        merge_children(cp, cp.name + "_mesh")
        wobble(cp, "idle", "rotation_euler", 1, 0.25, seconds=4, phase=k * 1.1)
        # sparks flickering at the stub
        sp = pivot("sparks_%d" % k, (ex, -1.15, -1.1))
        for s in range(5):
            a = -math.pi / 2 + (s - 2) * 0.35
            box((0.012, 0.012, 0.18), (ex + side * math.cos(a + math.pi / 2) * 0.1, -1.16, -1.1 + math.sin(a) * 0.1 - 0.08), SPARK,
                rot=(0, a * side, 0), parent=sp)
        merge_children(sp, sp.name + "_mesh")
        blink(sp, ["1010011000100100", "0100100110010010"][k % 2])
        # an amber warning lamp on the parapet posts at the edge
        bp = pivot("warn_%d" % k, (ex - side * 0.1, 1.25, 1.55))
        lathe([(0.0, 0.0), (0.07, 0.0), (0.07, 0.08), (0.0, 0.08)], (ex - side * 0.1, 1.25, 1.5), neon_mat((1.0, 0.55, 0.05), 5.0, "warn"), segs=8, arc=math.pi, parent=bp)
        lathe([(0.07, 0.0), (0.3, -1.2)], (ex - side * 0.1, 1.25, 1.54), beam_mat((1.0, 0.55, 0.05), 0.1, 1.5), segs=8, arc=math.pi * 0.3, rot=(math.pi / 2, 0, 0),
              parent=bp)
        merge_children(bp, bp.name + "_mesh")
        spin(bp, "idle", "Z", seconds=4, turns=4 * side)
        k += 1

# -------------------------------------------------------------- parapets --
for (a, b) in SPANS:
    for y, h, rail in ((-1.2, 0.95, M.n_cyan), (1.22, 1.3, M.n_pink)):
        box((b - a - 0.1, 0.03, h - 0.12), ((a + b) / 2, y, (h - 0.12) / 2 + 0.06), M.glass)
        tube([(a + 0.02, y, h), (b - 0.02, y, h)], 0.045, M.chrome, verts=6)
        tube([(a + 0.02, y - 0.05 * (1 if y < 0 else -1), h - 0.06), (b - 0.02, y - 0.05 * (1 if y < 0 else -1), h - 0.06)], 0.014, rail, verts=4)
        slab_at(a, b, y - 0.05, y + 0.05, 0.0, 0.07, STEEL)
        n = max(int((b - a) / 2.0), 1)
        for i in range(n + 1):
            px = a + 0.05 + (b - a - 0.1) * i / n
            slab_at(px - 0.04, px + 0.04, y - 0.04, y + 0.04, 0.0, h, STEEL_LIGHT)

# ----------------------------------------------------------- gate arches --
ADS = [(1.0, 0.25, 0.7), (0.2, 0.8, 1.0), (0.6, 0.3, 1.0), (1.0, 0.6, 0.2)]
for i, gx in enumerate((2.5, 15.5, 28.0, 41.0)):
    col = [M.n_pink, M.n_cyan][i % 2]
    for y in (-1.45, 1.45):
        slab_at(gx - 0.14, gx + 0.14, y - 0.14, y + 0.14, 0.0, 5.0, STEEL)
        tube([(gx - 0.15, y - 0.15, 0.1), (gx - 0.15, y - 0.15, 4.9)], 0.02, col, verts=4)
        tube([(gx + 0.15, y - 0.15, 0.1), (gx + 0.15, y - 0.15, 4.9)], 0.02, col, verts=4)
    slab_at(gx - 0.2, gx + 0.2, -1.6, 1.6, 5.0, 5.35, STEEL)
    tube([(gx, -1.62, 5.02), (gx, 1.62, 5.02)], 0.03, col, verts=4)
    # a holo-ad board riding on the lintel
    slab_at(gx - 1.3, gx + 1.3, -0.05, 0.05, 5.35, 6.75, STEEL)
    box((2.45, 0.02, 1.25), (gx, -0.07, 6.05), anim_neon(ADS[i], "screen", 1.6))
    quad_dots(rect_pts(gx - 1.28, gx + 1.28, 5.38, 6.72, 0.14), -0.08, 0.05, anim_neon((1.0, 0.85, 0.5), "marquee", 3.0))
    neon_text(["DRINK", "FLY", "DREAM", "PLAY"][i], gx, 5.85, -0.1, 0.4, M.n_white, r=0.018, align="center", verts=3)

# ----------------------------------------------------------- lamp posts --
for i in range(9):
    lx = 1.2 + i * 6.0
    if in_gap(lx - 0.3, lx + 0.3):
        lx += 1.8
    tube([(lx, 1.35, 0.0), (lx, 1.35, 3.6), (lx, 1.15, 3.95), (lx, 0.8, 4.0)], 0.045, STEEL, verts=5)
    lathe([(0.1, 0.0), (0.1, 0.25), (0.06, 0.3)], (lx, 1.35, 0.0), STEEL, segs=6, cap=False)
    lathe([(0.0, 0.05), (0.12, 0.0), (0.1, -0.08), (0.0, -0.1)], (lx, 0.8, 3.98), STEEL_LIGHT, segs=8)
    lathe([(0.0, 0.0), (0.08, -0.04), (0.0, -0.16)], (lx, 0.8, 3.9), M.bulb, segs=8)

# ----------------------------------------------- pylon with stay cables --
PX = 25.0
for dy, lean in ((1.9, 0.0), (3.4, 0.0)):
    prism([(PX - 0.7, -19.0), (PX + 0.7, -19.0), (PX + 0.22, 11.0), (PX - 0.22, 11.0)], dy - 0.3, dy + 0.3, STEEL, plane="xz")
    tube([(PX - 0.7, dy - 0.32, -18.0), (PX - 0.24, dy - 0.32, 10.8)], 0.025, M.n_violet, verts=4)
    tube([(PX + 0.7, dy - 0.32, -18.0), (PX + 0.24, dy - 0.32, 10.8)], 0.025, M.n_violet, verts=4)
for zz in (-12.0, -6.0, 4.5, 8.0, 10.8):
    slab_at(PX - 0.3, PX + 0.3, 1.6, 3.7, zz - 0.2, zz + 0.2, STEEL)
slab_at(PX - 0.5, PX + 0.5, 1.2, 3.8, -2.4, 0.0, STEEL)
for j in range(7):
    zz = 6.5 + j * 0.62
    for side in (-1, 1):
        ex = PX + side * (4.0 + j * 2.6)
        if in_gap(ex - 0.2, ex + 0.2):
            ex += side * 1.6
        tube([(PX + side * 0.2, 1.9, zz), (ex, 1.22, 1.3)], 0.018, M.chrome, verts=3, caps=False)
# holo-logo spinning at the pylon top
lathe([(0.35, 0.0), (0.35, 0.1), (0.0, 0.1)], (PX, 2.65, 11.2), STEEL, segs=12)
hp = pivot("holo_logo", (PX, 2.65, 12.1))
torus(0.7, 0.04, (PX, 2.65, 12.1), M.n_pink, rot=(math.pi / 2, 0, 0), major_segments=24, minor_segments=4, parent=hp)
prism([(PX, 11.65), (PX + 0.4, 12.1), (PX, 12.55), (PX - 0.4, 12.1)], 2.63, 2.67, anim_neon("cyan", "screen", 2.0), plane="xz", parent=hp)
merge_children(hp, "holo_logo_mesh")
spin(hp, "idle", "Z", seconds=4, turns=1)

# ------------------------------------------- gantry holding the wall gun --
GX = 46.7
for y in (-0.2, 1.45):
    slab_at(GX - 0.12, GX + 0.12, y - 0.12, y + 0.12, 0.0, 5.3, STEEL)
slab_at(GX - 0.15, GX + 0.15, -0.3, 1.6, 4.3, 4.55, STEEL)
slab_at(GX - 0.25, GX + 0.05, -0.25, 0.25, 3.6, 4.3, STEEL_LIGHT)
for s in range(5):
    box((0.06, 0.02, 0.25), (GX - 0.12 + s * 0.06, -0.33, 4.42), HAZARD[s % 2])
tube([(GX - 0.13, -0.33, 0.2), (GX - 0.13, -0.33, 5.2)], 0.015, M.n_red, verts=4)

# ------------------------------------------------------------ far tower --
TX = 48.6                                         # the tower's face (x) and its lobby door at x 50.5..52.9
# lobby interior, lit, behind the play plane
slab_at(TX, TX + 9.0, 3.4, 3.5, 0.0, 4.6, M.backlight)
slab_at(TX, TX + 9.0, 1.0, 3.5, -0.02, 0.0, M.marble_white)
for cx in (TX + 1.0, TX + 6.4):
    column(cx, 1.5, 4.4, M.marble_white, M.gold, r=0.18)
slab_at(TX + 4.4, TX + 6.0, 1.3, 1.9, 0.0, 1.1, M.marble_black)                     # reception
box((1.6, 0.02, 0.05), (TX + 5.2, 1.29, 1.0), M.n_pink)
chandelier("lobby_chandelier", TX + 3.3, 1.8, drop=0.9, r=0.55, arms=5, tiers=1, spin_ball=False, strands=10).location.z = 4.6
potted_palm(TX + 1.8, 1.9, h=2.2, fronds=7, seed=5, m_pot=M.gold)
# the facade: stone piers, a glass curtain wall with lit windows
# a stone pilaster in front of the game's end wall cells (x 53..54)
slab_at(TX + 4.3, TX + 5.7, -1.95, -1.1, 0.0, 4.6, FACADE)
box((1.4, 0.03, 0.05), (TX + 5.0, -1.97, 4.3), M.gold)
for (a, b) in ((TX, TX + 1.9), (TX + 5.7, TX + 9.0)):                            # glass storefront
    box((b - a, 0.03, 4.5), ((a + b) / 2, -1.2, 2.25), M.glass)
    n = max(int((b - a) / 1.2), 1)
    for i in range(n + 1):
        slab_at(a + (b - a) * i / n - 0.04, a + (b - a) * i / n + 0.04, -1.26, -1.14, 0.0, 4.6, M.gold)
    slab_at(a, b, -1.26, -1.14, 0.0, 0.15, M.gold)
slab_at(TX, TX + 9.0, -1.9, 3.6, 4.6, 12.6, FACADE)                                # the tower above
slab_at(TX, TX + 9.0, -1.9, 3.6, -19.0, -0.02, FACADE)                               # and below
slab_at(TX + 9.0, TX + 9.4, -1.9, 3.6, 0.0, 12.6, FACADE)
slab_at(TX - 0.3, TX + 9.3, -2.1, -1.8, 4.5, 4.9, STEEL)                            # canopy
box((9.6, 0.02, 0.05), (TX + 4.5, -2.12, 4.52), anim_neon("pink", "marquee", 3.0))
quad_dots([(TX - 0.2 + i * 0.2, 4.7) for i in range(49)], -2.12, 0.05, anim_neon((1.0, 0.8, 0.45), "marquee", 3.0))
for tx_ in (TX + 0.1, TX + 9.1):
    tube([(tx_, -2.0, 4.5), (tx_, -2.0, 0.0)], 0.04, M.gold, verts=6)
# door frame and a revolving door in the opening (x 50.5 .. 52.9)
DX0, DX1 = TX + 1.9, TX + 4.3
slab_at(DX0 - 0.08, DX0, -1.9, 0.6, 0.0, 4.6, M.gold)
slab_at(DX1, DX1 + 0.08, -1.9, 0.6, 0.0, 4.6, M.gold)
slab_at(DX0, DX1, -1.9, -1.1, 3.6, 4.6, FACADE)
neon_text("LOBBY", (DX0 + DX1) / 2, 3.85, -1.95, 0.45, M.n_cyan, r=0.022, align="center", verts=4)
lathe([(1.0, 0.0), (1.0, 0.12), (0.0, 0.12)], ((DX0 + DX1) / 2, 0.2, 3.35), M.gold, segs=16)
rp = pivot("revolving_door", ((DX0 + DX1) / 2, 0.2, 0.0))
tube([((DX0 + DX1) / 2, 0.2, 0.0), ((DX0 + DX1) / 2, 0.2, 3.35)], 0.05, M.gold, verts=6, parent=rp)
for a in range(4):
    ang = TAU * a / 4 + 0.4
    c, s_ = math.cos(ang), math.sin(ang)
    cx, cy = (DX0 + DX1) / 2, 0.2
    mesh_obj([(cx, cy, 0.05), (cx + c * 0.95, cy + s_ * 0.95, 0.05), (cx + c * 0.95, cy + s_ * 0.95, 3.2), (cx, cy, 3.2)],
             [(0, 1, 2, 3), (3, 2, 1, 0)], M.glass, "wing", False, parent=rp, closed=False)
    tube([(cx + c * 0.95, cy + s_ * 0.95, 0.05), (cx + c * 0.95, cy + s_ * 0.95, 3.2)], 0.025, M.gold, verts=4, parent=rp)
merge_children(rp, "revolving_door_mesh")
spin(rp, "idle", "Z", seconds=4, turns=0.5)
# lit windows up the tower
rnd = rng(21)
WIN_PTS = {}
for r in range(-12, 5):
    if -1.2 < 5.6 + r * 1.5 < 5.0:                  # no windows across the lobby
        continue
    for c in range(6):
        wx = TX + 0.9 + c * 1.35
        wz = 5.6 + r * 1.5
        WIN_PTS.setdefault(int(rnd() * 3) if rnd() > 0.25 else 3, []).append((wx, wz))
    box((9.0, 0.06, 0.1), (TX + 4.5, -1.93, 5.0 + r * 1.5), STEEL_LIGHT)
for mi, pts in WIN_PTS.items():
    o = quad_dots(pts, -1.92, 1.0, (WIN_MATS + [M.glass_dark])[mi])
    for i, (wx, wz) in enumerate(pts):                  # widen the squares to 0.9 x 1.0 panes
        for j, (dx, dz) in enumerate(((-0.45, -0.5), (0.45, -0.5), (0.45, 0.5), (-0.45, 0.5))):
            o.data.vertices[i * 4 + j].co = (wx + dx, -1.92, wz + dz)
# blade sign
slab_at(TX - 0.9, TX - 0.2, -1.4, -1.2, 5.0, 12.2, M.black_metal)
for i, ch in enumerate("PALACE"):
    neon_text(ch, TX - 0.55, 11.1 - i * 1.15, -1.42, 0.8, M.n_pink, r=0.035, align="center", verts=4)
quad_dots([(TX - 0.9, 5.1 + i * 0.25) for i in range(29)] + [(TX - 0.2, 5.1 + i * 0.25) for i in range(29)], -1.43, 0.06,
          anim_neon((1.0, 0.8, 0.45), "marquee", 3.0))
neon_text("NEON", TX + 4.5, 10.9, -1.95, 1.0, M.n_cyan, r=0.045, align="center", verts=4)
# searchlights sweeping from the crown
for i, sx in enumerate((TX + 1.5, TX + 7.5)):
    slab_at(sx - 0.3, sx + 0.3, -0.5, 0.1, 12.6, 13.0, STEEL)
    sp = pivot("searchlight_%d" % i, (sx, -0.2, 13.1))
    lathe([(0.0, 0.3), (0.25, 0.25), (0.3, 0.0), (0.25, -0.1)], (sx, -0.2, 13.2), STEEL_LIGHT, segs=10, parent=sp)
    lathe([(0.25, 0.0), (2.2, 14.0)], (sx, -0.2, 13.4), beam_mat((0.7, 0.85, 1.0), 0.07, 1.3), segs=12, parent=sp, cap=False)
    merge_children(sp, sp.name + "_mesh")
    key(sp, "idle", "rotation_euler", [(LOOP * k / 8, (0.1 * math.cos(k * math.pi / 4), 0.5 * math.sin(k * math.pi / 4 + i * 2.0), 0)) for k in range(9)],
        interp="BEZIER")

# ----------------------------------------------- the exit from the shaft --
tube([(-0.05, -1.2, 0.0), (-0.05, -1.2, 3.3), (-0.05, 1.2, 3.3), (-0.05, 1.2, 0.0)], 0.05, M.n_cyan, verts=5)
slab_at(-0.3, 0.0, -1.5, 1.5, 3.3, 3.7, STEEL)
neon_text("SKYBRIDGE", -0.15, 3.4, -1.55, 0.22, M.n_pink, r=0.012, align="center", verts=3)

finish("skybridge", 2048, 12000)
