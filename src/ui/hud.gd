class_name Hud
extends CanvasLayer
## In-game overlay: score, shield bar, pause button and the touch controls.

signal pause_pressed

const BUTTON_MARGIN := 40.0
const BUTTON_SIZE := 190.0

@onready var score_label: Label = %Score
@onready var shield_bar: ShieldBar = %ShieldBar
@onready var pause_button: Button = %PauseButton
@onready var touch_left: TouchScreenButton = $Touch/Left
@onready var touch_right: TouchScreenButton = $Touch/Right
@onready var touch_jump: TouchScreenButton = $Touch/Jump


func _ready() -> void:
	pause_button.pressed.connect(func(): pause_pressed.emit())
	get_viewport().size_changed.connect(_layout_touch)
	_layout_touch()
	set_score(0)


func bind_player(player: Player) -> void:
	player.score_changed.connect(set_score)
	player.shields_changed.connect(shield_bar.set_state)
	shield_bar.set_state(player.max_shields, player.active_shields)


func set_score(score: int) -> void:
	score_label.text = "SCORE %d" % score


func set_touch_controls_visible(visible: bool) -> void:
	$Touch.visible = visible


func _layout_touch() -> void:
	var size := get_viewport().get_visible_rect().size
	for button in [touch_left, touch_right, touch_jump]:
		button.scale = Vector2.ONE * (BUTTON_SIZE / button.texture_normal.get_width())
	var y := size.y - BUTTON_MARGIN - BUTTON_SIZE
	touch_left.position = Vector2(BUTTON_MARGIN, y)
	touch_right.position = Vector2(BUTTON_MARGIN * 2 + BUTTON_SIZE, y)
	touch_jump.position = Vector2(size.x - BUTTON_MARGIN - BUTTON_SIZE, y)
