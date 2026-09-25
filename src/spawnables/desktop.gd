extends MultiBody
## The workstation: its screen (and the monitor's RGB strip) only glows
## while the monitor sits on the desk.

## [material, property, lit value] for every glowing surface of the monitor.
var _glow: Array = []

@onready var monitor: RigidBody3D = $Monitor
@onready var desk_area: Area3D = $Desk/MonitorArea


func _ready() -> void:
	super._ready()
	var mesh := monitor.find_child("monitor", true, false) as MeshInstance3D
	if mesh != null:
		for i in mesh.mesh.get_surface_count():
			var m := mesh.get_active_material(i)
			if m is ShaderMaterial:
				# The animated screen shader (shared between instances).
				var sm: ShaderMaterial = m.duplicate()
				mesh.set_surface_override_material(i, sm)
				_glow.append([sm, "energy", sm.get_shader_parameter("energy")])
			elif m is StandardMaterial3D and (m as StandardMaterial3D).emission_enabled:
				var std: StandardMaterial3D = m.duplicate()
				mesh.set_surface_override_material(i, std)
				_glow.append([std, "emission_energy_multiplier", std.emission_energy_multiplier])
	desk_area.body_entered.connect(_on_desk_body.bind(true))
	desk_area.body_exited.connect(_on_desk_body.bind(false))


func _on_desk_body(body: Node, on: bool) -> void:
	if body != monitor:
		return
	for g in _glow:
		var value: Variant = g[2] if on else 0.0
		if g[0] is ShaderMaterial:
			(g[0] as ShaderMaterial).set_shader_parameter(g[1], value)
		else:
			(g[0] as Material).set(g[1], value)
