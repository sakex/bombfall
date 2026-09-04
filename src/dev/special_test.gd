extends Node
## Dev harness: starts a game, immediately generates the special level named
## by --special=<name> as the next storey and drops the player into it.
##   godot --path . res://src/dev/special_test.tscn -- --special=boss_bat_arena --screenshot=x.png:4

var _game: GameScene


func _ready() -> void:
	_game = load("res://src/game/game.tscn").instantiate()
	add_child(_game)
	await get_tree().process_frame
	var world := _game.world
	var roof := world.next_roof
	world.render_special_level()
	_game.player.position = Vector3(Grid.CENTER_X, -(roof + 1.5), 0.0)
	_game.player.add_immunity(60.0)
	_game.rig.snap()
	print("SPECIAL at roof ", roof, " levels=", world.levels.size())
