// A blast's shockwave: a thin bright ring on a camera-facing quad that races
// outwards and thins away. `progress` 0..1 (set by explosion.gd).
shader_type spatial;
render_mode unshaded, blend_add, depth_draw_never, cull_disabled, shadows_disabled, fog_disabled;

instance uniform float progress = 1.0;

void fragment() {
	vec2 p = UV * 2.0 - 1.0;
	float r = length(p);
	float width = mix(0.16, 0.025, progress);
	float ring = smoothstep(width, 0.0, abs(r - 0.9));
	float haze = smoothstep(0.92, 0.3, r) * 0.18 * (1.0 - progress);
	float fade = (1.0 - progress) * (1.0 - progress);
	vec3 col = mix(vec3(1.0, 0.8, 0.55), vec3(1.0, 0.3, 0.75), progress);
	ALBEDO = col * (ring * 2.6 + haze) * fade;
}
