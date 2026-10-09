#!/usr/bin/env bash
# Builds Pocket Code as an Android app (APK) without Gradle.
#
# Needs: Java 17+, Python 3, npm, and the Android SDK with
#   platforms;android-34 and build-tools;34.0.0
# Usage:
#   ANDROID_HOME=/path/to/android-sdk ./build.sh
# Optional:
#   KEYSTORE=/path/key.jks KEYSTORE_PASS=secret  (defaults to ~/.pocketcode/release.jks, created on first run)
# Output: build/PocketCode.apk
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
APP="$(cd "$HERE/.." && pwd)"
SDK="${ANDROID_HOME:-${ANDROID_SDK_ROOT:-$HOME/Android/Sdk}}"
BT="$SDK/build-tools/${BUILD_TOOLS:-34.0.0}"
JAR="$SDK/platforms/${PLATFORM:-android-34}/android.jar"
OUT="$HERE/build"
KEYSTORE="${KEYSTORE:-$HOME/.pocketcode/release.jks}"
KEYSTORE_PASS="${KEYSTORE_PASS:-pocketcode}"

[ -f "$JAR" ] || { echo "android.jar not found at $JAR. Set ANDROID_HOME." >&2; exit 1; }
[ -x "$BT/aapt2" ] || { echo "build-tools not found at $BT." >&2; exit 1; }

rm -rf "$OUT"
mkdir -p "$OUT/assets/lib" "$OUT/npm" "$OUT/gen" "$OUT/classes" "$OUT/dex"

echo "1/6 Bundling the editor and its libraries for offline use"
python3 - "$APP/index.html" "$OUT/assets/index.html" "$OUT/npm" "$OUT/assets/lib" <<'PY'
import os, re, shutil, subprocess, sys, tarfile
src, dst, npm_dir, lib_dir = sys.argv[1:5]
html = open(src, encoding='utf-8').read()
urls = sorted(set(re.findall(r'https://cdn\.jsdelivr\.net/npm/([^"\']+)', html)))
packs = {}
for u in urls:
    spec, path = u.split('/', 1) if not u.startswith('@') else ('/'.join(u.split('/')[:2]), '/'.join(u.split('/')[2:]))
    if spec not in packs:
        tgz = subprocess.check_output(['npm', 'pack', spec, '--silent'], cwd=npm_dir, text=True).strip().splitlines()[-1]
        target = os.path.join(npm_dir, spec.replace('/', '_'))
        with tarfile.open(os.path.join(npm_dir, tgz)) as t:
            t.extractall(target, filter="data") if hasattr(tarfile, "data_filter") else t.extractall(target)
        packs[spec] = os.path.join(target, 'package')
    out = os.path.join(lib_dir, spec, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    shutil.copyfile(os.path.join(packs[spec], path), out)
html = html.replace('https://cdn.jsdelivr.net/npm/', 'lib/')
html = re.sub(r'\s*<link rel="(manifest|apple-touch-icon)"[^>]*>', '', html)
open(dst, 'w', encoding='utf-8').write(html)
print('   bundled', len(urls), 'library files')
PY

echo "2/6 Compiling resources"
"$BT/aapt2" compile --dir "$HERE/res" -o "$OUT/res.zip"
"$BT/aapt2" link -o "$OUT/unsigned.apk" -I "$JAR" --manifest "$HERE/AndroidManifest.xml" \
  -A "$OUT/assets" --java "$OUT/gen" --auto-add-overlay "$OUT/res.zip"

echo "3/6 Compiling Java"
find "$HERE/src" "$OUT/gen" -name '*.java' > "$OUT/sources.txt"
javac -nowarn -source 8 -target 8 -encoding UTF-8 -classpath "$JAR" -d "$OUT/classes" @"$OUT/sources.txt" 2>&1 | grep -v -e '^warning: \[options\]' -e '^Picked up JAVA_TOOL_OPTIONS' -e '^[0-9]* warning' || true
[ -n "$(find "$OUT/classes" -name '*.class' -print -quit)" ] || { echo "Java compile failed." >&2; exit 1; }

echo "4/6 Converting to Android bytecode"
# The d8 in build-tools 34 crashes on Java 21 class files, so use a newer D8 from Google's Maven repository.
R8_JAR="${R8_JAR:-$HOME/.pocketcode/r8-8.5.35.jar}"
if [ ! -f "$R8_JAR" ]; then
  mkdir -p "$(dirname "$R8_JAR")"
  curl -fsSL -o "$R8_JAR" https://dl.google.com/android/maven2/com/android/tools/r8/8.5.35/r8-8.5.35.jar
fi
find "$OUT/classes" -name '*.class' > "$OUT/classes.txt"
java -cp "$R8_JAR" com.android.tools.r8.D8 --release --min-api 24 --lib "$JAR" --output "$OUT/dex" $(cat "$OUT/classes.txt")
(cd "$OUT/dex" && zip -q -j "$OUT/unsigned.apk" classes.dex)

echo "5/6 Aligning"
"$BT/zipalign" -p -f 4 "$OUT/unsigned.apk" "$OUT/aligned.apk"

echo "6/6 Signing"
if [ ! -f "$KEYSTORE" ]; then
  mkdir -p "$(dirname "$KEYSTORE")"
  keytool -genkeypair -keystore "$KEYSTORE" -storepass "$KEYSTORE_PASS" -keypass "$KEYSTORE_PASS" -alias pocketcode \
    -keyalg RSA -keysize 2048 -validity 10000 -dname "CN=Pocket Code" 2>&1 | grep -v JAVA_TOOL_OPTIONS || true
fi
"$BT/apksigner" sign --ks "$KEYSTORE" --ks-pass "pass:$KEYSTORE_PASS" --ks-key-alias pocketcode --out "$OUT/PocketCode.apk" "$OUT/aligned.apk"
"$BT/apksigner" verify "$OUT/PocketCode.apk"
echo "Done: $OUT/PocketCode.apk ($(du -h "$OUT/PocketCode.apk" | cut -f1))"
