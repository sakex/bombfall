class_name Explosion
extends Area3D
## A blast sphere that grows for 0.4 s, hurting everything inside and
## punching a hole through the hotel's cells, then fades out.

const BASE_RADIUS := 2.89        ## 184.7 px
const GROW_TIME := 0.4
const FADE_TIME := 0.8

var final_radius := BASE_RADIUS * 1.5
## Decorative explosion: no damage, no holes.
var harmless := false

var _elapsed := 0.0
var _radius := 0.0
var _cells: CellGrid

@onready var shape: CollisionShape3D = $Shape
@onready var fireball: MeshInstance3D = $Fireball
@onready var core: MeshInstance3D = $Core
@onready var light: OmniLight3D = $Light
@onready var sfx: AudioStreamPlayer3D = $Sfx


func set_explosion_scale(bomb_scale: float) -> void:
	final_radius = BASE_RADIUS * 1.5 * bomb_scale


func _ready() -> void:
	shape.shape = shape.shape.duplicate()   # grows per blast, so never shared
	_cells = get_tree().get_first_node_in_group("cell_grid") as CellGrid
	if harmless:
		collision_mask = 0
	sfx.play()
	_apply_radius(0.0, 0.0)


func _physics_process(delta: float) -> void:
	_elapsed += delta
	if _elapsed <= GROW_TIME:
		var t := _elapsed / GROW_TIME
		_apply_radius(final_radius * t, t)
		if not harmless:
			_blast()
	else:
		var t := clampf((_elapsed - GROW_TIME) / FADE_TIME, 0.0, 1.0)
		_apply_radius(final_radius * (1.0 + 0.15 * t), 1.0 - t)
		shape.disabled = true
		if t >= 1.0:
			queue_free()


func _apply_radius(radius: float, intensity: float) -> void:
	_radius = radius
	(shape.shape as SphereShape3D).radius = maxf(radius, 0.05)
	fireball.scale = Vector3.ONE * maxf(radius, 0.01)
	core.scale = Vector3.ONE * maxf(radius * 0.55, 0.01)
	var mat := fireball.get_active_material(0) as StandardMaterial3D
	if mat != null:
		mat.albedo_color.a = 0.85 * intensity
	var core_mat := core.get_active_material(0) as StandardMaterial3D
	if core_mat != null:
		core_mat.albedo_color.a = intensity
	light.light_energy = 6.0 * intensity
	light.omni_range = 4.0 + radius * 2.5


func _blast() -> void:
	for body in get_overlapping_bodies():
		if body.has_method("kill"):
			body.call_deferred("kill")
	# Area props (trampolines and the like) are not reliably reported as
	# overlapping areas by the physics engine, so reach them by distance.
	for node in get_tree().get_nodes_in_group("props"):
		if node is Node3D and not (node is PhysicsBody3D) and node.has_method("kill"):
			if (node as Node3D).global_position.distance_to(global_position) <= _radius + 0.6:
				node.call_deferred("kill")
	if _cells != null:
		_cells.destroy_in_sphere(global_position, _radius, get_instance_id())
