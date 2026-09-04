class_name PauseScreen
extends Control
## Pause overlay with volume sliders.

signal resumed
signal retry
signal main_menu

@onready var music_slider: HSlider = %MusicSlider
@onready var sfx_slider: HSlider = %SfxSlider


func _ready() -> void:
	visible = false
	%ContinueButton.pressed.connect(_continue)
	%RetryButton.pressed.connect(func(): _save_volumes(); retry.emit())
	%MenuButton.pressed.connect(func(): _save_volumes(); main_menu.emit())
	music_slider.value_changed.connect(func(v): SaveData.set_bus_volume("music", v))
	sfx_slider.value_changed.connect(func(v): SaveData.set_bus_volume("sfx", v))


func open() -> void:
	music_slider.set_value_no_signal(SaveData.get_bus_volume("music"))
	sfx_slider.set_value_no_signal(SaveData.get_bus_volume("sfx"))
	visible = true
	get_tree().paused = true


func _continue() -> void:
	_save_volumes()
	visible = false
	get_tree().paused = false
	resumed.emit()


func _save_volumes() -> void:
	SaveData.set_volumes(music_slider.value, sfx_slider.value)


func _unhandled_input(event: InputEvent) -> void:
	if visible and event.is_action_pressed("pause"):
		_continue()
		get_viewport().set_input_as_handled()
