class_name Treadmill
extends PlanarBody
## A running treadmill: its belt drags whatever stands on it sideways.

const PUSH := 4.7              ## 300 px/s per tick
const CHECK_EVERY := 1.0 / 30.0
const BELT_SHADER := preload("res://assets/shaders/haz_belt.gdshader")

static var _belt_material: ShaderMaterial

var _direction := -1.0
var _since_check := 0.0
var _rollers: Array[Node3D] = []

@onready var model: Node3D = $Model
@onready var moving_area: Area3D = $MovingArea


func _ready() -> void:
	add_to_group("props")
	for i in 2:
		var r := model.find_child("roller_%d" % (i + 1), true, false)
		if r != null:
			_rollers.append(r)
	if randi() % 2 == 0:
		_direction = 1.0
		model.scale.x = -1.0
		moving_area.position.x = -moving_area.position.x
	# The belt surface (material "haz_belt") scrolls its ribs with the rollers.
	if _belt_material == null:
		_belt_material = ShaderMaterial.new()
		_belt_material.shader = BELT_SHADER
	for mesh in ModelUtil.all_meshes(model):
		for i in mesh.mesh.get_surface_count():
			var source := mesh.mesh.surface_get_material(i)
			if source != null and source.resource_name.begins_with("haz_belt"):
				mesh.set_surface_override_material(i, _belt_material)


func _physics_process(delta: float) -> void:
	for r in _rollers:
		r.rotation.z += delta * 6.0 * _direction
	_since_check += delta
	if _since_check < CHECK_EVERY:
		return
	_since_check = 0.0
	var force := (global_transform.basis.x * PUSH * _direction)
	force.z = 0.0
	for body in moving_area.get_overlapping_bodies():
		if body == self:
			continue
		if body is RigidBody3D:
			body.apply_central_impulse(force)
		elif body is Player:
			body.lateral_force += force.x
			body.velocity.y += force.y
