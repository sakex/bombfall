// Skyscraper facades: a dark shell with a procedural grid of lit windows in
// three neon tints, computed from world position so towers can be moved and
// recycled freely. Used by the City MultiMesh.
shader_type spatial;
render_mode cull_back, unshaded;

uniform vec3 base_color : source_color = vec3(0.045, 0.03, 0.08);
uniform vec3 color_a : source_color = vec3(0.15, 0.9, 1.0);
uniform vec3 color_b : source_color = vec3(1.0, 0.25, 0.7);
uniform vec3 color_c : source_color = vec3(1.0, 0.8, 0.35);
uniform float cell = 2.0;
uniform float lit_ratio = 0.5;
uniform float glow = 2.2;

varying vec3 world_pos;
varying vec3 world_normal;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
}

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	if (abs(world_normal.y) > 0.5) {
		ALBEDO = base_color;
	} else {
		vec2 uv = abs(world_normal.z) > abs(world_normal.x) ? world_pos.xy : world_pos.zy;
		vec2 id = floor(uv / cell);
		vec2 f = fract(uv / cell);
		float h = hash2(id + floor(world_pos.zx * 0.01) * 0.0);
		float h2 = hash2(id * 1.7 + 3.1);
		float lit = step(1.0 - lit_ratio, h);
		float inside = step(0.22, f.x) * step(f.x, 0.78) * step(0.28, f.y) * step(f.y, 0.72);
		vec3 tint = mix(mix(color_a, color_b, step(0.45, h2)), color_c, step(0.8, h2));
		float flicker = 0.8 + 0.2 * sin(TIME * (0.6 + h2 * 2.5) + h * 30.0);
		// A faint ledge line every floor keeps unlit stretches from reading flat.
		float ledge = smoothstep(0.02, 0.0, abs(f.y - 0.5) - 0.47) * 0.05;
		// Unshaded: the lit windows go straight into the colour (HDR, so they glow).
		ALBEDO = base_color + tint * inside * lit * flicker * glow + base_color * ledge;
	}
}
