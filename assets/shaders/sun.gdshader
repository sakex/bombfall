// The synthwave sun: a big disc grading from yellow to magenta, sliced by
// horizontal bands that widen towards the bottom, inside a soft halo.
// Additive so it burns through the haze.
shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;

uniform vec3 top_color : source_color = vec3(1.0, 0.92, 0.45);
uniform vec3 mid_color : source_color = vec3(1.0, 0.45, 0.25);
uniform vec3 bottom_color : source_color = vec3(0.95, 0.12, 0.55);
uniform float bands = 11.0;

void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float d = length(p);
	float y = UV.y;
	vec3 col = mix(top_color, mid_color, smoothstep(0.15, 0.55, y));
	col = mix(col, bottom_color, smoothstep(0.55, 0.95, y));
	float disc = 1.0 - smoothstep(0.62, 0.64, d);
	// Cuts: none in the upper half, growing gaps below.
	float gap = smoothstep(0.42, 0.95, y) * 0.55;
	float stripe = step(gap, fract(y * bands + 0.3));
	disc *= stripe;
	float halo = (exp(-max(d - 0.62, 0.0) * 6.0) * 0.55 + exp(-max(d - 0.62, 0.0) * 1.6) * 0.18) * smoothstep(1.0, 0.72, d);
	ALBEDO = col * disc * 2.4 + mix(mid_color, bottom_color, 0.5) * halo;
}
