// Flat black cut-outs (palm trees) with a faint magenta rim from the sun.
shader_type spatial;
render_mode unshaded, cull_disabled;

uniform vec3 rim : source_color = vec3(0.9, 0.2, 0.6);

void fragment() {
	float f = pow(1.0 - abs(dot(normalize(NORMAL), normalize(VIEW))), 3.0);
	ALBEDO = vec3(0.01, 0.0, 0.02) + rim * f * 0.35;
}
