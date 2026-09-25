# BombFall asset style guide

How the 3D assets are built, and the bar they are held to. Every model is a
Python script in `blender/` run by headless Blender; nothing is hand-edited.

## Art direction

**Realistic, premium, animated — inside a neon synthwave hotel.** Think of a
high-end mobile game or a toy-like animated film: believable manufactured
objects with correct proportions, real materials and construction detail, lit
by neon. Not photoreal clutter, not flat low-poly.

- **Silhouette first.** At game distance a 1.5 m prop is ~90 px tall. Shapes
  must read instantly: strong, specific outlines, clear part separation.
- **Real construction.** Things are built the way they are manufactured:
  rounded (bevelled) edges everywhere, panel seams, screws/rivets, hinges,
  feet, cable runs, vents, labels, trims, gaskets. Nothing is a bare box.
- **Material contrast.** Every object mixes 2–4 materials (painted metal +
  chrome trim + rubber feet + glossy plastic panel …). Values and roughness
  should differ so parts separate even without colour.
- **Wear tells stories.** Edges are worn, crevices hold grime, bare metal
  shows through paint on handles and corners. Keep it tasteful (this is a
  luxury hotel that has seen some parties), not post-apocalyptic.
- **Neon is the accent, not the surface.** Emissive strips, screens and LEDs
  outline and punctuate. Big surfaces are real materials.
- **Palette.** Dark navy/plum/gunmetal bases; neon pink, magenta, cyan,
  violet, sunset orange/yellow accents; chrome and gold for luxury.
- **Everything that could move, moves.** See Animation below.

## Scale and camera

- 1 Blender unit = 1 metre = 1 game cell. Z up in Blender (Y up in Godot).
- The **front faces Blender -Y** (towards the game camera = Godot +Z).
- Floor props: origin at bottom centre (z = 0 is the floor). Tumbling things
  (bomb, coin, drone): origin at their centre.
- Game camera: 30 m away, 17.6 m wide on a 1080 px portrait screen, so about
  **61 px per metre** on a phone. The menu and previews get closer.
- Play plane is z = 0 in Godot; rooms are behind it (backdrop decor spans
  Blender y 0 … 1.85, the back wall is at y ≈ 1.9).

## The kit (`blender/common.py`)

```python
from common import *          # always
clean_scene()
m = pbr("paint", (0.08, 0.09, 0.12))             # dark painted metal, worn edges
cube((1, 0.5, 0.8), (0, 0, 0.4), m, bevel=0.03)
export("my_model")                                 # bakes + exports + preview
```

### Materials: `pbr(kind, colour, **opts)`

Procedural Cycles node trees (Bevel-node rounded edges, AO grime in crevices,
noise breakup of colour and roughness, scratches, bump). `export()` bakes
them into three maps per model (albedo, AO/roughness/metal, normal).

| kind | use for |
|---|---|
| `paint` | painted metal; edges wear through to bare steel |
| `metal` | bare/brushed steel, aluminium (brushed streaks) |
| `chrome` | polished chrome, mirror trims |
| `gold` | gold/brass fittings |
| `plastic` | ABS/moulded plastic, lacquer |
| `rubber` | tyres, feet, grips, cable sheaths |
| `fabric` | upholstery, bedding, curtains (`color2` = weave tone) |
| `leather` | sofas, chairs, belts |
| `wood` | varnished wood (`color2` = grain tone) |
| `ceramic` | porcelain, tiles, sinks |
| `marble` | stone (`color2` = vein colour) |
| `concrete` | plaster, concrete, render |
| `carpet` | rugs, carpet |
| `skin` | soft organic (the hero's cheeks, the bat's membrane) |
| `neon` | emissive tubes/LEDs: `pbr("neon", CYAN, strength=5)` — not baked |
| `screen` | emissive screens (flat) — not baked |
| `glass` | transparent glass (`alpha=0.3`) — not baked |

Options: `rough`, `metal`, `wear` (0–1), `grime` (0–1), `bump` (0–1), `edge`
(bevel radius in metres, default ~1 cm), `scale` (feature size), `color2`,
`name`. Legacy tuples (`METAL_DARK`, `NEON_CYAN`, `(WHITE, 0.3, 0.0)`) still
work and are routed to the nearest kind — but new code should call `pbr()`.

`anim(spec, "screen" | "marquee")` makes an emissive material the game swaps
for an animated shader at load (rolling scanlines / chasing marquee dots) on
**any** model. Use it for every screen, display and marquee.

### Export and bake: `export(name, tex=None, ground=None, ao_distance=None)`

- `tex`: atlas size. Defaults by size: <0.5 m → 256, <2.2 m → 512,
  <7 m → 1024, else 2048. Budgets: tiles 256; small pickups 256–512; props
  512–1024; the hero 1024; backdrops 2048; ceilings 1024.
- `ground`: adds a floor under the model while baking so the base gets a
  contact shadow (defaults on for floor props).
- Environment variables: `NO_BAKE=1` skips the bake (fast iteration: the
  preview then renders the live procedural materials), `BAKE_TEX=256` forces a
  small atlas, `BAKE_DUMP=dir` writes the baked maps as PNGs.
- Bake time is ~1 min per 1024² model on this machine (4 cores shared by
  everyone). Iterate with `NO_BAKE=1`, bake for the final export.

### Geometry helpers

`cube cyl cone sphere ico torus plane rod wedge slab wall_panel` (all take a
material and optional `bevel`, `parent`), `pivot(name, loc)` (a named Empty
= a Node3D the game or an animation moves), `attach`, `join`, `join_static`
(merge every non-pivoted mesh into one: always call it before export),
`mirror_copy`. Raw `bpy` is fine for anything more sculpted: bmesh, curves
converted to mesh, Subdivision Surface / Solidify / Array / Screw / Boolean
modifiers (modifiers are applied at bake time; armature modifiers are kept).

### Polygon budgets (triangles after modifiers)

tiles ≤ 400 (hundreds on screen) · coin ≤ 800 · bomb ≤ 3 000 · pickups
≤ 2 500 · props ≤ 6 000 (large ones ≤ 9 000) · hero ≤ 15 000 · boss
≤ 12 000 · backdrop ≤ 14 000 · ceiling ≤ 5 000. Spend polygons on silhouette
and curvature; the normal map carries small detail.

## Animation

```python
spin(p, "idle", "Z", seconds=2.0, turns=2)          # constant rotation loop
wobble(p, "idle", "location", 2, 0.05, seconds=2)   # seamless sine on one channel
key(p, "fire", "rotation_euler", [(0, (0,0,0)), (4, (0.3,0,0)), (12, (0,0,0))])
```

- Frames are at 30 fps. Start every clip from the rest pose at frame 0:
  `export()` evaluates the scene at frame 0 for the rest pose.
- `export(tex=N)` wins over the `BAKE_TEX` environment variable. Keys go on **pivots** (Empties) or armature bones.
- A clip is named by its second argument; all objects' keys for the same name
  export as one glTF animation.
- **`idle`** loops and auto-plays on every instance with a random phase (the
  Game autoload does it). Clips named `<name>_loop` also loop — Godot's
  importer strips the suffix, so in the game the clip is called `<name>`. Anything else is
  a one-shot the game plays with `ModelUtil.play(model, "clip")`, which then
  returns to `idle`.
- **Every part of one clip must share its period**: the clip lasts as long as
  its longest track, so a 1 s spin in a 2 s idle stops half the time. Pick
  one length (2 s or 4 s) per model and make spins whole turns over it.
- Constant tracks are stripped at load, but never keyframe a node the game
  script also moves (see the contracts below) — pick one owner per node.
- glTF cannot animate materials here: blink an LED by scaling a small
  emissive mesh, use `anim()` screens, or let the game script drive it.
- Characters: an Armature with a skinned mesh, bone keys through
  `key(armature, "run", 'pose.bones["thigh.L"].rotation_quaternion', …)`.
  Skinning survives the bake. Rigid parts can be bone-parented.

## Node-name contracts (the game looks these up)

| model | names the scripts expect |
|---|---|
| player | `leg_l leg_r arm_l arm_r eye_l eye_r antenna scarf jet_l jet_r` (until the hero rework replaces the code) |
| bomb | meshes `ring`, `display`, `fuse` (their materials are recoloured) |
| drone | `rotor_1` … `rotor_4` (spun in code) |
| wall_gun | `gun` (aimed in code) |
| treadmill | `roller_1` … (spun in code) |
| button | `top` (pressed in code) |
| light_ring | mesh `glow` |
| air_fan | `blades` |
| bumper | mesh `cap_light` |
| slot_machine | `lever`, `reel_1` … `reel_3`, mesh `marquee` |
| arcade_cabinet | meshes `screen`, `marquee` |
| desktop | `monitor` |
| painting | `canvas` |
| boss_bat | rigged: bone `jaw` (code-driven), meshes `eyes`, `heart_glow`; clips `idle`, `fall` |
| vault_door | `wheel`, mesh `lock_light` |
| backdrop/ceiling | any `spin_*` (rotates) / `sway_*` (swings) pivot |

Rename or remove one only together with the GDScript that uses it.

## Checking your work

```sh
blender -b --python blender/<name>.py -- --preview blender/previews     # bake + export + preview
NO_BAKE=1 blender -b --python blender/<name>.py -- --preview /tmp/pv    # fast look
```

Then in Godot (always under the shared lock — several people import at once):

```sh
flock /tmp/godot.lock timeout 900 godot --headless --path . --import
export VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/lvp_icd.x86_64.json:/usr/share/vulkan/icd.d/lvp_icd.json
flock /tmp/godot.lock timeout 590 xvfb-run -a -s "-screen 0 1080x1920x24" godot --path . \
  src/dev/gallery.tscn --rendering-driver vulkan --rendering-method mobile --resolution 540x960 -- \
  --items=res://src/spawnables/toilet.tscn,res://src/actors/bomb.tscn --zoom=8 --theme=room1 \
  --screenshot=/tmp/shot.png:2.5
```

`--zoom` is the view width in metres, `--game-scale` shows the real in-game
size, `--turn=30` yaws the items, `--at=0.5` freezes animations halfway.
Full game: `src/game/game.tscn -- --theme=casino --screenshot=…`, special
rooms: `src/dev/special_test.tscn -- --special=vault`.

After a first import of a new model, run `python3 tools/fix_texture_imports.py`
and import again: it makes the baked textures GPU-compressed (the build
scripts do this automatically).

Regression (must stay green): `src/dev/physics_test.tscn`,
`src/dev/hitbox_audit.tscn` (collision shapes vs. mesh), `src/dev/doable_test.tscn`,
`src/dev/smoke_test.tscn`. If a model's size changes, update its collision
shapes in the `.tscn` (or `tools/gen_prop_scenes.py` for simple props).
