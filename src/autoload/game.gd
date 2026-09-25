extends Node
## Scene routing and the per-run state that outlives a scene swap.

const MENU_SCENE := "res://src/main/main_menu.tscn"
const GAME_SCENE := "res://src/game/game.tscn"
const TUTORIAL_SCENE := "res://src/game/tutorial.tscn"

## Coins a revive costs now that there is no rewarded ad to watch.
const REVIVE_COST := 250

var runs_this_session := 0
var _fade: ColorRect


func _ready() -> void:
	get_tree().node_added.connect(_on_node_added)
	var layer := CanvasLayer.new()
	layer.layer = 100
	add_child(layer)
	_fade = ColorRect.new()
	_fade.color = Color(0.03, 0.01, 0.05, 1.0)
	_fade.set_anchors_and_offsets_preset(Control.PRESET_FULL_RECT)
	_fade.mouse_filter = Control.MOUSE_FILTER_IGNORE
	layer.add_child(_fade)
	get_tree().process_frame.connect(func(): _fade_from_black(), CONNECT_ONE_SHOT)
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screenshot="):
			var spec := arg.trim_prefix("--screenshot=").split(":")
			_screenshot_path = spec[0]
			if spec.size() > 1:
				_screenshot_at = float(spec[1])
	set_process(_screenshot_path != "")


func _fade_from_black() -> void:
	_fade.modulate.a = 1.0
	var t := create_tween()
	t.tween_property(_fade, "modulate:a", 0.0, 0.45)


## Fades to black, runs [param during] while the screen is dark, fades back.
func blink(during: Callable, hold := 0.15) -> void:
	var t := create_tween()
	t.tween_property(_fade, "modulate:a", 1.0, 0.25)
	await t.finished
	during.call()
	await get_tree().create_timer(hold).timeout
	_fade_from_black()


## Fades to black, switches scene, fades back in.
func _switch(path: String) -> void:
	get_tree().paused = false
	var t := create_tween()
	t.tween_property(_fade, "modulate:a", 1.0, 0.25)
	await t.finished
	get_tree().change_scene_to_file(path)
	await get_tree().process_frame
	_fade_from_black()

## Developer aid: `--screenshot=path.png[:seconds]` saves a frame and quits.
var _screenshot_path := ""
var _screenshot_at := 2.5
var _elapsed := 0.0


func _process(delta: float) -> void:
	_elapsed += delta
	if _elapsed >= _screenshot_at:
		var img := get_viewport().get_texture().get_image()
		img.save_png(_screenshot_path)
		print("SCREENSHOT ", _screenshot_path)
		get_tree().quit()


func go_to_menu() -> void:
	_switch(MENU_SCENE)


func start_game() -> void:
	runs_this_session += 1
	if runs_this_session > 1 or not SaveData.first_launch:
		Services.ads.show_interstitial()
	_switch(GAME_SCENE)


func start_tutorial() -> void:
	_switch(TUTORIAL_SCENE)


## Every imported model's AnimationPlayer starts its "idle" clip on its own:
## the Blender scripts author ambient motion (rotors, blinking, breathing) as
## an "idle" clip, and this loops it with a random phase so identical props
## do not move in lockstep. See ModelUtil.prepare_animations.
func _on_node_added(node: Node) -> void:
	if node is MeshInstance3D and node.owner != null and node.owner.scene_file_path.ends_with(".glb"):
		ModelUtil.animate_materials(node)
	elif node is AnimationPlayer and node.owner != null and node.owner.scene_file_path.ends_with(".glb"):
		ModelUtil.prepare_animations(node as AnimationPlayer)
		if (node as AnimationPlayer).has_animation("idle"):
			_start_idle.call_deferred(node)


func _start_idle(player: AnimationPlayer) -> void:
	if not is_instance_valid(player) or not player.is_inside_tree() or player.is_playing():
		return
	player.play("idle")
	player.seek(randf() * player.current_animation_length, true)
