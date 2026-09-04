class_name BatHeart
extends Node3D
## The boss's heart, dangling on a short rope near the ceiling. Grab it to
## win the fight.

signal heart_taken

@onready var heart_body: RigidBody3D = $HeartBody
@onready var area: Area3D = $HeartBody/Area
@onready var rope: Rope = $Rope
@onready var anchor: StaticBody3D = $Anchor


func _ready() -> void:
	visible = false
	rope.connect_head(heart_body)
	rope.connect_tail(anchor)
	area.body_entered.connect(_on_body)
	heart_body.collision_layer = 0
	area.monitoring = false


func enable_heart() -> void:
	visible = true
	heart_body.collision_layer = Layers.PICKUP
	area.monitoring = true


func _on_body(body: Node) -> void:
	if body is Player:
		heart_body.queue_free()
		heart_taken.emit()
