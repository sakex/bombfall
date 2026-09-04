class_name CellGrid
extends Node3D
## The destructible cells of the hotel (floors, walls, junk).
##
## Visuals go through one MultiMesh per cell kind, collisions through one
## static body per cell created directly on the PhysicsServer, so a level
## costs no scene nodes at all and an explosion can punch a hole by simply
## dropping a few cells.

enum Kind { FLOOR, JUNK }

const MODELS := {
	Kind.FLOOR: "res://assets/models/tile_floor.glb",
	Kind.JUNK: "res://assets/models/tile_junk.glb",
}
const CAPACITY := 1024

class Cell:
	var kind: int
	var body: RID
	var instance: int


var _cells: Dictionary = {}          # Vector2i(cx, row) -> Cell
var _multimeshes: Dictionary = {}    # Kind -> MultiMesh
var _free_slots: Dictionary = {}     # Kind -> Array[int]
var _shape: RID
var _space: RID


func _ready() -> void:
	_space = get_world_3d().space
	_shape = PhysicsServer3D.box_shape_create()
	PhysicsServer3D.shape_set_data(_shape, Vector3(Grid.CELL, Grid.CELL, Grid.DEPTH) * 0.5)
	for kind in MODELS:
		var mesh := _extract_mesh(MODELS[kind])
		var mm := MultiMesh.new()
		mm.transform_format = MultiMesh.TRANSFORM_3D
		mm.mesh = mesh
		mm.instance_count = CAPACITY
		var hidden := Transform3D().scaled(Vector3.ZERO)
		for i in CAPACITY:
			mm.set_instance_transform(i, hidden)
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.name = "Cells%d" % kind
		add_child(mmi)
		_multimeshes[kind] = mm
		var slots: Array[int] = []
		slots.resize(CAPACITY)
		for i in CAPACITY:
			slots[i] = CAPACITY - 1 - i
		_free_slots[kind] = slots


func _exit_tree() -> void:
	for key in _cells:
		PhysicsServer3D.free_rid(_cells[key].body)
	_cells.clear()
	if _shape.is_valid():
		PhysicsServer3D.free_rid(_shape)


static func _extract_mesh(path: String) -> Mesh:
	var scene: PackedScene = load(path)
	var root := scene.instantiate()
	var found: Mesh = null
	var stack: Array[Node] = [root]
	while not stack.is_empty() and found == null:
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			found = (n as MeshInstance3D).mesh
		stack.append_array(n.get_children())
	root.free()
	return found


func has_cell(cx: int, row: int) -> bool:
	return _cells.has(Vector2i(cx, row))


func set_cell(cx: int, row: int, kind: int) -> void:
	var key := Vector2i(cx, row)
	if _cells.has(key):
		if _cells[key].kind == kind:
			return
		remove_cell(cx, row)
	var slots: Array[int] = _free_slots[kind]
	if slots.is_empty():
		push_warning("CellGrid is full; cell %s dropped" % key)
		return
	var cell := Cell.new()
	cell.kind = kind
	cell.instance = slots.pop_back()
	var xform := Transform3D(Basis(), Grid.cell_center(cx, row))
	_multimeshes[kind].set_instance_transform(cell.instance, xform)
	cell.body = PhysicsServer3D.body_create()
	PhysicsServer3D.body_set_mode(cell.body, PhysicsServer3D.BODY_MODE_STATIC)
	PhysicsServer3D.body_set_space(cell.body, _space)
	PhysicsServer3D.body_add_shape(cell.body, _shape)
	PhysicsServer3D.body_set_state(cell.body, PhysicsServer3D.BODY_STATE_TRANSFORM, xform)
	# Areas and rays report this node as the collider of every cell.
	PhysicsServer3D.body_attach_object_instance_id(cell.body, get_instance_id())
	PhysicsServer3D.body_set_collision_layer(cell.body, Layers.WORLD)
	PhysicsServer3D.body_set_collision_mask(cell.body, Layers.SOLID)
	_cells[key] = cell


func remove_cell(cx: int, row: int) -> bool:
	var key := Vector2i(cx, row)
	if not _cells.has(key):
		return false
	var cell: Cell = _cells[key]
	_multimeshes[cell.kind].set_instance_transform(cell.instance, Transform3D().scaled(Vector3.ZERO))
	_free_slots[cell.kind].append(cell.instance)
	PhysicsServer3D.free_rid(cell.body)
	_cells.erase(key)
	return true


## Removes every cell whose centre lies within [param radius] of [param center].
## Returns how many cells were destroyed.
func destroy_in_sphere(center: Vector3, radius: float) -> int:
	var destroyed := 0
	var c0 := Grid.col_of(center.x - radius) - 1
	var c1 := Grid.col_of(center.x + radius) + 1
	var r0 := Grid.row_of(center.y + radius) - 1
	var r1 := Grid.row_of(center.y - radius) + 1
	var reach := radius + Grid.CELL * 0.5
	for row in range(r0, r1 + 1):
		for cx in range(c0, c1 + 1):
			if not _cells.has(Vector2i(cx, row)):
				continue
			var p := Grid.cell_center(cx, row)
			if Vector2(p.x, p.y).distance_to(Vector2(center.x, center.y)) <= reach:
				remove_cell(cx, row)
				destroyed += 1
	return destroyed


## Clears every cell in rows row0..row1 (inclusive).
func clear_rows(row0: int, row1: int) -> void:
	for key in _cells.keys():
		if key.y >= row0 and key.y <= row1:
			remove_cell(key.x, key.y)


func cell_count() -> int:
	return _cells.size()
