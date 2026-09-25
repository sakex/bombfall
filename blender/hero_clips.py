# The hero's authored clips (30 fps). Poses are bone -> (x, y, z) degrees in
# the bone's local axes with semantic signs (see hero_kit.author):
#   thigh/upper_arm/spine/chest/neck/head/antenna  +x = tip swings forward
#   shin  -x = knee bends          forearm +x = elbow bends
#   foot  +x = toes up             hand    -x = wrist bends back
#   limbs +z = outwards            spine/neck/head +y = turn to its left
#   scarf +x = tail lifts, +z = tail swings to the character's right
#   "hips@" = hips offset in metres (x, y, z world; -y is forward)
import math

from hero_kit import author

TAU = 2 * math.pi
THIGH, SHIN = 0.135, 0.125


def _merge(*poses):
    out = {}
    for p in poses:
        for k, v in p.items():
            if k in out and k != "hips@":
                out[k] = tuple(a + b for a, b in zip(out[k], v))
            else:
                out[k] = v
    return out


def both(bone, x=0.0, y=0.0, z=0.0):
    return {bone + "_l": (x, y, z), bone + "_r": (x, y, z)}


def crouch_drop(thigh_deg, shin_deg):
    """How far the hips drop for a leg bend with the foot kept on the floor."""
    a, b = math.radians(thigh_deg), math.radians(thigh_deg + shin_deg)
    return (THIGH + SHIN) - (THIGH * math.cos(a) + SHIN * math.cos(b))


REST_ARMS = _merge(both("upper_arm", 0, 0, -6), both("forearm", 12), both("hand", 4))


# ------------------------------------------------------------------ idle --
def idle(arm):
    n = 120
    poses = []
    for f in range(0, n + 1, 5):
        t = f / n
        br = math.sin(TAU * 2 * t)                      # two breaths
        sway = math.cos(TAU * t)                        # one weight shift
        # Look around: left at ~35%, right at ~75%.
        look = 24 * math.exp(-((t - 0.36) / 0.10) ** 2) - 20 * math.exp(-((t - 0.76) / 0.09) ** 2)
        nod = -5 * math.exp(-((t - 0.36) / 0.10) ** 2) + 4 * math.exp(-((t - 0.56) / 0.05) ** 2)
        ant = math.sin(TAU * 2 * t - 0.9)
        p = _merge(REST_ARMS, {
            "hips@": (0.012 * sway, 0.0, -0.004 - 0.004 * br),
            "hips": (0, 0, 2.2 * sway),
            "spine": (1.0 + 0.5 * br, 0, -1.6 * sway),
            "chest": (-1.8 * br, look * 0.15, -0.6 * sway),
            "neck": (-1.0 + nod * 0.4, look * 0.3, 0),
            "head": (nod, look * 0.55, 3.0 * sway + look * 0.08),
            "shoulder_l": (0, 0, 2.5 * br), "shoulder_r": (0, 0, 2.5 * br),
            "upper_arm_l": (3 * br - 2 * sway, 0, -6 - 2 * br), "upper_arm_r": (3 * br + 2 * sway, 0, -6 - 2 * br),
            "forearm_l": (14 + 3 * sway, 0, 0), "forearm_r": (14 - 3 * sway, 0, 0),
            "thigh_l": (0, 0, -2.2 * sway), "thigh_r": (0, 0, 2.2 * sway),
            "foot_l": (0, 0, 0), "foot_r": (0, 0, 0),
            "antenna_1": (3 + 4 * ant, 0, -look * 0.12), "antenna_2": (2 + 4 * math.sin(TAU * 2 * t - 1.6), 0, -look * 0.15),
            "antenna_3": (2 + 4 * math.sin(TAU * 2 * t - 2.3), 0, -look * 0.15),
            "scarf_1": (-10 + 2 * br, 0, 12 + 4 * sway), "scarf_2": (-45 + 4 * math.sin(TAU * 2 * t - 1), 0, 6),
            "scarf_3": (-25 + 5 * math.sin(TAU * 2 * t - 2), 0, 4),
        })
        poses.append((f, p))
    author(arm, "idle", poses, loop=True)


# ------------------------------------------------------------------- run --
def _leg_run(ph):
    """(thigh, shin, foot) x-rotations for one leg; ph = 0 at its heel strike."""
    ph %= TAU
    thigh = 46 * math.cos(ph) + 6
    st = 0.8 * math.pi
    if ph < st:
        u = ph / st
        shin = -12 - 30 * math.sin(math.pi * u)
        foot = 14 * max(0.0, 1 - u / 0.3) - 34 * max(0.0, (u - 0.45) / 0.55) ** 1.5
    else:
        u = (ph - st) / (TAU - st)
        shin = -12 - 112 * math.sin(math.pi * u ** 0.75)
        foot = -34 + 48 * u
    return thigh, shin, foot


def run(arm):
    n = 20
    poses = []
    for f in range(n + 1):
        ph = TAU * f / n
        tl, sl, fl = _leg_run(ph)
        tr, sr, fr = _leg_run(ph + math.pi)
        bob = math.cos(2 * ph - 0.4 * math.pi)          # low at the down poses
        c = math.cos(ph)
        p = {
            "hips@": (0, 0, 0.010 - 0.022 * bob),
            "hips": (4, -9 * c, 3 * math.sin(ph)),
            "spine": (16 + 3 * bob, 0, 0),
            "chest": (4, 12 * c, -2 * math.sin(ph)),
            "neck": (-6, -2 * c, 0),
            "head": (-12 - 3 * bob, -1 * c, 0),
            "thigh_l": (tl, 0, -2), "shin_l": (sl, 0, 0), "foot_l": (fl, 0, 0),
            "thigh_r": (tr, 0, -2), "shin_r": (sr, 0, 0), "foot_r": (fr, 0, 0),
            "shoulder_l": (-8 * c, 0, 2), "shoulder_r": (8 * c, 0, 2),
            "upper_arm_l": (-66 * c + 4, 0, -10), "upper_arm_r": (66 * c + 4, 0, -10),
            "forearm_l": (78 - 18 * c, 0, 0), "forearm_r": (78 + 18 * c, 0, 0),
            "hand_l": (10, 0, 0), "hand_r": (10, 0, 0),
            "antenna_1": (-10 - 5 * math.cos(2 * ph - 2.0), 0, 3 * math.sin(ph)),
            "antenna_2": (-8 - 5 * math.cos(2 * ph - 2.8), 0, 3 * math.sin(ph - 0.6)),
            "antenna_3": (-6 - 5 * math.cos(2 * ph - 3.5), 0, 3 * math.sin(ph - 1.2)),
            "scarf_1": (4 + 6 * math.sin(2 * ph), 0, 6 * math.sin(ph)),
            "scarf_2": (-4 + 9 * math.sin(2 * ph - 1.3), 0, 6 * math.sin(ph - 0.8)),
            "scarf_3": (-2 + 12 * math.sin(2 * ph - 2.5), 0, 8 * math.sin(ph - 1.6)),
        }
        poses.append((f, p))
    author(arm, "run_loop", poses, loop=True)


# ------------------------------------------------------------------ jump --
JUMP_POSE = {
    "hips@": (0, 0, 0.02),
    "hips": (2, 6, 0), "spine": (4, 0, 0), "chest": (-2, -8, 0), "neck": (-2, 0, 0), "head": (-8, 0, 0),
    "thigh_l": (72, 0, 4), "shin_l": (-104, 0, 0), "foot_l": (14, 0, 0),
    "thigh_r": (-26, 0, 2), "shin_r": (-24, 0, 0), "foot_r": (-42, 0, 0),
    "shoulder_l": (-6, 0, 6), "shoulder_r": (10, 0, 14),
    "upper_arm_l": (112, 0, 16), "upper_arm_r": (146, 0, 22),
    "forearm_l": (40, 0, 0), "forearm_r": (22, 0, 0), "hand_l": (-10, 0, 0), "hand_r": (-12, 0, 0),
    "antenna_1": (-18, 0, 0), "antenna_2": (-12, 0, 0), "antenna_3": (-8, 0, 0),
    "scarf_1": (-35, 0, 0), "scarf_2": (-18, 0, 0), "scarf_3": (-10, 0, 0),
}


def _scale(pose, k):
    return {b: (tuple(a * k for a in v)) for b, v in pose.items()}


def jump(arm):
    author(arm, "jump", [(0, _scale(JUMP_POSE, 0.7)), (4, JUMP_POSE),
                         (8, _merge(JUMP_POSE, {"upper_arm_l": (8, 0, 0), "thigh_l": (4, 0, 0), "antenna_1": (6, 0, 0)}))])


def rise(arm):
    n = 30
    poses = []
    for f in range(0, n + 1, 3):
        ph = TAU * f / n
        s = math.sin(ph)
        p = {
            "hips@": (0, 0, 0.01),
            "hips": (4, 5, 2 * s), "spine": (2, 0, 0), "chest": (-2, -6, -1.5 * s), "neck": (-2, 0, 0),
            "head": (-8 + 2 * s, 0, 2 * s),
            "thigh_l": (78 + 4 * s, 0, 6), "shin_l": (-112 - 4 * s, 0, 0), "foot_l": (14, 0, 0),
            "thigh_r": (26 - 5 * s, 0, 4), "shin_r": (-64 + 6 * s, 0, 0), "foot_r": (-24, 0, 0),
            "shoulder_l": (0, 0, 8), "shoulder_r": (8, 0, 14),
            "upper_arm_l": (120 + 6 * s, 0, 18), "upper_arm_r": (148 - 5 * s, 0, 22),
            "forearm_l": (30, 0, 0), "forearm_r": (18, 0, 0), "hand_l": (-10, 0, 0), "hand_r": (-14, 0, 0),
            "antenna_1": (-16 + 3 * math.sin(2 * ph), 0, 0), "antenna_2": (-10 + 3 * math.sin(2 * ph - 1), 0, 0),
            "antenna_3": (-6 + 3 * math.sin(2 * ph - 2), 0, 0),
            "scarf_1": (-42 + 5 * math.sin(2 * ph), 0, 4 * s), "scarf_2": (-18 + 8 * math.sin(2 * ph - 1.2), 0, 5 * s),
            "scarf_3": (-10 + 10 * math.sin(2 * ph - 2.4), 0, 6 * s),
        }
        poses.append((f, p))
    author(arm, "rise_loop", poses, loop=True)


def fall(arm):
    n = 24
    poses = []
    for f in range(0, n + 1, 2):
        ph = TAU * f / n
        s, c = math.sin(ph), math.cos(ph)
        p = {
            "hips@": (0, 0, 0.0),
            "hips": (-4, 4 * s, 0), "spine": (2, 0, 3 * c), "chest": (0, -4 * s, 0), "neck": (4, 0, 0),
            "head": (4 + 3 * math.sin(2 * ph), 6 * s, -4 * c),
            "thigh_l": (28 + 26 * s, 0, 8), "shin_l": (-40 - 30 * math.sin(ph + 1.3), 0, 0), "foot_l": (-20, 0, 0),
            "thigh_r": (28 - 26 * s, 0, 8), "shin_r": (-40 + 30 * math.sin(ph + 1.3), 0, 0), "foot_r": (-20, 0, 0),
            "shoulder_l": (0, 0, 14), "shoulder_r": (0, 0, 14),
            "upper_arm_l": (92 + 30 * s, 0, 34), "upper_arm_r": (92 - 30 * s, 0, 34),
            "forearm_l": (26 + 24 * math.sin(ph + 1.0), 0, 0), "forearm_r": (26 - 24 * math.sin(ph + 1.0), 0, 0),
            "hand_l": (0, 0, 14 * s), "hand_r": (0, 0, -14 * s),
            "antenna_1": (6 + 5 * math.sin(2 * ph), 0, 4 * c), "antenna_2": (4 + 5 * math.sin(2 * ph - 1), 0, 4 * c),
            "antenna_3": (4 + 5 * math.sin(2 * ph - 2), 0, 4 * c),
            "scarf_1": (55 + 6 * math.sin(2 * ph), 0, 6 * s), "scarf_2": (22 + 10 * math.sin(2 * ph - 1.2), 0, 8 * s),
            "scarf_3": (12 + 14 * math.sin(2 * ph - 2.4), 0, 10 * s),
        }
        poses.append((f, p))
    author(arm, "fall_loop", poses, loop=True)


def _squat(thigh, shin, extra=None):
    p = {
        "hips@": (0, 0, -crouch_drop(thigh, shin)),
        "thigh_l": (thigh, 0, 4), "shin_l": (shin, 0, 0), "foot_l": (-(thigh + shin), 0, 0),
        "thigh_r": (thigh, 0, 4), "shin_r": (shin, 0, 0), "foot_r": (-(thigh + shin), 0, 0),
    }
    return _merge(p, extra or {})


def land(arm):
    squash = _squat(62, -108, _merge(REST_ARMS, {
        "spine": (22, 0, 0), "chest": (6, 0, 0), "neck": (-6, 0, 0), "head": (-12, 0, 0),
        "upper_arm_l": (40, 0, 44), "upper_arm_r": (40, 0, 44), "forearm_l": (30, 0, 0), "forearm_r": (30, 0, 0),
        "antenna_1": (24, 0, 0), "antenna_2": (14, 0, 0), "antenna_3": (8, 0, 0),
        "scarf_1": (10, 0, 0), "scarf_2": (-20, 0, 0), "scarf_3": (-10, 0, 0)}))
    mid = _squat(20, -38, _merge(REST_ARMS, {
        "spine": (6, 0, 0), "head": (-4, 0, 0), "upper_arm_l": (8, 0, 14), "upper_arm_r": (8, 0, 14),
        "antenna_1": (-10, 0, 0), "antenna_2": (-8, 0, 0), "antenna_3": (-4, 0, 0),
        "scarf_1": (-6, 0, 8), "scarf_2": (-40, 0, 4), "scarf_3": (-20, 0, 0)}))
    rest = _merge(REST_ARMS, {"hips@": (0, 0, -0.004), "spine": (1, 0, 0), "forearm_l": (14, 0, 0),
                              "forearm_r": (14, 0, 0), "antenna_1": (3, 0, 0), "antenna_2": (2, 0, 0),
                              "antenna_3": (2, 0, 0), "scarf_1": (-10, 0, 12), "scarf_2": (-45, 0, 6),
                              "scarf_3": (-25, 0, 4)})
    author(arm, "land", [(0, squash), (3, squash), (7, mid), (12, rest)])


# ------------------------------------------------------------------ push --
def push(arm):
    n = 30
    poses = []
    for f in range(n + 1):
        ph = TAU * f / n
        # Two short steps per loop; each foot slides back while planted.
        def leg(p):
            p %= TAU
            if p < 1.2 * math.pi:           # planted, pushing back
                u = p / (1.2 * math.pi)
                return 6 - 34 * u, -20 - 6 * math.sin(math.pi * u), 20 + 6 * u
            u = (p - 1.2 * math.pi) / (0.8 * math.pi)
            return -28 + 34 * u, -26 - 44 * math.sin(math.pi * u), 26 - 6 * u
        tl, sl, fl = leg(ph)
        tr, sr, fr = leg(ph + math.pi)
        shove = math.cos(2 * ph)
        p = {
            "hips@": (0, -0.03, -0.035 + 0.008 * shove),
            "hips": (12, -4 * math.cos(ph), 2 * math.sin(ph)),
            "spine": (18, 0, 0), "chest": (8 + 2 * shove, 4 * math.cos(ph), 0), "neck": (-10, 0, 0),
            "head": (-22 - 2 * shove, 0, 2 * math.sin(ph)),
            "thigh_l": (tl, 0, 3), "shin_l": (sl, 0, 0), "foot_l": (fl, 0, 0),
            "thigh_r": (tr, 0, 3), "shin_r": (sr, 0, 0), "foot_r": (fr, 0, 0),
            "shoulder_l": (12, 0, 4), "shoulder_r": (12, 0, 4),
            "upper_arm_l": (122 - 4 * shove, 0, -8), "upper_arm_r": (122 - 4 * shove, 0, -8),
            "forearm_l": (6 + 6 * shove, 0, 0), "forearm_r": (6 + 6 * shove, 0, 0),
            "hand_l": (-60, 0, 0), "hand_r": (-60, 0, 0),
            "antenna_1": (-6 + 3 * shove, 0, 0), "antenna_2": (-4 + 3 * shove, 0, 0), "antenna_3": (-2, 0, 0),
            "scarf_1": (-8, 0, 10 + 4 * math.sin(ph)), "scarf_2": (-35 + 5 * math.sin(2 * ph), 0, 6),
            "scarf_3": (-20 + 6 * math.sin(2 * ph - 1), 0, 4),
        }
        poses.append((f, p))
    author(arm, "push_loop", poses, loop=True)


# ------------------------------------------------------------ hurt/death --
def hurt(arm):
    flinch = _merge(_squat(18, -30), {
        "hips@": (0, 0.03, -0.02),
        "spine": (-10, 0, 6), "chest": (-6, 6, 0), "neck": (-2, 0, 0), "head": (-6, -8, 12),
        "shoulder_l": (0, 0, 18), "shoulder_r": (0, 0, 18),
        "upper_arm_l": (62, 0, 28), "upper_arm_r": (70, 0, 24), "forearm_l": (100, 0, 0), "forearm_r": (95, 0, 0),
        "hand_l": (-20, 0, 0), "hand_r": (-20, 0, 0),
        "antenna_1": (-30, 0, 10), "antenna_2": (-18, 0, 8), "antenna_3": (-10, 0, 6),
        "scarf_1": (20, 0, 0), "scarf_2": (-10, 0, 0), "scarf_3": (-5, 0, 0)})
    back = _merge(REST_ARMS, {"spine": (5, 0, -2), "head": (4, 0, -4), "antenna_1": (14, 0, -4),
                              "antenna_2": (8, 0, 0), "scarf_1": (-8, 0, 8), "scarf_2": (-40, 0, 4),
                              "scarf_3": (-22, 0, 0)})
    rest = _merge(REST_ARMS, {"antenna_1": (3, 0, 0), "scarf_1": (-10, 0, 12), "scarf_2": (-45, 0, 6),
                              "scarf_3": (-25, 0, 4), "forearm_l": (14, 0, 0), "forearm_r": (14, 0, 0)})
    author(arm, "hurt", [(0, _scale(flinch, 0.3)), (2, flinch), (5, flinch), (9, back), (14, rest)])


def death(arm):
    jolt = {
        "hips@": (0, 0.02, 0.08),
        "spine": (-18, 0, 0), "chest": (-8, 0, 0), "neck": (-6, 0, 0), "head": (-18, 0, 0),
        "shoulder_l": (0, 0, 16), "shoulder_r": (0, 0, 16),
        "upper_arm_l": (40, 0, 70), "upper_arm_r": (36, 0, 74), "forearm_l": (20, 0, 0), "forearm_r": (26, 0, 0),
        "hand_l": (-20, 0, 0), "hand_r": (-20, 0, 0),
        "thigh_l": (-6, 0, 6), "shin_l": (-8, 0, 0), "foot_l": (-30, 0, 0),
        "thigh_r": (12, 0, 6), "shin_r": (-20, 0, 0), "foot_r": (-24, 0, 0),
        "antenna_1": (-35, 0, 0), "antenna_2": (-20, 0, 0), "antenna_3": (-12, 0, 0),
        "scarf_1": (30, 0, 0), "scarf_2": (10, 0, 0), "scarf_3": (5, 0, 0),
    }
    wobble = _merge(_squat(14, -24), REST_ARMS, {
        "spine": (4, 0, 10), "chest": (0, 0, 6), "head": (8, 10, -16),
        "upper_arm_l": (-6, 0, 20), "upper_arm_r": (0, 0, 8),
        "antenna_1": (18, 0, 20), "antenna_2": (10, 0, 12), "antenna_3": (8, 0, 8),
        "scarf_1": (-10, 0, 0), "scarf_2": (-30, 0, 0)})
    wobble2 = _merge(wobble, {"spine": (0, 0, -18), "chest": (0, 0, -6), "head": (0, -18, 30),
                              "antenna_1": (0, 0, -40), "antenna_2": (0, 0, -24)})
    buckle = _merge(_squat(62, -112), REST_ARMS, {
        "spine": (12, 0, -4), "chest": (4, 0, 0), "head": (16, -6, 8),
        "upper_arm_l": (-10, 0, 10), "upper_arm_r": (-10, 0, 10),
        "antenna_1": (20, 0, 0), "antenna_2": (14, 0, 0), "antenna_3": (10, 0, 0),
        "scarf_1": (10, 0, 0), "scarf_2": (-20, 0, 0)})
    sit = {
        "hips@": (0, 0.0, -0.24),
        "hips": (-10, 0, 0), "spine": (4, 0, 0), "chest": (2, 0, 0), "head": (6, 14, 14),
        "thigh_l": (84, 0, 14), "shin_l": (-24, 0, 0), "foot_l": (10, 0, 0),
        "thigh_r": (80, 0, 16), "shin_r": (-34, 0, 0), "foot_r": (14, 0, 0),
        "upper_arm_l": (0, 0, 30), "upper_arm_r": (0, 0, 32), "forearm_l": (20, 0, 0), "forearm_r": (20, 0, 0),
        "antenna_1": (30, 0, 10), "antenna_2": (20, 0, 8), "antenna_3": (14, 0, 6),
        "scarf_1": (-6, 0, 10), "scarf_2": (-40, 0, 0), "scarf_3": (-20, 0, 0),
    }
    flop = {
        "hips@": (0, 0.02, -0.25),
        "hips": (-62, 0, 0), "spine": (-8, 0, 0), "chest": (-4, 0, 0), "neck": (0, 0, 0), "head": (14, 10, 10),
        "thigh_l": (110, 0, 22), "shin_l": (-24, 0, 0), "foot_l": (8, 0, 0),
        "thigh_r": (104, 0, 26), "shin_r": (-34, 0, 0), "foot_r": (10, 0, 0),
        "shoulder_l": (0, 0, 10), "shoulder_r": (0, 0, 10),
        "upper_arm_l": (20, 0, 84), "upper_arm_r": (26, 0, 80), "forearm_l": (14, 0, 0), "forearm_r": (20, 0, 0),
        "antenna_1": (-40, 0, 0), "antenna_2": (-24, 0, 0), "antenna_3": (-16, 0, 0),
        "scarf_1": (30, 0, 20), "scarf_2": (-10, 0, 0), "scarf_3": (-10, 0, 0),
    }
    settle = _merge(flop, {"hips@": (0, 0.02, -0.25), "hips": (-6, 0, 0), "thigh_l": (-24, 0, -6),
                           "thigh_r": (-18, 0, -8), "shin_l": (4, 0, 0), "shin_r": (10, 0, 0),
                           "upper_arm_l": (0, 0, 6), "upper_arm_r": (0, 0, 4),
                           "antenna_1": (-16, 0, 0), "antenna_2": (-18, 0, 0), "antenna_3": (-14, 0, 0),
                           "head": (-4, 4, 4)})
    author(arm, "death", [(0, {}), (4, jolt), (8, wobble), (13, wobble2), (18, buckle), (23, sit), (29, flop),
                          (36, settle)])


def wave(arm):
    base = _merge(REST_ARMS, {"hips": (0, 0, 3), "spine": (-2, 0, -3), "head": (-4, 10, 10)})
    poses = [(0, _merge(REST_ARMS, {}))]
    up = _merge(base, {"shoulder_r": (0, 0, 16), "upper_arm_r": (10, 0, 108), "forearm_r": (10, 0, 0),
                       "hand_r": (0, 0, 0), "antenna_1": (8, 0, -6)})
    for i, f in enumerate(range(6, 44, 6)):
        z = 28 if i % 2 == 0 else -18
        poses.append((f, _merge(up, {"forearm_r": (0, 0, z), "hand_r": (0, 0, z * 0.4),
                                     "antenna_1": (0, 0, z * 0.3 - 6), "antenna_2": (0, 0, z * 0.3)})))
    poses.append((52, _merge(REST_ARMS, {})))
    author(arm, "wave", poses)


ALL = [idle, run, jump, rise, fall, land, push, hurt, death, wave]


def author_all(arm):
    for fn in ALL:
        fn(arm)
