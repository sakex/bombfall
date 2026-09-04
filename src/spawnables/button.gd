class_name PressButton
extends PlanarBody
## A floor button. Press it with anything heavy: nine times out of ten it
## drops a coin from above, otherwise a bomb.

const BOMB_SCENE := "res://src/actors/bomb.tscn"
const COIN_SCENE := "res://src/actors/coin.tscn"
const DROP_HEIGHT := 7.5        ## 480 px
const PRESS_DEPTH := 0.15

var coin_budget := 0
var _world: Node = null
var _pressed := false
var _overlaps := 0

@onready var model: Node3D = $Model
@onready var top: Node3D = model.find_child("top", true, false)
@onready var press_area: Area3D = $PressArea
@onready var sfx_click: AudioStreamPlayer3D = $SfxClick


func _ready() -> void:
	add_to_group("props")
	press_area.body_entered.connect(_on_enter)
	press_area.body_exited.connect(_on_exit)


func set_world(world: Node) -> void:
	_world = world


func _process(delta: float) -> void:
	if top == null:
		return
	var target := -PRESS_DEPTH if _pressed else 0.0
	top.position.y = lerpf(top.position.y, target, minf(1.0, delta * 15.0))


func _on_enter(body: Node) -> void:
	if body == self:
		return
	_overlaps += 1
	if not _pressed:
		_pressed = true
		_activate()


func _on_exit(body: Node) -> void:
	if body == self:
		return
	_overlaps = maxi(_overlaps - 1, 0)
	if _overlaps == 0:
		_pressed = false


func _activate() -> void:
	sfx_click.play()
	if _world == null:
		return
	var above := global_position + Vector3(0.0, DROP_HEIGHT, 0.0)
	if randi() % 10 == 0:
		_world.spawn_scene(BOMB_SCENE, above, {"bomb_time": 4.0, "bomb_scale": 0.8})
		kill()
	else:
		_world.spawn_coin(maxi(coin_budget / 5, 1), above)
