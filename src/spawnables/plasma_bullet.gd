class_name PlasmaBullet
extends Area3D
## A slow plasma shot from a wall gun or the bat boss.

signal hit(item: Node)

const LIFETIME := 8.0

var velocity := Vector3(4.0, 0.0, 0.0)
## Boss shots pass through bombs so they can build blocks around the arena.
var dont_free_on_bombs := false
var _freed := false
var _age := 0.0

@onready var model: Node3D = $Model


func _ready() -> void:
	body_entered.connect(_handle_collision)


func _physics_process(delta: float) -> void:
	position += velocity * delta
	model.rotation.z += delta * PI * (1.0 if velocity.x >= 0.0 else -1.0)
	_age += delta
	if _age > LIFETIME:
		queue_free()


func _handle_collision(collider: Node) -> void:
	if _freed:
		return
	if collider is Player or collider is Bomb or collider is Drone:
		collider.call_deferred("kill")
	if dont_free_on_bombs and collider is Bomb:
		return
	_freed = true
	hit.emit(collider)
	queue_free()


func set_velocity(v: Vector3) -> void:
	velocity = v
