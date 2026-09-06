shader_type spatial;
render_mode unshaded, cull_back;
// Monitors, CRTs and wall screens: rolling scanlines, a slow bright band,
// static and the odd glitch frame.

uniform vec3 color : source_color = vec3(0.2, 0.9, 0.95);
uniform float energy = 1.6;

varying vec3 wpos;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment_lines(out float b) {
	float lines = 0.7 + 0.3 * step(0.5, fract(wpos.y * 26.0 + TIME * 5.0));
	float band = 1.0 - smoothstep(0.0, 0.12, abs(fract(TIME * 0.2 + wpos.y * 0.12) - 0.5));
	float noise = hash(vec2(floor(wpos.y * 60.0), floor(TIME * 24.0))) * 0.2;
	float glitch = step(0.975, hash(vec2(floor(TIME * 6.0), 1.0))) * 0.7 * step(0.5, fract(wpos.y * 3.0 + TIME * 30.0));
	b = lines * (0.85 + 0.45 * band) + noise + glitch;
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float b;
	fragment_lines(b);
	ALBEDO = color * energy * b;
}
