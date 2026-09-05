// A big pale moon with a few craters and a magenta terminator glow.
shader_type spatial;
render_mode unshaded, cull_disabled, blend_add, depth_draw_never, fog_disabled;

uniform vec3 color : source_color = vec3(0.85, 0.7, 0.95);

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	vec2 p = (UV - 0.5) * 2.0;
	float d = length(p);
	float disc = 1.0 - smoothstep(0.7, 0.72, d);
	float shade = 0.55 + 0.45 * smoothstep(-0.7, 0.7, p.x);
	float craters = 1.0;
	for (int i = 0; i < 6; i++) {
		vec2 c = vec2(hash2(vec2(float(i), 1.0)), hash2(vec2(2.0, float(i)))) * 1.0 - 0.5;
		float r = 0.06 + hash2(vec2(float(i), 3.0)) * 0.1;
		craters -= smoothstep(r, r * 0.6, length(p - c)) * 0.25;
	}
	float rim = exp(-max(d - 0.7, 0.0) * 8.0) * 0.5;
	ALBEDO = color * disc * shade * craters * 1.2 + vec3(0.9, 0.3, 0.7) * rim;
}
