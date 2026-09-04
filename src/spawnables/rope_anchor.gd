extends StaticBody3D
## The hook a rope hangs from inside a wall. Explosions remove it.

func kill() -> void:
	queue_free()
