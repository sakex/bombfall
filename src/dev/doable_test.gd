extends Node
## Plays every special storey with a scripted bot and checks it can be
## passed: the bot must end up below the storey within the time limit.
##   godot --headless --path . res://src/dev/doable_test.tscn [-- --only=vault]

const SPECIALS := {
	"wall_block": {"rows": 16, "limit": 150.0},
	"obstacle_course": {"rows": 37, "limit": 180.0},
	"vault": {"rows": 19, "limit": 200.0},
	"boss_bat_arena": {"rows": 20, "limit": 300.0},
}

var _game: GameScene
var _name := ""
var _roof := 0
var _bottom_y := 0.0
var _t := 0.0
var _limit := 0.0
var _results: Array[String] = []
var _queue: Array[String] = []
var _heart_x := 13.25
var _running := false
var _limit_override := 0.0
var _jump_ticks := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	var only := ""
	Engine.time_scale = 3.0
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--only="):
			only = arg.trim_prefix("--only=")
		if arg.begins_with("--limit="):
			_limit_override = float(arg.trim_prefix("--limit="))
		if arg.begins_with("--speed="):
			Engine.time_scale = float(arg.trim_prefix("--speed="))
	for key in SPECIALS:
		if only == "" or only == key:
			_queue.append(key)
	_next()


func _next() -> void:
	_running = false
	if _game != null:
		_game.queue_free()
		_game = null
		await get_tree().process_frame
	if _queue.is_empty():
		print("DOABLE_RESULT " + " ".join(_results))
		get_tree().quit()
		return
	_name = _queue.pop_front()
	_game = load("res://src/game/game.tscn").instantiate()
	_game.record_scores = false
	_game.allow_revive = true
	add_child(_game)
	await get_tree().process_frame
	var world := _game.world
	world.forced_special = _name
	_roof = world.next_roof
	world.render_special_level()
	_bottom_y = -float(_roof + SPECIALS[_name]["rows"]) - 1.0
	_limit = SPECIALS[_name]["limit"] if _limit_override <= 0.0 else _limit_override
	_t = 0.0
	_game.player.position = Vector3(Grid.CENTER_X, -(_roof + 1.5), 0.0)
	_game.player.add_immunity(100000.0)
	_game.rig.snap()
	if _name == "obstacle_course":
		_check_ledges()
	print("DOABLE start %s roof=%d bottom_y=%.1f" % [_name, _roof, _bottom_y])
	_running = true


## Every ledge of the obstacle course must be reachable from a lower one.
func _check_ledges() -> void:
	var jump_h := Player.SPEED.y * Player.SPEED.y / (2.0 * Player.GRAVITY)
	var ledges: Array = ObstacleCourse.LEDGES.duplicate()
	ledges.sort_custom(func(a, b): return a[1] > b[1])   # bottom first (bigger row)
	var floor_row := 37.0
	var reachable := [[Grid.CENTER_X, floor_row, 16.0]]
	for ledge in ledges:
		var ok := false
		for r in reachable:
			var dy: float = r[1] - ledge[1]
			var dx: float = maxf(0.0, absf(ledge[0] + ledge[2] * 0.5 - (r[0] + r[2] * 0.5)) - (ledge[2] + r[2]) * 0.5)
			if dy <= jump_h - 0.4 and dx <= 6.0:
				ok = true
				break
		print("  ledge x=%.1f row=%.1f w=%.1f reachable=%s" % [ledge[0], ledge[1], ledge[2], ok])
		if not ok:
			_results.append("obstacle_course:LEDGE_UNREACHABLE")
		reachable.append(ledge)


func _physics_process(delta: float) -> void:
	if not _running or _game == null or not is_instance_valid(_game.player):
		return
	var player := _game.player
	_t += delta
	if _game.death_screen.visible:
		get_tree().paused = false
		_game.death_screen.visible = false
		player.revive()
	if player.position.y < _bottom_y:
		print("DOABLE %s PASS in %.1fs" % [_name, _t])
		_results.append("%s:PASS" % _name)
		_release_all()
		_next()
		return
	if _t > _limit:
		print("DOABLE %s FAIL y=%.1f (bottom %.1f) after %.0fs" % [_name, player.position.y, _bottom_y, _t])
		_results.append("%s:FAIL" % _name)
		_release_all()
		_next()
		return
	match _name:
		"boss_bat_arena":
			_bot_climb(player, _heart_x)
		_:
			_bot_wander(player)
	if int(_t * 2.0) % 40 == 0 and int(_t * 60.0) % 120 == 0:
		print("  t=%.0f y=%.1f x=%.1f" % [_t, player.position.y, player.position.x])


## Paces the room and hops now and then, waiting for bombs to open the way.
func _bot_wander(player: Player) -> void:
	var right := fmod(_t, 8.0) < 4.0
	Input.action_press("move_right" if right else "move_left")
	Input.action_release("move_left" if right else "move_right")
	_hop(int(_t * 60.0) % 150 < 6)


## Climbs the crystal ladder: stand beside the next step, jump towards it.
func _bot_climb(player: Player, target_x: float) -> void:
	var arena := _game.world.find_child("BossBatArena", true, false)
	if int(_t * 60.0) % 600 == 0:
		var blocks := get_tree().get_nodes_in_group("boss_blocks").size()
		print("  arena=%s ladder=%d boss_blocks=%d awake=%s" % [arena != null, arena.ladder.size() if arena != null else -1, blocks, arena._boss_awake if arena != null else "?"])
	if arena != null and arena.boss.is_dying():
		# Fight won: get off the ladder and wait for the floor to open.
		_steer(player, Grid.CENTER_X)
		_hop(false)
		return
	var next: Node3D = null
	if arena != null:
		for step in arena.ladder:
			if not is_instance_valid(step):
				continue
			var y: float = step.global_position.y
			if y > player.position.y + 0.3 and (next == null or y < next.global_position.y):
				next = step
	if next == null:
		_steer(player, target_x)
		_hop(false)
		return
	var step_x: float = next.global_position.x
	var approach_x := step_x + 1.7 * signf(Grid.CENTER_X - step_x)
	# A jump in progress is held for a fixed time so the release never cuts it.
	if _jump_ticks > 0:
		_jump_ticks -= 1
		_steer(player, step_x)
		_hop(true)
		return
	if int(_t * 60.0) % 120 == 0:
		print("  DBG t=%.0f p=(%.1f,%.1f) floor=%s vy=%.1f step=(%.1f,%.1f) approach=%.1f jump=%s" % [_t, player.position.x, player.position.y, player.is_on_floor(), player.velocity.y, step_x, next.global_position.y, approach_x, Input.is_action_pressed("jump")])
	if player.is_on_floor() and player.velocity.y <= 0.01:
		if absf(player.position.x - approach_x) > 0.5:
			_steer(player, approach_x)
			_hop(false)
		else:
			_steer(player, step_x)
			_jump_ticks = 24
			_hop(true)
	else:
		_steer(player, step_x)
		_hop(false)


func _steer(player: Player, x: float) -> void:
	var dx := x - player.position.x
	if absf(dx) > 0.3:
		Input.action_press("move_right" if dx > 0.0 else "move_left")
		Input.action_release("move_left" if dx > 0.0 else "move_right")
	else:
		Input.action_release("move_left")
		Input.action_release("move_right")


var _hop_state := false
func _hop(pressed: bool) -> void:
	if pressed != _hop_state and _name == "boss_bat_arena":
		_hop_state = pressed
		print("  HOP %s t=%.2f y=%.2f floor=%s vy=%.1f death=%.2f immune=%s atfloor=%s" % [pressed, _t, _game.player.position.y, _game.player.is_on_floor(), _game.player.velocity.y, _game.player._death_progress, _game.player.is_immune, _game.player._at_floor])
	if pressed:
		Input.action_press("jump")
	else:
		Input.action_release("jump")


func _release_all() -> void:
	for a in ["move_left", "move_right", "jump"]:
		Input.action_release(a)
