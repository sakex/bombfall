#!/usr/bin/env bash
# Rebuild every 3D model with headless Blender.
#   tools/build_models.sh            # export all blender/*.py to assets/models
#   tools/build_models.sh bomb coin  # only these
#   PREVIEW=1 tools/build_models.sh  # also render blender/previews/*.png
set -euo pipefail
cd "$(dirname "$0")/.."
BLENDER="${BLENDER:-blender}"
OUT="$PWD/assets/models"
ARGS=(--out "$OUT")
if [[ "${PREVIEW:-0}" == "1" ]]; then ARGS+=(--preview "$PWD/blender/previews"); fi
if [[ $# -gt 0 ]]; then
  scripts=("$@")
else
  scripts=()
  # Model scripts are the ones that call export(); the rest are shared kits.
  for f in blender/*.py; do
    n=$(basename "$f" .py)
    grep -qE '^\s*export\(' "$f" || continue
    scripts+=("$n")
  done
fi
fail=0
for n in "${scripts[@]}"; do
  if ! "$BLENDER" -b --python "blender/$n.py" -- "${ARGS[@]}" 2>&1 | grep -E "EXPORTED|PREVIEW|Error|Traceback|line [0-9]+" ; then
    echo "FAILED: $n"; fail=1
  fi
done
# Godot imports the extracted textures on its next --import; make them
# GPU-compressed once they exist (a second import applies the change).
if command -v godot >/dev/null 2>&1; then
  godot --headless --path . --import >/dev/null 2>&1 || true
  python3 tools/fix_texture_imports.py
  godot --headless --path . --import >/dev/null 2>&1 || true
fi
exit $fail
