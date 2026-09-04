// The neon ground grid the city stands on: glowing lines in world space
// that roll towards the viewer, over a dark violet floor that catches the
// horizon glow in the distance.
shader_type spatial;
render_mode unshaded, cull_disabled;

uniform vec3 floor_color : source_color = vec3(0.06, 0.01, 0.1);
uniform vec3 line_color : source_color = vec3(1.0, 0.2, 0.75);
uniform vec3 line_color_2 : source_color = vec3(0.25, 0.9, 1.0);
uniform float spacing = 10.0;
uniform float speed = 6.0;

varying vec3 world_pos;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	float z = world_pos.z + TIME * speed;
	vec2 g = vec2(world_pos.x, z) / spacing;
	vec2 f = abs(fract(g) - 0.5);
	vec2 fw = fwidth(g) * 1.5;
	float lx = 1.0 - smoothstep(0.0, fw.x + 0.03, f.x - 0.02);
	float lz = 1.0 - smoothstep(0.0, fw.y + 0.03, f.y - 0.02);
	float line = max(lx, lz);
	float major = step(0.9, fract(floor(g.x) * 0.2 + 0.05)) * lx + step(0.9, fract(floor(g.y) * 0.2 + 0.05)) * lz;
	vec3 lc = mix(line_color, line_color_2, clamp(major, 0.0, 1.0));
	// Distance glow: the far floor picks up the sunset.
	float depth = clamp(-world_pos.z / 420.0, 0.0, 1.0);
	vec3 base = mix(floor_color, vec3(0.55, 0.08, 0.35), depth * depth);
	ALBEDO = base + lc * line * (2.2 - depth * 1.2);
}
