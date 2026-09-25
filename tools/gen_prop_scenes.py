#!/usr/bin/env python3
"""Writes the .tscn files of the simple pushable props (one rigid body, one
collision shape, one model). Re-run after changing a model's size."""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "src", "spawnables")

# name: (model, shape, size/params, centre y, mass[, script])
# shape "boxes" is a compound: params = [(size, (centre x, centre y)), ...]
# and "centre y" only sets the centre of mass.
# Shapes hug the visible mesh on X/Y (see src/dev/hitbox_audit.tscn); Z may
# be thicker for stability. The centre of mass sits at 42% of the height but
# never above 40% of the width: a sliding box on a floor with friction 1
# tips over as soon as its centre of mass is higher than half its width.
PROPS = {
    # The toilet is turned 30 degrees towards the camera: its box sits a
    # little right of the origin.
    "toilet": ("toilet", "boxes", [((1.6, 2.75, 1.2), (0.08, 1.375))], 1.375, 40),
    "bathtub": ("bathtub", "box", (5.7, 2.2, 2.2), 1.1, 120),
    "chair": ("chair", "box", (1.65, 3.0, 1.6), 1.5, 28),
    # The top and the place settings; the candelabra rises above it.
    "table": ("table", "box", (2.0, 1.45, 1.6), 0.725, 60),
    # The cabinet; the rabbit ears rise above it.
    "tv": ("tv", "box", (1.9, 2.1, 1.3), 1.05, 25),
    "champagne": ("champagne", "cylinder", (0.3, 1.0), 0.5, 3),
    "cake": ("cake", "cylinder", (0.45, 0.95), 0.48, 4),
    "bench_press": ("bench_press", "box", (4.0, 3.0, 2.6), 1.5, 90),
    # Beds: the mattress and pillows, plus the headboard at +X.
    "bed1": ("bed1", "boxes", [((5.9, 1.4, 2.3), (0.0, 0.7)), ((0.3, 1.95, 2.3), (2.82, 0.975))], 0.8, 100),
    "bed2": ("bed2", "boxes", [((5.9, 1.55, 2.6), (0.0, 0.775)), ((0.7, 2.85, 2.6), (2.62, 1.425))], 1.0, 110),
    "bed_rich": ("bed_rich", "box", (5.75, 2.8, 2.8), 1.4, 120),
    "arcade_cabinet": ("arcade_cabinet", "box", (1.34, 2.8, 1.2), 1.4, 45, "arcade_cabinet"),
}

SOLID = 1 | 2 | 8 | 16 | 32 | 256 | 512 | 2048

TEMPLATE = """[gd_scene load_steps={steps} format=3]

[ext_resource type="Script" path="res://src/spawnables/{script}.gd" id="1"]
[ext_resource type="PackedScene" path="res://assets/models/{model}.glb" id="2"]

{shape_resource}

[node name="{name}" type="RigidBody3D"]
collision_layer = 32
collision_mask = {mask}
mass = {mass}
center_of_mass_mode = 1
center_of_mass = Vector3(0, {com}, 0)
angular_damp = 2.0
can_sleep = false
script = ExtResource("1")

{shape_nodes}
[node name="Model" parent="." instance=ExtResource("2")]
"""

SHAPE_NODE = """[node name="{node}" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, {cx}, {cy}, 0)
shape = SubResource("{res}")
"""


def shape_resource(kind, params, res="shape"):
    if kind == "box":
        return '[sub_resource type="BoxShape3D" id="%s"]\nsize = Vector3(%g, %g, %g)' % ((res,) + tuple(params))
    if kind == "cylinder":
        return '[sub_resource type="CylinderShape3D" id="%s"]\nradius = %g\nheight = %g' % ((res,) + tuple(params))
    raise ValueError(kind)


def shapes(kind, params, cy):
    """[(resource text, node text)] for a prop's collision shape(s)."""
    if kind != "boxes":
        return [(shape_resource(kind, params), SHAPE_NODE.format(node="Shape", cx=0, cy=cy, res="shape"))]
    out = []
    for i, (size, (x, y)) in enumerate(params):
        res = "shape" if i == 0 else "shape%d" % (i + 1)
        node = "Shape" if i == 0 else "Shape%d" % (i + 1)
        out.append((shape_resource("box", size, res), SHAPE_NODE.format(node=node, cx=x, cy=y, res=res)))
    return out


def main():
    for name, spec in PROPS.items():
        model, kind, params, cy, mass = spec[:5]
        script = spec[5] if len(spec) > 5 else "prop"
        width = {"box": lambda: params[0], "cylinder": lambda: params[0] * 2.0, "boxes": lambda: params[0][0][0]}[kind]()
        com = round(min(cy * 2.0 * 0.42, width * 0.4), 2)
        sh = shapes(kind, params, cy)
        path = os.path.join(OUT, name + ".tscn")
        with open(path, "w") as f:
            f.write(TEMPLATE.format(model=model, name=name.title().replace("_", ""), mask=SOLID, mass=mass, com=com, script=script,
                                    steps=3 + len(sh), shape_resource="\n\n".join(r for r, _ in sh),
                                    shape_nodes="\n".join(n for _, n in sh)))
        print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
