# Shared builders for the pushable furniture. Each function builds one prop
# at the origin (bottom centre on the floor, facing -Y) and is called from a
# tiny per-asset script so every model still has its own .glb.
import math

import bpy

from common import *  # noqa: F401,F403

PORCELAIN = ((0.88, 0.92, 0.96), 0.2, 0.0)
PORCELAIN_DIM = ((0.55, 0.62, 0.70), 0.3, 0.0)
CUSHION = ((0.16, 0.05, 0.22), 0.85, 0.0)
FABRIC = ((0.45, 0.08, 0.18), 0.9, 0.0)
CHROME_TRIM = METAL_CHROME


def toilet():
    """A futuristic toilet, ~1.9 m wide, 3 m tall (with the tank tower)."""
    cube((1.0, 0.9, 0.9), (0, 0.3, 0.45), PORCELAIN, bevel=0.12)                    # pedestal
    cyl(0.75, 0.35, (0, -0.15, 1.0), PORCELAIN, scale_hint=None) if False else None
    bowl = sphere(0.78, (0, -0.15, 0.95), PORCELAIN, scale=(1.0, 1.0, 0.45), segments=20, rings=10)
    torus(0.72, 0.09, (0, -0.15, 1.2), PORCELAIN_DIM, major_segments=24)             # seat ring
    cube((0.9, 0.6, 1.6), (0, 0.65, 1.9), PORCELAIN, bevel=0.08)                     # tank tower
    cube((0.6, 0.06, 0.5), (0, 0.33, 2.2), SCREEN_CYAN, bevel=0.01)                  # control screen
    for i in range(3):
        sphere(0.05, (-0.25 + i * 0.25, 0.32, 1.8), [NEON_PINK, NEON_CYAN, NEON_GREEN][i], segments=8, rings=6)
    cube((0.16, 0.4, 0.08), (0.62, 0.3, 1.35), CHROME_TRIM, bevel=0.02)              # flush arm
    cube((0.7, 0.06, 0.08), (0, -0.5, 1.28), NEON_CYAN, bevel=0.0)                   # rim light
    lid = pivot("lid", (0, 0.5, 1.28))
    cube((1.3, 1.1, 0.10), (0, -0.1, 1.33), PORCELAIN, bevel=0.06, parent=lid)


def bathtub():
    """A clawfoot tub with a cyan water surface, 6 m long, 2.4 m tall."""
    tub = sphere(2.8, (0, 0, 1.1), PORCELAIN, scale=(1.0, 0.42, 0.42), segments=24, rings=12)
    cube((5.4, 2.0, 0.8), (0, 0, 0.9), PORCELAIN, bevel=0.15)
    cube((4.9, 1.6, 0.05), (0, 0, 1.55), neon((0.4, 0.9, 1.0), 0.9, (0.1, 0.4, 0.5)), bevel=0.0)  # water
    cube((5.7, 2.2, 0.16), (0, 0, 1.62), PORCELAIN_DIM, bevel=0.06)                   # rim
    for sx in (-1, 1):
        for sy in (-1, 1):
            sphere(0.22, (sx * 2.1, sy * 0.7, 0.2), CHROME_TRIM, scale=(1, 1, 0.8), segments=10, rings=8)  # feet
    cyl(0.07, 0.9, (2.2, 0, 2.0), CHROME_TRIM, verts=10)                              # tap
    rod((2.2, 0, 2.45), (1.7, 0, 2.3), 0.06, CHROME_TRIM)
    for s in (-1, 1):
        cyl(0.09, 0.08, (2.35, s * 0.25, 1.85), [NEON_CYAN, NEON_PINK][s > 0], rot=(math.pi / 2, 0, 0), verts=10)
    for i in range(6):
        sphere(0.08 + (i % 3) * 0.03, (-1.5 + i * 0.6, -0.5 + (i % 2) * 0.9, 1.6), (WHITE, 0.1, 0.0), segments=6, rings=4)  # foam


def chair():
    """A gamer throne: tall back, neon piping, on a chrome star base. 2.3 x 3 m."""
    for i in range(5):
        a = i / 5.0 * math.tau
        rod((0, 0, 0.12), (math.cos(a) * 0.9, math.sin(a) * 0.9, 0.05), 0.06, CHROME_TRIM)
        sphere(0.1, (math.cos(a) * 0.9, math.sin(a) * 0.9, 0.08), PLASTIC_BLACK, segments=8, rings=6)
    cyl(0.12, 0.6, (0, 0, 0.4), CHROME_TRIM, verts=10)
    cube((1.7, 1.5, 0.35), (0, 0, 0.9), CUSHION, bevel=0.12)                          # seat
    cube((1.7, 0.45, 2.0), (0, 0.6, 1.95), CUSHION, bevel=0.14)                       # back
    cube((1.2, 0.2, 0.5), (0, 0.42, 2.55), PLASTIC_BLACK, bevel=0.08)                 # headrest
    for s in (-1, 1):
        cube((0.3, 1.1, 0.5), (s * 0.85, -0.05, 1.2), PLASTIC_BLACK, bevel=0.1)       # armrests
        rod((s * 0.85, 0.85, 1.05), (s * 0.85, 0.85, 2.85), 0.03, NEON_MAGENTA)       # piping
        rod((s * 0.85, -0.7, 0.75), (s * 0.85, 0.7, 0.75), 0.03, NEON_MAGENTA)
    cube((0.6, 0.05, 0.6), (0, 0.36, 1.9), NEON_CYAN, bevel=0.02)                     # back emblem


def table(radius=0.95):
    """A round pedestal table with a candle-lit dinner on it, 2 m across and
    2 m tall (2.7 m with the candle). The game seats two chairs beside it
    (see table_with_chairs.tscn), each its own rigid body."""
    cyl(0.45, 0.15, (0, 0, 0.08), METAL_DARK, verts=16)
    cyl(0.14, 1.9, (0, 0, 1.0), METAL_DARK, verts=10)
    cyl(radius, 0.12, (0, 0, 2.0), ((0.05, 0.05, 0.08), 0.15, 0.3), verts=28)
    torus(radius, 0.04, (0, 0, 2.0), NEON_PINK, major_segments=28)
    cyl(0.2, 0.02, (0.35, -0.3, 2.07), (WHITE, 0.4, 0.0), verts=14)                  # plate
    cyl(0.2, 0.02, (-0.35, 0.3, 2.07), (WHITE, 0.4, 0.0), verts=14)
    cyl(0.05, 0.5, (0.0, 0.0, 2.3), (WHITE, 0.6, 0.0), verts=8)                       # candle
    sphere(0.05, (0.0, 0.0, 2.6), NEON_ORANGE, scale=(0.7, 0.7, 1.4), segments=8, rings=6)
    cyl(0.07, 0.45, (-0.5, -0.2, 2.28), ((0.1, 0.3, 0.15), 0.1, 0.0), verts=8)       # bottle
    cyl(0.03, 0.2, (-0.5, -0.2, 2.6), ((0.1, 0.3, 0.15), 0.1, 0.0), verts=8)


def tv():
    """A boxy retro TV on a stand, 2 m wide, 2.2 m tall."""
    cube((1.6, 0.9, 0.5), (0, 0, 0.25), METAL_DARK, bevel=0.03)                       # stand
    cube((1.9, 1.3, 1.5), (0, 0.15, 1.3), ((0.35, 0.22, 0.12), 0.7, 0.0), bevel=0.06)
    cube((1.4, 0.1, 1.1), (0, -0.5, 1.35), SCREEN_CYAN, bevel=0.03)
    cube((1.3, 0.04, 0.12), (0, -0.56, 1.55), neon((1.0, 0.4, 0.7), 2.5), bevel=0.0)  # a band of colour bars
    cube((1.3, 0.04, 0.12), (0, -0.56, 1.25), neon((0.3, 1.0, 0.5), 2.5), bevel=0.0)
    for i in range(2):
        cyl(0.07, 0.06, (0.7, -0.52, 0.9 + i * 0.25), CHROME_TRIM, rot=(math.pi / 2, 0, 0), verts=10)
    rod((0.4, 0.2, 2.05), (0.9, 0.2, 2.9), 0.025, CHROME_TRIM)                        # antennas
    rod((-0.4, 0.2, 2.05), (-0.9, 0.2, 2.9), 0.025, CHROME_TRIM)


def champagne():
    """A champagne bottle in a bucket of ice, 0.6 m wide, 1 m tall."""
    cyl(0.28, 0.45, (0, 0, 0.22), CHROME_TRIM, r2=0.22, verts=14)
    for i in range(7):
        a = i * 0.9
        sphere(0.06, (math.cos(a) * 0.15, math.sin(a) * 0.15, 0.47), (WHITE, 0.05, 0.0), segments=6, rings=4)
    cyl(0.11, 0.55, (0.05, 0, 0.6), ((0.08, 0.25, 0.12), 0.1, 0.0), verts=10)
    cyl(0.11, 0.1, (0.05, 0, 0.9), ((0.08, 0.25, 0.12), 0.1, 0.0), r2=0.04, verts=10)
    cyl(0.04, 0.16, (0.05, 0, 1.0), METAL_GOLD, verts=8)
    cube((0.16, 0.02, 0.12), (0.05, -0.11, 0.65), METAL_GOLD, bevel=0.0)


def cake():
    """A three-tier birthday cake with candles, 0.9 m wide, 0.9 m tall."""
    cyl(0.45, 0.04, (0, 0, 0.02), CHROME_TRIM, verts=20)
    for i, (r, h, m) in enumerate([(0.42, 0.28, ((0.95, 0.65, 0.8), 0.6, 0.0)), (0.32, 0.24, ((0.6, 0.35, 0.2), 0.6, 0.0)), (0.22, 0.2, ((0.95, 0.65, 0.8), 0.6, 0.0))]):
        z = 0.04 + sum(hh for _, hh, _ in [(0.42, 0.28, 0), (0.32, 0.24, 0), (0.22, 0.2, 0)][:i])
        cyl(r, h, (0, 0, z + h / 2), m, verts=16)
        torus(r, 0.03, (0, 0, z + h), (WHITE, 0.5, 0.0), major_segments=16)
    for i in range(5):
        a = i / 5.0 * math.tau
        cyl(0.02, 0.18, (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.85), [NEON_PINK, NEON_CYAN, NEON_YELLOW, NEON_GREEN, NEON_ORANGE][i], verts=6)
        sphere(0.03, (math.cos(a) * 0.12, math.sin(a) * 0.12, 0.96), NEON_ORANGE, segments=6, rings=4)


def bench_press():
    """A bench with a loaded barbell on its rack, 4 m wide, 3.3 m tall."""
    cube((0.7, 2.6, 0.25), (0, 0, 1.0), FABRIC, bevel=0.06)                            # bench pad
    cube((0.5, 2.2, 0.12), (0, 0, 0.82), METAL_DARK, bevel=0.02)
    for sy in (-1, 1):
        cube((0.5, 0.08, 0.76), (0, sy * 0.9, 0.38), METAL_DARK, bevel=0.01)
        cube((0.7, 0.2, 0.06), (0, sy * 0.9, 0.03), METAL_DARK, bevel=0.01)
    for sx in (-1, 1):
        cube((0.1, 0.1, 2.9), (sx * 0.9, 0.9, 1.45), METAL_DARK, bevel=0.01)          # uprights
        cube((0.16, 0.3, 0.12), (sx * 0.9, 0.75, 2.75), METAL_DARK, bevel=0.01)       # hooks
        rod((sx * 0.9, 0.9, 0.3), (sx * 0.9, 0.9, 1.7), 0.03, NEON_GREEN)
    rod((-2.0, 0.85, 2.85), (2.0, 0.85, 2.85), 0.05, CHROME_TRIM)                     # barbell
    for sx in (-1, 1):
        for i, r in enumerate((0.45, 0.38, 0.3)):
            cyl(r, 0.08, (sx * (1.25 + i * 0.12), 0.85, 2.85), [((0.5, 0.05, 0.1), 0.6, 0.3), ((0.05, 0.2, 0.55), 0.6, 0.3), ((0.9, 0.7, 0.1), 0.6, 0.3)][i], rot=(0, math.pi / 2, 0), verts=16)
            torus(r * 0.55, 0.02, (sx * (1.25 + i * 0.12) - sx * 0.05, 0.85, 2.85), NEON_CYAN, rot=(0, math.pi / 2, 0))


def bed(variant):
    """Three beds: 0 = single hotel bed (6 x 1.6 m), 1 = double with a tall
    headboard (6 x 2.9 m), 2 = royal four-poster (6 x 2.8 m)."""
    if variant == 0:
        cube((5.8, 2.2, 0.5), (0, 0, 0.45), METAL_DARK, bevel=0.05)
        cube((5.7, 2.1, 0.5), (0, 0, 0.95), ((0.3, 0.45, 0.6), 0.9, 0.0), bevel=0.12)
        cube((3.6, 2.0, 0.12), (-0.9, 0, 1.25), (WHITE, 0.9, 0.0), bevel=0.05)
        cube((1.2, 1.4, 0.35), (2.2, 0, 1.35), (WHITE, 0.9, 0.0), bevel=0.12)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl(0.08, 0.2, (sx * 2.7, sy * 0.95, 0.1), CHROME_TRIM, verts=8)
        rod((-2.9, -1.1, 1.0), (2.9, -1.1, 1.0), 0.03, NEON_CYAN)
    elif variant == 1:
        cube((5.8, 2.4, 0.6), (0, 0, 0.5), (WOOD, 0.7, 0.0), bevel=0.05)
        cube((5.7, 2.3, 0.6), (0, 0, 1.1), ((0.5, 0.1, 0.25), 0.9, 0.0), bevel=0.15)
        cube((3.8, 2.2, 0.14), (-0.8, 0, 1.45), ((0.95, 0.9, 0.85), 0.9, 0.0), bevel=0.05)
        for i in range(2):
            cube((1.1, 0.9, 0.4), (2.2, -0.55 + i * 1.1, 1.55), (WHITE, 0.9, 0.0), bevel=0.14)
        cube((0.3, 2.6, 2.9), (2.85, 0, 1.45), (WOOD, 0.7, 0.0), bevel=0.06)          # headboard
        for i in range(4):
            cube((0.05, 0.4, 2.2), (2.68, -0.9 + i * 0.6, 1.6), NEON_PINK, bevel=0.0)
    else:
        cube((5.8, 2.6, 0.7), (0, 0, 0.55), METAL_GOLD, bevel=0.06)
        cube((5.6, 2.4, 0.5), (0, 0, 1.15), ((0.45, 0.05, 0.15), 0.85, 0.0), bevel=0.15)
        cube((3.6, 2.2, 0.12), (-0.8, 0, 1.46), ((0.35, 0.04, 0.12), 0.85, 0.0), bevel=0.04)
        for i in range(3):
            cube((0.9, 0.7, 0.4), (2.0, -0.8 + i * 0.8, 1.6), METAL_GOLD if i == 1 else ((0.9, 0.8, 0.6), 0.9, 0.0), bevel=0.12)
        for sx in (-1, 1):
            for sy in (-1, 1):
                cyl(0.08, 2.7, (sx * 2.75, sy * 1.2, 1.4), METAL_GOLD, verts=10)
                sphere(0.14, (sx * 2.75, sy * 1.2, 2.8), METAL_GOLD, segments=8, rings=6)
        for sy in (-1, 1):
            cube((5.6, 0.06, 0.06), (0, sy * 1.2, 2.75), METAL_GOLD, bevel=0.0)
        cube((5.5, 2.5, 0.06), (0, 0, 2.78), ((0.45, 0.05, 0.15), 0.85, 0.0), bevel=0.0)  # canopy
        cube((0.25, 2.5, 2.4), (2.85, 0, 1.6), METAL_GOLD, bevel=0.04)


def painting_frame():
    """An ornate frame; the game puts a painting texture on the "canvas" quad.
    3.75 m square, centred, canvas facing -Y."""
    S = 3.75
    cube((S, 0.25, S), (0, 0, 0), METAL_GOLD, bevel=0.06)
    cube((S - 0.55, 0.12, S - 0.55), (0, -0.09, 0), ((0.3, 0.2, 0.06), 0.6, 0.6), bevel=0.02)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sphere(0.16, (sx * (S / 2 - 0.16), -0.15, sz * (S / 2 - 0.16)), METAL_GOLD, segments=8, rings=6)
    for s in (-1, 1):
        cube((0.5, 0.06, 0.12), (0, -0.15, s * (S / 2 - 0.14)), METAL_GOLD, bevel=0.02)
        cube((0.12, 0.06, 0.5), (s * (S / 2 - 0.14), -0.15, 0), METAL_GOLD, bevel=0.02)
    canvas = plane((S - 0.8, S - 0.8), (0, -0.16, 0), (WHITE, 0.8, 0.0), rot=(math.pi / 2, 0, 0), name="canvas")
    return canvas


def statue_parts():
    """The chrome statue in three pieces: 'base' (plinth), 'body' and
    'head', each returned as a separate object list so the game can make
    them separate bodies. Total 4 m wide, 8 m tall."""
    parts = {}
    base = [
        cube((3.6, 2.2, 0.6), (0, 0, 0.3), METAL_DARK, bevel=0.06),
        cube((2.8, 1.8, 1.2), (0, 0, 1.2), ((0.15, 0.15, 0.2), 0.4, 0.5), bevel=0.06),
        cube((3.0, 2.0, 0.15), (0, 0, 1.85), METAL_CHROME, bevel=0.03),
        cube((2.4, 0.05, 0.12), (0, -0.92, 1.0), NEON_CYAN, bevel=0.0),
    ]
    parts["base"] = base
    CHROME_BODY = ((0.55, 0.75, 0.8), 0.15, 1.0)
    GLOW = neon((0.3, 0.95, 1.0), 3.0)
    Z = 1.92
    body = []
    for s in (-1, 1):
        body.append(cyl(0.28, 1.9, (s * 0.35, 0, Z + 0.95), CHROME_BODY, verts=12))
        body.append(cube((0.6, 0.9, 0.3), (s * 0.35, -0.15, Z + 0.15), CHROME_BODY, bevel=0.06))
    body.append(cyl(0.9, 0.7, (0, 0, Z + 2.2), CHROME_BODY, r2=0.75, verts=14))
    body.append(sphere(1.0, (0, 0, Z + 3.1), CHROME_BODY, scale=(1.0, 0.7, 1.0), segments=16, rings=10))
    body.append(cube((0.12, 0.06, 2.4), (0, -0.95, Z + 2.9), GLOW, bevel=0.0))
    for s in (-1, 1):
        body.append(cube((0.5, 0.06, 0.06), (s * 0.45, -0.85, Z + 3.3), GLOW, bevel=0.0))
        body.append(rod((s * 1.0, 0, Z + 3.7), (s * 1.35, -0.3, Z + 2.2), 0.2, CHROME_BODY))
        body.append(sphere(0.26, (s * 1.35, -0.3, Z + 2.05), CHROME_BODY, segments=10, rings=8))
        body.append(sphere(0.3, (s * 1.0, 0, Z + 3.8), CHROME_BODY, segments=10, rings=8))
    body.append(cyl(0.3, 0.4, (0, 0, Z + 4.05), CHROME_BODY, verts=10))
    parts["body"] = body
    HZ = Z + 4.25
    head = [
        sphere(0.7, (0, 0, HZ + 0.7), CHROME_BODY, scale=(0.9, 0.95, 1.05), segments=16, rings=12),
        cube((0.9, 0.1, 0.16), (0, -0.62, HZ + 0.78), GLOW, bevel=0.0),
        cyl(0.25, 0.3, (0, 0, HZ + 1.5), CHROME_BODY, r2=0.05, verts=10),
    ]
    parts["head"] = head
    return parts


def desktop_parts():
    """The workstation in three pieces: 'desk' (with a tower on the side),
    'monitor' and 'tower' (a separate hard drive block). 4 x 5 m."""
    parts = {}
    DESK_M = ((0.14, 0.16, 0.22), 0.5, 0.4)
    desk = [
        cube((3.9, 1.8, 0.16), (0, 0, 1.9), DESK_M, bevel=0.04),
        cube((3.7, 0.05, 0.08), (0, -0.92, 1.9), NEON_GREEN, bevel=0.0),
        cube((1.0, 1.6, 1.8), (-1.4, 0, 0.9), DESK_M, bevel=0.04),
        cube((0.3, 1.6, 1.8), (1.75, 0, 0.9), DESK_M, bevel=0.04),
        cube((0.8, 0.06, 0.25), (-1.4, -0.82, 1.3), (SLATE, 0.5, 0.5), bevel=0.01),
        cube((0.8, 0.06, 0.25), (-1.4, -0.82, 0.8), (SLATE, 0.5, 0.5), bevel=0.01),
        sphere(0.06, (-1.15, -0.86, 1.3), NEON_PINK, segments=6, rings=4),
        sphere(0.06, (-1.15, -0.86, 0.8), NEON_PINK, segments=6, rings=4),
        cube((1.3, 0.5, 0.06), (0.4, -0.5, 2.01), PLASTIC_BLACK, bevel=0.01),        # keyboard
        cube((1.2, 0.35, 0.03), (0.4, -0.5, 2.05), neon((0.6, 0.2, 1.0), 1.5, (0.15, 0.05, 0.25)), bevel=0.0),
        sphere(0.12, (1.35, -0.45, 2.05), PLASTIC_BLACK, scale=(1, 1.4, 0.7), segments=8, rings=6),
        cyl(0.1, 0.35, (-0.9, -0.3, 2.15), ((0.9, 0.1, 0.2), 0.5, 0.0), verts=8),    # mug
    ]
    parts["desk"] = desk
    monitor = [
        cube((2.3, 0.14, 1.7), (0, 0.35, 0.95), PLASTIC_BLACK, bevel=0.04),
        cube((2.1, 0.06, 1.5), (0, 0.27, 0.95), SCREEN_CYAN, bevel=0.0),
        sphere(0.35, (0, 0.24, 0.95), neon((0.3, 0.6, 1.0), 3.0, (0.1, 0.2, 0.4)), scale=(1.6, 0.2, 1.0), segments=12, rings=8),
        cube((1.6, 0.03, 0.08), (0, 0.23, 1.5), neon((1.0, 0.4, 0.8), 2.5), bevel=0.0),
        cube((0.5, 0.3, 0.1), (0, 0.35, 0.05), PLASTIC_BLACK, bevel=0.02),
        cube((0.16, 0.1, 0.4), (0, 0.4, 0.25), PLASTIC_BLACK, bevel=0.02),
        cube((2.3, 0.04, 0.05), (0, 0.28, 1.83), NEON_CYAN, bevel=0.0),
    ]
    parts["monitor"] = monitor
    tower = [
        cube((0.9, 1.2, 2.1), (0, 0, 1.05), ((0.12, 0.12, 0.16), 0.4, 0.5), bevel=0.05),
        cube((0.7, 0.05, 1.7), (0, -0.62, 1.05), ((0.05, 0.05, 0.08), 0.1, 0.0), bevel=0.0),   # glass side
        torus(0.22, 0.03, (0, -0.65, 1.5), NEON_GREEN, rot=(math.pi / 2, 0, 0)),
        torus(0.22, 0.03, (0, -0.65, 0.7), NEON_MAGENTA, rot=(math.pi / 2, 0, 0)),
        cube((0.5, 0.03, 0.06), (0, -0.66, 1.1), NEON_CYAN, bevel=0.0),
        cube((0.3, 0.05, 0.2), (0.15, -0.63, 1.95), NEON_PINK, bevel=0.0),
    ]
    parts["tower"] = tower
    return parts
