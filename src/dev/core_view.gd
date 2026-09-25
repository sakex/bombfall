extends Node
## Dev tool for the core gameplay objects: runs the gallery (same arguments)
## and adds a free close-up camera and an explosion trigger.
##   godot --path . res://src/dev/core_view.tscn --rendering-method mobile -- \
##     --items=res://src/actors/bomb.tscn --focus=8.5,-2 --view=3 \
##     [--explode=1.0] [--shot=/tmp/x.png --shot-at=1.25]
## --focus is a world point (x,y) to centre, --view the width in metres.
## --explode blows up every bomb after that many seconds (physics time);
## --shot-at freezes time at that moment (physics time) and saves the frame.

var _t := 0.0
var _exploded := false
var _args := {}
var _shot_taken := false


func _ready() -> void:
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		_args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	add_child(load("res://src/dev/gallery.tscn").instantiate())
	for i in 4:
		await get_tree().process_frame
	if _args.has("focus") or _args.has("view"):
		var cam := get_viewport().get_camera_3d()
		var view := float(_args.get("view", "6"))
		var dist := float(_args.get("dist", "30"))
		cam.fov = rad_to_deg(2.0 * atan((view * 0.5) / dist))
		var f: PackedStringArray = String(_args.get("focus", "8.5,-4")).split(",")
		cam.position = Vector3(float(f[0]), float(f[1]), dist)


func _physics_process(delta: float) -> void:
	_t += delta
	if _args.has("explode") and not _exploded and _t >= float(_args["explode"]):
		_exploded = true
		for b in get_tree().get_nodes_in_group("bombs"):
			(b as Bomb).no_collisions = false
			b.explode()
	if _args.has("shot") and not _shot_taken and _t >= float(_args.get("shot-at", "2.0")):
		_shot_taken = true
		Engine.time_scale = 0.0
		_capture.call_deferred()


func _capture() -> void:
	for i in 3:
		await RenderingServer.frame_post_draw
	var img := get_viewport().get_texture().get_image()
	img.save_png(String(_args["shot"]))
	print("SHOT ", _args["shot"])
	Engine.time_scale = 1.0
	get_tree().quit()
