class_name CellGrid
extends Node3D
## The destructible cells of the hotel (floors, walls, junk).
##
## Visuals go through one MultiMesh per cell kind and band of rows (so the
## storeys above and below the screen get frustum-culled instead of drawn),
## collisions through one static body per cell created directly on the
## PhysicsServer, so a level costs almost no scene nodes and an explosion
## can punch a hole by simply dropping a few cells.

enum Kind { FLOOR, JUNK, STEEL }

const MODELS := {
	Kind.FLOOR: "res://assets/models/tile_floor.glb",
	Kind.JUNK: "res://assets/models/tile_junk.glb",
	Kind.STEEL: "res://assets/models/tile_steel.glb",
}
## Blasts a cell can take before it goes.
const HIT_POINTS := {Kind.FLOOR: 1, Kind.JUNK: 1, Kind.STEEL: 3}
## Rows per MultiMesh band; one band holds at most BAND_ROWS * 17 cells.
const BAND_ROWS := 12
const BAND_CAPACITY := BAND_ROWS * (Grid.WALL_RIGHT + 1)

class Cell:
	var kind: int
	var body: RID
	var instance: int
	var chunk: Chunk
	var hp: int = 1


## One MultiMesh: a kind of cell within a band of rows.
class Chunk:
	var multimesh: MultiMesh
	var node: MultiMeshInstance3D
	var free_slots: Array[int] = []
	var used := 0
	var hidden: Transform3D


var _cells: Dictionary = {}          # Vector2i(cx, row) -> Cell
var _meshes: Dictionary = {}         # Kind -> Mesh
var _chunks: Dictionary = {}         # Vector2i(kind, band) -> Chunk
var _shape: RID
var _space: RID


func _ready() -> void:
	_space = get_world_3d().space
	_shape = PhysicsServer3D.box_shape_create()
	PhysicsServer3D.shape_set_data(_shape, Vector3(Grid.CELL, Grid.CELL, Grid.DEPTH) * 0.5)
	for kind in MODELS:
		_meshes[kind] = _extract_mesh(MODELS[kind])


static func _band_of(row: int) -> int:
	return int(floor(float(row) / BAND_ROWS))


## The chunk drawing [param kind] cells in [param row]'s band, made on demand.
func _chunk_for(kind: int, row: int) -> Chunk:
	var band := _band_of(row)
	var key := Vector2i(kind, band)
	if _chunks.has(key):
		return _chunks[key]
	var chunk := Chunk.new()
	chunk.multimesh = MultiMesh.new()
	chunk.multimesh.transform_format = MultiMesh.TRANSFORM_3D
	chunk.multimesh.mesh = _meshes[kind]
	chunk.multimesh.instance_count = BAND_CAPACITY
	# Hidden instances collapse to a point inside the band so the chunk's
	# bounds stay tight and it can be culled when the band scrolls away.
	chunk.hidden = Transform3D(Basis().scaled(Vector3.ZERO), Grid.cell_center(int(Grid.CENTER_X), band * BAND_ROWS + BAND_ROWS / 2))
	for i in BAND_CAPACITY:
		chunk.multimesh.set_instance_transform(i, chunk.hidden)
	chunk.free_slots.resize(BAND_CAPACITY)
	for i in BAND_CAPACITY:
		chunk.free_slots[i] = BAND_CAPACITY - 1 - i
	chunk.node = MultiMeshInstance3D.new()
	chunk.node.multimesh = chunk.multimesh
	chunk.node.name = "Cells%d_%d" % [kind, band]
	add_child(chunk.node)
	_chunks[key] = chunk
	return chunk


func _release_chunk(kind: int, row: int) -> void:
	var key := Vector2i(kind, _band_of(row))
	var chunk: Chunk = _chunks[key]
	chunk.node.queue_free()
	_chunks.erase(key)


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
	var chunk := _chunk_for(kind, row)
	if chunk.free_slots.is_empty():
		push_warning("CellGrid band is full; cell %s dropped" % key)
		return
	var cell := Cell.new()
	cell.kind = kind
	cell.hp = HIT_POINTS.get(kind, 1)
	cell.chunk = chunk
	cell.instance = chunk.free_slots.pop_back()
	chunk.used += 1
	var xform := Transform3D(Basis(), Grid.cell_center(cx, row))
	chunk.multimesh.set_instance_transform(cell.instance, xform)
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
	cell.chunk.multimesh.set_instance_transform(cell.instance, cell.chunk.hidden)
	cell.chunk.free_slots.append(cell.instance)
	cell.chunk.used -= 1
	if cell.chunk.used == 0:
		_release_chunk(cell.kind, row)
	PhysicsServer3D.free_rid(cell.body)
	_cells.erase(key)
	return true


## Blasts every cell whose centre lies within [param radius] of [param center];
## cells with hit points left are only damaged. [param blast_id] lets one
## explosion damage a tough cell once rather than every frame it grows.
## Returns how many cells were destroyed.
func destroy_in_sphere(center: Vector3, radius: float, blast_id: int = 0) -> int:
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
				var cell: Cell = _cells[Vector2i(cx, row)]
				if cell.hp > 1:
					if blast_id != 0 and _hit_by.get(Vector2i(cx, row), 0) == blast_id:
						continue
					_hit_by[Vector2i(cx, row)] = blast_id
					cell.hp -= 1
					_shake(cell)
					continue
				_hit_by.erase(Vector2i(cx, row))
				remove_cell(cx, row)
				destroyed += 1
	return destroyed


var _hit_by: Dictionary = {}


## Nudges a damaged cell's instance so the hit reads visually.
func _shake(cell: Cell) -> void:
	Sfx.play("steel_hit")
	var mm: MultiMesh = cell.chunk.multimesh
	var xform: Transform3D = mm.get_instance_transform(cell.instance)
	xform.basis = Basis().rotated(Vector3.FORWARD, randf_range(-0.12, 0.12)).scaled(Vector3(0.94, 0.94, 0.94))
	mm.set_instance_transform(cell.instance, xform)


## Clears every cell in rows row0..row1 (inclusive).
func clear_rows(row0: int, row1: int) -> void:
	for key in _cells.keys():
		if key.y >= row0 and key.y <= row1:
			remove_cell(key.x, key.y)


func cell_count() -> int:
	return _cells.size()
