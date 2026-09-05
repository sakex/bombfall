class_name City
extends Node3D
## The synthwave megacity behind the hotel: a dusk sky with a banded sun,
## a scrolling neon grid for a ground, contoured mountains and palm
## silhouettes on the horizon, neon-edged towers with lit facades, spires,
## beacons, flying cars, adverts and layers of magenta haze. It all sits far
## behind the play plane so perspective gives real parallax as the camera
## descends; the sky, ground and horizon follow the camera, while towers
## are world-fixed and recycled below the view, rising out of the grid.

const TOWER_COUNT := 120
const CROWN_COUNT := 40
const CAR_COUNT := 70
const BILLBOARD_COUNT := 8
const MOUNTAIN_COUNT := 13
const PALM_COUNT := 10
const Z_NEAR := -45.0
const Z_FAR := -150.0
const X_MIN := -110.0
const X_MAX := 130.0
const GROUND_DROP := 42.0       ## the grid sits this far below the camera
const AVENUE_SLOPE := 0.2      ## half-width of the open avenue grows with depth
const SKY_Z := -460.0
const SUN_Z := -430.0
const HORIZON_Z := -330.0

class Tower:
	var index: int
	var x: float
	var z: float
	var width: float
	var depth: float
	var height: float
	var top: float
	var beacon := -1
	var crown := -1
	var crown_size := Vector3.ZERO
	var spire := -1
	var spire_height := 0.0
	var edges: PackedInt32Array

class Car:
	var lane_y: float
	var z: float
	var x: float
	var speed: float
	var length: float

var _towers: Array[Tower] = []
var _cars: Array[Car] = []
var _tower_mm: MultiMesh
var _edge_mm: MultiMesh
var _beacon_mm: MultiMesh
var _car_mm: MultiMesh
var _billboards: Array[MeshInstance3D] = []
var _billboard_tower: Array[int] = []
var _follow: Array[Node3D] = []          # nodes that track the camera (sky, sun, grid, horizon)
var _camera: Camera3D
var _rng := RandomNumberGenerator.new()
var _edge_count := 0


func _ready() -> void:
	_rng.seed = 1337
	_build_sky()
	_build_sun()
	_build_grid()
	_build_mountains()
	_build_palms()
	_build_haze()
	_build_towers()
	_build_edges()
	_build_beacons()
	_build_cars()
	_build_billboards()
	_build_moon()
	_build_airship()
	_build_searchlights()
	_build_skybridges()


func _camera_pos() -> Vector3:
	if _camera == null or not is_instance_valid(_camera):
		_camera = get_viewport().get_camera_3d()
	return _camera.global_position if _camera != null else Vector3(Grid.CENTER_X, 0.0, 30.0)


static func _shader_material(path: String, params: Dictionary = {}) -> ShaderMaterial:
	var m := ShaderMaterial.new()
	m.shader = load(path)
	for key in params:
		m.set_shader_parameter(key, params[key])
	return m


func _quad(size: Vector2, material: Material, offset: Vector3) -> MeshInstance3D:
	var mi := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = size
	mi.mesh = quad
	mi.material_override = material
	mi.set_meta("offset", offset)
	add_child(mi)
	_follow.append(mi)
	return mi


# ------------------------------------------------------------------ build --
func _build_sky() -> void:
	_quad(Vector2(760.0, 1100.0), _shader_material("res://assets/shaders/sky.gdshader"), Vector3(0.0, -120.0, SKY_Z))


func _build_sun() -> void:
	_quad(Vector2(260.0, 260.0), _shader_material("res://assets/shaders/sun.gdshader"), Vector3(30.0, -40.0, SUN_Z))


func _build_grid() -> void:
	var mi := MeshInstance3D.new()
	var plane := PlaneMesh.new()
	plane.size = Vector2(1400.0, 420.0)
	plane.subdivide_depth = 8
	mi.mesh = plane
	mi.material_override = _shader_material("res://assets/shaders/grid.gdshader")
	mi.set_meta("offset", Vector3(0.0, -GROUND_DROP, -240.0))
	add_child(mi)
	_follow.append(mi)


func _build_mountains() -> void:
	var mm := MultiMesh.new()
	mm.transform_format = MultiMesh.TRANSFORM_3D
	mm.use_custom_data = true
	var cone := CylinderMesh.new()
	cone.top_radius = 0.0
	cone.bottom_radius = 1.0
	cone.height = 1.0
	cone.radial_segments = 7
	cone.rings = 1
	cone.material = _shader_material("res://assets/shaders/mountain.gdshader")
	mm.mesh = cone
	mm.instance_count = MOUNTAIN_COUNT
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = mm
	mmi.name = "Mountains"
	mmi.set_meta("offset", Vector3(0.0, -GROUND_DROP, 0.0))
	add_child(mmi)
	_follow.append(mmi)
	for i in MOUNTAIN_COUNT:
		var x := lerpf(-460.0, 500.0, float(i) / (MOUNTAIN_COUNT - 1)) + _rng.randf_range(-25.0, 25.0)
		var z := HORIZON_Z + _rng.randf_range(-40.0, 30.0)
		var h := _rng.randf_range(28.0, 75.0) * (0.55 if absf(x - 30.0) < 90.0 else 1.0)
		var r := _rng.randf_range(45.0, 95.0)
		var t := Transform3D(Basis().scaled(Vector3(r, h, r * 0.8)).rotated(Vector3.UP, _rng.randf() * TAU), Vector3(x, h * 0.5, z))
		mm.set_instance_transform(i, t)
		mm.set_instance_custom_data(i, Color(x, 0.0, z, h))


func _build_palms() -> void:
	var material := _shader_material("res://assets/shaders/silhouette.gdshader")
	var trunks := MultiMesh.new()
	trunks.transform_format = MultiMesh.TRANSFORM_3D
	var trunk := CylinderMesh.new()
	trunk.top_radius = 0.5
	trunk.bottom_radius = 1.0
	trunk.height = 1.0
	trunk.radial_segments = 6
	trunk.material = material
	trunks.mesh = trunk
	trunks.instance_count = PALM_COUNT
	var leaves := MultiMesh.new()
	leaves.transform_format = MultiMesh.TRANSFORM_3D
	var leaf := SphereMesh.new()
	leaf.radius = 1.0
	leaf.height = 2.0
	leaf.radial_segments = 8
	leaf.rings = 4
	leaf.material = material
	leaves.mesh = leaf
	leaves.instance_count = PALM_COUNT * 7
	for i in PALM_COUNT:
		var x := lerpf(-200.0, 240.0, float(i) / (PALM_COUNT - 1)) + _rng.randf_range(-15.0, 15.0)
		var z := _rng.randf_range(-250.0, -300.0)
		var h := _rng.randf_range(24.0, 40.0)
		var lean := _rng.randf_range(-0.15, 0.15)
		var tb := Basis().rotated(Vector3.FORWARD, lean).scaled(Vector3(1.2, h, 1.2))
		trunks.set_instance_transform(i, Transform3D(tb, Vector3(x, h * 0.5, z)))
		var top := Vector3(x - sin(lean) * h * 0.5, h * 0.95, z)
		for k in 7:
			var a := float(k) / 7.0 * TAU + _rng.randf_range(-0.3, 0.3)
			var droop := _rng.randf_range(0.35, 0.7)
			var length := _rng.randf_range(7.0, 11.0)
			var dir := Vector3(cos(a), -droop, sin(a) * 0.4).normalized()
			var basis := Basis().looking_at(dir, Vector3.UP).scaled(Vector3(1.6, 1.0, length * 0.5))
			var lb := Basis(basis.x, basis.y, basis.z)
			leaves.set_instance_transform(i * 7 + k, Transform3D(lb, top + dir * length * 0.45))
	for mm in [trunks, leaves]:
		var mmi := MultiMeshInstance3D.new()
		mmi.multimesh = mm
		mmi.set_meta("offset", Vector3(0.0, -GROUND_DROP, 0.0))
		add_child(mmi)
		_follow.append(mmi)


func _build_haze() -> void:
	for i in 3:
		var z: float = [-70.0, -140.0, -240.0][i]
		var strength: float = [0.10, 0.16, 0.22][i]
		var mat := _shader_material("res://assets/shaders/haze.gdshader", {"strength": strength})
		var w := 300.0 + absf(z) * 1.6
		_quad(Vector2(w, w * 0.9), mat, Vector3(0.0, -GROUND_DROP * 0.55, z))


func _build_towers() -> void:
	_tower_mm = MultiMesh.new()
	_tower_mm.transform_format = MultiMesh.TRANSFORM_3D
	_tower_mm.use_custom_data = true
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	box.material = _shader_material("res://assets/shaders/city_windows.gdshader")
	_tower_mm.mesh = box
	_tower_mm.instance_count = TOWER_COUNT + CROWN_COUNT
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _tower_mm
	mmi.name = "Towers"
	add_child(mmi)
	var start_y := _camera_pos().y
	var crown_slot := TOWER_COUNT
	for i in TOWER_COUNT:
		var t := Tower.new()
		t.index = i
		var depth_t := float(i) / TOWER_COUNT
		t.z = lerpf(Z_NEAR, Z_FAR, depth_t) + _rng.randf_range(-6.0, 6.0)
		# Towers line an open avenue that follows the view cone, so the sun,
		# grid and mountains stay visible between two walls of skyscrapers.
		var avenue := AVENUE_SLOPE * (30.0 - t.z) + 4.0
		var side := -1.0 if _rng.randf() < 0.5 else 1.0
		t.x = Grid.CENTER_X + side * _rng.randf_range(avenue, avenue + 90.0)
		t.width = _rng.randf_range(6.0, 18.0) * (1.0 + depth_t * 1.3)
		t.depth = _rng.randf_range(6.0, 16.0) * (1.0 + depth_t * 1.3)
		t.height = _rng.randf_range(150.0, 340.0)
		t.top = start_y + _rng.randf_range(-100.0, 70.0)
		if crown_slot < TOWER_COUNT + CROWN_COUNT and _rng.randf() < 0.4:
			t.crown = crown_slot
			t.crown_size = Vector3(t.width * _rng.randf_range(0.45, 0.7), _rng.randf_range(8.0, 22.0), t.depth * _rng.randf_range(0.45, 0.7))
			_tower_mm.set_instance_custom_data(t.crown, Color(_rng.randf(), 0.45, 0.0, 1.0))
			crown_slot += 1
		_tower_mm.set_instance_custom_data(i, Color(_rng.randf(), _rng.randf_range(0.35, 0.65), 0.0, 1.0))
		_towers.append(t)
	for t in _towers:
		_place_tower(t)


func _place_tower(t: Tower) -> void:
	var basis := Basis().scaled(Vector3(t.width, t.height, t.depth))
	_tower_mm.set_instance_transform(t.index, Transform3D(basis, Vector3(t.x, t.top - t.height * 0.5, t.z)))
	var custom := _tower_mm.get_instance_custom_data(t.index)
	_tower_mm.set_instance_custom_data(t.index, Color(custom.r, custom.g, t.top, t.height))
	var roof := t.top
	if t.crown >= 0:
		var cb := Basis().scaled(t.crown_size)
		_tower_mm.set_instance_transform(t.crown, Transform3D(cb, Vector3(t.x, t.top + t.crown_size.y * 0.5, t.z)))
		var cc := _tower_mm.get_instance_custom_data(t.crown)
		_tower_mm.set_instance_custom_data(t.crown, Color(cc.r, cc.g, t.top + t.crown_size.y, t.crown_size.y))
		roof = t.top + t.crown_size.y
	if t.beacon >= 0:
		var bb := Basis().scaled(Vector3(1.5, 3.5, 1.5))
		_beacon_mm.set_instance_transform(t.beacon, Transform3D(bb, Vector3(t.x, roof + t.spire_height + 1.7, t.z)))
	if _edge_mm != null:
		_place_edges(t)


func _build_edges() -> void:
	_edge_mm = MultiMesh.new()
	_edge_mm.transform_format = MultiMesh.TRANSFORM_3D
	_edge_mm.use_colors = true
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	box.material = _shader_material("res://assets/shaders/neon_edge.gdshader")
	_edge_mm.mesh = box
	# 4 vertical edges + 4 roof edges per tower, a spire for some.
	_edge_mm.instance_count = TOWER_COUNT * 9
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _edge_mm
	mmi.name = "Edges"
	add_child(mmi)
	var palette := [Color(1.0, 0.2, 0.7), Color(0.2, 0.9, 1.0), Color(0.7, 0.3, 1.0), Color(1.0, 0.5, 0.2)]
	for t in _towers:
		t.edges = PackedInt32Array()
		for k in 8:
			t.edges.append(_edge_count)
			_edge_mm.set_instance_color(_edge_count, palette[(t.index + (k / 4)) % palette.size()])
			_edge_count += 1
		if _rng.randf() < 0.45:
			t.spire = _edge_count
			t.spire_height = _rng.randf_range(10.0, 30.0)
			_edge_mm.set_instance_color(_edge_count, palette[(t.index + 2) % palette.size()])
			_edge_count += 1
		_place_edges(t)


func _place_edges(t: Tower) -> void:
	var hw := t.width * 0.5
	var hd := t.depth * 0.5
	var mid := t.top - t.height * 0.5
	var thick := 0.35 + absf(t.z) * 0.006
	var corners := [Vector2(-hw, -hd), Vector2(hw, -hd), Vector2(hw, hd), Vector2(-hw, hd)]
	for k in 4:
		var c: Vector2 = corners[k]
		_edge_mm.set_instance_transform(t.edges[k], Transform3D(Basis().scaled(Vector3(thick, t.height, thick)), Vector3(t.x + c.x, mid, t.z + c.y)))
	# Roof rim.
	_edge_mm.set_instance_transform(t.edges[4], Transform3D(Basis().scaled(Vector3(t.width, thick, thick)), Vector3(t.x, t.top, t.z - hd)))
	_edge_mm.set_instance_transform(t.edges[5], Transform3D(Basis().scaled(Vector3(t.width, thick, thick)), Vector3(t.x, t.top, t.z + hd)))
	_edge_mm.set_instance_transform(t.edges[6], Transform3D(Basis().scaled(Vector3(thick, thick, t.depth)), Vector3(t.x - hw, t.top, t.z)))
	_edge_mm.set_instance_transform(t.edges[7], Transform3D(Basis().scaled(Vector3(thick, thick, t.depth)), Vector3(t.x + hw, t.top, t.z)))
	if t.spire >= 0:
		var roof := t.top + (t.crown_size.y if t.crown >= 0 else 0.0)
		_edge_mm.set_instance_transform(t.spire, Transform3D(Basis().scaled(Vector3(thick, t.spire_height, thick)), Vector3(t.x, roof + t.spire_height * 0.5, t.z)))


func _build_beacons() -> void:
	_beacon_mm = MultiMesh.new()
	_beacon_mm.transform_format = MultiMesh.TRANSFORM_3D
	_beacon_mm.use_custom_data = true
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	box.material = _shader_material("res://assets/shaders/beacon.gdshader")
	_beacon_mm.mesh = box
	_beacon_mm.instance_count = TOWER_COUNT / 2
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _beacon_mm
	mmi.name = "Beacons"
	add_child(mmi)
	var slot := 0
	for t in _towers:
		if slot >= _beacon_mm.instance_count:
			break
		if _rng.randf() < 0.55:
			t.beacon = slot
			_beacon_mm.set_instance_custom_data(slot, Color(_rng.randf(), 0, 0, 0))
			_place_tower(t)
			slot += 1


func _build_cars() -> void:
	_car_mm = MultiMesh.new()
	_car_mm.transform_format = MultiMesh.TRANSFORM_3D
	_car_mm.use_custom_data = true
	var quad := QuadMesh.new()
	quad.size = Vector2(1.0, 1.0)
	quad.material = _shader_material("res://assets/shaders/car_light.gdshader")
	_car_mm.mesh = quad
	_car_mm.instance_count = CAR_COUNT
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _car_mm
	mmi.name = "Cars"
	add_child(mmi)
	var palette := [Color(1.0, 0.3, 0.3), Color(1.0, 0.9, 0.6), Color(0.3, 0.9, 1.0), Color(1.0, 0.4, 0.9)]
	for i in CAR_COUNT:
		var c := Car.new()
		c.lane_y = _rng.randf_range(-45.0, 45.0)
		c.z = _rng.randf_range(Z_NEAR + 4.0, Z_FAR + 10.0)
		c.x = _rng.randf_range(X_MIN, X_MAX)
		c.speed = _rng.randf_range(10.0, 30.0) * (1.0 if _rng.randf() < 0.5 else -1.0)
		c.length = _rng.randf_range(3.0, 7.0) * (0.6 + absf(c.z) / 120.0)
		_cars.append(c)
		var color: Color = palette[i % palette.size()] if c.speed > 0 else Color(1.0, 0.25, 0.2)
		_car_mm.set_instance_custom_data(i, color)


func _build_billboards() -> void:
	var candidates := _towers.filter(func(t): return t.z > -100.0)
	for i in BILLBOARD_COUNT:
		if candidates.is_empty():
			break
		var t: Tower = candidates[_rng.randi() % candidates.size()]
		var mi := MeshInstance3D.new()
		var quad := QuadMesh.new()
		quad.size = Vector2(t.width * 0.8, _rng.randf_range(8.0, 16.0))
		mi.mesh = quad
		var hue := _rng.randf()
		mi.material_override = _shader_material("res://assets/shaders/billboard.gdshader", {
			"color_a": Color.from_hsv(hue, 0.9, 1.0),
			"color_b": Color.from_hsv(fmod(hue + 0.4, 1.0), 0.9, 1.0),
			"speed": _rng.randf_range(0.2, 0.6),
		})
		add_child(mi)
		_billboards.append(mi)
		_billboard_tower.append(t.index)
	_place_billboards()


func _place_billboards() -> void:
	for i in _billboards.size():
		var t := _towers[_billboard_tower[i]]
		var mi := _billboards[i]
		var offset := (float(i) * 37.0)
		mi.position = Vector3(t.x, t.top - 25.0 - fmod(offset, 60.0), t.z + t.depth * 0.5 + 0.4)


func _build_moon() -> void:
	_quad(Vector2(120.0, 120.0), _shader_material("res://assets/shaders/moon.gdshader"), Vector3(-150.0, 120.0, SUN_Z + 5.0))


var _airship: Node3D
var _airship_x := 0.0


func _build_airship() -> void:
	# A blimp with an advert on its flank, drifting across the sky.
	_airship = Node3D.new()
	add_child(_airship)
	var hull := MeshInstance3D.new()
	var sph := SphereMesh.new()
	sph.radius = 1.0
	sph.height = 2.0
	sph.radial_segments = 16
	sph.rings = 8
	hull.mesh = sph
	hull.scale = Vector3(28.0, 9.0, 9.0)
	var hm := StandardMaterial3D.new()
	hm.albedo_color = Color(0.12, 0.05, 0.16)
	hm.roughness = 0.6
	hull.material_override = hm
	_airship.add_child(hull)
	var gondola := MeshInstance3D.new()
	var gb := BoxMesh.new()
	gb.size = Vector3(9.0, 3.0, 3.5)
	gondola.mesh = gb
	gondola.position = Vector3(0.0, -8.5, 0.0)
	gondola.material_override = hm
	_airship.add_child(gondola)
	var ad := MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(22.0, 7.0)
	ad.mesh = quad
	ad.position = Vector3(0.0, 0.0, 9.3)
	ad.material_override = _shader_material("res://assets/shaders/billboard.gdshader", {"color_a": Color(1.0, 0.3, 0.6), "color_b": Color(0.3, 0.9, 1.0), "speed": 0.25, "bands": 4.0})
	_airship.add_child(ad)
	for x in [-11.0, 11.0]:
		var fin := MeshInstance3D.new()
		var fb := BoxMesh.new()
		fb.size = Vector3(6.0, 7.0, 0.6)
		fin.mesh = fb
		fin.position = Vector3(-24.0, 0.0, 0.0)
		fin.rotation.x = deg_to_rad(x * 8.0)
		fin.material_override = hm
		_airship.add_child(fin)
	var light := MeshInstance3D.new()
	var lb := BoxMesh.new()
	lb.size = Vector3(1.5, 1.5, 1.5)
	light.mesh = lb
	light.position = Vector3(28.5, 0.0, 0.0)
	var lm := StandardMaterial3D.new()
	lm.emission_enabled = true
	lm.emission = Color(1.0, 0.2, 0.2)
	lm.emission_energy_multiplier = 5.0
	light.material_override = lm
	_airship.add_child(light)
	_airship_x = -140.0


var _searchlights: Array[Node3D] = []


func _build_searchlights() -> void:
	for i in 3:
		var t := _towers[(i * 37 + 11) % _towers.size()]
		var pivot := Node3D.new()
		add_child(pivot)
		var beam := MeshInstance3D.new()
		var quad := QuadMesh.new()
		quad.size = Vector2(14.0, 160.0)
		beam.mesh = quad
		beam.position = Vector3(0.0, 80.0, 0.0)
		beam.material_override = _shader_material("res://assets/shaders/searchlight.gdshader", {"color": [Color(1.0, 0.5, 0.9), Color(0.5, 0.9, 1.0), Color(1.0, 0.8, 0.5)][i]})
		pivot.add_child(beam)
		pivot.set_meta("tower", t.index)
		pivot.set_meta("phase", float(i) * 2.1)
		_searchlights.append(pivot)


var _bridge_mm: MultiMesh
var _bridges: Array = []


func _build_skybridges() -> void:
	_bridge_mm = MultiMesh.new()
	_bridge_mm.transform_format = MultiMesh.TRANSFORM_3D
	_bridge_mm.use_colors = true
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	box.material = _shader_material("res://assets/shaders/neon_edge.gdshader", {"intensity": 1.6})
	_bridge_mm.mesh = box
	# Pair up towers that stand close together at a similar depth.
	for i in _towers.size():
		for j in range(i + 1, _towers.size()):
			var a := _towers[i]
			var b := _towers[j]
			if absf(a.z - b.z) < 12.0 and absf(a.x - b.x) > (a.width + b.width) * 0.5 + 4.0 and absf(a.x - b.x) < 45.0:
				_bridges.append([i, j, _rng.randf_range(20.0, 90.0)])
				break
		if _bridges.size() >= 16:
			break
	_bridge_mm.instance_count = _bridges.size()
	for k in _bridges.size():
		_bridge_mm.set_instance_color(k, [Color(0.4, 0.9, 1.0), Color(1.0, 0.4, 0.8)][k % 2])
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _bridge_mm
	mmi.name = "Skybridges"
	add_child(mmi)
	_place_bridges()


func _place_bridges() -> void:
	for k in _bridges.size():
		var a := _towers[_bridges[k][0]]
		var b := _towers[_bridges[k][1]]
		var drop: float = _bridges[k][2]
		var y := minf(a.top, b.top) - drop
		var mid := Vector3((a.x + b.x) * 0.5, y, (a.z + b.z) * 0.5)
		var length := absf(a.x - b.x)
		_bridge_mm.set_instance_transform(k, Transform3D(Basis().scaled(Vector3(length, 1.2, 3.0)), mid))


# ----------------------------------------------------------------- update --
func _process(delta: float) -> void:
	var cam := _camera_pos()
	_airship_x += delta * 4.0
	if _airship_x > 220.0:
		_airship_x = -160.0
	if _airship != null:
		_airship.position = Vector3(cam.x + _airship_x, cam.y + 55.0, -190.0)
	var now := Time.get_ticks_msec() / 1000.0
	for pivot in _searchlights:
		var tower := _towers[pivot.get_meta("tower")]
		pivot.position = Vector3(tower.x, tower.top + (tower.crown_size.y if tower.crown >= 0 else 0.0), tower.z)
		pivot.rotation = Vector3(0.0, 0.0, sin(now * 0.35 + pivot.get_meta("phase")) * 0.5)
	_place_bridges()
	var anchor := Vector3(cam.x, cam.y, 0.0)
	for node in _follow:
		node.position = anchor + node.get_meta("offset")
	# Recycle towers that scrolled out above the view: they re-emerge from the grid.
	for t in _towers:
		var view_half := 70.0 * (1.0 + absf(t.z) / 80.0)
		if t.top - t.height > cam.y + view_half:
			t.top = cam.y - GROUND_DROP - _rng.randf_range(2.0, 50.0)
			_place_tower(t)
	_place_billboards()
	for i in _cars.size():
		var c := _cars[i]
		c.x += c.speed * delta
		if c.x > X_MAX + 10.0:
			c.x = X_MIN - 10.0
		elif c.x < X_MIN - 10.0:
			c.x = X_MAX + 10.0
		var basis := Basis().scaled(Vector3(c.length, 0.9, 1.0))
		_car_mm.set_instance_transform(i, Transform3D(basis, Vector3(c.x, cam.y + c.lane_y, c.z)))
