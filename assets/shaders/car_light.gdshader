// Flying-car light streaks: a bright core fading towards the tail.
shader_type spatial;
render_mode unshaded, cull_disabled;

varying vec2 uv;
varying vec4 tint;

void vertex() {
	uv = UV;
	tint = INSTANCE_CUSTOM;
}

void fragment() {
	float core = 1.0 - abs(uv.y - 0.5) * 2.0;
	ALBEDO = tint.rgb * (0.1 + core * 5.0);
}
