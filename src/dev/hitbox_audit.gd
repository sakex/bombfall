extends Node
## Hitbox audit, run headlessly:
##   godot --headless --path . res://src/dev/hitbox_audit.tscn
## Instantiates every spawnable (plus the bomb and the coin) and, for each
## physics body / area in it, compares the merged bounding box of its meshes
## with the box covered by its collision shapes (both in the body's space).
## Prints one row per body and flags shapes that are noticeably smaller,
## larger or offset on X/Y, or whose base does not sit on the mesh's base.
## Area rows are informational (triggers rarely match a mesh) and are not
## counted in the final HITBOX_RESULT line; neither are meshes that are meant
## to stick out of the shape (flames, antennas, a bomb's fuse, a table's
## candle, a pickup's floating item).

const SCENE_DIRS := ["res://src/spawnables/"]
const EXTRA_SCENES := ["res://src/actors/bomb.tscn", "res://src/actors/coin.tscn"]
const SKIP := ["rope.tscn"]
## Relative tolerance on the X/Y extents and on the centre offset.
const TOLERANCE := 0.15
const MIN_OFFSET := 0.12
const BASE_TOLERANCE := 0.12

var _flags := 0
var _rows := 0


func _ready() -> void:
	seed(1)
	PhysicsServer3D.set_active(false)
	var paths: Array[String] = []
	for dir in SCENE_DIRS:
		var files := ResourceLoader.list_directory(dir)
		files.sort()
		for f in files:
			if f.ends_with(".tscn") and not SKIP.has(f):
				paths.append(dir + f)
	paths.append_array(EXTRA_SCENES)
	print("%-24s %-14s %-32s %-32s %s" % ["scene", "body", "mesh aabb (min..max x|y|z)", "shape aabb", "flags"])
	for path in paths:
		await _audit_scene(path)
	print("HITBOX_RESULT rows=%d flags=%d" % [_rows, _flags])
	get_tree().quit()


func _audit_scene(path: String) -> void:
	var packed: PackedScene = load(path)
	if packed == null:
		print("%s: cannot load" % path)
		return
	var node := packed.instantiate() as Node3D
	if node == null:
		return
	if "random_flip" in node:
		node.set("random_flip", false)
	if "play_start_sound" in node:
		node.set("play_start_sound", false)
	add_child(node)
	await get_tree().physics_frame
	await get_tree().physics_frame
	var scene_name := path.get_file().get_basename()
	for obj in _collision_objects(node):
		if obj is RopeLink and scene_name != "rope_link":
			continue
		_audit_body(scene_name, obj)
	node.queue_free()
	await get_tree().process_frame


func _collision_objects(root: Node) -> Array[CollisionObject3D]:
	var out: Array[CollisionObject3D] = []
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_front()
		if n is CollisionObject3D:
			out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


## The meshes that visually belong to [param body]: every MeshInstance3D below
## it whose nearest CollisionObject3D ancestor is the body itself.
func _meshes_of(body: CollisionObject3D) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	var stack: Array[Node] = []
	for c in body.get_children():
		stack.append(c)
	if body is Area3D and _owns_area(body.get_parent()):
		for c in body.get_parent().get_children():
			if c != body:
				stack.append(c)
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is CollisionObject3D or _owns_area(n):
			continue
		if n is MeshInstance3D and (n as MeshInstance3D).mesh != null and (n as MeshInstance3D).visible:
			out.append(n)
		for c in n.get_children():
			stack.append(c)
	return out


## A plain node grouping a model with its own Area3D (a pickup's floating
## item): its meshes are the area's, not the body's.
func _owns_area(n: Node) -> bool:
	if n is CollisionObject3D or n is MeshInstance3D:
		return false
	for c in n.get_children():
		if c is Area3D:
			return true
	return false


func _aabb_in(space: Transform3D, local: AABB, xform: Transform3D) -> AABB:
	var rel := space.affine_inverse() * xform
	var result := AABB()
	for i in 8:
		var p := rel * local.get_endpoint(i)
		if i == 0:
			result = AABB(p, Vector3.ZERO)
		else:
			result = result.expand(p)
	return result


## Exact bounds of a mesh's vertices in [param space]; the local AABB of a
## mesh joined in a rotated frame would otherwise be inflated.
func _vertex_aabb(space: Transform3D, m: MeshInstance3D) -> AABB:
	var rel := space.affine_inverse() * m.global_transform
	var result := AABB()
	var first := true
	for i in m.mesh.get_surface_count():
		var arrays := m.mesh.surface_get_arrays(i)
		if arrays.is_empty():
			continue
		var verts: PackedVector3Array = arrays[Mesh.ARRAY_VERTEX]
		for v in verts:
			var p := rel * v
			if first:
				result = AABB(p, Vector3.ZERO)
				first = false
			else:
				result = result.expand(p)
	if first:
		return _aabb_in(space, m.mesh.get_aabb(), m.global_transform)
	return result


func _shape_local_aabb(shape: Shape3D) -> AABB:
	if shape is BoxShape3D:
		var s: Vector3 = (shape as BoxShape3D).size
		return AABB(-s * 0.5, s)
	if shape is SphereShape3D:
		var r: float = (shape as SphereShape3D).radius
		return AABB(Vector3(-r, -r, -r), Vector3(r, r, r) * 2.0)
	if shape is CylinderShape3D:
		var c := shape as CylinderShape3D
		return AABB(Vector3(-c.radius, -c.height * 0.5, -c.radius), Vector3(c.radius * 2.0, c.height, c.radius * 2.0))
	if shape is CapsuleShape3D:
		var k := shape as CapsuleShape3D
		return AABB(Vector3(-k.radius, -k.height * 0.5, -k.radius), Vector3(k.radius * 2.0, k.height, k.radius * 2.0))
	return AABB()


func _merge(a: AABB, b: AABB, first: bool) -> AABB:
	return b if first else a.merge(b)


func _audit_body(scene_name: String, body: CollisionObject3D) -> void:
	var space := body.global_transform
	var mesh_box := AABB()
	var has_mesh := false
	for m in _meshes_of(body):
		mesh_box = _merge(mesh_box, _vertex_aabb(space, m), not has_mesh)
		has_mesh = true
	var shape_box := AABB()
	var has_shape := false
	for c in body.get_children():
		if c is CollisionShape3D and not (c as CollisionShape3D).disabled and (c as CollisionShape3D).shape != null:
			var cs := c as CollisionShape3D
			shape_box = _merge(shape_box, _aabb_in(space, _shape_local_aabb(cs.shape), cs.global_transform), not has_shape)
			has_shape = true
	var flags: Array[String] = []
	if has_mesh and has_shape:
		for axis in [0, 1]:
			var name := "x" if axis == 0 else "y"
			var ms: float = mesh_box.size[axis]
			var ss: float = shape_box.size[axis]
			if ms > 0.05:
				if ss < ms * (1.0 - TOLERANCE):
					flags.append("%s-small(%.0f%%)" % [name, ss / ms * 100.0])
				elif ss > ms * (1.0 + TOLERANCE):
					flags.append("%s-large(%.0f%%)" % [name, ss / ms * 100.0])
			var off: float = absf(shape_box.get_center()[axis] - mesh_box.get_center()[axis])
			if off > maxf(ms * TOLERANCE, MIN_OFFSET):
				flags.append("%s-offset(%+.2f)" % [name, shape_box.get_center()[axis] - mesh_box.get_center()[axis]])
		if absf(shape_box.position.y - mesh_box.position.y) > BASE_TOLERANCE:
			flags.append("base(%+.2f)" % (shape_box.position.y - mesh_box.position.y))
	elif has_shape and not has_mesh:
		flags.append("no-mesh")
	elif has_mesh and not has_shape:
		flags.append("no-shape")
	var kind := "rigid" if body is RigidBody3D else ("static" if body is StaticBody3D else ("area" if body is Area3D else "other"))
	print("%-24s %-14s %-32s %-32s %s" % [scene_name, "%s[%s]" % [body.name, kind], _fmt(mesh_box) if has_mesh else "-", _fmt(shape_box) if has_shape else "-", " ".join(flags)])
	_rows += 1
	if not flags.is_empty() and body is PhysicsBody3D:
		_flags += 1


func _fmt(b: AABB) -> String:
	var e := b.end
	return "%.2f..%.2f|%.2f..%.2f|%.2f..%.2f" % [b.position.x, e.x, b.position.y, e.y, b.position.z, e.z]
