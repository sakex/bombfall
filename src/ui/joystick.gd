class_name Joystick
extends Control
## The thumb pad for left/right, built like the floating, re-centering,
## draggable d-pads of the better mobile platformers:
##
##  * Press intent. The pad remembers where the thumb last was. Press to the
##    right of that spot and you run right immediately, no slide needed; the
##    base lands behind the thumb already fully deflected.
##  * Following base. While dragging, the base trails the thumb and is never
##    more than FOLLOW pixels away, so reversing direction is a slide of a few
##    millimetres, never all the way back to where the touch began.
##  * Snappy ramp. A tiny dead zone, then near-full speed within a fingertip.
##
## Feeds move_left / move_right as analog strengths; drawn in code.

const FOLLOW := 44.0             ## max distance between thumb and base (px)
const DEAD_ZONE := 5.0           ## px before the pad reacts to a drag
const RAMP := 26.0               ## px of deflection for full speed
const SNAP := 22.0               ## press this far from the last spot = instant run
const MEMORY := 20.0             ## seconds the last spot is remembered
const KNOB := 52.0
const REST_ALPHA := 0.75

var axis := 0.0

var _touch_index := -1
var _anchor := Vector2.ZERO      ## base (x matters; y is the thumb's row)
var _knob := Vector2.ZERO
var _rest := Vector2.ZERO
var _last_spot := Vector2.ZERO   ## where the thumb was last seen
var _last_spot_time := -1000.0
var _glow := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(_place_rest)
	_place_rest()


func _place_rest() -> void:
	_rest = Vector2(FOLLOW + 110.0, size.y - 170.0)
	if _touch_index < 0:
		_anchor = _rest
		_knob = _rest
	queue_redraw()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var touch := event as InputEventScreenTouch
		if touch.pressed and _touch_index < 0:
			_press(touch.position, touch.index)
			accept_event()
		elif not touch.pressed and touch.index == _touch_index:
			_release(touch.position)
			accept_event()
	elif event is InputEventScreenDrag:
		var drag := event as InputEventScreenDrag
		if drag.index == _touch_index:
			_drag(drag.position)
			accept_event()
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		# Mouse emulation for desktop testing.
		var mb := event as InputEventMouseButton
		if mb.pressed and _touch_index < 0:
			_press(mb.position, 0)
		elif not mb.pressed and _touch_index == 0:
			_release(mb.position)
	elif event is InputEventMouseMotion and _touch_index == 0:
		_drag((event as InputEventMouseMotion).position)


func _press(pos: Vector2, index: int) -> void:
	_touch_index = index
	_knob = pos
	var now := Time.get_ticks_msec() / 1000.0
	var remembered := now - _last_spot_time < MEMORY
	var side := pos.x - _last_spot.x
	if remembered and absf(side) > SNAP:
		# Pressed clearly to one side of where the thumb was: go that way now.
		_anchor = Vector2(pos.x - signf(side) * FOLLOW, pos.y)
	else:
		_anchor = pos
	_last_spot = pos
	_last_spot_time = now
	_update_axis()


func _drag(pos: Vector2) -> void:
	_knob = pos
	# The base trails the thumb so it is never further than FOLLOW away.
	_anchor.x = clampf(_anchor.x, pos.x - FOLLOW, pos.x + FOLLOW)
	_anchor.y = pos.y
	_last_spot = pos
	_last_spot_time = Time.get_ticks_msec() / 1000.0
	_update_axis()


func _release(pos: Vector2) -> void:
	_touch_index = -1
	_last_spot = pos
	_last_spot_time = Time.get_ticks_msec() / 1000.0
	_set_axis(0.0)
	# Rest where the thumb left off: that spot is the reference for the next press.
	_anchor = pos
	_knob = pos


func _update_axis() -> void:
	var dx := _knob.x - _anchor.x
	if absf(dx) < DEAD_ZONE:
		_set_axis(0.0)
		return
	var strength := clampf((absf(dx) - DEAD_ZONE) / RAMP, 0.0, 1.0)
	# Any deflection past the dead zone already means "go": start brisk.
	strength = maxf(strength, 0.6)
	_set_axis(signf(dx) * strength)


func _set_axis(value: float) -> void:
	axis = value
	if value > 0.0:
		Input.action_release("move_left")
		Input.action_press("move_right", value)
	elif value < 0.0:
		Input.action_release("move_right")
		Input.action_press("move_left", -value)
	else:
		Input.action_release("move_left")
		Input.action_release("move_right")
	queue_redraw()


func _process(delta: float) -> void:
	var target := 1.0 if _touch_index >= 0 else 0.0
	if not is_equal_approx(_glow, target):
		_glow = move_toward(_glow, target, delta * 6.0)
		queue_redraw()


func _exit_tree() -> void:
	if _touch_index >= 0:
		_release(_knob)


func _draw() -> void:
	var alpha := lerpf(REST_ALPHA, 1.0, _glow)
	var cyan := Color(0.36, 0.95, 1.0, alpha)
	var pink := Color(1.0, 0.3, 0.78, alpha)
	var ink := Color(0.07, 0.02, 0.13, 0.85 * alpha)
	var half := FOLLOW + KNOB * 0.6
	var track := Rect2(_anchor - Vector2(half, KNOB * 0.9), Vector2(half * 2.0, KNOB * 1.8))
	_capsule(track.grow(KNOB * 0.2), Color(pink, 0.25 * alpha), Color(0, 0, 0, 0))
	_capsule(track, ink, cyan)
	draw_line(_anchor + Vector2(-half, 0), _anchor + Vector2(half, 0), Color(cyan, 0.7 * alpha), 2.0)
	for side: float in [-1.0, 1.0]:
		var tip := _anchor + Vector2(side * (half - 8.0), 0)
		var lit: bool = axis != 0.0 and signf(axis) == side
		draw_polyline(PackedVector2Array([tip + Vector2(-side * 16.0, -16.0), tip, tip + Vector2(-side * 16.0, 16.0)]), Color(1.0, 1.0, 1.0, alpha) if lit else pink, 5.0)
	# Knob: a glowing puck clamped to the track.
	var knob := Vector2(clampf(_knob.x, _anchor.x - FOLLOW, _anchor.x + FOLLOW), _anchor.y)
	draw_circle(knob, KNOB * 1.35, Color(pink, 0.22 * alpha))
	draw_circle(knob, KNOB, ink)
	draw_arc(knob, KNOB - 2.0, 0.0, TAU, 40, cyan, 5.0)
	draw_circle(knob, KNOB * 0.42, Color(1.0, 0.45, 0.85, alpha))
	draw_arc(knob, KNOB * 0.62, 0.0, TAU, 32, Color(pink, 0.9 * alpha), 2.0)


func _capsule(rect: Rect2, fill: Color, border: Color) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.set_corner_radius_all(int(rect.size.y * 0.5))
	if border.a > 0.0:
		sb.set_border_width_all(3)
		sb.border_color = border
	sb.anti_aliasing = true
	sb.draw(get_canvas_item(), rect)
