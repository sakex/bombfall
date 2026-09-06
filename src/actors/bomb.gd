class_name Bomb
extends PlanarBody
## A bomb. Counts down while the player is close, then explodes; also
## explodes at once when another explosion reaches it (chain reactions).

const EXPLOSION := preload("res://src/actors/explosion.tscn")
const BASE_RADIUS := 1.75           ## 112 px
const COUNTDOWN_DISTANCE := 13.0    ## 832 px: too far away and the fuse pauses
const FORGET_DISTANCE := 78.0       ## 5000 px: far behind the player, remove
const BOUNCE_SOUND_SPEED := 1.6

@export var bomb_time := 4.0
## Placed in a level as a hazard: never counts down, only chain-explodes.
@export var no_timeout := false
## Decorative bombs (tutorial pictures) never hurt anything.
@export var no_collisions := false

var bomb_scale := 1.0
var alive_for := 0.0
var _player: Node3D = null
var _ring_material: StandardMaterial3D
var _display_material: StandardMaterial3D

@onready var model: Node3D = $Model
@onready var shape: CollisionShape3D = $Shape
@onready var detection: Area3D = $Detection
@onready var sfx_bounce: AudioStreamPlayer3D = $SfxBounce


func _ready() -> void:
	add_to_group("bombs")
	body_entered.connect(_on_body_entered)
	detection.body_entered.connect(_on_player_near)
	_ring_material = ModelUtil.own_material(ModelUtil.find_mesh(model, "ring"))
	_display_material = ModelUtil.own_material(ModelUtil.find_mesh(model, "display"))
	# Every bomb gets its own shape: the scene's shape resource is shared by
	# all instances, and resizing it for one bomb used to resize them all.
	shape.shape = shape.shape.duplicate()
	set_bomb_scale(bomb_scale)
	if no_collisions:
		collision_layer = 0
		collision_mask = 0
		freeze = true
	if no_timeout and _ring_material != null:
		_ring_material.emission_energy_multiplier = 0.3


func set_bomb_scale(value: float) -> void:
	bomb_scale = value
	if not is_node_ready():
		return
	model.scale = Vector3.ONE * value
	(shape.shape as SphereShape3D).radius = BASE_RADIUS * value
	mass = 10.0 * value


func _process(delta: float) -> void:
	if no_timeout:
		return
	if _player == null and not no_collisions:
		return
	if not no_collisions:
		var distance := global_position.distance_to(_player.global_position)
		if distance > COUNTDOWN_DISTANCE:
			if distance > FORGET_DISTANCE and _player.global_position.y < global_position.y:
				queue_free()
			return
	alive_for += delta
	var t := clampf(alive_for / bomb_time, 0.0, 1.0)
	if _ring_material != null:
		_ring_material.emission_energy_multiplier = 1.0 + 6.0 * t
		_ring_material.emission = Color(0.05, 0.85, 0.95).lerp(Color(1.0, 0.15, 0.1), t)
	if _display_material != null:
		var blink := fmod(alive_for * (2.0 + 10.0 * t), 1.0) < 0.5
		_display_material.emission_energy_multiplier = 6.0 if blink else 1.0
	if alive_for >= bomb_time and not no_collisions:
		explode()


func explode() -> void:
	if killed:
		return
	killed = true
	var explosion: Explosion = EXPLOSION.instantiate()
	explosion.set_explosion_scale(bomb_scale)
	explosion.position = global_position
	explosion.harmless = no_collisions
	get_parent().add_child(explosion)
	queue_free()


func kill() -> void:
	explode()


func _on_body_entered(_body: Node) -> void:
	if linear_velocity.length() > BOUNCE_SOUND_SPEED:
		sfx_bounce.play()


func _on_player_near(body: Node3D) -> void:
	if body is Player:
		_player = body
