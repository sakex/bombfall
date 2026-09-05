extends Node
## Physics regression scenarios, run headlessly:
##   godot --headless --path . res://src/dev/physics_test.tscn
## Each scenario builds a small arena (floor at row 5 unless noted), runs a
## number of physics frames while scripting the player, then checks a fact
## about the world. Prints one PASS/FAIL line per scenario.

const BOMB := preload("res://src/actors/bomb.tscn")
const COIN := preload("res://src/actors/coin.tscn")
const PLAYER := preload("res://src/actors/player.tscn")

var _arena: Node3D
var _cells: CellGrid
var _player: Player
var _failures := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	await _scenario_land()
	await _scenario_wall()
	await _scenario_bomb_hole()
	await _scenario_coin()
	await _scenario_rope()
	await _scenario_trampoline()
	await _scenario_pickup()
	await _scenario_push()
	await _scenario_wall_gun()
	await _scenario_treadmill()
	await _scenario_drone()
	await _scenario_button()
	await _scenario_light_ring()
	print("PHYSICS_RESULT failures=%d" % _failures)
	get_tree().quit()


# ------------------------------------------------------------- helpers --
func _build(floor_row: int = 5, hole: Array = []) -> void:
	if _arena != null:
		_arena.queue_free()
		await get_tree().process_frame
	_release_all()
	_arena = Node3D.new()
	add_child(_arena)
	_cells = CellGrid.new()
	_cells.add_to_group("cell_grid")
	_arena.add_child(_cells)
	for row in range(0, floor_row + 6):
		_cells.set_cell(0, row, CellGrid.Kind.FLOOR)
		_cells.set_cell(16, row, CellGrid.Kind.FLOOR)
	for cx in range(0, 17):
		if hole.has(cx):
			continue
		_cells.set_cell(cx, floor_row, CellGrid.Kind.FLOOR)
	_player = PLAYER.instantiate()
	_player.play_start_sound = false
	_player.position = Vector3(8.5, -2.0, 0.0)
	_arena.add_child(_player)


func _frames(n: int) -> void:
	for i in n:
		await get_tree().physics_frame


func _release_all() -> void:
	for a in ["move_left", "move_right", "jump"]:
		Input.action_release(a)


func _check(name: String, ok: bool, detail: String = "") -> void:
	if ok:
		print("PASS %s %s" % [name, detail])
	else:
		_failures += 1
		print("FAIL %s %s" % [name, detail])


func _add(scene: PackedScene, pos: Vector3, props: Dictionary = {}) -> Node3D:
	var n: Node3D = scene.instantiate()
	n.position = pos
	for k in props:
		n.set(k, props[k])
	_arena.add_child(n)
	return n


# ----------------------------------------------------------- scenarios --
func _scenario_land() -> void:
	await _build()
	await _frames(180)
	_check("land", _player.is_on_floor() and absf(_player.position.y + 5.0) < 0.06 and absf(_player.position.x - 8.5) < 0.2,
		"y=%.3f x=%.2f floor=%s" % [_player.position.y, _player.position.x, _player.is_on_floor()])


func _scenario_wall() -> void:
	await _build()
	_player.position.x = 2.5
	await _frames(60)
	Input.action_press("move_left")
	await _frames(150)
	_release_all()
	_check("wall_left", _player.position.x > 1.3 and _player.position.x < 1.5, "x=%.3f" % _player.position.x)
	Input.action_press("move_right")
	await _frames(240)
	_release_all()
	_check("wall_right", _player.position.x < 15.7 and _player.position.x > 15.5, "x=%.3f" % _player.position.x)


func _scenario_bomb_hole() -> void:
	await _build(5)
	_player.position.x = 13.5
	var before := _cells.cell_count()
	var bomb := _add(BOMB, Vector3(5.5, -2.0, 0.0), {"bomb_time": 1.0})
	await _frames(60)
	_check("bomb_rests", is_instance_valid(bomb) and bomb.position.y > -3.4 and bomb.position.y < -3.1, "y=%.2f" % (bomb.position.y if is_instance_valid(bomb) else 999.0))
	await _frames(120)
	var destroyed := before - _cells.cell_count()
	_check("bomb_hole", destroyed >= 5 and destroyed <= 12 and not _cells.has_cell(5, 5), "destroyed=%d" % destroyed)
	_check("bomb_gone", not is_instance_valid(bomb))
	# Now walk into the hole.
	Input.action_press("move_left")
	await _frames(200)
	_release_all()
	_check("fall_through_hole", _player.position.y < -6.0, "y=%.2f x=%.2f" % [_player.position.y, _player.position.x])


func _scenario_coin() -> void:
	await _build()
	var coin := _add(COIN, Vector3(11.0, -3.5, 0.0), {"value": 3})
	await _frames(60)
	Input.action_press("move_right")
	await _frames(90)
	_release_all()
	_check("coin_pickup", _player.score == 3 and not is_instance_valid(coin), "score=%d" % _player.score)


func _scenario_rope() -> void:
	await _build(12)
	var roped := _add(load("res://src/spawnables/roped_bomb.tscn"), Vector3(9.0, -3.0, 0.0))
	await _frames(240)
	var bomb: Node3D = roped.get_node("Bomb")
	var links := roped.get_node("Rope").get_child_count()
	_check("rope_holds", bomb.position.y > -9.5 and bomb.position.y < -3.0 and links >= 6, "bomb_y=%.2f rope_children=%d" % [bomb.position.y, links])
	var anchor_x := 1.0
	_check("rope_length", bomb.global_position.distance_to(Vector3(anchor_x, -3.0, 0.0)) < 9.5, "dist=%.2f" % bomb.global_position.distance_to(Vector3(anchor_x, -3.0, 0.0)))


func _scenario_trampoline() -> void:
	await _build()
	_add(load("res://src/spawnables/trampoline.tscn"), Vector3(8.5, -5.0, 0.0))
	var max_y := -100.0
	var bounced := false
	for i in 240:
		await get_tree().physics_frame
		max_y = maxf(max_y, _player.position.y)
		if _player.velocity.y > 5.0:
			bounced = true
	_check("trampoline", bounced and max_y > -3.0, "max_y=%.2f bounced=%s" % [max_y, bounced])


func _scenario_pickup() -> void:
	await _build()
	_add(load("res://src/spawnables/shield_battery.tscn"), Vector3(11.5, -5.0, 0.0))
	_player.set_max_shields(2)
	await _frames(60)
	Input.action_press("move_right")
	await _frames(30)
	Input.action_press("jump")
	await _frames(10)
	Input.action_release("jump")
	await _frames(120)
	_release_all()
	_check("pickup_shield", _player.active_shields == 1, "shields=%d x=%.2f" % [_player.active_shields, _player.position.x])


func _scenario_push() -> void:
	await _build()
	var toilet := _add(load("res://src/spawnables/toilet.tscn"), Vector3(10.5, -5.0, 0.0))
	await _frames(60)
	var start := toilet.position.x
	Input.action_press("move_right")
	await _frames(120)
	_release_all()
	var upright := toilet.transform.basis.y.dot(Vector3.UP) > 0.9
	_check("push_prop", toilet.position.x - start > 0.5 and upright and toilet.position.y > -5.2 and toilet.position.y < -4.6, "moved=%.2f y=%.2f upright=%s" % [toilet.position.x - start, toilet.position.y, upright])


func _scenario_wall_gun() -> void:
	await _build()
	_add(load("res://src/spawnables/wall_gun.tscn"), Vector3(1.0, -4.0, 0.0))
	_player.set_max_shields(3)
	_player.set_active_shields(3)
	await _frames(300)
	var bullets := 0
	var hits := 3 - _player.active_shields
	for n in _arena.get_children():
		if n is PlasmaBullet:
			bullets += 1
	_check("wall_gun_fires", bullets > 0 or hits > 0, "bullets=%d shield_hits=%d" % [bullets, hits])


func _scenario_treadmill() -> void:
	await _build()
	_add(load("res://src/spawnables/treadmill.tscn"), Vector3(8.5, -5.0, 0.0))
	_player.position = Vector3(8.0, -3.5, 0.0)
	await _frames(180)
	_check("treadmill_moves_player", absf(_player.position.x - 8.0) > 0.8, "x=%.2f" % _player.position.x)


func _scenario_drone() -> void:
	await _build()
	var drone: Drone = _add(load("res://src/spawnables/drone.tscn"), Vector3(4.5, -2.0, 0.0))
	await _frames(180)
	var hover_ok := is_instance_valid(drone) and absf(drone.position.y + 2.0) < 1.0
	var moved := is_instance_valid(drone) and absf(drone.position.x - 4.5) > 1.0
	_check("drone_hovers", hover_ok and moved, "y=%.2f x=%.2f" % [drone.position.y if is_instance_valid(drone) else 0.0, drone.position.x if is_instance_valid(drone) else 0.0])
	if is_instance_valid(drone):
		drone.turn_off()
		await _frames(120)
		_check("drone_falls", not is_instance_valid(drone) or drone.position.y < -3.0, "y=%.2f" % (drone.position.y if is_instance_valid(drone) else -99.0))


func _scenario_button() -> void:
	await _build()
	var button := _add(load("res://src/spawnables/button.tscn"), Vector3(11.0, -5.0, 0.0), {"coin_budget": 10})
	var world_stub := WorldStub.new()
	world_stub.arena = _arena
	button.set_world(world_stub)
	await _frames(30)
	_add(load("res://src/spawnables/toilet.tscn"), Vector3(11.0, -2.5, 0.0))
	await _frames(150)
	_check("button_press", world_stub.spawned > 0, "spawned=%d" % world_stub.spawned)


func _scenario_light_ring() -> void:
	await _build()
	var ring := _add(load("res://src/spawnables/light_ring.tscn"), Vector3(12.0, -5.0, 0.0))
	var bomb := _add(BOMB, Vector3(5.0, -2.5, 0.0), {"no_timeout": true})
	await _frames(60 * 6)
	_check("light_ring_laser", not is_instance_valid(bomb), "bomb_alive=%s beam=%s" % [is_instance_valid(bomb), ring.get_node("Laser/Beam").visible])


class WorldStub extends Node:
	var arena: Node3D
	var spawned := 0
	func spawn_coin(value: int, position: Vector3) -> void:
		spawned += 1
		var c: Coin = load("res://src/actors/coin.tscn").instantiate()
		c.value = value
		c.position = position
		arena.add_child(c)
	func spawn_scene(path: String, position: Vector3, props: Dictionary = {}) -> void:
		spawned += 1
