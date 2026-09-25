// Skyscraper facades: dark glass curtain walls with mullions and floor
// spandrels that reflect the sunset sky, and lit windows that open onto
// fake rooms with real depth (interior mapping: each window traces the view
// ray into a box and shades the wall, floor or ceiling it hits), so the
// city parallaxes like a real one as you fall. Some rooms flicker like TVs,
// a few switch on and off over time. Everything is computed from world
// position so the towers can be moved and recycled. INSTANCE_CUSTOM:
// x = hue shift, y = window density, z = tower top world Y, w = height.
shader_type spatial;
render_mode cull_back, unshaded;

uniform vec3 base_color : source_color = vec3(0.025, 0.012, 0.05);
uniform vec3 sun_tint : source_color = vec3(0.9, 0.25, 0.45);
uniform vec3 sun_dir = vec3(0.35, -0.2, -0.9);
uniform vec3 color_a : source_color = vec3(0.15, 0.9, 1.0);
uniform vec3 color_b : source_color = vec3(1.0, 0.25, 0.7);
uniform vec3 color_c : source_color = vec3(1.0, 0.75, 0.35);
uniform vec3 sky_low : source_color = vec3(0.85, 0.3, 0.45);
uniform vec3 sky_high : source_color = vec3(0.12, 0.04, 0.22);
uniform vec2 cell = vec2(1.15, 1.75);   // window bay width, floor height (m)
uniform float room_depth = 1.4;        // depth of the fake rooms, in bay widths
uniform float glow = 2.0;

varying vec3 world_pos;
varying vec3 world_normal;
varying vec4 custom;

void vertex() {
	world_pos = (MODEL_MATRIX * vec4(VERTEX, 1.0)).xyz;
	world_normal = normalize((MODEL_MATRIX * vec4(NORMAL, 0.0)).xyz);
	custom = INSTANCE_CUSTOM;
}

float hash2(vec2 p) {
	return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453);
}

// The colour of a lit room seen through a window: `p` is the point on the
// glass inside the bay (0..1, 0..1), `r` the view ray in facade space
// (x along the facade, y up, z into the building).
vec3 room(vec2 p, vec3 r, vec3 light, float h) {
	vec3 inv = 1.0 / max(abs(r), vec3(1e-4));
	float tx = (r.x > 0.0 ? 1.0 - p.x : p.x) * inv.x;
	float ty = (r.y > 0.0 ? 1.0 - p.y : p.y) * inv.y;
	float tz = room_depth * inv.z;
	float t = min(tx, min(ty, tz));
	vec3 hit = vec3(p + r.xy * t, r.z * t);   // x, y in 0..1, z = depth
	float depth = hit.z / room_depth;
	vec3 c;
	if (t == tz) {
		// Back wall: a lit wall with a framed picture or a screen.
		float art = step(0.3, hit.x) * step(hit.x, 0.7) * step(0.45, hit.y) * step(hit.y, 0.8);
		c = light * (0.95 + 0.4 * art * (h - 0.5));
	} else if (t == ty) {
		// Ceiling with a lamp, or the floor.
		c = r.y > 0.0 ? light * (0.7 + 0.8 * smoothstep(0.25, 0.0, length(hit.xz - vec2(0.5, room_depth * 0.5)) / 2.0))
		               : light * 0.28;
	} else {
		c = light * mix(0.62, 0.42, depth);   // side walls, darker further in
	}
	// Furniture: a dark band low on the far half of the room.
	c *= 1.0 - 0.55 * step(hit.y, 0.28) * step(0.45, depth);
	return c * mix(1.0, 0.7, depth);
}

void fragment() {
	float sun = clamp(dot(world_normal, -normalize(sun_dir)), 0.0, 1.0);
	vec3 shell = base_color + sun_tint * sun * 0.09;
	float up = clamp((world_pos.y - (custom.z - custom.w)) / max(custom.w, 1.0), 0.0, 1.0);
	shell = mix(shell + vec3(0.07, 0.01, 0.05), shell, smoothstep(0.0, 0.45, up));
	vec3 col = shell;
	vec3 view = normalize(world_pos - CAMERA_POSITION_WORLD);
	if (abs(world_normal.y) < 0.5) {
		bool along_x = abs(world_normal.z) > abs(world_normal.x);
		vec3 tangent = along_x ? vec3(sign(world_normal.z), 0.0, 0.0) : vec3(0.0, 0.0, -sign(world_normal.x));
		vec2 uv = vec2(dot(world_pos, tangent), world_pos.y);
		vec2 id = floor(uv / cell);
		vec2 f = fract(uv / cell);
		// Glass that reflects the sunset sky, brighter at grazing angles.
		vec3 refl = reflect(view, world_normal);
		float fres = pow(1.0 - clamp(dot(-view, world_normal), 0.0, 1.0), 3.0);
		vec3 sky = mix(sky_low, sky_high, clamp(refl.y * 1.6 + 0.35, 0.0, 1.0));
		vec3 glass = shell * 0.8 + sky * (0.05 + 0.35 * fres);
		// Mullions every bay, a spandrel (floor slab) band every floor.
		float mullion = step(f.x, 0.09) + step(0.91, f.x);
		float spandrel = step(f.y, 0.3);
		float frame = clamp(mullion + spandrel, 0.0, 1.0);
		// Which rooms are lit: density per tower, whole dark floors, and a
		// slow random switching so the city is alive.
		float floor_dark = step(0.15, hash2(vec2(id.y, custom.x * 91.0)));
		float h = hash2(id + custom.x * 13.0);
		float h2 = hash2(id * 1.7 + 3.1 + custom.x);
		float epoch = floor(TIME / (18.0 + 30.0 * h2) + h * 7.0);
		float swap = step(0.93, hash2(id + epoch));
		float lit = abs(step(1.0 - custom.y * 0.62, h) * floor_dark - swap);
		vec3 tint = mix(mix(color_a, color_b, step(0.45, h2)), color_c, step(0.8, h2));
		// TV rooms flicker; others breathe very slightly.
		float tv = step(0.9, hash2(id * 3.3 + custom.x));
		float flicker = mix(0.9 + 0.1 * sin(TIME * (0.6 + h2 * 2.5) + h * 30.0),
		                    0.6 + 0.4 * hash2(vec2(floor(TIME * 9.0), h)), tv);
		vec3 r = vec3(dot(view, tangent), view.y, dot(view, -world_normal));
		vec2 p = vec2((f.x - 0.09) / 0.82, (f.y - 0.3) / 0.7);
		// Blinds pulled part way down in some rooms.
		float blinds = step(1.0 - hash2(id * 2.1 + custom.x) * 0.6, p.y) * step(0.5, h2);
		vec3 inside = room(p, r, tint * glow * (0.5 + 0.5 * h) * flicker, h);
		inside = mix(inside, tint * glow * 0.35 * flicker, blinds);
		vec3 win = mix(glass, inside + sky * 0.08 * fres, lit);
		float band = step(0.93, fract(uv.y / (cell.y * 12.0))) * 0.9;
		float roof = smoothstep(0.9, 0.0, custom.z - world_pos.y) * 1.2;
		col = mix(win, shell * 0.55 + sky * 0.03, frame) + color_b * band + color_a * roof;
	} else if (world_normal.y > 0.5) {
		col = shell * 0.6 + color_a * 0.05;
	}
	ALBEDO = col;
}
