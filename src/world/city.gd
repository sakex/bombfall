class_name City
extends Node3D
## The neon megacity seen through the hotel's windows: instanced towers with
## procedurally lit facades, blinking rooftop beacons, streams of flying
## cars, animated adverts and a starry sky. Everything sits far behind the
## play plane so perspective gives real parallax as the camera descends,
## and towers are recycled below the view so the city never ends.

const TOWER_COUNT := 140
const CAR_COUNT := 70
const BILLBOARD_COUNT := 10
const Z_NEAR := -30.0
const Z_FAR := -125.0
const X_MIN := -90.0
const X_MAX := 110.0
const SKY_Z := -170.0

class Tower:
	var index: int
	var x: float
	var z: float
	var width: float
	var depth: float
	var height: float
	var top: float
	var beacon := -1

class Car:
	var lane_y: float
	var z: float
	var x: float
	var speed: float
	var length: float

var _towers: Array[Tower] = []
var _cars: Array[Car] = []
var _tower_mm: MultiMesh
var _beacon_mm: MultiMesh
var _car_mm: MultiMesh
var _billboards: Array[MeshInstance3D] = []
var _billboard_tower: Array[int] = []
var _sky: MeshInstance3D
var _camera: Camera3D
var _rng := RandomNumberGenerator.new()


func _ready() -> void:
	_rng.seed = 1337
	_build_sky()
	_build_towers()
	_build_beacons()
	_build_cars()
	_build_billboards()


func _camera_y() -> float:
	if _camera == null or not is_instance_valid(_camera):
		_camera = get_viewport().get_camera_3d()
	return _camera.global_position.y if _camera != null else 0.0


func _camera_x() -> float:
	return _camera.global_position.x if _camera != null else Grid.CENTER_X


# ------------------------------------------------------------------ build --
func _build_sky() -> void:
	_sky = MeshInstance3D.new()
	var quad := QuadMesh.new()
	quad.size = Vector2(420.0, 640.0)
	_sky.mesh = quad
	var mat := ShaderMaterial.new()
	mat.shader = load("res://assets/shaders/sky.gdshader")
	_sky.material_override = mat
	_sky.position = Vector3(Grid.CENTER_X, 0.0, SKY_Z)
	add_child(_sky)


func _build_towers() -> void:
	_tower_mm = MultiMesh.new()
	_tower_mm.transform_format = MultiMesh.TRANSFORM_3D
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	_tower_mm.mesh = box
	_tower_mm.instance_count = TOWER_COUNT
	var mat := ShaderMaterial.new()
	mat.shader = load("res://assets/shaders/city_windows.gdshader")
	box.material = mat
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _tower_mm
	mmi.name = "Towers"
	add_child(mmi)
	var start_y := _camera_y()
	for i in TOWER_COUNT:
		var t := Tower.new()
		t.index = i
		var depth_t := float(i) / TOWER_COUNT
		t.z = lerpf(Z_NEAR, Z_FAR, depth_t) + _rng.randf_range(-6.0, 6.0)
		t.x = _rng.randf_range(X_MIN, X_MAX)
		# Avoid a tower straight behind the shaft at the nearest depth, it would hide the rest.
		if t.z > -45.0 and absf(t.x - Grid.CENTER_X) < 12.0:
			t.x += 24.0 * signf(t.x - Grid.CENTER_X + 0.01)
		t.width = _rng.randf_range(4.0, 14.0) * (1.0 + depth_t * 1.5)
		t.depth = _rng.randf_range(4.0, 12.0) * (1.0 + depth_t * 1.5)
		t.height = _rng.randf_range(140.0, 320.0)
		t.top = start_y + _rng.randf_range(-120.0, 80.0)
		_towers.append(t)
		_place_tower(t)


func _place_tower(t: Tower) -> void:
	var basis := Basis().scaled(Vector3(t.width, t.height, t.depth))
	_tower_mm.set_instance_transform(t.index, Transform3D(basis, Vector3(t.x, t.top - t.height * 0.5, t.z)))
	if t.beacon >= 0:
		var bb := Basis().scaled(Vector3(1.2, 3.0, 1.2))
		_beacon_mm.set_instance_transform(t.beacon, Transform3D(bb, Vector3(t.x, t.top + 1.5, t.z)))


func _build_beacons() -> void:
	_beacon_mm = MultiMesh.new()
	_beacon_mm.transform_format = MultiMesh.TRANSFORM_3D
	_beacon_mm.use_custom_data = true
	var box := BoxMesh.new()
	box.size = Vector3.ONE
	var mat := ShaderMaterial.new()
	mat.shader = load("res://assets/shaders/beacon.gdshader")
	box.material = mat
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
	var mat := ShaderMaterial.new()
	mat.shader = load("res://assets/shaders/car_light.gdshader")
	quad.material = mat
	_car_mm.mesh = quad
	_car_mm.instance_count = CAR_COUNT
	var mmi := MultiMeshInstance3D.new()
	mmi.multimesh = _car_mm
	mmi.name = "Cars"
	add_child(mmi)
	var palette := [Color(1.0, 0.3, 0.3), Color(1.0, 0.9, 0.6), Color(0.3, 0.9, 1.0), Color(1.0, 0.4, 0.9)]
	for i in CAR_COUNT:
		var c := Car.new()
		c.lane_y = _rng.randf_range(-45.0, 40.0)
		c.z = _rng.randf_range(Z_NEAR + 5.0, Z_FAR + 10.0)
		c.x = _rng.randf_range(X_MIN, X_MAX)
		c.speed = _rng.randf_range(8.0, 26.0) * (1.0 if _rng.randf() < 0.5 else -1.0)
		c.length = _rng.randf_range(5.0, 12.0)
		_cars.append(c)
		var color: Color = palette[i % palette.size()] if c.speed > 0 else Color(1.0, 0.25, 0.2)
		_car_mm.set_instance_custom_data(i, color)


func _build_billboards() -> void:
	var candidates := _towers.filter(func(t): return t.z > -80.0 and absf(t.x - Grid.CENTER_X) > 8.0)
	for i in BILLBOARD_COUNT:
		if candidates.is_empty():
			break
		var t: Tower = candidates[_rng.randi() % candidates.size()]
		var mi := MeshInstance3D.new()
		var quad := QuadMesh.new()
		quad.size = Vector2(t.width * 0.8, _rng.randf_range(8.0, 16.0))
		mi.mesh = quad
		var mat := ShaderMaterial.new()
		mat.shader = load("res://assets/shaders/billboard.gdshader")
		var hue := _rng.randf()
		mat.set_shader_parameter("color_a", Color.from_hsv(hue, 0.9, 1.0))
		mat.set_shader_parameter("color_b", Color.from_hsv(fmod(hue + 0.4, 1.0), 0.9, 1.0))
		mat.set_shader_parameter("speed", _rng.randf_range(0.2, 0.6))
		mi.material_override = mat
		add_child(mi)
		_billboards.append(mi)
		_billboard_tower.append(t.index)
	_place_billboards()


func _place_billboards() -> void:
	for i in _billboards.size():
		var t := _towers[_billboard_tower[i]]
		var mi := _billboards[i]
		var offset := (float(i) * 37.0)
		mi.position = Vector3(t.x, t.top - 25.0 - fmod(offset, 60.0), t.z + t.depth * 0.5 + 0.2)


# ----------------------------------------------------------------- update --
func _process(delta: float) -> void:
	var cy := _camera_y()
	_sky.position = Vector3(_camera_x(), cy, SKY_Z)
	# Recycle towers that scrolled out above the view.
	for t in _towers:
		var view_half := 70.0 * (1.0 + absf(t.z) / 80.0)
		if t.top - t.height > cy + view_half:
			t.top = cy - view_half - _rng.randf_range(0.0, 60.0)
			_place_tower(t)
	_place_billboards()
	# Cars follow the camera vertically and cruise sideways.
	for i in _cars.size():
		var c := _cars[i]
		c.x += c.speed * delta
		if c.x > X_MAX + 10.0:
			c.x = X_MIN - 10.0
		elif c.x < X_MIN - 10.0:
			c.x = X_MAX + 10.0
		var basis := Basis().scaled(Vector3(c.length, 1.1, 1.0))
		_car_mm.set_instance_transform(i, Transform3D(basis, Vector3(c.x, cy + c.lane_y, c.z)))
