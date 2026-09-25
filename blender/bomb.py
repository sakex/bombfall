# The bomb: a machined steel drum mine, radius 1.75 m, its face towards the
# camera. A brushed bezel bolted over the rim holds the neon `ring` (the game
# shifts it from cyan to red as the timer runs out), a chunky seven-segment
# countdown (`display`, blinked by the game) sits in a rubber housing, and a
# braided fuse cord rises from a threaded detonator collar on top, ending in
# a glowing ember (`fuse`; bomb.tscn hangs its spark particles on it).
# Stencils, a warning sticker, a pressure gauge that ticks and a blinking
# arming LED finish it. Centred on the origin.
#   blender -b --python blender/bomb.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
R = 1.75
FRONT = (math.pi / 2, 0, 0)     # lathe local +Z -> world -Y (towards the camera)
FACE_Y = -0.44                  # the front plate


# ------------------------------------------------------------------ decals --
def draw_stripes(img, d):
    w, h = img.size
    d.rectangle((0, 0, w, h), fill=(235, 180, 20, 255))
    for k in range(-2, 4):
        x = k * w // 2
        d.polygon([(x, h), (x + w // 4, h), (x + w // 4 + h, 0), (x + h, 0)], fill=(20, 18, 22, 255))


def draw_side_label(img, d):
    w, h = img.size
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=6, fill=(22, 22, 28, 255))
    f = pil_font(int(h * 0.62))
    d.text((w / 2, h / 2), "HIGH EXPLOSIVE  ·  BF-7", font=f, fill=(235, 232, 220, 255), anchor="mm")


def draw_sticker(img, d):
    w, h = img.size
    d.rounded_rectangle((2, 2, w - 3, h - 3), radius=14, fill=(245, 190, 25, 255))
    d.rounded_rectangle((10, 10, w - 11, h - 11), radius=10, outline=(25, 20, 25, 255), width=5)
    # Warning triangle.
    cx, cy, s = h * 0.55, h / 2, h * 0.34
    d.polygon([(cx, cy - s), (cx + s * 1.1, cy + s * 0.85), (cx - s * 1.1, cy + s * 0.85)], fill=(25, 20, 25, 255))
    d.polygon([(cx, cy - s * 0.55), (cx + s * 0.68, cy + s * 0.6), (cx - s * 0.68, cy + s * 0.6)], fill=(245, 190, 25, 255))
    d.rectangle((cx - s * 0.08, cy - s * 0.25, cx + s * 0.08, cy + s * 0.25), fill=(25, 20, 25, 255))
    d.ellipse((cx - s * 0.09, cy + s * 0.34, cx + s * 0.09, cy + s * 0.52), fill=(25, 20, 25, 255))
    f1 = pil_font(int(h * 0.30))
    f2 = pil_font(int(h * 0.15))
    tx = h * 1.05 + (w - h * 1.05) / 2
    d.text((tx, h * 0.40), "DANGER", font=f1, fill=(25, 20, 25, 255), anchor="mm")
    d.text((tx, h * 0.72), "HIGH EXPLOSIVE", font=f2, fill=(25, 20, 25, 255), anchor="mm")
    # Wear: a torn corner and scuffs.
    d.polygon([(w - 3, h - 40), (w - 3, h - 3), (w - 46, h - 3)], fill=(0, 0, 0, 0))
    import random
    rnd = random.Random(7)
    for _ in range(26):
        x, y = rnd.uniform(0, w), rnd.uniform(0, h)
        d.line((x, y, x + rnd.uniform(-30, 30), y + rnd.uniform(-4, 4)), fill=(120, 95, 40, 140), width=2)


FW = 2.44          # the face artwork covers the plate, 2.44 m square


def face_px(x, z, n):
    return ((x + FW / 2) / FW * n, (FW / 2 - z) / FW * n)


def draw_face(img, d):
    """Paint on the face plate: the plate colour, a timer scale of 60 ticks,
    the stencilled serial, the warning sticker and scuffs."""
    import random
    n = img.size[0]
    k = n / FW
    c = n / 2
    r = 1.215 * k
    d.ellipse((c - r, c - r, c + r, c + r), fill=(96, 106, 128, 255))
    for i in range(60):
        a = math.tau * i / 60
        r0 = (1.02 if i % 5 == 0 else 1.08) * k
        r1 = 1.16 * k
        d.line((c + r0 * math.sin(a), c - r0 * math.cos(a), c + r1 * math.sin(a), c - r1 * math.cos(a)),
               fill=(222, 222, 214, 255), width=7 if i % 5 == 0 else 3)
    # Stencilled serial above the display, with spray gaps.
    f = pil_font(int(0.17 * k))
    x, y = face_px(0, 0.84, n)
    d.text((x, y), "BF-04", font=f, fill=(226, 226, 230, 255), anchor="mm")
    # Warning sticker below the display.
    sw, sh = int(1.05 * k), int(0.35 * k)
    from PIL import Image, ImageDraw
    st = Image.new("RGBA", (sw, sh), (0, 0, 0, 0))
    draw_sticker(st, ImageDraw.Draw(st))
    x, y = face_px(-0.525, -0.125, n)
    img.alpha_composite(st, (int(x), int(y)))
    rnd = random.Random(5)
    for _ in range(90):            # scuffs and scratches
        a = rnd.uniform(0, math.tau)
        rr = math.sqrt(rnd.uniform(0.05, 1.0)) * 1.15 * k
        x, y = c + rr * math.cos(a), c + rr * math.sin(a)
        ln = rnd.uniform(8, 40)
        b = rnd.uniform(-0.5, 0.5)
        d.line((x, y, x + ln * math.cos(b), y + ln * math.sin(b)), fill=(150, 155, 165, 150), width=1)
    for _ in range(180):           # spray gaps in the stencil
        x, y = face_px(rnd.uniform(-0.3, 0.3), 0.84 + rnd.uniform(-0.09, 0.09), n)
        rr = rnd.uniform(1, 3)
        d.ellipse((x - rr, y - rr, x + rr, y + rr), fill=(96, 106, 128, 255))


def draw_engrave(img, d):
    """Height: machined grooves (alpha = depth) on the face plate."""
    n = img.size[0]
    k = n / FW
    c = n / 2
    for rr, wdt in ((1.0, 5), (0.97, 2)):
        r = rr * k
        d.ellipse((c - r, c - r, c + r, c + r), outline=(0, 0, 0, 255), width=wdt)
    for sx in (-1, 1):             # vent slots either side of the display
        for j in range(4):
            x0, y0 = face_px(sx * 0.82 - 0.12, 0.44 - j * 0.09, n)
            x1, y1 = face_px(sx * 0.82 + 0.12, 0.44 - j * 0.09, n)
            d.rounded_rectangle((x0, y0 - 5, x1, y1 + 5), radius=5, fill=(0, 0, 0, 255))


def draw_gauge(img, d):
    w, h = img.size
    c = w / 2
    d.ellipse((0, 0, w - 1, h - 1), fill=(228, 222, 205, 255))
    for i in range(9):
        a = math.radians(225 - i * 33.75)
        r0, r1 = c * 0.70, c * 0.9
        d.line((c + r0 * math.cos(a), c - r0 * math.sin(a), c + r1 * math.cos(a), c - r1 * math.sin(a)),
               fill=(30, 25, 30, 255), width=6)
    d.arc((c * 0.12, c * 0.12, w - c * 0.12, h - c * 0.12), -60, 45, fill=(210, 30, 30, 255), width=12)


stripes = decal_image("bomb_stripes", 128, 32, draw_stripes)
side_label = decal_image("bomb_side_label", 512, 48, draw_side_label)
face = decal_image("bomb_face", 1024, 1024, draw_face)
engrave = decal_image("bomb_engrave", 1024, 1024, draw_engrave)
gauge_face = decal_image("bomb_gauge", 128, 128, draw_gauge)

BAND = 1.705
CYL = ((0, 0, 0), (0, 1, 0), BAND)
CASING = decal_pbr("paint", (0.085, 0.09, 0.115), [
    dict(image=stripes, origin=(0, 0, BAND), size=(0.46, 0.2), v=(0, -1, 0), repeat=True, cyl=CYL,
         depth=0.02, rough=0.5),
    dict(image=side_label, origin=(BAND, 0, 0), size=(2.4, 0.16), v=(0, -1, 0), cyl=CYL, depth=0.02, rough=0.45,
         flip_u=True),
    dict(image=side_label, origin=(-BAND, 0, 0), size=(2.4, 0.16), v=(0, -1, 0), cyl=CYL, depth=0.02, rough=0.45),
    dict(image=face, origin=(0, FACE_Y, 0), size=(FW, FW), depth=0.012, rough=0.5),
    dict(image=engrave, origin=(0, FACE_Y, 0), size=(FW, FW), depth=0.012, mode="none", emboss=-1.0),
], name="bomb_casing", wear=0.8, grime=0.6, scale=0.8)
BEZEL = pbr("metal", (0.46, 0.47, 0.52), rough=0.3, name="bomb_bezel", grime=0.5)
BOLT = pbr("chrome", (0.7, 0.7, 0.74), name="bomb_bolt")
HOUSING = pbr("rubber", (0.035, 0.035, 0.045), rough=0.7, name="bomb_housing")
GLASS_RED = pbr("plastic", (0.06, 0.008, 0.01), rough=0.08, name="bomb_lcd_glass", wear=0.0)
GHOST = pbr("neon", (0.05, 0.005, 0.005), emit=(0.9, 0.05, 0.03), strength=0.25, name="bomb_ghost")
DIGITS = pbr("neon", (0.3, 0.02, 0.02), emit=(1.0, 0.07, 0.04), strength=4.0, name="bomb_digits")
RING = pbr("neon", (0.06, 0.07, 0.09), emit=CYAN, strength=3.0, name="bomb_ring")
BRASS_M = pbr("gold", (0.55, 0.38, 0.12), rough=0.35, name="bomb_brass")
CORD = pbr("fabric", (0.26, 0.17, 0.08), color2=(0.45, 0.32, 0.16), name="bomb_cord", scale=0.3)
EMBER = pbr("neon", (1.0, 0.5, 0.1), emit=(1.0, 0.45, 0.08), strength=9.0, name="bomb_ember")
GX, GZ = -0.58, -0.74
GAUGE = decal_pbr("plastic", (0.8, 0.78, 0.72), [
    dict(image=gauge_face, origin=(GX, FACE_Y - 0.06, GZ), size=(0.32, 0.32), depth=0.05),
], name="bomb_gauge_face", wear=0.0, grime=0.3)
NEEDLE = pbr("plastic", (0.75, 0.05, 0.04), name="bomb_needle")
KEY = pbr("rubber", (0.12, 0.12, 0.14), name="bomb_key")
KEY_RED = pbr("plastic", (0.7, 0.05, 0.05), name="bomb_key_red", rough=0.3)
LED = pbr("neon", (0.4, 0.02, 0.02), emit=(1.0, 0.1, 0.1), strength=8.0, name="bomb_led")

# ------------------------------------------------------------------ casing --
# (radius, z) with z towards the front: back plate, chamfered back rim, the
# side wall with a recessed belt (hazard stripes), then the front lip.
lathe([
    (0.0, -0.40), (1.62, -0.40), (1.72, -0.36), (1.75, -0.28),
    (1.75, -0.12), (1.705, -0.10), (1.705, 0.10), (1.75, 0.12), (1.75, 0.28), (1.72, 0.36),
    (1.62, 0.40), (1.46, 0.40),
    # neon channel, then the raised face plate
    (1.46, 0.34), (1.28, 0.34), (1.26, 0.42), (1.21, 0.44), (0.0, 0.44),
], CASING, segments=32, rot=FRONT, name="casing", angle=34)

# Brushed bezel ring bolted over the front lip.
lathe([(1.70, 0.39), (1.70, 0.47), (1.65, 0.50), (1.49, 0.50), (1.47, 0.39)],
      BEZEL, segments=32, rot=FRONT, name="bezel", angle=40)
for i in range(12):
    a = (i + 0.5) / 12 * math.tau
    bolt((math.cos(a) * 1.575, -0.495, math.sin(a) * 1.575), (0, -1, 0), 0.055, 0.04, BOLT, spin=a)

# The neon ring, sunk in its channel.
torus(1.37, 0.055, (0, -0.36, 0), RING, rot=FRONT, major_segments=28, minor_segments=5, name="ring")

# ----------------------------------------------------------------- display --
DX, DZ = 0.0, 0.30
bm_box((1.22, 0.2, 0.56), (DX, FACE_Y - 0.08, DZ), HOUSING, chamfer=0.05, smooth_angle=35)
bm_box((1.02, 0.02, 0.38), (DX, FACE_Y - 0.185, DZ), GLASS_RED)
for sx in (-1, 1):      # corner screws holding the housing
    for sz in (-1, 1):
        bolt((DX + sx * 0.567, FACE_Y - 0.178, DZ + sz * 0.225), (0, -1, 0), 0.022, 0.012, BOLT, sides=6)

SEGS = {"0": "abcdef", "3": "abcdg", "8": "abcdefg"}


def seg_rects(ch, x0, z0, w=0.15, h=0.27, t=0.034, gap=0.006):
    """Seven-segment bars of a digit (lower-left corner x0, z0), as
    (cx, cz, sx, sz) rectangles."""
    r = {
        "a": (x0 + w / 2, z0 + h - t / 2, w - 2 * gap, t),
        "g": (x0 + w / 2, z0 + h / 2, w - 2 * gap, t),
        "d": (x0 + w / 2, z0 + t / 2, w - 2 * gap, t),
        "f": (x0 + t / 2, z0 + h * 0.75, t, h / 2 - 2 * gap),
        "b": (x0 + w - t / 2, z0 + h * 0.75, t, h / 2 - 2 * gap),
        "e": (x0 + t / 2, z0 + h * 0.25, t, h / 2 - 2 * gap),
        "c": (x0 + w - t / 2, z0 + h * 0.25, t, h / 2 - 2 * gap),
    }
    return [r[s] for s in SEGS[ch]]


def flat_quads(rects, y, m, name, skew=0.12, base_z=0.0):
    bm = bmesh.new()
    for cx, cz, sx, sz in rects:
        vs = []
        for (px, pz) in ((cx - sx / 2, cz - sz / 2), (cx + sx / 2, cz - sz / 2),
                         (cx + sx / 2, cz + sz / 2), (cx - sx / 2, cz + sz / 2)):
            vs.append(bm.verts.new((px + skew * (pz - base_z), y, pz)))
        bm.faces.new(vs)
    o = bpy.data.objects.new(name, bpy.data.meshes.new(name))
    bm.to_mesh(o.data)
    bm.free()
    bpy.context.collection.objects.link(o)
    o.data.materials.append(m)
    return o


xs = [-0.43, -0.23, 0.08, 0.28]
ghost, lit = [], []
for x, ch in zip(xs, "0003"):
    ghost += seg_rects("8", x, DZ - 0.135)
    lit += seg_rects(ch, x, DZ - 0.135)
for cz in (DZ - 0.05, DZ + 0.06):     # the colon
    ghost.append((0.0, cz, 0.035, 0.035))
    lit.append((0.0, cz, 0.035, 0.035))
flat_quads(ghost, FACE_Y - 0.2, GHOST, "lcd_ghost", base_z=DZ)
flat_quads(lit, FACE_Y - 0.206, DIGITS, "display", base_z=DZ)

# Arming LED on the housing (blinks in the idle clip).
led_p = pivot("arm_led", (DX + 0.40, FACE_Y - 0.19, DZ + 0.235))
sphere(0.03, (DX + 0.40, FACE_Y - 0.19, DZ + 0.235), LED, segments=6, rings=4, name="led", parent=led_p)

# ------------------------------------------------------- gauge and keypad --
lathe([(0.2, 0.0), (0.2, 0.05), (0.17, 0.075), (0.155, 0.06)],
      BOLT, segments=16, loc=(GX, FACE_Y, GZ), rot=FRONT, name="gauge_bezel")
lathe([(0.158, 0.06), (0.0, 0.06)], GAUGE, segments=16, loc=(GX, FACE_Y, GZ), rot=FRONT, name="gauge_face")
needle = pivot("needle", (GX, FACE_Y - 0.08, GZ))
needle.rotation_euler = (0, math.radians(-60), 0)
cube((0.022, 0.008, 0.12), (GX, FACE_Y - 0.08, GZ + 0.045), NEEDLE, bevel=0.0, parent=needle)
bolt((GX, FACE_Y - 0.078, GZ), (0, -1, 0), 0.02, 0.01, BOLT, sides=6, parent=needle)

KX, KZ = 0.50, -0.72
bm_box((0.46, 0.06, 0.33), (KX, FACE_Y - 0.02, KZ), HOUSING, chamfer=0.02)
for j in range(2):
    for i in range(3):
        m = KEY_RED if (i == 2 and j == 0) else KEY
        bm_box((0.1, 0.05, 0.1), (KX - 0.14 + i * 0.14, FACE_Y - 0.06, KZ + 0.07 - j * 0.14), m)

# ----------------------------------------------------------- the detonator --
TOP = R - 0.04
lathe([(0.42, TOP - 0.1), (0.42, TOP + 0.06), (0.37, TOP + 0.1), (0.2, TOP + 0.1), (0.13, TOP + 0.26),
       (0.13, TOP + 0.42), (0.1, TOP + 0.45), (0.0, TOP + 0.45)], BEZEL, segments=16, name="collar", angle=40)
bolt((0, 0, TOP + 0.1), (0, 0, 1), 0.22, 0.16, BEZEL, name="nut")
for i in range(4):
    a = i / 4 * math.tau + math.pi / 4
    bolt((math.cos(a) * 0.34, math.sin(a) * 0.34, TOP + 0.075), (0, 0, 1), 0.04, 0.035, BOLT)
# Armoured conduit from the display up over the rim into the collar.
tube(smooth_path([(0.42, FACE_Y - 0.1, DZ + 0.3), (0.5, FACE_Y - 0.18, 0.95), (0.52, -0.62, 1.42),
                  (0.46, -0.45, 1.72), (0.3, -0.22, TOP + 0.02)], 2),
     0.035, KEY, sides=5, name="conduit")

# Braided fuse cord: rises from the cap and curls over, swaying in the idle.
arm = pivot("fuse_arm", (0, 0, TOP + 0.45))
cord = smooth_path([(0, 0, TOP + 0.4), (0.0, 0.0, TOP + 0.62), (0.1, -0.02, TOP + 0.84), (0.3, -0.04, TOP + 0.94),
                    (0.5, -0.05, TOP + 0.88)], 3)
tube(cord, 0.055, CORD, sides=5, name="fuse_cord", parent=arm, twist=0.9)
tip = cord[-1]
lathe([(0.0, -0.02), (0.07, -0.02), (0.07, 0.07), (0.0, 0.07)], BRASS_M, segments=8,
      loc=(tip.x - 0.04, tip.y, tip.z + 0.015), rot=(0, math.radians(110), 0), name="ferrule", parent=arm)
sphere(0.085, (tip.x + 0.04, tip.y, tip.z - 0.01), EMBER, segments=8, rings=5, name="fuse", parent=arm)

# ------------------------------------------------------------------- idle --
# One 4 s loop: the cord sways, the gauge needle ticks round, the LED blinks.
wobble(arm, "idle", "rotation_euler", 1, math.radians(5), seconds=4, phase=0.0)
wobble(arm, "idle", "rotation_euler", 0, math.radians(3.5), seconds=4, phase=1.3)
# glTF keeps no step interpolation here, so every tick is a pair of keys
# one frame apart (a snap) with a hold in between.
ticks = []
for k in range(16):
    ang = math.radians(-60 + 7.5 * k)
    ticks += [(k * 7.5, (0, ang, 0)), (k * 7.5 + 6.5, (0, ang, 0))]
ticks.append((120, (0, math.radians(-60), 0)))
key(needle, "idle", "rotation_euler", ticks, interp="LINEAR")
blink = []
for k in range(8):
    v = (1, 1, 1) if k % 2 == 0 else (0.15, 0.15, 0.15)
    blink += [(k * 15, v), (k * 15 + 14, v)]
blink.append((120, (1, 1, 1)))
key(led_p, "idle", "scale", blink, interp="LINEAR")

tri_breakdown()
finish("bomb", keep=("ring", "display"))
tri_report("bomb")
export("bomb", tex=1024)
sheet("bomb", zoom=1.0)
