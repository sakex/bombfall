extends Node
## Scene routing and the per-run state that outlives a scene swap.

const MENU_SCENE := "res://src/main/main_menu.tscn"
const GAME_SCENE := "res://src/game/game.tscn"
const TUTORIAL_SCENE := "res://src/game/tutorial.tscn"

## Coins a revive costs now that there is no rewarded ad to watch.
const REVIVE_COST := 250

var runs_this_session := 0

## Developer aid: `--screenshot=path.png[:seconds]` saves a frame and quits.
var _screenshot_path := ""
var _screenshot_at := 2.5
var _elapsed := 0.0


func _ready() -> void:
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--screenshot="):
			var spec := arg.trim_prefix("--screenshot=").split(":")
			_screenshot_path = spec[0]
			if spec.size() > 1:
				_screenshot_at = float(spec[1])
	set_process(_screenshot_path != "")


func _process(delta: float) -> void:
	_elapsed += delta
	if _elapsed >= _screenshot_at:
		var img := get_viewport().get_texture().get_image()
		img.save_png(_screenshot_path)
		print("SCREENSHOT ", _screenshot_path)
		get_tree().quit()


func go_to_menu() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file(MENU_SCENE)


func start_game() -> void:
	runs_this_session += 1
	if runs_this_session > 1 or not SaveData.first_launch:
		Services.ads.show_interstitial()
	get_tree().paused = false
	get_tree().change_scene_to_file(GAME_SCENE)


func start_tutorial() -> void:
	get_tree().paused = false
	get_tree().change_scene_to_file(TUTORIAL_SCENE)
