class_name Prop
extends PlanarBody
## Pushable furniture. Bounced around by the player and bombs, wiped out by
## explosions. Half of them spawn mirrored so rooms do not look copy-pasted
## (off-centre collision shapes, like a bed's headboard, flip with the model).

@export var random_flip := true

@onready var model: Node3D = get_node_or_null("Model")


func _ready() -> void:
	add_to_group("props")
	if random_flip and model != null and randi() % 2 == 0:
		model.scale.x = -model.scale.x
		for child in get_children():
			if child is CollisionShape3D:
				child.position.x = -child.position.x
