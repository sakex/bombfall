// A soft additive light cone sweeping the sky.
shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never;

uniform vec3 color : source_color = vec3(0.9, 0.5, 1.0);
uniform float strength = 0.35;

void fragment() {
	float along = 1.0 - UV.y;
	float edge = 1.0 - smoothstep(0.3, 0.5, abs(UV.x - 0.5));
	ALBEDO = color * strength * edge * (1.0 - along) * (1.0 - along);
}
