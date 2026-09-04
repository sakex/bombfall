class_name RopedProp
extends Killable
## A prop hung on one or two ropes: ropes are the "Rope*" children, the prop
## is the first physics body child.


func _ready() -> void:
	var body: PhysicsBody3D = null
	for child in get_children():
		if child is PhysicsBody3D:
			body = child
			break
	if body == null:
		return
	for child in get_children():
		if child is Rope:
			child.connect_head(body)


func kill() -> void:
	for child in get_children():
		if child.has_method("kill"):
			child.kill()
	super.kill()
