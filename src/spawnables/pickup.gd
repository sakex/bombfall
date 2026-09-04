class_name Pickup
extends PlanarBody
## A pedestal with a floating upgrade above it. Touch the item to take it.

enum Kind { SHIELD_BATTERY, SHIELD_CORE, MAGNET, CRATE }

const COIN := preload("res://src/actors/coin.tscn")

@export var kind: Kind = Kind.SHIELD_BATTERY
## Crates scatter 30 frozen coins worth this budget in total.
var coin_budget := 0

var _taken := false

@onready var item: Node3D = $Item
@onready var item_area: Area3D = $Item/Area


func _ready() -> void:
	add_to_group("pickups")
	item_area.body_entered.connect(_on_body)


func _process(delta: float) -> void:
	if _taken:
		return
	item.rotation.y += delta * 1.5
	item.position.y = 2.1 + sin(Time.get_ticks_msec() / 1000.0 * 2.0) * 0.12


func _on_body(body: Node) -> void:
	if _taken or not (body is Player):
		return
	_taken = true
	match kind:
		Kind.SHIELD_BATTERY:
			body.increment_shield()
		Kind.SHIELD_CORE:
			body.increment_max_shield()
		Kind.MAGNET:
			body.increase_magnet()
		Kind.CRATE:
			body.increment_shield(2)
			_spawn_coins()
	item.queue_free()


func _spawn_coins() -> void:
	var each := int(ceil(float(coin_budget) * 5.0 / 30.0))
	var parent := get_parent()
	for i in 6:
		for j in 5:
			var coin: Coin = COIN.instantiate()
			coin.value = each
			coin.position = global_position + Vector3(i * 1.1 - 2.75, 3.0 + j * 1.1, 0.0)
			coin.freeze_for(2.0)
			parent.add_child(coin)
