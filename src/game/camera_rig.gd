class_name CameraRig
extends Node3D
## Follows the player down the shaft. The camera keeps the full 17.5 m width
## of the hotel in view whatever the phone's aspect ratio.

const VIEW_WIDTH := 17.6
const SMOOTHING := 3.0

@export var target: Node3D
@export var distance := 30.0
@export var y_offset := -3.0
## Set by special levels that want to hold the camera still.
var override_target: Node3D = null

@onready var camera: Camera3D = $Camera3D


func _ready() -> void:
	add_to_group("camera_rig")
	camera.keep_aspect = Camera3D.KEEP_WIDTH
	camera.fov = rad_to_deg(2.0 * atan((VIEW_WIDTH * 0.5) / distance))
	camera.position = Vector3(0.0, 0.0, distance)
	camera.near = 0.5
	camera.far = 120.0
	if target != null:
		position = _desired()


func _desired() -> Vector3:
	var focus := override_target if override_target != null else target
	if focus == null:
		return position
	var x := Grid.CENTER_X
	if focus.global_position.x > Grid.INTERIOR_MAX_X + 0.5:
		x = focus.global_position.x + 3.0   # out on the skybridge: lead the runner
	return Vector3(x, focus.global_position.y + y_offset, 0.0)


func _physics_process(delta: float) -> void:
	position = position.lerp(_desired(), 1.0 - exp(-SMOOTHING * delta))


func snap() -> void:
	position = _desired()
