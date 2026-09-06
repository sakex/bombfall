class_name Drone
extends PlanarBody
## A patrol drone hovering across the room. Touching the player knocks it
## out of the air; bumping into anything else blows it up.

const EXPLOSION := preload("res://src/actors/explosion.tscn")
@export var min_x := 4.1              ## 264 px
@export var max_x := 12.9             ## 824 px
const SPEED := 4.7              ## 300 px/s
const MAX_IMPULSE := Vector2(4.7, 0.8)
const MAX_ROTATE := PI
const FALL_GRAVITY := 0.78

var turned_off := false
var _target_speed := Vector2(SPEED, 0.0)
var _hover_y := 0.0
var _rotors: Array[Node3D] = []

@onready var model: Node3D = $Model


func _ready() -> void:
	add_to_group("drones")
	gravity_scale = 0.0
	contact_monitor = true
	max_contacts_reported = 4
	if position.x > (max_x + min_x) * 0.5:
		_target_speed.x = -SPEED
	_hover_y = position.y
	for i in 4:
		var r := model.find_child("rotor_%d" % (i + 1), true, false)
		if r != null:
			_rotors.append(r)
	_set_mirrored(_target_speed.x > 0.0)


func _set_mirrored(mirrored: bool) -> void:
	model.scale.x = -1.0 if mirrored else 1.0


func turn_off() -> void:
	if turned_off:
		return
	turned_off = true
	gravity_scale = FALL_GRAVITY


func _physics_process(delta: float) -> void:
	_handle_collisions()
	if killed:
		return
	if not turned_off:
		for r in _rotors:
			r.rotation.y += delta * 45.0
	if turned_off:
		return
	if absf(rotation.z) > PI / 2.0:
		turn_off()
		return
	if position.x <= min_x:
		_target_speed.x = SPEED
	elif position.x >= max_x:
		_target_speed.x = -SPEED
	_target_speed.y = _hover_y - position.y
	_set_mirrored(_target_speed.x > 0.0)
	var diff := Vector2(_target_speed.x - linear_velocity.x, _target_speed.y - linear_velocity.y)
	diff = Vector2(clampf(diff.x, -MAX_IMPULSE.x, MAX_IMPULSE.x), clampf(diff.y, -MAX_IMPULSE.y, MAX_IMPULSE.y))
	linear_velocity += Vector3(diff.x, diff.y, 0.0) * delta * 4.0
	rotation.z -= clampf(rotation.z, -MAX_ROTATE, MAX_ROTATE) * delta


func _handle_collisions() -> void:
	for body in get_colliding_bodies():
		if body is Player:
			turn_off()
		elif not (body is Bomb):
			kill()
			return


func _on_killed() -> void:
	var explosion: Explosion = EXPLOSION.instantiate()
	explosion.set_explosion_scale(0.7)
	explosion.position = global_position
	get_parent().add_child(explosion)
