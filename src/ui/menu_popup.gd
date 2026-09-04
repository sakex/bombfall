class_name MenuPopup
extends Control
## Base for the menu overlays: a dimmed backdrop, a titled panel, and
## closing by tapping outside. Subclasses fill [method _build].

var panel: PanelContainer
var content: VBoxContainer
var _title := ""


func _init(title: String = "") -> void:
	_title = title


func _ready() -> void:
	theme = load("res://src/ui/theme.tres")
	set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	var dim := ColorRect.new()
	dim.color = Color(0.05, 0.0, 0.08, 0.7)
	dim.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	dim.gui_input.connect(_on_outside_input)
	add_child(dim)
	var center := CenterContainer.new()
	center.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	center.mouse_filter = Control.MOUSE_FILTER_IGNORE
	add_child(center)
	panel = PanelContainer.new()
	panel.custom_minimum_size = Vector2(900, 0)
	center.add_child(panel)
	content = VBoxContainer.new()
	content.add_theme_constant_override("separation", 22)
	panel.add_child(content)
	if _title != "":
		var title_panel := PanelContainer.new()
		title_panel.add_theme_stylebox_override("panel", load("res://src/ui/theme.tres").get_stylebox("panel", "PanelContainer").duplicate())
		(title_panel.get_theme_stylebox("panel") as StyleBoxFlat).bg_color = Color(0.424, 0.078, 0.392)
		var title := Label.new()
		title.text = _title
		title.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
		title.add_theme_font_size_override("font_size", 64)
		title_panel.add_child(title)
		content.add_child(title_panel)
	_build()
	visible = false


func _build() -> void:
	pass


func open() -> void:
	_refresh()
	visible = true


func close() -> void:
	visible = false


func _refresh() -> void:
	pass


func _on_outside_input(event: InputEvent) -> void:
	if event is InputEventMouseButton and event.pressed:
		close()


# ---- small widget helpers -------------------------------------------------
static func label(text: String, size: int = 40, color: Color = Color(0.95, 0.92, 1.0)) -> Label:
	var l := Label.new()
	l.text = text
	l.horizontal_alignment = HORIZONTAL_ALIGNMENT_CENTER
	l.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
	l.add_theme_font_size_override("font_size", size)
	l.add_theme_color_override("font_color", color)
	return l


static func button(text: String, min_height: float = 90.0) -> Button:
	var b := Button.new()
	b.text = text
	b.custom_minimum_size = Vector2(0, min_height)
	return b
