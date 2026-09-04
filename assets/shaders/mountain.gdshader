// Horizon mountains: black silhouettes with neon contour lines running
// around them, the way vector-scan landscapes were drawn.
shader_type spatial;
render_mode unshaded, cull_back;

uniform vec3 fill : source_color = vec3(0.03, 0.01, 0.06);
uniform vec3 line_color : source_color = vec3(0.9, 0.25, 0.8);
uniform float band = 7.0;

varying vec3 world_pos;
varying vec4 custom;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	custom = INSTANCE_CUSTOM;
}

void fragment() {
	float h = world_pos.y - custom.y;
	float c = fract(h / band);
	float fw = fwidth(h / band) * 1.5;
	float contour = 1.0 - smoothstep(0.0, fw + 0.04, abs(c - 0.5) - 0.02);
	float a = atan(world_pos.z - custom.z, world_pos.x - custom.x);
	float rc = fract(a * 12.0 / 6.2832);
	float ridge = 1.0 - smoothstep(0.0, fwidth(rc) * 1.5 + 0.02, abs(rc - 0.5) - 0.01);
	float fade = clamp(h / (custom.w + 0.001), 0.0, 1.0);
	ALBEDO = fill + line_color * (contour * 1.6 + ridge * 0.5) * (0.35 + 0.65 * fade);
}
