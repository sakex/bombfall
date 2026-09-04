class_name Trampoline
extends Area3D
## Flings whatever touches its mat along its local up axis. Placed on floors
## or, rotated, on walls.

const BOUNCE := 31.25          ## 2000 px/s
const CHECK_EVERY := 1.0 / 30.0

var killed := false
var _since_check := 0.0


func _ready() -> void:
	add_to_group("props")


func _physics_process(delta: float) -> void:
	_since_check += delta
	if _since_check < CHECK_EVERY:
		return
	_since_check = 0.0
	var force := global_transform.basis.y * BOUNCE
	force.z = 0.0
	for body in get_overlapping_bodies():
		if body is RigidBody3D:
			body.apply_central_impulse(force)
		elif body is Player:
			body.lateral_force += force.x / 5.0
			body.velocity.y += force.y / 10.0


func kill() -> void:
	if killed:
		return
	killed = true
	queue_free()
