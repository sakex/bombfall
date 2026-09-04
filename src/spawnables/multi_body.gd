class_name MultiBody
extends Node3D
## A prop made of several rigid pieces sharing one glTF model (statue,
## desktop). At start each named mesh of the model is moved under the body
## with the same name; the empty root frees itself once every piece is gone.

@onready var model: Node3D = $Model


func _ready() -> void:
	for body in get_children():
		if body is RigidBody3D:
			var mesh := model.find_child(body.name.to_lower(), true, false)
			if mesh != null:
				mesh.reparent(body, true)
			body.tree_exited.connect(_on_piece_gone)
	if randi() % 2 == 0:
		_mirror()
	model.queue_free()


func _mirror() -> void:
	for body in get_children():
		if body is RigidBody3D:
			for child in body.get_children():
				if child is MeshInstance3D:
					child.position.x = -child.position.x
					child.scale.x = -child.scale.x
				elif child is CollisionShape3D:
					child.position.x = -child.position.x


func _on_piece_gone() -> void:
	if not is_inside_tree():
		return
	for child in get_children():
		if child is RigidBody3D and not child.is_queued_for_deletion():
			return
	queue_free()


func kill() -> void:
	for body in get_children():
		if body is RigidBody3D and body.has_method("kill"):
			body.kill()
