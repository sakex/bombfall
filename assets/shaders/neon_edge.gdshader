// Neon strips: per-instance colour from vertex colour, boosted for glow.
shader_type spatial;
render_mode unshaded, cull_back;

uniform float intensity = 3.0;

void fragment() {
	ALBEDO = COLOR.rgb * intensity;
}
