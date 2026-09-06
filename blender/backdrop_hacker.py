# Backdrop for the "hacker" rooms, cyberpunk edition: a navy den of server
# racks under green/cyan neon seams, a long desk with a wall of screens,
# scanline monitors, kanji shop signs, circuit traces glowing across the
# wall, a wet grid floor, a radar hologram turning by the desk, and a
# projection map, lasers and cables on the upper wall. 15 m wide.
#   blender -b --python blender/backdrop_hacker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from props import *  # noqa: F401,F403
from synth import *  # noqa: F401,F403

clean_scene()
D = 1.85  # the back wall is at Y = 1.9
WINDOWS = [(10.6, 4.2, 3.6, 2.0), (0.3, 4.4, 3.0, 1.6)]
GREEN = neon((0.25, 1.0, 0.45), 2.2, (0.02, 0.12, 0.05))
AMBER = neon((1.0, 0.6, 0.15), 2.0, (0.12, 0.06, 0.01))
GRID_G = neon((0.3, 1.0, 0.5), 3.5)
HACK_NAVY = ((0.020, 0.040, 0.070), 0.85, 0.0)

# Wall: near-black navy with green seams, cyan circuit traces, neon-lined windows.
cube((15.0, 0.03, 7.0), (7.5, D + 0.025, 3.5), HACK_NAVY, bevel=0.0)
neon_seams(0.0, 15.0, 0.0, 7.0, D + 0.0, GRID_G, spacing=1.4, avoid=WINDOWS, r=0.012)
for w in WINDOWS:
    window_neon(w, D - 0.02, NEON_ICE)
circuit_trace(0.4, 4.4, D + 0.0, 6.55, m=NEON_ICE, seed=4, steps=5)
circuit_trace(10.4, 14.6, D + 0.0, 6.6, m=NEON_ICE, seed=9, steps=5)
circuit_trace(3.5, 10.5, D + 0.0, 6.4, m=GREEN, seed=2, steps=7)
# Floor: wet slab with a green grid.
wet_floor(0.0, 15.0, 0.0, D)
grid_floor(0.2, 14.8, 0.1, D - 0.1, m=GRID_G, m2=NEON_ICE, nx=10, ny=3)

# Left: two server racks and a stack of crates, an LED column between them.
server_rack(0.6, D - 0.8, 0.0)
server_rack(1.4, D - 0.8, 0.0, h=1.9, units=8)
led_column(2.0, D + 0.0, 0.0, 3.6, m=GREEN, alt=NEON_ICE, w=0.18)
box(2.7, D - 0.9, 0.0, w=0.7, d=0.6, h=0.5, m=MAT_PLUM, rot=0.15)
box(2.7, D - 0.9, 0.5, w=0.6, d=0.5, h=0.45, m=MAT_PLUM, rot=-0.2)
kanji_sign(3.5, D + 0.0, 1.2, 2.7, m=NEON_HOT, seed=8, frame=NEON_ICE)

# Centre: a long desk under a wall of monitors.
desk(6.5, D - 0.9, 0.0, w=4.6, d=0.85, m=MAT_INK)
cube((4.6, 0.02, 0.03), (6.5, D - 1.33, 0.76), GREEN, bevel=0.0)              # desk edge light
crt(4.9, D - 0.6, 0.81, w=0.55, screen=GREEN)
monitor(5.9, D - 0.5, 0.81, w=0.7, h=0.45, screen=GREEN)
monitor(6.9, D - 0.5, 0.81, w=0.9, h=0.55, screen=SCREEN_CYAN)
monitor(7.9, D - 0.5, 0.81, w=0.7, h=0.45, screen=GREEN, tilt=-0.1)
crt(8.6, D - 0.6, 0.81, w=0.5, screen=AMBER)
cube((0.45, 0.16, 0.02), (6.4, D - 1.35, 0.82), PLASTIC_BLACK, bevel=0.0)    # keyboard
cube((0.4, 0.01, 0.01), (6.4, D - 1.35, 0.835), NEON_HOT, bevel=0.0)
sphere(0.05, (7.1, D - 1.35, 0.85), PLASTIC_BLACK, scale=(1, 1.4, 0.7))        # mouse
cyl(0.05, 0.14, (5.4, D - 1.3, 0.88), NEON_GREEN, verts=10)                    # energy drink
# Wall of screens above the desk, a scanline main screen in the middle.
for i, (w, h, scr) in enumerate([(0.9, 0.6, GREEN), (0.9, 0.6, GREEN), (0.7, 0.5, AMBER)]):
    x = [4.7, 8.3, 9.3][i]
    monitor(x, D + 0.0, 1.9 + (0.25 if i % 2 else 0), w=w, h=h, screen=scr, stand=False)
scanline_screen(6.5, D + 0.0, 2.25, 2.2, 1.0, colour=ICE, frame=NEON_ICE, seed=3)
for i in range(3):
    monitor(5.4 + i * 1.3, D + 0.0, 3.05, w=1.0, h=0.62, screen=GREEN if i != 1 else AMBER, stand=False)
scanline_screen(9.9, D + 0.0, 2.3, 1.2, 0.9, colour=(1.0, 0.3, 0.5), frame=NEON_HOT, seed=6)
neon_sign("NO SLEEP", 3.9, D + 0.0, 4.4, NEON_GREEN, cell=0.14, backing=MAT_INK)
neon_tube_frame(3.75, 8.05, 4.25, 5.25, D - 0.02, NEON_HOT, r=0.02)
neon_polygon(9.4, 4.8, D + 0.0, 0.5, 3, NEON_HOT)
neon_polygon(9.4, 4.8, D + 0.0, 0.3, 3, GREEN, rot=math.pi)
horizon_lines(8.3, 10.3, D + 0.0, 5.55, n=4, spacing=0.13, m=NEON_ICE)

# Right: shelves of loose hardware and a second work nook.
shelf(11.8, D - 0.4, 1.4, w=2.4)
shelf(11.8, D - 0.4, 2.2, w=2.4)
led_strip(10.6, 13.0, D - 0.42, 1.38, m=NEON_ICE, r=0.012)
led_strip(10.6, 13.0, D - 0.42, 2.18, m=NEON_HOT, r=0.012)
for i in range(5):
    box(10.8 + i * 0.5, D - 0.3, 1.4, w=0.35, d=0.3, h=0.2 + (i % 2) * 0.12, m=(SLATE, 0.6, 0.4))
for i in range(4):
    crt(10.9 + i * 0.62, D - 0.35, 2.22, w=0.42, screen=[GREEN, AMBER, SCREEN_CYAN, GREEN][i])
desk(12.6, D - 0.9, 0.0, w=2.2, d=0.8, m=MAT_INK)
monitor(12.2, D - 0.5, 0.81, w=0.8, h=0.5, screen=SCREEN_CYAN)
crt(13.2, D - 0.6, 0.81, w=0.5, screen=GREEN)
server_rack(14.4, D - 0.8, 0.0, w=0.65, h=2.4, units=10)
cube((0.5, 0.45, 0.06), (13.0, D - 1.25, 0.84), (WOOD_LIGHT, 0.85, 0.0), bevel=0.0)   # pizza box
kanji_sign(14.0, D + 0.0, 2.7, 1.3, m=NEON_ICE, seed=12, w=0.4)

# A radar hologram by the desk, cable spaghetti and cases on the floor.
hologram(9.6, 0.55, 0.0, "globe", "spin_radar", m=GREEN, r=0.42, ring=NEON_ICE)
for i in range(4):
    cable_drape(2.8 + i * 0.6, 3.3 + i * 0.6, D - 1.4 + (i % 2) * 0.3, 0.05, sag=-0.15, segments=4, r=0.015)
box(3.6, D - 1.3, 0.0, w=0.5, d=0.4, h=0.45, m=(GUNMETAL, 0.5, 0.6))
cube((0.03, 0.02, 0.03), (3.62, D - 1.52, 0.3), NEON_ORANGE, bevel=0.0)

# ---- upper wall (7 m to 9.5 m): a projection wall map, a vent, lasers and cables.
cube((15.0, 0.03, 2.5), (7.5, D + 0.025, 8.25), HACK_NAVY, bevel=0.0)
cube((5.0, 0.06, 2.0), (8.7, D + 0.0, 8.3), MAT_NAVY, bevel=0.0)
neon_tube_frame(6.2, 11.2, 7.3, 9.3, D - 0.03, GREEN, r=0.02)
for i in range(60):
    k = (i * 7919) % 1000
    px = 6.5 + (k % 47) / 47.0 * 4.4
    pz = 7.5 + ((k // 47) % 19) / 19.0 * 1.6
    cube((0.05, 0.02, 0.05), (px, D - 0.04, pz), NEON_GREEN if k % 5 else NEON_ORANGE, bevel=0.0)
for i in range(4):
    cube((5.0, 0.02, 0.01), (8.7, D - 0.035, 7.5 + i * 0.5), neon((0.2, 0.8, 0.4), 0.8), bevel=0.0)
neon_sign("ACCESS DENIED", 0.5, D + 0.0, 8.3, NEON_RED, cell=0.12, backing=MAT_INK)
chevron_strip(0.4, 6.0, 7.5, D + 0.0, m=NEON_HOT, h=0.26)
cube((1.4, 0.1, 1.0), (12.6, D + 0.0, 8.4), METAL_DARK, bevel=0.0)
for i in range(6):
    cube((1.2, 0.04, 0.05), (12.6, D - 0.06, 7.98 + i * 0.16), METAL_STEEL, bevel=0.0)
led_column(14.3, D + 0.0, 7.1, 2.3, m=GREEN, alt=NEON_HOT)
laser_fan(3.4, D - 0.4, 9.5, m=GRID_G, n=5, spread=1.3, length=2.2)
star_field(0.0, 15.0, 7.1, 9.4, D + 0.0, n=14, seed=8, m=neon((0.4, 1.0, 0.6), 2.0, (0.1, 0.3, 0.15)))
pipe_run(0.2, 14.8, D - 0.2, 9.3, r=0.08, drops=(4.0, 11.0))
for i in range(5):
    cable_drape(0.5 + i * 2.9, 3.0 + i * 2.9, D - 0.1, 9.2, sag=0.5, m=PLASTIC_BLACK, segments=6, r=0.02)

strip_bevels()
join_static("decor")
export("backdrop_hacker")
