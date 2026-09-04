class_name TutorialModal
extends MenuPopup
## First-launch prompt offering the tutorial.


func _init() -> void:
	super._init("welcome to bombfall")


func _build() -> void:
	content.add_child(label("Do you want to play the tutorial?", 40))
	var play := button("play tutorial")
	play.pressed.connect(func(): SaveData.mark_tutorial_offered(); Game.start_tutorial())
	content.add_child(play)
	var skip := button("skip", 80)
	skip.pressed.connect(func(): SaveData.mark_tutorial_offered(); close())
	content.add_child(skip)
