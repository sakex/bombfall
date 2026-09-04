class_name Ledge
extends StaticBody3D
## A floating platform of the obstacle course, sized in cells.

static var _material: Material = null


static func make(x: float, top_y: float, width: float, height: float = 1.0) -> Ledge:
	var ledge := Ledge.new()
	ledge.collision_layer = Layers.WORLD
	ledge.collision_mask = 0
	var shape := CollisionShape3D.new()
	var box := BoxShape3D.new()
	box.size = Vector3(width, height, Grid.DEPTH)
	shape.shape = box
	ledge.add_child(shape)
	var mesh := MeshInstance3D.new()
	var bm := BoxMesh.new()
	bm.size = Vector3(width, height, Grid.DEPTH)
	mesh.mesh = bm
	mesh.material_override = _ledge_material()
	ledge.add_child(mesh)
	var trim := MeshInstance3D.new()
	var tm := BoxMesh.new()
	tm.size = Vector3(width - 0.1, 0.06, 0.06)
	trim.mesh = tm
	var glow := StandardMaterial3D.new()
	glow.emission_enabled = true
	glow.emission = Color(1.0, 0.4, 0.75)
	glow.emission_energy_multiplier = 3.0
	glow.albedo_color = Color(0.3, 0.1, 0.2)
	trim.material_override = glow
	trim.position = Vector3(0.0, height * 0.5 - 0.15, Grid.DEPTH * 0.5 + 0.03)
	ledge.add_child(trim)
	ledge.position = Vector3(x + width * 0.5, top_y - height * 0.5, 0.0)
	return ledge


static func _ledge_material() -> Material:
	if _material == null:
		var m := StandardMaterial3D.new()
		m.albedo_color = Color(0.16, 0.16, 0.22)
		m.metallic = 0.6
		m.roughness = 0.45
		_material = m
	return _material
