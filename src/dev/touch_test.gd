extends Node
## Feeds fake touches to the HUD and checks the thumb zones react:
##   godot --headless --path . res://src/dev/touch_test.tscn

var _game: GameScene
var _fails := 0


func _ready() -> void:
	_game = load("res://src/game/game.tscn").instantiate()
	add_child(_game)
	_game.hud.set_touch_controls_visible(true)
	await get_tree().process_frame
	await get_tree().process_frame
	var size := get_viewport().get_visible_rect().size
	print("viewport ", size, " touch visible=", _game.hud.get_node("Touch").visible, " zone pos=", _game.hud.jump_zone.position, " shape=", (_game.hud.jump_zone.shape as RectangleShape2D).size, " stick rect=", _game.hud.joystick.get_global_rect())
	var key := InputEventKey.new()
	key.keycode = KEY_SPACE
	key.physical_keycode = KEY_SPACE
	key.pressed = true
	Input.parse_input_event(key)
	await get_tree().process_frame
	await get_tree().process_frame
	print("key space -> jump pressed=", Input.is_action_pressed("jump"))
	key = InputEventKey.new()
	key.keycode = KEY_SPACE
	key.physical_keycode = KEY_SPACE
	key.pressed = false
	Input.parse_input_event(key)
	await get_tree().process_frame
	# Jump: bottom-right corner, then the middle of the right half.
	await _check_touch(Vector2(size.x * 0.9, size.y * 0.92), "jump", true, "jump bottom-right")
	await _check_touch(Vector2(size.x * 0.6, size.y * 0.5), "jump", true, "jump mid-right")
	await _check_touch(Vector2(size.x * 0.9, 60.0), "jump", false, "no jump on the top bar")
	await _check_touch(Vector2(size.x * 0.3, size.y * 0.5), "jump", false, "no jump on the left")
	# Stick: press anywhere on the left, drag right/left.
	await _check_drag(Vector2(size.x * 0.25, size.y * 0.3), 220.0, "move_right", "stick drag right (upper left)")
	await _check_drag(Vector2(size.x * 0.15, size.y * 0.9), -220.0, "move_left", "stick drag left (lower left)")
	# Smart stick: press intent, following base, quick reversal.
	var p0 := Vector2(size.x * 0.2, size.y * 0.6)
	_touch(p0, true, 2)
	await get_tree().process_frame
	_touch(p0, false, 2)
	await get_tree().process_frame
	_touch(p0 + Vector2(90.0, 0.0), true, 2)
	await get_tree().process_frame
	await get_tree().process_frame
	_report(Input.get_action_strength("move_right") > 0.9, "press right of last spot runs right at once: %.2f" % Input.get_action_strength("move_right"))
	_touch(p0 + Vector2(90.0, 0.0), false, 2)
	await get_tree().process_frame
	_touch(p0 - Vector2(60.0, 0.0), true, 2)
	await get_tree().process_frame
	await get_tree().process_frame
	_report(Input.get_action_strength("move_left") > 0.9, "press left of last spot runs left at once: %.2f" % Input.get_action_strength("move_left"))
	# Reversal while dragging: run right 120 px, slide back 60 px -> left.
	_drag_to(p0 - Vector2(60.0, 0.0) + Vector2(120.0, 0.0), 2)
	await get_tree().process_frame
	var right_str := Input.get_action_strength("move_right")
	_drag_to(p0 - Vector2(60.0, 0.0) + Vector2(60.0, 0.0), 2)
	await get_tree().process_frame
	await get_tree().process_frame
	_report(right_str > 0.9 and Input.get_action_strength("move_left") > 0.5, "slide back 60 px reverses: right=%.2f then left=%.2f" % [right_str, Input.get_action_strength("move_left")])
	_touch(p0, false, 2)
	await get_tree().process_frame
	_report(Input.get_action_strength("move_left") == 0.0 and Input.get_action_strength("move_right") == 0.0, "release stops")
	print("TOUCH_RESULT failures=%d" % _fails)
	get_tree().quit()


## Synthetic events are in window pixels; the viewport is stretched over them.
func _to_window(pos: Vector2) -> Vector2:
	return get_viewport().get_final_transform() * pos


func _touch(pos: Vector2, pressed: bool, index := 0) -> void:
	var ev := InputEventScreenTouch.new()
	ev.position = _to_window(pos)
	ev.pressed = pressed
	ev.index = index
	Input.parse_input_event(ev)


func _drag_to(pos: Vector2, index: int) -> void:
	var ev := InputEventScreenDrag.new()
	ev.index = index
	ev.position = _to_window(pos)
	Input.parse_input_event(ev)


func _check_touch(pos: Vector2, action: String, expect: bool, label: String) -> void:
	_touch(pos, true)
	await get_tree().process_frame
	await get_tree().process_frame
	var got := Input.is_action_pressed(action)
	_touch(pos, false)
	await get_tree().process_frame
	_report(got == expect, "%s: %s pressed=%s" % [label, action, got])


func _check_drag(pos: Vector2, dx: float, action: String, label: String) -> void:
	_touch(pos, true, 1)
	await get_tree().process_frame
	var ev := InputEventScreenDrag.new()
	ev.index = 1
	ev.position = _to_window(pos + Vector2(dx, 0.0))
	ev.relative = _to_window(Vector2(dx, 0.0))
	Input.parse_input_event(ev)
	await get_tree().process_frame
	await get_tree().process_frame
	var strength := Input.get_action_strength(action)
	var other := Input.get_action_strength("move_left" if action == "move_right" else "move_right")
	_touch(pos + Vector2(dx, 0.0), false, 1)
	await get_tree().process_frame
	await get_tree().process_frame
	var released := Input.get_action_strength(action) == 0.0
	_report(strength > 0.9 and other == 0.0 and released, "%s: strength=%.2f other=%.2f released=%s" % [label, strength, other, released])


func _report(ok: bool, text: String) -> void:
	if not ok:
		_fails += 1
	print("%s %s" % ["PASS" if ok else "FAIL", text])
