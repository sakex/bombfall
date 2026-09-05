class_name VaultLevel
extends Node3D
## The vault: a slab of steel cells seals the shaft under a giant safe
## door. Steel takes three blasts, so it takes a few bombs to crack it;
## the treasure room below is packed with coins, a crate and a doubler.

const COIN := preload("res://src/actors/coin.tscn")
const CRATE := preload("res://src/spawnables/crate.tscn")
const DOUBLER := preload("res://src/spawnables/doubler.tscn")
const SLAB_ROW := 9
const FLOOR_ROW := 19

var coin_budget := 0
var _world: Node = null
var _cracked := false
var _lock: StandardMaterial3D
var _wheel: Node3D

@onready var door: Node3D = $Door


func _ready() -> void:
	_lock = ModelUtil.own_material(ModelUtil.find_mesh(door, "lock_light"))
	_wheel = door.find_child("wheel", true, false)


func set_world(world: Node) -> void:
	_world = world
	call_deferred("_build")


func _build() -> void:
	var roof := Grid.row_of(global_position.y)
	for cx in range(1, Grid.WALL_RIGHT):
		_world.cells.set_cell(cx, roof + SLAB_ROW, CellGrid.Kind.STEEL)
		_world.cells.set_cell(cx, roof + SLAB_ROW + 1, CellGrid.Kind.STEEL)
	# Treasure room.
	for i in 10:
		for j in 3:
			var coin: Coin = COIN.instantiate()
			coin.value = maxi(coin_budget / 4, 1)
			coin.position = Vector3(3.0 + i * 1.1, -(SLAB_ROW + 4.0 + j * 1.2), 0.0)
			add_child(coin)
	var crate: Pickup = CRATE.instantiate()
	crate.coin_budget = coin_budget
	crate.position = Vector3(5.0, -(FLOOR_ROW), 0.0)
	add_child(crate)
	var doubler: Pickup = DOUBLER.instantiate()
	doubler.position = Vector3(12.0, -(FLOOR_ROW), 0.0)
	add_child(doubler)


func _process(delta: float) -> void:
	if _wheel != null:
		_wheel.rotation.z += delta * (0.4 if not _cracked else 3.0)
	if not _cracked and _world != null:
		var roof := Grid.row_of(global_position.y)
		var intact := 0
		for cx in range(1, Grid.WALL_RIGHT):
			if _world.cells.has_cell(cx, roof + SLAB_ROW + 1):
				intact += 1
		if intact < Grid.WALL_RIGHT - 1:
			_cracked = true
			if _lock != null:
				_lock.emission = Color(0.2, 1.0, 0.4)
				_lock.emission_energy_multiplier = 5.0
