class_name LightRing
extends PlanarBody
## A portal ring that charges up, then sweeps a laser across the room for a
## few seconds. The laser detonates bombs and cuts drones and ropes loose.

const CHARGE_TIME := 1.0
const LASER_ON_TIME := 0.8
const OFF_TIME := 3.0
const ON_TIME := 4.0
const BEAM_LENGTH := 14.0

## Fires to the right instead of the left (rings on the left half do this).
var flipped := false:
	set(value):
		flipped = value
		if is_node_ready():
			_apply_flip()

var _active := false
var _charge := 0.0
var _laser_on := false
var _beam := 0.0
var _glow: StandardMaterial3D

@onready var model: Node3D = $Model
@onready var laser: Area3D = $Laser
@onready var laser_shape: CollisionShape3D = $Laser/Shape
@onready var beam_mesh: MeshInstance3D = $Laser/Beam
@onready var timer: Timer = $Timer


func _ready() -> void:
	add_to_group("props")
	gravity_scale = 0.78
	_glow = ModelUtil.own_material(ModelUtil.find_mesh(model, "glow"))
	timer.timeout.connect(_toggle)
	timer.start(OFF_TIME)
	_apply_flip()
	_set_beam(0.0)


func _apply_flip() -> void:
	model.scale.x = -1.0 if flipped else 1.0
	laser.scale.x = -1.0 if flipped else 1.0


func _toggle() -> void:
	_active = not _active
	if _active:
		timer.start(ON_TIME)
	else:
		_laser_on = false
		_charge = 0.0
		if _glow != null:
			_glow.emission_energy_multiplier = 1.0
		timer.start(OFF_TIME)


func _physics_process(delta: float) -> void:
	if _active:
		if _charge < 1.0:
			_charge = minf(_charge + delta / CHARGE_TIME, 1.0)
			if _glow != null:
				_glow.emission_energy_multiplier = 1.0 + 7.0 * _charge
				_glow.emission = Color(0.6, 0.3, 1.0).lerp(Color(1.0, 0.25, 0.6), _charge)
		else:
			_laser_on = true
	if _laser_on and _beam < 1.0:
		_set_beam(minf(_beam + delta / LASER_ON_TIME, 1.0))
	elif not _laser_on and _beam > 0.0:
		_set_beam(maxf(_beam - delta / LASER_ON_TIME, 0.0))
	if _beam <= 0.0:
		return
	for body in laser.get_overlapping_bodies():
		if body is Bomb:
			body.call_deferred("kill")
		elif body.has_method("turn_off"):
			body.call_deferred("turn_off")


func _set_beam(amount: float) -> void:
	_beam = amount
	var length := BEAM_LENGTH * amount
	laser_shape.disabled = amount <= 0.0
	(laser_shape.shape as BoxShape3D).size = Vector3(maxf(length, 0.05), 0.5, 0.5)
	laser_shape.position.x = -length * 0.5
	beam_mesh.visible = amount > 0.0
	beam_mesh.scale = Vector3(maxf(length, 0.01), 1.0, 1.0)
	beam_mesh.position.x = -length * 0.5
