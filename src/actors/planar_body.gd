class_name PlanarBody
extends RigidBody3D
## A rigid body confined to the XY plane: the hotel is 3D to look at but the
## game still plays on a 2D slice, exactly like the original.
##
## Also carries the shared "kill" contract: explosions, lasers and fire call
## [method kill] on anything they touch; most props simply vanish.

var killed := false


func _init() -> void:
	axis_lock_linear_z = true
	axis_lock_angular_x = true
	axis_lock_angular_y = true


func kill() -> void:
	if killed:
		return
	killed = true
	_on_killed()
	queue_free()


## Hook for subclasses that need effects before disappearing.
func _on_killed() -> void:
	pass
