class_name Backdrop
extends Node3D
## The room behind a storey's play plane: a themed back wall two metres
## deep with window openings onto the city, floor and ceiling slabs bridging
## the gap, neon trims, a coloured room light and the set dressing built in
## Blender:
##   assets/models/backdrop_<theme>.glb  anchored at floor level (<= 9.5 m tall)
##   assets/models/ceiling_<theme>.glb   hanging from the ceiling (<= 3 m)

const DECOR_Z := -1.05          ## front of the room, just behind the play plane
const WALL_Z := -3.0            ## the back wall's front face
const WALL_THICKNESS := 0.3
const FRAME := 0.12
static var _materials: Dictionary = {}


static func build(theme: Dictionary, roof: int, height: int) -> Backdrop:
	var b := Backdrop.new()
	b.name = "Backdrop_%s_%d" % [theme["id"], roof]
	var w := float(Grid.WIDTH - 1)
	var h := float(height - 1)
	var cx := 1.0 + w * 0.5
	var top := -(roof + 1.0)
	var bottom := top - h
	var mid := top - h * 0.5
	var depth := DECOR_Z - WALL_Z
	var zmid := (DECOR_Z + WALL_Z) * 0.5
	var wall_material := _surface(theme["wall"], "wall")
	# Back wall, with the theme's windows cut out (room coords: x from the
	# left wall, y from the floor).
	var windows: Array = []
	for rect in theme.get("windows", []):
		var r: Rect2 = rect
		if r.position.y + r.size.y <= h - 0.3:
			windows.append(r)
	for piece in _wall_pieces(w, h, windows):
		b._box(Vector3(piece.size.x, piece.size.y, WALL_THICKNESS),
			Vector3(1.0 + piece.position.x + piece.size.x * 0.5, bottom + piece.position.y + piece.size.y * 0.5, WALL_Z - WALL_THICKNESS * 0.5), wall_material)
	for r in windows:
		b._window(r, bottom, theme)
	# Floor and ceiling slabs behind the play plane.
	b._box(Vector3(w, 0.3, depth), Vector3(cx, bottom - 0.15, zmid), _surface(theme["floor"], "floor"))
	b._box(Vector3(w, 0.3, depth), Vector3(cx, top + 0.15, zmid), _surface(theme["wall"].darkened(0.3), "ceiling"))
	# Side returns so the room reads as a box when seen at an angle.
	b._box(Vector3(0.3, h, depth), Vector3(1.0 - 0.15, mid, zmid), _surface(theme["wall"].darkened(0.2), "wall"))
	b._box(Vector3(0.3, h, depth), Vector3(16.0 + 0.15, mid, zmid), _surface(theme["wall"].darkened(0.2), "wall"))
	# Neon trims where the wall meets floor and ceiling.
	var trim := _glow(theme["trim"], 2.5)
	b._box(Vector3(w, 0.06, 0.06), Vector3(cx, top - 0.05, WALL_Z + 0.03), trim)
	b._box(Vector3(w, 0.06, 0.06), Vector3(cx, bottom + 0.05, WALL_Z + 0.03), trim)
	# A coloured room light so the set dressing is not lost in the dark.
	var light := OmniLight3D.new()
	light.light_color = theme["trim"].lerp(Color.WHITE, 0.5)
	light.light_energy = 1.4
	light.omni_range = maxf(h, w) * 0.9
	light.omni_attenuation = 1.2
	light.position = Vector3(cx, mid + h * 0.15, DECOR_Z + 0.5)
	b.add_child(light)
	# Set dressing (skipped with --nodecor, a debugging aid).
	if not OS.get_cmdline_user_args().has("--nodecor"):
		b._decor("res://assets/models/backdrop_%s.glb" % theme["id"], Vector3(1.0, bottom, DECOR_Z))
		b._decor("res://assets/models/ceiling_%s.glb" % theme["id"], Vector3(1.0, top, DECOR_Z))
	return b


## Splits a w x h wall into rectangles that avoid the window openings:
## horizontal bands between window edges, each band cut around the windows
## crossing it.
static func _wall_pieces(w: float, h: float, windows: Array) -> Array[Rect2]:
	var edges: Array[float] = [0.0, h]
	for r in windows:
		edges.append(r.position.y)
		edges.append(r.position.y + r.size.y)
	edges.sort()
	var pieces: Array[Rect2] = []
	for i in range(edges.size() - 1):
		var y0: float = edges[i]
		var y1: float = edges[i + 1]
		if y1 - y0 < 0.001:
			continue
		var ymid := (y0 + y1) * 0.5
		var cuts: Array[float] = [0.0, w]
		var crossing: Array = windows.filter(func(r): return r.position.y < ymid and r.position.y + r.size.y > ymid)
		crossing.sort_custom(func(a, b): return a.position.x < b.position.x)
		var x := 0.0
		for r in crossing:
			if r.position.x > x:
				pieces.append(Rect2(x, y0, r.position.x - x, y1 - y0))
			x = maxf(x, r.position.x + r.size.x)
		if x < w:
			pieces.append(Rect2(x, y0, w - x, y1 - y0))
	return pieces


func _window(r: Rect2, bottom: float, theme: Dictionary) -> void:
	var x0 := 1.0 + r.position.x
	var y0 := bottom + r.position.y
	var cx := x0 + r.size.x * 0.5
	var cy := y0 + r.size.y * 0.5
	var frame := _surface(theme["wall"].darkened(0.55).lerp(Color(0.5, 0.55, 0.6), 0.5), "metal")
	# Frame around the opening, sitting proud of the wall.
	_box(Vector3(r.size.x + FRAME * 2.0, FRAME, WALL_THICKNESS + 0.1), Vector3(cx, y0 - FRAME * 0.5, WALL_Z - WALL_THICKNESS * 0.5), frame)
	_box(Vector3(r.size.x + FRAME * 2.0, FRAME, WALL_THICKNESS + 0.1), Vector3(cx, y0 + r.size.y + FRAME * 0.5, WALL_Z - WALL_THICKNESS * 0.5), frame)
	_box(Vector3(FRAME, r.size.y, WALL_THICKNESS + 0.1), Vector3(x0 - FRAME * 0.5, cy, WALL_Z - WALL_THICKNESS * 0.5), frame)
	_box(Vector3(FRAME, r.size.y, WALL_THICKNESS + 0.1), Vector3(x0 + r.size.x + FRAME * 0.5, cy, WALL_Z - WALL_THICKNESS * 0.5), frame)
	# Mullions.
	var columns := maxi(int(r.size.x / 1.6), 1)
	for i in range(1, columns):
		_box(Vector3(0.06, r.size.y, 0.08), Vector3(x0 + r.size.x * i / columns, cy, WALL_Z - WALL_THICKNESS * 0.5), frame)
	if r.size.y > 1.4:
		_box(Vector3(r.size.x, 0.06, 0.08), Vector3(cx, y0 + r.size.y * 0.5, WALL_Z - WALL_THICKNESS * 0.5), frame)
	# Glass (skipped with --noglass, a debugging aid).
	if not OS.get_cmdline_user_args().has("--noglass"):
		_box(Vector3(r.size.x, r.size.y, 0.02), Vector3(cx, cy, WALL_Z - WALL_THICKNESS * 0.5), _glass())
	# A soft light spill from the city onto the sill.
	_box(Vector3(r.size.x, 0.05, 0.3), Vector3(cx, y0 + 0.03, WALL_Z + 0.15), _glow(Color(0.5, 0.8, 1.0), 0.6))


func _box(size: Vector3, at: Vector3, material: Material) -> void:
	var mi := MeshInstance3D.new()
	var mesh := BoxMesh.new()
	mesh.size = size
	mi.mesh = mesh
	mi.material_override = material
	mi.position = at
	add_child(mi)


var _spinners: Array[Node3D] = []
var _swayers: Array[Node3D] = []


func _decor(path: String, at: Vector3) -> void:
	if not ResourceLoader.exists(path):
		return
	var decor: Node3D = (load(path) as PackedScene).instantiate()
	decor.position = at
	add_child(decor)
	# Named pivots the Blender scripts left for us to animate.
	ModelUtil.animate_materials(decor)
	for node in decor.find_children("spin_*", "Node3D", true, false):
		_spinners.append(node)
	for node in decor.find_children("sway_*", "Node3D", true, false):
		_swayers.append(node)
	set_process(not _spinners.is_empty() or not _swayers.is_empty())


func _process(delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	for node in _spinners:
		node.rotation.y += delta * 2.5
	for node in _swayers:
		node.rotation.z = sin(t * 1.3 + node.position.x) * 0.12
		node.rotation.x = cos(t * 0.9 + node.position.x) * 0.06


## Physically based surfaces for the room shell, textured with small
## seamless noise maps generated once at load (no files to ship) and mapped
## in world space, so walls of any size get the same grain:
## wall = matte painted plaster, floor = polished stone that reflects the
## neon sky, ceiling = rough plaster, metal = brushed window frames.
static func _surface(color: Color, kind: String) -> StandardMaterial3D:
	var key := "s:%s:%s" % [kind, color.to_html()]
	if _materials.has(key):
		return _materials[key]
	var m := StandardMaterial3D.new()
	m.albedo_color = color
	m.uv1_triplanar = true
	m.uv1_world_triplanar = true
	m.uv1_triplanar_sharpness = 4.0
	match kind:
		"wall":
			m.albedo_texture = _noise_texture("wall_albedo")
			m.roughness = 0.82
			m.normal_enabled = true
			m.normal_texture = _noise_texture("wall_normal")
			m.normal_scale = 0.6
			m.uv1_scale = Vector3.ONE * 0.35
		"floor":
			m.albedo_texture = _noise_texture("floor_albedo")
			m.roughness = 0.2
			m.roughness_texture = _noise_texture("floor_rough")
			m.metallic_specular = 0.6
			m.normal_enabled = true
			m.normal_texture = _noise_texture("wall_normal")
			m.normal_scale = 0.25
			m.uv1_scale = Vector3.ONE * 0.5
		"ceiling":
			m.albedo_texture = _noise_texture("wall_albedo")
			m.roughness = 0.92
			m.uv1_scale = Vector3.ONE * 0.5
		"metal":
			m.metallic = 0.85
			m.roughness = 0.34
			m.roughness_texture = _noise_texture("brushed")
			m.albedo_texture = _noise_texture("brushed")
			m.uv1_scale = Vector3(0.3, 4.0, 0.3)
	_materials[key] = m
	return m


static func _noise_texture(kind: String) -> Texture2D:
	var key := "tex:" + kind
	if _materials.has(key):
		return _materials[key]
	var noise := FastNoiseLite.new()
	noise.noise_type = FastNoiseLite.TYPE_SIMPLEX_SMOOTH
	noise.fractal_octaves = 5
	var tex := NoiseTexture2D.new()
	tex.width = 256
	tex.height = 256
	tex.seamless = true
	tex.generate_mipmaps = true
	var ramp := Gradient.new()
	match kind:
		"wall_albedo":
			noise.frequency = 0.02
			ramp.set_color(0, Color(0.78, 0.78, 0.8))
			ramp.set_color(1, Color(1.05, 1.04, 1.06))
			tex.color_ramp = ramp
		"floor_albedo":
			noise.frequency = 0.012
			noise.fractal_octaves = 6
			ramp.set_color(0, Color(0.7, 0.7, 0.72))
			ramp.set_color(1, Color(1.1, 1.08, 1.1))
			tex.color_ramp = ramp
		"floor_rough":
			noise.frequency = 0.03
			ramp.set_color(0, Color(0.55, 0.55, 0.55))
			ramp.set_color(1, Color(1.4, 1.4, 1.4))
			tex.color_ramp = ramp
		"wall_normal":
			noise.frequency = 0.05
			tex.as_normal_map = true
			tex.bump_strength = 3.0
		"brushed":
			noise.frequency = 0.08
			ramp.set_color(0, Color(0.8, 0.8, 0.82))
			ramp.set_color(1, Color(1.1, 1.1, 1.12))
			tex.color_ramp = ramp
	tex.noise = noise
	_materials[key] = tex
	return tex


static func _plain(color: Color) -> StandardMaterial3D:
	var key := "p:" + color.to_html()
	if not _materials.has(key):
		var m := StandardMaterial3D.new()
		m.albedo_color = color
		m.roughness = 0.9
		_materials[key] = m
	return _materials[key]


static func _glow(color: Color, energy: float) -> StandardMaterial3D:
	var key := "g:%s:%.1f" % [color.to_html(), energy]
	if not _materials.has(key):
		var m := StandardMaterial3D.new()
		m.albedo_color = color.darkened(0.6)
		m.emission_enabled = true
		m.emission = color
		m.emission_energy_multiplier = energy
		_materials[key] = m
	return _materials[key]


static func _glass() -> StandardMaterial3D:
	if not _materials.has("glass"):
		var m := StandardMaterial3D.new()
		# Unshaded: a lit, glossy pane picks up a specular sheen that ignores
		# alpha and turns the whole window into a solid plate.
		m.transparency = BaseMaterial3D.TRANSPARENCY_ALPHA
		m.shading_mode = BaseMaterial3D.SHADING_MODE_UNSHADED
		m.albedo_color = Color(0.6, 0.8, 1.0, 0.07)
		_materials["glass"] = m
	return _materials["glass"]
