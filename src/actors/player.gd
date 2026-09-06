class_name Player
extends CharacterBody3D
## The falling hero. A CharacterBody3D locked to the XY plane, driven by the
## same tuning as the original 2D game (converted from 64 px cells to metres).

signal score_changed(score: int)
signal shields_changed(active: int, maximum: int)
signal magnets_changed(count: int)
signal doubler_changed(active: bool)
## Short text for the HUD when something is picked up.
signal pickup_taken(text: String)
## Emitted once the death animation finished; the game shows the death screen.
signal died(score: int)

const GRAVITY := 47.0                 ## 3000 px/s²
const SPEED := Vector2(12.5, 21.9)    ## 800 px/s run, 1400 px/s jump
const PUSH_SPEED := 5.5               ## props we walk into are shoved up to this speed
const PUSH_GAIN := 0.35
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
var doubler_time := 0.0
## Lateral push accumulated from treadmills and trampolines; decays with gravity.
var lateral_force := 0.0

var _at_floor := false
var _falling_out_for := 0.0
var _death_progress := 0.0
var _pulling_coins: Array[Coin] = []
var _run_phase := 0.0
var _facing := 1.0
var _was_on_floor := true
var _squash := 1.0
var _blink_timer := 2.5
var _blink := 0.0
var _antenna_spring := Vector2.ZERO
var _antenna_vel := Vector2.ZERO
var _last_velocity := Vector3.ZERO
var _intent_x := 0.0
## Set by the skybridge while the player is legitimately outside the shaft.
var outside_ok := false

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
@onready var _eyes: Array[Node3D] = [model.find_child("eye_l", true, false), model.find_child("eye_r", true, false)]
@onready var _antenna: Node3D = model.find_child("antenna", true, false)
@onready var _scarf: Node3D = model.find_child("scarf", true, false)
@onready var _jets: Array[Node3D] = [model.find_child("jet_l", true, false), model.find_child("jet_r", true, false)]


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
	if doubler_time > 0.0:
		doubler_time -= delta
		if doubler_time <= 0.0:
			doubler_changed.emit(false)
	_animate(delta)


# ----------------------------------------------------------------- movement --
func _read_input() -> void:
	var right := Input.get_action_strength("move_right")
	var left := Input.get_action_strength("move_left")
	var direction := right - left
	if direction != 0.0:
		_facing = signf(direction)
	velocity.x = lateral_force + direction * SPEED.x
	_intent_x = velocity.x
	if Input.get_action_strength("jump") > 0.0 and _at_floor:
		velocity.y = SPEED.y
		_squash = 1.25
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
			var body := collider as RigidBody3D
			if body.has_method("turn_off"):
				body.call_deferred("turn_off")
			# Shove sideways only, and only up to a sensible speed, so furniture
			# slides instead of being launched or flipped.
			var direction := -collision.get_normal()
			direction.y = 0.0
			direction.z = 0.0
			if direction.length() < 0.3:
				continue
			direction = direction.normalized()
			var wanted := PUSH_SPEED * clampf(absf(_intent_x) / SPEED.x, 0.0, 1.0)
			var current := body.linear_velocity.dot(direction)
			if current < wanted:
				body.apply_central_impulse(direction * (wanted - current) * body.mass * PUSH_GAIN)


func _check_fall_out(delta: float) -> void:
	var outside := position.x < Grid.INTERIOR_MIN_X - 1.0 or position.x > Grid.INTERIOR_MAX_X + 0.2
	if outside_ok:
		outside = false
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
	var speed_t := clampf(absf(velocity.x) / SPEED.x, 0.0, 1.0)
	if running:
		_run_phase += delta * TAU * RUN_CYCLE_HZ * (0.6 + 0.4 * speed_t)
	else:
		_run_phase = lerpf(_run_phase, roundf(_run_phase / TAU) * TAU, minf(1.0, delta * 10.0))
	# Run cycle: legs stride with a quick knee lift on the back swing, arms
	# pump opposite to the legs, the torso leans into the run and bobs.
	var stride := sin(_run_phase)
	var lift := maxf(0.0, -sin(_run_phase * 2.0)) * 0.35
	var amp := (0.55 + 0.45 * speed_t) if running else 0.0
	var airborne := 0.0 if _at_floor else clampf(-velocity.y / SPEED.y, -0.6, 0.6)
	_set_limb("leg_l", (stride * 1.0 - lift * maxf(0.0, -stride)) * amp + airborne * 0.5)
	_set_limb("leg_r", (-stride * 1.0 - lift * maxf(0.0, stride)) * amp - airborne * 0.3)
	_set_limb("arm_l", (-stride * 1.1 - 0.35) * amp - airborne * 1.2)
	_set_limb("arm_r", (stride * 1.1 - 0.35) * amp - airborne * 1.2)
	var lean := (0.22 * speed_t) if running else 0.0
	model.rotation.x = lerpf(model.rotation.x, lean, minf(1.0, delta * 8.0))
	_animate_extras(delta, running)
	if is_immune:
		model.visible = fmod(Time.get_ticks_msec() / 1000.0 * 10.0, TAU) < PI
	else:
		model.visible = true


## The little touches: landing squash, falling stretch, blinking, a springy antenna, a fluttering scarf and jet flames.
func _animate_extras(delta: float, running: bool) -> void:
	if _at_floor and not _was_on_floor:
		_squash = 0.72
	_was_on_floor = _at_floor
	_squash = lerpf(_squash, 1.0, minf(1.0, delta * 9.0))
	var stretch := 1.0 + clampf(-velocity.y / SPEED.y, 0.0, 1.0) * 0.12
	var bob := absf(sin(_run_phase)) * 0.05 if running else 0.0
	model.scale = Vector3(2.0 - _squash, _squash * stretch + bob, 2.0 - _squash)
	# Blink.
	_blink_timer -= delta
	if _blink_timer <= 0.0:
		_blink = 0.14
		_blink_timer = randf_range(2.0, 5.0)
	if _blink > 0.0:
		_blink -= delta
	for eye in _eyes:
		if eye != null:
			eye.scale.y = 0.08 if _blink > 0.0 else 1.0
	# Antenna: a damped spring driven by acceleration.
	var accel := (velocity - _last_velocity) / maxf(delta, 0.001)
	_last_velocity = velocity
	_antenna_vel += (-Vector2(accel.x, accel.y) * 0.004 - _antenna_spring * 60.0 - _antenna_vel * 6.0) * delta
	_antenna_spring += _antenna_vel * delta
	if _antenna != null:
		_antenna.rotation = Vector3(clampf(_antenna_spring.y, -0.7, 0.7), 0.0, clampf(-_antenna_spring.x, -0.7, 0.7))
	# Scarf trails the motion.
	if _scarf != null:
		var flutter := sin(Time.get_ticks_msec() / 1000.0 * 9.0) * 0.12
		_scarf.rotation.x = clampf(velocity.y * 0.04, -0.9, 0.5) + flutter
		_scarf.rotation.z = clampf(-velocity.x * _facing * 0.03, -0.6, 0.6)
	# Jets burn while rising.
	var thrust := clampf(velocity.y / SPEED.y, 0.0, 1.0) if not _at_floor else 0.0
	for jet in _jets:
		if jet != null:
			jet.visible = thrust > 0.05
			jet.scale = Vector3(1.0, 0.6 + thrust * 0.9 + randf() * 0.2, 1.0)


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
	model.rotation = Vector3.ZERO
	model.scale = Vector3.ONE
	_squash = 1.0
	position.x = Grid.CENTER_X
	velocity = Vector3.ZERO
	set_active_shields(max_shields)
	add_immunity(REVIVE_IMMUNITY)


# -------------------------------------------------------------- collectibles --
func increment_score(value: int) -> void:
	if value > 0:
		sfx_coin.play()
		if doubler_time > 0.0:
			value *= 2
	score += value
	score_changed.emit(score)


func activate_doubler(seconds: float = 12.0) -> void:
	sfx_core_up.play()
	doubler_time = maxf(doubler_time, 0.0) + seconds
	doubler_changed.emit(true)
	pickup_taken.emit("coins x2!")


func increment_shield(count: int = 1) -> void:
	sfx_shield_up.play()
	set_active_shields(active_shields + count)
	pickup_taken.emit("shield up!")


func set_shields_to_max() -> void:
	sfx_shield_up.play()
	set_active_shields(max_shields)


func increment_max_shield() -> void:
	sfx_core_up.play()
	set_max_shields(max_shields + 1)
	pickup_taken.emit("max shields +1")


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
	pickup_taken.emit("magnet!")


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
