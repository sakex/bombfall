# Ceiling of the sky bar (rich2), Neon Palace: black lacquer coffers on a
# brass grid behind a cyan-lit cornice; smoked-glass globe pendants over
# the bar that sway (sway_*); a mirror ball over the DJ booth that turns
# (spin_disco) throwing glints and a small one over the bar; three
# moving-head lights sweeping coloured beams (sweep_*); two neon halo
# rings over the lounge swaying on fine cables (sway_halo).
#   blender -b --python blender/ceiling_rich2.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
LACQUER = pbr("plastic", (0.015, 0.02, 0.05), rough=0.15, name="ceiling_lacquer")
slab_at(0.0, 15.0, 0.0, WALL, -0.05, 0.0, LACQUER)
for i in range(11):
    bx = i * 1.5
    slab_at(bx - 0.03, bx + 0.03, 0.15, WALL, -0.12, -0.05, M.brass)
slab_at(0.0, 15.0, 1.0, 1.06, -0.12, -0.05, M.brass)
cornice(0.0, 15.0, 0.0, M.black_metal, M.brass, h=0.3, d=0.2, light=M.n_cyan)
# pendants over the bar
for i in range(5):
    px = 6.9 + i * 0.95
    pendant("sway_pendant_%d" % i, px, 0.75, 1.1 + (i % 2) * 0.25, m_shade=neon_mat((1.0, 0.6, 0.3), 1.8, "amber_glass"), kind="globe", r=0.16)
# the mirror ball over the decks
disco_ball("spin_disco", 13.3, 0.9, drop=0.9, r=0.34)
# moving heads sweeping the room
moving_head("sweep_0", 1.6, 0.6, (0.2, 0.85, 1.0), beam=2.8, aim=0.25, phase=0.0)
moving_head("sweep_1", 11.8, 0.5, (1.0, 0.2, 0.7), beam=2.8, aim=-0.2, phase=2.0)
moving_head("sweep_2", 14.6, 0.6, (0.6, 0.25, 1.0), beam=2.8, aim=0.3, phase=4.0)
# halo rings over the lounge: two neon hoops on fine cables
hp = pivot("sway_halo", (3.0, 1.0, 0.0))
for k in range(3):
    a = TAU * k / 3 + 0.3
    tube([(3.0 + math.cos(a) * 0.9, 1.0 + math.sin(a) * 0.5, -0.05), (3.0 + math.cos(a) * 0.9, 1.0 + math.sin(a) * 0.5, -1.0)], 0.004, M.steel, verts=3, caps=False, parent=hp)
torus(0.92, 0.035, (3.0, 1.0, -1.0), M.n_cyan, scale=(1.0, 0.55, 1.0), major_segments=28, minor_segments=4, parent=hp)
torus(0.62, 0.03, (3.0, 1.0, -1.25), M.n_pink, scale=(1.0, 0.55, 1.0), major_segments=24, minor_segments=4, parent=hp)
for k in range(3):
    a = TAU * k / 3 + 0.3
    tube([(3.0 + math.cos(a) * 0.9, 1.0 + math.sin(a) * 0.5, -1.0), (3.0 + math.cos(a) * 0.6, 1.0 + math.sin(a) * 0.33, -1.25)], 0.004, M.steel, verts=3, caps=False, parent=hp)
merge_children(hp, "sway_halo_mesh")
disco_ball("spin_disco_small", 8.8, 1.35, drop=0.55, r=0.18)

finish("ceiling_rich2", 1024, 5000)
