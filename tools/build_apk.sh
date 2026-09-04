#!/usr/bin/env bash
# Export the Android APK headlessly.
#   tools/build_apk.sh            # release build -> dist/BombFall.apk
#   tools/build_apk.sh debug      # debug build, signed with the debug key
#
# Needs: the godot binary (GODOT env var or on PATH), the matching export
# templates installed, and an Android SDK path configured in the editor
# settings (only platform-tools/adb and build-tools/apksigner are used).
# Release builds are signed with the keystore named by the standard Godot
# variables GODOT_ANDROID_KEYSTORE_RELEASE_PATH / _USER / _PASSWORD; when
# unset, a throwaway key is generated under ~/.local/share/godot/keystores.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT="${GODOT:-godot}"
MODE="${1:-release}"
mkdir -p dist
if [[ "$MODE" == "release" ]]; then
  if [[ -z "${GODOT_ANDROID_KEYSTORE_RELEASE_PATH:-}" ]]; then
    KS="$HOME/.local/share/godot/keystores/bombfall-release.keystore"
    if [[ ! -f "$KS" ]]; then
      mkdir -p "$(dirname "$KS")"
      keytool -genkeypair -v -keystore "$KS" -alias bombfall -keyalg RSA -keysize 2048 -validity 10950 \
        -storepass bombfall -keypass bombfall -dname "CN=BombFall,O=BombFall,C=CH" >/dev/null 2>&1
      echo "generated throwaway release keystore at $KS (alias bombfall, password bombfall)"
    fi
    export GODOT_ANDROID_KEYSTORE_RELEASE_PATH="$KS"
    export GODOT_ANDROID_KEYSTORE_RELEASE_USER="${GODOT_ANDROID_KEYSTORE_RELEASE_USER:-bombfall}"
    export GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD="${GODOT_ANDROID_KEYSTORE_RELEASE_PASSWORD:-bombfall}"
  fi
  "$GODOT" --headless --path . --import >/dev/null 2>&1 || true
  "$GODOT" --headless --path . --export-release Android dist/BombFall.apk
else
  "$GODOT" --headless --path . --import >/dev/null 2>&1 || true
  "$GODOT" --headless --path . --export-debug Android dist/BombFall-debug.apk
fi
ls -la dist/*.apk
