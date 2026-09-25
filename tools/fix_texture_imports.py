#!/usr/bin/env python3
"""Make every baked model texture import as a GPU-compressed texture.

Godot extracts the textures embedded in our .glb models next to them
(assets/models/<model>_<model>_{albedo,orm,normal}.jpg) and imports them
lossless, only switching to VRAM compression after its editor notices they
are used in 3D -- which a headless build never does. Uncompressed they would
cost ~5 MB of video memory each on a phone. This sets VRAM compression
(ETC2/ASTC on Android), mipmaps, and normal-map mode for normal maps.
Run it after `godot --import`, then import again. Idempotent.
"""
import glob
import os
import re
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")


def size_limit(path):
    """Largest size a baked map keeps in the game. The camera sees about
    61 px per metre: a 1024 atlas already matches that over a whole room, and
    256 still beats it on a 1-2 m prop. Normal and AO/roughness/metal maps
    carry softer detail, so they go one step smaller. The bakes stay bigger
    in the repository (and the APK stays under 100 MB)."""
    name = os.path.basename(path)
    kind = re.search(r"_(albedo|orm|normal)\.", name).group(1)
    if name.startswith(("backdrop_", "skybridge")):
        size = 1024
    elif name.startswith("ceiling_"):
        size = 512
    elif name.startswith("player_"):
        size = 1024
    else:
        size = 256     # still ~100 texels per metre on a 1-2 m prop
    if kind != "albedo":
        size //= 2
    return size


def fix(path):
    s = open(path).read()
    wanted = {
        "compress/mode": "2",
        # Normal maps as ordinary 4 bpp textures: Godot rebuilds the normal's
        # Z from X and Y anyway, and the two-channel format costs twice as much.
        "compress/normal_map": "2",
        "process/size_limit": str(size_limit(path)),
        "mipmaps/generate": "true",
        "detect_3d/compress_to": "0",
        "roughness/mode": "0",
    }
    changed = False
    for key, value in wanted.items():
        pat = re.compile(r"^%s=.*$" % re.escape(key), re.M)
        line = "%s=%s" % (key, value)
        if pat.search(s):
            if pat.search(s).group(0) != line:
                s = pat.sub(line, s)
                changed = True
        elif "[params]" in s:
            s = s.rstrip("\n") + "\n" + line + "\n"
            changed = True
    if changed:
        open(path, "w").write(s)
    return changed


def main():
    paths = []
    for ext in ("jpg", "jpeg", "png"):
        paths += glob.glob(os.path.join(ROOT, "assets", "models", "*_albedo.%s.import" % ext))
        paths += glob.glob(os.path.join(ROOT, "assets", "models", "*_orm.%s.import" % ext))
        paths += glob.glob(os.path.join(ROOT, "assets", "models", "*_normal.%s.import" % ext))
    n = sum(fix(p) for p in sorted(paths))
    print("fix_texture_imports: %d of %d texture imports updated" % (n, len(paths)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
