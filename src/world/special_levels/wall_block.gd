class_name WallBlockLevel
extends SpecialLevel
## A storey packed solid with junk. Bombs, coins and a magnet are buried in
## pockets; the player has to blast a way through.

const SIZE := 16


func draw(world: Node, roof: int, coin_budget: int) -> Level:
	var level := Level.new(roof, SIZE)
	level.is_special = true
	var grid := BinaryGrid.new(Grid.WALL_RIGHT + 1, SIZE)
	var bomb := SpawnRegistry.spec("bomb")
	var magnet := SpawnRegistry.spec("magnet")
	# Bombs in 4x4 pockets.
	for i in randi_range(1, 4):
		var cell := _reserve(grid, 4, 4)
		if cell.x < 0:
			break
		if bomb != null:
			world.add_spawned(bomb.spawn(SpawnableSpec.Where.FLOATING, Rect2i(cell.x, roof + cell.y, 4, 4), coin_budget), level)
	# Coins in 1x1 pockets.
	for i in randi_range(5, 10):
		var cell := _reserve(grid, 1, 1)
		if cell.x < 0:
			break
		world.spawn_coin(coin_budget, Grid.cell_center(cell.x, roof + cell.y))
	# One magnet in a 2x3 pocket.
	var mcell := _reserve(grid, 2, 3)
	if mcell.x >= 0 and magnet != null:
		world.add_spawned(magnet.spawn(SpawnableSpec.Where.FLOOR, Rect2i(mcell.x, roof + mcell.y, 2, 3), coin_budget), level)
	# Fill everything else with junk.
	for y in SIZE:
		for x in range(0, Grid.WALL_RIGHT + 1):
			if grid.is_cell_free(x, y):
				world.cells.set_cell(x, roof + y, CellGrid.Kind.JUNK)
	return level


func _reserve(grid: BinaryGrid, w: int, h: int) -> Vector2i:
	var squares := grid.free_squares(1, 15, 1, SIZE - h, w, h)
	if squares.is_empty():
		return Vector2i(-1, -1)
	var cell := squares[randi() % squares.size()]
	grid.set_square(cell.x, cell.y, w, h)
	return cell


func advance_rows() -> int:
	return SIZE - 1
