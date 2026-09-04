extends Node
## Headless regression run: plays the real game scene for a while with a
## scripted player, exploding bombs and generating storeys, then reports.
##   godot --headless --path . res://src/dev/smoke_test.tscn

const FRAMES := 60 * 40

var _game: GameScene
var _frame := 0
var _min_y := 0.0
var _start_cells := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	_game = load("res://src/game/game.tscn").instantiate()
	add_child(_game)
	_game.record_scores = false
	await get_tree().process_frame
	_start_cells = _game.world.cells.cell_count()


func _physics_process(_delta: float) -> void:
	if _game == null or not is_instance_valid(_game.player):
		return
	var player := _game.player
	var world := _game.world
	var t := _frame / 60.0
	var right := fmod(t, 6.0) < 3.0
	Input.action_press("move_right" if right else "move_left")
	Input.action_release("move_left" if right else "move_right")
	if _frame % 90 == 0:
		Input.action_press("jump")
	elif _frame % 90 == 5:
		Input.action_release("jump")
	if _frame % 120 == 0:
		player.add_immunity(3.0)  # keep the run alive through the blasts
	_min_y = minf(_min_y, player.position.y)
	if _game.death_screen.visible:
		print("SMOKE_DEATH at t=%.1fs y=%.1f x=%.1f score=%d" % [t, player.position.y, player.position.x, player.score])
		get_tree().paused = false
		player.revive()
		_game.death_screen.visible = false
	if _frame % 600 == 0:
		print("t=%ds y=%.1f descended=%d cells=%d props=%d bombs=%d coins=%d" % [
			int(t), player.position.y, world.levels_descended, world.cells.cell_count(),
			world.get_node("Props").get_child_count(), get_tree().get_nodes_in_group("bombs").size(),
			get_tree().get_nodes_in_group("coins").size()])
	_frame += 1
	if _frame >= FRAMES:
		print("SMOKE_RESULT start_cells=%d min_y=%.1f descended=%d difficulty=%d score=%d alive_levels=%d" % [
			_start_cells, _min_y, world.levels_descended, world.difficulty, player.score, world.levels.size()])
		get_tree().quit()
