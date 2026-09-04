class_name StorePopup
extends MenuPopup
## Spend coins on shield cells, shield cores and magnets. Prices step up
## with each copy owned, as in the original.

signal any_buyable(buyable: bool)

const ITEMS := [
	{"id": "base_shields", "name": "shield cell", "costs": [100, 1000, 2000], "blurb": "Start every run with one more shield charged."},
	{"id": "max_shields", "name": "shield core", "costs": [0, 1000, 2000, 5000], "blurb": "Raise the number of shields you can hold."},
	{"id": "magnets", "name": "magnet", "costs": [500, 2000, 5000, 10000], "blurb": "Pull coins towards you from further away."},
]

var _coins_label: Label
var _rows: Array[Dictionary] = []
var _confirm: MenuPopup


func _init() -> void:
	super._init("store")


func _build() -> void:
	_coins_label = label("0 coins", 44, Color(1.0, 0.85, 0.3))
	content.add_child(_coins_label)
	for item in ITEMS:
		var row := PanelContainer.new()
		var box := VBoxContainer.new()
		box.add_theme_constant_override("separation", 8)
		row.add_child(box)
		var name_label := label(item["name"], 46, Color(0.7, 0.95, 1.0))
		box.add_child(name_label)
		box.add_child(label(item["blurb"], 30, Color(0.8, 0.78, 0.9)))
		var owned := label("", 30)
		box.add_child(owned)
		var buy := button("buy", 80)
		buy.pressed.connect(_ask.bind(item))
		box.add_child(buy)
		content.add_child(row)
		_rows.append({"item": item, "owned": owned, "buy": buy})
	var close_button := button("close", 80)
	close_button.pressed.connect(close)
	content.add_child(close_button)
	SaveData.changed.connect(func(_d): _refresh())


static func cost_of(item: Dictionary) -> int:
	var count := int(SaveData.data.get(item["id"], 0))
	var costs: Array = item["costs"]
	if count < 0 or count >= costs.size():
		return -1
	return costs[count]


func _refresh() -> void:
	var coins := int(SaveData.data["coins"])
	_coins_label.text = "%d coins" % coins
	var buyable := false
	for row in _rows:
		var item: Dictionary = row["item"]
		var cost := cost_of(item)
		var count := int(SaveData.data.get(item["id"], 0))
		row["owned"].text = "owned: %d" % count
		var buy: Button = row["buy"]
		if cost < 0:
			buy.text = "max level"
			buy.disabled = true
		else:
			buy.text = "buy for %d" % cost
			buy.disabled = not SaveData.can_afford(cost)
			buyable = buyable or SaveData.can_afford(cost)
	any_buyable.emit(buyable)


func _ask(item: Dictionary) -> void:
	var cost := cost_of(item)
	if cost < 0:
		return
	if _confirm == null:
		_confirm = ConfirmPopup.new()
		add_child(_confirm)
	_confirm.ask("buy %s for %d coins?" % [item["name"], cost], func():
		if SaveData.buy(item["id"], cost):
			_refresh())


class ConfirmPopup extends MenuPopup:
	var _text: Label
	var _on_yes: Callable

	func _init() -> void:
		super._init("confirm")

	func _build() -> void:
		_text = label("", 40)
		content.add_child(_text)
		var yes := button("confirm")
		yes.pressed.connect(func(): close(); _on_yes.call())
		content.add_child(yes)
		var no := button("cancel", 80)
		no.pressed.connect(close)
		content.add_child(no)

	func ask(text: String, on_yes: Callable) -> void:
		_text.text = text
		_on_yes = on_yes
		open()
