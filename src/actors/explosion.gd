class_name Explosion
extends Area3D
## A blast sphere that grows for 0.4 s, hurting everything inside and
## punching a hole through the hotel's cells, then fades out.
##
## The look (visual only, gameplay above is unchanged): a noise-shaded
## fireball (assets/shaders/core_fireball.gdshader) that cools from white
## heat to smoke and erodes away, an additive core flash, a shockwave ring,
## and GPU particles (26 sparks, 9 debris chunks, 10 smoke puffs; the smoke
## outlives the blast by a moment).

const BASE_RADIUS := 2.89        ## 184.7 px
const GROW_TIME := 0.4
const FADE_TIME := 0.8
const SHOCK_TIME := 0.35

var final_radius := BASE_RADIUS * 1.5
## Decorative explosion: no damage, no holes.
var harmless := false

var _elapsed := 0.0
var _radius := 0.0
var _cells: CellGrid
var _fx_scale := 1.0

@onready var shape: CollisionShape3D = $Shape
@onready var fireball: MeshInstance3D = $Fireball
@onready var core: MeshInstance3D = $Core
@onready var light: OmniLight3D = $Light
@onready var sfx: AudioStreamPlayer3D = $Sfx
@onready var shockwave: MeshInstance3D = $Shockwave
@onready var effects: Node3D = $Effects
@onready var smoke: GPUParticles3D = $Effects/Smoke


func set_explosion_scale(bomb_scale: float) -> void:
	final_radius = BASE_RADIUS * 1.5 * bomb_scale
	_fx_scale = bomb_scale


func _ready() -> void:
	shape.shape = shape.shape.duplicate()   # grows per blast, so never shared
	_cells = get_tree().get_first_node_in_group("cell_grid") as CellGrid
	if harmless:
		collision_mask = 0
	sfx.play()
	effects.scale = Vector3.ONE * _fx_scale
	fireball.set_instance_shader_parameter("seed", randf() * 50.0)
	for p in effects.get_children():
		(p as GPUParticles3D).restart()
	_apply_radius(0.0, 0.0)
	_update_shockwave()


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
			_release_smoke()
			queue_free()
	_update_shockwave()


func _apply_radius(radius: float, intensity: float) -> void:
	_radius = radius
	(shape.shape as SphereShape3D).radius = maxf(radius, 0.05)
	fireball.scale = Vector3.ONE * maxf(radius, 0.01)
	core.scale = Vector3.ONE * maxf(radius * 0.55, 0.01)
	# Visual heat: the fire flashes up almost at once and cools through the
	# fade; the core flash is brightest at the start.
	var growing := _elapsed <= GROW_TIME
	var heat := sqrt(intensity) if growing else intensity
	var age := clampf(_elapsed / (GROW_TIME + FADE_TIME), 0.0, 1.0)
	fireball.set_instance_shader_parameter("heat", heat)
	fireball.set_instance_shader_parameter("age", age)
	core.set_instance_shader_parameter("heat", (1.0 - 0.35 * intensity) if growing else intensity * intensity)
	light.light_energy = 6.0 * intensity
	light.omni_range = 4.0 + radius * 2.5


func _update_shockwave() -> void:
	var p := clampf(_elapsed / SHOCK_TIME, 0.0, 1.0)
	shockwave.visible = p < 1.0
	var r := final_radius * (0.2 + 1.3 * (1.0 - pow(1.0 - p, 3.0)))
	shockwave.scale = Vector3.ONE * r / 0.9
	shockwave.set_instance_shader_parameter("progress", p)


## The smoke drifts on for a moment after the blast itself is gone.
func _release_smoke() -> void:
	var parent := get_parent()
	if parent == null or not is_instance_valid(smoke) or smoke.get_parent() != effects:
		return
	smoke.reparent(parent)
	parent.get_tree().create_timer(smoke.lifetime).timeout.connect(smoke.queue_free)


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
