class_name Painting
extends Prop
## A framed masterpiece. The canvas shows one of the classic paintings the
## original game shipped, picked at random.

const PAINTINGS_DIR := "res://assets/textures/paintings/"
static var _textures: Array[Texture2D] = []


func _ready() -> void:
	random_flip = false
	super._ready()
	if _textures.is_empty():
		for file in ResourceLoader.list_directory(PAINTINGS_DIR):
			if file.ends_with(".png"):
				_textures.append(load(PAINTINGS_DIR + file))
	var canvas := model.find_child("canvas", true, false) as MeshInstance3D
	if canvas != null and not _textures.is_empty():
		var material := StandardMaterial3D.new()
		material.albedo_texture = _textures[randi() % _textures.size()]
		material.roughness = 0.8
		canvas.set_surface_override_material(0, material)
