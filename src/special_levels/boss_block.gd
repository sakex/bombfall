extends PlanarBody
## Crystal blocks left behind by the bat boss's shots; they melt after a while.

@export var lifetime := 10.0


func _ready() -> void:
	if lifetime > 0.0:
		get_tree().create_timer(lifetime).timeout.connect(queue_free)
