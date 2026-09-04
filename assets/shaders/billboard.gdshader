// Animated holographic advert: scrolling neon bands and a pulsing frame.
shader_type spatial;
render_mode unshaded, cull_back;

uniform vec3 color_a : source_color = vec3(1.0, 0.2, 0.7);
uniform vec3 color_b : source_color = vec3(0.2, 0.9, 1.0);
uniform float speed = 0.35;
uniform float bands = 6.0;

void fragment() {
	vec2 uv = UV;
	float t = fract(uv.y * bands - TIME * speed);
	float band = smoothstep(0.1, 0.25, t) * smoothstep(0.9, 0.75, t);
	float frame = step(0.04, uv.x) * step(uv.x, 0.96) * step(0.04, uv.y) * step(uv.y, 0.96);
	vec3 col = mix(color_a, color_b, 0.5 + 0.5 * sin(uv.x * 6.283 + TIME));
	float glyph = step(0.5, fract(uv.x * 9.0 + floor(uv.y * bands) * 0.37 + floor(TIME * 2.0) * 0.13));
	vec3 e = col * (band * glyph * 2.5 + (1.0 - frame) * 3.0) + color_b * 0.15;
	ALBEDO = e + vec3(0.02);
}
