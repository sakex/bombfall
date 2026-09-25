# Ceiling of the streamer studio (tiktoker), Neon Palace: a white ceiling
# with a pink LED cove, soft clouds lit from within, a mirror ball over the
# bed (spin_disco), a white fan turning (spin_fan), paper lanterns and
# rattan pendants that sway (sway_*), neon stars dangling on strings
# (sway_star_*) and a swag of fairy lights with chasing bulbs.
#   blender -b --python blender/ceiling_tiktoker.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from kit_palace import *  # noqa: F401,F403

reset()
slab_at(0.0, 15.0, 0.0, WALL, -0.04, 0.0, M.lacquer_white)
cornice(0.0, 15.0, 0.0, M.lacquer_white, None, h=0.22, d=0.18, light=M.n_pink)
# clouds: puffy cushions hanging flat under the ceiling with a glow rim
for (cx, cy, s) in ((2.5, 1.2, 1.0), (12.4, 1.1, 0.8)):
    for (dx, dy, r) in ((-0.5, 0.0, 0.45), (0.1, 0.15, 0.55), (0.65, -0.05, 0.42)):
        o = sphere(r * s, (cx + dx * s, cy + dy * s * 0.5, -0.35), M.plush_white, scale=(1.0, 0.6, 0.45), segments=12, rings=7)
    tube([(cx + math.cos(a) * 1.1 * s, cy + math.sin(a) * 0.4 * s, -0.5) for a in [TAU * i / 20 for i in range(21)]], 0.012, anim_neon("pink", "marquee", 2.5), verts=3)
    for dx in (-0.6, 0.6):
        tube([(cx + dx * s, cy, 0.0), (cx + dx * s, cy, -0.25)], 0.004, M.steel, verts=3, caps=False)
disco_ball("spin_disco", 6.9, 1.0, drop=0.85, r=0.26)
ceiling_fan("spin_fan", 9.6, 1.0, drop=0.4, r=0.7, blades=3, m_metal=M.lacquer_white, m_blade=M.lacquer_white)
pendant("sway_lantern_0", 4.8, 0.8, 1.2, m_shade=neon_mat((1.0, 0.7, 0.8), 1.5, "paper_pink"), kind="lantern", r=0.2)
pendant("sway_lantern_1", 8.2, 0.7, 1.45, m_shade=neon_mat((1.0, 0.85, 0.6), 1.5, "paper_warm"), kind="lantern", r=0.17)
pendant("sway_rattan", 13.9, 0.9, 1.0, m_shade=M.bulb, m_metal=M.oak, kind="dome", r=0.24)
# neon stars on strings
for i, (sx, drop, col) in enumerate(((1.0, 1.1, M.n_amber), (5.9, 1.35, M.n_cyan), (11.0, 1.2, M.n_pink), (14.6, 1.5, M.n_amber))):
    p = pivot("sway_star_%d" % i, (sx, 0.5, 0.0))
    tube([(sx, 0.5, 0.0), (sx, 0.5, -drop + 0.2)], 0.003, M.steel, verts=3, caps=False, parent=p)
    pts = [(sx + math.cos(math.pi / 2 + TAU * k / 10) * (0.2 if k % 2 == 0 else 0.09), -drop + math.sin(math.pi / 2 + TAU * k / 10) * (0.2 if k % 2 == 0 else 0.09))
           for k in range(11)]
    tube([(px, 0.5, pz) for px, pz in pts], 0.018, col, verts=4, parent=p)
    merge_children(p, p.name + "_mesh")
# a swag of fairy lights across the front
pts = []
for i in range(60):
    t = i / 59
    pts.append((0.2 + 14.6 * t, -0.25 - 0.35 * abs(math.sin(t * math.pi * 4))))
tube([(px, 0.25, pz) for px, pz in pts], 0.004, M.black_metal, verts=3, caps=False)
quad_dots(pts, 0.23, 0.05, anim_neon((1.0, 0.75, 0.45), "marquee", 2.5), diamond=True)

finish("ceiling_tiktoker", 1024, 5000)
