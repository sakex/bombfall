// The night sky behind the city: navy overhead, a magenta haze low down,
// with a sprinkle of stars.
shader_type spatial;
render_mode unshaded, cull_disabled;

uniform vec3 top_color : source_color = vec3(0.02, 0.01, 0.05);
uniform vec3 mid_color : source_color = vec3(0.16, 0.04, 0.22);
uniform vec3 glow_color : source_color = vec3(0.7, 0.12, 0.45);

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	float y = UV.y;
	vec3 col = mix(top_color, mid_color, smoothstep(0.1, 0.75, y));
	col = mix(col, glow_color, smoothstep(0.72, 1.0, y) * 0.8);
	vec2 cellp = UV * vec2(160.0, 260.0);
	vec2 id = floor(cellp);
	float star = step(0.985, hash2(id)) * (0.5 + 0.5 * sin(TIME * 2.0 + hash2(id + 7.0) * 20.0));
	float d = length(fract(cellp) - 0.5);
	star *= smoothstep(0.25, 0.05, d) * (1.0 - smoothstep(0.55, 0.9, y));
	ALBEDO = col + vec3(star) * 1.5;
}
