class_name BossBatArena
extends Node3D
## The bat boss fight. Entering the arena locks the camera and wakes the
## boss; killing it opens the floor and drops a crate of coins.

const CRATE_SCENE := "res://src/spawnables/crate.tscn"
const BLOCK := preload("res://src/special_levels/boss_block.tscn")
const BOSS_SPAWN_TIME := 3.0
const FLOOR_DELETE_DELAY := 10.0
## The bat's crystals also grow up the wall under its heart while the fight
## drags on: one frozen step every few seconds, so the heart is always
## reachable within a couple of minutes even if the stray shots do not pile up.
const LADDER_INTERVAL := 8.0
const LADDER_STEPS := [
	Vector2(14.5, -17.2), Vector2(11.8, -14.6), Vector2(14.5, -12.0), Vector2(11.8, -9.4),
	Vector2(14.5, -6.8), Vector2(12.4, -4.4),
]

var coin_budget := 0
var _world: Node = null
var _player: Player = null
var _rig: CameraRig = null
var _spawn_progress := 0.0
var _boss_awake := false
var _floor_flashing := false
var _floor_material: StandardMaterial3D
var _ladder_time := 0.0
var _ladder_built := 0
var ladder: Array[Node3D] = []

@onready var boss: BossBat = $BossBat
@onready var heart: BatHeart = $BatHeart
@onready var detection: Area3D = $PlayerDetection
@onready var kill_area: Area3D = $BossKillArea
@onready var floor_body: StaticBody3D = $Floor
@onready var floor_mesh: MeshInstance3D = $Floor/Mesh
@onready var camera_anchor: Node3D = $CameraAnchor


func _ready() -> void:
	boss.model.scale = Vector3.ONE * 0.01
	detection.body_entered.connect(_on_player_entered)
	detection.body_exited.connect(_on_player_exited)
	boss.level_won.connect(_level_won)
	heart.heart_taken.connect(_level_won)
	kill_area.body_entered.connect(_on_kill_area)
	_floor_material = floor_mesh.material_override as StandardMaterial3D
	_rig = get_tree().get_first_node_in_group("camera_rig") as CameraRig


func set_world(world: Node) -> void:
	_world = world


func _process(delta: float) -> void:
	if _player != null and not _boss_awake:
		_spawn_progress = minf(_spawn_progress + delta / BOSS_SPAWN_TIME, 1.0)
		boss.model.scale = Vector3.ONE * maxf(_spawn_progress, 0.01)
		if _spawn_progress >= 1.0:
			_boss_awake = true
			boss.start()
			heart.enable_heart()
	if _boss_awake and not boss.is_dying() and _ladder_built < LADDER_STEPS.size():
		_ladder_time += delta
		if _ladder_time >= LADDER_INTERVAL:
			_ladder_time = 0.0
			_grow_ladder_step()
	if _floor_flashing and _floor_material != null:
		_floor_material.emission_energy_multiplier = 1.0 + 3.0 * (0.5 + 0.5 * sin(Time.get_ticks_msec() / 1000.0 * 12.0))


func _grow_ladder_step() -> void:
	var step: Vector2 = LADDER_STEPS[_ladder_built]
	_ladder_built += 1
	var block: RigidBody3D = BLOCK.instantiate()
	block.lifetime = 0.0
	block.indestructible = true
	block.freeze = true
	block.freeze_mode = RigidBody3D.FREEZE_MODE_STATIC
	block.position = Vector3(step.x, step.y, 0.0)
	block.scale = Vector3(2.0, 0.7, 1.0)
	add_child(block)
	ladder.append(block)


func _on_player_entered(body: Node) -> void:
	if not (body is Player):
		return
	_player = body
	boss.player = body
	if _rig != null:
		_rig.override_target = camera_anchor


func _on_player_exited(body: Node) -> void:
	if body == _player and _rig != null and _rig.override_target == camera_anchor:
		_rig.override_target = null


func _level_won() -> void:
	boss.set_dying()


func _on_kill_area(body: Node) -> void:
	if body != boss:
		return
	kill_area.queue_free()
	boss.kill()
	if _world != null:
		_world.spawn_scene(CRATE_SCENE, position + Vector3(8.75, -10.25, 0.0), {"coin_budget": coin_budget})
	_floor_flashing = true
	if _floor_material != null:
		_floor_material.emission_enabled = true
		_floor_material.emission = Color(1.0, 0.4, 0.2)
	get_tree().create_timer(FLOOR_DELETE_DELAY).timeout.connect(_delete_floor)


func _delete_floor() -> void:
	if is_instance_valid(floor_body):
		floor_body.queue_free()
	if _rig != null and _rig.override_target == camera_anchor:
		_rig.override_target = null


func _exit_tree() -> void:
	if _rig != null and _rig.override_target == camera_anchor:
		_rig.override_target = null
