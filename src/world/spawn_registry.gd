class_name SpawnRegistry
## The catalogue of everything the hotel can be furnished with, the room
## themes that pick from it, and the shield items. Numbers come straight
## from the original Rust tables (pixels turned into 1 m cells).

const W := SpawnableSpec.Where

const SCENES := "res://src/spawnables/"

static var _specs: Dictionary = {}
static var _shield_items: Array[SpawnableSpec] = []
static var _themes: Array[Dictionary] = []


static func spec(id: String) -> SpawnableSpec:
	_ensure()
	return _specs.get(id)


static func all_specs() -> Dictionary:
	_ensure()
	return _specs


## Shield items weighted by how likely they are (a battery is 10x a crate).
static func shield_items() -> Array[SpawnableSpec]:
	_ensure()
	return _shield_items


static func themes() -> Array[Dictionary]:
	_ensure()
	return _themes


static func _ensure() -> void:
	if not _specs.is_empty():
		return
	for s in _build_specs():
		if s.available():
			_specs[s.id] = s
		else:
			print("SpawnRegistry: '%s' skipped, missing scene %s" % [s.id, s.scene_path])
	for entry in [["shield_battery", 10], ["shield_core", 2], ["magnet", 4], ["crate", 1], ["doubler", 3]]:
		var s: SpawnableSpec = _specs.get(entry[0])
		if s == null:
			continue
		for i in entry[1]:
			_shield_items.append(s)
	_themes = _build_themes()


static func _build_specs() -> Array[SpawnableSpec]:
	var out: Array[SpawnableSpec] = []
	# Hazards with their own behaviour.
	out.append(SpawnableSpec.new("bomb", "res://src/actors/bomb.tscn", Vector2i(4, 4), 1)
		.floor().centered().per_level(4).with({"no_timeout": true}))
	out.append(SpawnableSpec.new("trampoline", SCENES + "trampoline.tscn", Vector2i(2, 2), 5)
		.floor().wall().per_level(4).invert().level_bound().placed_by(_place_trampoline))
	out.append(SpawnableSpec.new("wallgun", SCENES + "wall_gun.tscn", Vector2i(4, 3), 10)
		.wall().roof().per_level(4).invert().level_bound().placed_by(_place_wallgun))
	out.append(SpawnableSpec.new("drone", SCENES + "drone.tscn", Vector2i(13, 2), 4)
		.float_().per_level(5).level_bound().placed_by(_place_drone))
	out.append(SpawnableSpec.new("light_ring", SCENES + "light_ring.tscn", Vector2i(4, 4), 3)
		.floor().placed_by(_place_light_ring))
	out.append(SpawnableSpec.new("button", SCENES + "button.tscn", Vector2i(2, 1), 1)
		.floor().level_bound())
	out.append(SpawnableSpec.new("fire_zone", SCENES + "fire_zone.tscn", Vector2i(2, 2), 5)
		.floor().centered())
	# Ropes.
	out.append(SpawnableSpec.new("roped_bomb", SCENES + "roped_bomb.tscn", Vector2i(4, 4), 3)
		.float_().per_level(3))
	out.append(SpawnableSpec.new("roped_bomb_two_ways", SCENES + "roped_bomb_two_ways.tscn", Vector2i(4, 4), 3)
		.float_())
	out.append(SpawnableSpec.new("roped_painting", SCENES + "roped_painting.tscn", Vector2i(4, 5), 4)
		.float_().per_level(3))
	# Plain furniture: pushed around, blown up, otherwise harmless.
	out.append(SpawnableSpec.new("statue", SCENES + "statue.tscn", Vector2i(4, 8), 1).floor())
	out.append(SpawnableSpec.new("desktop", SCENES + "desktop.tscn", Vector2i(4, 5), 1).floor())
	out.append(SpawnableSpec.new("toilet", SCENES + "toilet.tscn", Vector2i(2, 3), 1).floor())
	out.append(SpawnableSpec.new("bathtub", SCENES + "bathtub.tscn", Vector2i(6, 2), 3).floor())
	out.append(SpawnableSpec.new("floor_painting", SCENES + "painting.tscn", Vector2i(4, 4), 3).floor().centered())
	out.append(SpawnableSpec.new("treadmill", SCENES + "treadmill.tscn", Vector2i(4, 3), 3).floor())
	out.append(SpawnableSpec.new("bench_press", SCENES + "bench_press.tscn", Vector2i(4, 4), 3).floor())
	out.append(SpawnableSpec.new("bed1", SCENES + "bed1.tscn", Vector2i(6, 2), 3).floor())
	out.append(SpawnableSpec.new("bed2", SCENES + "bed2.tscn", Vector2i(6, 3), 3).floor())
	out.append(SpawnableSpec.new("bed_rich", SCENES + "bed_rich.tscn", Vector2i(6, 3), 3).floor())
	out.append(SpawnableSpec.new("tv", SCENES + "tv.tscn", Vector2i(2, 3), 2).floor())
	out.append(SpawnableSpec.new("champagne", SCENES + "champagne.tscn", Vector2i(1, 1), 1).floor().per_level(5))
	out.append(SpawnableSpec.new("cake", SCENES + "cake.tscn", Vector2i(1, 1), 1).floor())
	out.append(SpawnableSpec.new("chair", SCENES + "chair.tscn", Vector2i(3, 3), 1).floor())
	out.append(SpawnableSpec.new("table_with_chairs", SCENES + "table_with_chairs.tscn", Vector2i(5, 4), 1).floor())
	# Arcade and casino toys.
	out.append(SpawnableSpec.new("arcade_cabinet", SCENES + "arcade_cabinet.tscn", Vector2i(2, 3), 1).floor().per_level(3))
	out.append(SpawnableSpec.new("slot_machine", SCENES + "slot_machine.tscn", Vector2i(2, 3), 2).floor().per_level(2))
	out.append(SpawnableSpec.new("bumper", SCENES + "bumper.tscn", Vector2i(2, 2), 3).floor().per_level(3).level_bound())
	out.append(SpawnableSpec.new("air_fan", SCENES + "air_fan.tscn", Vector2i(2, 2), 4).floor().per_level(2).level_bound())
	# Shield items.
	out.append(SpawnableSpec.new("shield_battery", SCENES + "shield_battery.tscn", Vector2i(2, 3), 10).floor())
	out.append(SpawnableSpec.new("shield_core", SCENES + "shield_core.tscn", Vector2i(2, 3), 2).floor())
	out.append(SpawnableSpec.new("magnet", SCENES + "magnet.tscn", Vector2i(2, 3), 4).floor())
	out.append(SpawnableSpec.new("crate", SCENES + "crate.tscn", Vector2i(2, 3), 1).floor())
	out.append(SpawnableSpec.new("doubler", SCENES + "doubler.tscn", Vector2i(2, 3), 3).floor())
	return out


static func _place_trampoline(node: Node3D, where: int, rect: Rect2i) -> void:
	match where:
		W.LEFT_WALL:
			node.rotation.z = -PI / 2.0
			node.position = Vector3(rect.position.x, -(rect.position.y + rect.size.y * 0.5), 0.0)
		W.RIGHT_WALL:
			node.rotation.z = PI / 2.0
			node.position = Vector3(rect.end.x, -(rect.position.y + rect.size.y * 0.5), 0.0)


static func _place_wallgun(node: Node3D, where: int, rect: Rect2i) -> void:
	match where:
		W.LEFT_WALL:
			node.position = Vector3(rect.position.x, -(rect.position.y + rect.size.y * 0.5), 0.0)
		W.RIGHT_WALL:
			node.position = Vector3(rect.end.x, -(rect.position.y + rect.size.y * 0.5), 0.0)
			node.set("mirrored", true)
		W.ROOF:
			node.rotation.z = -PI / 2.0
			node.position = Vector3(rect.position.x + rect.size.x * 0.5, -rect.position.y, 0.0)


static func _place_drone(node: Node3D, _where: int, rect: Rect2i) -> void:
	node.position = Vector3(randf_range(2.0, 12.5), -(rect.position.y + 0.7), 0.0)


static func _place_light_ring(node: Node3D, _where: int, rect: Rect2i) -> void:
	# The ring fires its laser across the room: point it at the far wall.
	if node.position.x < Grid.CENTER_X:
		node.set("flipped", true)


static func _build_themes() -> Array[Dictionary]:
	return [
		{
			"id": "gym", "windows": [Rect2(0.2, 7.6, 1.6, 1.3), Rect2(13.2, 7.6, 1.6, 1.3), Rect2(4.2, 4.6, 6.6, 2.2)], "height": 16,
			"spawnables": ["trampoline", "wallgun", "roped_bomb", "treadmill", "bench_press", "button"],
			"wall": Color(0.13, 0.26, 0.29), "trim": Color(0.2, 1.0, 0.75), "floor": Color(0.21, 0.42, 0.42),
		},
		{
			"id": "rich1", "windows": [Rect2(1.7, 2.0, 4.6, 2.6), Rect2(1.5, 7.7, 2.2, 1.2), Rect2(11.3, 7.7, 2.2, 1.2)], "height": 16,
			"spawnables": ["table_with_chairs", "button", "statue", "light_ring", "drone", "floor_painting", "roped_painting", "desktop", "bed_rich", "bathtub", "wallgun", "cake", "tv", "champagne"],
			"wall": Color(0.31, 0.21, 0.13), "trim": Color(1.0, 0.75, 0.2), "floor": Color(0.47, 0.31, 0.16),
		},
		{
			"id": "rich2", "windows": [Rect2(0.4, 5.2, 2.6, 1.6), Rect2(12.2, 5.2, 2.6, 1.6), Rect2(3.6, 5.2, 7.8, 1.5)], "height": 15,
			"spawnables": ["table_with_chairs", "button", "statue", "light_ring", "drone", "floor_painting", "roped_painting", "desktop", "bed_rich", "bathtub", "wallgun", "cake", "tv", "champagne"],
			"wall": Color(0.16, 0.21, 0.36), "trim": Color(0.3, 0.8, 1.0), "floor": Color(0.26, 0.26, 0.47),
		},
		{
			"id": "hacker", "windows": [Rect2(10.6, 4.2, 3.6, 2.0), Rect2(0.3, 4.4, 3.0, 1.6)], "height": 16,
			"spawnables": ["chair", "button", "wallgun", "roped_bomb", "drone", "trampoline", "desktop"],
			"wall": Color(0.08, 0.16, 0.13), "trim": Color(0.2, 1.0, 0.4), "floor": Color(0.13, 0.23, 0.21),
		},
		{
			"id": "tiktoker", "windows": [Rect2(5.0, 4.0, 4.0, 2.2), Rect2(9.6, 4.6, 2.2, 1.6)], "height": 16,
			"spawnables": ["chair", "wallgun", "roped_painting", "drone", "bathtub", "light_ring", "desktop", "treadmill", "bed2"],
			"wall": Color(0.36, 0.10, 0.31), "trim": Color(1.0, 0.3, 0.7), "floor": Color(0.52, 0.16, 0.42),
		},
		{
			"id": "room1", "windows": [Rect2(0.9, 2.1, 3.4, 2.6), Rect2(1.1, 7.4, 3.0, 1.5), Rect2(8.9, 7.4, 3.0, 1.5)], "height": 16,
			"spawnables": ["chair", "table_with_chairs", "roped_bomb_two_ways", "drone", "toilet", "treadmill", "desktop", "bed1", "cake", "champagne"],
			"wall": Color(0.26, 0.16, 0.47), "trim": Color(0.75, 0.4, 1.0), "floor": Color(0.36, 0.23, 0.57),
		},
		{
			"id": "room2", "windows": [Rect2(3.0, 4.7, 4.0, 1.9), Rect2(1.1, 7.6, 2.6, 1.1), Rect2(6.2, 7.6, 2.6, 1.1), Rect2(11.3, 7.6, 2.6, 1.1)], "height": 16,
			"spawnables": ["chair", "table_with_chairs", "roped_bomb_two_ways", "drone", "toilet", "desktop", "wallgun", "tv"],
			"wall": Color(0.13, 0.18, 0.42), "trim": Color(0.4, 0.55, 1.0), "floor": Color(0.21, 0.26, 0.52),
		},
		{
			"id": "arcade", "windows": [Rect2(0.5, 5.6, 3.2, 1.6), Rect2(10.3, 5.6, 3.8, 1.6), Rect2(4.6, 6.0, 5.4, 1.3)], "height": 16,
			"spawnables": ["arcade_cabinet", "bumper", "air_fan", "chair", "drone", "roped_bomb", "button", "trampoline", "champagne", "tv"],
			"wall": Color(0.16, 0.08, 0.34), "trim": Color(1.0, 0.35, 0.8), "floor": Color(0.14, 0.06, 0.28),
		},
		{
			"id": "casino", "windows": [Rect2(5.6, 5.85, 4.4, 1.05), Rect2(11.0, 6.0, 3.0, 0.9)], "height": 15,
			"spawnables": ["slot_machine", "table_with_chairs", "champagne", "cake", "statue", "light_ring", "drone", "wallgun", "bumper", "roped_painting", "button"],
			"wall": Color(0.42, 0.08, 0.16), "trim": Color(1.0, 0.8, 0.3), "floor": Color(0.5, 0.07, 0.1),
		},
		{
			"id": "toilet1", "windows": [Rect2(7.0, 3.2, 3.6, 1.6), Rect2(2.0, 7.9, 2.0, 1.0), Rect2(6.5, 7.9, 2.0, 1.0), Rect2(11.0, 7.9, 2.0, 1.0)], "height": 16,
			"spawnables": ["bathtub", "toilet", "roped_bomb_two_ways", "drone", "trampoline", "tv", "fire_zone"],
			"wall": Color(0.26, 0.34, 0.39), "trim": Color(0.6, 0.95, 1.0), "floor": Color(0.36, 0.47, 0.52),
		},
	]
