class_name World
extends Node3D
## Procedural hotel: keeps eight storeys alive around the player, furnishes
## each from a themed catalogue, rains bombs, and recycles what is far above.
## A GDScript port of the original Rust/GDNative generator.

const BOMB_SCENE := "res://src/actors/bomb.tscn"
const FIRE_ZONE_SCENE := "res://src/spawnables/fire_zone.tscn"
const COIN := preload("res://src/actors/coin.tscn")
const LEVELS_ALIVE := 8
const GC_DISTANCE := 28.0        ## 1800 px

## Preview mode (main menu): no bombs, no special levels.
@export var is_preview := false
@export var coin_budget := 1

## Node whose Y position drives generation (the player or the preview camera).
var tracked: Node3D

var cells: CellGrid
var levels: Array[Level] = []
var difficulty := 0
var player_level := 0
var levels_descended := 0
var at_special_level := false
var next_roof := 0
var levels_since_shield_item := 0
var time_since_bomb := 0.0
var time_between_bombs := 2.0

## Developer aids: `--theme=<id>` forces a room theme, `--special=<scene>`
## (wall_block / obstacle_course / boss_bat_arena) forces the special level.
var forced_theme := ""
var forced_special := ""
var _themes: Array[Dictionary] = []
var _used_themes: Array[Dictionary] = []
var _special_levels: Array[SpecialLevel] = []
var _used_special_levels: Array[SpecialLevel] = []
var _world_bound: Array[Node] = []
var _props: Node3D


func _ready() -> void:
	add_to_group("world")
	cells = CellGrid.new()
	cells.name = "CellGrid"
	cells.add_to_group("cell_grid")
	add_child(cells)
	_props = Node3D.new()
	_props.name = "Props"
	add_child(_props)
	_themes = SpawnRegistry.themes().duplicate()
	for arg in OS.get_cmdline_user_args():
		if arg.begins_with("--theme="):
			forced_theme = arg.trim_prefix("--theme=")
		if arg.begins_with("--special="):
			forced_special = arg.trim_prefix("--special=")
	for special in [
		WallBlockLevel.new(),
		SceneLevel.new("res://src/special_levels/obstacle_course.tscn", 35, 37, 37),
		SceneLevel.new("res://src/special_levels/boss_bat_arena.tscn", 22, 20),
		SceneLevel.new("res://src/special_levels/vault.tscn", 19, 20, 19),
	]:
		if special.available():
			_special_levels.append(special)
	_init_levels()


func _init_levels() -> void:
	var size := 15
	for i in LEVELS_ALIVE:
		var level := Level.new(next_roof, size)
		_draw_level(level)
		levels.append(level)
		next_roof = level.next_roof()
		size = randi_range(11, 15)


func _pick_theme() -> Dictionary:
	if forced_theme != "":
		for theme in SpawnRegistry.themes():
			if theme["id"] == forced_theme:
				return theme
	if _themes.is_empty():
		_themes = _used_themes
		_used_themes = []
	var theme: Dictionary = _themes.pop_at(randi() % _themes.size())
	_used_themes.append(theme)
	return theme


func _draw_level(level: Level) -> void:
	var theme := _pick_theme()
	level.draw_walls(cells, difficulty)
	level.backdrop = Backdrop.build(theme, level.roof, level.height)
	add_child(level.backdrop)
	var shield_item := _maybe_shield_item()
	if shield_item != null:
		level.place(shield_item, coin_budget, self)
	var specs: Array = []
	for id in theme["spawnables"]:
		var spec := SpawnRegistry.spec(id)
		if spec != null:
			specs.append(spec)
	level.draw_spawnables(difficulty, coin_budget, specs, self)
	level.draw_coins(coin_budget, self)
	difficulty += 1
	coin_budget += 1


func _maybe_shield_item() -> SpawnableSpec:
	levels_since_shield_item += 1
	if levels_since_shield_item <= 2:
		return null
	if randi_range(0, levels_since_shield_item) >= 2:
		levels_since_shield_item = 0
		var items := SpawnRegistry.shield_items()
		if items.is_empty():
			return null
		return items[randi() % items.size()]
	return null


func _render_one_new_level() -> void:
	var theme_height: int = 16
	var size := randi_range(10, theme_height)
	var level := Level.new(next_roof, size)
	_draw_level(level)
	next_roof = level.next_roof() + (0 if level.double_floor else 1)
	_push_level(level)


func _special_matches(special: SpecialLevel, name: String) -> bool:
	if special is SceneLevel:
		return (special as SceneLevel).scene_path.get_file().get_basename() == name
	return name == "wall_block"


## Generates the next storey as a special level (public for the dev tools).
func render_special_level() -> void:
	_render_special_level()


func _render_special_level() -> void:
	if _special_levels.is_empty():
		_special_levels = _used_special_levels
		_used_special_levels = []
	var index := randi() % _special_levels.size()
	if forced_special != "":
		for i in _special_levels.size():
			if _special_matches(_special_levels[i], forced_special):
				index = i
	var special: SpecialLevel = _special_levels.pop_at(index)
	_used_special_levels.append(special)
	var level := special.draw(self, next_roof, coin_budget)
	next_roof += special.advance_rows()
	difficulty += 1
	coin_budget += 1
	_push_level(level)


func _push_level(level: Level) -> void:
	if levels.size() >= LEVELS_ALIVE:
		var old: Level = levels.pop_front()
		old.clear(cells)
	levels.append(level)


func _render_new_levels(count: int) -> void:
	for i in count:
		if not is_preview and difficulty % 10 == 0 and (not _special_levels.is_empty() or not _used_special_levels.is_empty()):
			_render_special_level()
		else:
			_render_one_new_level()
		levels_descended += 1
		time_between_bombs = maxf(2.0 - levels_descended * 0.02, 1.0)


# ------------------------------------------------------------------ spawning --
## Adds a generated node to the world; [param level] binds its lifetime.
func add_spawned(node: Node3D, level: Level) -> void:
	if node == null:
		return
	if node.has_method("set_world"):
		node.call("set_world", self)
	_props.add_child(node)
	if level != null:
		level.bind(node)
	else:
		_world_bound.append(node)


func spawn_coin(value: int, position: Vector3) -> Coin:
	var coin: Coin = COIN.instantiate()
	coin.value = value
	coin.position = position
	add_spawned(coin, null)
	return coin


## Instantiates any scene at a position with optional property overrides.
func spawn_scene(path: String, position: Vector3, props: Dictionary = {}, level: Level = null) -> Node3D:
	if not ResourceLoader.exists(path):
		push_warning("spawn_scene: missing %s" % path)
		return null
	var node: Node3D = (load(path) as PackedScene).instantiate()
	node.position = position
	for key in props:
		node.set(key, props[key])
	add_spawned(node, level)
	return node


func _spawn_falling_bomb() -> void:
	if tracked == null:
		return
	var interval := randf_range(3.0, 6.0)
	var y := tracked.global_position.y + randf_range(6.25, 9.4)
	var last := levels.back() as Level
	if time_between_bombs <= 0.5 and ResourceLoader.exists(FIRE_ZONE_SCENE):
		time_between_bombs += 0.3
		spawn_scene(FIRE_ZONE_SCENE, Vector3(tracked.global_position.x, y, 0.0), {}, last)
	else:
		spawn_scene(BOMB_SCENE, Vector3(randf_range(1.0, 14.6), y, 0.0), {"bomb_time": interval, "bomb_scale": interval / 6.0}, last)
	if not at_special_level:
		time_between_bombs = maxf(time_between_bombs * 0.975, 0.5)


# ------------------------------------------------------------------- update --
func _process(delta: float) -> void:
	if tracked == null:
		return
	if not is_preview:
		time_since_bomb += delta
		if time_since_bomb >= time_between_bombs:
			time_since_bomb -= time_between_bombs
			_spawn_falling_bomb()
	var row := -tracked.global_position.y
	var at_level := -1
	for i in levels.size():
		if levels[i].contains_row(row):
			at_level = i
			break
	if at_level < 0:
		return
	if at_level > player_level:
		player_level = at_level
		time_between_bombs = 2.0 - player_level * 0.02
	at_special_level = levels[at_level].is_special
	if at_level >= 5:
		_render_new_levels(at_level - 4)
		player_level = 4
		_collect_garbage()


func _collect_garbage() -> void:
	var y := tracked.global_position.y
	for i in range(_world_bound.size() - 1, -1, -1):
		var node := _world_bound[i]
		if not is_instance_valid(node):
			_world_bound.remove_at(i)
			continue
		var p := (node as Node3D).global_position
		if p.y > y and p.distance_to(tracked.global_position) > GC_DISTANCE:
			node.queue_free()
			_world_bound.remove_at(i)


## World Y of the top of the floor of the storey containing [param y].
func floor_y_at(y: float) -> float:
	var row := -y
	for level in levels:
		if level.contains_row(row):
			return -float(level.floor_row())
	return y - 5.0


## The row the player is currently in (for the HUD / debugging).
func current_roof() -> int:
	return levels[mini(player_level, levels.size() - 1)].roof if not levels.is_empty() else 0
