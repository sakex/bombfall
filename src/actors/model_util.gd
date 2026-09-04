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
