// Synthwave dusk: deep violet overhead sinking through magenta to a hot
// orange band at the horizon, a scatter of stars and a few thin cirrus
// streaks. UV.y runs from 0 at the top of the quad to 1 at the bottom.
shader_type spatial;
render_mode unshaded, cull_disabled, fog_disabled;

uniform vec3 top_color : source_color = vec3(0.02, 0.005, 0.06);
uniform vec3 violet : source_color = vec3(0.22, 0.03, 0.38);
uniform vec3 magenta : source_color = vec3(0.85, 0.12, 0.48);
uniform vec3 orange : source_color = vec3(1.0, 0.5, 0.18);
uniform vec3 below : source_color = vec3(0.12, 0.02, 0.16);
uniform float horizon = 0.62;

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void fragment() {
	float y = UV.y;
	vec3 col = mix(top_color, violet, smoothstep(0.05, horizon - 0.25, y));
	col = mix(col, magenta, smoothstep(horizon - 0.22, horizon - 0.04, y));
	col = mix(col, orange, smoothstep(horizon - 0.06, horizon, y));
	col = mix(col, below, smoothstep(horizon, horizon + 0.03, y));
	// Stars, densest at the top.
	vec2 cellp = UV * vec2(220.0, 320.0);
	vec2 id = floor(cellp);
	float h = hash2(id);
	float star = step(0.975, h) * (0.55 + 0.45 * sin(TIME * 2.5 + hash2(id + 7.0) * 30.0));
	float d = length(fract(cellp) - 0.5);
	star *= smoothstep(0.3, 0.05, d) * (1.0 - smoothstep(0.35, horizon - 0.1, y));
	// Cirrus streaks lit from below.
	float streak = 0.0;
	for (int i = 0; i < 4; i++) {
		float fy = horizon - 0.08 - float(i) * 0.05;
		float band = smoothstep(0.012, 0.0, abs(y - fy) - 0.004);
		float along = 0.5 + 0.5 * sin(UV.x * (11.0 + float(i) * 3.0) + float(i) * 1.7 + TIME * 0.02);
		streak += band * along * (0.35 - float(i) * 0.06);
	}
	col += mix(orange, magenta, 0.4) * streak;
	ALBEDO = col + vec3(star) * 1.4;
}
