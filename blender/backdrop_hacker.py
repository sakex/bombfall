# Backdrop for the "hacker" rooms: a dim den of server racks, stacked CRT
# monitors with green code, a big desk with a wall of screens, cables
# drooping from the ceiling, pizza boxes and one hanging lamp. Set dressing
# only (no physics): origin at floor level on the left wall, 15 m wide,
# props stay below 9.5 m and within 1.9 m of depth.
#   blender -b --python blender/backdrop_hacker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403

clean_scene()
D = 1.85  # the back wall is at Y = 1.9
GREEN = neon((0.25, 1.0, 0.45), 2.2, (0.02, 0.12, 0.05))
AMBER = neon((1.0, 0.6, 0.15), 2.0, (0.12, 0.06, 0.01))

wall_panel_lines(0.0, 15.0, D + 0.02, 0.0, 7.0, spacing=1.2)

# Left: two server racks and a stack of crates.
server_rack(0.6, D - 0.8, 0.0)
server_rack(1.4, D - 0.8, 0.0, h=1.9, units=8)
box(2.3, D - 0.9, 0.0, w=0.7, d=0.6, h=0.5, m=(WOOD_LIGHT, 0.85, 0.0), rot=0.15)
box(2.3, D - 0.9, 0.5, w=0.6, d=0.5, h=0.45, m=(WOOD_LIGHT, 0.85, 0.0), rot=-0.2)

# Centre: a long desk under a wall of monitors.
desk(6.5, D - 0.9, 0.0, w=4.6, d=0.85)
crt(4.9, D - 0.6, 0.81, w=0.55, screen=GREEN)
monitor(5.9, D - 0.5, 0.81, w=0.7, h=0.45, screen=GREEN)
monitor(6.9, D - 0.5, 0.81, w=0.9, h=0.55, screen=SCREEN_CYAN)
monitor(7.9, D - 0.5, 0.81, w=0.7, h=0.45, screen=GREEN, tilt=-0.1)
crt(8.6, D - 0.6, 0.81, w=0.5, screen=AMBER)
cube((0.45, 0.16, 0.02), (6.4, D - 1.35, 0.82), PLASTIC_BLACK, bevel=0.005)   # keyboard
sphere(0.05, (7.1, D - 1.35, 0.85), PLASTIC_BLACK, scale=(1, 1.4, 0.7))        # mouse
cyl(0.05, 0.14, (5.4, D - 1.3, 0.88), NEON_GREEN, verts=10)                    # energy drink
# Wall of screens above the desk.
for i, (w, h, scr) in enumerate([(0.9, 0.6, GREEN), (1.4, 0.8, SCREEN_CYAN), (0.9, 0.6, GREEN), (0.7, 0.5, AMBER)]):
    x = 4.7 + i * 1.15 + (0.2 if i > 1 else 0)
    monitor(x, D + 0.0, 1.9 + (0.25 if i % 2 else 0), w=w, h=h, screen=scr, stand=False)
for i in range(3):
    monitor(5.4 + i * 1.3, D + 0.0, 3.0, w=1.0, h=0.62, screen=GREEN if i != 1 else AMBER, stand=False)
poster(9.6, D + 0.0, 2.2, w=0.7, h=1.0, face=neon((0.9, 0.2, 0.3), 1.2, (0.2, 0.04, 0.06)))
poster(10.4, D + 0.0, 2.1, w=0.6, h=0.8, face=neon((0.3, 0.6, 1.0), 1.2, (0.05, 0.1, 0.25)))
neon_sign("NO SLEEP", 3.9, D + 0.0, 4.4, NEON_GREEN, cell=0.14, backing=PLASTIC_BLACK)

# Right: shelves of loose hardware and a second work nook.
shelf(11.8, D - 0.4, 1.4, w=2.4)
shelf(11.8, D - 0.4, 2.2, w=2.4)
for i in range(5):
    box(10.8 + i * 0.5, D - 0.3, 1.4, w=0.35, d=0.3, h=0.2 + (i % 2) * 0.12, m=(SLATE, 0.6, 0.4))
for i in range(4):
    crt(10.9 + i * 0.62, D - 0.35, 2.22, w=0.42, screen=[GREEN, AMBER, SCREEN_CYAN, GREEN][i])
desk(12.6, D - 0.9, 0.0, w=2.2, d=0.8)
monitor(12.2, D - 0.5, 0.81, w=0.8, h=0.5, screen=SCREEN_CYAN)
crt(13.2, D - 0.6, 0.81, w=0.5, screen=GREEN)
server_rack(14.4, D - 0.8, 0.0, w=0.65, h=2.4, units=10)
cube((0.5, 0.45, 0.06), (13.0, D - 1.25, 0.84), (WOOD_LIGHT, 0.85, 0.0), bevel=0.01)   # pizza box

# Floor clutter: cable spaghetti and cases.
for i in range(4):
    cable_drape(2.8 + i * 0.6, 3.3 + i * 0.6, D - 1.4 + (i % 2) * 0.3, 0.05, sag=-0.15, segments=4, r=0.015)
box(3.6, D - 1.3, 0.0, w=0.5, d=0.4, h=0.45, m=(GUNMETAL, 0.5, 0.6))
cube((0.03, 0.02, 0.03), (3.62, D - 1.52, 0.3), NEON_ORANGE, bevel=0.0)

# ---- upper wall (7 m to 9.5 m): a projection wall map, a vent and cables.
cube((5.0, 0.06, 2.0), (7.5, D + 0.0, 8.2), (NAVY, 0.6, 0.0), bevel=0.02)
for i in range(60):
    k = (i * 7919) % 1000
    px = 5.3 + (k % 47) / 47.0 * 4.4
    pz = 7.4 + ((k // 47) % 19) / 19.0 * 1.6
    cube((0.05, 0.02, 0.05), (px, D - 0.04, pz), NEON_GREEN if k % 5 else NEON_ORANGE, bevel=0.0)
for i in range(4):
    cube((5.0, 0.02, 0.01), (7.5, D - 0.035, 7.4 + i * 0.5), neon((0.2, 0.8, 0.4), 0.8), bevel=0.0)
neon_sign("ACCESS DENIED", 1.0, D + 0.0, 7.6, NEON_RED, cell=0.12, backing=PLASTIC_BLACK)
cube((1.4, 0.1, 1.0), (12.6, D + 0.0, 8.4), METAL_DARK, bevel=0.02)
for i in range(6):
    cube((1.2, 0.04, 0.05), (12.6, D - 0.06, 7.98 + i * 0.16), METAL_STEEL, bevel=0.0)
pipe_run(0.2, 14.8, D - 0.2, 9.3, r=0.08, drops=(4.0, 11.0))
for i in range(5):
    cable_drape(0.5 + i * 2.9, 3.0 + i * 2.9, D - 0.1, 9.2, sag=0.5, m=PLASTIC_BLACK, segments=6, r=0.02)
wall_panel_lines(0.0, 15.0, D + 0.02, 7.0, 9.5, spacing=1.2)

join_static("decor")
export("backdrop_hacker")
