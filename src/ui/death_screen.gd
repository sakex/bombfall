class_name DeathScreen
extends Control
## Shown when the run ends: retry, revive (for coins), or back to the menu.

signal retry
signal revive
signal main_menu

@onready var score_label: Label = %ScoreLabel
@onready var best_label: Label = %BestLabel
@onready var revive_button: Button = %ReviveButton
@onready var retry_button: Button = %RetryButton
@onready var menu_button: Button = %MenuButton


func _ready() -> void:
	visible = false
	retry_button.pressed.connect(func(): retry.emit())
	revive_button.pressed.connect(func(): revive.emit())
	menu_button.pressed.connect(func(): main_menu.emit())


func show_game_over(score: int, can_revive: bool) -> void:
	score_label.text = "SCORE %d" % score
	best_label.text = "BEST %d" % int(SaveData.data["max_score"]["score"])
	revive_button.visible = can_revive
	revive_button.text = "revive (%d coins)" % Game.REVIVE_COST
	revive_button.disabled = not SaveData.can_afford(Game.REVIVE_COST)
	visible = true
