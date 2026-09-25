extends SceneTree
## Dev: lists a model's animation clips and their tracks.
##   godot --headless --path . -s res://src/dev/furn_dump_anim.gd -- res://assets/models/desktop.glb


func _initialize() -> void:
	var n: Node = load(OS.get_cmdline_user_args()[0]).instantiate()
	root.add_child(n)
	var player := n.find_child("AnimationPlayer", true, false) as AnimationPlayer
	if player == null:
		print("no AnimationPlayer")
		quit()
		return
	for clip in player.get_animation_list():
		var a := player.get_animation(clip)
		print("clip %s length=%.2f loop=%d tracks=%d" % [clip, a.length, a.loop_mode, a.get_track_count()])
		for t in a.get_track_count():
			print("  %s keys=%d" % [a.track_get_path(t), a.track_get_key_count(t)])
	quit()
