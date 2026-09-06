# Synthwave / cyberpunk dressing kit for the room backdrops, used next to
# props.py:  `from synth import *`.  Everything follows the backdrop
# conventions: X is the room width (0..15), Z is up with the floor at 0,
# +Y goes deeper into the room (the back wall sits at y = D = 1.85), and
# the helpers build at a position and return nothing (the theme script joins
# the meshes with join_static at the end).  Pieces are deliberately cheap:
# bevel-free cubes, 4-6 sided rods, so a whole room of them stays well under
# the face budget.  The colours match the city shaders (sun.gdshader,
# grid.gdshader, the billboard palette): hot pink, ice cyan, lavender,
# sunset orange over deep navy/plum bases.
import math

import bpy

from common import *  # noqa: F401,F403

# ---------------------------------------------------------------- palette --
SYNTH_NAVY = (0.030, 0.020, 0.090)
SYNTH_INK = (0.045, 0.020, 0.075)
SYNTH_PLUM = (0.100, 0.035, 0.170)
SYNTH_GRAPE = (0.160, 0.050, 0.260)
SYNTH_DUSK = (0.220, 0.080, 0.300)
HOT_PINK = (1.00, 0.20, 0.70)
ICE = (0.25, 0.90, 1.00)
LAVENDER = (0.70, 0.30, 1.00)
SUN_YELLOW = (1.00, 0.92, 0.45)
SUN_ORANGE = (1.00, 0.45, 0.25)
SUN_MAGENTA = (0.95, 0.12, 0.55)
MINT_G = (0.30, 1.00, 0.75)

# Dark bases (base, roughness, metallic).
MAT_NAVY = (SYNTH_NAVY, 0.8, 0.0)
MAT_INK = (SYNTH_INK, 0.85, 0.0)
MAT_PLUM = (SYNTH_PLUM, 0.8, 0.0)
MAT_GRAPE = (SYNTH_GRAPE, 0.75, 0.0)
MAT_DUSK = (SYNTH_DUSK, 0.75, 0.0)
GLOSS_NAVY = (SYNTH_NAVY, 0.08, 0.35)       # wet, reflective floor
GLOSS_PLUM = (SYNTH_PLUM, 0.10, 0.30)
CHROME_M = ((0.70, 0.72, 0.80), 0.15, 1.0)

# Neons.
NEON_HOT = neon(HOT_PINK, 4.0)
NEON_ICE = neon(ICE, 4.0)
NEON_LAV = neon(LAVENDER, 4.0)
NEON_SUN = neon(SUN_ORANGE, 3.5)
NEON_SUNSET = neon(SUN_MAGENTA, 4.0)
NEON_MINT = neon(MINT_G, 3.5)
NEON_STAR = neon((1.0, 0.95, 0.9), 2.5, (0.3, 0.3, 0.3))
SYNTH_NEONS = [NEON_HOT, NEON_ICE, NEON_LAV, NEON_SUN]
# Dim "lit screen" faces.
SCREEN_PINK = neon((1.0, 0.35, 0.7), 1.4, (0.12, 0.03, 0.08))
SCREEN_ICE = neon(ICE, 1.4, (0.03, 0.10, 0.12))
SCREEN_LAV = neon(LAVENDER, 1.4, (0.08, 0.03, 0.14))


def _lerp3(a, b, t):
    return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))


def _rng(seed):
    """A tiny deterministic generator: returns a function giving 0..1."""
    state = [seed * 7919 + 17]

    def nxt():
        state[0] = (state[0] * 1103515245 + 12345) & 0x7FFFFFFF
        return (state[0] >> 8) / float(1 << 23)
    return nxt


# ------------------------------------------------------------- tube lines --
def tube(p0, p1, m, r=0.025):
    """One glowing neon tube between two points (a 6-sided rod)."""
    return rod(p0, p1, r, m, verts=6)


def _split(a, b, cuts):
    """Split the span a..b around the (lo, hi) intervals in `cuts`."""
    spans = [(a, b)]
    for lo, hi in cuts:
        out = []
        for s0, s1 in spans:
            if hi <= s0 or lo >= s1:
                out.append((s0, s1))
                continue
            if lo > s0:
                out.append((s0, lo))
            if hi < s1:
                out.append((hi, s1))
        spans = out
    return [(s0, s1) for s0, s1 in spans if s1 - s0 > 0.05]


def hline(x0, x1, y, z, m, r=0.02, avoid=()):
    """A horizontal tube on the wall, broken around the window rectangles in
    `avoid` (each (x, z, w, h) in room coordinates, as in SpawnRegistry)."""
    cuts = [(rx - 0.15, rx + rw + 0.15) for (rx, rz, rw, rh) in avoid if rz - 0.15 < z < rz + rh + 0.15]
    for s0, s1 in _split(x0, x1, cuts):
        tube((s0, y, z), (s1, y, z), m, r)


def vline(x, y, z0, z1, m, r=0.02, avoid=()):
    cuts = [(rz - 0.15, rz + rh + 0.15) for (rx, rz, rw, rh) in avoid if rx - 0.15 < x < rx + rw + 0.15]
    for s0, s1 in _split(z0, z1, cuts):
        tube((x, y, s0), (x, y, s1), m, r)


def neon_tube_frame(x0, x1, z0, z1, y, m, r=0.025):
    """A glowing rectangular outline standing on the wall."""
    tube((x0, y, z0), (x1, y, z0), m, r)
    tube((x0, y, z1), (x1, y, z1), m, r)
    tube((x0, y, z0), (x0, y, z1), m, r)
    tube((x1, y, z0), (x1, y, z1), m, r)


def window_neon(rect, y, m, margin=0.2, r=0.03):
    """A neon outline just outside a window opening (rect = (x, z, w, h))."""
    x, z, w, h = rect
    neon_tube_frame(x - margin, x + w + margin, z - margin, z + h + margin, y, m, r)


def neon_seams(x0, x1, z0, z1, y, m, spacing=1.5, avoid=(), r=0.015):
    """Glowing panel seams replacing wall_panel_lines: one horizontal line
    at each `spacing` and verticals at 1.5 x spacing, skipping windows."""
    zz = z0 + spacing
    while zz < z1 - 0.1:
        hline(x0, x1, y, zz, m, r, avoid)
        zz += spacing
    xx = x0 + spacing * 1.5
    while xx < x1 - 0.1:
        vline(xx, y, z0, z1, m, r, avoid)
        xx += spacing * 1.5


def horizon_lines(x0, x1, y, z, n=4, spacing=0.12, m=NEON_HOT, r=0.015, avoid=()):
    """A stack of thin horizontal glow lines (the striped-horizon motif)."""
    for i in range(n):
        hline(x0, x1, y, z + i * spacing, m, r, avoid)


def neon_polygon(x, z, y, r, n, m, rot=0.0, tube_r=0.025):
    """An outline polygon (n=3 triangle...) on the wall, centre (x, z)."""
    pts = []
    for i in range(n):
        a = rot + math.pi / 2 + i * math.tau / n
        pts.append((x + math.cos(a) * r, y, z + math.sin(a) * r))
    for i in range(n):
        tube(pts[i], pts[(i + 1) % n], m, tube_r)


def chrome_trim(x0, x1, y, z, r=0.03):
    """A chrome rail."""
    rod((x0, y, z), (x1, y, z), r, CHROME_M, verts=8)


# ------------------------------------------------------------- big motifs --
def sunset_mural(x, z, y, r, bands=8, half=False, panel=True, frame=NEON_HOT, grid=True, backing=MAT_NAVY):
    """The synthwave sun: a striped disc grading yellow -> orange -> magenta
    with gaps that widen towards the bottom, on a dark panel with a horizon
    line and a converging grid below it.  (x, z) is the disc centre; the
    panel is about 2.6 r wide.  With `half`, only the upper half shows above
    the horizon."""
    top = z + r
    bottom = z if half else z - r
    height = top - bottom
    if panel:
        pw, ph = r * 2.6, height + r * (1.4 if grid else 0.5)
        pz = bottom + ph / 2 - r * (1.0 if grid else 0.25)
        cube((pw, 0.05, ph), (x, y + 0.03, pz), backing, bevel=0.0)
        if frame is not None:
            neon_tube_frame(x - pw / 2, x + pw / 2, pz - ph / 2, pz + ph / 2, y - 0.01, frame, r=0.02)
    seg = height / bands
    for i in range(bands):
        frac = (i + 0.5) / bands               # 0 at the top, 1 at the bottom
        gap = 0.55 * max(0.0, min(1.0, (frac - 0.35) / 0.6)) ** 1.2
        bh = seg * (1.0 - gap)
        zc = top - i * seg - bh / 2
        dz = zc - z
        if abs(dz) >= r:
            continue
        w = 2.0 * math.sqrt(max(r * r - dz * dz, 0.0))
        if frac < 0.5:
            col = _lerp3(SUN_YELLOW, SUN_ORANGE, frac / 0.5)
        else:
            col = _lerp3(SUN_ORANGE, SUN_MAGENTA, (frac - 0.5) / 0.5)
        cube((w, 0.04, bh), (x, y - 0.02, zc), neon(col, 3.0, tuple(c * 0.3 for c in col)), bevel=0.0)
    if grid and panel:
        hz = bottom - r * 0.05
        gx0, gx1 = x - r * 1.3, x + r * 1.3
        cube((r * 2.6, 0.03, 0.03), (x, y - 0.015, hz), NEON_ICE, bevel=0.0)
        depth = r * 0.9
        for k in (-3, -2, -1, 0, 1, 2, 3):
            fx = x + k * r * 0.45
            bx = x + k * r * 0.12
            rod((fx, y - 0.015, hz - depth), (bx, y - 0.015, hz), 0.012, NEON_HOT, verts=4)
        for k in (1, 2, 3):
            lz = hz - depth * (k * k) / 9.0
            cube((r * 2.6, 0.03, 0.02), (x, y - 0.015, lz), NEON_HOT, bevel=0.0)


def grid_floor(x0, x1, y0, y1, z=0.0, m=NEON_HOT, m2=None, nx=6, ny=3, r=0.012, converge=0.5):
    """Glowing grid lines on the floor: `ny + 1` lines across and `nx + 1`
    lines running towards the back wall, converging a little so the floor
    reads as a synthwave plain even from straight on."""
    m2 = m2 or m
    for j in range(ny + 1):
        yy = y0 + (y1 - y0) * j / ny
        cube((x1 - x0, 0.03, r * 2), ((x0 + x1) / 2, yy, z + r), m if j % 2 else m2, bevel=0.0)
    cx = (x0 + x1) / 2
    for i in range(nx + 1):
        fx = x0 + (x1 - x0) * i / nx
        bx = cx + (fx - cx) * (1.0 - converge * 0.5)
        rod((fx, y0, z + r), (bx, y1, z + r), r, m if i % 2 else m2, verts=4)


def wet_floor(x0, x1, y0, y1, z=0.0, m=GLOSS_NAVY):
    """A glossy dark slab so the neon reflects a little."""
    cube((x1 - x0, y1 - y0, 0.02), ((x0 + x1) / 2, (y0 + y1) / 2, z + 0.01), m, bevel=0.0)


def neon_palm(x, y, z, h, m=NEON_HOT, fronds=6, lean=0.12, r=0.03):
    """A palm silhouette drawn in neon tubes (trunk + drooping fronds), in
    the wall plane so it reads from the front."""
    pts = [(x, y, z), (x + lean * h * 0.25, y, z + h * 0.4), (x + lean * h * 0.6, y, z + h * 0.75), (x + lean * h, y, z + h)]
    for a, b in zip(pts, pts[1:]):
        rod(a, b, r, m, verts=5)
    tx, tz = x + lean * h, z + h
    fl = h * 0.45
    for k in range(fronds):
        a = math.pi * (0.08 + 0.84 * k / (fronds - 1))
        dx, dz = math.cos(a), math.sin(a)
        p = (tx, y, tz)
        for s in range(3):
            droop = 0.25 * (s + 1)
            q = (p[0] + dx * fl / 3, y, p[2] + (dz - droop) * fl / 3)
            rod(p, q, r * 0.8, m, verts=5)
            p = q
    sphere(r * 2.2, (tx, y, tz), m, segments=6, rings=4)


def chevron_strip(x0, x1, z, y, m=NEON_ICE, h=0.35, thick=0.05, direction=1, avoid=()):
    """A row of neon chevrons (arrows) along the wall."""
    step = h * 1.25
    cuts = [(rx - 0.3, rx + rw + 0.3) for (rx, rz, rw, rh) in avoid if rz - h < z < rz + rh + h]
    for s0, s1 in _split(x0, x1, cuts):
        n = int((s1 - s0) / step)
        if n < 1:
            continue
        start = s0 + ((s1 - s0) - n * step) / 2 + step / 2
        for i in range(n):
            cx = start + i * step
            arm = h * 0.72
            for sgn in (-1, 1):
                cube((arm, 0.04, thick), (cx + sgn * direction * arm * 0.35, y, z + sgn * h * 0.25), m,
                     rot=(0, sgn * direction * math.pi / 4, 0), bevel=0.0)


def kanji_sign(x, y, z, h, m=NEON_HOT, backing=MAT_INK, w=0.5, seed=3, frame=None):
    """A vertical shop sign with abstract glyph blocks (three or four
    strokes per cell), the way the city's billboards suggest lettering."""
    cube((w, 0.06, h), (x, y + 0.04, z + h / 2), backing, bevel=0.0)
    nxt = _rng(seed)
    cell = w * 1.05
    n = max(int((h - 0.1) / cell), 1)
    cw = w * 0.7
    for i in range(n):
        cz = z + h - 0.05 - cell * (i + 0.5)
        strokes = 3 + int(nxt() * 2)
        for s in range(strokes):
            horiz = nxt() < 0.55
            u, v = (nxt() - 0.5) * cw * 0.7, (nxt() - 0.5) * cw * 0.7
            length = cw * (0.5 + nxt() * 0.5)
            if horiz:
                cube((length, 0.02, 0.04), (x + u * 0.5, y, cz + v), m, bevel=0.0)
            else:
                cube((0.04, 0.02, length), (x + u, y, cz + v * 0.5), m, bevel=0.0)
    if frame is not None:
        neon_tube_frame(x - w / 2, x + w / 2, z, z + h, y - 0.01, frame, r=0.015)


def scanline_screen(x, y, z, w, h, colour=ICE, frame=NEON_ICE, lines=None, body=MAT_NAVY, bars=True, seed=1):
    """A wall screen: dimly lit face striped with dark scanlines, a few
    bright data bars and a glowing tube frame."""
    cube((w, 0.06, h), (x, y, z), body, bevel=0.0)
    cube((w * 0.94, 0.02, h * 0.9), (x, y - 0.035, z), neon(colour, 1.3, tuple(c * 0.12 for c in colour)), bevel=0.0)
    n = lines or max(int(h / 0.14), 2)
    for i in range(n):
        lz = z - h * 0.45 + h * 0.9 * (i + 0.5) / n
        cube((w * 0.94, 0.012, h * 0.9 / n * 0.35), (x, y - 0.05, lz), (SYNTH_NAVY, 0.6, 0.0), bevel=0.0)
    if bars:
        nxt = _rng(seed)
        for i in range(4):
            bw = w * (0.15 + nxt() * 0.35)
            bx = x - w * 0.42 + nxt() * (w * 0.84 - bw) + bw / 2
            bz = z - h * 0.38 + nxt() * h * 0.76
            cube((bw, 0.012, 0.05), (bx, y - 0.055, bz), neon(colour, 3.5), bevel=0.0)
    if frame is not None:
        neon_tube_frame(x - w / 2, x + w / 2, z - h / 2, z + h / 2, y - 0.02, frame, r=0.02)


def laser_fan(x, y, z_ceiling, m=NEON_HOT, n=5, spread=1.3, length=2.4, tilt=0.0, drop=0.05):
    """A cluster of thin neon cones fanning down from a ceiling emitter."""
    cyl(0.14, 0.10, (x, y, z_ceiling - drop), METAL_DARK, verts=8)
    cyl(0.08, 0.04, (x, y, z_ceiling - drop - 0.06), m, verts=8)
    for i in range(n):
        a = -spread / 2 + spread * i / max(n - 1, 1)
        end = (x + math.sin(a) * length, y + tilt * length, z_ceiling - drop - math.cos(a) * length)
        rod((x, y, z_ceiling - drop - 0.08), end, 0.035, m, r2=0.004, verts=5)


def led_column(x, y, z, h, m=NEON_ICE, alt=NEON_HOT, body=MAT_INK, w=0.22, pitch=0.3):
    """A dark vertical bar with a ladder of glowing dots and a lit cap."""
    cube((w, 0.18, h), (x, y + 0.09, z + h / 2), body, bevel=0.0)
    n = int((h - 0.3) / pitch)
    for i in range(n):
        cube((w * 0.5, 0.02, 0.07), (x, y - 0.01, z + 0.2 + i * pitch), alt if i % 4 == 3 else m, bevel=0.0)
    cube((w * 0.8, 0.02, 0.06), (x, y - 0.01, z + h - 0.06), m, bevel=0.0)


def star_field(x0, x1, z0, z1, y, n=24, seed=5, m=NEON_STAR, size=0.05, avoid=()):
    """A scatter of tiny glowing dots (stars on a dark upper wall)."""
    nxt = _rng(seed)
    k = 0
    tries = 0
    while k < n and tries < n * 6:
        tries += 1
        sx = x0 + nxt() * (x1 - x0)
        sz = z0 + nxt() * (z1 - z0)
        if any(rx - 0.1 < sx < rx + rw + 0.1 and rz - 0.1 < sz < rz + rh + 0.1 for (rx, rz, rw, rh) in avoid):
            continue
        s = size * (0.7 + nxt() * 0.8)
        cube((s, 0.02, s), (sx, y, sz), m, bevel=0.0)
        k += 1


def join_under(parent, name):
    """Merge every mesh parented to `parent` into one object (still parented),
    so an animated pivot costs one MeshInstance3D instead of a dozen."""
    objs = [o for o in parent.children if o.type == "MESH"]
    if len(objs) < 2:
        return objs[0] if objs else None
    return join(objs, name)


def hologram(x, y, z, kind="globe", name="spin_holo", m=NEON_ICE, r=0.45, base=True, ring=None):
    """A projector puck with a glowing wireframe shape floating above it on a
    `spin_*` pivot that the game rotates.  kinds: globe, pyramid, cube,
    diamond, coin, heart.  Returns the pivot."""
    ring = ring or m
    if base:
        cyl(0.32 * r / 0.45 + 0.1, 0.08, (x, y, z + 0.04), METAL_DARK, verts=12)
        torus(0.26 * r / 0.45 + 0.08, 0.02, (x, y, z + 0.09), ring, major_segments=16, minor_segments=4)
    cz = z + 0.2 + r
    p = pivot(name, (x, y, cz))
    tr = r * 0.05
    if kind == "globe":
        torus(r, tr, (x, y, cz), m, major_segments=16, minor_segments=4, parent=p)
        torus(r, tr, (x, y, cz), m, rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=4, parent=p)
        torus(r, tr, (x, y, cz), m, rot=(math.pi / 2, 0, math.pi / 2), major_segments=16, minor_segments=4, parent=p)
        torus(r * 0.55, tr, (x, y, cz + r * 0.7), m, major_segments=12, minor_segments=4, parent=p)
        rod((x, y, cz - r * 1.1), (x, y, cz + r * 1.1), tr, m, verts=4, parent=p)
    elif kind == "pyramid":
        base_pts = [(x + sx * r, y + sy * r, cz - r * 0.8) for sx, sy in ((-1, -1), (1, -1), (1, 1), (-1, 1))]
        apex = (x, y, cz + r * 0.9)
        for i in range(4):
            rod(base_pts[i], base_pts[(i + 1) % 4], tr, m, verts=4, parent=p)
            rod(base_pts[i], apex, tr, m, verts=4, parent=p)
        sphere(tr * 2.5, apex, m, segments=6, rings=4, parent=p)
    elif kind == "cube":
        c = [(x + sx * r * 0.75, y + sy * r * 0.75, cz + sz * r * 0.75) for sx in (-1, 1) for sy in (-1, 1) for sz in (-1, 1)]
        for i in range(8):
            for j in range(i + 1, 8):
                if sum(1 for k in range(3) if abs(c[i][k] - c[j][k]) > 1e-6) == 1:
                    rod(c[i], c[j], tr, m, verts=4, parent=p)
    elif kind == "diamond":
        eq = [(x + r, y, cz), (x, y + r, cz), (x - r, y, cz), (x, y - r, cz)]
        top, bot = (x, y, cz + r * 1.3), (x, y, cz - r * 1.3)
        for i in range(4):
            rod(eq[i], eq[(i + 1) % 4], tr, m, verts=4, parent=p)
            rod(eq[i], top, tr, m, verts=4, parent=p)
            rod(eq[i], bot, tr, m, verts=4, parent=p)
    elif kind == "coin":
        cyl(r, r * 0.15, (x, y, cz), m, rot=(math.pi / 2, 0, 0), verts=16, bevel=0.0, parent=p)
        torus(r * 1.05, tr, (x, y, cz), neon(WHITE, 3.0), rot=(math.pi / 2, 0, 0), major_segments=16, minor_segments=4, parent=p)
        cube((r * 0.25, r * 0.2, r * 0.9), (x, y, cz), neon(SUN_YELLOW, 3.0), bevel=0.0, parent=p)
        cube((r * 0.6, r * 0.2, r * 0.22), (x, y, cz + r * 0.3), neon(SUN_YELLOW, 3.0), bevel=0.0, parent=p)
        cube((r * 0.6, r * 0.2, r * 0.22), (x, y, cz - r * 0.3), neon(SUN_YELLOW, 3.0), bevel=0.0, parent=p)
    elif kind == "heart":
        for sx in (-1, 1):
            torus(r * 0.5, tr, (x + sx * r * 0.5, y, cz + r * 0.35), m, rot=(math.pi / 2, 0, 0), major_segments=14, minor_segments=4, parent=p)
            rod((x + sx * r * 0.95, y, cz + r * 0.1), (x, y, cz - r * 1.0), tr, m, verts=4, parent=p)
    join_under(p, name + "_mesh")
    return p


def neon_arch(x, z, y, r, m=NEON_LAV, segments=10, tube_r=0.03, span=math.pi):
    """A glowing arc (half ring by default) on the wall, centre (x, z)."""
    pts = [(x + math.cos(a) * r, y, z + math.sin(a) * r) for a in [span * i / segments for i in range(segments + 1)]]
    for a, b in zip(pts, pts[1:]):
        rod(a, b, tube_r, m, verts=5)


def circuit_trace(x0, x1, y, z, m=NEON_ICE, seed=2, steps=6, r=0.015):
    """A right-angled circuit-board trace wandering along the wall, ending
    in little glowing pads."""
    nxt = _rng(seed)
    px, pz = x0, z
    cube((0.08, 0.02, 0.08), (px, y, pz), m, bevel=0.0)
    for i in range(steps):
        nx = x0 + (x1 - x0) * (i + 1) / steps
        tube((px, y, pz), (nx, y, pz), m, r)
        nz = z + (nxt() - 0.5) * 0.8
        tube((nx, y, pz), (nx, y, nz), m, r)
        px, pz = nx, nz
    cube((0.08, 0.02, 0.08), (px, y, pz), m, bevel=0.0)


def neon_stripe_panel(x, z, y, w, h, colours=(NEON_HOT, NEON_LAV, NEON_ICE), backing=MAT_INK, n=None):
    """A dark panel carrying diagonal racing stripes in three neons."""
    cube((w, 0.05, h), (x, y + 0.03, z), backing, bevel=0.0)
    n = n or max(int(w / 0.45), 3)
    for i in range(n):
        sx = x - w / 2 + w * (i + 0.5) / n
        cube((0.07, 0.02, h * 0.95), (sx, y, z), colours[i % len(colours)], rot=(0, 0.35, 0), bevel=0.0)


def strip_bevels(limit=0.7):
    """Remove bevel modifiers from every mesh whose extent is under `limit`
    metres in all directions: at the game's scale (about 30 px/m on the back
    wall) those bevels are invisible but cost most of a room's faces.  Call
    it just before join_static."""
    n = 0
    for o in all_meshes():
        if not any(md.type == "BEVEL" for md in o.modifiers):
            continue
        dims = [abs(o.dimensions[i]) for i in range(3)]
        if max(dims) < limit:
            for md in [md for md in o.modifiers if md.type == "BEVEL"]:
                o.modifiers.remove(md)
            n += 1
    return n
