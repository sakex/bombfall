# Backdrop for the sky bar (rich2), Neon Palace: a five-metre reef aquarium
# glowing blue on a black marble plinth (tropical fish swim laps, bubbles
# rise, kelp sways, fluorescent coral), a velvet lounge in front of it, a
# backlit onyx bar with brass foot rail, stools, cocktails and a back bar of
# bottles under a "SKY BAR" neon, and a DJ booth with spinning decks,
# pulsing speaker stacks and a bouncing equaliser on an LED wall.  Above
# the window band: art-deco fan lights and a neon wave.  15 m wide.
#   blender -b --python blender/backdrop_rich2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
WINDOWS = [(0.4, 5.2, 2.6, 1.6), (12.2, 5.2, 2.6, 1.6), (3.6, 5.2, 7.8, 1.5)]
LACQUER = pbr("plastic", (0.05, 0.09, 0.2), rough=0.2, name="navy_lacquer")
FISH_MATS = [neon_mat(c, s, n) for c, s, n in (((1.0, 0.35, 0.05), 1.3, "fish_orange"), ((0.1, 0.35, 1.0), 1.4, "fish_blue"),
                                                 ((1.0, 0.85, 0.1), 1.2, "fish_yellow"), ((0.9, 0.9, 1.0), 1.0, "fish_white"),
                                                 ((1.0, 0.2, 0.55), 1.3, "fish_pink"))]
CORAL = [neon_mat((1.0, 0.25, 0.6), 1.6, "coral_pink"), neon_mat((1.0, 0.5, 0.15), 1.5, "coral_orange"),
         neon_mat((0.6, 0.3, 1.0), 1.5, "coral_violet"), neon_mat((0.3, 1.0, 0.7), 1.3, "coral_mint")]
BUBBLE = neon_mat((0.7, 0.95, 1.0), 1.2, "bubble")

# ------------------------------------------------------------ architecture --
slab_at(0.0, 15.0, 0.0, WALL, 0.0, 0.02, M.terrazzo)
for bx in (0.2, 5.6, 11.6, 14.8):
    box((0.03, WALL, 0.004), (bx, WALL / 2, 0.021), M.brass)
box((15.0, 0.03, 0.004), (7.5, 0.05, 0.021), M.brass)
# navy lacquer wall panels with brass pinstripes on the lower wall
wall_cover(WINDOWS, 0.0, 9.3, LACQUER)
for i in range(26):
    px = 0.3 + i * 0.58
    if 0.2 < px < 5.5 or 6.1 < px < 11.1 or 11.9 < px < 14.8:
        continue
    box((0.035, 0.02, 4.9), (px, WALL - 0.03, 2.55), M.brass)
box((15.0, 0.05, 0.05), (7.5, WALL - 0.03, 5.08), M.brass)
tube([(0.05, WALL - 0.06, 5.12), (14.95, WALL - 0.06, 5.12)], 0.015, M.n_cyan, verts=4)

# --------------------------------------------------------------- aquarium --
AX0, AX1, AZ0, AZ1 = 0.35, 5.35, 0.95, 4.2
AYF, AYB = 1.16, 1.9
slab_at(AX0 - 0.1, AX1 + 0.1, AYF - 0.08, WALL, 0.0, AZ0, M.marble_black)                   # plinth
box((AX1 - AX0 + 0.2, 0.02, 0.03), ((AX0 + AX1) / 2, AYF - 0.09, AZ0 - 0.12), M.brass)
box((AX1 - AX0 + 0.2, 0.02, 0.03), ((AX0 + AX1) / 2, AYF - 0.09, 0.1), M.brass)
# water: a deep-to-bright gradient on the back, light rays, caustic ripples
for k in range(5):
    z0 = AZ0 + (AZ1 - AZ0) * k / 5
    z1 = AZ0 + (AZ1 - AZ0) * (k + 1) / 5
    c = (0.01 + 0.012 * k, 0.07 + 0.07 * k, 0.28 + 0.09 * k)
    box((AX1 - AX0, 0.02, z1 - z0 + 0.002), ((AX0 + AX1) / 2, AYB - 0.01, (z0 + z1) / 2), neon_mat(c, 1.0, "water%d" % k))
for k in range(3):
    pts = [(AX0 + 0.1 + (AX1 - AX0 - 0.2) * i / 14, AYB - 0.03, AZ1 - 0.25 - k * 0.22 + math.sin(i * 1.7 + k) * 0.05) for i in range(15)]
    tube(pts, 0.012, neon_mat((0.5, 0.95, 1.0), 1.6, "caustic"), verts=3, caps=False)
for k, bx in enumerate((1.1, 2.6, 4.2)):
    v = [(bx - 0.25, AYB - 0.06, AZ1), (bx + 0.25, AYB - 0.06, AZ1), (bx + 0.9, AYF + 0.25, AZ0 + 0.3), (bx - 0.1, AYF + 0.25, AZ0 + 0.3)]
    mesh_obj(v, [(0, 1, 2, 3), (3, 2, 1, 0)], beam_mat((0.5, 0.9, 1.0), 0.08, 1.2, "ray"), "ray", False, closed=False)
# sand, rocks, corals
prism([(AX0, AZ0), (AX1, AZ0), (AX1, AZ0 + 0.18), (AX0 + 3.6, AZ0 + 0.28), (AX0 + 2.0, AZ0 + 0.14), (AX0 + 0.8, AZ0 + 0.3), (AX0, AZ0 + 0.2)],
      AYF + 0.02, AYB - 0.02, M.sand, plane="xz")
rnd = rng(7)
for (rx, ry, rs) in ((0.9, 1.7, 0.35), (1.5, 1.75, 0.5), (3.4, 1.72, 0.45), (4.6, 1.65, 0.3), (2.3, 1.5, 0.22)):
    o = ico(rs, (AX0 + rx, ry, AZ0 + 0.18 + rs * 0.4), M.rock, subdiv=1)
    o.scale = (1.3, 0.6, 0.8)
for (cx, cz, m, n) in ((0.95, 1.55, CORAL[0], 5), (1.75, 1.75, CORAL[2], 6), (3.4, 1.75, CORAL[1], 5), (4.5, 1.45, CORAL[3], 4), (2.6, 1.3, CORAL[0], 4)):
    X = AX0 + cx
    for k in range(n):
        a = math.pi * (0.15 + 0.7 * k / max(n - 1, 1))
        L = 0.35 + rnd() * 0.3
        mid = (X + math.cos(a) * L * 0.4, 1.62 + (rnd() - 0.5) * 0.2, cz - 0.2 + math.sin(a) * L * 0.5)
        end = (X + math.cos(a) * L * 0.8, mid[1], cz - 0.2 + math.sin(a) * L)
        tube([(X, 1.62, cz - 0.35), mid, end], 0.035, m, verts=4, radii=[0.05, 0.035, 0.018])
brain = ico(0.2, (AX0 + 2.95, 1.55, AZ0 + 0.3), CORAL[1], subdiv=2)
brain.scale = (1.2, 0.8, 0.7)
# kelp swaying from the sand
for i, kx in enumerate((0.55, 1.35, 2.15, 3.9, 4.85)):
    p = pivot("kelp_%d" % i, (AX0 + kx, 1.78, AZ0 + 0.2))
    hgt = 2.0 + (i % 3) * 0.45
    pts = [(AX0 + kx + math.sin(t * 2.5 + i) * 0.08, 1.78, AZ0 + 0.2 + hgt * t / 6) for t in range(7)]
    tube(pts, 0.05, M.leaf_light, verts=3, caps=False, parent=p, radii=[0.03, 0.06, 0.07, 0.07, 0.06, 0.05, 0.02])
    merge_children(p, p.name + "_mesh")
    wobble(p, "idle", "rotation_euler", 1, 0.12, seconds=4, phase=i * 1.3)
# fish swimming laps (pivot keyed along x, turning at each end, tail wagging)


def fish(i, x0, x1, y, z, size, m, fins=None, phase=0.0):
    p = pivot("fish_%d" % i, (x0, y, z))
    body = sphere(size, (x0, y, z), m, scale=(1.6, 0.45, 1.0 if i % 3 else 1.35), segments=8, rings=5, parent=p)
    tail = pivot("fish_%d_tail" % i, (x0 - size * 1.45, y, z), parent=p)
    prism([(x0 - size * 1.45, z), (x0 - size * 2.3, z + size * 0.8), (x0 - size * 2.1, z), (x0 - size * 2.3, z - size * 0.8)],
          y - size * 0.05, y + size * 0.05, fins or m, plane="xz", parent=tail)
    prism([(x0 - size * 0.6, z + size * 0.8), (x0 + size * 0.3, z + size * 0.95), (x0 - size * 0.9, z + size * 1.5)],
          y - size * 0.04, y + size * 0.04, fins or m, plane="xz", parent=p)
    ico(size * 0.14, (x0 + size * 1.1, y - size * 0.4, z + size * 0.25), M.plastic_black, subdiv=1, parent=p)
    merge_children(tail, tail.name + "_mesh")
    parts = [c for c in p.children if c.type == "MESH"]
    join(parts, p.name + "_mesh")
    # a lap: out along +x, a quick turn, back along -x, turn; sampled with
    # a per-fish time offset so the school is not in step
    def at(t):
        if t < 0.42:
            u = t / 0.42
            return x0 + (x1 - x0) * u, dz * math.sin(u * math.pi), 0.0
        if t < 0.5:
            u = (t - 0.42) / 0.08
            return x1 + size * 0.6 * math.sin(u * math.pi), 0.0, math.pi * u
        if t < 0.92:
            u = (t - 0.5) / 0.42
            return x1 + (x0 - x1) * u, -dz * math.sin(u * math.pi), math.pi
        u = (t - 0.92) / 0.08
        return x0 - size * 0.6 * math.sin(u * math.pi), 0.0, math.pi + math.pi * u
    dz = size * 0.8
    n = 40
    ks_loc, ks_rot = [], []
    for k in range(n + 1):
        tt = k / n + phase
        xx, zz, rz = at(tt % 1.0)
        rz += TAU * math.floor(tt)
        ks_loc.append((LOOP * k / n, (xx, y, z + zz)))
        ks_rot.append((LOOP * k / n, (0.0, 0.0, rz)))
    key(p, "idle", "location", ks_loc, interp="LINEAR")
    key(p, "idle", "rotation_euler", ks_rot, interp="LINEAR")
    key(tail, "idle", "rotation_euler", [(LOOP * k / 16, (0, 0, 0.35 if k % 2 else -0.35)) for k in range(17)], interp="BEZIER")
    return p


fish(0, AX0 + 0.5, AX0 + 2.6, 1.45, 2.9, 0.1, FISH_MATS[0], FISH_MATS[3], phase=0.00)
fish(1, AX0 + 1.8, AX0 + 4.2, 1.6, 3.5, 0.13, FISH_MATS[1], FISH_MATS[2], phase=0.37)
fish(2, AX0 + 2.5, AX0 + 4.6, 1.4, 2.2, 0.11, FISH_MATS[2], phase=0.74)
fish(3, AX0 + 0.6, AX0 + 2.0, 1.7, 1.9, 0.08, FISH_MATS[4], FISH_MATS[3], phase=0.11)
fish(4, AX0 + 3.0, AX0 + 4.5, 1.55, 3.1, 0.09, FISH_MATS[0], FISH_MATS[3], phase=0.48)
fish(5, AX0 + 1.0, AX0 + 3.4, 1.75, 2.5, 0.07, FISH_MATS[1], phase=0.85)
fish(6, AX0 + 3.2, AX0 + 4.7, 1.35, 1.55, 0.07, FISH_MATS[4], phase=0.22)
fish(7, AX0 + 0.4, AX0 + 1.6, 1.5, 3.7, 0.09, FISH_MATS[2], FISH_MATS[1], phase=0.59)
# bubbles rising from two airstones
for s, bx in enumerate((AX0 + 1.25, AX0 + 4.1)):
    lathe([(0.05, 0), (0.05, 0.05), (0.0, 0.06)], (bx, 1.75, AZ0 + 0.2), M.rock, segs=6)
    for k in range(6):
        phase = (k / 6.0 + s * 0.08) % 1.0
        r = 0.02 + (k % 3) * 0.012
        zb, zt = AZ0 + 0.3, AZ1 - 0.1
        p = pivot("bubble_%d_%d" % (s, k), (bx, 1.75, zb))
        ico(r, (bx, 1.75, zb), BUBBLE, subdiv=1, parent=p)
        f_top = (1.0 - phase) * LOOP
        z_at0 = zb + (zt - zb) * phase
        wig = 0.04 * (1 if k % 2 else -1)
        ks = [(0, (bx + wig * 0.5, 1.75, z_at0)), (f_top, (bx + wig, 1.75, zt)), (min(f_top + 1, LOOP), (bx, 1.75, zb)), (LOOP, (bx + wig * 0.5, 1.75, z_at0))]
        ks = sorted({f: v for f, v in ks}.items())
        key(p, "idle", "location", ks, interp="LINEAR")
# glass front, a steel frame and an LED hood
box((AX1 - AX0, 0.02, AZ1 - AZ0 + 0.1), ((AX0 + AX1) / 2, AYF, (AZ0 + AZ1) / 2 + 0.05), M.glass)
slab_at(AX0 - 0.12, AX1 + 0.12, AYF - 0.1, WALL, AZ1 + 0.05, AZ1 + 0.4, M.black_metal)
box((AX1 - AX0 + 0.24, 0.02, 0.03), ((AX0 + AX1) / 2, AYF - 0.11, AZ1 + 0.3), M.brass)
tube([(AX0, AYF - 0.02, AZ1 + 0.04), (AX1, AYF - 0.02, AZ1 + 0.04)], 0.02, M.n_cyan, verts=4)
for fx in (AX0 - 0.06, AX1 + 0.06):
    slab_at(fx - 0.06, fx + 0.06, AYF - 0.1, WALL, AZ0 - 0.05, AZ1 + 0.05, M.black_metal)
    box((0.02, 0.02, AZ1 - AZ0), (fx, AYF - 0.11, (AZ0 + AZ1) / 2), M.brass)

# ----------------------------------------------------------------- lounge --
modern_sofa(2.85, 0.12, w=2.9, m=M.velvet_teal, d=0.85, h=0.72, cushions=3)
for i, px in enumerate((1.9, 3.8)):
    pillow(px - 0.2, px + 0.2, 0.42, 0.78, 0.62, 0.07, [M.velvet_gold, M.velvet_plum][i], nx=2, nz=2)
lathe([(0.15, 0), (0.05, 0.05), (0.04, 0.36), (0.0, 0.36)], (0.75, 0.55, 0), M.brass, segs=8)
lathe([(0.26, 0), (0.26, 0.03), (0.0, 0.03)], (0.75, 0.55, 0.36), M.marble_black, segs=14)
cocktail(0.7, 0.5, 0.39, 0, M.n_pink)
cocktail(0.85, 0.62, 0.39, 2, M.n_cyan)
potted_palm(5.8, 1.05, h=2.4, fronds=8, seed=9, m_pot=M.gold)

# -------------------------------------------------------------------- bar --
BX0, BX1 = 6.5, 11.0
# back bar: cabinets, a backlit onyx wall with glass shelves of bottles
slab_at(BX0, BX1, 1.45, WALL, 0.0, 1.0, M.walnut)
for i in range(6):
    a = BX0 + 0.05 + i * (BX1 - BX0 - 0.1) / 6
    moulding_frame(a + 0.06, a + (BX1 - BX0 - 0.1) / 6 - 0.06, 0.12, 0.88, 1.44, M.brass, t=0.02)
slab_at(BX0 - 0.03, BX1 + 0.03, 1.4, WALL, 1.0, 1.05, M.marble_black)
slab_at(BX0, BX1, WALL - 0.03, WALL, 1.05, 3.3, M.backlight)
for sx in (BX0, BX1):
    slab_at(sx - 0.06, sx + 0.06, 1.5, WALL, 1.05, 3.3, M.walnut)
slab_at(BX0 - 0.08, BX1 + 0.08, 1.45, WALL, 3.3, 3.42, M.walnut)
box((BX1 - BX0 + 0.16, 0.02, 0.03), ((BX0 + BX1) / 2, 1.44, 3.36), M.brass)
BOTTLES = [M.glass_bottle_green, M.glass_bottle_amber, M.glass_bottle_clear, M.glass_bottle_blue, M.glass_bottle_amber]
for k, sz in enumerate((1.05, 1.75, 2.45)):
    if k:
        box((BX1 - BX0 - 0.12, 0.3, 0.02), ((BX0 + BX1) / 2, 1.75, sz), M.glass)
    n = 13 if k else 10
    for j in range(n):
        bx = BX0 + 0.25 + j * (BX1 - BX0 - 0.5) / (n - 1)
        bottle(bx, 1.74, sz + 0.01, kind=(j * 3 + k) % 4, m=BOTTLES[(j + k * 2) % len(BOTTLES)], h=0.3 + ((j + k) % 3) * 0.04)
# "SKY BAR" neon on a mirror band above the back bar
slab_at(BX0 - 0.08, BX1 + 0.08, WALL - 0.04, WALL, 3.5, 4.75, M.mirror)
moulding_frame(BX0 - 0.08, BX1 + 0.08, 3.5, 4.75, WALL - 0.05, M.brass, t=0.04)
neon_text("SKY BAR", (BX0 + BX1) / 2, 3.78, WALL - 0.09, 0.72, M.n_cyan, r=0.032, align="center", verts=4)
# the counter: fluted walnut ribs over a warm-lit onyx core, marble top
prism(rounded_rect(BX1 - BX0 + 0.3, 0.55, 0.2, 3, (BX0 + BX1) / 2, 0.62), 0.0, 1.02, M.backlight, plane="xy")
nr = 34
for i in range(nr):
    rx = BX0 - 0.1 + (BX1 - BX0 + 0.2) * (i + 0.5) / nr
    box((0.06, 0.05, 0.98), (rx, 0.34, 0.51), M.walnut)
slab_at(BX0 - 0.2, BX1 + 0.2, 0.3, 0.38, 0.0, 0.1, M.black_metal)
prism(rounded_rect(BX1 - BX0 + 0.45, 0.72, 0.25, 3, (BX0 + BX1) / 2, 0.62), 1.02, 1.09, M.marble_black, plane="xy")
box((BX1 - BX0 + 0.1, 0.02, 0.05), ((BX0 + BX1) / 2, 0.255, 1.055), M.brass)
tube([(BX0 - 0.1, 0.18, 0.22), (BX1 + 0.1, 0.18, 0.22)], 0.025, M.brass, verts=6)
for rx in (BX0 + 0.2, (BX0 + BX1) / 2, BX1 - 0.2):
    tube([(rx, 0.18, 0.22), (rx, 0.32, 0.3)], 0.015, M.brass, verts=4)
for i in range(4):
    bar_stool(BX0 + 0.55 + i * 1.12, 0.0 + 0.02, h=0.8)
# on the counter
cocktail(7.2, 0.6, 1.09, 0, M.n_pink)
cocktail(8.4, 0.5, 1.09, 1, M.n_amber)
cocktail(8.55, 0.62, 1.09, 2, M.n_cyan)
cocktail(10.2, 0.55, 1.09, 0, M.n_green)
lathe([(0.04, 0), (0.045, 0.12), (0.03, 0.17), (0.02, 0.22), (0.0, 0.23)], (9.3, 0.6, 1.09), M.chrome, segs=8)
lathe([(0.08, 0), (0.1, 0.2), (0.11, 0.22), (0.1, 0.22)], (7.8, 0.65, 1.09), M.chrome, segs=10, cap=False)
bottle(7.82, 0.65, 1.12, kind=3, m=M.glass_bottle_green)
for lx in (7.0, 9.8):
    lathe([(0.07, 0), (0.07, 0.01), (0.015, 0.03), (0.012, 0.3)], (lx, 0.75, 1.09), M.brass, segs=8, cap=False)
    lathe([(0.12, 0.0), (0.07, 0.12), (0.0, 0.13)], (lx, 0.75, 1.36), M.shade, segs=10)

# ------------------------------------------------------------------- DJ --
DX = 13.35
# LED wall with a bouncing equaliser
slab_at(DX - 1.3, DX + 1.3, WALL - 0.06, WALL, 1.6, 4.7, M.black_metal)
box((2.45, 0.02, 2.95), (DX, WALL - 0.07, 3.15), anim_neon((0.35, 0.15, 0.9), "screen", 1.0))
for i in range(12):
    bx = DX - 1.05 + i * 0.19
    p = pivot("eq_%d" % i, (bx, WALL - 0.1, 1.75))
    box((0.13, 0.02, 1.0), (bx, WALL - 0.1, 2.25), [M.n_pink, M.n_magenta, M.n_cyan][i % 3], parent=p)
    rv = rng(i + 30)
    vals = [(1, 1, 0.2 + 0.8 * rv()) for _ in range(16)]
    keys_loop(p, "scale", vals, interp="LINEAR")
# speakers either side
speaker(11.95, 1.3, w=0.55, h=1.5, d=0.5, name="woofer_l", beat_phase=0)
speaker(14.7, 1.3, w=0.5, h=1.5, d=0.5, name="woofer_r", beat_phase=1)
# the booth: a slanted front with chasing LED stripes, decks on top
prism([(0.35, 0.0), (1.2, 0.0), (1.2, 1.02), (0.25, 1.02)], DX - 1.0, DX + 1.0, M.black_metal, plane="yz")
for k in range(3):
    box((1.95, 0.02, 0.04), (DX, 0.3 + 0.03 * k * 0, 0.3 + k * 0.22), anim_neon("cyan" if k % 2 else "pink", "marquee"), rot=(-0.1, 0, 0))
slab_at(DX - 1.05, DX + 1.05, 0.25, 1.25, 1.02, 1.06, M.marble_black)
box((2.1, 0.02, 0.04), (DX, 0.24, 1.04), M.chrome)
for sx in (-1, 1):
    cx = DX + sx * 0.62
    slab_at(cx - 0.24, cx + 0.24, 0.45, 0.85, 1.06, 1.14, M.plastic_grey)
    rp = pivot("spin_deck_%s" % ("l" if sx < 0 else "r"), (cx - 0.04, 0.64, 1.145))
    lathe([(0.16, 0), (0.16, 0.012), (0.05, 0.012), (0.0, 0.013)], (cx - 0.04, 0.64, 1.14), M.plastic_black, segs=14, parent=rp)
    lathe([(0.05, 0), (0.05, 0.004), (0.0, 0.004)], (cx - 0.04, 0.64, 1.153), [M.n_pink, M.n_cyan][sx > 0], segs=8, parent=rp)
    box((0.03, 0.1, 0.005), (cx + 0.04, 0.64, 1.156), M.plastic_white, parent=rp)
    merge_children(rp, rp.name + "_mesh")
    tube([(cx + 0.19, 0.78, 1.16), (cx + 0.19, 0.78, 1.2), (cx + 0.13, 0.6, 1.2), (cx + 0.05, 0.55, 1.17)], 0.006, M.chrome, verts=4)
slab_at(DX - 0.16, DX + 0.16, 0.45, 0.85, 1.06, 1.16, M.plastic_black)
for k in range(4):
    box((0.02, 0.1, 0.02), (DX - 0.1 + k * 0.066, 0.62, 1.17), M.plastic_white)
    lathe([(0.012, 0), (0.012, 0.02)], (DX - 0.1 + k * 0.066, 0.52, 1.16), [M.n_cyan, M.n_pink][k % 2], segs=5, cap=False)
# laptop on a stand
tube([(DX, 0.95, 1.06), (DX, 1.0, 1.25)], 0.012, M.chrome, verts=4)
box((0.34, 0.24, 0.015), (DX, 1.0, 1.26), M.steel, rot=(0.25, 0, 0))
box((0.34, 0.015, 0.22), (DX, 1.14, 1.38), M.steel, rot=(-0.25, 0, 0))
box((0.3, 0.005, 0.18), (DX, 1.13, 1.38), anim_neon("violet", "screen", 1.4), rot=(-0.25, 0, 0))
torus(0.09, 0.012, (DX + 0.35, 0.95, 1.12), M.plastic_black, rot=(math.pi / 2, 0, 0), major_segments=10, minor_segments=3)

# -------------------------------------------------------------- upper band --
for fx in (1.2, 7.5, 13.8):
    # art-deco fan light: a stepped half-disc with gold rays over a glow
    prism(circle_pts(fx, 7.15, 0.55, 12, 0.0, math.pi), WALL - 0.04, WALL - 0.01, M.shade, plane="xz")
    for k in range(7):
        a = math.pi * (k + 0.5) / 7
        tube([(fx, WALL - 0.06, 7.15), (fx + math.cos(a) * 0.62, WALL - 0.06, 7.15 + math.sin(a) * 0.62)], 0.018, M.gold, verts=4)
    tube([(fx + math.cos(math.pi * i / 12) * 0.62, WALL - 0.06, 7.15 + math.sin(math.pi * i / 12) * 0.62) for i in range(13)], 0.022, M.gold, verts=4)
    box((1.4, 0.05, 0.06), (fx, WALL - 0.04, 7.1), M.gold)
for k in range(2):
    pts = [(0.2 + 14.6 * i / 40, WALL - 0.05, 8.2 + k * 0.28 + math.sin(i * 0.5 + k) * 0.12) for i in range(41)]
    tube(pts, 0.02, [M.n_cyan, M.n_pink][k], verts=4, caps=False)
neon_text("COCKTAILS", 4.35, 7.25, WALL - 0.05, 0.45, M.n_pink, r=0.022, verts=4, align="center")
neon_text("DJ NIGHTS", 10.65, 7.25, WALL - 0.05, 0.45, M.n_cyan, r=0.022, verts=4, align="center")

finish("backdrop_rich2", 2048, 14000, windows=WINDOWS, wall=(0.06, 0.07, 0.21))
