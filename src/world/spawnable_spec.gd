class_name SpawnableSpec
extends RefCounted
## Describes one thing the generator can place in a level: which scene,
## where it may go, how many cells it occupies and how "dangerous" it is.
## Mirrors the Rust `Spawnable` trait of the original.

enum Where { FLOOR, LEFT_WALL, RIGHT_WALL, ROOF, FLOATING }
enum Anchor { BOTTOM, CENTER }

var id: String
var scene_path: String
var on_floor := false
var on_wall := false
var on_roof := false
var floating := false
var size := Vector2i(1, 1)          ## footprint in cells (width, height)
var difficulty := 1
var max_per_level := 1
## Level-bound props vanish with their level; world-bound ones are garbage
## collected once they are far above the player (they may have fallen).
var bound_to_level := false
var invert_on_walls := false
var anchor := Anchor.BOTTOM
## Optional: func(node: Node3D, where: int, rect: Rect2i) for custom placement.
var placer: Callable
## Properties assigned to the instance right after instantiation.
var extra: Dictionary = {}

var _packed: PackedScene


func _init(p_id: String, p_scene: String, p_size: Vector2i, p_difficulty: int) -> void:
	id = p_id
	scene_path = p_scene
	size = p_size
	difficulty = p_difficulty


# Builder-style helpers keep the registry table readable.
func floor() -> SpawnableSpec:
	on_floor = true
	return self


func wall() -> SpawnableSpec:
	on_wall = true
	return self


func roof() -> SpawnableSpec:
	on_roof = true
	return self


func float_() -> SpawnableSpec:
	floating = true
	anchor = Anchor.CENTER
	return self


func centered() -> SpawnableSpec:
	anchor = Anchor.CENTER
	return self


func per_level(n: int) -> SpawnableSpec:
	max_per_level = n
	return self


func level_bound() -> SpawnableSpec:
	bound_to_level = true
	return self


func invert() -> SpawnableSpec:
	invert_on_walls = true
	return self


func with(props: Dictionary) -> SpawnableSpec:
	extra = props
	return self


func placed_by(fn: Callable) -> SpawnableSpec:
	placer = fn
	return self


func where_options() -> Array[int]:
	var out: Array[int] = []
	if on_floor:
		out.append(Where.FLOOR)
	if on_wall:
		out.append(Where.LEFT_WALL)
		out.append(Where.RIGHT_WALL)
	if on_roof:
		out.append(Where.ROOF)
	if floating:
		out.append(Where.FLOATING)
	return out


static func is_wall(where: int) -> bool:
	return where == Where.LEFT_WALL or where == Where.RIGHT_WALL


func footprint(where: int) -> Vector2i:
	if invert_on_walls and is_wall(where):
		return Vector2i(size.y, size.x)
	return size


func available() -> bool:
	return ResourceLoader.exists(scene_path)


## Instantiates the scene positioned for the cell rectangle [param rect]
## (absolute columns/rows). Does not add it to the tree.
func spawn(where: int, rect: Rect2i, coin_budget: int) -> Node3D:
	if _packed == null:
		_packed = load(scene_path)
	var node := _packed.instantiate() as Node3D
	node.position = default_position(where, rect)
	if "coin_budget" in node:
		node.set("coin_budget", coin_budget)
	for key in extra:
		node.set(key, extra[key])
	if placer.is_valid():
		placer.call(node, where, rect)
	return node


func default_position(where: int, rect: Rect2i) -> Vector3:
	var cx := rect.position.x + rect.size.x * 0.5
	match where:
		Where.LEFT_WALL:
			return Vector3(rect.position.x, -(rect.position.y + rect.size.y * 0.5), 0.0)
		Where.RIGHT_WALL:
			return Vector3(rect.end.x, -(rect.position.y + rect.size.y * 0.5), 0.0)
		Where.ROOF:
			return Vector3(cx, -rect.position.y, 0.0)
	if anchor == Anchor.CENTER:
		return Vector3(cx, -(rect.position.y + rect.size.y * 0.5), 0.0)
	return Vector3(cx, -rect.end.y, 0.0)
