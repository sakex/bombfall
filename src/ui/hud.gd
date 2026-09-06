class_name Hud
extends CanvasLayer
## In-game overlay: score, depth, shields, an active-doubler badge, the
## pause button and the touch controls.

signal pause_pressed

const BUTTON_MARGIN := 44.0
const BUTTON_SIZE := 210.0
const TOP_BAR_HEIGHT := 160.0       ## score panel and pause button live here

var _player: Player
var _score_tween: Tween

@onready var score_label: Label = %Score
@onready var depth_label: Label = %Depth
@onready var shield_bar: ShieldBar = %ShieldBar
@onready var pause_button: TextureButton = %PauseButton
@onready var doubler_badge: PanelContainer = %DoublerBadge
@onready var doubler_label: Label = %DoublerLabel
@onready var toast: Label = %Toast
@onready var joystick: Joystick = $Touch/Joystick
@onready var jump_zone: TouchScreenButton = $Touch/JumpZone
@onready var jump_hint: TextureRect = $Touch/JumpHint


func _ready() -> void:
	pause_button.pressed.connect(func(): pause_pressed.emit())
	get_viewport().size_changed.connect(_layout_touch)
	_layout_touch()
	set_score(0)
	# Thumb controls only where there is a thumb (debug builds keep them for screenshots).
	$Touch.visible = OS.has_feature("mobile") or DisplayServer.is_touchscreen_available() or OS.is_debug_build()
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


## The whole left half of the screen is the stick and the whole right half
## jumps (below the top bar, which keeps the pause button); the round button
## is only a hint, the zones react anywhere.
func _layout_touch() -> void:
	var size := get_viewport().get_visible_rect().size
	var top := TOP_BAR_HEIGHT
	joystick.position = Vector2(0.0, top)
	joystick.size = Vector2(size.x * 0.5, size.y - top)
	var zone := Vector2(size.x * 0.5, size.y - top)
	(jump_zone.shape as RectangleShape2D).size = zone
	# A RectangleShape2D is centred on the node, so park the node mid-zone.
	jump_zone.position = Vector2(size.x * 0.75, top + zone.y * 0.5)
	jump_hint.size = Vector2(BUTTON_SIZE, BUTTON_SIZE)
	jump_hint.position = Vector2(size.x - BUTTON_MARGIN - BUTTON_SIZE, size.y - BUTTON_MARGIN - BUTTON_SIZE)

