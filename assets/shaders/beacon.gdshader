// Blinking rooftop beacons; INSTANCE_CUSTOM.x offsets the phase per instance.
shader_type spatial;
render_mode unshaded;

uniform vec3 color : source_color = vec3(1.0, 0.2, 0.25);

varying float phase;

void vertex() {
	phase = INSTANCE_CUSTOM.x;
}

void fragment() {
	float on = step(0.6, fract(TIME * 0.8 + phase));
	ALBEDO = color * (0.3 + 4.0 * on);
}
