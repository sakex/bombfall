extends Node3D
## Developer scene: a few hand-built floors with bombs and coins, used to
## smoke-test physics headlessly and to screenshot the look of the assets.
## Run with: godot --path . res://src/dev/sandbox.tscn
## Add --screenshot=path.png to save a frame after a couple of seconds.

const BOMB := preload("res://src/actors/bomb.tscn")
const COIN := preload("res://src/actors/coin.tscn")

@onready var cells: CellGrid = $CellGrid
@onready var player: Player = $Player
@onready var rig: CameraRig = $CameraRig

var _shot_path := ""
var _elapsed := 0.0


func _ready() -> void:
	rig.target = player
	for level in 3:
		var roof := level * 12
		for row in range(roof + 1, roof + 12):
			cells.set_cell(0, row, CellGrid.Kind.FLOOR)
			cells.set_cell(16, row, CellGrid.Kind.FLOOR)
		for cx in range(0, 17):
			if level == 0 and cx >= 6 and cx <= 8:
				continue
			cells.set_cell(cx, roof + 12, CellGrid.Kind.FLOOR if level != 1 else CellGrid.Kind.JUNK)
	player.position = Vector3(Grid.CENTER_X, -2.0, 0.0)
	player.set_max_shields(3)
	player.set_active_shields(2)
	var bomb: Bomb = BOMB.instantiate()
	bomb.position = Vector3(4.0, -3.0, 0.0)
	bomb.bomb_time = 2.5
	bomb.bomb_scale = 0.8
	add_child(bomb)
	var bomb2: Bomb = BOMB.instantiate()
	bomb2.position = Vector3(12.0, -6.0, 0.0)
	bomb2.no_timeout = true
	add_child(bomb2)
	for i in 6:
		var coin: Coin = COIN.instantiate()
		coin.position = Vector3(3.0 + i * 2.0, -8.0, 0.0)
		coin.value = i
		add_child(coin)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screenshot="):
			_shot_path = arg.trim_prefix("--screenshot=")
	$Hud.bind_player(player)
	rig.snap()


func _process(delta: float) -> void:
	_elapsed += delta
	if _shot_path != "" and _elapsed > 2.5:
		var img := get_viewport().get_texture().get_image()
		img.save_png(_shot_path)
		print("SCREENSHOT ", _shot_path, " cells=", cells.cell_count(), " player=", player.position)
		_shot_path = ""
		get_tree().quit()
