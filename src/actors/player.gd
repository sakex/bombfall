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
const PUSH_SPEED := 5.5               ## a light prop we walk into is shoved up to this speed
const PUSH_GAIN := 0.35
const PUSH_REF_MASS := 25.0           ## chair-sized; heavier props move slower and creep
const HEAD_BUMP := 9.5                ## m/s given to a bomb we jump into from below
const DEATH_ANIMATION_TIME := 1.8     ## the collapse clip, then a beat before the death screen
const FALL_OUT_TIME := 2.0            ## seconds outside the shaft before dying
const MAGNET_RADIUS_PER_LEVEL := 5.0  ## 320 px per magnet upgrade
const SHIELD_IMMUNITY := 5.0
const REVIVE_IMMUNITY := 10.0
const RUN_CYCLE_HZ := 3.2            ## full strides per second at top speed
const RUN_CLIP_STRIDES := 1.0         ## the run clip holds one full stride (two steps)
const PUSH_CYCLE_HZ := 1.1
## How long each clip takes to crossfade in.
const BLEND := {
	"idle": 0.25, "run": 0.12, "push": 0.15, "jump": 0.05, "rise": 0.12,
	"fall": 0.25, "land": 0.05, "hurt": 0.05, "death": 0.08, "wave": 0.2,
}

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
var _push_time := 0.0             ## seconds left of the shove pose after a push
var _pre_slide_velocity := Vector3.ZERO
var _facing := 1.0
var _was_on_floor := true
var _squash := 1.0
var _blink_timer := 2.5
var _blink := 0.0
var _antenna_spring := Vector3.ZERO
var _antenna_vel := Vector3.ZERO
var _scarf_spring := 0.0
var _scarf_vel := 0.0
var _clip := ""
var _clip_phase := -1.0            ## last normalised position of a stepping clip
var _air_time := 0.0
var _jump_time := 0.0
var _land_time := 0.0
var _hurt_time := 0.0
var _death_started := false
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
@onready var _anim: AnimationPlayer = ModelUtil.anim_player(model)
@onready var _skel: Skeleton3D = _find_skeleton(model)
## Bone ids and the bone-local axes the procedural touches work along.
var _bones := {}
var _blink_axis := {}
var _jet_axis := {}


func _ready() -> void:
	add_to_group("player")
	up_direction = Vector3.UP
	floor_max_angle = deg_to_rad(80.0)
	floor_stop_on_slope = false
	magnet_area.body_entered.connect(_on_magnet_body_entered)
	immunity_timer.timeout.connect(_on_immunity_timeout)
	_update_shield_bubble()
	_setup_rig()
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
		_jump_time = 0.26
		Sfx.play("jump")
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
	_pre_slide_velocity = velocity
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
			# Jumping into something from below knocks it up and away.
			if collision.get_normal().y < -0.5 and _pre_slide_velocity.y > 2.0:
				var away := signf(body.global_position.x - global_position.x)
				if away == 0.0:
					away = _facing
				body.apply_central_impulse(Vector3(away * 0.4, 1.0, 0.0).normalized() * HEAD_BUMP * body.mass)
				_squash = 1.18
				Sfx.play("metal_bounce" if body is Bomb else "land", 1.2)
				continue
			# Shove sideways only, and only up to a sensible speed, so furniture
			# slides instead of being launched or flipped.
			var direction := -collision.get_normal()
			direction.y = 0.0
			direction.z = 0.0
			if direction.length() < 0.3:
				continue
			direction = direction.normalized()
			# Heft: a bottle skids off at full speed, a toilet lumbers, a bathtub creeps.
			var heft := clampf(PUSH_REF_MASS / maxf(body.mass, 1.0), 0.18, 1.0)
			var wanted := PUSH_SPEED * heft * clampf(absf(_intent_x) / SPEED.x, 0.0, 1.0)
			var current := body.linear_velocity.dot(direction)
			if current < wanted:
				# Shove low, near the floor, so friction cannot tip tall props over.
				var impulse := direction * (wanted - current) * body.mass * PUSH_GAIN * heft
				body.apply_impulse(impulse, Vector3(0.0, 0.12, 0.0))
			if absf(_intent_x) > 0.5 and direction.x * _facing > 0.0:
				_push_time = 0.12


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
# The model is a skinned rig with authored clips (blender/player.py): idle,
# run, push, jump, rise, fall, land, hurt, death, wave (the importer strips
# the "_loop" suffix of the Blender clips and loops them). The
# AnimationPlayer is advanced by hand here each frame so the procedural
# touches (blinks, jet flames, antenna and scarf springs) can be layered on
# the bones after the clip has posed them.
static func _find_skeleton(root: Node) -> Skeleton3D:
	if root == null:
		return null
	var found := root.find_children("*", "Skeleton3D", true, false)
	return null if found.is_empty() else found[0] as Skeleton3D


func _setup_rig() -> void:
	if _anim != null:
		ModelUtil.prepare_animations(_anim)
		_anim.callback_mode_process = AnimationMixer.ANIMATION_CALLBACK_MODE_PROCESS_MANUAL
	if _skel != null:
		for bone in ["eye_l", "eye_r", "jet_l", "jet_r", "antenna_1", "antenna_2", "antenna_3",
				"scarf_1", "scarf_2", "scarf_3"]:
			_bones[bone] = _skel.find_bone(bone)
		for bone in ["eye_l", "eye_r"]:
			_blink_axis[bone] = _dominant_axis(bone, Vector3.UP)
		for bone in ["jet_l", "jet_r"]:
			_jet_axis[bone] = _dominant_axis(bone, Vector3.DOWN)
	_play("idle", 0.0)
	if _anim != null:
		_anim.advance(0.0)
	_apply_rig(0.0, 1.0)


## The bone-local axis (0 = x, 1 = y, 2 = z) closest to a skeleton-space direction.
func _dominant_axis(bone: String, dir: Vector3) -> int:
	var i: int = _bones.get(bone, -1)
	if i < 0:
		return 1
	var local := (_skel.get_bone_global_rest(i).basis.inverse() * dir).abs()
	if local.x >= local.y and local.x >= local.z:
		return 0
	return 1 if local.y >= local.z else 2


## The AnimationPlayer's name for a clip ("run" may also be "run_loop").
func _real(clip: String) -> String:
	if _anim != null and not _anim.has_animation(clip) and _anim.has_animation(clip + "_loop"):
		return clip + "_loop"
	return clip


## Crossfades to [param clip] unless it is already the current one.
func _play(clip: String, blend := -1.0) -> void:
	if _anim == null or not _anim.has_animation(_real(clip)) or clip == _clip:
		return
	_clip = clip
	_clip_phase = -1.0
	_anim.play(_real(clip), BLEND.get(clip, 0.15) if blend < 0.0 else blend)


## Plays a one-shot clip from its start, even if it is already playing.
func _replay(clip: String) -> void:
	if _clip == clip and _anim != null:
		_anim.seek(0.0, false)
	else:
		_play(clip)


func _animate(delta: float) -> void:
	var target_yaw := _facing * deg_to_rad(65.0)
	model.rotation.y = lerp_angle(model.rotation.y, target_yaw, minf(1.0, delta * 12.0))
	var speed_t := clampf(absf(velocity.x) / SPEED.x, 0.0, 1.0)
	var running := absf(velocity.x) > 0.5 and _at_floor
	_push_time = maxf(_push_time - delta, 0.0)
	var shoving := _push_time > 0.0 and _at_floor
	_jump_time = maxf(_jump_time - delta, 0.0)
	_land_time = maxf(_land_time - delta, 0.0)
	_air_time = 0.0 if _at_floor else _air_time + delta
	if _at_floor and not _was_on_floor:
		_squash = 0.72
		Sfx.play("land", 1.0, clampf(-_last_velocity.y * 0.25 - 6.0, -10.0, 4.0))
		if not running and not shoving and _last_velocity.y < -3.0:
			_land_time = 0.32
			_replay("land")
	_was_on_floor = _at_floor
	if _hurt_time > 0.0:
		var fresh := _hurt_time >= 0.45
		_hurt_time = maxf(_hurt_time - delta, 0.0)
		if fresh:
			_replay("hurt")

	# Pick the clip for the gameplay state.
	var clip := "idle"
	var speed := 1.0
	if _hurt_time > 0.0:
		clip = "hurt"
	elif not _at_floor:
		if _jump_time > 0.0:
			clip = "jump"
		elif _air_time > 0.08:
			clip = "rise" if velocity.y > 1.5 else "fall"
		else:
			clip = _clip if _clip != "" else "idle"   # a short drop keeps the stride going
	elif shoving:
		clip = "push"
		speed = PUSH_CYCLE_HZ * _clip_length(clip) * (0.75 + 0.5 * clampf(absf(_intent_x) / SPEED.x, 0.0, 1.0))
	elif running:
		clip = "run"
		speed = RUN_CYCLE_HZ * (0.6 + 0.4 * speed_t) * _clip_length(clip) / RUN_CLIP_STRIDES
	elif _land_time > 0.0:
		clip = "land"
	_play(clip)
	if _anim != null:
		_anim.speed_scale = speed if (_clip == "run" or _clip == "push") else 1.0
		_anim.advance(delta)
	_footsteps(speed_t)
	_animate_extras(delta)
	if is_immune:
		model.visible = fmod(Time.get_ticks_msec() / 1000.0 * 10.0, TAU) < PI
	else:
		model.visible = true


func _clip_length(clip: String) -> float:
	if _anim == null or not _anim.has_animation(_real(clip)):
		return 1.0
	return _anim.get_animation(_real(clip)).length


## A step sound at each heel strike: the run and push clips hold two steps,
## with the contacts at the start and the middle of the clip.
func _footsteps(speed_t: float) -> void:
	if _anim == null or not _at_floor or (_clip != "run" and _clip != "push") \
			or _anim.current_animation != _real(_clip):
		_clip_phase = -1.0
		return
	var length := _anim.current_animation_length
	if length <= 0.0:
		return
	var ph := fmod(_anim.current_animation_position / length + 0.97, 1.0)   # a frame early, as the heel lands
	if _clip_phase >= 0.0 and ((_clip_phase < 0.5 and ph >= 0.5) or ph < _clip_phase):
		if _clip == "run":
			Sfx.play("step", 0.9 + 0.2 * speed_t)
		else:
			Sfx.play("step", 0.72)
	_clip_phase = ph


## The little touches: landing squash, falling stretch, blinking, a springy
## antenna, a streaming scarf and jet flames while rising.
func _animate_extras(delta: float) -> void:
	_squash = lerpf(_squash, 1.0, minf(1.0, delta * 9.0))
	var stretch := 1.0 + clampf(-velocity.y / SPEED.y, 0.0, 1.0) * 0.08
	model.scale = Vector3(2.0 - _squash, _squash * stretch, 2.0 - _squash)
	_blink_timer -= delta
	if _blink_timer <= 0.0:
		_blink = 0.14
		_blink_timer = randf_range(2.0, 5.0)
	if _blink > 0.0:
		_blink -= delta
	# Antenna: a damped spring driven by acceleration (world space).
	var accel := (velocity - _last_velocity) / maxf(delta, 0.001)
	_last_velocity = velocity
	_antenna_vel += (-accel * 0.004 - _antenna_spring * 60.0 - _antenna_vel * 6.0) * delta
	_antenna_spring += _antenna_vel * delta
	# Scarf: lifts when falling or running fast, drops while rising.
	var scarf_target := clampf(-velocity.y * 0.016, -0.35, 0.45) + 0.18 * clampf(absf(velocity.x) / SPEED.x, 0.0, 1.0)
	_scarf_vel += ((scarf_target - _scarf_spring) * 40.0 - _scarf_vel * 7.0) * delta
	_scarf_spring += _scarf_vel * delta
	_apply_rig(delta, 0.1 if _blink > 0.0 else 1.0)


## Poses the procedural bones on top of the clip: eye scale (blink), jet
## flame size, antenna and scarf offsets.
func _apply_rig(_delta: float, eye_open: float, jets_on := true) -> void:
	if _skel == null:
		return
	for eye in ["eye_l", "eye_r"]:
		var i: int = _bones.get(eye, -1)
		if i >= 0:
			var sc := Vector3.ONE
			sc[_blink_axis[eye]] = eye_open
			_skel.set_bone_pose_scale(i, sc)
	var thrust := clampf(velocity.y / SPEED.y, 0.0, 1.0) if (not _at_floor and jets_on) else 0.0
	for jet in ["jet_l", "jet_r"]:
		var i: int = _bones.get(jet, -1)
		if i < 0:
			continue
		var sc := Vector3.ONE * 0.001
		if thrust > 0.05:
			sc = Vector3.ONE * (0.75 + 0.35 * thrust)
			sc[_jet_axis[jet]] = 0.5 + thrust * 0.9 + randf() * 0.25
		_skel.set_bone_pose_scale(i, sc)
	# Antenna: tip the chain away from the acceleration.
	var sideways := Vector3.UP.cross(Vector3(clampf(_antenna_spring.x, -0.7, 0.7), 0.0, 0.0))
	var tilt := sideways + model.global_basis.x.normalized() * clampf(_antenna_spring.y, -0.7, 0.7)
	_add_rotation(["antenna_1", "antenna_2", "antenna_3"], tilt, [0.55, 0.3, 0.25])
	var flutter := sin(Time.get_ticks_msec() / 1000.0 * 13.0) * 0.07 * clampf(absf(velocity.x) / SPEED.x + absf(velocity.y) / SPEED.y, 0.0, 1.0)
	var lift := model.global_basis.x.normalized() * (_scarf_spring + flutter)
	_add_rotation(["scarf_1", "scarf_2", "scarf_3"], lift, [0.5, 0.3, 0.3])


## Rotates each bone by `share` of the world-space rotation vector `rotvec`
## (axis * angle in radians), after the clip posed it.
func _add_rotation(bones: Array, rotvec: Vector3, shares: Array) -> void:
	var angle := rotvec.length()
	if angle < 0.0005:
		return
	var axis_skel := (_skel.global_basis.inverse() * (rotvec / angle)).normalized()
	for k in bones.size():
		var i: int = _bones.get(bones[k], -1)
		if i < 0:
			continue
		var local := (_skel.get_bone_global_pose(i).basis.inverse() * axis_skel).normalized()
		_skel.set_bone_pose_rotation(i, _skel.get_bone_pose_rotation(i) * Quaternion(local, angle * shares[k]))


func _advance_death(delta: float) -> void:
	if not _death_started:
		_death_started = true
		_hurt_time = 0.0
		_play("death")
	_death_progress += delta / DEATH_ANIMATION_TIME
	var t := minf(_death_progress, 1.0)
	model.visible = true
	model.scale = model.scale.lerp(Vector3.ONE, minf(1.0, delta * 10.0))
	shield_bubble.visible = false
	if _anim != null:
		_anim.speed_scale = 1.0
		_anim.advance(delta)
	# The eyes squeeze shut as it flops over.
	_apply_rig(delta, 1.0 - 0.9 * smoothstep(0.5, 0.6, t), false)
	if _death_progress >= 1.0:
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
	_hurt_time = 0.45
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
	_death_started = false
	set_process(true)
	model.position = Vector3.ZERO
	model.rotation = Vector3.ZERO
	model.scale = Vector3.ONE
	_squash = 1.0
	_hurt_time = 0.0
	_land_time = 0.0
	_jump_time = 0.0
	_antenna_spring = Vector3.ZERO
	_antenna_vel = Vector3.ZERO
	_clip = ""
	_play("idle", 0.0)
	if _anim != null:
		_anim.advance(0.0)
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
