extends SceneTree
## Dev: checks that multi-body props keep their idle clip after MultiBody
## splits the model (the desktop's fans spin, the statue's core pulses).
##   godot --headless --path . -s res://src/dev/furn_anim_check.gd


func _initialize() -> void:
	var ok := true
	for spec in [["res://src/spawnables/desktop.tscn", "fan_1", "rotation"], ["res://src/spawnables/statue.tscn", "core", "scale"]]:
		var n: Node3D = load(spec[0]).instantiate()
		root.add_child(n)
		for body in n.get_children():
			if body is RigidBody3D:
				(body as RigidBody3D).freeze = true
		for i in 5:
			await process_frame
		var player := n.get_node_or_null("AnimationPlayer") as AnimationPlayer
		var target := n.find_child(spec[1], true, false) as Node3D
		var a: Variant = target.get(spec[2]) if target != null else null
		for i in 20:
			await process_frame
		var b: Variant = target.get(spec[2]) if target != null else null
		var playing: bool = player != null and player.is_playing() and player.current_animation == "idle"
		var moved: bool = a != null and a != b
		if player != null:
			var an := player.get_animation("idle")
			print("  assigned=%s current=%s root=%s tracks=%s" % [player.assigned_animation, player.current_animation, player.root_node,
				[] if an == null else range(an.get_track_count()).map(func(t): return String(an.track_get_path(t)))])
		print("FURN_ANIM %s player=%s playing=%s node=%s moved=%s (%s -> %s)" % [spec[0].get_file(), player != null, playing, target != null, moved, a, b])
		ok = ok and playing and moved
		n.queue_free()
	print("FURN_ANIM_RESULT ok=%s" % ok)
	quit()
