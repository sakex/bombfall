extends Node
## Headless check of the hazards' rigs and clips (blender/hazards.py):
##   godot --headless --path . res://src/dev/haz_probe.tscn
## Kills the bat boss's heart and reports its jaw bone (the jaw must drop:
## the direction's y goes down), its clips, and runs each gadget's one-shot.

var _bat: Node
var _t := 0.0
var _stage := 0


func _ready() -> void:
	_bat = load("res://src/special_levels/boss_bat.tscn").instantiate()
	add_child(_bat)
	for scene in ["wall_gun", "bumper", "trampoline"]:
		var n: Node3D = load("res://src/spawnables/%s.tscn" % scene).instantiate()
		add_child(n)
		var clip: String = {"wall_gun": "fire", "bumper": "hit", "trampoline": "bounce"}[scene]
		print("HAZ_PROBE %s play %s -> %s" % [scene, clip, ModelUtil.play(n.get_node("Model"), clip)])


func _process(delta: float) -> void:
	_t += delta
	var sk: Skeleton3D = _bat.get_node("Model").find_children("*", "Skeleton3D", true, false)[0]
	var jaw := sk.find_bone("jaw")
	if _stage == 0:
		_stage = 1
		print("HAZ_PROBE bat clips=%s jaw rest dir=%s" % [ModelUtil.anim_player(_bat.get_node("Model")).get_animation_list(), sk.get_bone_global_pose(jaw).basis.y])
	elif _stage == 1 and _t > 0.3:
		_stage = 2
		_bat.set_dying()
		_bat.freeze = true
	elif _stage == 2 and _t > 1.0:
		print("HAZ_PROBE bat dying jaw dir=%s clip=%s" % [sk.get_bone_global_pose(jaw).basis.y, ModelUtil.anim_player(_bat.get_node("Model")).current_animation])
		get_tree().quit()
