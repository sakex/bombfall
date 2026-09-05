class_name Hud
extends CanvasLayer
## In-game overlay: score, depth, shields, an active-doubler badge, the
## pause button and the touch controls.

signal pause_pressed

const BUTTON_MARGIN := 40.0
const BUTTON_SIZE := 190.0

var _player: Player
var _score_tween: Tween

@onready var score_label: Label = %Score
@onready var depth_label: Label = %Depth
@onready var shield_bar: ShieldBar = %ShieldBar
@onready var pause_button: Button = %PauseButton
@onready var doubler_badge: PanelContainer = %DoublerBadge
@onready var doubler_label: Label = %DoublerLabel
@onready var toast: Label = %Toast
@onready var touch_left: TouchScreenButton = $Touch/Left
@onready var touch_right: TouchScreenButton = $Touch/Right
@onready var touch_jump: TouchScreenButton = $Touch/Jump


func _ready() -> void:
	pause_button.pressed.connect(func(): pause_pressed.emit())
	get_viewport().size_changed.connect(_layout_touch)
	_layout_touch()
	set_score(0)
	doubler_badge.visible = false
	toast.modulate.a = 0.0


func bind_player(player: Player) -> void:
	_player = player
	player.score_changed.connect(set_score)
	player.shields_changed.connect(shield_bar.set_state)
	player.doubler_changed.connect(_on_doubler)
	player.pickup_taken.connect(show_toast)
	shield_bar.set_state(player.max_shields, player.active_shields)


func _process(_delta: float) -> void:
	if _player == null:
		return
	depth_label.text = "%d m" % maxi(int(-_player.position.y), 0)
	if _player.doubler_time > 0.0:
		doubler_label.text = "x2  %ds" % ceili(_player.doubler_time)


func set_score(score: int) -> void:
	score_label.text = "%d" % score
	if _score_tween != null:
		_score_tween.kill()
	score_label.scale = Vector2(1.25, 1.25)
	_score_tween = create_tween()
	_score_tween.tween_property(score_label, "scale", Vector2.ONE, 0.18).set_trans(Tween.TRANS_BACK)


func _on_doubler(active: bool) -> void:
	doubler_badge.visible = active


func show_toast(text: String) -> void:
	toast.text = text
	toast.modulate.a = 1.0
	toast.scale = Vector2(1.3, 1.3)
	var t := create_tween()
	t.tween_property(toast, "scale", Vector2.ONE, 0.2).set_trans(Tween.TRANS_BACK)
	t.tween_interval(0.9)
	t.tween_property(toast, "modulate:a", 0.0, 0.4)


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
