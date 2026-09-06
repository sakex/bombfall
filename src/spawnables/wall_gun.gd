class_name WallGun
extends PlanarBody
## A turret bolted to a wall or the ceiling. Tracks the player within range
## and fires a plasma bolt every few seconds while the aim is on.

const BULLET := preload("res://src/spawnables/plasma_bullet.tscn")
const MAX_ANGLE := PI / 4.0
const BULLET_SPEED := 3.9        ## 250 px/s
const BARREL_LENGTH := 3.2

## True on the right wall: the model is mirrored and aims the other way.
var mirrored := false:
	set(value):
		mirrored = value
		if is_node_ready():
			model.scale.x = -1.0 if value else 1.0

var _player: Node3D = null

@onready var model: Node3D = $Model
@onready var gun: Node3D = model.find_child("gun", true, false)
@onready var detection: Area3D = $Detection
@onready var timer: Timer = $Timer


func _ready() -> void:
	add_to_group("props")
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_STATIC
	model.scale.x = -1.0 if mirrored else 1.0
	detection.body_entered.connect(func(b): if b is Player: _player = b)
	detection.body_exited.connect(func(b): if b == _player: _player = null)
	timer.timeout.connect(_shoot)


func _process(_delta: float) -> void:
	if _player == null or gun == null:
		return
	gun.rotation.z = _aim_angle()


func _aim_angle() -> float:
	var local := to_local(_player.global_position + Vector3(0, 0.7, 0))
	if mirrored:
		local.x = -local.x
	local -= Vector3(0.7, 1.0, 0.0)
	return clampf(atan2(local.y, local.x), -MAX_ANGLE, MAX_ANGLE)


func _shoot() -> void:
	Sfx.play("plasma")
	if _player == null or gun == null:
		return
	var angle := _aim_angle()
	if angle <= -MAX_ANGLE or angle >= MAX_ANGLE:
		return
	var direction := gun.global_transform.basis.x.normalized()
	direction.z = 0.0
	var bullet: PlasmaBullet = BULLET.instantiate()
	bullet.position = gun.global_position + direction * BARREL_LENGTH
	bullet.set_velocity(direction * BULLET_SPEED)
	get_parent().add_child(bullet)
