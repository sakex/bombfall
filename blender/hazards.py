# Builders for the hazards and pick-ups: things with moving pivots the game
# animates. Same conventions as furniture.py (origin at the bottom centre,
# facing -Y in Blender / +Z in Godot).
import math

from common import *  # noqa: F401,F403

RUBBER = ((0.06, 0.06, 0.09), 0.9, 0.0)
DRONE_BODY = ((0.10, 0.11, 0.16), 0.4, 0.6)


def trampoline():
    """A 2 m round trampoline; the game bounces whatever touches its mat."""
    for i in range(4):
        a = i / 4.0 * math.tau + math.pi / 4
        rod((math.cos(a) * 0.75, math.sin(a) * 0.75, 0.0), (math.cos(a) * 0.85, math.sin(a) * 0.85, 0.55), 0.04, METAL_STEEL)
        sphere(0.06, (math.cos(a) * 0.75, math.sin(a) * 0.75, 0.03), METAL_DARK, segments=8, rings=6)
    torus(0.95, 0.06, (0, 0, 0.6), METAL_STEEL, major_segments=28)
    torus(0.95, 0.03, (0, 0, 0.66), NEON_CYAN, major_segments=28)
    cyl(0.82, 0.05, (0, 0, 0.6), RUBBER, verts=28)
    for i in range(16):
        a = i / 16.0 * math.tau
        rod((math.cos(a) * 0.82, math.sin(a) * 0.82, 0.6), (math.cos(a) * 0.93, math.sin(a) * 0.93, 0.6), 0.012, METAL_CHROME, verts=5)
    cube((0.9, 0.04, 0.01), (0, 0, 0.63), NEON_PINK, bevel=0.0)
    cube((0.04, 0.9, 0.01), (0, 0, 0.63), NEON_PINK, bevel=0.0)


def wall_gun():
    """A wall-mounted turret. The mount plate hugs the wall at x = 0 and the
    'gun' pivot (at x = 0.7) swings the barrel, which points along +X."""
    cube((0.4, 1.4, 2.0), (0.2, 0, 1.0), METAL_DARK, bevel=0.05)
    for z in (0.3, 1.7):
        for y in (-0.5, 0.5):
            sphere(0.07, (0.42, y, z), METAL_CHROME, segments=8, rings=6)
    cube((0.3, 0.06, 1.6), (0.42, 0, 1.0), NEON_ORANGE, bevel=0.0)
    cyl(0.32, 0.5, (0.65, 0, 1.0), METAL_STEEL, rot=(0, math.pi / 2, 0), verts=14)
    g = pivot("gun", (0.7, 0, 1.0))
    sphere(0.36, (0.7, 0, 1.0), METAL_DARK, segments=14, rings=10, parent=g)
    cube((1.9, 0.6, 0.5), (1.6, 0, 1.0), METAL_STEEL, bevel=0.05, parent=g)
    cyl(0.16, 1.4, (2.5, 0, 1.0), METAL_DARK, rot=(0, math.pi / 2, 0), verts=12, parent=g)
    cyl(0.10, 0.2, (3.2, 0, 1.0), NEON_MAGENTA, rot=(0, math.pi / 2, 0), verts=10, parent=g)
    cube((1.2, 0.04, 0.12), (1.6, -0.31, 1.15), NEON_MAGENTA, bevel=0.0, parent=g)
    cube((0.6, 0.45, 0.25), (1.3, 0, 1.4), METAL_DARK, bevel=0.03, parent=g)
    cube((0.4, 0.02, 0.15), (1.3, -0.24, 1.42), SCREEN_CYAN, bevel=0.0, parent=g)
    torus(0.19, 0.03, (2.0, 0, 1.0), NEON_MAGENTA, rot=(0, math.pi / 2, 0), parent=g)


def plasma_bullet():
    """A crackling plasma ball, 0.6 m across, centred."""
    sphere(0.22, (0, 0, 0), neon((1.0, 0.95, 0.7), 8.0, (0.9, 0.85, 0.6)), segments=12, rings=8)
    sphere(0.30, (0, 0, 0), neon((0.5, 0.3, 1.0), 4.0, (0.3, 0.15, 0.6)), scale=(1.0, 0.85, 1.0), segments=12, rings=8)
    for i in range(6):
        a = i / 6.0 * math.tau
        cone(0.06, 0.28, (math.cos(a) * 0.36, 0, math.sin(a) * 0.36), neon((0.6, 0.4, 1.0), 5.0), rot=(0, a + math.pi / 2, 0), verts=5)


def drone():
    """A quadcopter, 2 m across: body with a camera eye and four arms with
    rotor pivots rotor_1..rotor_4 the game spins. Centred at the body."""
    sphere(0.55, (0, 0, 0), DRONE_BODY, scale=(1.0, 0.85, 0.45), segments=16, rings=10)
    cube((0.8, 0.5, 0.25), (0, 0, 0.15), DRONE_BODY, bevel=0.06)
    sphere(0.14, (0, -0.42, -0.02), neon((1.0, 0.2, 0.3), 5.0, (0.3, 0.05, 0.08)), segments=10, rings=8)  # eye
    cube((0.7, 0.06, 0.04), (0, -0.3, 0.12), NEON_CYAN, bevel=0.0)
    cyl(0.16, 0.3, (0, 0, -0.32), METAL_DARK, r2=0.10, verts=10)
    sphere(0.10, (0, 0, -0.5), neon((0.2, 0.9, 1.0), 4.0), segments=8, rings=6)
    for i, (sx, sy) in enumerate([(-1, -1), (1, -1), (1, 1), (-1, 1)]):
        ax, ay = sx * 0.85, sy * 0.55
        rod((sx * 0.3, sy * 0.2, 0.05), (ax, ay, 0.1), 0.06, METAL_STEEL)
        cyl(0.09, 0.18, (ax, ay, 0.12), METAL_DARK, verts=10)
        p = pivot("rotor_%d" % (i + 1), (ax, ay, 0.24))
        cyl(0.03, 0.12, (ax, ay, 0.25), METAL_CHROME, verts=6, parent=p)
        for k in range(2):
            cube((0.62, 0.08, 0.015), (ax, ay, 0.30), ((0.3, 0.32, 0.36), 0.4, 0.5), rot=(0, 0, k * math.pi / 2), bevel=0.0, parent=p)
        torus(0.36, 0.02, (ax, ay, 0.30), NEON_CYAN if i % 2 else NEON_MAGENTA, major_segments=20, minor_segments=5)


def light_ring():
    """A standing portal ring on a base, 3.1 m wide, 4 m tall. The 'ring'
    pivot holds the glowing torus (its emission is raised as it charges);
    the laser beam itself is a mesh the game adds, firing along -X."""
    cube((2.6, 1.6, 0.3), (0, 0, 0.15), METAL_DARK, bevel=0.05)
    cube((2.2, 1.2, 0.35), (0, 0, 0.45), METAL_STEEL, bevel=0.05)
    cube((2.0, 0.05, 0.1), (0, -0.62, 0.45), NEON_MAGENTA, bevel=0.0)
    for s in (-1, 1):
        rod((s * 0.9, 0.3, 0.6), (s * 1.25, 0.2, 2.3), 0.10, METAL_STEEL)
    r = pivot("ring", (0, 0, 2.35))
    torus(1.35, 0.14, (0, 0, 2.35), METAL_STEEL, rot=(math.pi / 2, 0, 0), major_segments=32, minor_segments=10, parent=r)
    torus(1.35, 0.06, (0, -0.15, 2.35), neon((0.6, 0.3, 1.0), 1.0, (0.2, 0.1, 0.35)), rot=(math.pi / 2, 0, 0), major_segments=32, minor_segments=8, name="glow", parent=r)
    for i in range(12):
        a = i / 12.0 * math.tau
        cube((0.18, 0.4, 0.12), (math.cos(a) * 1.38, 0, 2.35 + math.sin(a) * 1.38), METAL_DARK, rot=(0, -a, 0), bevel=0.01, parent=r)
    cyl(0.14, 0.4, (-1.55, 0, 2.35), METAL_DARK, rot=(0, math.pi / 2, 0), verts=10, name="emitter")
    sphere(0.12, (-1.78, 0, 2.35), neon((1.0, 0.3, 0.6), 4.0), segments=10, rings=8)
    for k in range(3):
        cable_pts = [(1.2 - k * 0.1, 0.5, 0.6), (1.6, 0.6, 1.4 + k * 0.3), (1.3, 0.55, 2.2 + k * 0.2)]
        for a, b in zip(cable_pts, cable_pts[1:]):
            rod(a, b, 0.02, PLASTIC_BLACK, verts=5)


def button():
    """A big red floor button, 1.9 m wide. The cap sits on the 'top' pivot
    and the game pushes it down 0.15 m when something rests on it."""
    cube((1.9, 1.3, 0.28), (0, 0, 0.14), METAL_DARK, bevel=0.06)
    cube((1.7, 1.1, 0.06), (0, 0, 0.31), METAL_STEEL, bevel=0.02)
    for sx in (-1, 1):
        for sy in (-1, 1):
            sphere(0.05, (sx * 0.8, sy * 0.5, 0.3), METAL_CHROME, segments=8, rings=6)
    cube((1.7, 0.04, 0.06), (0, -0.66, 0.2), NEON_YELLOW, bevel=0.0)
    for i in range(6):
        cube((0.16, 0.04, 0.16), (-0.75 + i * 0.3, -0.66, 0.14), NEON_YELLOW if i % 2 else PLASTIC_BLACK, bevel=0.0)
    t = pivot("top", (0, 0, 0.34))
    cube((1.3, 0.9, 0.32), (0, 0, 0.5), ((0.85, 0.06, 0.08), 0.35, 0.0), bevel=0.12, parent=t)
    cube((1.0, 0.6, 0.02), (0, 0, 0.67), neon((1.0, 0.3, 0.3), 1.5, (0.6, 0.06, 0.08)), bevel=0.0, parent=t)


def fire_zone():
    """A blazing fireball 2 m across, centred; the game wobbles it."""
    sphere(0.75, (0, 0, 0), neon((1.0, 0.3, 0.05), 4.0, (0.8, 0.2, 0.02)), scale=(1.1, 1.0, 1.25), segments=14, rings=10)
    sphere(0.45, (0, -0.2, 0.1), neon((1.0, 0.75, 0.2), 7.0, (1.0, 0.6, 0.1)), scale=(1.1, 1.0, 1.3), segments=12, rings=8)
    for i in range(7):
        a = i / 7.0 * math.tau
        cone(0.22, 0.9, (math.cos(a) * 0.5, math.sin(a) * 0.35, 0.55), neon((1.0, 0.45, 0.05), 3.5, (0.8, 0.3, 0.02)), rot=(math.sin(a) * 0.4, -math.cos(a) * 0.4, 0), verts=6)
    for i in range(5):
        sphere(0.08, (math.cos(i * 1.3) * 0.7, math.sin(i * 1.3) * 0.5, 0.9 + i * 0.15), neon((1.0, 0.8, 0.3), 6.0), segments=6, rings=4)


def rope_link():
    """One 1 m chain link, lying along X, centred: a capsule with a neon core."""
    cyl(0.12, 0.8, (0, 0, 0), METAL_STEEL, rot=(0, math.pi / 2, 0), verts=10)
    sphere(0.14, (-0.42, 0, 0), METAL_DARK, segments=10, rings=8)
    sphere(0.14, (0.42, 0, 0), METAL_DARK, segments=10, rings=8)
    cube((0.6, 0.26, 0.03), (0, 0, 0.0), NEON_CYAN, bevel=0.0)
    torus(0.17, 0.03, (0, 0, 0), METAL_CHROME, rot=(0, math.pi / 2, 0), major_segments=14, minor_segments=6)


def treadmill():
    """A treadmill 4 m long, 2.75 m tall: deck with rollers ('roller_1',
    'roller_2' pivots the game spins) and a console at +X."""
    cube((3.6, 1.4, 0.35), (-0.2, 0, 0.3), METAL_DARK, bevel=0.06)
    cube((3.2, 1.1, 0.08), (-0.2, 0, 0.52), RUBBER, bevel=0.01)
    for i in range(6):
        cube((0.08, 1.0, 0.012), (-1.5 + i * 0.52, 0, 0.565), NEON_CYAN, bevel=0.0)
    for k, x in enumerate((-1.85, 1.45)):
        p = pivot("roller_%d" % (k + 1), (x, 0, 0.42))
        cyl(0.16, 1.2, (x, 0, 0.42), METAL_STEEL, rot=(math.pi / 2, 0, 0), verts=12, parent=p)
        cube((0.04, 1.2, 0.34), (x, 0, 0.42), NEON_MAGENTA, bevel=0.0, parent=p)
    for s in (-1, 1):
        cube((0.5, 0.25, 0.15), (-0.2, s * 0.62, 0.62), METAL_STEEL, bevel=0.03)
    rod((1.6, -0.5, 0.5), (1.9, -0.5, 2.0), 0.07, METAL_STEEL)
    rod((1.6, 0.5, 0.5), (1.9, 0.5, 2.0), 0.07, METAL_STEEL)
    rod((1.9, -0.5, 2.0), (1.9, 0.5, 2.0), 0.06, METAL_CHROME)
    cube((0.9, 1.2, 0.5), (1.85, 0, 2.3), METAL_DARK, rot=(0, -0.3, 0), bevel=0.05)
    cube((0.6, 0.9, 0.03), (1.72, 0, 2.52), SCREEN_CYAN, rot=(0, -0.3, 0), bevel=0.0)
    cube((0.5, 0.05, 0.05), (1.75, -0.5, 2.6), NEON_PINK, rot=(0, -0.3, 0), bevel=0.0)
    for s in (-1, 1):
        rod((1.4, s * 0.55, 2.0), (0.4, s * 0.62, 1.9), 0.04, METAL_CHROME)


def pedestal():
    """The pick-up pedestal ('pusher'): a heavy column 1.5 m wide, 1.5 m tall
    with a cyan tractor beam rising above it where the item floats."""
    cube((1.5, 1.2, 0.35), (0, 0, 0.18), METAL_DARK, bevel=0.06)
    cyl(0.5, 0.9, (0, 0, 0.8), METAL_STEEL, r2=0.42, verts=16)
    cyl(0.56, 0.16, (0, 0, 1.3), METAL_DARK, verts=16)
    torus(0.5, 0.04, (0, 0, 1.36), NEON_CYAN, major_segments=24)
    for i in range(4):
        a = i / 4.0 * math.tau
        cube((0.12, 0.05, 0.6), (math.cos(a) * 0.46, math.sin(a) * 0.46, 0.75), NEON_CYAN, rot=(0, 0, a), bevel=0.0)
    cyl(0.42, 1.3, (0, 0, 2.05), neon((0.3, 0.9, 1.0), 0.5, (0.05, 0.25, 0.3)), r2=0.3, verts=16, name="beam")


def shield_battery():
    """A glowing cyan energy cell, 0.8 m wide, 1.4 m tall, centred."""
    cyl(0.32, 1.1, (0, 0, 0), METAL_STEEL, verts=14)
    cyl(0.34, 0.5, (0, 0, 0), neon((0.2, 0.9, 1.0), 3.5, (0.05, 0.3, 0.4)), verts=14)
    for z in (-0.32, 0.32):
        torus(0.33, 0.04, (0, 0, z), METAL_DARK, major_segments=16)
    cyl(0.16, 0.18, (0, 0, 0.62), METAL_CHROME, verts=10)
    cube((0.2, 0.05, 0.05), (0, -0.36, 0.0), NEON_WHITE, bevel=0.0)
    cube((0.05, 0.05, 0.2), (0, -0.36, 0.0), NEON_WHITE, bevel=0.0)


def shield_core():
    """A hexagonal shield core token, 1 m wide, 1.2 m tall, centred."""
    cyl(0.6, 0.18, (0, 0, 0), METAL_CHROME, rot=(math.pi / 2, 0, 0), verts=6)
    cyl(0.5, 0.2, (0, 0, 0), neon((0.4, 0.5, 1.0), 2.5, (0.1, 0.12, 0.35)), rot=(math.pi / 2, 0, 0), verts=6)
    for s in (-1, 1):
        cyl(0.28, 0.04, (0, s * 0.12, 0), neon((0.8, 0.9, 1.0), 4.0, (0.5, 0.6, 0.7)), rot=(math.pi / 2, 0, 0), verts=6)
        torus(0.42, 0.03, (0, s * 0.11, 0), NEON_CYAN, rot=(math.pi / 2, 0, 0), major_segments=12)


def magnet():
    """A classic horseshoe magnet 1.2 m tall, poles pointing up, centred."""
    RED_M = ((0.85, 0.06, 0.08), 0.35, 0.2)
    arc = torus(0.4, 0.14, (0, 0, -0.15), RED_M, rot=(math.pi / 2, 0, 0), major_segments=24, minor_segments=10)
    bpy.ops.object.select_all(action="DESELECT")
    arc.select_set(True)
    bpy.context.view_layer.objects.active = arc
    bpy.ops.object.mode_set(mode="EDIT")
    bpy.ops.mesh.select_all(action="SELECT")
    bpy.ops.mesh.bisect(plane_co=(0, 0, -0.15), plane_no=(0, 0, 1), clear_inner=True, use_fill=True)
    bpy.ops.object.mode_set(mode="OBJECT")
    for s in (-1, 1):
        cube((0.28, 0.28, 0.5), (s * 0.4, 0, 0.1), RED_M, bevel=0.03)
        cube((0.28, 0.28, 0.25), (s * 0.4, 0, 0.47), METAL_CHROME, bevel=0.03)
        cube((0.29, 0.29, 0.03), (s * 0.4, 0, 0.35), NEON_CYAN, bevel=0.0)
    for i in range(3):
        torus(0.15 + i * 0.12, 0.012, (0, 0, 0.75 + i * 0.05), neon((0.5, 0.9, 1.0), 2.5), rot=(0, 0, 0), major_segments=16, minor_segments=5)


def crate():
    """A supply crate 1.4 m wide, 1.2 m tall, centred, with a glowing cross."""
    cube((1.4, 1.0, 1.2), (0, 0, 0), ((0.45, 0.30, 0.10), 0.85, 0.0), bevel=0.04)
    for z in (-0.5, 0.5):
        cube((1.45, 1.05, 0.08), (0, 0, z), METAL_DARK, bevel=0.01)
    for x in (-0.6, 0.6):
        cube((0.08, 1.05, 1.25), (x, 0, 0), METAL_DARK, bevel=0.01)
    cube((0.5, 0.04, 0.16), (0, -0.52, 0), NEON_GREEN, bevel=0.0)
    cube((0.16, 0.04, 0.5), (0, -0.52, 0), NEON_GREEN, bevel=0.0)
    cube((0.7, 0.02, 0.7), (0, -0.51, 0), ((0.9, 0.9, 0.85), 0.8, 0.0), bevel=0.0)


def boss_bat():
    """The bat boss: a 4 m armoured body with horned head and glowing veins;
    'wing_l' / 'wing_r' pivots at the shoulders flap the wings. Centred."""
    ARMOR = ((0.12, 0.05, 0.08), 0.45, 0.5)
    VEIN = neon((1.0, 0.45, 0.1), 4.0, (0.4, 0.15, 0.03))
    sphere(1.1, (0, 0, 0), ARMOR, scale=(0.9, 0.75, 1.3), segments=16, rings=12)
    sphere(0.7, (0, 0, 1.5), ARMOR, scale=(1.0, 0.9, 0.85), segments=14, rings=10)
    for s in (-1, 1):
        cone(0.18, 0.9, (s * 0.5, 0, 2.2), ARMOR, rot=(0, s * 0.3, 0), verts=8)
        sphere(0.14, (s * 0.28, -0.6, 1.55), neon((1.0, 0.2, 0.1), 6.0), segments=8, rings=6)
        cube((0.1, 0.06, 0.9), (s * 0.35, -0.75, 0.2), VEIN, rot=(0, s * 0.2, 0), bevel=0.0)
        cube((0.5, 0.06, 0.08), (s * 0.35, -0.75, -0.4), VEIN, bevel=0.0)
        rod((s * 0.6, 0, -1.1), (s * 0.8, -0.2, -1.9), 0.16, ARMOR)
        sphere(0.2, (s * 0.85, -0.25, -1.95), ARMOR, segments=8, rings=6)
        for k in range(3):
            cone(0.05, 0.3, (s * (0.75 + k * 0.1), -0.35, -2.1), METAL_CHROME, rot=(0.5, 0, 0), verts=5)
    cube((0.3, 0.06, 1.6), (0, -0.78, 0.3), VEIN, bevel=0.0)
    for s in (-1, 1):
        w = pivot("wing_l" if s < 0 else "wing_r", (s * 0.9, 0.1, 0.7))
        rod((s * 0.9, 0.1, 0.7), (s * 2.6, 0.1, 1.6), 0.13, ARMOR, parent=w)
        rod((s * 2.6, 0.1, 1.6), (s * 4.2, 0.1, 0.6), 0.10, ARMOR, parent=w)
        rod((s * 2.6, 0.1, 1.6), (s * 3.6, 0.1, -0.6), 0.09, ARMOR, parent=w)
        rod((s * 2.6, 0.1, 1.6), (s * 2.5, 0.1, -1.2), 0.08, ARMOR, parent=w)
        mem = cube((3.0, 0.05, 2.4), (s * 2.6, 0.12, 0.3), neon((0.6, 0.1, 0.2), 1.2, (0.25, 0.04, 0.08)), bevel=0.0, parent=w)
        mem.rotation_euler = (0, 0, 0)
        for k in range(3):
            cube((1.2, 0.02, 0.05), (s * (1.9 + k * 0.5), 0.09, 1.2 - k * 0.6), VEIN, rot=(0, s * (0.4 - k * 0.5), 0), bevel=0.0, parent=w)


def heart():
    """A glowing heart 1 m tall, centred."""
    HEART_M = neon((1.0, 0.15, 0.3), 4.0, (0.5, 0.05, 0.1))
    for s in (-1, 1):
        sphere(0.3, (s * 0.25, 0, 0.2), HEART_M, segments=12, rings=8)
    cone(0.5, 0.75, (0, 0, -0.2), HEART_M, rot=(math.pi, 0, 0), verts=12)
    sphere(0.08, (-0.3, -0.2, 0.35), NEON_WHITE, segments=6, rings=4)


def block():
    """A 1 m crystal block the boss's shots leave behind, centred."""
    cube((0.95, 0.95, 0.95), (0, 0, 0), neon((0.5, 0.2, 0.9), 1.0, (0.25, 0.1, 0.45)), bevel=0.12)
    cube((0.6, 0.6, 0.6), (0, 0, 0), neon((0.9, 0.5, 1.0), 3.0), rot=(0.6, 0.4, 0.3), bevel=0.05)
