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
	await _scenario_head_bump()
	await _scenario_bomb_rest()
	await _scenario_coin()
	await _scenario_rope()
	await _scenario_trampoline()
	await _scenario_trampoline_blast()
	await _scenario_pickup()
	await _scenario_push()
	await _scenario_wall_gun()
	await _scenario_treadmill()
	await _scenario_drone()
	await _scenario_button()
	await _scenario_light_ring()
	await _scenario_table_set()
	await _scenario_chair_drop()
	await _scenario_champagne()
	await _scenario_bumper()
	await _scenario_air_fan()
	await _scenario_desktop()
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


## Bombs of different sizes must each rest exactly on the floor: the shape
## used to be shared between instances, so small ones floated and big ones sank.
func _scenario_bomb_rest() -> void:
	await _build()
	_player.position = Vector3(2.0, -4.0, 0.0)
	var small := _add(load("res://src/actors/bomb.tscn"), Vector3(6.0, -2.5, 0.0), {"bomb_time": 60.0, "bomb_scale": 0.5})
	var big := _add(load("res://src/actors/bomb.tscn"), Vector3(11.0, -2.5, 0.0), {"bomb_time": 60.0, "bomb_scale": 1.0})
	await _frames(150)
	var floor_top := -5.0
	var small_gap: float = small.position.y - Bomb.BASE_RADIUS * 0.5 - floor_top
	var big_gap: float = big.position.y - Bomb.BASE_RADIUS * 1.0 - floor_top
	_check("bomb_rest_on_floor", absf(small_gap) < 0.04 and absf(big_gap) < 0.04, "small_gap=%.3f big_gap=%.3f" % [small_gap, big_gap])


## Explosions must take trampolines with them (an Area3D, not a body).
func _scenario_trampoline_blast() -> void:
	await _build()
	_player.position = Vector3(2.0, -4.0, 0.0)
	# The bomb lands beside the trampoline (on it, the mat would fling it away).
	var tramp := _add(load("res://src/spawnables/trampoline.tscn"), Vector3(8.5, -5.0, 0.0))
	var chair := _add(load("res://src/spawnables/chair.tscn"), Vector3(13.0, -5.0, 0.0))
	_add(load("res://src/actors/bomb.tscn"), Vector3(11.0, -3.0, 0.0), {"bomb_time": 0.6, "bomb_scale": 0.8})
	await _frames(120)
	_check("trampoline_blasted", not is_instance_valid(tramp) and not is_instance_valid(chair), "trampoline alive=%s chair alive=%s" % [is_instance_valid(tramp), is_instance_valid(chair)])


## A bomb sitting on the runner's head gets knocked up and away by a jump.
func _scenario_head_bump() -> void:
	await _build()
	_player.position = Vector3(8.5, -4.0, 0.0)
	# Held just above the helmet, let go as the jump starts.
	var bomb := _add(load("res://src/actors/bomb.tscn"), Vector3(8.5, -1.4, 0.0), {"bomb_time": 60.0, "freeze": true})
	await _frames(60)
	var rest_y := bomb.position.y
	(bomb as RigidBody3D).freeze = false
	Input.action_press("jump")
	await _frames(8)
	Input.action_release("jump")
	await _frames(10)
	var rise := bomb.position.y - rest_y
	var vy: float = (bomb as RigidBody3D).linear_velocity.y
	_release_all()
	_check("head_bump_bomb", rise > 0.4 or vy > 3.0, "player=(%.2f,%.2f) rest_y=%.2f rise=%.2f vy=%.2f" % [_player.position.x, _player.position.y, rest_y, rise, vy])


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


func _upright(body: Node3D) -> bool:
	return body.global_transform.basis.y.dot(Vector3.UP) > 0.95


func _scenario_table_set() -> void:
	await _build()
	var set := _add(load("res://src/spawnables/table_with_chairs.tscn"), Vector3(11.5, -5.0, 0.0))
	await _frames(90)
	var table: RigidBody3D = set.get_node("Table")
	var chair_l: RigidBody3D = set.get_node("ChairL")
	var chair_r: RigidBody3D = set.get_node("ChairR")
	var bodies: Array[RigidBody3D] = [table, chair_l, chair_r]
	var settled := true
	for b in bodies:
		settled = settled and absf(b.global_position.y + 5.0) < 0.1 and _upright(b)
	# The chairs face the table: their models look along +X (left) and -X (right).
	var facing: bool = chair_l.get_node("Model").global_transform.basis.z.normalized().x > 0.9 and chair_r.get_node("Model").global_transform.basis.z.normalized().x < -0.9
	_check("table_set_rests", settled and facing and chair_l.global_position.x < table.global_position.x and chair_r.global_position.x > table.global_position.x,
		"table_y=%.2f chairs_y=%.2f/%.2f facing=%s" % [table.global_position.y, chair_l.global_position.y, chair_r.global_position.y, facing])
	var chair_start := chair_l.global_position.x
	var table_start := table.global_position.x
	# Shove the table to the right: the chair behind it must stay put.
	table.apply_central_impulse(Vector3(1.0, 0.0, 0.0) * table.mass * 10.0)
	await _frames(120)
	var moved := table.global_position.x - table_start
	var chair_drift := chair_l.global_position.x - chair_start
	_check("table_split", moved > 0.5 and absf(chair_drift) < 0.05 and _upright(table) and _upright(chair_l),
		"table_moved=%.2f left_chair_drift=%.3f" % [moved, chair_drift])
	# Walking into the left chair slides it on its own across the gap the
	# table left behind, so it ends up further along than the table did.
	var table_x := table.global_position.x
	Input.action_press("move_right")
	await _frames(90)
	_release_all()
	var chair_moved := chair_l.global_position.x - chair_start
	var table_moved := table.global_position.x - table_x
	_check("chair_pushed_alone", chair_moved > 0.3 and chair_moved > table_moved + 0.2 and _upright(chair_l),
		"chair_moved=%.2f table_moved=%.3f" % [chair_moved, table_moved])


func _scenario_chair_drop() -> void:
	await _build()
	var chair := _add(load("res://src/spawnables/chair.tscn"), Vector3(4.5, -2.0, 0.0))
	await _frames(180)
	_check("chair_lands_upright", _upright(chair) and absf(chair.position.y + 5.0) < 0.1 and absf(chair.position.x - 4.5) < 0.2,
		"y=%.3f x=%.2f up=%.3f" % [chair.position.y, chair.position.x, chair.global_transform.basis.y.dot(Vector3.UP)])


func _scenario_champagne() -> void:
	await _build()
	var bottle := _add(load("res://src/spawnables/champagne.tscn"), Vector3(5.5, -3.0, 0.0))
	await _frames(180)
	_check("champagne_on_floor", is_instance_valid(bottle) and absf(bottle.position.y + 5.0) < 0.08 and _upright(bottle),
		"y=%.3f up=%.3f" % [bottle.position.y, bottle.global_transform.basis.y.dot(Vector3.UP)])


func _scenario_bumper() -> void:
	await _build()
	_add(load("res://src/spawnables/bumper.tscn"), Vector3(11.5, -5.0, 0.0))
	await _frames(60)
	Input.action_press("move_right")
	var kicked := false
	var max_x := 0.0
	var max_y := -100.0
	for i in 120:
		await get_tree().physics_frame
		max_x = maxf(max_x, _player.position.x)
		max_y = maxf(max_y, _player.position.y)
		if _player.velocity.y > 3.0 and _player.velocity.x < -3.0:
			kicked = true
	_release_all()
	_check("bumper_kicks_player", kicked and max_x < 11.0 and max_y > -4.6, "kicked=%s max_x=%.2f max_y=%.2f" % [kicked, max_x, max_y])


func _scenario_air_fan() -> void:
	await _build()
	_add(load("res://src/spawnables/air_fan.tscn"), Vector3(12.0, -5.0, 0.0))
	_player.position = Vector3(12.0, -3.0, 0.0)
	var max_y := -100.0
	var min_y := 100.0
	for i in 180:
		await get_tree().physics_frame
		max_y = maxf(max_y, _player.position.y)
		min_y = minf(min_y, _player.position.y)
	_check("air_fan_lifts_player", max_y > -1.5 and min_y > -4.4, "max_y=%.2f min_y=%.2f" % [max_y, min_y])


func _scenario_desktop() -> void:
	await _build()
	var desktop := _add(load("res://src/spawnables/desktop.tscn"), Vector3(11.0, -5.0, 0.0))
	await _frames(120)
	var desk: RigidBody3D = desktop.get_node("Desk")
	var monitor: RigidBody3D = desktop.get_node("Monitor")
	var tower: RigidBody3D = desktop.get_node("Tower")
	var meshes_ok := monitor.find_child("monitor", true, false) != null and tower.find_child("tower", true, false) != null
	_check("desktop_stacks", meshes_ok and absf(desk.global_position.y + 5.0) < 0.1 and absf(monitor.global_position.y + 3.0) < 0.15 and absf(tower.global_position.y + 5.0) < 0.1 and _upright(monitor),
		"desk_y=%.2f monitor_y=%.2f tower_y=%.2f meshes=%s" % [desk.global_position.y, monitor.global_position.y, tower.global_position.y, meshes_ok])


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
