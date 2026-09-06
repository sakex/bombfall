extends Node
## One-line sound effects from anywhere: `Sfx.play("jump")`. A small pool of
## players on the sfx bus, a little random pitch so repeats do not machine-gun,
## and every button in the game clicks without wiring anything up.

const POOL_SIZE := 14
## name -> [path, volume dB, pitch jitter]
const SOUNDS := {
	"jump": ["res://assets/audio/sfx/jump.wav", -6.0, 0.08],
	"land": ["res://assets/audio/sfx/land.wav", -8.0, 0.12],
	"step": ["res://assets/audio/sfx/step.wav", -14.0, 0.2],
	"coin": ["res://assets/audio/sfx/coin.wav", -4.0, 0.1],
	"hit": ["res://assets/audio/sfx/hit.wav", -2.0, 0.05],
	"death": ["res://assets/audio/sfx/death.wav", 0.0, 0.0],
	"start": ["res://assets/audio/sfx/start.wav", -3.0, 0.0],
	"click": ["res://assets/audio/sfx/click.wav", -8.0, 0.05],
	"swoosh": ["res://assets/audio/sfx/swoosh.wav", -10.0, 0.1],
	"shield_battery_up": ["res://assets/audio/sfx/shield_battery_up.wav", -4.0, 0.0],
	"shield_core_up": ["res://assets/audio/sfx/shield_core_up.wav", -3.0, 0.0],
	"magnet_up": ["res://assets/audio/sfx/magnet_up.wav", -5.0, 0.0],
	"doubler_up": ["res://assets/audio/sfx/doubler_up.wav", -4.0, 0.0],
	"crate_open": ["res://assets/audio/sfx/crate_open.wav", -3.0, 0.05],
	"bumper": ["res://assets/audio/sfx/bumper.wav", -4.0, 0.1],
	"slot_spin": ["res://assets/audio/sfx/slot_spin.wav", -8.0, 0.0],
	"slot_win": ["res://assets/audio/sfx/slot_win.wav", -3.0, 0.0],
	"plasma": ["res://assets/audio/sfx/plasma.wav", -7.0, 0.1],
	"laser_on": ["res://assets/audio/sfx/laser_on.wav", -8.0, 0.05],
	"fire": ["res://assets/audio/sfx/fire.wav", -6.0, 0.1],
	"vault_crack": ["res://assets/audio/sfx/vault_crack.wav", -2.0, 0.0],
	"steel_hit": ["res://assets/audio/sfx/steel_hit.wav", -9.0, 0.15],
	"door": ["res://assets/audio/sfx/door.wav", -3.0, 0.0],
	"bat": ["res://assets/audio/sfx/bat.wav", -4.0, 0.1],
	"heart": ["res://assets/audio/sfx/heart.wav", -2.0, 0.0],
	"metal_bounce": ["res://assets/audio/sfx/metal_bounce.wav", -8.0, 0.15],
}

var _streams: Dictionary = {}
var _pool: Array[AudioStreamPlayer] = []
var _next := 0


func _ready() -> void:
	process_mode = Node.PROCESS_MODE_ALWAYS
	for name in SOUNDS:
		_streams[name] = load(SOUNDS[name][0])
	for i in POOL_SIZE:
		var p := AudioStreamPlayer.new()
		p.bus = &"sfx"
		add_child(p)
		_pool.append(p)
	get_tree().node_added.connect(_on_node_added)


## Plays a named effect; [param pitch] scales the random jitter, [param db]
## offsets the table volume.
func play(name: String, pitch := 1.0, db := 0.0) -> void:
	if not _streams.has(name):
		push_warning("Sfx: unknown sound " + name)
		return
	var spec: Array = SOUNDS[name]
	var p := _pool[_next]
	_next = (_next + 1) % POOL_SIZE
	p.stream = _streams[name]
	p.volume_db = spec[1] + db
	p.pitch_scale = pitch * (1.0 + randf_range(-spec[2], spec[2]))
	p.play()


## Every button clicks.
func _on_node_added(node: Node) -> void:
	if node is BaseButton:
		(node as BaseButton).pressed.connect(func(): play("click"))
