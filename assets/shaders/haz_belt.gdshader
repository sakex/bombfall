shader_type spatial;
render_mode cull_disabled;
// The treadmill's running belt (blender/hazards.py treadmill): ribbed black
// rubber whose ribs scroll towards the model's -X (the belt's top always
// runs that way in model space; treadmill.gd mirrors the model to reverse).

uniform float speed = 1.1;           // metres per second
uniform float rib = 0.085;           // rib spacing in metres
uniform vec3 rubber : source_color = vec3(0.03, 0.03, 0.036);
uniform vec3 rib_color : source_color = vec3(0.075, 0.075, 0.09);

varying vec3 lp;

float hash(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

void vertex() {
	lp = VERTEX;
}

void fragment() {
	float x = (lp.x + TIME * speed) / rib;
	float r = smoothstep(0.35, 0.5, fract(x)) * (1.0 - smoothstep(0.62, 0.78, fract(x)));
	float grain = hash(floor(vec2(lp.x + TIME * speed, lp.z) * 140.0)) * 0.012;
	ALBEDO = mix(rubber, rib_color, r) + grain;
	ROUGHNESS = mix(0.82, 0.55, r);
	SPECULAR = 0.35;
}
