// The white-hot heart of an explosion: an additive glow that is brightest
// facing the camera and fades to nothing at its rim. `heat` (0..1) drives it.
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_back, shadows_disabled, fog_disabled;

instance uniform float heat = 1.0;
uniform vec3 color : source_color = vec3(1.0, 0.82, 0.55);

void fragment() {
	float facing = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	float glow = pow(facing, 2.5);
	ALBEDO = color * glow * heat * 2.6;
}
