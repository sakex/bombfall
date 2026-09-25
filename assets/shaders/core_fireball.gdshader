// The explosion's fireball: a noise-displaced sphere whose colour runs from
// a white-hot core through orange and red to dark smoke at the rim, with
// billows scrolling up and outwards. `heat` (0..1) is the blast's intensity
// and `age` (0..1) its life: as it ages the fire cools into smoke and the
// ball erodes into wisps. Unshaded and emissive (HDR), so it blooms.
shader_type spatial;
render_mode unshaded, blend_mix, depth_draw_never, cull_back, shadows_disabled, fog_disabled;

instance uniform float heat = 1.0;
instance uniform float age = 0.0;
instance uniform float seed = 0.0;
uniform float billow = 0.32;

varying vec3 p_obj;

float hash(vec3 p) {
	p = fract(p * 0.3183099 + vec3(0.71, 0.113, 0.419));
	p *= 17.0;
	return fract(p.x * p.y * p.z * (p.x + p.y + p.z));
}

float vnoise(vec3 x) {
	vec3 i = floor(x);
	vec3 f = fract(x);
	f = f * f * (3.0 - 2.0 * f);
	return mix(mix(mix(hash(i), hash(i + vec3(1.0, 0.0, 0.0)), f.x),
				   mix(hash(i + vec3(0.0, 1.0, 0.0)), hash(i + vec3(1.0, 1.0, 0.0)), f.x), f.y),
			   mix(mix(hash(i + vec3(0.0, 0.0, 1.0)), hash(i + vec3(1.0, 0.0, 1.0)), f.x),
				   mix(hash(i + vec3(0.0, 1.0, 1.0)), hash(i + vec3(1.0, 1.0, 1.0)), f.x), f.y), f.z);
}

float fbm(vec3 p) {
	float s = 0.0;
	float a = 0.5;
	for (int i = 0; i < 3; i++) {
		s += a * vnoise(p);
		p = p * 2.07 + vec3(5.3, 1.7, 9.1);
		a *= 0.5;
	}
	return s / 0.875;
}

void vertex() {
	vec3 q = VERTEX * 2.1 + vec3(seed, -TIME * 0.9 + seed * 0.37, seed * 0.61);
	float n = fbm(q);
	// Billows push out more as the ball grows old and turns to smoke.
	VERTEX += NORMAL * (n - 0.45) * (billow + 0.25 * age);
	p_obj = VERTEX;
}

vec3 fire_ramp(float t) {
	vec3 smoke = vec3(0.09, 0.07, 0.11);
	vec3 ember = vec3(0.55, 0.12, 0.12);
	vec3 red = vec3(2.2, 0.42, 0.06);
	vec3 orange = vec3(4.2, 1.7, 0.35);
	vec3 white = vec3(6.5, 5.2, 3.4);
	vec3 c = mix(smoke, ember, smoothstep(0.08, 0.3, t));
	c = mix(c, red, smoothstep(0.3, 0.48, t));
	c = mix(c, orange, smoothstep(0.48, 0.7, t));
	c = mix(c, white, smoothstep(0.78, 0.98, t));
	return c;
}

void fragment() {
	float facing = clamp(dot(normalize(NORMAL), normalize(VIEW)), 0.0, 1.0);
	vec3 q = p_obj * 2.6 + vec3(seed * 1.3, -TIME * 1.6, seed);
	float n = fbm(q);
	float fine = vnoise(p_obj * 7.0 + vec3(0.0, -TIME * 3.0, seed));
	float t = facing * 0.95 + (n - 0.5) * 0.9 + (fine - 0.5) * 0.25;
	t = t * (0.35 + 0.75 * heat) - age * 0.55;
	ALBEDO = fire_ramp(t);
	// Soft rim, then erosion by the noise as the blast dies away.
	float a = smoothstep(0.0, 0.35, facing + (n - 0.5) * 0.5);
	float erode = smoothstep(age * 1.05 - 0.05, age * 1.05 + 0.2, n + facing * 0.35);
	ALPHA = clamp(a * erode * min(heat * 1.6, 1.0), 0.0, 1.0);
}
