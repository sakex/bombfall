class_name Killable
extends Node3D
## A non-physics node that can still be destroyed by an explosion.

var killed := false


func kill() -> void:
	if killed:
		return
	killed = true
	queue_free()
