class_name GameScene
extends Node3D
## A run of the game: world, player, camera and the overlays.

@export var record_scores := true
## Scene loaded by "retry" (the tutorial restarts itself).
@export var retry_scene := "res://src/game/game.tscn"
@export var allow_revive := true

var _revived := false
var _score_recorded := false

@onready var world: World = $World
@onready var player: Player = $Player
@onready var rig: CameraRig = $CameraRig
@onready var hud: Hud = $Hud
@onready var death_screen: DeathScreen = $Overlays/DeathScreen
@onready var pause_screen: PauseScreen = $Overlays/PauseScreen


func _ready() -> void:
	get_tree().paused = false
	var data := SaveData.data
	player.set_max_shields(int(data["max_shields"]))
	player.set_active_shields(int(data["base_shields"]))
	player.set_magnets(int(data["magnets"]))
	player.position = Vector3(Grid.CENTER_X, 0.0, 0.0)
	player.died.connect(_on_player_died)
	world.tracked = player
	rig.target = player
	rig.snap()
	hud.bind_player(player)
	hud.pause_pressed.connect(_pause)
	death_screen.retry.connect(_retry)
	death_screen.revive.connect(_revive)
	death_screen.main_menu.connect(_to_menu)
	pause_screen.retry.connect(_retry)
	pause_screen.main_menu.connect(_to_menu)


func _unhandled_input(event: InputEvent) -> void:
	if event.is_action_pressed("pause") and not pause_screen.visible and not death_screen.visible:
		_pause()


func _pause() -> void:
	if death_screen.visible:
		return
	pause_screen.open()


func _on_player_died(score: int) -> void:
	get_tree().paused = true
	var previous_best := int(SaveData.data["max_score"]["score"])
	_record(score)
	death_screen.show_game_over(score, allow_revive, maxi(int(-player.position.y), 0), previous_best)


func _record(score: int) -> void:
	if not record_scores:
		return
	SaveData.record_score(score, _score_recorded)
	_score_recorded = true


func _revive() -> void:
	if not SaveData.can_afford(Game.REVIVE_COST):
		return
	SaveData.data["coins"] -= Game.REVIVE_COST
	SaveData.save()
	_revived = true
	death_screen.visible = false
	get_tree().paused = false
	player.revive()


func _retry() -> void:
	_save_partial()
	if retry_scene == Game.GAME_SCENE:
		Game.start_game()
	else:
		get_tree().paused = false
		get_tree().change_scene_to_file(retry_scene)


func _to_menu() -> void:
	_save_partial()
	Game.go_to_menu()


## Leaving mid-run still banks the coins collected so far.
func _save_partial() -> void:
	if not death_screen.visible:
		_record(player.score)
