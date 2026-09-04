class_name SettingsPopup
extends MenuPopup
## Volume sliders and the player name.

var _music: HSlider
var _sfx: HSlider
var _name: LineEdit
var _status: Label


func _init() -> void:
	super._init("settings")


func _build() -> void:
	content.add_child(label("volume", 46, Color(0.7, 0.95, 1.0)))
	_music = _slider_row("music")
	_sfx = _slider_row("sfx")
	content.add_child(label("account", 46, Color(0.7, 0.95, 1.0)))
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 20)
	var name_label := label("name", 36)
	name_label.custom_minimum_size = Vector2(200, 0)
	row.add_child(name_label)
	_name = LineEdit.new()
	_name.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	_name.max_length = 16
	_name.placeholder_text = "your name"
	row.add_child(_name)
	content.add_child(row)
	_status = label("", 28, Color(0.6, 0.95, 0.7))
	content.add_child(_status)
	var apply := button("change name", 80)
	apply.pressed.connect(_change_name)
	content.add_child(apply)
	var close_button := button("close", 80)
	close_button.pressed.connect(close)
	content.add_child(close_button)
	Services.backend.username_changed.connect(_on_name_result)


func _slider_row(bus: String) -> HSlider:
	var row := HBoxContainer.new()
	row.add_theme_constant_override("separation", 20)
	var l := label(bus, 36)
	l.custom_minimum_size = Vector2(200, 0)
	row.add_child(l)
	var slider := HSlider.new()
	slider.max_value = 1.0
	slider.step = 0.01
	slider.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	slider.size_flags_vertical = Control.SIZE_SHRINK_CENTER
	slider.custom_minimum_size = Vector2(0, 60)
	slider.value_changed.connect(func(v): SaveData.set_bus_volume(bus, v))
	row.add_child(slider)
	content.add_child(row)
	return slider


func _refresh() -> void:
	_music.set_value_no_signal(SaveData.get_bus_volume("music"))
	_sfx.set_value_no_signal(SaveData.get_bus_volume("sfx"))
	_name.text = str(SaveData.data["username"])
	_status.text = ""


func close() -> void:
	SaveData.set_volumes(_music.value, _sfx.value)
	super.close()


func _change_name() -> void:
	var new_name := _name.text.strip_edges()
	if new_name.is_empty():
		_status.text = "enter a name first"
		return
	Services.backend.change_username(new_name)


func _on_name_result(result: Dictionary) -> void:
	if result.has("error"):
		_status.text = str(result["error"])
		return
	SaveData.set_username(str(result["username"]))
	_status.text = "name changed to %s" % result["username"]
