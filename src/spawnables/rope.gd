class_name Rope
extends Node3D
## A chain of links pinned end to end. Grows from its origin towards -X until
## it hits a wall (or for [member chains] links), hooks its tail to an anchor
## in that wall and its head to whatever [method connect_head] was given.
## The anchor is killable: blow up the wall and the rope swings free.

const LINK := preload("res://src/spawnables/rope_link.tscn")
const LINK_LENGTH := 1.0
const MAX_LENGTH := 16.0

@export var chains := 1
@export var expand_until_wall := false
@export var unbreakable := false
@export var no_collisions := false

var _head: PhysicsBody3D = null
var _tail: PhysicsBody3D = null
var _links: Array[RopeLink] = []
var _built := false


func connect_head(body: PhysicsBody3D) -> void:
	_head = body
	if _built:
		_pin_head()


func connect_tail(body: PhysicsBody3D) -> void:
	_tail = body
	if _built:
		_pin_tail()


func _physics_process(_delta: float) -> void:
	if _built:
		set_physics_process(false)
		return
	_build()


func _build() -> void:
	_built = true
	var count := chains
	var anchor_x := -1.0
	if expand_until_wall:
		var space := get_world_3d().direct_space_state
		var query := PhysicsRayQueryParameters3D.create(global_position, global_position + Vector3(-MAX_LENGTH, 0, 0), Layers.WORLD)
		var hit := space.intersect_ray(query)
		if hit.is_empty():
			count = int(MAX_LENGTH)
		else:
			var distance: float = global_position.distance_to(hit["position"])
			count = maxi(int(round(distance / LINK_LENGTH)), 1)
			anchor_x = -distance
	for i in count:
		var link: RopeLink = LINK.instantiate()
		link.unbreakable = unbreakable
		link.position = Vector3(-(i + 0.5) * LINK_LENGTH, 0.0, 0.0)
		if no_collisions:
			link.collision_layer = 0
			link.collision_mask = 0
		add_child(link)
		_links.append(link)
	for i in range(1, _links.size()):
		_links[i].joint = _pin(_links[i - 1], _links[i], Vector3(-i * LINK_LENGTH, 0.0, 0.0))
	if expand_until_wall:
		var anchor := StaticBody3D.new()
		anchor.set_script(load("res://src/spawnables/rope_anchor.gd"))
		anchor.collision_layer = Layers.POLE
		anchor.collision_mask = 0
		var shape := CollisionShape3D.new()
		var box := BoxShape3D.new()
		box.size = Vector3(0.6, 0.6, 0.6)
		shape.shape = box
		anchor.add_child(shape)
		anchor.position = Vector3(anchor_x if anchor_x < 0.0 else -count * LINK_LENGTH, 0.0, 0.0)
		add_child(anchor)
		_tail = anchor
	_pin_head()
	_pin_tail()


func _pin(a: PhysicsBody3D, b: PhysicsBody3D, local_pos: Vector3) -> PinJoint3D:
	var joint := PinJoint3D.new()
	joint.position = local_pos
	add_child(joint)
	joint.node_a = joint.get_path_to(a)
	joint.node_b = joint.get_path_to(b)
	return joint


func _pin_head() -> void:
	if _head != null and not _links.is_empty():
		_links[0].joint = _pin(_head, _links[0], Vector3.ZERO)


func _pin_tail() -> void:
	if _tail != null and not _links.is_empty():
		_pin(_links.back(), _tail, Vector3(-_links.size() * LINK_LENGTH, 0.0, 0.0))


func kill() -> void:
	queue_free()
