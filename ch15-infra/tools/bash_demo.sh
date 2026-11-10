#!/bin/bash
# Run the clean-up scripts with a PATH that contains ONLY the fake rm, so nothing
# can be deleted. Run under WSL as root: bash tools/bash_demo.sh
# For the folder checks it creates /srv/pennant/builds/release-42 (an empty
# folder) and /srv/pennant/builds/release-link (a link to /etc), and removes
# only what it created when it finishes.
HERE="$(cd "$(dirname "$0")/.." && pwd)"
chmod +x "$HERE/project/fakebin/rm"
ROOT=/srv/pennant/builds
CREATED=()
for d in /srv /srv/pennant "$ROOT" "$ROOT/release-42"; do
  if [ ! -e "$d" ]; then /bin/mkdir "$d" && CREATED+=("$d"); fi
done
if [ ! -e "$ROOT/release-link" ] && [ ! -L "$ROOT/release-link" ]; then
  /bin/ln -s /etc "$ROOT/release-link" && CREATED+=("$ROOT/release-link")
fi

run() {  # run <label> <script> [BUILD_DIR value; omit for unset]
  echo "== $1"
  if [ $# -ge 3 ]; then
    env -i PATH="$HERE/project/fakebin" BUILD_DIR="$3" /bin/bash "$HERE/$2" 2>&1
  else
    env -i PATH="$HERE/project/fakebin" /bin/bash "$HERE/$2" 2>&1
  fi
  echo "exit=$?"
}

O=project/clean_build.sh
F=answer-key/clean_build_fixed.sh
R=tools/regression/clean_build_fixed_v1_8_1.sh
run "original, set" $O "$ROOT/release-42"
run "original, empty" $O
run "fixed, set" $F "$ROOT/release-42"
run "fixed, empty" $F
run "fixed, dot-dot" $F "$ROOT/../../outside"
run "fixed, builds root" $F "$ROOT/"
run "fixed, link" $F "$ROOT/release-link"
run "fixed, nested" $F "$ROOT/release-42/sub"
run "v1.8.1 fix, dot-dot" $R "$ROOT/../../outside"
run "v1.8.1 fix, builds root" $R "$ROOT/"

# Remove only what this script created, newest first.
for (( i=${#CREATED[@]}-1; i>=0; i-- )); do
  p="${CREATED[$i]}"
  if [ -L "$p" ]; then /usr/bin/unlink "$p"; else /bin/rmdir "$p"; fi
done
