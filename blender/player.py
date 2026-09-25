# The hero: a chibi astronaut-robot (~1.6 m to the helmet top) in a coral
# rubberised pressure suit, with a glossy black bomb face inside a coral
# full-face biker helmet (flipped-up smoked visor on chrome hinges, racing
# stripes, tail light), two huge glowing eyes with sparkles, a springy
# antenna, a cyan scarf, a jet pack, white stitched mittens and chunky boots.
#
# One skinned mesh on an Armature; authored clips (30 fps):
#   idle, run_loop, jump, rise_loop, fall_loop, land, push_loop, hurt,
#   death, wave. src/actors/player.gd picks and crossfades them, and adds
#   blinks (eye_l/eye_r bone scale), jet flames (jet_l/jet_r bone scale),
#   antenna and scarf springs (bone rotation offsets) on top.
#   blender -b --python blender/player.py -- --preview blender/previews
#   NO_BAKE=1 ... for a fast look; HERO_SHEET=0 skips the pose contact sheet.
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from hero_kit import *  # noqa: F401,F403

# Take --preview away from common.export(): the stock preview would show all
# clips stacked at once. This script renders its own previews.
PREVIEW = None
if "--preview" in sys.argv:
    i = sys.argv.index("--preview")
    PREVIEW = sys.argv[i + 1]
    del sys.argv[i:i + 2]

clean_scene()

# ------------------------------------------------------------- materials --
SUIT = pbr("fabric", (0.92, 0.22, 0.17), rough=0.62, bump=0.30, grime=0.30, name="suit")
SUIT_PAD = pbr("rubber", (0.16, 0.04, 0.08), rough=0.55, name="suit_pad")
HELMET = pbr("plastic", (1.0, 0.30, 0.20), rough=0.12, wear=0.10, grime=0.10, bump=0.0, name="helmet")
FACE = pbr("plastic", (0.006, 0.006, 0.010), rough=0.06, wear=0.0, grime=0.0, bump=0.0, name="face")
VISOR = pbr("plastic", (0.03, 0.02, 0.06), rough=0.04, wear=0.0, grime=0.08, bump=0.0, name="visor")
CHROME_M = pbr("chrome", CHROME, name="chrome")
GLOVE = pbr("leather", (0.80, 0.80, 0.84), rough=0.45, grime=0.35, name="glove")
BOOT = pbr("plastic", (0.82, 0.82, 0.86), rough=0.30, grime=0.35, name="boot")
SOLE = pbr("rubber", (0.03, 0.03, 0.04), name="sole")
PACK = pbr("paint", (0.06, 0.065, 0.09), name="pack")
BELT = pbr("leather", (0.045, 0.035, 0.05), name="belt")
SCARF = pbr("fabric", (0.03, 0.56, 0.74), color2=(0.02, 0.36, 0.52), rough=0.8, name="scarf")
NOZZLE = pbr("metal", (0.22, 0.23, 0.27), rough=0.3, name="nozzle")
RUBBER = pbr("rubber", (0.025, 0.025, 0.03), name="rubber")
EYE_RIM = pbr("neon", (0.02, 0.20, 0.50), strength=2.0, name="eye_rim")
EYE = pbr("neon", (0.10, 0.85, 1.00), strength=3.2, name="eye")
EYE_CORE = pbr("neon", (0.02, 0.22, 0.55), strength=1.6, name="eye_core")
SPARK = pbr("neon", (1.0, 1.0, 1.0), strength=10.0, name="spark")
BLUSH = pbr("neon", (1.0, 0.33, 0.55), strength=1.3, name="blush")
PINK_L = pbr("neon", PINK, strength=6.0, name="pink_light")
CYAN_L = pbr("neon", CYAN, strength=4.0, name="cyan_light")
FLAME = pbr("neon", (1.0, 0.50, 0.12), strength=6.0, name="flame")
FLAME_CORE = pbr("neon", (1.0, 0.92, 0.65), strength=9.0, name="flame_core")

# ------------------------------------------------------------ dimensions --
HC = V((0.0, -0.01, 1.20))            # head centre
HR = (0.47, 0.44, 0.43)               # helmet outer radii
FR = (0.418, 0.39, 0.382)             # the black face/head inside it
NECK_CUT = HC.z - 0.335
S = {1: V((0.215, 0.0, 0.745)), -1: V((-0.215, 0.0, 0.745))}      # shoulders
E = {s: V((s * 0.30, 0.0, 0.61)) for s in (1, -1)}                 # elbows
WR = {s: V((s * 0.35, -0.012, 0.49)) for s in (1, -1)}             # wrists
HT = {s: V((s * 0.375, -0.03, 0.35)) for s in (1, -1)}             # mitten tips
HIP = {s: V((s * 0.105, 0.0, 0.37)) for s in (1, -1)}
KNEE = {s: V((s * 0.11, -0.012, 0.235)) for s in (1, -1)}
ANK = {s: V((s * 0.115, 0.0, 0.11)) for s in (1, -1)}
TOE = {s: V((s * 0.115, -0.17, 0.045)) for s in (1, -1)}
SIDE = {1: "l", -1: "r"}              # character's left is +X (it faces -Y)

PARTS = []                            # (object, skin spec)


def part(o, skin):
    PARTS.append((o, skin))
    return o


# Torso rings: (z, rx, ry, cx, cy). A pot belly, a flatter back.
TORSO = [
    (0.262, 0.03, 0.03, 0, 0.0), (0.275, 0.09, 0.08, 0, 0.0), (0.30, 0.15, 0.13, 0, -0.003),
    (0.335, 0.19, 0.162, 0, -0.006), (0.38, 0.215, 0.182, 0, -0.01), (0.44, 0.23, 0.195, 0, -0.014),
    (0.50, 0.236, 0.200, 0, -0.016), (0.56, 0.234, 0.197, 0, -0.014), (0.62, 0.226, 0.19, 0, -0.01),
    (0.68, 0.212, 0.178, 0, -0.006), (0.735, 0.19, 0.16, 0, -0.003), (0.785, 0.16, 0.138, 0, 0.0),
    (0.825, 0.12, 0.108, 0, 0.0), (0.855, 0.082, 0.078, 0, 0.0), (0.885, 0.07, 0.066, 0, 0.0),
    (0.93, 0.066, 0.062, 0, 0.0),
]


def torso_at(z):
    """Interpolated (rx, ry, cy) of the torso at height z."""
    for a, b in zip(TORSO[:-1], TORSO[1:]):
        if a[0] <= z <= b[0]:
            t = (z - a[0]) / (b[0] - a[0])
            return tuple(a[i] + (b[i] - a[i]) * t for i in (1, 2, 4))
    r = TORSO[0] if z < TORSO[0][0] else TORSO[-1]
    return r[1], r[2], r[4]


def torso_pt(z, ang, off=0.0):
    """Point on the torso surface at height z; ang 0 = front (-Y), +90 = +X."""
    rx, ry, cy = torso_at(z)
    a = math.radians(ang)
    return V(((rx + off) * math.sin(a), cy - (ry + off) * math.cos(a), z))


def torso_skin(co):
    return ("chain", ["hips", "spine", "chest", "neck"],
            [(0, 0, 0.20), (0, 0, 0.52), (0, 0, 0.66), (0, 0, 0.84), (0, 0, 0.96)], [0.07, 0.07, 0.035])


TORSO_SKIN = torso_skin(None)


# ------------------------------------------------------------------ body --
def build_torso():
    o = lathe(TORSO, SUIT, segs=24, name="torso", caps=(True, False))
    part(o, TORSO_SKIN)
    # Belt with a chrome buckle and two pouches.
    zb = 0.43
    path = [torso_pt(zb, a, 0.006) for a in range(0, 360, 18)]
    belt = tube(path, [(0.03, 0.011)] * len(path), BELT, segs=6, closed=True, fixed=True, ref=(0, 0, 1),
                shape=lambda i, a: 1.0 / max(abs(math.cos(a)) ** 4 + abs(math.sin(a)) ** 4, 1e-6) ** 0.25,
                name="belt")
    part(belt, TORSO_SKIN)
    p = torso_pt(zb, 0, 0.018)
    part(rounded_box((0.085, 0.022, 0.066), p, CHROME_M, radius=0.008, segs=2, name="buckle"), TORSO_SKIN)
    for s in (1, -1):
        ang = s * 62
        q = torso_pt(zb - 0.01, ang, 0.035)
        rot = (0, 0, math.radians(-ang))
        part(rounded_box((0.085, 0.05, 0.08), q, BELT, radius=0.014, segs=2, rot=rot, name="pouch"), TORSO_SKIN)
        part(rounded_box((0.09, 0.056, 0.032), q + V((0, 0, 0.028)), SUIT_PAD, radius=0.01, segs=1, rot=rot, name="flap"), TORSO_SKIN)
        part(rounded_box((0.016, 0.008, 0.016), torso_pt(zb + 0.005, ang, 0.063), CHROME_M, radius=0.004, segs=1, rot=rot, name="snap"), TORSO_SKIN)
    # Zip down the chest with a chrome pull tab.
    zs = [0.835 - 0.03 * i for i in range(14)]
    zp = [torso_pt(z, 0, 0.002) for z in zs if z > zb + 0.03]
    zip_ = tube(zp, [(0.011, 0.004)] * len(zp), RUBBER, segs=6, ref=(1, 0, 0), name="zip")
    part(zip_, TORSO_SKIN)
    part(rounded_box((0.02, 0.008, 0.04), torso_pt(0.77, 0, 0.012), CHROME_M, radius=0.005, segs=1, name="zip_tab"), TORSO_SKIN)
    # Chest badge: a chrome ring, dark face and a glowing lightning bolt.
    bz, ba = 0.64, 30
    c = torso_pt(bz, ba, 0.004)
    rx, ry, cy = torso_at(bz)
    nrm = V((c.x / rx ** 2, (c.y - cy) / ry ** 2, 0.0)).normalized()
    q = V((0, 0, 1)).rotation_difference(nrm)
    ring = prim("cylinder", CHROME_M, "badge", vertices=20, radius=0.05, depth=0.014)
    transform(ring, loc=c, rot=q)
    part(ring, TORSO_SKIN)
    face = prim("cylinder", RUBBER, "badge_face", vertices=20, radius=0.04, depth=0.006)
    transform(face, loc=c + nrm * 0.006, rot=q)
    part(face, TORSO_SKIN)
    bolt = [(-0.004, 0.032), (0.02, 0.032), (0.006, 0.006), (0.02, 0.006), (-0.012, -0.034), (-0.002, -0.006), (-0.016, -0.006)]
    bm_verts = [V((x, y, 0.0)) for x, y in bolt] + [V((x, y, 0.004)) for x, y in bolt]
    n = len(bolt)
    faces = [tuple(range(n))[::-1], tuple(range(n, 2 * n))] + [(i, (i + 1) % n, n + (i + 1) % n, n + i) for i in range(n)]
    b = mesh_object("bolt", bm_verts, faces, CYAN_L, smooth=False)
    transform(b, loc=c + nrm * 0.009, rot=q)
    part(b, TORSO_SKIN)


def build_leg(s):
    x = s
    top = HIP[s] + V((0, 0, 0.07))
    path = [top, HIP[s], HIP[s].lerp(KNEE[s], 0.5), KNEE[s] + V((0, 0, 0.03)), KNEE[s], KNEE[s] - V((0, 0, 0.03)),
            KNEE[s].lerp(ANK[s], 0.5), ANK[s] + V((0, 0, 0.02)), ANK[s] - V((0, 0, 0.02))]
    radii = [0.08, 0.086, 0.08, 0.074, 0.072, 0.07, 0.066, 0.062, 0.06]
    leg = tube(path, radii, SUIT, segs=14, name="leg_" + SIDE[s], ref=(1, 0, 0))
    bones = ["hips", "thigh_" + SIDE[s], "shin_" + SIDE[s], "foot_" + SIDE[s]]
    part(leg, ("chain", bones, [top, HIP[s], KNEE[s], ANK[s], TOE[s]], [0.035, 0.05, 0.03]))
    # Knee pad: a rubber shell over the front of the knee.
    kp = prim("uv_sphere", SUIT_PAD, "knee_pad", segments=10, ring_count=6, radius=1.0)
    transform(kp, loc=KNEE[s] + V((0, -0.048, -0.005)), scale=(0.07, 0.045, 0.07))
    part(kp, ("rigid", "shin_" + SIDE[s]))
    # Boot: upper shaft, a bulbous toe box, padded cuff, rubber sole with a lit strip.
    ax, ay = ANK[s].x, ANK[s].y
    foot = "foot_" + SIDE[s]
    shaft = lathe([(0.03, 0.08, 0.09, ax, ay + 0.01), (0.07, 0.09, 0.098, ax, ay + 0.01),
                   (0.13, 0.086, 0.09, ax, ay + 0.004), (0.175, 0.084, 0.086, ax, ay), (0.19, 0.08, 0.082, ax, ay)],
                  BOOT, segs=18, name="boot_shaft", caps=(True, False))
    part(shaft, ("rigid", foot))
    toe_path = [V((ax, 0.07, 0.07)), V((ax, 0.02, 0.075)), V((ax, -0.05, 0.072)), V((ax, -0.11, 0.066)),
                V((ax, -0.155, 0.058)), V((ax, -0.185, 0.05)), V((ax, -0.198, 0.045))]
    toe_r = [(0.05, 0.085), (0.068, 0.095), (0.07, 0.098), (0.064, 0.097), (0.054, 0.09), (0.036, 0.072), (0.012, 0.035)]
    toe = tube(toe_path, toe_r, BOOT, segs=14, ref=(0, 0, 1), name="boot_toe")
    part(toe, ("rigid", foot))
    cuff = [V((ax + 0.087 * math.sin(math.radians(a)), ay - 0.089 * math.cos(math.radians(a)), 0.19)) for a in range(0, 360, 30)]
    part(tube(cuff, [0.02] * len(cuff), SUIT_PAD, segs=6, closed=True, fixed=True, ref=(0, 0, 1), name="boot_cuff"), ("rigid", foot))
    sole = rounded_box((0.215, 0.31, 0.05), (ax, -0.055, 0.025), SOLE, radius=0.02, segs=2, name="sole")
    part(sole, ("rigid", foot))
    strip = [V((ax + 0.112 * math.sin(math.radians(a)) * 0.98, -0.055 - 0.16 * math.cos(math.radians(a)), 0.03))
             for a in range(0, 360, 15)]
    # Squarish loop just proud of the sole's side.
    strip = []
    for a in range(0, 360, 18):
        r = math.radians(a)
        c, sn = math.cos(r), math.sin(r)
        k = 1.0 / (abs(c) ** 5 + abs(sn) ** 5) ** 0.2
        strip.append(V((ax + 0.109 * sn * k, -0.055 - 0.157 * c * k, 0.028)))
    part(tube(strip, [(0.006, 0.004)] * len(strip), CYAN_L, segs=4, closed=True, fixed=True, ref=(0, 0, 1),
              name="sole_light"), ("rigid", foot))
    # Lace strap across the instep with a chrome buckle.
    strap = [V((ax + 0.1 * math.sin(math.radians(a)), -0.05 - 0.075 * math.cos(math.radians(a)) + 0.0,
                0.075 + 0.058 * math.cos(math.radians(a)) ** 0.5 if abs(a) <= 90 else 0.075)) for a in range(-90, 91, 15)]
    part(tube(strap, [(0.004, 0.022)] * len(strap), SUIT_PAD, segs=4, ref=(0, 0, 1), caps=(True, True), name="boot_strap"),
         ("rigid", foot))
    part(rounded_box((0.03, 0.02, 0.026), V((ax + s * 0.075, -0.07, 0.11)), CHROME_M, radius=0.005, segs=1,
                     rot=(0, 0, 0), name="boot_buckle"), ("rigid", foot))


def build_arm(s):
    sd = SIDE[s]
    root = V((s * 0.16, 0.0, 0.765))
    path = [root, S[s], S[s].lerp(E[s], 0.5), E[s] + (S[s] - E[s]).normalized() * 0.03, E[s],
            E[s] + (WR[s] - E[s]).normalized() * 0.03, E[s].lerp(WR[s], 0.55), WR[s] + V((0, 0, 0.012))]
    radii = [0.066, 0.068, 0.064, 0.06, 0.059, 0.057, 0.054, 0.05]
    arm = tube(path, radii, SUIT, segs=12, name="arm_" + sd, ref=(0, -1, 0), caps=(True, True))
    part(arm, ("chain", ["shoulder_" + sd, "upper_arm_" + sd, "forearm_" + sd, "hand_" + sd],
               [root, S[s], E[s], WR[s], HT[s]], [0.03, 0.045, 0.02]))
    # Shoulder pad: a rubber dome over the joint.
    pad = prim("uv_sphere", SUIT_PAD, "shoulder_pad", segments=14, ring_count=8, radius=1.0)
    cut_below(pad, -0.15)
    d = (S[s] - E[s]).normalized()
    q = V((0, 0, 1)).rotation_difference((d + V((s * 0.6, 0, 0.9))).normalized())
    transform(pad, loc=S[s] + V((s * 0.012, 0, 0.012)), rot=q, scale=(0.088, 0.085, 0.07))
    part(pad, ("rigid", "upper_arm_" + sd))
    # Elbow pad on the back of the elbow.
    ep = prim("uv_sphere", SUIT_PAD, "elbow_pad", segments=10, ring_count=5, radius=1.0)
    transform(ep, loc=E[s] + V((s * 0.006, 0.038, 0)), scale=(0.05, 0.03, 0.052))
    part(ep, ("rigid", "forearm_" + sd))
    # Mitten glove: flared cuff, a padded palm, a thumb pointing forward.
    hand = "hand_" + sd
    wdir = (HT[s] - WR[s]).normalized()
    g = [WR[s] - wdir * 0.035, WR[s] - wdir * 0.005, WR[s] + wdir * 0.015, WR[s] + wdir * 0.04]
    cuff = tube(g, [0.056, 0.066, 0.068, 0.058], GLOVE, segs=14, ref=(1, 0, 0), caps=(False, False), name="glove_cuff")
    part(cuff, ("rigid", hand))
    mp = [WR[s] + wdir * t for t in (0.03, 0.055, 0.08, 0.105, 0.125, 0.14, 0.15)]
    mr = [(0.047, 0.056), (0.046, 0.064), (0.045, 0.068), (0.043, 0.066), (0.038, 0.058), (0.028, 0.044), (0.012, 0.02)]
    mit = tube(mp, mr, GLOVE, segs=14, ref=(1, 0, 0), name="mitten")
    part(mit, ("rigid", hand))
    t0 = WR[s] + wdir * 0.06 + V((-s * 0.012, -0.05, 0))
    t1 = t0 + V((-s * 0.004, -0.028, -0.03))
    t2 = t1 + V((0, -0.006, -0.02))
    th = tube([t0, t1, t2], [0.024, 0.023, 0.018], GLOVE, segs=10, name="thumb", cap_depth=0.012)
    part(th, ("rigid", hand))


# ------------------------------------------------------------------ head --
def build_head():
    # The glossy black bomb face (front half only; the helmet hides the rest).
    face = prim("uv_sphere", FACE, "face", segments=24, ring_count=12, radius=1.0)
    transform(face, loc=HC, scale=FR)
    cut_below(face, HC.y + 0.12, keep_above=False, axis=(0, 1, 0))
    part(face, ("rigid", "head"))

    # Helmet shell: loops that radiate from a rounded-rectangle face opening
    # to the back pole, so the rim has clean, concentric edge flow.
    Wo, Ho, z0, pw = 0.64, 0.40, -0.035, 3.0

    def sp(v, e):
        return math.copysign(abs(v) ** e, v)

    M, K = 40, 13
    edge = []
    for j in range(M):
        b = 2 * math.pi * j / M
        cx = Wo * sp(math.cos(b), 2 / pw)
        cz = z0 + Ho * sp(math.sin(b), 2 / pw)
        if cz < z0:
            cz = z0 + (cz - z0) * 1.08 + 0.05 * (1 - abs(cx / Wo)) ** 2 * 0   # flat chin line
        cy = -math.sqrt(max(0.0, 1 - cx * cx - cz * cz))
        edge.append(V((cx, cy, cz)).normalized())
    back = V((0, 1, 0))
    verts, faces = [], []
    for k in range(K):
        t = (k / K) ** 1.35
        for j in range(M):
            e = edge[j]
            om = math.acos(max(-1.0, min(1.0, e.dot(back))))
            d = (e * math.sin((1 - t) * om) + back * math.sin(t * om)) / math.sin(om)
            verts.append(ell_point(HC, HR, d))
    verts.append(ell_point(HC, HR, back))
    pole = len(verts) - 1
    for k in range(K - 1):
        for j in range(M):
            j2 = (j + 1) % M
            faces.append((k * M + j, k * M + j2, (k + 1) * M + j2, (k + 1) * M + j))
    for j in range(M):
        faces.append(((K - 1) * M + j, (K - 1) * M + (j + 1) % M, pole))
    shell = mesh_object("helmet", verts, faces, HELMET)
    fix_normals(shell, outward_from=HC)
    cut_below(shell, NECK_CUT)
    solidify(shell, 0.036, offset=-1.0, rim_mat=CYAN_L, bevel=0.007)     # a neon gasket round the face
    part(shell, ("rigid", "head"))
    decorate_helmet()

    # Neck roll: padding inside the helmet's bottom edge.
    rx, ry = HR[0] * math.sqrt(1 - ((HC.z - NECK_CUT) / HR[2]) ** 2), HR[1] * math.sqrt(1 - ((HC.z - NECK_CUT) / HR[2]) ** 2)
    ring = [V((HC.x + (rx - 0.03) * math.sin(math.radians(a)), HC.y - (ry - 0.03) * math.cos(math.radians(a)), NECK_CUT + 0.005))
            for a in range(0, 360, 20)]
    part(tube(ring, [(0.03, 0.036)] * len(ring), SUIT_PAD, segs=6, closed=True, fixed=True, ref=(0, 0, 1), name="neck_roll"),
         ("rigid", "head"))

    # Flipped-up smoked visor: a band over the forehead pivoting on hinges.
    tau = math.radians(47)
    VR = tuple(r + 0.028 for r in HR)

    def vdir(u, v):
        phi = (u * 2 - 1) * math.radians(84)
        w = math.radians(12.5) * (0.55 + 0.45 * math.cos(phi) ** 0.6)
        s_ = (v * 2 - 1) * w
        return V((math.sin(phi), -math.cos(phi) * math.cos(tau + s_), math.cos(phi) * math.sin(tau + s_)))
    visor = patch(HC, VR, vdir, 30, 3, VISOR, name="visor")
    solidify(visor, 0.014, offset=-1.0, rim_mat=CHROME_M, bevel=0.004)
    part(visor, ("rigid", "head"))

    # Hinges: chrome discs with a screw head and a cyan LED.
    for s in (1, -1):
        c = HC + V((s * (HR[0] + 0.012), 0.0, 0.0))
        rot = (0, math.pi / 2, 0)
        h = prim("cylinder", CHROME_M, "hinge", vertices=18, radius=0.078, depth=0.034)
        b = h.modifiers.new("bevel", "BEVEL")
        b.width, b.segments, b.limit_method = 0.01, 1, "ANGLE"
        apply_mods(h)
        transform(h, loc=c, rot=rot)
        part(h, ("rigid", "head"))
        h2 = prim("cylinder", NOZZLE, "hinge_cap", vertices=12, radius=0.048, depth=0.012)
        transform(h2, loc=c + V((s * 0.019, 0, 0)), rot=rot)
        part(h2, ("rigid", "head"))
        h3 = prim("cylinder", CYAN_L, "hinge_led", vertices=12, radius=0.024, depth=0.008)
        transform(h3, loc=c + V((s * 0.025, 0, 0)), rot=rot)
        part(h3, ("rigid", "head"))

    # Tail light across the back.
    tl = disc(HC, HR, (0, 1, -0.08), 0.46, 0.042, PINK_L, lift=0.003, dome=0.0, rings=1, segs=24, name="tail_light",
              shape=lambda a: 1.0 / (abs(math.cos(a)) ** 6 + abs(math.sin(a)) ** 6) ** (1 / 6))
    part(tl, ("rigid", "head"))

    # Face: eyes (rim, iris, core, two sparkles), blush and a cat smile.
    for s in (1, -1):
        d0 = V((s * 0.33, -0.94, 0.07)).normalized()
        up = V((0, 0, 1))
        U = (up - up.dot(d0) * d0).normalized()
        Ev = U.cross(d0).normalized()

        def at(dx, dy):
            return (d0 + Ev * dx + U * dy).normalized()
        eye = "eye_" + SIDE[s]
        tilt = -s * 0.10
        for m_, w, h, dx, dy, lift, dome, nm in (
                (EYE_RIM, 0.235, 0.300, 0.0, 0.0, 0.003, 0.010, "eye_rim"),
                (EYE, 0.205, 0.268, 0.0, 0.004, 0.006, 0.013, "eye_iris"),
                (EYE_CORE, 0.115, 0.150, 0.0, -0.045, 0.011, 0.012, "eye_core"),
                (SPARK, 0.060, 0.064, s * 0.075, 0.10, 0.018, 0.010, "spark_big"),
                (SPARK, 0.027, 0.027, -s * 0.07, -0.10, 0.018, 0.008, "spark_small")):
            o = disc(HC, FR, at(dx, dy), w, h, m_, lift=lift, dome=dome, rings=2, segs=20, name=nm, roll=tilt)
            part(o, ("rigid", eye))
        part(disc(HC, FR, (s * 0.62, -0.74, -0.30), 0.10, 0.052, BLUSH, lift=0.003, rings=1, segs=14, name="blush"),
             ("rigid", "head"))
    mouth = []
    for i in range(9):
        t = i / 8.0
        x = (t - 0.5) * 0.11
        z = -0.325 + 0.022 * abs(math.sin(t * 2 * math.pi)) * (-1) + 0.012
        d = V((x / FR[0], -1.0, z)).normalized()
        mouth.append(ell_point(HC, FR, d, 0.006))
    part(tube(mouth, [0.0095] * len(mouth), CYAN_L, segs=5, name="mouth", cap_depth=0.006), ("rigid", "head"))

    # Antenna: chrome collar, a springy rubber stalk and a glowing ball.
    base_d = V((0.30, 0.10, 0.95)).normalized()
    base = ell_point(HC, HR, base_d)
    nrm = ell_normal(HR, base_d)
    col = prim("cylinder", CHROME_M, "antenna_base", vertices=14, radius=0.036, depth=0.05)
    transform(col, loc=base + nrm * 0.005, rot=V((0, 0, 1)).rotation_difference(nrm))
    part(col, ("rigid", "head"))
    pts = [base + nrm * 0.02 + V((0.02 * i * i / 9.0, 0.0, 0.0)) + nrm * (0.075 * i) for i in range(4)]
    ANT.extend(pts)
    stalk = tube(pts, [0.014, 0.012, 0.011, 0.01], RUBBER, segs=8, name="antenna")
    part(stalk, ("chain", ["head", "antenna_1", "antenna_2", "antenna_3"], [pts[0] - nrm * 0.03] + pts,
                 [0.012, 0.02, 0.02]))
    for i, p in enumerate(pts[1:3]):
        r = prim("torus", CHROME_M, "antenna_ring", major_radius=0.016, minor_radius=0.005, major_segments=8, minor_segments=4)
        transform(r, loc=p, rot=V((0, 0, 1)).rotation_difference((pts[i + 2] - pts[i + 1]).normalized()))
        part(r, ("rigid", "antenna_%d" % (i + 1)))
    tip = pts[-1] + (pts[-1] - pts[-2]).normalized() * 0.04
    ball = prim("uv_sphere", PINK_L, "antenna_tip", segments=14, ring_count=8, radius=0.045)
    transform(ball, loc=tip)
    part(ball, ("rigid", "antenna_3"))


ANT = []


def decorate_suit():
    """Puffer-suit quilting across the torso, side seams, and a sole tread."""
    ex = Ex(SUIT)
    x, z = ex.x, ex.z
    torso = ex.smooth(0.20, 0.18, abs(x)) * ex.smooth(0.465, 0.49, z) * ex.smooth(0.80, 0.77, z)
    rib = abs(ex.sin((z - 0.47) * (math.pi / 0.066)))
    puff = ex.op("POWER", rib, 0.45)
    zip_gap = ex.smooth(0.012, 0.03, abs(x))
    ex.relief((puff - 1.0) * (torso * zip_gap * 0.012), 1.0)
    ex.darken(((1.0 - puff) * (1.0 - puff)) * (torso * zip_gap), 0.9)
    seam = ex.band(abs(x), 0.205, 0.003, 0.002) * ex.smooth(0.46, 0.5, z) * ex.smooth(0.72, 0.68, z)
    ex.relief(-seam * 0.004, 1.0)
    ex.darken(seam, 0.5)
    sole = Ex(SOLE)
    tread = sole.band((sole.y * (1 / 0.032)).frac(), 0.5, 0.22, 0.05) * sole.smooth(0.012, 0.004, sole.z)
    sole.relief(-tread * 0.004, 1.0)
    sole.darken(tread, 0.5)


def decorate_helmet():
    """Paint racing stripes, chin/brow vents and seams into the shell material."""
    ex = Ex(HELMET)
    x, y, z = ex.x, ex.y, ex.z
    behind = ex.smooth(HC.y - 0.30, HC.y - 0.18, y)                 # from the visor back
    over = ex.smooth(HC.z - 0.12, HC.z - 0.02, z)
    stripe = ex.band(x, 0.0, 0.045, 0.002) * behind * over
    pin = (ex.band(x, 0.078, 0.008, 0.0015) + ex.band(x, -0.078, 0.008, 0.0015)) * behind * over
    ex.paint(stripe, (0.92, 0.92, 0.95))
    ex.paint(pin, (0.05, 0.75, 0.9), rough=0.2)
    # Chin vents: three slots on the chin bar.
    front = ex.smooth(HC.y - 0.2, HC.y - 0.3, y)
    zc = HC.z - 0.265
    slots = (ex.band(x, 0.0, 0.035, 0.004) + ex.band(x, 0.1, 0.035, 0.004) + ex.band(x, -0.1, 0.035, 0.004)) * \
        ex.band(z, zc, 0.013, 0.004) * front
    ex.paint(slots, (0.02, 0.02, 0.025), rough=0.6)
    ex.relief(-slots * 0.004 - (stripe + pin) * 0.0008, 1.0)


# -------------------------------------------------------------- backpack --
def build_pack():
    PC = V((0.0, 0.255, 0.585))
    skin = ("rigid", "chest")
    body = rounded_box((0.33, 0.13, 0.28), PC, PACK, radius=0.05, segs=3, name="pack")
    part(body, skin)
    lid = rounded_box((0.30, 0.11, 0.06), PC + V((0, 0.012, 0.15)), PACK, radius=0.025, segs=2, name="pack_lid")
    part(lid, skin)
    # Vents: slats on the back face, a cyan status strip, chrome screws.
    for i in range(4):
        v = rounded_box((0.19, 0.016, 0.016), PC + V((0, 0.068, 0.045 - i * 0.034)), NOZZLE, radius=0.006, segs=1,
                        name="vent")
        part(v, skin)
    part(rounded_box((0.21, 0.006, 0.15), PC + V((0, 0.062, -0.005)), RUBBER, radius=0.004, segs=1, name="vent_bg"), skin)
    part(rounded_box((0.12, 0.012, 0.016), PC + V((0, 0.066, 0.11)), CYAN_L, radius=0.005, segs=1, name="pack_led"), skin)
    for sx in (-1, 1):
        for sz in (-1, 1):
            sc = prim("cylinder", CHROME_M, "screw", vertices=8, radius=0.011, depth=0.01)
            transform(sc, loc=PC + V((sx * 0.13, 0.066, 0.02 + sz * 0.085)), rot=(math.pi / 2, 0, 0))
            part(sc, skin)
    # Jet nozzles: bell-shaped, chrome lip, dark throat; flames on jet bones.
    for s in (1, -1):
        c = V((s * 0.105, 0.28, 0.0))
        bell = lathe([(0.475, 0.04, 0.04, c.x, c.y), (0.45, 0.046, 0.046, c.x, c.y), (0.425, 0.05, 0.05, c.x, c.y),
                      (0.40, 0.058, 0.058, c.x, c.y), (0.385, 0.064, 0.064, c.x, c.y)],
                     NOZZLE, segs=16, name="nozzle", caps=(False, True))
        part(bell, skin)
        lip = prim("torus", CHROME_M, "nozzle_lip", major_radius=0.062, minor_radius=0.008, major_segments=14, minor_segments=4)
        transform(lip, loc=(c.x, c.y, 0.385))
        part(lip, skin)
        throat = prim("cylinder", RUBBER, "throat", vertices=14, radius=0.05, depth=0.004)
        transform(throat, loc=(c.x, c.y, 0.392))
        part(throat, skin)
        jet = "jet_" + SIDE[s]
        outer = lathe([(0.39, 0.05, 0.05, c.x, c.y), (0.34, 0.058, 0.058, c.x, c.y), (0.28, 0.045, 0.045, c.x, c.y),
                       (0.21, 0.022, 0.022, c.x, c.y), (0.16, 0.004, 0.004, c.x, c.y)], FLAME, segs=12, name="flame",
                      caps=(True, True))
        part(outer, ("rigid", jet))
        inner = lathe([(0.392, 0.032, 0.032, c.x, c.y - 0.0), (0.35, 0.036, 0.036, c.x, c.y - 0.0),
                       (0.30, 0.024, 0.024, c.x, c.y - 0.0), (0.25, 0.003, 0.003, c.x, c.y - 0.0)],
                      FLAME_CORE, segs=10, name="flame_core", caps=(True, True))
        # Push the core slightly towards the camera so it reads through the outer cone.
        transform(inner, loc=(0, -0.012, 0))
        part(inner, ("rigid", jet))
    # Shoulder straps with chrome buckles.
    for s in (1, -1):
        pts = [V((s * 0.115, 0.215, 0.70)), V((s * 0.12, 0.17, 0.80)), V((s * 0.125, 0.09, 0.84)),
               V((s * 0.13, 0.0, 0.845))]
        for z in (0.82, 0.78, 0.73, 0.68, 0.62, 0.56):
            rx, ry, cy = torso_at(z)
            xx = s * 0.13
            yy = cy - ry * math.sqrt(max(0.0, 1 - (xx / rx) ** 2)) - 0.008
            pts.append(V((xx, yy, z)))
        st = tube(pts, [(0.021, 0.006)] * len(pts), BELT, segs=6, ref=(1, 0, 0), name="strap")
        part(st, TORSO_SKIN)
        bz = 0.70
        rx, ry, cy = torso_at(bz)
        yy = cy - ry * math.sqrt(max(0.0, 1 - (0.13 / rx) ** 2)) - 0.018
        part(rounded_box((0.056, 0.016, 0.04), V((s * 0.13, yy, bz)), CHROME_M, radius=0.007, segs=1, name="strap_buckle"),
             TORSO_SKIN)
    # Chest strap between the two shoulder straps.
    rx, ry, cy = torso_at(0.66)
    pts = [V((xx, cy - ry * math.sqrt(max(0.0, 1 - (xx / rx) ** 2)) - 0.01, 0.66)) for xx in [i * 0.026 - 0.13 for i in range(11)]]
    part(tube(pts, [(0.004, 0.013)] * len(pts), BELT, segs=6, ref=(0, -1, 0), name="chest_strap"), TORSO_SKIN)


# ----------------------------------------------------------------- scarf --
SCARF_J = [V((0.0, 0.165, 0.805)), V((0.01, 0.31, 0.795)), V((0.025, 0.455, 0.765)), V((0.04, 0.595, 0.71))]


def build_scarf():
    # The wrap: a thick, folded loop around the neck.
    pts = []
    for a in range(0, 360, 12):
        r = math.radians(a)
        pts.append(V((0.172 * math.sin(r), 0.004 - 0.156 * math.cos(r), 0.80 + 0.012 * math.cos(r))))
    wrap = tube(pts, [(0.046, 0.042)] * len(pts), SCARF, segs=8, closed=True, fixed=True, ref=(0, 0, 1), name="scarf_wrap",
                shape=lambda i, a: 1.0 + 0.10 * math.sin(3 * a + i * 1.3) * (0.5 + 0.5 * math.cos(a)))
    part(wrap, ("rigid", "chest"))
    knot = prim("uv_sphere", SCARF, "scarf_knot", segments=12, ring_count=8, radius=1.0)
    transform(knot, loc=(0.0, 0.165, 0.80), scale=(0.06, 0.05, 0.055))
    part(knot, ("rigid", "chest"))
    # Two tails streaming back, with twists and folds.
    for k, (dx, dz, ln, w0) in enumerate(((0.03, 0.0, 1.0, 0.052), (-0.035, -0.035, 0.8, 0.046))):
        n = 10
        pts, radii = [], []
        for i in range(n + 1):
            t = i / n * ln
            # Walk the scarf bone chain.
            seg = min(int(t * 3), 2)
            f = t * 3 - seg
            p = SCARF_J[seg].lerp(SCARF_J[seg + 1], f) if t < 1 else SCARF_J[3]
            p = p + V((dx + 0.02 * math.sin(t * 7 + k), 0, dz + 0.012 * math.sin(t * 9 + k * 2)))
            pts.append(p)
            w = w0 * (1.0 - 0.25 * t) * (1 + 0.12 * math.sin(t * 11))
            radii.append((0.009, w) if i < n else (0.006, w * 0.35))
        tail = tube(pts, radii, SCARF, segs=8, ref=(0, 0, 1), name="scarf_tail", start=math.pi / 8,
                    shape=lambda i, a: 1.0)
        # Twist the ribbon a little along its length.
        part(tail, ("chain", ["chest", "scarf_1", "scarf_2", "scarf_3"], [SCARF_J[0] - V((0, 0.05, 0))] + SCARF_J,
                    [0.03, 0.05, 0.05]))


# ------------------------------------------------------------------- rig --
def rig_bones():
    FWD, UP = (0, -1, 0), (0, 0, 1)
    b = [("root", (0, 0, 0), (0, 0, 0.12), None, FWD),
         ("hips", (0, 0, 0.40), (0, 0, 0.52), "root", FWD),
         ("spine", (0, 0, 0.52), (0, 0, 0.66), "hips", FWD),
         ("chest", (0, 0, 0.66), (0, 0, 0.84), "spine", FWD),
         ("neck", (0, 0, 0.84), (0, 0, 0.92), "chest", FWD),
         ("head", (0, 0, 0.92), (0, 0, 1.45), "neck", FWD)]
    for s in (1, -1):
        sd = SIDE[s]
        d0 = V((s * 0.33, -0.94, 0.07)).normalized()
        ec = ell_point(HC, FR, d0)
        b += [("eye_" + sd, tuple(ec), tuple(ec + V((0, 0, 0.1))), "head", FWD),
              ("shoulder_" + sd, (s * 0.06, 0, 0.765), tuple(S[s]), "chest", FWD),
              # Arm bones hang straight down (the mesh is in an A-pose): a
              # swing about their x is then a pure forward/back swing that
              # keeps the arms splayed clear of the belly and the helmet.
              ("upper_arm_" + sd, tuple(S[s]), tuple(S[s] - V((0, 0, 0.14))), "shoulder_" + sd, FWD),
              ("forearm_" + sd, tuple(E[s]), tuple(E[s] - V((0, 0, 0.12))), "upper_arm_" + sd, FWD),
              ("hand_" + sd, tuple(WR[s]), tuple(WR[s] - V((0, 0, 0.10))), "forearm_" + sd, FWD),
              ("thigh_" + sd, tuple(HIP[s]), tuple(KNEE[s]), "hips", FWD),
              ("shin_" + sd, tuple(KNEE[s]), tuple(ANK[s]), "thigh_" + sd, FWD),
              ("foot_" + sd, tuple(ANK[s]), tuple(TOE[s]), "shin_" + sd, UP),
              ("jet_" + sd, (s * 0.105, 0.28, 0.39), (s * 0.105, 0.28, 0.20), "chest", FWD)]
    for i in range(3):
        b.append(("antenna_%d" % (i + 1), tuple(ANT[i]), tuple(ANT[i + 1]), "head" if i == 0 else "antenna_%d" % i, FWD))
    for i in range(3):
        b.append(("scarf_%d" % (i + 1), tuple(SCARF_J[i]), tuple(SCARF_J[i + 1]), "chest" if i == 0 else "scarf_%d" % i, UP))
    return b


# Atlas share per part (see hero_kit.bake_hero): what the camera sees most
# gets the most texels; hidden faces get very few.
UV_WEIGHT = {"helmet": 1.7, "torso": 1.3, "mitten": 1.3, "glove_cuff": 1.2, "face": 0.35, "visor": 0.8,
             "screw": 0.4, "snap": 0.4, "antenna_ring": 0.4, "antenna_base": 0.5, "hinge_cap": 0.6,
             "throat": 0.3, "sole": 0.6, "neck_roll": 0.5, "nozzle": 0.7, "vent": 0.6, "vent_bg": 0.5}


def uv_weight(o, nm):
    attr = o.data.attributes.new("uv_weight", "FLOAT", "FACE")
    base = UV_WEIGHT.get(nm, 1.0)
    vals = []
    for p in o.data.polygons:
        w = base
        if nm == "helmet" and p.normal.dot(p.center - HC) < 0:
            w = 0.25                    # the inside of the shell
        vals.append(w)
    attr.data.foreach_set("value", vals)


def skin_and_join(arm):
    objs = []
    cnt = {}
    for o, spec in PARTS:
        apply_mods(o)
        nm = o.name.split(".")[0]
        cnt[nm] = cnt.get(nm, 0) + tris(o)
        uv_weight(o, nm)
        if spec[0] == "rigid":
            weigh_rigid(o, spec[1])
        else:
            weigh_chain(o, spec[1], spec[2], spec[3])
        objs.append(o)
    select_only(objs[0])
    for o in objs:
        o.select_set(True)
    print("TRIS_BY_PART", sorted(cnt.items(), key=lambda kv: -kv[1]))
    bpy.ops.object.join()
    hero = bpy.context.object
    hero.name = "hero"
    hero.parent = arm
    md = hero.modifiers.new("skin", "ARMATURE")
    md.object = arm
    return hero


# ------------------------------------------------------------------ main --
decorate_suit()
build_torso()
for s in (1, -1):
    build_leg(s)
    build_arm(s)
build_head()
build_pack()
build_scarf()
arm = build_armature(rig_bones())
hero = skin_and_join(arm)
print("HERO_TRIS", tris(hero), "VERTS", len(hero.data.vertices), "BONES", len(arm.data.bones))

STAGE = os.environ.get("HERO_STAGE", "full")
if STAGE == "model":
    out = PREVIEW or "/tmp"
    shoot(os.path.join(out, "player_front.png"), yaw_deg=0, target=(0, 0, 0.85), dist=4.0, size=512, samples=32)
    shoot(os.path.join(out, "player_34.png"), yaw_deg=40, target=(0, 0, 0.85), dist=4.0, size=512, samples=32)
    shoot(os.path.join(out, "player_back.png"), yaw_deg=150, target=(0, 0, 0.85), dist=4.0, size=512, samples=32)
    shoot(os.path.join(out, "player_face.png"), yaw_deg=20, target=(0, 0, 1.15), dist=2.2, size=512, samples=32)
    sys.exit(0)

# ------------------------------------------------------ bake, clips, export --
import hero_clips  # noqa: E402

JETS = ("jet_l", "jet_r")


def jets(scale):
    for j in JETS:
        arm.pose.bones[j].scale = (scale, scale, scale)
    bpy.context.view_layer.update()


jets(0.001)                     # no flames in the AO bake
if os.environ.get("NO_BAKE") != "1":
    bake_hero("player", tex=int(os.environ.get("BAKE_TEX", 0)) or 1024)
jets(1.0)
hero_clips.author_all(arm)
export("player", bake=False)
if os.environ.get("HERO_DEBUG"):
    exec(open(os.environ["HERO_DEBUG"]).read())

if PREVIEW:
    jets(0.001)
    show_clip(arm, "idle", 0)
    shoot(os.path.join(PREVIEW, "player.png"), yaw_deg=32, target=(0, 0, 0.82), dist=4.0, size=640, samples=48)
    shoot(os.path.join(PREVIEW, "player_face.png"), yaw_deg=18, target=(0, 0, 1.12), dist=2.1, size=512, samples=48)
    shoot(os.path.join(PREVIEW, "player_back.png"), yaw_deg=150, target=(0, 0, 0.82), dist=4.0, size=384, samples=32)
    if os.environ.get("HERO_SHEET", "1") != "0":
        sheet = [("idle", (0, 40, 70)), ("run_loop", (0, 2, 5, 7, 10, 15)), ("jump", (4,)), ("rise_loop", (0,)),
                 ("fall_loop", (0, 12)), ("land", (2, 7)), ("push_loop", (0, 8, 15)), ("hurt", (3,)),
                 ("death", (4, 13, 18, 23, 29, 36)), ("wave", (12,))]
        only = os.environ.get("HERO_CLIPS")
        paths, labels = [], []
        for clip, frames in sheet:
            if only and clip not in only.split(","):
                continue
            for f in frames:
                show_clip(arm, clip, f)
                if clip in ("jump", "rise_loop"):
                    jets(1.0)
                else:
                    jets(0.001)
                p = os.path.join(PREVIEW, "_pose_%s_%02d.png" % (clip, f))
                shoot(p, yaw_deg=float(os.environ.get("HERO_YAW", 60)), target=(0, 0, 0.75), dist=3.5, size=256,
                      samples=int(os.environ.get("HERO_SAMPLES", 16)))
                paths.append(p)
                labels.append("%s %d" % (clip, f))
        montage(paths, os.path.join(PREVIEW, "player_sheet.png"), cols=6, labels=labels)
        for p in paths:
            os.remove(p)
    unmute_all(arm)
