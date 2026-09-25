shader_type spatial;
render_mode blend_add, unshaded, cull_disabled, depth_draw_never, shadows_disabled;
// The light ring's laser (src/spawnables/light_ring.tscn): a white-hot
// core fading to pink at the edges of the beam box, with energy pulses
// racing away from the emitter (towards the model's -X) and a slight
// shimmer. The beam node is scaled along X to its length by light_ring.gd.

uniform vec3 color : source_color = vec3(1.0, 0.25, 0.6);
uniform vec3 core : source_color = vec3(1.0, 0.85, 0.95);
uniform float energy = 3.0;
uniform float half_width = 0.14;

varying vec3 lp;
varying vec3 wp;

void vertex() {
	lp = VERTEX;
	wp = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
}

void fragment() {
	// distance from the beam's axis, 0 at the centre of each face
	float r = clamp(max(abs(lp.y), abs(lp.z)) / half_width, 0.0, 1.0);
	float across = abs(dot(NORMAL, VIEW));
	float centre = pow(across, 3.0);
	float pulse = 0.75 + 0.25 * sin(wp.x * 7.0 + TIME * 38.0) + 0.1 * sin(TIME * 90.0);
	vec3 c = mix(color, core, centre);
	ALBEDO = c * energy * pulse * (0.35 + 0.65 * centre) * (1.0 - 0.5 * r);
}
