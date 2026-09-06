class_name Skybridge
extends Node3D
## The skybridge: this storey's floor is sealed with steel, but a doorway in
## the right wall opens onto a neon bridge to the next tower. Gaps, fire,
## bumpers, a drone, a laser ring and a wall gun stand between the door and
## the lobby of the other building, where the fall continues.

const ROWS := 14                 ## storey height in rows; the deck is the floor row
const LENGTH := 48               ## deck cells
const DOOR_ROWS := 3
const GAPS := [[8, 3], [19, 3], [31, 4]]        ## [first cell, width]
const COIN_ARCS := [8, 19, 31, 40]
const BUMPERS := [14.5, 26.5]
const FIRE := [5.0, 37.5]
const DRONE_X := 23.0
const RING_X := 43.0
const GUN_X := 46.0

const BUMPER_SCENE := "res://src/spawnables/bumper.tscn"
const FIRE_SCENE := "res://src/spawnables/fire_zone.tscn"
const DRONE_SCENE := "res://src/spawnables/drone.tscn"
const RING_SCENE := "res://src/spawnables/light_ring.tscn"
const GUN_SCENE := "res://src/spawnables/wall_gun.tscn"

var coin_budget := 0
var _world: Node = null
var _level: Level = null
var _player: Player = null
var _entered := false
var _deck_y := 0.0

@onready var end_door: Area3D = $EndDoor
@onready var decor: Node3D = $Decor


func _ready() -> void:
	end_door.body_entered.connect(_on_end_door)


func set_world(world: Node) -> void:
	_world = world
	call_deferred("_build")


func _build() -> void:
	var roof := Grid.row_of(global_position.y)
	var deck_row := roof + ROWS
	_deck_y = -float(deck_row)
	for level in _world.levels:
		if level.roof == roof:
			_level = level
	# Seal the shaft, open the door, lay the deck.
	for cx in range(1, Grid.WALL_RIGHT):
		_world.cells.set_cell(cx, deck_row, CellGrid.Kind.STEEL)
	for row in range(deck_row - DOOR_ROWS, deck_row):
		_world.cells.remove_cell(Grid.WALL_RIGHT, row)
	var x0 := Grid.WALL_RIGHT + 1
	for i in LENGTH + 5:
		if not _in_gap(i):
			_world.cells.set_cell(x0 + i, deck_row, CellGrid.Kind.FLOOR)
	# The far tower's wall (behind its doorway) stops anyone overshooting.
	for row in range(deck_row - 10, deck_row + 1):
		_world.cells.set_cell(x0 + LENGTH + 5, row, CellGrid.Kind.STEEL)
	# Obstacles and coins along the deck.
	var value := maxi(coin_budget / 3, 1)
	for gx in COIN_ARCS:
		for k in 5:
			var t := k / 4.0
			var pos := Vector3(x0 + gx - 1.0 + t * 5.0, _deck_y + 1.6 + sin(t * PI) * 2.2, 0.0)
			_world.spawn_coin(value, pos)
	for bx in BUMPERS:
		_world.spawn_scene(BUMPER_SCENE, Vector3(x0 + bx, _deck_y, 0.0), {}, _level)
	for fx in FIRE:
		_world.spawn_scene(FIRE_SCENE, Vector3(x0 + fx, _deck_y + 0.9, 0.0), {}, _level)
	_world.spawn_scene(DRONE_SCENE, Vector3(x0 + DRONE_X, _deck_y + 2.6, 0.0), {"min_x": x0 + 16.0, "max_x": x0 + 30.0}, _level)
	_world.spawn_scene(RING_SCENE, Vector3(x0 + RING_X, _deck_y, 0.0), {}, _level)
	_world.spawn_scene(GUN_SCENE, Vector3(x0 + GUN_X, _deck_y + 4.0, 0.0), {"mirrored": true}, _level)


func _in_gap(i: int) -> bool:
	for gap in GAPS:
		if i >= gap[0] and i < gap[0] + gap[1]:
			return true
	return false


func _process(_delta: float) -> void:
	if _world == null or _world.tracked == null or _entered:
		return
	if _player == null:
		_player = _world.tracked as Player
		if _player == null:
			return
	var on_bridge := _player.position.x > Grid.INTERIOR_MAX_X and absf(_player.position.y - _deck_y) < 12.0
	_player.outside_ok = on_bridge
	if on_bridge and _player.position.y < _deck_y - 9.0:
		_player.outside_ok = false
		_player.insta_kill()


## Through the far door: fade out, step into the next tower's shaft just
## under this storey's sealed floor, fade back in.
func _on_end_door(body: Node) -> void:
	if _entered or not (body is Player):
		return
	_entered = true
	Sfx.play("door")
	var player := body as Player
	Game.blink(func():
		player.outside_ok = false
		player.position = Vector3(Grid.CENTER_X, _deck_y - 1.5, 0.0)
		player.velocity = Vector3.ZERO
		player.add_immunity(1.5)
		if _world.has_method("enter_next_building"):
			_world.enter_next_building()
		var rig := get_tree().get_first_node_in_group("camera_rig") as CameraRig
		if rig != null:
			rig.snap()
	)


func _exit_tree() -> void:
	if is_instance_valid(_player):
		_player.outside_ok = false
