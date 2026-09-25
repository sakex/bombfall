class_name FireZone
extends PlanarBody
## A falling fireball dropped when bombs come too fast. Burns the first ten
## things it touches, then burns out.
##
## The model is a clump of burning wreckage: its flame meshes (materials
## "haz_flame_*") get the animated flame shader here, and the model is held
## upright so the fire keeps burning upwards however the body tumbles.

const MAX_KILLS := 10
const FLAME_SHADER := preload("res://assets/shaders/haz_flame.gdshader")

static var _flame_materials: Dictionary = {}

var _kills: Array[Node] = []

@onready var model: Node3D = $Model
@onready var burn_area: Area3D = $BurnArea
@onready var light: OmniLight3D = $Light


func _ready() -> void:
	add_to_group("props")
	burn_area.body_entered.connect(_on_body)
	burn_area.area_entered.connect(_on_body)
	for mesh in ModelUtil.all_meshes(model):
		for i in mesh.mesh.get_surface_count():
			var source := mesh.mesh.surface_get_material(i)
			if source != null and source.resource_name.begins_with("haz_flame"):
				mesh.set_surface_override_material(i, _flame_material(source))
				mesh.cast_shadow = GeometryInstance3D.SHADOW_CASTING_SETTING_OFF


static func _flame_material(source: Material) -> ShaderMaterial:
	if _flame_materials.has(source.resource_name):
		return _flame_materials[source.resource_name]
	var colour := Color(1.0, 0.35, 0.05)
	if source is StandardMaterial3D and (source as StandardMaterial3D).emission_enabled:
		colour = (source as StandardMaterial3D).emission
	var sm := ShaderMaterial.new()
	sm.shader = FLAME_SHADER
	sm.set_shader_parameter("color", colour)
	sm.set_shader_parameter("core", colour.lerp(Color(1.0, 0.95, 0.75), 0.6))
	sm.set_shader_parameter("energy", 2.4 if source.resource_name.ends_with("core") else 2.0)
	_flame_materials[source.resource_name] = sm
	return sm


func _process(_delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	var sway := Basis(Vector3.UP, sin(t * 3.0) * 0.4)
	model.global_basis = sway.scaled(Vector3(1.0 + 0.04 * sin(t * 13.0), 1.0 + 0.06 * sin(t * 9.0 + 1.0), 1.0))
	light.light_energy = 3.0 + 0.7 * sin(t * 17.0) + 0.45 * sin(t * 29.0 + 1.3)


func _on_body(body: Node) -> void:
	if body == self or not body.has_method("kill"):
		return
	body.call_deferred("kill")
	Sfx.play("fire")
	if not _kills.has(body):
		_kills.append(body)
		if _kills.size() >= MAX_KILLS:
			queue_free()
