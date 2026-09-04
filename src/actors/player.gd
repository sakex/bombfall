class_name Player
extends CharacterBody3D
## The falling hero. A CharacterBody3D locked to the XY plane, driven by the
## same tuning as the original 2D game (converted from 64 px cells to metres).

signal score_changed(score: int)
signal shields_changed(active: int, maximum: int)
signal magnets_changed(count: int)
## Emitted once the death animation finished; the game shows the death screen.
signal died(score: int)

const GRAVITY := 47.0                 ## 3000 px/s²
const SPEED := Vector2(12.5, 21.9)    ## 800 px/s run, 1400 px/s jump
const IMPULSE_STRENGTH := 15.6        ## impulse handed to props we bump into
const DEATH_ANIMATION_TIME := 2.0
const FALL_OUT_TIME := 2.0            ## seconds outside the shaft before dying
const MAGNET_RADIUS_PER_LEVEL := 5.0  ## 320 px per magnet upgrade
const SHIELD_IMMUNITY := 5.0
const REVIVE_IMMUNITY := 10.0
const RUN_CYCLE_HZ := 3.2

@export var play_start_sound := true

var score := 0
var max_shields := 1
var active_shields := 0
var magnets := 0
var is_immune := false
## Lateral push accumulated from treadmills and trampolines; decays with gravity.
var lateral_force := 0.0

var _at_floor := false
var _falling_out_for := 0.0
var _death_progress := 0.0
var _pulling_coins: Array[Coin] = []
var _run_phase := 0.0
var _facing := 1.0

@onready var model: Node3D = $Model
@onready var shield_bubble: MeshInstance3D = $Shield
@onready var feet_area: Area3D = $Feet
@onready var magnet_area: Area3D = $Magnet
@onready var magnet_shape: CollisionShape3D = $Magnet/Shape
@onready var immunity_timer: Timer = $ImmunityTimer
@onready var sfx_coin: AudioStreamPlayer = $SfxCoin
@onready var sfx_shield_up: AudioStreamPlayer = $SfxShieldUp
@onready var sfx_core_up: AudioStreamPlayer = $SfxCoreUp
@onready var sfx_hit: AudioStreamPlayer = $SfxHit
@onready var sfx_death: AudioStreamPlayer = $SfxDeath
@onready var sfx_start: AudioStreamPlayer = $SfxStart
@onready var _limbs := {
	"leg_l": model.find_child("leg_l", true, false),
	"leg_r": model.find_child("leg_r", true, false),
	"arm_l": model.find_child("arm_l", true, false),
	"arm_r": model.find_child("arm_r", true, false),
}


func _ready() -> void:
	add_to_group("player")
	up_direction = Vector3.UP
	floor_max_angle = deg_to_rad(80.0)
	floor_stop_on_slope = false
	magnet_area.body_entered.connect(_on_magnet_body_entered)
	immunity_timer.timeout.connect(_on_immunity_timeout)
	_update_shield_bubble()
	if play_start_sound:
		sfx_start.play()


func _physics_process(delta: float) -> void:
	if _death_progress > 0.0:
		return
	_at_floor = is_on_floor() or feet_area.has_overlapping_bodies()
	_read_input()
	_move(delta)
	_push_props()
	_pull_coins(delta)
	_check_fall_out(delta)


func _process(delta: float) -> void:
	if _death_progress > 0.0:
		_advance_death(delta)
		return
	_animate(delta)


# ----------------------------------------------------------------- movement --
func _read_input() -> void:
	var right := Input.get_action_strength("move_right")
	var left := Input.get_action_strength("move_left")
	var direction := right - left
	if direction != 0.0:
		_facing = signf(direction)
	velocity.x = lateral_force + direction * SPEED.x
	if Input.get_action_strength("jump") > 0.0 and _at_floor:
		velocity.y = SPEED.y
	if Input.is_action_just_released("jump") and velocity.y > 0.0:
		velocity.y = 0.0


func _move(delta: float) -> void:
	# The lateral push from treadmills/trampolines bleeds off like gravity.
	if absf(lateral_force) < 0.15:
		lateral_force = 0.0
	lateral_force = clampf(lateral_force, -SPEED.x, SPEED.x)
	if lateral_force > 0.0:
		lateral_force = maxf(lateral_force - GRAVITY * delta, 0.0)
	elif lateral_force < 0.0:
		lateral_force = minf(lateral_force + GRAVITY * delta, 0.0)
	velocity.y -= GRAVITY * delta
	velocity.y = maxf(velocity.y, -SPEED.y)
	velocity.x = clampf(velocity.x, -SPEED.x, SPEED.x)
	velocity.z = 0.0
	move_and_slide()
	position.z = 0.0


func _push_props() -> void:
	for i in get_slide_collision_count():
		var collision := get_slide_collision(i)
		var collider := collision.get_collider()
		if collider is RigidBody3D:
			if collider.has_method("turn_off"):
				collider.call_deferred("turn_off")
			var normal := collision.get_normal()
			# Standing on top of it: only a quarter of the shove.
			var strength := IMPULSE_STRENGTH * (0.25 if normal.y > 0.9 else 1.0)
			var impulse := -normal * strength
			impulse.z = 0.0
			collider.apply_central_impulse(impulse)


func _check_fall_out(delta: float) -> void:
	var outside := position.x < Grid.INTERIOR_MIN_X - 1.0 or position.x > Grid.INTERIOR_MAX_X + 0.2
	if not is_on_floor() and outside:
		_falling_out_for += delta
		if _falling_out_for > FALL_OUT_TIME:
			insta_kill()
	else:
		_falling_out_for = 0.0


# ---------------------------------------------------------------- animation --
func _animate(delta: float) -> void:
	var target_yaw := _facing * deg_to_rad(65.0)
	model.rotation.y = lerp_angle(model.rotation.y, target_yaw, minf(1.0, delta * 12.0))
	var running := absf(velocity.x) > 0.5 and _at_floor
	if running:
		_run_phase += delta * TAU * RUN_CYCLE_HZ
	else:
		_run_phase = lerpf(_run_phase, roundf(_run_phase / PI) * PI, minf(1.0, delta * 10.0))
	var swing := sin(_run_phase) * (0.75 if running else 0.0)
	var airborne := 0.0 if _at_floor else clampf(-velocity.y / SPEED.y, -0.6, 0.6)
	_set_limb("leg_l", swing + airborne * 0.4)
	_set_limb("leg_r", -swing - airborne * 0.2)
	_set_limb("arm_l", -swing * 0.8 - airborne * 1.2)
	_set_limb("arm_r", swing * 0.8 - airborne * 1.2)
	if is_immune:
		model.visible = fmod(Time.get_ticks_msec() / 1000.0 * 10.0, TAU) < PI
	else:
		model.visible = true


func _set_limb(name: String, angle: float) -> void:
	var limb: Node3D = _limbs[name]
	if limb != null:
		limb.rotation.x = angle


func _advance_death(delta: float) -> void:
	_death_progress += delta / DEATH_ANIMATION_TIME
	var t := _death_progress
	model.visible = true
	model.position = Vector3(randf_range(-1.0, 1.0), randf_range(-0.5, 0.5), 0.0) * t * 0.35
	model.rotation.z = sin(t * 40.0) * t * 0.6
	model.scale = Vector3.ONE * maxf(0.05, 1.0 - t * t)
	shield_bubble.visible = false
	if t >= 1.0:
		_death_progress = 1.0
		set_process(false)
		died.emit(score)


# ------------------------------------------------------------------- damage --
## An explosion or hazard touched us. Costs a shield, or the run.
func kill() -> void:
	if is_immune or _death_progress > 0.0:
		return
	if active_shields == 0:
		_death_progress = 0.001
		sfx_death.play()
		return
	lower_shields()


## Death that ignores shields (falling out of the hotel).
func insta_kill() -> void:
	active_shields = 0
	is_immune = false
	kill()


func lower_shields() -> void:
	sfx_hit.play()
	set_active_shields(active_shields - 1)
	add_immunity(SHIELD_IMMUNITY)


func add_immunity(seconds: float) -> void:
	is_immune = true
	immunity_timer.wait_time = immunity_timer.time_left + seconds
	immunity_timer.start()


func _on_immunity_timeout() -> void:
	is_immune = false
	model.visible = true


func revive() -> void:
	_death_progress = 0.0
	set_process(true)
	model.position = Vector3.ZERO
	model.rotation.z = 0.0
	model.scale = Vector3.ONE
	position.x = Grid.CENTER_X
	velocity = Vector3.ZERO
	set_active_shields(max_shields)
	add_immunity(REVIVE_IMMUNITY)


# -------------------------------------------------------------- collectibles --
func increment_score(value: int) -> void:
	if value > 0:
		sfx_coin.play()
	score += value
	score_changed.emit(score)


func increment_shield(count: int = 1) -> void:
	sfx_shield_up.play()
	set_active_shields(active_shields + count)


func set_shields_to_max() -> void:
	sfx_shield_up.play()
	set_active_shields(max_shields)


func increment_max_shield() -> void:
	sfx_core_up.play()
	set_max_shields(max_shields + 1)


func set_active_shields(count: int) -> void:
	active_shields = clampi(count, 0, max_shields)
	_update_shield_bubble()
	shields_changed.emit(active_shields, max_shields)


func set_max_shields(count: int) -> void:
	max_shields = maxi(count, 1)
	active_shields = mini(active_shields, max_shields)
	_update_shield_bubble()
	shields_changed.emit(active_shields, max_shields)


func _update_shield_bubble() -> void:
	shield_bubble.visible = active_shields > 0
	var material := shield_bubble.get_active_material(0) as StandardMaterial3D
	if material != null:
		material.albedo_color.a = clampf(0.10 + 0.08 * active_shields, 0.0, 0.5)
		material.emission_energy_multiplier = 0.6 + 0.4 * active_shields


func increase_magnet() -> void:
	set_magnets(magnets + 1)


func set_magnets(count: int) -> void:
	magnets = maxi(count, 0)
	magnets_changed.emit(magnets)
	var shape := magnet_shape.shape as SphereShape3D
	if magnets == 0:
		shape.radius = 0.1
		magnet_shape.disabled = true
	else:
		magnet_shape.disabled = false
		shape.radius = MAGNET_RADIUS_PER_LEVEL * magnets


func _on_magnet_body_entered(body: Node3D) -> void:
	if body is Coin and not _pulling_coins.has(body):
		body.remove_collisions()
		_pulling_coins.append(body)


func _pull_coins(delta: float) -> void:
	for i in range(_pulling_coins.size() - 1, -1, -1):
		var coin := _pulling_coins[i]
		if not is_instance_valid(coin):
			_pulling_coins.remove_at(i)
			continue
		if coin.unpickable:
			continue
		var to_player := global_position + Vector3(0, 0.7, 0) - coin.global_position
		coin.linear_velocity = to_player * 150.0 * delta
