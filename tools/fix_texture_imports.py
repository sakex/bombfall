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


def fix(path):
    s = open(path).read()
    normal = re.search(r"_normal\.(jpg|jpeg|png)\.import$", path) is not None
    wanted = {
        "compress/mode": "2",
        "compress/normal_map": "1" if normal else "2",
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
