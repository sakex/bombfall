class_name CreditsPopup
extends MenuPopup


func _init() -> void:
	super._init("credits & oss")


func _build() -> void:
	content.add_child(label("BombFall", 56, Color(1.0, 0.6, 0.95)))
	content.add_child(label("a game by\nAlexandre Senges", 36))
	content.add_child(label("music", 46, Color(0.7, 0.95, 1.0)))
	content.add_child(label("Karl Casey @ White Bat Audio", 34))
	content.add_child(label("open source", 46, Color(0.7, 0.95, 1.0)))
	content.add_child(label("Godot Engine\nBlender\nJolt Physics\nKARIXBY font", 34))
	var close_button := button("close", 80)
	close_button.pressed.connect(close)
	content.add_child(close_button)
