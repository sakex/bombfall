class_name Trampoline
extends Area3D
## Flings whatever touches its mat along its local up axis. Placed on floors
## or, rotated, on walls.

const BOUNCE := 31.25          ## 2000 px/s
const CHECK_EVERY := 1.0 / 30.0
const CLIP_GAP := 0.35          ## seconds between two "bounce" clips

var killed := false
var _since_check := 0.0
var _since_clip := CLIP_GAP

@onready var model: Node3D = $Model


func _ready() -> void:
	add_to_group("props")


func _physics_process(delta: float) -> void:
	_since_check += delta
	_since_clip += delta
	if _since_check < CHECK_EVERY:
		return
	_since_check = 0.0
	var force := global_transform.basis.y * BOUNCE
	force.z = 0.0
	var launched := false
	for body in get_overlapping_bodies():
		if body is RigidBody3D:
			body.apply_central_impulse(force)
			launched = true
		elif body is Player:
			body.lateral_force += force.x / 5.0
			body.velocity.y += force.y / 10.0
			launched = true
	# The mat dips and rebounds (a one-shot clip on the model).
	if launched and _since_clip >= CLIP_GAP:
		_since_clip = 0.0
		ModelUtil.play(model, "bounce")


func kill() -> void:
	if killed:
		return
	killed = true
	queue_free()
