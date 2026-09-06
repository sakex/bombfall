extends PlanarBody
## Crystal blocks left behind by the bat boss's shots; they melt after a while.

@export var lifetime := 10.0
## The ladder crystals the arena grows survive blasts.
@export var indestructible := false


func _ready() -> void:
	add_to_group("boss_blocks")
	if lifetime > 0.0:
		get_tree().create_timer(lifetime).timeout.connect(queue_free)


func kill() -> void:
	if indestructible:
		return
	super()
