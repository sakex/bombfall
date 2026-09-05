extends Prop
## An arcade cabinet whose screen keeps playing attract mode.

var _screen: StandardMaterial3D
var _marquee: StandardMaterial3D


func _ready() -> void:
	super._ready()
	_screen = ModelUtil.own_material(ModelUtil.find_mesh(model, "screen"))
	_marquee = ModelUtil.own_material(ModelUtil.find_mesh(model, "marquee"))


func _process(_delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0 + position.x
	if _screen != null:
		_screen.emission = Color.from_hsv(fmod(t * 0.15, 1.0), 0.7, 1.0)
		_screen.emission_energy_multiplier = 1.5 + 0.8 * absf(sin(t * 5.0))
	if _marquee != null:
		_marquee.emission_energy_multiplier = 2.0 + 2.0 * float(fmod(t * 3.0, 1.0) < 0.5)
