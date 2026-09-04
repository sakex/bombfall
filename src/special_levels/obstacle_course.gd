class_name ObstacleCourse
extends Node3D
## A 37-row drop onto a solid floor. Reaching the bottom makes a tower of
## ledges appear above with a crate at the top and two wall guns covering
## it: climb for the reward while the bombs keep coming, or blast through.

const WALL_GUN := preload("res://src/spawnables/wall_gun.tscn")
const CRATE := preload("res://src/spawnables/crate.tscn")
## (x, top row, width) in cells, from the original 32 px tile map.
const LEDGES := [
	[3.0, 6.0, 1.0], [8.0, 9.5, 2.0], [0.5, 13.5, 1.0], [14.5, 14.0, 1.5],
	[1.0, 18.5, 4.5], [13.0, 18.5, 2.5], [11.0, 22.0, 1.0], [4.0, 24.5, 2.5],
	[12.5, 28.0, 1.0], [5.0, 31.0, 2.5], [0.5, 34.0, 2.0],
]

var coin_budget := 0
var _spawned := false

@onready var trigger: Area3D = $Trigger


func _ready() -> void:
	trigger.body_entered.connect(_on_trigger)


func _on_trigger(body: Node) -> void:
	if _spawned or not (body is Player):
		return
	_spawned = true
	for entry in LEDGES:
		add_child(Ledge.make(entry[0], -entry[1], entry[2]))
	var crate: Pickup = CRATE.instantiate()
	crate.coin_budget = coin_budget
	crate.position = Vector3(3.5, -6.0, 0.0)
	add_child(crate)
	var gun_a: WallGun = WALL_GUN.instantiate()
	gun_a.position = Vector3(1.0, -13.9, 0.0)
	add_child(gun_a)
	var gun_b: WallGun = WALL_GUN.instantiate()
	gun_b.rotation.z = -PI / 2.0
	gun_b.position = Vector3(2.4, -19.5, 0.0)
	add_child(gun_b)
