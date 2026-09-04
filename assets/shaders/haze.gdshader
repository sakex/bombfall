// A translucent sheet of magenta haze; several at different depths give
// the skyline atmospheric layering.
shader_type spatial;
render_mode unshaded, cull_disabled, blend_mix, depth_draw_never, fog_disabled;

uniform vec3 color : source_color = vec3(0.7, 0.12, 0.45);
uniform float strength = 0.22;
uniform float horizon = 0.55;

void fragment() {
	float y = UV.y;
	float a = smoothstep(0.0, horizon, y) * strength * (1.0 - smoothstep(horizon + 0.15, 1.0, y) * 0.6);
	ALBEDO = color;
	ALPHA = a;
}
