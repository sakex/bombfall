extends SceneTree
var n: Node3D
var t := 0.0
var played := false
func _initialize():
	n = load("res://src/spawnables/wall_gun.tscn").instantiate()
	root.add_child(n)
func _process(delta):
	t += delta
	var m: Node3D = n.get_node("Model")
	var flare: Node3D = m.find_child("flare", true, false)
	var barrel: Node3D = m.find_child("barrel", true, false)
	if t > 0.3 and not played:
		played = true
		print("play ->", ModelUtil.play(m, "fire"), " current=", ModelUtil.anim_player(m).current_animation)
	if played and t < 0.8:
		var ap := ModelUtil.anim_player(m)
		print("t=%.2f anim=%s pos=%.2f flare=%s barrel=%s" % [t, ap.current_animation, ap.current_animation_position, flare.scale, barrel.position])
	if t > 0.8:
		quit()
	return false
