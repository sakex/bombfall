class_name AirFan
extends StaticBody3D
## A floor fan: a column of air above it carries whatever floats in.

const LIFT := 26.0
const PLAYER_LIFT := 75.0

var killed := false
var _blades: Node3D

@onready var model: Node3D = $Model
@onready var column: Area3D = $Column


func _ready() -> void:
	add_to_group("props")
	_blades = model.find_child("blades", true, false)


func _physics_process(delta: float) -> void:
	if _blades != null:
		_blades.rotation.y += delta * 30.0
	for body in column.get_overlapping_bodies():
		if body is RigidBody3D:
			body.apply_central_force(Vector3.UP * LIFT * body.mass * body.gravity_scale)
		elif body is Player:
			body.velocity.y += PLAYER_LIFT * delta
			body.velocity.y = minf(body.velocity.y, 14.0)


func kill() -> void:
	if killed:
		return
	killed = true
	queue_free()
