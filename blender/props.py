# Reusable set-dressing pieces for the room backdrops: monitors, shelves,
# posters, neon signs, pipes, lamps, plants, sofas... Every helper builds at
# a given floor position (x, y) with z = 0 on the floor, facing -Y, and
# returns nothing: the theme script joins everything at the end.
import math

import bpy

from common import *  # noqa: F401,F403

CREST_RED = (0.45, 0.04, 0.05)
WOOD_LIGHT = (0.45, 0.28, 0.12)
TERRACOTTA_M = ((0.36, 0.10, 0.04), 0.8, 0.0)
LEAF = ((0.05, 0.35, 0.12), 0.7, 0.0)

# 5-row x 3-column bitmap font for block-letter neon signs.
_FONT = {
    "A": ["010", "101", "111", "101", "101"],
    "B": ["110", "101", "110", "101", "110"],
    "C": ["011", "100", "100", "100", "011"],
    "D": ["110", "101", "101", "101", "110"],
    "E": ["111", "100", "110", "100", "111"],
    "F": ["111", "100", "110", "100", "100"],
    "J": ["011", "001", "001", "101", "010"],
    "Q": ["010", "101", "101", "011", "001"],
    "Z": ["111", "001", "010", "100", "111"],
    "3": ["111", "001", "011", "001", "111"],
    "5": ["111", "100", "110", "001", "110"],
    "6": ["011", "100", "111", "101", "111"],
    "8": ["111", "101", "111", "101", "111"],
    "9": ["111", "101", "111", "001", "110"],
    "G": ["011", "100", "101", "101", "011"],
    "H": ["101", "101", "111", "101", "101"],
    "I": ["111", "010", "010", "010", "111"],
    "K": ["101", "101", "110", "101", "101"],
    "L": ["100", "100", "100", "100", "111"],
    "M": ["101", "111", "111", "101", "101"],
    "N": ["110", "101", "101", "101", "101"],
    "O": ["010", "101", "101", "101", "010"],
    "P": ["110", "101", "110", "100", "100"],
    "R": ["110", "101", "110", "101", "101"],
    "S": ["011", "100", "010", "001", "110"],
    "T": ["111", "010", "010", "010", "010"],
    "U": ["101", "101", "101", "101", "111"],
    "V": ["101", "101", "101", "101", "010"],
    "W": ["101", "101", "111", "111", "101"],
    "X": ["101", "101", "010", "101", "101"],
    "Y": ["101", "101", "010", "010", "010"],
    "!": ["010", "010", "010", "000", "010"],
    "$": ["011", "110", "010", "011", "110"],
    "0": ["111", "101", "101", "101", "111"],
    "1": ["010", "110", "010", "010", "111"],
    "2": ["110", "001", "010", "100", "111"],
    "4": ["101", "101", "111", "001", "001"],
    "7": ["111", "001", "010", "010", "010"],
    " ": ["000", "000", "000", "000", "000"],
}


def neon_sign(text, x, y, z, m, cell=0.16, gap=0.6, backing=None):
    """Block letters glowing on the wall; `cell` is the size of one dot.
    Returns the total width."""
    cx = x
    for ch in text.upper():
        rows = _FONT.get(ch, _FONT[" "])
        for r, row in enumerate(rows):
            for c, bit in enumerate(row):
                if bit == "1":
                    cube((cell * 0.9, 0.06, cell * 0.9), (cx + c * cell, y, z + (4 - r) * cell), anim(m, "marquee"), bevel=0.0)
        cx += cell * 3 + cell * gap
    width = cx - x - cell * gap
    if backing is not None:
        cube((width + cell * 1.5, 0.05, cell * 6.2), (x + width / 2 - cell / 2, y + 0.06, z + cell * 2), backing, bevel=0.02)
    return width


def monitor(x, y, z, w=0.6, h=0.42, screen=SCREEN_CYAN, tilt=0.0, stand=True):
    """A flat screen on a stand, its face towards -Y."""
    cube((w, 0.05, h), (x, y, z + h / 2 + (0.12 if stand else 0.0)), PLASTIC_DARK, rot=(tilt, 0, 0), bevel=0.01)
    cube((w * 0.92, 0.02, h * 0.88), (x, y - 0.03, z + h / 2 + (0.12 if stand else 0.0)), anim(screen, "screen"), rot=(tilt, 0, 0), bevel=0.0)
    if stand:
        cyl(0.03, 0.12, (x, y, z + 0.06), METAL_DARK, verts=8)
        cube((w * 0.4, 0.2, 0.02), (x, y, z + 0.01), METAL_DARK, bevel=0.005)


def crt(x, y, z, w=0.5, screen=SCREEN_CYAN):
    """A boxy old monitor."""
    cube((w, w * 0.9, w * 0.8), (x, y + w * 0.45, z + w * 0.4), PLASTIC_DARK, bevel=0.03)
    cube((w * 0.78, 0.03, w * 0.58), (x, y, z + w * 0.42), screen, bevel=0.0)


def shelf(x, y, z, w=2.0, d=0.35, m=METAL_DARK):
    cube((w, d, 0.05), (x, y + d / 2, z), m, bevel=0.01)
    for s in (-1, 1):
        cube((0.04, 0.05, 0.25), (x + s * (w / 2 - 0.05), y + d - 0.04, z - 0.14), m, bevel=0.005)


def poster(x, y, z, w=0.7, h=1.0, frame=PLASTIC_DARK, face=NEON_MAGENTA):
    cube((w, 0.04, h), (x, y, z), frame, bevel=0.01)
    cube((w * 0.9, 0.02, h * 0.9), (x, y - 0.02, z), face, bevel=0.0)


def framed_picture(x, y, z, w=1.2, h=0.9, frame=METAL_GOLD, face=(PLUM, 0.7, 0.0)):
    cube((w, 0.08, h), (x, y, z), frame, bevel=0.02)
    cube((w * 0.86, 0.03, h * 0.82), (x, y - 0.04, z), face, bevel=0.0)


def window(x, y, z, w=2.4, h=2.0, frame=METAL_DARK, sky=(NAVY, 0.9, 0.0), lights=NEON_CYAN, seed=0):
    """A window onto the neon city: dark glass with a scatter of lit windows."""
    cube((w, 0.06, h), (x, y, z), frame, bevel=0.02)
    cube((w - 0.16, 0.02, h - 0.16), (x, y - 0.03, z), sky, bevel=0.0)
    cube((0.05, 0.05, h - 0.16), (x, y - 0.03, z), frame, bevel=0.0)
    cube((w - 0.16, 0.05, 0.05), (x, y - 0.03, z), frame, bevel=0.0)
    rng = seed
    for i in range(int(w * h * 9)):
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        lx = x - w / 2 + 0.12 + (rng % 1000) / 1000.0 * (w - 0.24)
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        lz = z - h / 2 + 0.1 + (rng % 1000) / 1000.0 * (h - 0.6)
        rng = (rng * 1103515245 + 12345) & 0x7FFFFFFF
        c = lights if rng % 3 else NEON_PINK
        cube((0.05, 0.02, 0.04), (lx, y - 0.05, lz), c, bevel=0.0)
    # Skyline silhouettes at the bottom.
    for i in range(6):
        bx = x - w / 2 + 0.25 + i * (w - 0.4) / 5.0
        bh = 0.25 + ((i * 7) % 4) * 0.12
        cube((0.22, 0.02, bh), (bx, y - 0.045, z - h / 2 + 0.08 + bh / 2), (DARK, 0.9, 0.0), bevel=0.0)


def pipe_run(x0, x1, y, z, r=0.06, m=METAL_STEEL, drops=()):
    rod((x0, y, z), (x1, y, z), r, m, verts=10)
    for dx in drops:
        rod((dx, y, z), (dx, y, z - 0.6), r * 0.8, m, verts=10)
        sphere(r * 1.3, (dx, y, z), m, segments=8, rings=6)


def hanging_lamp(x, y, z_ceiling, drop=0.6, m=NEON_YELLOW, shade=METAL_DARK):
    rod((x, y, z_ceiling), (x, y, z_ceiling - drop), 0.015, PLASTIC_BLACK, verts=6)
    cyl(0.22, 0.16, (x, y, z_ceiling - drop - 0.08), shade, r2=0.12, verts=14)
    sphere(0.08, (x, y, z_ceiling - drop - 0.18), m, segments=10, rings=8)


def light_bar(x, y, z, length=2.0, m=NEON_WHITE, rot=(0, 0, 0)):
    cube((length, 0.10, 0.06), (x, y, z), m, rot=rot, bevel=0.01)
    cube((length + 0.1, 0.14, 0.04), (x, y, z + 0.04), METAL_DARK, rot=rot, bevel=0.005)


def plant(x, y, z, size=1.0):
    cyl(0.18 * size, 0.28 * size, (x, y, z + 0.14 * size), TERRACOTTA_M, r2=0.14 * size, verts=12)
    for i in range(6):
        a = i / 6.0 * math.tau
        leaf = sphere(0.18 * size, (x + math.cos(a) * 0.12 * size, y + math.sin(a) * 0.12 * size, z + 0.45 * size), LEAF, scale=(0.5, 1.4, 0.9), segments=8, rings=6)
        leaf.rotation_euler = (0.5, 0, a)
    sphere(0.16 * size, (x, y, z + 0.55 * size), LEAF, segments=8, rings=6)


def box(x, y, z, w=0.6, d=0.5, h=0.5, m=(WOOD, 0.85, 0.0), rot=0.0):
    cube((w, d, h), (x, y, z + h / 2), m, rot=(0, 0, rot), bevel=0.02)


def sofa(x, y, z, w=2.2, m=(PLUM, 0.8, 0.0), trim=METAL_GOLD):
    d = 0.9
    cube((w, d, 0.42), (x, y + d / 2, z + 0.21), m, bevel=0.06)             # seat
    cube((w, 0.25, 0.85), (x, y + d - 0.125, z + 0.42), m, bevel=0.06)      # back
    for s in (-1, 1):
        cube((0.22, d, 0.62), (x + s * (w / 2 - 0.11), y + d / 2, z + 0.31), m, bevel=0.06)
    for i in range(3):
        cube((w / 3.3, 0.18, 0.40), (x - w / 3 + i * w / 3, y + 0.32, z + 0.60), trim if False else m, bevel=0.06)
    for s in (-1, 1):
        cyl(0.03, 0.10, (x + s * (w / 2 - 0.2), y + 0.2, z + 0.05), trim, verts=8)


def locker(x, y, z, w=0.6, h=1.9, m=(SLATE, 0.5, 0.6), accent=NEON_CYAN):
    cube((w, 0.5, h), (x, y + 0.25, z + h / 2), m, bevel=0.02)
    cube((w * 0.5, 0.02, 0.06), (x, y - 0.01, z + h * 0.7), accent, bevel=0.0)
    cube((w * 0.5, 0.02, 0.06), (x, y - 0.01, z + h * 0.6), accent, bevel=0.0)
    cube((0.04, 0.04, 0.16), (x + w * 0.3, y - 0.02, z + h * 0.5), METAL_CHROME, bevel=0.005)


def column(x, y, z, h=6.0, r=0.28, m=(BONE, 0.6, 0.0), cap=METAL_GOLD):
    cyl(r, h, (x, y, z + h / 2), m, verts=16)
    cyl(r * 1.3, 0.12, (x, y, z + 0.06), cap, verts=16)
    cyl(r * 1.3, 0.12, (x, y, z + h - 0.06), cap, verts=16)


def cable_drape(x0, x1, y, z, sag=0.5, m=PLASTIC_BLACK, segments=6, r=0.025):
    pts = []
    for i in range(segments + 1):
        t = i / segments
        pts.append((x0 + (x1 - x0) * t, y, z - sag * math.sin(t * math.pi)))
    for a, b in zip(pts, pts[1:]):
        rod(a, b, r, m, verts=6)


def led_strip(x0, x1, y, z, m=NEON_PINK, r=0.02):
    rod((x0, y, z), (x1, y, z), r, m, verts=6)


def server_rack(x, y, z, w=0.7, h=2.2, units=9):
    cube((w, 0.8, h), (x, y + 0.4, z + h / 2), (GUNMETAL, 0.5, 0.7), bevel=0.02)
    for i in range(units):
        uz = z + 0.15 + i * (h - 0.3) / units
        cube((w - 0.1, 0.04, 0.16), (x, y - 0.02, uz), (SLATE, 0.5, 0.5), bevel=0.005)
        for j in range(4):
            c = NEON_GREEN if (i + j) % 3 else NEON_ORANGE
            cube((0.03, 0.02, 0.03), (x - w / 2 + 0.1 + j * 0.07, y - 0.05, uz + 0.03), c, bevel=0.0)


def desk(x, y, z, w=1.8, d=0.8, m=(SLATE, 0.6, 0.3), legs=METAL_DARK):
    cube((w, d, 0.06), (x, y + d / 2, z + 0.75), m, bevel=0.01)
    for sx in (-1, 1):
        cube((0.06, d - 0.1, 0.72), (x + sx * (w / 2 - 0.05), y + d / 2, z + 0.36), legs, bevel=0.005)


def bed_flat(x, y, z, w=2.0, d=1.4, m=(PLUM, 0.85, 0.0), sheet=(WHITE, 0.9, 0.0), frame=METAL_DARK):
    cube((w, d, 0.30), (x, y + d / 2, z + 0.25), frame, bevel=0.03)
    cube((w * 0.98, d * 0.98, 0.22), (x, y + d / 2, z + 0.50), m, bevel=0.05)
    cube((w * 0.6, d * 0.9, 0.06), (x - w * 0.18, y + d / 2, z + 0.64), sheet, bevel=0.02)
    cube((0.45, d * 0.35, 0.14), (x + w * 0.35, y + d * 0.5, z + 0.68), sheet, bevel=0.05)
    cube((w, 0.12, 1.1), (x, y + d + 0.06, z + 0.55), frame, bevel=0.03)


def rug(x, y, z, w=3.0, d=1.6, m=(CREST_RED, 0.9, 0.0), border=METAL_GOLD):
    cube((w, d, 0.02), (x, y, z + 0.01), m, bevel=0.0)
    cube((w + 0.12, d + 0.12, 0.015), (x, y, z + 0.005), border, bevel=0.0)


def wall_clock(x, y, z, r=0.3):
    cyl(r, 0.06, (x, y, z), METAL_STEEL, rot=(math.pi / 2, 0, 0), verts=20)
    cyl(r * 0.88, 0.02, (x, y - 0.03, z), (WHITE, 0.6, 0.0), rot=(math.pi / 2, 0, 0), verts=20)
    cube((0.03, 0.02, r * 0.6), (x, y - 0.045, z + r * 0.25), DARK, bevel=0.0)
    cube((r * 0.5, 0.02, 0.03), (x + r * 0.2, y - 0.045, z), DARK, bevel=0.0)


def vending_machine(x, y, z, glow=NEON_CYAN):
    cube((1.0, 0.8, 2.0), (x, y + 0.4, z + 1.0), (SLATE, 0.5, 0.4), bevel=0.03)
    cube((0.55, 0.03, 1.2), (x - 0.15, y - 0.01, z + 1.2), (NAVY, 0.3, 0.0), bevel=0.01)
    for r in range(4):
        for c in range(3):
            cube((0.12, 0.05, 0.16), (x - 0.35 + c * 0.2, y - 0.03, z + 0.75 + r * 0.28), [NEON_PINK, NEON_CYAN, NEON_YELLOW][(r + c) % 3], bevel=0.01)
    cube((0.16, 0.03, 0.4), (x + 0.33, y - 0.01, z + 1.3), glow, bevel=0.01)
    cube((0.5, 0.03, 0.15), (x - 0.15, y - 0.01, z + 0.3), DARK, bevel=0.01)


def bookshelf(x, y, z, w=1.6, h=2.4, m=(WOOD, 0.8, 0.0)):
    cube((w, 0.4, h), (x, y + 0.2, z + h / 2), m, bevel=0.01)
    rows = 4
    for r in range(rows):
        rz = z + 0.15 + r * (h - 0.3) / rows
        cube((w - 0.1, 0.36, 0.03), (x, y + 0.2, rz), (WOOD_LIGHT, 0.8, 0.0), bevel=0.0)
        bx = x - w / 2 + 0.12
        k = 0
        while bx < x + w / 2 - 0.12:
            bw = 0.06 + ((r * 5 + k) % 4) * 0.02
            bh = 0.28 + ((r * 3 + k) % 3) * 0.05
            c = [(0.5, 0.08, 0.1), (0.08, 0.2, 0.5), (0.1, 0.4, 0.15), (0.6, 0.45, 0.1), (0.35, 0.1, 0.5)][(r + k) % 5]
            cube((bw, 0.28, bh), (bx, y + 0.22, rz + bh / 2 + 0.02), (c, 0.85, 0.0), bevel=0.0)
            bx += bw + 0.012
            k += 1


def chandelier(x, y, z_ceiling, drop=0.9):
    rod((x, y, z_ceiling), (x, y, z_ceiling - drop), 0.02, METAL_GOLD, verts=8)
    torus(0.6, 0.03, (x, y, z_ceiling - drop), METAL_GOLD, major_segments=24)
    for i in range(8):
        a = i / 8.0 * math.tau
        px, py = x + math.cos(a) * 0.6, y + math.sin(a) * 0.6
        cyl(0.03, 0.18, (px, py, z_ceiling - drop + 0.1), (BONE, 0.5, 0.0), verts=8)
        sphere(0.05, (px, py, z_ceiling - drop + 0.22), NEON_YELLOW, segments=8, rings=6)


def mirror(x, y, z, w=1.0, h=1.6, frame=METAL_CHROME):
    cube((w, 0.05, h), (x, y, z), frame, bevel=0.02)
    cube((w - 0.1, 0.02, h - 0.1), (x, y - 0.03, z), ((0.45, 0.55, 0.65), 0.05, 1.0), bevel=0.0)


def sink(x, y, z, m=(WHITE, 0.3, 0.0)):
    cube((0.6, 0.45, 0.16), (x, y + 0.22, z + 0.85), m, bevel=0.05)
    cube((0.5, 0.35, 0.02), (x, y + 0.22, z + 0.94), (SLATE, 0.3, 0.0), bevel=0.0)
    rod((x, y + 0.4, z + 0.93), (x, y + 0.4, z + 1.15), 0.02, METAL_CHROME, verts=8)
    rod((x, y + 0.4, z + 1.15), (x, y + 0.22, z + 1.12), 0.02, METAL_CHROME, verts=8)
    rod((x, y + 0.2, z + 0.77), (x, y + 0.2, z + 0.02), 0.04, METAL_CHROME, verts=8)


def urinal(x, y, z, m=(WHITE, 0.3, 0.0)):
    cube((0.35, 0.3, 0.7), (x, y + 0.15, z + 0.75), m, bevel=0.08)
    cube((0.3, 0.05, 0.3), (x, y - 0.02, z + 0.85), (SLATE, 0.3, 0.0), bevel=0.02)
    rod((x, y + 0.15, z + 1.1), (x, y + 0.15, z + 1.5), 0.025, METAL_CHROME, verts=8)


def tile_wall(x0, x1, y, z0, z1, size=0.5, m=((0.85, 0.9, 0.92), 0.25, 0.0), grout=0.02):
    """A grid of bathroom tiles standing on the wall, in front of it."""
    nx = int((x1 - x0) / size)
    nz = int((z1 - z0) / size)
    for i in range(nx):
        for j in range(nz):
            cx = x0 + (i + 0.5) * size
            cz = z0 + (j + 0.5) * size
            cube((size - grout, 0.04, size - grout), (cx, y, cz), m, bevel=0.0)


def dumbbell(x, y, z, length=0.5, r=0.12, m=METAL_DARK):
    rod((x - length / 2, y, z), (x + length / 2, y, z), 0.025, METAL_CHROME, verts=8)
    for s in (-1, 1):
        cyl(r, 0.12, (x + s * (length / 2 - 0.06), y, z), m, rot=(0, math.pi / 2, 0), verts=12)


def punching_bag(x, y, z_ceiling, drop=1.2, h=1.3, r=0.25, m=(CREST_RED, 0.7, 0.0)):
    rod((x, y, z_ceiling), (x, y, z_ceiling - drop), 0.02, METAL_CHROME, verts=6)
    cyl(r, h, (x, y, z_ceiling - drop - h / 2), m, verts=14, bevel=0.06)
    torus(r * 0.9, 0.03, (x, y, z_ceiling - drop - 0.1), METAL_DARK)
    torus(r * 0.9, 0.03, (x, y, z_ceiling - drop - h + 0.1), METAL_DARK)


def spotlight(x, y, z_ceiling, m=NEON_WHITE, aim=0.3):
    cyl(0.12, 0.28, (x, y, z_ceiling - 0.2), METAL_DARK, rot=(aim, 0, 0), verts=12, r2=0.09)
    cyl(0.085, 0.03, (x, y - math.sin(aim) * 0.15, z_ceiling - 0.2 - math.cos(aim) * 0.15), m, rot=(aim, 0, 0), verts=12)


def ring_light(x, y, z, r=0.45):
    rod((x, y, z), (x, y, z + 1.4), 0.02, METAL_DARK, verts=8)
    for a in (0, 2.1, 4.2):
        rod((x, y, z + 0.02), (x + math.cos(a) * 0.35, y + math.sin(a) * 0.35, z), 0.015, METAL_DARK, verts=6)
    torus(r, 0.05, (x, y, z + 1.4 + r), NEON_WHITE, rot=(math.pi / 2, 0, 0), major_segments=28)
    cube((0.08, 0.02, 0.16), (x, y - 0.02, z + 1.4 + r), PLASTIC_BLACK, bevel=0.01)


def phone_tripod(x, y, z):
    for a in (0.5, 2.6, 4.7):
        rod((x, y, z + 1.2), (x + math.cos(a) * 0.3, y + math.sin(a) * 0.3, z), 0.012, METAL_DARK, verts=6)
    cube((0.08, 0.015, 0.16), (x, y - 0.01, z + 1.32), PLASTIC_BLACK, bevel=0.01)
    cube((0.06, 0.01, 0.13), (x, y - 0.02, z + 1.32), SCREEN_CYAN, bevel=0.0)


def treadmill_silhouette(x, y, z, m=(SLATE, 0.6, 0.4)):
    cube((1.6, 0.7, 0.16), (x, y + 0.35, z + 0.10), m, bevel=0.03)
    cube((1.4, 0.55, 0.04), (x, y + 0.35, z + 0.20), PLASTIC_BLACK, bevel=0.0)
    rod((x + 0.7, y + 0.35, z + 0.18), (x + 0.7, y + 0.35, z + 1.2), 0.04, m, verts=8)
    cube((0.5, 0.3, 0.2), (x + 0.7, y + 0.35, z + 1.25), m, bevel=0.03)
    cube((0.35, 0.03, 0.14), (x + 0.7, y + 0.2, z + 1.27), SCREEN_CYAN, bevel=0.0)


def weight_rack(x, y, z, w=1.6):
    cube((w, 0.4, 0.05), (x, y + 0.2, z + 0.5), METAL_DARK, bevel=0.01)
    cube((w, 0.4, 0.05), (x, y + 0.2, z + 0.95), METAL_DARK, bevel=0.01)
    for s in (-1, 1):
        cube((0.05, 0.05, 1.0), (x + s * (w / 2 - 0.05), y + 0.38, z + 0.5), METAL_DARK, bevel=0.005)
    n = int(w / 0.38)
    for i in range(n):
        dumbbell(x - w / 2 + 0.25 + i * 0.38, y + 0.2, z + 0.62, length=0.28, r=0.07 + (i % 3) * 0.02)
        dumbbell(x - w / 2 + 0.25 + i * 0.38, y + 0.2, z + 1.07, length=0.28, r=0.06 + ((i + 1) % 3) * 0.02)


def air_duct(x0, x1, y, z, size=0.45, m=(STEEL, 0.5, 0.6)):
    cube((x1 - x0, size, size), ((x0 + x1) / 2, y, z), m, bevel=0.02)
    n = int((x1 - x0) / 1.5)
    for i in range(n + 1):
        cube((0.04, size + 0.05, size + 0.05), (x0 + i * (x1 - x0) / max(n, 1), y, z), METAL_DARK, bevel=0.005)


def exit_sign(x, y, z):
    neon_sign("EXIT", x, y, z, NEON_GREEN, cell=0.07, backing=PLASTIC_BLACK)


def wall_panel_lines(x0, x1, y, z0, z1, spacing=1.0, m=METAL_DARK):
    """Thin seams that break up a big wall into panels."""
    zz = z0 + spacing
    while zz < z1:
        cube((x1 - x0, 0.04, 0.03), ((x0 + x1) / 2, y, zz), m, bevel=0.0)
        zz += spacing
    xx = x0 + spacing * 1.5
    while xx < x1:
        cube((0.03, 0.04, z1 - z0), (xx, y, (z0 + z1) / 2), m, bevel=0.0)
        xx += spacing * 1.5
