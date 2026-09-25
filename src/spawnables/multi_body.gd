class_name MultiBody
extends Node3D
## A prop made of several independent rigid pieces: the statue and the
## desktop share one glTF model whose named meshes are moved under the body
## with the same name (each body's transform then places its piece); the
## dinner set simply holds ready-made prop scenes. The model's idle clip
## (the desktop's fans, the statue's chest core) keeps playing: its
## AnimationPlayer moves to this node and its tracks are re-pointed at the
## pieces' new homes. The empty root frees itself once every piece is gone.

@onready var model: Node3D = get_node_or_null("Model")


func _ready() -> void:
	var moved := {}
	for body in get_children():
		if body is RigidBody3D:
			if model != null:
				var mesh := model.find_child(body.name.to_lower(), true, false)
				if mesh != null:
					moved[String(mesh.name)] = String(body.name)
					# Keep the mesh's own offset: the body's transform positions it.
					mesh.reparent(body, false)
			body.tree_exited.connect(_on_piece_gone)
	if model != null:
		var player := ModelUtil.anim_player(model)
		if player != null and not moved.is_empty():
			_adopt(player, moved)
		if randi() % 2 == 0:
			_mirror()
		model.queue_free()


## Moves the model's AnimationPlayer here and rewrites every track path
## "piece/..." as "Body/piece/..." (once per shared animation resource; all
## instances of a scene split the same way).
func _adopt(player: AnimationPlayer, moved: Dictionary) -> void:
	for lib_name in player.get_animation_library_list():
		var lib := player.get_animation_library(lib_name)
		for clip in lib.get_animation_list():
			var anim := lib.get_animation(clip)
			if anim.has_meta("_multi_body"):
				continue
			anim.set_meta("_multi_body", true)
			for t in range(anim.get_track_count() - 1, -1, -1):
				var path := String(anim.track_get_path(t))
				var first := path.get_slice("/", 0).get_slice(":", 0)
				if moved.has(first):
					anim.track_set_path(t, NodePath(String(moved[first]) + "/" + path))
				else:
					anim.remove_track(t)  # its node goes away with the model
	var was_playing := player.current_animation
	player.reparent(self, false)
	player.root_node = NodePath("..")
	if was_playing != "":
		player.play(was_playing)


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
