#!/usr/bin/env python3
"""Writes the .tscn files of the simple pushable props (one rigid body, one
collision shape, one model). Re-run after changing a model's size."""
import os

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
OUT = os.path.join(ROOT, "src", "spawnables")

# name: (model, shape, size/params, centre y, mass)
PROPS = {
    "toilet": ("toilet", "box", (1.6, 2.7, 1.2), 1.35, 40),
    "bathtub": ("bathtub", "box", (5.7, 1.7, 2.2), 0.85, 120),
    "chair": ("chair", "box", (2.2, 3.0, 1.6), 1.5, 30),
    "table_with_chairs": ("table_with_chairs", "box", (4.6, 2.5, 1.6), 1.25, 80),
    "tv": ("tv", "box", (1.9, 2.1, 1.3), 1.05, 25),
    "champagne": ("champagne", "cylinder", (0.3, 1.0), 0.5, 3),
    "cake": ("cake", "cylinder", (0.45, 0.95), 0.48, 4),
    "bench_press": ("bench_press", "box", (4.0, 3.0, 2.6), 1.5, 90),
    "bed1": ("bed1", "box", (5.8, 1.6, 2.2), 0.8, 100),
    "bed2": ("bed2", "box", (5.8, 2.9, 2.4), 1.45, 100),
    "bed_rich": ("bed_rich", "box", (5.8, 2.8, 2.6), 1.4, 120),
    "arcade_cabinet": ("arcade_cabinet", "box", (1.3, 2.8, 1.2), 1.4, 45),
}

SOLID = 1 | 2 | 8 | 16 | 32 | 256 | 512 | 2048

TEMPLATE = """[gd_scene load_steps=4 format=3]

[ext_resource type="Script" path="res://src/spawnables/prop.gd" id="1"]
[ext_resource type="PackedScene" path="res://assets/models/{model}.glb" id="2"]

{shape_resource}

[node name="{name}" type="RigidBody3D"]
collision_layer = 32
collision_mask = {mask}
mass = {mass}
center_of_mass_mode = 1
center_of_mass = Vector3(0, {com}, 0)
angular_damp = 1.5
can_sleep = false
script = ExtResource("1")

[node name="Shape" type="CollisionShape3D" parent="."]
transform = Transform3D(1, 0, 0, 0, 1, 0, 0, 0, 1, 0, {cy}, 0)
shape = SubResource("shape")

[node name="Model" parent="." instance=ExtResource("2")]
"""


def shape_resource(kind, params):
    if kind == "box":
        return '[sub_resource type="BoxShape3D" id="shape"]\nsize = Vector3(%g, %g, %g)' % params
    if kind == "cylinder":
        return '[sub_resource type="CylinderShape3D" id="shape"]\nradius = %g\nheight = %g' % params
    raise ValueError(kind)


def main():
    for name, (model, kind, params, cy, mass) in PROPS.items():
        path = os.path.join(OUT, name + ".tscn")
        with open(path, "w") as f:
            f.write(TEMPLATE.format(model=model, name=name.title().replace("_", ""), mask=SOLID, mass=mass, cy=cy, com=round(cy * 0.45, 2),
                                    shape_resource=shape_resource(kind, params)))
        print("wrote", os.path.relpath(path, ROOT))


if __name__ == "__main__":
    main()
