shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
// Flame tongues of the fire zone (blender/hazards.py fire_zone). The mesh
// runs from VERTEX.y = 0 (base) to 1 (tip); the object scale sizes it.
// Scrolling value noise licks upwards and eats the edges; the tongue sways
// more towards its tip; the centre (facing the camera) burns hotter.

uniform vec4 color : source_color = vec4(1.0, 0.35, 0.05, 1.0);
uniform vec4 core : source_color = vec4(1.0, 0.85, 0.45, 1.0);
uniform float energy = 2.2;
uniform float speed = 1.0;

varying float h;
varying vec3 lp;
varying float seed;

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
	h = clamp(VERTEX.y, 0.0, 1.0);
	seed = fract(NODE_POSITION_WORLD.x * 1.37 + NODE_POSITION_WORLD.y * 0.71 + MODEL_MATRIX[3].x * 3.1);
	float t = TIME * speed;
	VERTEX.x += sin(t * 5.3 + seed * 20.0 + VERTEX.y * 4.0) * 0.1 * h * h;
	VERTEX.z += cos(t * 4.1 + seed * 13.0 + VERTEX.y * 3.0) * 0.07 * h * h;
	lp = VERTEX;
}

void fragment() {
	float t = TIME * speed;
	float a = atan(lp.z, lp.x);
	vec2 uv = vec2(a * 0.9 + seed * 10.0, lp.y * 2.4 - t * 2.6);
	float n = noise(uv * 2.0) * 0.6 + noise(uv * 4.7 + vec2(3.1, t)) * 0.4;
	float facing = clamp(abs(dot(NORMAL, VIEW)), 0.0, 1.0);
	float body = smoothstep(1.0, 0.25, h) * (0.35 + 0.65 * facing);
	float m = clamp(body * (0.5 + n) - (1.0 - facing) * 0.25 - h * n * 0.5, 0.0, 1.0);
	vec3 c = mix(color.rgb, core.rgb, clamp(facing * (1.0 - h) * 1.4 - 0.2, 0.0, 1.0));
	ALBEDO = c * m * energy;
}
