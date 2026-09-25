// Smoke puffs for particles: a camera-facing quad (the game camera never
// turns) turned into a soft, billowy disc by a noise texture. Colour and
// alpha come from the particle colour ramp; each puff spins its own way.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_disabled, shadows_disabled, fog_disabled;

uniform sampler2D noise_tex : hint_default_white, filter_linear, repeat_enable;

varying float spin;
varying float life;

void vertex() {
	spin = INSTANCE_CUSTOM.x + float(INSTANCE_ID) * 1.7;
	life = INSTANCE_CUSTOM.y;
}

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float c = cos(spin);
	float s = sin(spin);
	vec2 q = vec2(c * p.x - s * p.y, s * p.x + c * p.y);
	float n = texture(noise_tex, q * 0.35 + vec2(0.5 + spin * 0.13, 0.5 - life * 0.25)).r;
	float r = length(p) + (n - 0.5) * 0.7;
	float a = smoothstep(1.0, 0.25, r);
	ALBEDO = COLOR.rgb * (0.6 + 0.7 * n);
	ALPHA = a * COLOR.a;
}
