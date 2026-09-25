extends Node3D
## Dev tool: lines up game scenes on a floor inside a themed room, under the
## game's own environment and lights, and frames them with a camera.
##   godot --path . res://src/dev/gallery.tscn --rendering-driver vulkan \
##     --rendering-method mobile --resolution 540x960 -- \
##     --items=res://src/spawnables/toilet.tscn,res://src/actors/bomb.tscn \
##     [--theme=room1] [--zoom=8] [--game-scale] [--turn=25] [--at=0.8] \
##     --screenshot=/path/shot.png:2.5
## --zoom is the view width in metres (default fits the items); --game-scale
## uses the real in-game camera (17.6 m wide from 30 m); --turn yaws every
## item by that many degrees to show depth; --at=<t> freezes animations at
## a point (default: play normally).

const FLOOR_ROW := 6

var _items: Array[Node3D] = []


func _ready() -> void:
	var args := {}
	for a in OS.get_cmdline_user_args():
		var kv := a.trim_prefix("--").split("=", true, 1)
		args[kv[0]] = kv[1] if kv.size() > 1 else "1"
	var env_scene: Node = load("res://src/game/environment.tscn").instantiate()
	add_child(env_scene)
	if args.has("noshadow"):
		(env_scene.get_node("KeyLight") as DirectionalLight3D).shadow_enabled = false
	if not args.has("no-city"):
		add_child(load("res://src/world/city.tscn").instantiate())
	var cells := CellGrid.new()
	cells.add_to_group("cell_grid")
	add_child(cells)
	for cx in range(0, Grid.WALL_RIGHT + 1):
		cells.set_cell(cx, FLOOR_ROW, CellGrid.Kind.FLOOR)
	for row in range(0, FLOOR_ROW):
		cells.set_cell(0, row, CellGrid.Kind.FLOOR)
		cells.set_cell(Grid.WALL_RIGHT, row, CellGrid.Kind.FLOOR)
	var theme_id: String = args.get("theme", "room1")
	for theme in SpawnRegistry.themes():
		if theme["id"] == theme_id:
			var bd := Backdrop.build(theme, 0, FLOOR_ROW)
			add_child(bd)
			if args.has("no-omni"):
				for l in bd.find_children("*", "OmniLight3D", true, false):
					l.queue_free()
			if args.has("room-noshadow"):
				for g in bd.find_children("*", "GeometryInstance3D", true, false):
					(g as GeometryInstance3D).cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF
	var paths: PackedStringArray = String(args.get("items", "")).split(",", false)
	var total := 0.0
	var widths: Array[float] = []
	for p in paths:
		var n: Node3D = load(p).instantiate()
		if n is RigidBody3D:
			(n as RigidBody3D).freeze = true
		_items.append(n)
		var w := 2.2
		widths.append(w)
		total += w
	var x := Grid.CENTER_X - total * 0.5
	var turn := deg_to_rad(float(args.get("turn", "0")))
	for i in _items.size():
		var n := _items[i]
		add_child(n)
		var aabb := _aabb(n)
		widths[i] = maxf(aabb.size.x, 1.0) + 0.6
	total = 0.0
	for w in widths:
		total += w
	x = Grid.CENTER_X - total * 0.5
	for i in _items.size():
		var n := _items[i]
		var aabb := _aabb(n)
		var floor_y := -float(FLOOR_ROW)
		n.position = Vector3(x + widths[i] * 0.5 - aabb.get_center().x, floor_y - aabb.position.y if aabb.position.y < -0.05 or aabb.position.y > 0.05 else floor_y, 0.0)
		n.rotation.y = turn
		x += widths[i]
	await get_tree().process_frame
	for i in _items.size():
		var mdl := _items[i].get_node_or_null("Model") as Node3D
		print("GALLERY item %d %s model_scale=%s" % [i, _items[i].name, mdl.scale if mdl else "-"])
	var cam := Camera3D.new()
	add_child(cam)
	cam.keep_aspect = Camera3D.KEEP_WIDTH
	var view := float(args.get("zoom", str(maxf(total + 1.0, 4.0))))
	var dist := 30.0
	if args.has("game-scale"):
		view = 17.6
	cam.fov = rad_to_deg(2.0 * atan((view * 0.5) / dist))
	var focus_y := -float(FLOOR_ROW) + minf(view * 0.35, 4.0)
	cam.position = Vector3(Grid.CENTER_X, focus_y, dist)
	cam.far = 400.0
	cam.current = true
	if args.has("at"):
		await get_tree().process_frame
		for ap in find_children("*", "AnimationPlayer", true, false):
			var player := ap as AnimationPlayer
			if player.current_animation != "":
				player.seek(float(args["at"]) * player.current_animation_length, true)
				player.pause()


func _aabb(n: Node) -> AABB:
	var box := AABB()
	var first := true
	for m in n.find_children("*", "MeshInstance3D", true, false):
		var mi := m as MeshInstance3D
		var local: AABB = (n as Node3D).global_transform.affine_inverse() * mi.global_transform * mi.get_aabb()
		box = local if first else box.merge(local)
		first = false
	return box
