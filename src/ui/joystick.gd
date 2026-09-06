class_name Joystick
extends Control
## A one-axis floating thumb stick for moving left and right. Touch anywhere
## on the control and drag sideways: the stick appears where the thumb landed
## and feeds an analog strength into the move_left / move_right actions, so
## a small drag walks and a full one runs. Drawn in code, no textures.

const RADIUS := 135.0            ## drag distance for full speed, in pixels
const KNOB := 56.0
const DEAD_ZONE := 0.08
const REST_ALPHA := 0.8

var axis := 0.0

var _touch_index := -1
var _anchor := Vector2.ZERO
var _knob := Vector2.ZERO
var _rest := Vector2.ZERO
var _glow := 0.0


func _ready() -> void:
	mouse_filter = Control.MOUSE_FILTER_STOP
	resized.connect(_place_rest)
	_place_rest()


func _place_rest() -> void:
	_rest = Vector2(RADIUS + 90.0, size.y - 170.0)
	if _touch_index < 0:
		_anchor = _rest
		_knob = _rest
	queue_redraw()


func _gui_input(event: InputEvent) -> void:
	if event is InputEventScreenTouch:
		var touch := event as InputEventScreenTouch
		if touch.pressed and _touch_index < 0:
			_touch_index = touch.index
			_anchor = touch.position
			_knob = touch.position
			_set_axis(0.0)
			accept_event()
		elif not touch.pressed and touch.index == _touch_index:
			_release()
			accept_event()
	elif event is InputEventScreenDrag:
		var drag := event as InputEventScreenDrag
		if drag.index == _touch_index:
			var dx := clampf((drag.position.x - _anchor.x) / RADIUS, -1.0, 1.0)
			_knob = Vector2(_anchor.x + dx * RADIUS, _anchor.y)
			_set_axis(dx)
			accept_event()
	elif event is InputEventMouseButton and (event as InputEventMouseButton).button_index == MOUSE_BUTTON_LEFT:
		# Mouse emulation for desktop testing.
		var mb := event as InputEventMouseButton
		if mb.pressed and _touch_index < 0:
			_touch_index = 0
			_anchor = mb.position
			_knob = mb.position
			_set_axis(0.0)
		elif not mb.pressed and _touch_index == 0:
			_release()
	elif event is InputEventMouseMotion and _touch_index == 0:
		var dx := clampf(((event as InputEventMouseMotion).position.x - _anchor.x) / RADIUS, -1.0, 1.0)
		_knob = Vector2(_anchor.x + dx * RADIUS, _anchor.y)
		_set_axis(dx)


func _release() -> void:
	_touch_index = -1
	_set_axis(0.0)
	_anchor = _rest
	_knob = _rest


func _set_axis(value: float) -> void:
	if absf(value) < DEAD_ZONE:
		value = 0.0
	else:
		value = signf(value) * (absf(value) - DEAD_ZONE) / (1.0 - DEAD_ZONE)
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
		_release()


func _draw() -> void:
	var alpha := lerpf(REST_ALPHA, 1.0, _glow)
	var cyan := Color(0.36, 0.95, 1.0, alpha)
	var pink := Color(1.0, 0.3, 0.78, alpha)
	var ink := Color(0.07, 0.02, 0.13, 0.85 * alpha)
	# Track: a slanted capsule with tick marks and chevrons at both ends.
	var half := RADIUS + KNOB * 0.5
	var track := Rect2(_anchor - Vector2(half, KNOB * 0.9), Vector2(half * 2.0, KNOB * 1.8))
	_capsule(track.grow(KNOB * 0.2), Color(pink, 0.25 * alpha), Color(0, 0, 0, 0))
	_capsule(track, ink, cyan)
	draw_line(_anchor + Vector2(-half, 0), _anchor + Vector2(half, 0), Color(cyan, 0.7 * alpha), 2.0)
	for i in range(-2, 3):
		var x := _anchor.x + i * RADIUS * 0.5
		draw_line(Vector2(x, _anchor.y - 14), Vector2(x, _anchor.y + 14), Color(cyan, 0.5 * alpha), 2.0)
	for s in [-1.0, 1.0]:
		var tip := _anchor + Vector2(s * (half - 10.0), 0)
		draw_polyline(PackedVector2Array([tip + Vector2(-s * 18.0, -18.0), tip, tip + Vector2(-s * 18.0, 18.0)]), pink, 5.0)
	# Knob: a glowing puck.
	draw_circle(_knob, KNOB * 1.35, Color(pink, 0.22 * alpha))
	draw_circle(_knob, KNOB, ink)
	draw_arc(_knob, KNOB - 2.0, 0.0, TAU, 40, cyan, 5.0)
	draw_circle(_knob, KNOB * 0.42, Color(1.0, 0.45, 0.85, alpha))
	draw_arc(_knob, KNOB * 0.62, 0.0, TAU, 32, Color(pink, 0.9 * alpha), 2.0)


func _capsule(rect: Rect2, fill: Color, border: Color) -> void:
	var sb := StyleBoxFlat.new()
	sb.bg_color = fill
	sb.set_corner_radius_all(int(rect.size.y * 0.5))
	if border.a > 0.0:
		sb.set_border_width_all(3)
		sb.border_color = border
	sb.anti_aliasing = true
	sb.draw(get_canvas_item(), rect)
