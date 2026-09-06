class_name FireZone
extends PlanarBody
## A falling fireball dropped when bombs come too fast. Burns the first ten
## things it touches, then burns out.

const MAX_KILLS := 10

var _kills: Array[Node] = []

@onready var model: Node3D = $Model
@onready var burn_area: Area3D = $BurnArea


func _ready() -> void:
	add_to_group("props")
	burn_area.body_entered.connect(_on_body)
	burn_area.area_entered.connect(_on_body)


func _process(_delta: float) -> void:
	var t := Time.get_ticks_msec() / 1000.0
	model.scale = Vector3(1.0 + 0.08 * sin(t * 13.0), 1.0 + 0.12 * sin(t * 9.0 + 1.0), 1.0)
	model.rotation.y = sin(t * 3.0) * 0.4


func _on_body(body: Node) -> void:
	if body == self or not body.has_method("kill"):
		return
	body.call_deferred("kill")
	Sfx.play("fire")
	if not _kills.has(body):
		_kills.append(body)
		if _kills.size() >= MAX_KILLS:
			queue_free()
