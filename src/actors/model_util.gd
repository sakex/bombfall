class_name ModelUtil
## Helpers for the glTF models built by the Blender scripts.


## Finds the first MeshInstance3D under [param root] whose name matches.
static func find_mesh(root: Node, name: String) -> MeshInstance3D:
	var node := root.find_child(name, true, false)
	if node is MeshInstance3D:
		return node
	if node != null:
		for child in node.get_children():
			if child is MeshInstance3D:
				return child
	return null


## Gives a mesh instance its own copy of surface [param surface]'s material so
## it can be animated without affecting every other instance of the model.
static func own_material(mesh: MeshInstance3D, surface: int = 0) -> StandardMaterial3D:
	if mesh == null:
		return null
	var existing := mesh.get_surface_override_material(surface)
	if existing != null:
		return existing
	var base := mesh.mesh.surface_get_material(surface)
	if base == null:
		return null
	var copy: StandardMaterial3D = base.duplicate()
	mesh.set_surface_override_material(surface, copy)
	return copy


## Applies [param material] to every surface of every mesh below [param root].
static func override_all(root: Node, material: Material) -> void:
	for mesh in all_meshes(root):
		for i in mesh.mesh.get_surface_count():
			mesh.set_surface_override_material(i, material)


static func all_meshes(root: Node) -> Array[MeshInstance3D]:
	var out: Array[MeshInstance3D] = []
	var stack: Array[Node] = [root]
	while not stack.is_empty():
		var n: Node = stack.pop_back()
		if n is MeshInstance3D:
			out.append(n)
		stack.append_array(n.get_children())
	return out


## Sets [param visible] on the whole model tree (used to blink the player).
static func set_visible(root: Node, visible: bool) -> void:
	if root is Node3D:
		(root as Node3D).visible = visible


# ---------------------------------------------------------------- animation --
## Clips named "idle" or ending in "_loop" loop; everything else plays once.
## The glTF exporter pads each clip with the rest pose of every other animated
## part, which would freeze parts the game moves in code, so constant tracks
## are dropped. Done once per animation resource (shared by all instances).
static func prepare_animations(player: AnimationPlayer) -> void:
	for clip in player.get_animation_list():
		var anim := player.get_animation(clip)
		if anim.has_meta("_prepared"):
			continue
		anim.set_meta("_prepared", true)
		if clip == "idle" or clip.ends_with("_loop"):
			anim.loop_mode = Animation.LOOP_LINEAR
		for t in range(anim.get_track_count() - 1, -1, -1):
			if _is_constant(anim, t):
				anim.remove_track(t)


static func _is_constant(anim: Animation, track: int) -> bool:
	var n := anim.track_get_key_count(track)
	if n <= 1:
		return true
	var first: Variant = anim.track_get_key_value(track, 0)
	for k in range(1, n):
		var v: Variant = anim.track_get_key_value(track, k)
		if v is Quaternion:
			if not (v as Quaternion).is_equal_approx(first):
				return false
		elif v is Vector3:
			if not (v as Vector3).is_equal_approx(first):
				return false
		elif v != first:
			return false
	return true


## The AnimationPlayer of an imported model, or null.
static func anim_player(root: Node) -> AnimationPlayer:
	if root == null:
		return null
	return root.find_child("AnimationPlayer", true, false) as AnimationPlayer


## Plays a one-shot clip on a model, then goes back to its idle loop.
static func play(root: Node, clip: String, speed := 1.0) -> bool:
	var player := anim_player(root)
	if player == null or not player.has_animation(clip):
		return false
	player.play(clip, 0.05, speed)
	if player.has_animation("idle"):
		player.queue("idle")
	return true


## Materials named anim_<kind> in any model (see blender/common.py `anim`)
## are swapped for shader materials that scroll, chase and flicker, so signs
## and screens live without any per-node animation. Called on every imported
## model by the Game autoload, and idempotent.
const ANIM_SHADERS := {
	"anim_marquee": "res://assets/shaders/anim_marquee.gdshader",
	"anim_screen": "res://assets/shaders/anim_screen.gdshader",
}
static var _anim_cache: Dictionary = {}


static func animate_materials(root: Node) -> void:
	var meshes: Array[Node] = root.find_children("*", "MeshInstance3D", true, false)
	if root is MeshInstance3D:
		meshes.append(root)
	for mesh_node in meshes:
		var mi := mesh_node as MeshInstance3D
		if mi.mesh == null:
			continue
		for i in mi.mesh.get_surface_count():
			var material := mi.get_active_material(i)
			if material == null:
				continue
			# Blender exports every material double-sided. On a double-sided
			# material the renderer flips the normal of faces it thinks point
			# away, and on mirrored props (the random flip) it guessed wrong
			# and lit the outside as if it were the inside: a white toilet went
			# near black. The baked models are closed and face the camera, so
			# single-sided is correct (and halves their shading work).
			if material is BaseMaterial3D and material.resource_name.ends_with("_baked") \
					and (material as BaseMaterial3D).cull_mode == BaseMaterial3D.CULL_DISABLED:
				(material as BaseMaterial3D).cull_mode = BaseMaterial3D.CULL_BACK
			for prefix in ANIM_SHADERS:
				if material.resource_name.begins_with(prefix):
					mi.set_surface_override_material(i, _anim_material(prefix, material))
					break


static func _anim_material(prefix: String, source: Material) -> ShaderMaterial:
	var colour := Color(0.9, 0.3, 0.8)
	var energy := 3.0
	if source is StandardMaterial3D:
		var std := source as StandardMaterial3D
		if std.emission_enabled and std.emission.get_luminance() > 0.05:
			colour = std.emission
			energy = maxf(std.emission_energy_multiplier, 1.0)
		else:
			colour = std.albedo_color
			energy = 1.0
	var key := "%s|%s|%.2f" % [prefix, colour.to_html(false), energy]
	if _anim_cache.has(key):
		return _anim_cache[key]
	var sm := ShaderMaterial.new()
	sm.shader = load(ANIM_SHADERS[prefix])
	sm.set_shader_parameter("color", colour)
	sm.set_shader_parameter("energy", energy)
	_anim_cache[key] = sm
	return sm
