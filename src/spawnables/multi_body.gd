class_name MultiBody
extends Node3D
## A prop made of several independent rigid pieces: the statue and the
## desktop share one glTF model whose named meshes are moved under the body
## with the same name (each body's transform then places its piece); the
## dinner set simply holds ready-made prop scenes. The empty root frees
## itself once every piece is gone.

@onready var model: Node3D = get_node_or_null("Model")


func _ready() -> void:
	for body in get_children():
		if body is RigidBody3D:
			if model != null:
				var mesh := model.find_child(body.name.to_lower(), true, false)
				if mesh != null:
					# Keep the mesh's own offset: the body's transform positions it.
					mesh.reparent(body, false)
			body.tree_exited.connect(_on_piece_gone)
	if model != null:
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
