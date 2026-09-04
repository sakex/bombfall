class_name SceneLevel
extends SpecialLevel
## A special storey built from a hand-made scene (obstacle course, boss
## arena). The scene's origin sits at the roof row's top-left corner; it may
## expose `coin_budget` and `set_world(world)`.

var scene_path: String
var height: int
var rows: int
var floor_row_offset: int


func _init(p_scene: String, p_height: int, p_rows: int, p_floor_offset: int = -1) -> void:
	scene_path = p_scene
	height = p_height
	rows = p_rows
	floor_row_offset = p_floor_offset


func available() -> bool:
	return ResourceLoader.exists(scene_path)


const ARENA_THEME := {"id": "arena", "wall": Color(0.12, 0.08, 0.2), "trim": Color(0.9, 0.3, 0.6), "floor": Color(0.16, 0.1, 0.24)}


func draw(world: Node, roof: int, coin_budget: int) -> Level:
	var level := Level.new(roof, height)
	level.is_special = true
	for row in range(roof + 1, roof + rows + 1):
		world.cells.set_cell(0, row, CellGrid.Kind.FLOOR)
		world.cells.set_cell(Grid.WALL_RIGHT, row, CellGrid.Kind.FLOOR)
	level.backdrop = Backdrop.build(ARENA_THEME, roof, rows + 1)
	world.add_child(level.backdrop)
	var node: Node3D = (load(scene_path) as PackedScene).instantiate()
	node.position = Grid.cell_corner(0, roof)
	if "coin_budget" in node:
		node.set("coin_budget", coin_budget)
	world.add_spawned(node, level)
	if floor_row_offset >= 0:
		for cx in range(0, Grid.WALL_RIGHT + 1):
			world.cells.set_cell(cx, roof + floor_row_offset, CellGrid.Kind.FLOOR)
	return level


func advance_rows() -> int:
	return rows
