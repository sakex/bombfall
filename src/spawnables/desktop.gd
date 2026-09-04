extends MultiBody
## The workstation: its screen only glows while the monitor sits on the desk.

var _screen_material: StandardMaterial3D

@onready var monitor: RigidBody3D = $Monitor
@onready var desk_area: Area3D = $Desk/MonitorArea


func _ready() -> void:
	super._ready()
	var mesh := monitor.find_child("monitor", true, false) as MeshInstance3D
	if mesh != null:
		# The screen is the emissive cyan surface of the monitor mesh.
		for i in mesh.mesh.get_surface_count():
			var m := mesh.mesh.surface_get_material(i) as StandardMaterial3D
			if m != null and m.emission_enabled and m.emission.b > 0.8 and m.emission.g > 0.8 and m.emission.r < 0.4:
				_screen_material = m.duplicate()
				mesh.set_surface_override_material(i, _screen_material)
				break
	desk_area.body_entered.connect(_on_desk_body.bind(true))
	desk_area.body_exited.connect(_on_desk_body.bind(false))


func _on_desk_body(body: Node, on: bool) -> void:
	if body == monitor and _screen_material != null:
		_screen_material.emission_energy_multiplier = 2.0 if on else 0.0
