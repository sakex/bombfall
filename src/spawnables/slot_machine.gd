class_name SlotMachine
extends PlanarBody
## A one-armed bandit. Anything that hits it hard enough pulls the lever:
## the reels spin, then it pays out coins, drops a bomb, or does nothing.

const COIN := preload("res://src/actors/coin.tscn")
const BOMB_SCENE := "res://src/actors/bomb.tscn"
const HIT_SPEED := 3.0
const SPIN_TIME := 1.3
const COOLDOWN := 3.0

var coin_budget := 0
var _world: Node = null
var _spinning := 0.0
var _cooldown := 0.0
var _reels: Array[Node3D] = []
var _marquee: StandardMaterial3D

@onready var model: Node3D = $Model
@onready var lever: Node3D = model.find_child("lever", true, false)
@onready var sfx: AudioStreamPlayer3D = $Sfx


func _ready() -> void:
	add_to_group("props")
	contact_monitor = true
	max_contacts_reported = 4
	body_entered.connect(_on_hit)
	for i in 3:
		var r := model.find_child("reel_%d" % (i + 1), true, false)
		if r != null:
			_reels.append(r)
	_marquee = ModelUtil.own_material(ModelUtil.find_mesh(model, "marquee"))
	if randi() % 2 == 0:
		model.scale.x = -1.0


func set_world(world: Node) -> void:
	_world = world


func _on_hit(body: Node) -> void:
	if _cooldown > 0.0 or _spinning > 0.0:
		return
	var speed := 0.0
	if body is RigidBody3D:
		speed = (body.linear_velocity - linear_velocity).length()
	elif body is Player:
		speed = body.velocity.length()
	if speed >= HIT_SPEED:
		_spinning = SPIN_TIME
		Sfx.play("slot_spin")


func _process(delta: float) -> void:
	_cooldown = maxf(_cooldown - delta, 0.0)
	if lever != null:
		lever.rotation.x = lerpf(lever.rotation.x, 1.2 if _spinning > 0.0 else 0.0, minf(1.0, delta * 8.0))
	if _marquee != null:
		_marquee.emission_energy_multiplier = 4.0 if fmod(Time.get_ticks_msec() / 250.0, 2.0) < 1.0 else 1.5
	if _spinning <= 0.0:
		return
	_spinning -= delta
	for i in _reels.size():
		var speed := 25.0 * (1.0 + i * 0.3) * clampf(_spinning / SPIN_TIME * 2.0, 0.0, 1.0)
		_reels[i].rotation.x += delta * speed
	if _spinning <= 0.0:
		for r in _reels:
			r.rotation.x = roundf(r.rotation.x / (PI / 2.0)) * (PI / 2.0)
		_cooldown = COOLDOWN
		_payout()


func _payout() -> void:
	var roll := randf()
	var tray := global_position + Vector3(0.0, 0.7, 0.0) + global_transform.basis.z * 0.9
	if roll < 0.6:
		Sfx.play("slot_win")
		var each := maxi(coin_budget / 3, 1)
		for i in 3:
			var coin: Coin = COIN.instantiate()
			coin.value = each
			coin.position = tray + Vector3(-0.4 + i * 0.4, 0.0, 0.0)
			get_parent().add_child(coin)
			coin.apply_central_impulse(Vector3(randf_range(-6.0, 6.0), 18.0, 0.0))
	elif roll < 0.75 and _world != null:
		_world.spawn_scene(BOMB_SCENE, global_position + Vector3(0.0, 4.5, 0.0), {"bomb_time": 3.0, "bomb_scale": 0.7})
