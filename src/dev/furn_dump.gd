extends SceneTree
## Dev: prints every mesh of a scene with its global transform and AABB,
## at rest and at a few points of its model's idle clip.
##   godot --headless --path . -s res://src/dev/furn_dump.gd -- res://src/spawnables/champagne.tscn


func _initialize() -> void:
	var path: String = OS.get_cmdline_user_args()[0]
	var n: Node3D = load(path).instantiate()
	if n is RigidBody3D:
		(n as RigidBody3D).freeze = true
	root.add_child(n)
	for i in 3:
		await process_frame
	_dump(n, "rest")
	var player := ModelUtil.anim_player(n)
	if player == null:
		player = n.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if player != null and player.has_animation("idle"):
		ModelUtil.prepare_animations(player)
		player.play("idle")
		var length := player.current_animation_length
		for t in [0.0, 0.25, 0.5, 0.75]:
			player.seek(length * t, true)
			await process_frame
			_dump(n, "t=%.2f" % t)
	quit()


func _dump(n: Node, label: String) -> void:
	print("--- ", label)
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var ab := mi.global_transform * mi.mesh.get_aabb()
		print("%-20s pos=%s scale=%s aabb=%s..%s" % [mi.name, mi.global_position, mi.global_transform.basis.get_scale(), ab.position, ab.end])
