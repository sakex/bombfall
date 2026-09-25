extends Node3D
## Dev viewer for the hazard models (blender/hazards.py): one scene under the
## game's environment, framed by a camera that can orbit it, with optional
## one-shot clips or script calls fired after a delay.
##   godot --path . res://src/dev/haz_view.tscn --rendering-driver vulkan \
##     --rendering-method mobile --resolution 540x960 -- \
##     --item=res://src/special_levels/boss_bat.tscn [--zoom=10] [--yaw=20] \
##     [--pitch=10] [--play=clip@1.0] [--call=set_dying@1.0] [--at=0.3] \
##     --screenshot=/tmp/x.png:2
## --zoom is the view width in metres; --at freezes the playing clip at that
## fraction after the play/call has fired.

var _item: Node3D


func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	add_child(load("res://src/game/environment.tscn").instantiate())
	_item = load(args.get("item", "res://src/spawnables/drone.tscn")).instantiate()
	if _item is RigidBody3D:
		(_item as RigidBody3D).freeze = true
	add_child(_item)
	await get_tree().process_frame
	var box := _aabb(_item)
	var centre := box.get_center()
	var view := float(args.get("zoom", str(maxf(box.size.x, box.size.y) * 1.4 + 1.0)))
	var cam := Camera3D.new()
	add_child(cam)
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	var dist := 30.0
	cam.fov = rad_to_deg(2.0 * atan((view * 0.5) / dist))
	var yaw := deg_to_rad(float(args.get("yaw", "0")))
	var pitch := deg_to_rad(float(args.get("pitch", "0")))
	var dir := Vector3(sin(yaw) * cos(pitch), sin(pitch), cos(yaw) * cos(pitch))
	cam.position = centre + dir * dist
	cam.look_at(centre)
	cam.far = 400.0
	cam.current = true
	var model := _item.get_node_or_null("Model")
	if args.has("play") and model != null:
		var spec: PackedStringArray = String(args["play"]).split("@")
		await get_tree().create_timer(float(spec[1]) if spec.size() > 1 else 0.5).timeout
		ModelUtil.play(model, spec[0])
	if args.has("call"):
		var spec: PackedStringArray = String(args["call"]).split("@")
		await get_tree().create_timer(float(spec[1]) if spec.size() > 1 else 0.5).timeout
		_item.call(spec[0])
		if _item is RigidBody3D:
			(_item as RigidBody3D).set_deferred("freeze", true)
	if args.has("at"):
		await get_tree().create_timer(float(args["at"])).timeout
		for ap in _item.find_children("*", "AnimationPlayer", true, false):
			(ap as AnimationPlayer).pause()


func _aabb(n: Node3D) -> AABB:
	var box := AABB()
	var first := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var local: AABB = mi.global_transform * mi.get_aabb()
		box = local if first else box.merge(local)
		first = false
	return box
