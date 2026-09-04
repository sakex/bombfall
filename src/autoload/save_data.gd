extends Node
## Persistent player profile: coins, upgrades, scores and settings.
##
## Stored as JSON at user://save_game.json with the same keys the original
## game used, so an upgraded install keeps its coins and high scores.

signal changed(data: Dictionary)

const SAVE_PATH := "user://save_game.json"
const MAX_LOCAL_SCORES := 50

const DEFAULTS := {
	"coins": 0,
	"base_shields": 0,
	"max_shields": 1,
	"magnets": 0,
	"scores": [],
	"max_score": {"score": 0, "date": ""},
	"volume_music": 1.0,
	"volume_sfx": 1.0,
	"games_since_last_rewarded_interstitial": 0,
	"username": "",
	"username_changed": false,
	"offered_tutorial": false,
}

var data: Dictionary = {}
## True on the very first launch (used to skip the pre-game ad and offer the tutorial).
var first_launch := false


func _ready() -> void:
	data = _load()
	var filled := false
	for key in DEFAULTS:
		if not data.has(key):
			data[key] = _dup(DEFAULTS[key])
			filled = true
	if filled:
		first_launch = data["scores"].is_empty()
		save()
	apply_volumes()


func _dup(value: Variant) -> Variant:
	return value.duplicate(true) if value is Dictionary or value is Array else value


func _load() -> Dictionary:
	if not FileAccess.file_exists(SAVE_PATH):
		return {}
	var file := FileAccess.open(SAVE_PATH, FileAccess.READ)
	if file == null:
		return {}
	var parsed: Variant = JSON.parse_string(file.get_as_text())
	return parsed if parsed is Dictionary else {}


func save() -> void:
	var file := FileAccess.open(SAVE_PATH, FileAccess.WRITE)
	if file == null:
		push_error("Cannot write save file: %s" % error_string(FileAccess.get_open_error()))
		return
	file.store_string(JSON.stringify(data))
	file.close()
	changed.emit(data)


func apply_volumes() -> void:
	set_bus_volume("music", data["volume_music"])
	set_bus_volume("sfx", data["volume_sfx"])


static func set_bus_volume(bus: String, linear: float) -> void:
	AudioServer.set_bus_volume_db(AudioServer.get_bus_index(bus), linear_to_db(clampf(linear, 0.0, 1.0)))


static func get_bus_volume(bus: String) -> float:
	return db_to_linear(AudioServer.get_bus_volume_db(AudioServer.get_bus_index(bus)))


func set_volumes(music: float, sfx: float) -> void:
	data["volume_music"] = music
	data["volume_sfx"] = sfx
	apply_volumes()
	save()


## Records a finished (or paused) run. Coins earned equal the score.
## When [param replaces_previous] is true the last recorded score is replaced
## instead of appended, which is how a revived run keeps a single entry.
func record_score(score: int, replaces_previous: bool = false) -> void:
	var previous := 0
	if replaces_previous and not data["scores"].is_empty():
		previous = int(data["scores"].back()["score"])
		data["scores"].pop_back()
	data["coins"] += score - previous
	var entry := {"score": score, "date": Time.get_datetime_string_from_system(true)}
	data["scores"].append(entry)
	while data["scores"].size() > MAX_LOCAL_SCORES:
		data["scores"].pop_front()
	if score > int(data["max_score"]["score"]):
		data["max_score"] = entry.duplicate()
	save()
	Services.backend.sync_profile(data)


## Sorted best-first list of {score, date} for the leaderboard.
func best_scores(limit: int = 20) -> Array:
	var scores: Array = data["scores"].duplicate()
	scores = scores.filter(func(e): return int(e["score"]) > 0)
	scores.sort_custom(func(a, b): return int(a["score"]) > int(b["score"]))
	return scores.slice(0, limit)


func can_afford(cost: int) -> bool:
	return cost > 0 and cost <= int(data["coins"])


func buy(product_id: String, cost: int) -> bool:
	if not can_afford(cost) or not data.has(product_id):
		return false
	data["coins"] -= cost
	data[product_id] += 1
	save()
	Services.backend.sync_profile(data)
	return true


func set_username(name: String) -> void:
	data["username"] = name
	data["username_changed"] = true
	save()


func mark_tutorial_offered() -> void:
	data["offered_tutorial"] = true
	save()
