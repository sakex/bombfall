class_name BossBat
extends PlanarBody
## The bat boss: flutters around the arena shooting plasma that turns into
## crystal blocks wherever it lands. Steal its heart and it drops like a
## stone; when it hits the floor the arena opens.
##
## The model is rigged (see blender/hazards.py boss_bat): its "idle" clip
## beats the wings (two beats per loop), "fall" flails them while it
## drops. The jaw bone is driven here: it snaps open on every shot and
## gapes while falling; the eyes flare when it fires and the chest heart
## goes dark once the heart has been taken.

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
const JAW_OPEN := 0.6             ## radians at a full gape
const EYE_ENERGY := 6.0

## Wing beats per second (plays the idle clip faster or slower).
@export var clap_per_second := 1.0

var player: Node3D = null
var _started := false
var _dying := false
var _direction := Vector2(SPEED, SPEED)
var _y_min := 0.0
var _y_max := 0.0
var _blocks: Array[Node] = []
var _anim: AnimationPlayer
var _skeleton: Skeleton3D
var _jaw := -1
var _jaw_rest := Quaternion.IDENTITY
var _jaw_amount := 0.0
var _jaw_target := 0.0
var _flash := 0.0
var _eyes: StandardMaterial3D
var _heart: StandardMaterial3D

@onready var model: Node3D = $Model
@onready var bullet_timer: Timer = $BulletTimer


func _ready() -> void:
	add_to_group("boss")
	freeze = true
	freeze_mode = RigidBody3D.FREEZE_MODE_KINEMATIC
	_y_min = position.y - 3.1
	_y_max = position.y + 8.5
	_randomize_direction()
	bullet_timer.timeout.connect(_shoot)
	_anim = ModelUtil.anim_player(model)
	if _anim != null:
		_anim.speed_scale = clap_per_second
	var skeletons := model.find_children("*", "Skeleton3D", true, false)
	if not skeletons.is_empty():
		_skeleton = skeletons[0]
		_jaw = _skeleton.find_bone("jaw")
		if _jaw >= 0:
			_jaw_rest = _skeleton.get_bone_rest(_jaw).basis.get_rotation_quaternion()
	_eyes = ModelUtil.own_material(ModelUtil.find_mesh(model, "eyes"))
	_heart = ModelUtil.own_material(ModelUtil.find_mesh(model, "heart_glow"))


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
	_jaw_target = 1.0
	if _anim != null:
		_anim.speed_scale = 1.0
		# Godot imports the "fall_loop" clip as "fall" (looping).
		ModelUtil.play(model, "fall")
	if _heart != null:
		_heart.emission_energy_multiplier = 0.15


func is_dying() -> bool:
	return _dying


func _randomize_direction() -> void:
	_direction = _direction.rotated(randf_range(-TAU, TAU))
	if (position.y >= _y_max and _direction.y > 0.0) or (position.y <= _y_min and _direction.y < 0.0):
		_direction.y = -_direction.y
	if (position.x <= X_MIN and _direction.x < 0.0) or (position.x >= X_MAX and _direction.x > 0.0):
		_direction.x = -_direction.x


func _process(delta: float) -> void:
	_animate_face(delta)
	if _dying or not _started:
		return
	if position.y <= _y_min or position.y >= _y_max or position.x <= X_MIN or position.x >= X_MAX:
		_randomize_direction()
	position += Vector3(_direction.x, _direction.y, 0.0) * delta
	model.scale.x = -1.0 if _direction.x < 0.0 else 1.0


## Jaw snap and eye flare: quick attack, slower release.
func _animate_face(delta: float) -> void:
	var rate := 14.0 if _jaw_amount < _jaw_target else 4.0
	_jaw_amount = move_toward(_jaw_amount, _jaw_target, delta * rate)
	if _jaw_amount >= _jaw_target and not _dying:
		_jaw_target = 0.0
	if _skeleton != null and _jaw >= 0:
		_skeleton.set_bone_pose_rotation(_jaw, _jaw_rest * Quaternion(Vector3.RIGHT, -_jaw_amount * JAW_OPEN))
	_flash = maxf(_flash - delta * 3.0, 0.0)
	if _eyes != null:
		var flicker: float = 0.6 + 0.4 * sin(Time.get_ticks_msec() * 0.05) if _dying else 1.0
		_eyes.emission_energy_multiplier = EYE_ENERGY * (1.0 + 1.5 * _flash) * flicker


func _shoot() -> void:
	if player == null or _dying:
		return
	Sfx.play("plasma", 0.8)
	_jaw_target = 1.0
	_flash = 1.0
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
	block.lifetime = 0.0   # crystals last the whole fight: they are the stairs to the heart
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
