# shield_battery: an energy cell, 0.8 m wide and 1.4 m tall, centred (it
# floats and spins above the pedestal; pickup.gd owns that motion). Chrome
# terminal caps with cooling ribs, a glass tube showing a glowing cyan core
# wrapped in a coil, a printed label band with a shield mark and a charge
# gauge. Idle: the coil turns and the core breathes.
#   blender -b --python blender/shield_battery.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()
R = 0.32


def draw_label(img, d):
    w, h = img.size
    d.rectangle((0, 0, w, h), fill=(18, 20, 34, 255))
    d.rectangle((0, 0, w, 6), fill=(40, 220, 240, 255))
    d.rectangle((0, h - 6, w, h), fill=(40, 220, 240, 255))
    for off in (0.0, 0.5):         # the mark and name at the front, again at the back
        cx = w * (0.42 + off)
        cy = h / 2
        s = h * 0.32
        d.polygon([(cx - s, cy - s * 0.9), (cx + s, cy - s * 0.9), (cx + s, cy), (cx, cy + s * 1.05), (cx - s, cy)],
                  fill=(40, 220, 240, 255))
        d.polygon([(cx - s * 0.7, cy - s * 0.65), (cx + s * 0.7, cy - s * 0.65), (cx + s * 0.7, cy - s * 0.02),
                   (cx, cy + s * 0.7), (cx - s * 0.7, cy - s * 0.02)], fill=(18, 20, 34, 255))
        d.rectangle((cx - s * 0.1, cy - s * 0.45, cx + s * 0.1, cy + s * 0.35), fill=(240, 240, 255, 255))
        d.rectangle((cx - s * 0.4, cy - s * 0.15, cx + s * 0.4, cy + s * 0.05), fill=(240, 240, 255, 255))
        f = pil_font(int(h * 0.3))
        d.text((cx + h * 0.95, cy - h * 0.12), "SHIELD", font=f, fill=(235, 238, 250, 255), anchor="mm")
        f2 = pil_font(int(h * 0.16))
        d.text((cx + h * 0.95, cy + h * 0.22), "CELL  +1  ·  9000 mAh", font=f2, fill=(120, 200, 220, 255),
               anchor="mm")


label = decal_image("battery_label", 1024, 160, draw_label)
CAP = pbr("chrome", (0.72, 0.73, 0.78), name="bat_cap")
DARKM = pbr("metal", (0.12, 0.13, 0.16), rough=0.35, name="bat_dark")
BAND = decal_pbr("plastic", (0.08, 0.09, 0.14), [
    dict(image=label, origin=(0, -0.345, -0.4), size=(2 * math.pi * 0.345, 0.2), v=(0, 0, 1),
         cyl=((0, 0, 0), (0, 0, 1), 0.345), depth=0.03, rough=0.3),
], name="bat_band", rough=0.25, wear=0.3)
GLASS = glass((0.7, 0.95, 1.0), alpha=0.22, rough=0.03, name="bat_glass")
CORE = pbr("neon", (0.1, 0.5, 0.6), emit=(0.25, 0.95, 1.0), strength=4.0, name="bat_core")
COIL = pbr("neon", (0.6, 0.9, 1.0), emit=(0.75, 0.97, 1.0), strength=6.0, name="bat_coil")
LED_ON = pbr("neon", (0.05, 0.4, 0.2), emit=(0.2, 1.0, 0.5), strength=4.0, name="bat_led")
BRASS_M = pbr("gold", (0.72, 0.5, 0.18), rough=0.25, name="bat_brass")

# Bottom cap (with a recess for the label band) and a ribbed top cap.
lathe([(0.0, -0.7), (0.3, -0.7), (0.34, -0.66), (0.34, -0.53), (0.325, -0.52), (0.325, -0.29), (0.36, -0.28),
       (0.36, -0.26), (0.3, -0.26), (0.3, -0.24), (0.0, -0.24)], CAP, segments=24, name="cap_bottom", angle=35)
lathe([(0.345, -0.515), (0.345, -0.295)], BAND, segments=24, name="band")
rib = []
for i in range(3):
    z = 0.31 + i * 0.065
    rib += [(0.36, z), (0.34, z + 0.012), (0.34, z + 0.03), (0.36, z + 0.042)]
lathe([(0.0, 0.24), (0.3, 0.24), (0.3, 0.26), (0.36, 0.28)] + rib + [(0.36, 0.5), (0.3, 0.56), (0.18, 0.58),
       (0.0, 0.58)], CAP, segments=24, name="cap_top", angle=35)
for z in (-0.25, 0.25):     # neon seals where the glass meets the caps
    torus(0.29, 0.016, (0, 0, z), CORE, major_segments=24, minor_segments=4)
lathe([(0.13, 0.58), (0.13, 0.66), (0.1, 0.7), (0.0, 0.7)], BRASS_M, segments=12, name="terminal")
cyl(0.3, 0.012, (0, 0, -0.706), DARKM, verts=24, bevel=0.0)
# Glass tube between the caps, the glowing core and a coil round it.
cyl(0.28, 0.52, (0, 0, 0), GLASS, verts=24, bevel=0.0, name="tube")
coil = pivot("coil", (0, 0, 0))
core = pivot("core", (0, 0, 0))
cyl(0.1, 0.5, (0, 0, 0), CORE, verts=12, bevel=0.0, name="core_rod", parent=core)
pts = []
for i in range(49):
    t = i / 48
    a = t * 5 * math.tau
    pts.append((0.18 * math.cos(a), 0.18 * math.sin(a), -0.23 + 0.46 * t))
tube(pts, 0.012, COIL, sides=4, name="coil_wire", parent=coil)
for s in (-1, 1):   # coil end posts
    cyl(0.03, 0.06, (0.18, 0, s * 0.235), BRASS_M, verts=6, bevel=0.0, parent=coil)
# Charge gauge on the bottom cap: four green bars.
for i in range(4):
    x = -0.09 + i * 0.06
    cube((0.045, 0.02, 0.05), (x, -0.335, -0.6), LED_ON, rot=(0, 0, 0), bevel=0.0)

spin(coil, "idle", "Z", seconds=2.0, turns=-1.0)
key(core, "idle", "scale", [(0, (1, 1, 1)), (15, (1.25, 1.25, 1.0)), (30, (1, 1, 1)), (45, (1.25, 1.25, 1.0)),
                            (60, (1, 1, 1))])

finish("shield_battery")
tri_report("shield_battery")
export("shield_battery", tex=512)
sheet("shield_battery", views=[(0, 0), (35, 20), (0, 70)])
