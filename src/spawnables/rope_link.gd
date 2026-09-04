class_name RopeLink
extends PlanarBody
## One link of a rope. Lasers call [method turn_off] to cut it loose.

var unbreakable := false
var joint: PinJoint3D = null


func turn_off() -> void:
	if unbreakable or joint == null or not is_instance_valid(joint):
		return
	joint.queue_free()
	joint = null
