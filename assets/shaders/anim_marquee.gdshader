shader_type spatial;
render_mode unshaded, cull_back;
// Neon sign dots: a chase wave runs along the letters while single dots
// twinkle and the whole tube flickers. Patterns use world space, so joined
// meshes need no UVs.

uniform vec3 color : source_color = vec3(1.0, 0.3, 0.8);
uniform float energy = 3.0;
uniform float speed = 1.4;

varying vec3 wpos;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void vertex() {
	wpos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	vec2 cell = floor(wpos.xy * 6.0);
	float chase = smoothstep(0.5, 0.62, fract(wpos.x * 0.3 - TIME * speed));
	float twinkle = step(0.92, hash(cell + floor(TIME * 3.0)));
	float flicker = 0.9 + 0.1 * sin(TIME * 41.0 + wpos.x * 2.0) * step(0.7, hash(vec2(floor(TIME * 2.0), 3.0)));
	float b = (0.4 + 0.6 * max(chase, twinkle)) * flicker;
	ALBEDO = color * energy * b;
}
