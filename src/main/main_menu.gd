extends Node3D
## Title screen: a live preview of the hotel scrolls past behind the menu.

const PREVIEW_SPEED := 1.1

@onready var world: World = $World
@onready var preview_target: Node3D = $PreviewTarget
@onready var rig: CameraRig = $CameraRig
@onready var popups: CanvasLayer = $Popups

var store: StorePopup
var settings: SettingsPopup
var leaderboard: LeaderboardPopup
var credits: CreditsPopup
var tutorial_modal: TutorialModal


func _ready() -> void:
	get_tree().paused = false
	world.is_preview = true
	world.tracked = preview_target
	rig.target = preview_target
	rig.y_offset = 8.5
	rig.camera.rotation.x = deg_to_rad(-2.5)
	preview_target.position = Vector3(Grid.CENTER_X, -4.0, 0.0)
	rig.snap()
	store = StorePopup.new()
	settings = SettingsPopup.new()
	leaderboard = LeaderboardPopup.new()
	credits = CreditsPopup.new()
	tutorial_modal = TutorialModal.new()
	for popup in [store, settings, leaderboard, credits, tutorial_modal]:
		popups.add_child(popup)
	%PlayButton.pressed.connect(Game.start_game)
	_style_play_button()
	%LeaderboardButton.pressed.connect(leaderboard.open)
	%StoreButton.pressed.connect(store.open)
	%SettingsButton.pressed.connect(settings.open)
	%TutorialButton.pressed.connect(Game.start_tutorial)
	%CreditsButton.pressed.connect(credits.open)
	store.any_buyable.connect(_on_any_buyable)
	store._refresh()
	if not SaveData.data["offered_tutorial"]:
		tutorial_modal.open()
	_refresh_stats()
	SaveData.changed.connect(func(_d): _refresh_stats())
	for label in [$Ui/Layout/VBox/Title, $Ui/Layout/VBox/Title2]:
		var t := create_tween().set_loops()
		t.tween_property(label, "scale", Vector2(1.04, 1.04), 1.1).set_trans(Tween.TRANS_SINE)
		t.tween_property(label, "scale", Vector2.ONE, 1.1).set_trans(Tween.TRANS_SINE)


func _refresh_stats() -> void:
	%Stats.text = "best %d   -   %d coins" % [int(SaveData.data["max_score"]["score"]), int(SaveData.data["coins"])]


func _process(delta: float) -> void:
	preview_target.position.y -= PREVIEW_SPEED * delta


func _on_any_buyable(buyable: bool) -> void:
	%StoreButton.modulate = Color(1.0, 0.9, 0.5) if buyable else Color.WHITE
	%StoreButton.text = "store  *" if buyable else "store"


## The play button is the hot-pink hero of the menu.
func _style_play_button() -> void:
	var button: Button = %PlayButton
	var normal: StyleBoxFlat = button.get_theme_stylebox("normal").duplicate()
	normal.bg_color = Color(0.85, 0.1, 0.55, 1.0)
	normal.border_color = Color(1.0, 0.75, 0.95, 1.0)
	normal.shadow_color = Color(1.0, 0.3, 0.8, 0.7)
	normal.shadow_size = 18
	button.add_theme_stylebox_override("normal", normal)
	var hover: StyleBoxFlat = normal.duplicate()
	hover.bg_color = Color(1.0, 0.2, 0.65, 1.0)
	button.add_theme_stylebox_override("hover", hover)
	var pressed: StyleBoxFlat = normal.duplicate()
	pressed.bg_color = Color(0.3, 0.9, 1.0, 1.0)
	pressed.border_color = Color(0.85, 1.0, 1.0, 1.0)
	pressed.shadow_color = Color(0.3, 0.9, 1.0, 0.7)
	button.add_theme_stylebox_override("pressed", pressed)
