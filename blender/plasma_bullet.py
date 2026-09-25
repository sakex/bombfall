# plasma_bullet: a ball of plasma about 0.6 m across, centred (wall guns and
# the bat boss fire it; the game spins the model in the screen plane as it
# flies). A white-hot core inside a violet energy shell and a faint outer
# halo, with three tapering wisps curling off it like a pinwheel. Idle: the
# shell and halo throb and the wisps flicker.
#   blender -b --python blender/plasma_bullet.py -- --preview blender/previews
import math
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import *  # noqa: F401,F403
from core_kit import *  # noqa: F401,F403

clean_scene()

CORE = pbr("neon", (1.0, 0.95, 0.9), emit=(1.0, 0.92, 0.95), strength=12.0, name="pb_core")
SHELL = glow_glass((0.7, 0.3, 1.0), alpha=0.6, strength=4.0, base=(0.35, 0.12, 0.6), name="pb_shell")
HALO = glow_glass((0.9, 0.3, 1.0), alpha=0.18, strength=2.5, base=(0.3, 0.08, 0.4), name="pb_halo")
WISP = pbr("neon", (0.45, 0.12, 0.8), emit=(0.7, 0.3, 1.0), strength=3.5, name="pb_wisp")
SPARK = pbr("neon", (0.9, 0.8, 1.0), emit=(1.0, 0.85, 1.0), strength=9.0, name="pb_spark")

ico(0.11, (0, 0, 0), CORE, subdiv=2, smooth=True, name="core")
shell = pivot("shell", (0, 0, 0))
sphere(0.2, (0, 0, 0), SHELL, segments=12, rings=8, name="shell_mesh", parent=shell)
halo = pivot("halo", (0, 0, 0))
sphere(0.29, (0, 0, 0), HALO, segments=12, rings=8, name="halo_mesh", parent=halo)

# Three wisps spiralling out in the screen plane, thick at the root.
wisps = pivot("wisps", (0, 0, 0))
for k in range(3):
    a0 = k * math.tau / 3
    pts, radii = [], []
    for i in range(9):
        t = i / 8
        a = a0 + t * 2.3
        r = 0.14 + t * 0.26
        pts.append((r * math.cos(a), (0.04 if k % 2 else -0.04) * t, r * math.sin(a)))
        radii.append(0.034 * (1 - t) + 0.005)
    tube(pts, radii, WISP, sides=5, name="wisp%d" % k, parent=wisps)
    sphere(0.025, pts[-1], SPARK, segments=6, rings=4, parent=wisps)

key(shell, "idle", "scale", [(0, (1, 1, 1)), (5, (1.12, 1.12, 1.12)), (10, (0.95, 0.95, 0.95)), (15, (1.08, 1.08, 1.08)),
                             (20, (1, 1, 1)), (30, (1, 1, 1))])
key(halo, "idle", "scale", [(0, (1, 1, 1)), (8, (1.18, 1.18, 1.18)), (18, (0.94, 0.94, 0.94)), (30, (1, 1, 1))])
key(wisps, "idle", "scale", [(0, (1, 1, 1)), (4, (1.1, 1, 1.1)), (9, (0.92, 1, 0.92)), (15, (1.06, 1, 1.06)),
                             (22, (0.96, 1, 0.96)), (30, (1, 1, 1))])

finish("plasma_bullet", keep=("core",))
tri_report("plasma_bullet")
export("plasma_bullet", tex=256)
sheet("plasma_bullet", views=[(0, 0), (40, 25)])
