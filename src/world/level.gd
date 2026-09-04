class_name Level
extends RefCounted
## One storey of the hotel: its rows, the occupancy grid used while placing
## props, and the props that must disappear with it.

const W := SpawnableSpec.Where

var roof: int                 ## row of the ceiling (= previous storey's floor)
var height: int               ## rows from roof to floor
var double_floor := false
var is_special := false
var grid: BinaryGrid
var bound_instances: Array[Node] = []
var backdrop: Node3D = null


func _init(p_roof: int, p_height: int) -> void:
	roof = p_roof
	height = p_height
	grid = BinaryGrid.new(Grid.WALL_RIGHT + 1, height + 2)


func floor_row() -> int:
	return roof + height


## Row the next storey's ceiling sits on.
func next_roof() -> int:
	return floor_row() + (1 if double_floor else 0)


func contains_row(row: float) -> bool:
	return row >= roof and row <= roof + height + 1


func bind(node: Node) -> void:
	bound_instances.append(node)


# ------------------------------------------------------------------ drawing --
func draw_walls(cells: CellGrid, difficulty: int) -> void:
	double_floor = difficulty >= 5
	for row in range(roof + 1, roof + height):
		cells.set_cell(0, row, CellGrid.Kind.FLOOR)
	var fl := floor_row()
	for cx in range(0, Grid.WALL_RIGHT):
		cells.set_cell(cx, fl, CellGrid.Kind.FLOOR)
		if double_floor:
			cells.set_cell(cx, fl + 1, CellGrid.Kind.FLOOR)
	for row in range(roof + 1, roof + height + 2):
		cells.set_cell(Grid.WALL_RIGHT, row, CellGrid.Kind.FLOOR)


## Cells (as top-left corners, level-relative rows) where a footprint fits.
func free_squares(where: int, w: int, h: int) -> Array[Vector2i]:
	var x0 := 1
	var x1 := Grid.WIDTH - w          # exclusive
	var y0 := 2
	var y1 := height - h              # exclusive
	match where:
		W.FLOOR:
			return grid.free_squares(x0, x1, height - h, height - h + 1, w, h)
		W.LEFT_WALL:
			return grid.free_squares(1, 2, y0, y1, w, h)
		W.RIGHT_WALL:
			return grid.free_squares(Grid.WIDTH - w, Grid.WIDTH - w + 1, y0, y1, w, h)
		W.ROOF:
			return grid.free_squares(x0, x1, 1, 2, w, h)
	return grid.free_squares(x0, x1, y0, y1, w, h)


## Tries every allowed placement in random order. Returns the node or null.
func place(spec: SpawnableSpec, coin_budget: int, world: Node) -> Node3D:
	var options := spec.where_options()
	options.shuffle()
	for where in options:
		var fp := spec.footprint(where)
		var squares := free_squares(where, fp.x, fp.y)
		if squares.is_empty():
			continue
		var cell := squares[randi() % squares.size()]
		grid.set_square(cell.x, cell.y, fp.x, fp.y)
		var rect := Rect2i(cell.x, roof + cell.y, fp.x, fp.y)
		var node := spec.spawn(where, rect, coin_budget)
		world.add_spawned(node, self if spec.bound_to_level else null)
		return node
	return null


func draw_spawnables(difficulty: int, coin_budget: int, specs: Array, world: Node) -> void:
	# Cheapest first, so the "affordable" prefix is contiguous.
	var pool: Array = []
	for spec in specs:
		pool.append([spec, spec.max_per_level])
	pool.sort_custom(func(a, b): return a[0].difficulty < b[0].difficulty)
	var budget := difficulty
	while budget > 0 and not pool.is_empty():
		var last := -1
		for i in pool.size():
			if pool[i][0].difficulty > budget:
				break
			last = i
		if last < 0:
			return
		var index := randi() % (last + 1)
		var entry: Array = pool[index]
		var node := place(entry[0], coin_budget, world)
		if node == null:
			pool.remove_at(index)
			continue
		budget -= entry[0].difficulty
		entry[1] -= 1
		if entry[1] == 0:
			pool.remove_at(index)


func draw_coins(coin_budget: int, world: Node) -> void:
	var budget := coin_budget
	while budget > 0:
		var value := randi_range(1, budget)
		var squares := free_squares(W.FLOATING, 1, 1)
		if squares.is_empty():
			return
		var cell := squares[randi() % squares.size()]
		grid.set_square(cell.x, cell.y, 1, 1)
		world.spawn_coin(value, Grid.cell_center(cell.x, roof + cell.y))
		budget -= value


func clear(cells: CellGrid) -> void:
	cells.clear_rows(roof + 1, next_roof() if not is_special else roof + height + 2)
	for node in bound_instances:
		if is_instance_valid(node):
			node.queue_free()
	bound_instances.clear()
	if is_instance_valid(backdrop):
		backdrop.queue_free()
	backdrop = null
