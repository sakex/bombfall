extends AudioStreamPlayer
## Background music that keeps playing across scene changes.
## Picks a random start track and cycles through the playlist.

const PLAYLIST := [
	"res://assets/audio/music/After The War.mp3",
	"res://assets/audio/music/City of Drones.mp3",
	"res://assets/audio/music/darksynth.mp3",
	"res://assets/audio/music/oren.mp3",
	"res://assets/audio/music/Rise of the Machines.mp3",
	"res://assets/audio/music/Galaxy.mp3",
	"res://assets/audio/music/Hackers.mp3",
	"res://assets/audio/music/LastStop.mp3",
	"res://assets/audio/music/blacktar.mp3",
]

var _next := 0


func _ready() -> void:
	bus = &"music"
	process_mode = Node.PROCESS_MODE_ALWAYS
	_next = randi() % PLAYLIST.size()
	finished.connect(_play_next)
	_play_next()


func _play_next() -> void:
	stream = load(PLAYLIST[_next])
	_next = (_next + 1) % PLAYLIST.size()
	play()
