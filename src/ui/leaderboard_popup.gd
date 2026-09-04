class_name LeaderboardPopup
extends MenuPopup
## Best runs on this device, plus the online board when a backend is wired.

var _tabs: TabContainer
var _local_list: VBoxContainer
var _global_list: VBoxContainer


func _init() -> void:
	super._init("leaderboard")


func _build() -> void:
	_tabs = TabContainer.new()
	_tabs.custom_minimum_size = Vector2(0, 900)
	content.add_child(_tabs)
	_local_list = _tab("local")
	_global_list = _tab("global")
	var close_button := button("close", 80)
	close_button.pressed.connect(close)
	content.add_child(close_button)
	Services.backend.leaderboard_loaded.connect(_show_global)


func _tab(title: String) -> VBoxContainer:
	var scroll := ScrollContainer.new()
	scroll.name = title
	scroll.horizontal_scroll_mode = ScrollContainer.SCROLL_MODE_DISABLED
	var list := VBoxContainer.new()
	list.size_flags_horizontal = Control.SIZE_EXPAND_FILL
	list.add_theme_constant_override("separation", 10)
	scroll.add_child(list)
	_tabs.add_child(scroll)
	return list


func _refresh() -> void:
	_fill(_local_list, SaveData.best_scores(20).map(func(e): return {"name": _name_or_you(), "score": e["score"], "date": e.get("date", "")}))
	_fill(_global_list, [])
	if Services.backend.available():
		Services.backend.fetch_leaderboard()
	else:
		_global_list.add_child(label("The online leaderboard needs an account backend, which this build does not include.", 32, Color(0.8, 0.78, 0.9)))


func _name_or_you() -> String:
	var name := str(SaveData.data["username"])
	return name if not name.is_empty() else "you"


func _show_global(entries: Array) -> void:
	_fill(_global_list, entries.map(func(e): return {"name": e.get("username", "?"), "score": e.get("score", 0), "date": ""}))


func _fill(list: VBoxContainer, entries: Array) -> void:
	for child in list.get_children():
		child.queue_free()
	if entries.is_empty():
		list.add_child(label("no runs yet", 36, Color(0.6, 0.6, 0.7)))
		return
	var rank := 1
	for entry in entries:
		var row := HBoxContainer.new()
		var r := label("%d." % rank, 36, Color(1.0, 0.6, 0.95))
		r.custom_minimum_size = Vector2(90, 0)
		row.add_child(r)
		var n := label(str(entry["name"]), 36)
		n.size_flags_horizontal = Control.SIZE_EXPAND_FILL
		n.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
		row.add_child(n)
		var s := label(str(entry["score"]), 36, Color(1.0, 0.85, 0.3))
		s.custom_minimum_size = Vector2(220, 0)
		s.horizontal_alignment = HORIZONTAL_ALIGNMENT_RIGHT
		row.add_child(s)
		list.add_child(row)
		rank += 1
