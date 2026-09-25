extends Node
## Dev harness for the Neon Palace skybridge model: starts a game, renders
## the skybridge special level and parks the player on the deck at
## --x=<metres from the first deck cell> (default 12), so the camera shows
## that stretch of the bridge.
##   godot --path . res://src/dev/palace_skybridge.tscn -- --special=skybridge --x=40 --screenshot=x.png:4

var _game: GameScene


func _ready() -> void:
	var at := 12.0
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--x="):
			at = float(arg.trim_prefix("--x="))
	_game = load("res://src/game/game.tscn").instantiate()
	add_child(_game)
	await get_tree().process_frame
	var world := _game.world
	var roof: int = world.next_roof
	world.render_special_level()
	for i in 3:
		await get_tree().process_frame
	var deck_y := -float(roof + 14)
	var player := _game.player
	player.position = Vector3(Grid.WALL_RIGHT + 1 + at, deck_y + 0.6, 0.0)
	player.velocity = Vector3.ZERO
	player.add_immunity(60.0)
	_game.rig.snap()
	print("PALACE_SKYBRIDGE roof=", roof, " x=", at)
