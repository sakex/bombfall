// Skyscraper facades: a dark shell lit by the sunset on one side, with a
// procedural grid of windows in neon tints, a bright band every dozen
// floors and a glowing roof line. Everything is computed from world
// position so the towers can be moved and recycled. INSTANCE_CUSTOM:
// x = hue shift, y = window density, z = tower top world Y, w = height.
shader_type spatial;
render_mode cull_back, unshaded;

uniform vec3 base_color : source_color = vec3(0.025, 0.012, 0.05);
uniform vec3 sun_tint : source_color = vec3(0.9, 0.25, 0.45);
uniform vec3 sun_dir = vec3(0.35, -0.2, -0.9);
uniform vec3 color_a : source_color = vec3(0.15, 0.9, 1.0);
uniform vec3 color_b : source_color = vec3(1.0, 0.25, 0.7);
uniform vec3 color_c : source_color = vec3(1.0, 0.75, 0.35);
uniform float cell = 1.5;
uniform float glow = 2.0;

varying vec3 world_pos;
varying vec3 world_normal;
varying vec4 custom;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	custom = INSTANCE_CUSTOM;
}

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	float sun = clamp(dot(world_normal, -normalize(sun_dir)), 0.0, 1.0);
	vec3 shell = base_color + sun_tint * sun * 0.09;
	// Warm haze near the ground, colder up high.
	float up = clamp((world_pos.y - (custom.z - custom.w)) / max(custom.w, 1.0), 0.0, 1.0);
	shell = mix(shell + vec3(0.07, 0.01, 0.05), shell, smoothstep(0.0, 0.45, up));
	vec3 col = shell;
	if (abs(world_normal.y) < 0.5) {
		vec2 uv = abs(world_normal.z) > abs(world_normal.x) ? world_pos.xy : world_pos.zy;
		vec2 id = floor(uv / cell);
		vec2 f = fract(uv / cell);
		float floor_dark = step(0.15, hash2(vec2(id.y, custom.x * 91.0)));   // some floors unlit
		float h = hash2(id + custom.x * 13.0);
		float h2 = hash2(id * 1.7 + 3.1 + custom.x);
		float lit = step(1.0 - custom.y, h) * floor_dark;
		float inside = step(0.22, f.x) * step(f.x, 0.78) * step(0.32, f.y) * step(f.y, 0.68);
		vec3 tint = mix(mix(color_a, color_b, step(0.45, h2)), color_c, step(0.8, h2));
		float flicker = 0.85 + 0.15 * sin(TIME * (0.6 + h2 * 2.5) + h * 30.0);
		float band = step(0.93, fract(uv.y / (cell * 12.0))) * 0.9;
		float roof = smoothstep(0.9, 0.0, custom.z - world_pos.y) * 1.2;
		float ledge = (1.0 - smoothstep(0.0, 0.04, abs(f.y - 0.5) - 0.46)) * 0.06;
		col += tint * inside * lit * flicker * glow * (0.6 + 0.4 * h) + color_b * band + color_a * roof + shell * ledge;
	} else if (world_normal.y > 0.5) {
		col = shell * 0.6 + color_a * 0.05;
	}
	ALBEDO = col;
}
