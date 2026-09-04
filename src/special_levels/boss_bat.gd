class_name BossBat
extends PlanarBody
## The bat boss: flutters around the arena shooting plasma that turns into
## crystal blocks wherever it lands. Steal its heart and it drops like a
## stone; when it hits the floor the arena opens.

signal level_won
signal fell

const BULLET := preload("res://src/spawnables/plasma_bullet.tscn")
const BLOCK := preload("res://src/special_levels/boss_block.tscn")
const EXPLOSION := preload("res://src/actors/explosion.tscn")
const SPEED := 2.2                ## 140 px/s on each axis
const BULLET_SPEED := 4.0
const MUZZLE := 2.4
const X_MIN := 3.0
const X_MAX := 13.0

@export var clap_per_second := 1.0
@export var min_rotation := -PI / 4.0
@export var max_rotation := PI / 4.0

var player: Node3D = null
var _started := false
var _dying := false
var _direction := Vector2(SPEED, SPEED)
var _wing_phase := 0.0
var _wing_dir := 1.0
var _y_min := 0.0
var _y_max := 0.0
var _blocks: Array[Node] = []

@onready var model: Node3D = $Model
@onready var wing_l: Node3D = model.find_child("wing_l", true, false)
@onready var wing_r: Node3D = model.find_child("wing_r", true, false)
@onready var bullet_timer: Timer = $BulletTimer


func _ready() -> void:
	add_to_group("boss")
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_KINEMATIC
	_y_min = position.y - 3.1
	_y_max = position.y + 8.5
	_randomize_direction()
	bullet_timer.timeout.connect(_shoot)


func start() -> void:
	_started = true
	bullet_timer.start()


func set_dying() -> void:
	if _dying:
		return
	_dying = true
	bullet_timer.stop()
	freeze = false
	gravity_scale = 1.5


func _randomize_direction() -> void:
	_direction = _direction.rotated(randf_range(-TAU, TAU))
	if (position.y >= _y_max and _direction.y > 0.0) or (position.y <= _y_min and _direction.y < 0.0):
		_direction.y = -_direction.y
	if (position.x <= X_MIN and _direction.x < 0.0) or (position.x >= X_MAX and _direction.x > 0.0):
		_direction.x = -_direction.x


func _process(delta: float) -> void:
	if _dying:
		return
	_wing_phase += delta * clap_per_second * _wing_dir * 2.0
	if _wing_phase >= 1.0:
		_wing_dir = -1.0
	elif _wing_phase <= 0.0:
		_wing_dir = 1.0
	var angle := lerpf(min_rotation, max_rotation, _wing_phase)
	if wing_l != null:
		wing_l.rotation.z = -angle
	if wing_r != null:
		wing_r.rotation.z = angle
	if not _started:
		return
	if position.y <= _y_min or position.y >= _y_max or position.x <= X_MIN or position.x >= X_MAX:
		_randomize_direction()
	position += Vector3(_direction.x, _direction.y, 0.0) * delta
	model.scale.x = -1.0 if _direction.x < 0.0 else 1.0


func _shoot() -> void:
	if player == null or _dying:
		return
	var to_player := player.global_position + Vector3(0, 0.7, 0) - global_position
	to_player.z = 0.0
	var direction := to_player.normalized()
	var bullet: PlasmaBullet = BULLET.instantiate()
	bullet.set_velocity(direction * BULLET_SPEED)
	bullet.position = global_position + direction * MUZZLE
	bullet.dont_free_on_bombs = true
	bullet.hit.connect(_on_bullet_hit.bind(bullet))
	get_parent().add_child(bullet)


func _on_bullet_hit(item: Node, bullet: PlasmaBullet) -> void:
	if item is BatHeart or (item != null and item.get_parent() is BatHeart):
		level_won.emit()
	if item is Player or item is Bomb:
		return
	var block := BLOCK.instantiate()
	block.position = bullet.global_position + Vector3(0.0, 0.5, 0.0)
	get_parent().add_child(block)
	_blocks.append(block)


func _on_killed() -> void:
	for block in _blocks:
		if is_instance_valid(block):
			block.queue_free()
	var explosion: Explosion = EXPLOSION.instantiate()
	explosion.set_explosion_scale(1.2)
	explosion.harmless = true
	explosion.position = global_position
	get_parent().add_child(explosion)
