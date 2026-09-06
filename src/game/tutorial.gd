extends GameScene
## The guided first run: the same hotel, no bombs until the player has
## learned to move, jump, push, shield up and collect coins.

const TOILET := preload("res://src/spawnables/toilet.tscn")
const BATTERY := preload("res://src/spawnables/shield_battery.tscn")
const CORE := preload("res://src/spawnables/shield_core.tscn")
const COIN := preload("res://src/actors/coin.tscn")

const STEPS := [
	"Touch the left half of the screen and slide to run. Tap to one side of where your thumb was to dash that way at once.",
	"Tap anywhere on the bottom right of the screen to jump. Hold it to jump higher.",
	"Everything can be pushed and destroyed. Try pushing the toilet!",
	"Your shields are the bar at the top of the screen. Grab the shield cell to charge one.",
	"Shield cores raise your maximum number of shields. Grab it!",
	"Coins raise your score and buy upgrades in the store. Shinier coins are worth more.",
	"Bombs fall from above. Use their blasts to blow holes through the floors, but do not get caught in them!",
]

var _step := -1
var _pressed_left := false
var _pressed_right := false
var _toilet: Node3D = null
var _toilet_origin := Vector3.ZERO

@onready var popup: PanelContainer = %TutorialPopup
@onready var instruction: Label = %Instruction
@onready var start_button: Button = %StartButton


func _ready() -> void:
	record_scores = false
	retry_scene = Game.TUTORIAL_SCENE
	allow_revive = false
	super._ready()
	world.is_preview = true
	popup.visible = false
	start_button.visible = false
	start_button.pressed.connect(_start_run)
	SaveData.mark_tutorial_offered()


func _process(_delta: float) -> void:
	if _step < 0:
		if player.is_on_floor():
			_show_step(0)
		return
	match _step:
		0:
			_pressed_left = _pressed_left or Input.is_action_pressed("move_left")
			_pressed_right = _pressed_right or Input.is_action_pressed("move_right")
			if _pressed_left and _pressed_right:
				_show_step(1)
		1:
			if Input.is_action_just_pressed("jump"):
				_toilet = _spawn_on_floor(TOILET, 3.5)
				_toilet_origin = _toilet.position
				_show_step(2)
		2:
			if not is_instance_valid(_toilet) or _toilet.position.distance_to(_toilet_origin) > 3.0:
				_spawn_on_floor(BATTERY, -3.5)
				_show_step(3)
		3:
			if player.active_shields > 0:
				_spawn_on_floor(CORE, 4.0)
				_show_step(4)
		4:
			if player.max_shields > 1:
				_spawn_coin_row()
				_show_step(5)
		5:
			if player.score >= 100:
				_show_step(6)
				start_button.visible = true


func _show_step(step: int) -> void:
	_step = step
	instruction.text = STEPS[step]
	popup.visible = true


## Places a scene on the floor of the player's storey, `dx` metres away
## (flipped when that would land in a wall).
func _spawn_on_floor(scene: PackedScene, dx: float) -> Node3D:
	var x := player.position.x + dx
	if x < 2.5 or x > 14.5:
		x = player.position.x - dx
	var node: Node3D = scene.instantiate()
	node.position = Vector3(x, world.floor_y_at(player.position.y) + 0.05, 0.0)
	world.add_spawned(node, null)
	return node


func _spawn_coin_row() -> void:
	var y := world.floor_y_at(player.position.y) + 3.0
	for i in 15:
		if i == 5:
			continue
		var coin: Coin = COIN.instantiate()
		coin.value = i
		coin.position = Vector3(1.5 + i * 0.95, y, 0.0)
		world.add_spawned(coin, null)


func _start_run() -> void:
	popup.visible = false
	player.increment_score(-100)
	world.is_preview = false
	record_scores = true
