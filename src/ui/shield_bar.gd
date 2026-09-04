class_name ShieldBar
extends HBoxContainer
## Row of shield cells: lit ones are active shields, dim ones are empty slots.

const CELL_SIZE := Vector2(64, 40)
const ACTIVE := Color(0.25, 0.9, 1.0)
const INACTIVE := Color(0.25, 0.9, 1.0, 0.15)

var _max := 0
var _active := 0


func _ready() -> void:
	alignment = BoxContainer.ALIGNMENT_CENTER
	add_theme_constant_override("separation", 6)
	_rebuild()


func set_state(max_shields: int, active_shields: int) -> void:
	_max = max_shields
	_active = active_shields
	_rebuild()


func set_active_shields(active_shields: int) -> void:
	_active = active_shields
	_refresh()


func set_max_shields(max_shields: int) -> void:
	_max = max_shields
	_rebuild()


func _rebuild() -> void:
	for child in get_children():
		child.queue_free()
	for i in _max:
		var cell := Panel.new()
		cell.custom_minimum_size = CELL_SIZE
		var style := StyleBoxFlat.new()
		style.bg_color = INACTIVE
		style.border_color = ACTIVE
		style.set_border_width_all(3)
		style.set_corner_radius_all(6)
		style.skew = Vector2(0.25, 0.0)
		cell.add_theme_stylebox_override("panel", style)
		add_child(cell)
	_refresh.call_deferred()


func _refresh() -> void:
	var i := 0
	for cell in get_children():
		var style := cell.get_theme_stylebox("panel") as StyleBoxFlat
		if style != null:
			style.bg_color = ACTIVE if i < _active else INACTIVE
		i += 1
