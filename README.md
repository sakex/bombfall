# BombFall

Fall through a neon hotel. Bombs rain from above: their blasts punch holes
through the floors you stand on, so ride them down, dodge the drones, wall
guns and lasers, push the furniture around, and grab coins and shields on
the way. The deeper you get, the faster it comes.

This is the 3D remake of the original 2D BombFall (Godot 3 + Rust). Same
game, same tuning, rebuilt on **Godot 4.7** with every asset modelled in
**Blender** from scripts, a procedurally lit cyberpunk city behind the
hotel's windows, and a single-language GDScript code base.

![Gameplay](docs/screenshots/gameplay.png)

## Play it

* **Android:** [`dist/BombFall.apk`](dist/BombFall.apk) (arm64, signed with a
  throwaway key, so it installs as a fresh app next to the store version).
  The GitHub Actions workflow rebuilds it on every push and attaches the APK
  as an artifact.
* **Desktop:** open the folder in Godot 4.7 and press play, or
  `godot --path .`. Keys: `A`/`D` or arrows to move, `Space`/`W`/`Up` to
  jump, `Esc` to pause. Mouse clicks act as touches on the on-screen buttons.

## Layout

| Path | What |
|---|---|
| `project.godot` | Godot 4.7 project: mobile renderer, Jolt physics, portrait 1080x1920. |
| `src/autoload/` | Singletons: `SaveData` (profile JSON, same keys as the original save), `Music` (playlist that survives scene changes), `Services` (ads/backend interfaces), `Game` (scene routing). |
| `src/actors/` | Player, bomb, explosion, coin and the `PlanarBody` base that pins rigid bodies to the XY plane. |
| `src/world/` | The generator: `World` (storey ring buffer, bomb rain, garbage collection), `Level` (layout on a `BinaryGrid`), `SpawnRegistry` (every prop with footprint, difficulty and the room themes), `CellGrid` (destructible floors/walls as PhysicsServer bodies + one MultiMesh per cell kind), `Backdrop` (themed rooms with window openings), `City` (the parallax skyline). |
| `src/spawnables/` | Hazards and furniture: drone, wall gun, light ring laser, trampoline, treadmill, pressure button, fire zone, ropes, pick-ups, pushable props. |
| `src/special_levels/` | The junk wall, the obstacle course and the bat boss arena, inserted every ten storeys. |
| `src/game/`, `src/main/`, `src/ui/` | Run scene, tutorial, camera rig, main menu with live preview, store, settings, leaderboard, credits, HUD. |
| `src/dev/` | Headless smoke test, a sandbox and a harness that forces a special level (excluded from exports). |
| `blender/` | One Python script per model plus `common.py` (primitives, neon materials, glTF export, preview render), `props.py` (set dressing kit) and `furniture.py` / `hazards.py` (prop builders). `blender/previews/` holds a render of each model. |
| `assets/models/` | The exported `.glb` files, committed so the game builds without Blender. |
| `assets/shaders/` | Facade, beacon, car-light, billboard and sky shaders of the city. |
| `tools/` | `build_models.sh` (rebuild all models), `build_apk.sh` (headless Android export), `gen_prop_scenes.py`. |

## Rebuilding the models

```sh
tools/build_models.sh              # every model -> assets/models/*.glb
tools/build_models.sh bomb player  # just these
PREVIEW=1 tools/build_models.sh    # also render blender/previews/*.png
```

Needs Blender 4.0+ on the PATH (`BLENDER=/path/to/blender` to override).
Each script runs with `blender -b --python blender/<name>.py`, builds the
model from primitives with named pivots the game animates (`leg_l`,
`rotor_1`, `wing_r`, `gun`, `top`...), joins the static parts into one mesh
and exports glTF with the Y-up conversion. One unit is one metre, which is
one hotel cell (the 2D game used 64 px cells).

## Building the APK

```sh
tools/build_apk.sh            # release -> dist/BombFall.apk
tools/build_apk.sh debug      # debug build
```

Requirements: the Godot 4.7.2 editor binary on the PATH (or `GODOT=...`),
its export templates installed, JDK 17, and an Android SDK path set in the
editor settings (`export/android/android_sdk_path`). Only `platform-tools/adb`
and `build-tools/<v>/apksigner` are used because the export does not use a
Gradle build. To sign with your own key, set
`GODOT_ANDROID_KEYSTORE_RELEASE_PATH`, `_USER` and `_PASSWORD` before running
the script; the CI workflow reads them from repository secrets.

The package name is `ch.senges.bombfall`; change `package/unique_name` in
`export_presets.cfg` if the store listing uses another one.

## Headless checks

```sh
godot --headless --path . --import
godot --headless --path . res://src/dev/smoke_test.tscn     # 40 s scripted run
godot --path . res://src/dev/special_test.tscn -- --special=boss_bat_arena
godot --path . -- --theme=gym --screenshot=shot.png:2       # any scene, saves a frame
```

## What changed from the original

* **Godot 3.5 to 4.7.** New scene format, `CharacterBody3D`/`RigidBody3D`
  with Jolt, typed GDScript, `max_polyphony` instead of four audio players,
  autoloads instead of hand-carrying the music player between scenes.
* **Rust/GDNative dropped.** GDNative does not exist in Godot 4 and the
  level generator was tile-map specific anyway; it is now `src/world/`, in
  GDScript, about the same size and easier to tweak. Nothing else in the
  game touched Rust.
* **2D to 3D.** Gameplay still happens on a plane (bodies are axis-locked),
  so every number from the original survives: bomb timers, blast radius,
  jump height, spawn tables and shield item odds. Floors and walls are
  destructible cells rendered with a MultiMesh; rooms are real boxes two
  metres deep with set dressing and windows onto a city that parallaxes as
  you fall.
* **Ads and Firebase are stubbed** (`src/autoload/services.gd`). Neither
  SDK can be bundled in a headless build (both need Google's Maven at build
  time). The interfaces are small: plug real implementations in and the
  store, leaderboard and revive flow use them. Until then reviving costs
  coins instead of an ad, the leaderboard is local, and the username is
  stored on the device.
* **Save files are compatible.** `user://save_game.json` keeps the same keys,
  so coins, upgrades and scores carry over.

Music by Karl Casey @ White Bat Audio. Font: KARIXBY.
