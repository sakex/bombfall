class_name Coin
extends PlanarBody
## A coin worth [member value] points. Brighter coins are worth more.

const TIERS := 6
static var _tier_materials: Dictionary = {}

@export var value := 1
@export var unpickable := false

@onready var model: Node3D = $Model
@onready var pickup: Area3D = $Pickup
@onready var timer: Timer = $Timer


func _ready() -> void:
	add_to_group("coins")
	pickup.body_entered.connect(_on_body_entered)
	_apply_tint()
	if unpickable:
		timer.start()


func _process(delta: float) -> void:
	model.rotation.y += delta * 2.0


func set_value(v: int) -> void:
	value = v
	if is_node_ready():
		_apply_tint()


func _apply_tint() -> void:
	var tier := clampi(int(round(float(value) / 5.0 * (TIERS - 1))), 0, TIERS - 1)
	var meshes := ModelUtil.all_meshes(model)
	for mesh in meshes:
		var key := "%s:%d" % [mesh.mesh.get_rid(), tier]
		var materials: Array = _tier_materials.get(key, [])
		if materials.is_empty():
			var brightness := lerpf(0.35, 1.6, float(tier) / (TIERS - 1))
			for i in mesh.mesh.get_surface_count():
				var base := mesh.mesh.surface_get_material(i) as StandardMaterial3D
				var m := base.duplicate() as StandardMaterial3D
				m.albedo_color = Color(base.albedo_color.r * brightness, base.albedo_color.g * brightness, base.albedo_color.b * brightness)
				if m.emission_enabled:
					m.emission_energy_multiplier = base.emission_energy_multiplier * brightness * brightness
				materials.append(m)
			_tier_materials[key] = materials
		for i in materials.size():
			mesh.set_surface_override_material(i, materials[i])


func remove_collisions() -> void:
	collision_layer = 0
	collision_mask = 0


func reset_collisions() -> void:
	collision_layer = Layers.COIN
	collision_mask = Layers.WORLD | Layers.BOMB | Layers.COIN | Layers.SPAWNABLE | Layers.CONNECTOR


func kill() -> void:
	if killed:
		return
	# Guard against being collected twice on the same frame.
	value = 0
	unpickable = true
	super.kill()


func _on_body_entered(body: Node3D) -> void:
	if body is Player and not unpickable:
		body.increment_score(value)
		kill()


## Drops the coin in the world frozen for a moment (crate rewards).
func freeze_for(seconds: float) -> void:
	unpickable = true
	timer.wait_time = seconds
	if not timer.timeout.is_connected(_unfreeze):
		timer.timeout.connect(_unfreeze)
	collision_layer = 0
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_STATIC
	if is_inside_tree():
		timer.start()


func _unfreeze() -> void:
	unpickable = false
	reset_collisions()
	freeze = false
