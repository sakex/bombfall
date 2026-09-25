shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
// The air fan's updraught (src/spawnables/air_fan.tscn): faint streaks
// rushing up an open cylinder, fading at both ends and towards the middle
// of the column so it reads as moving air, not a tube.

uniform vec3 color : source_color = vec3(0.55, 0.9, 1.0);
uniform float energy = 0.35;
uniform float speed = 5.0;
uniform float height = 7.0;

varying vec3 lp;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

float noise(vec2 p) {
	vec2 i = floor(p);
	vec2 f = fract(p);
	vec2 u = f * f * (3.0 - 2.0 * f);
	return mix(mix(hash(i), hash(i + vec2(1.0, 0.0)), u.x), mix(hash(i + vec2(0.0, 1.0)), hash(i + vec2(1.0, 1.0)), u.x), u.y);
}

void vertex() {
	lp = VERTEX;
}

void fragment() {
	float a = atan(lp.z, lp.x) / 6.2832 + 0.5;
	float y = lp.y / height + 0.5;                     // 0 at the fan, 1 at the top
	float lane = floor(a * 28.0);
	float offset = hash(vec2(lane, 3.0));
	float s = fract((lp.y - TIME * speed * (0.7 + 0.6 * offset)) / (1.6 + offset * 1.8) + offset);
	float streak = smoothstep(0.0, 0.12, s) * (1.0 - smoothstep(0.25, 0.5, s));
	float thin = 1.0 - smoothstep(0.1, 0.45, abs(fract(a * 28.0) - 0.5));
	float fade = smoothstep(0.0, 0.08, y) * (1.0 - smoothstep(0.55, 1.0, y));
	float edge = 1.0 - clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0);
	float b = streak * thin * fade * (0.35 + 0.65 * edge) * (0.6 + 0.8 * noise(vec2(a * 40.0, y * 3.0 - TIME)));
	ALBEDO = color * energy * b;
}
