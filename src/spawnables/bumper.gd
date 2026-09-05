class_name Bumper
extends StaticBody3D
## A pinball bumper: anything that touches its cap is flung away from it.

const KICK := 14.0
const PLAYER_KICK := 16.0

var killed := false
var _flash := 0.0
var _light: StandardMaterial3D
var _cooldowns: Dictionary = {}

@onready var model: Node3D = $Model
@onready var area: Area3D = $Area
@onready var sfx: AudioStreamPlayer3D = $Sfx


func _ready() -> void:
	add_to_group("props")
	area.body_entered.connect(_on_body)
	_light = ModelUtil.own_material(ModelUtil.find_mesh(model, "cap_light"))


func _on_body(body: Node) -> void:
	if body == self:
		return
	var id := body.get_instance_id()
	var now := Time.get_ticks_msec()
	if now - int(_cooldowns.get(id, -10000)) < 250:
		return
	_cooldowns[id] = now
	var origin := global_position + Vector3(0.0, 0.9, 0.0)
	var away := (body as Node3D).global_position + Vector3(0, 0.6, 0) - origin
	away.z = 0.0
	if away.length() < 0.05:
		away = Vector3.UP
	away = away.normalized()
	if away.y < 0.25:
		away = (away + Vector3(0, 0.5, 0)).normalized()
	if body is RigidBody3D:
		body.linear_velocity = away * KICK
	elif body is Player:
		body.velocity = away * PLAYER_KICK
		body.lateral_force = away.x * PLAYER_KICK * 0.5
	_flash = 1.0
	sfx.play()


func _process(delta: float) -> void:
	_flash = maxf(_flash - delta * 4.0, 0.0)
	if _light != null:
		_light.emission_energy_multiplier = 1.0 + 8.0 * _flash
	model.scale = Vector3(1.0 + _flash * 0.15, 1.0 - _flash * 0.1, 1.0 + _flash * 0.15)


func kill() -> void:
	if killed:
		return
	killed = true
	queue_free()
