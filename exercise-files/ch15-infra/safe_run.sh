#!/bin/bash
# Runs one clean-up script safely, the way the chapter's own tools/bash_demo.sh does:
# with env -i and a PATH that contains ONLY the stand-in rm in data/fakebin, which
# prints what it would delete and deletes nothing. check.py calls this, as root
# under WSL Ubuntu on Windows. Usage: bash safe_run.sh <script>
# For the folder checks it creates /srv/pennant/builds/release-42 (an empty
# folder) and /srv/pennant/builds/release-link (a link to /etc), and removes
# only what it created when it finishes. One addition to bash_demo.sh: the script
# itself runs as the unprivileged user nobody, so even a mistake that reached a
# real command couldn't delete system files.
HERE="$(cd "$(dirname "$0")" && pwd)"
FAKEBIN="$HERE/data/fakebin"
SCRIPT="$1"
if [ "$EUID" -ne 0 ] || [ ! -x /usr/sbin/runuser ]; then
  echo "SETUP FAILED: safe_run.sh needs root and runuser, to create the test folders and then drop to the user nobody"
  exit 2
fi
chmod +x "$FAKEBIN/rm"
ROOT=/srv/pennant/builds
CREATED=()

cleanup() {  # Remove only what this script created, newest first.
  for (( i=${#CREATED[@]}-1; i>=0; i-- )); do
    p="${CREATED[$i]}"
    if [ -L "$p" ]; then /usr/bin/unlink "$p"; else /bin/rmdir "$p"; fi
  done
}
trap cleanup EXIT

for d in /srv /srv/pennant "$ROOT" "$ROOT/release-42"; do
  if [ ! -e "$d" ]; then /bin/mkdir "$d" && CREATED+=("$d"); fi
done
if [ ! -e "$ROOT/release-link" ] && [ ! -L "$ROOT/release-link" ]; then
  /bin/ln -s /etc "$ROOT/release-link" && CREATED+=("$ROOT/release-link")
fi
if [ ! -d "$ROOT/release-42" ]; then
  echo "SETUP FAILED: couldn't create $ROOT/release-42 (run as root, in WSL or a throwaway machine)"
  exit 2
fi

run() {  # run <label> [BUILD_DIR value; omit for unset]
  echo "== $1"
  if [ $# -ge 2 ]; then
    /usr/sbin/runuser -u nobody -- /usr/bin/env -i PATH="$FAKEBIN" BUILD_DIR="$2" /bin/bash "$SCRIPT" 2>&1
  else
    /usr/sbin/runuser -u nobody -- /usr/bin/env -i PATH="$FAKEBIN" /bin/bash "$SCRIPT" 2>&1
  fi
  echo "exit=$?"
}

run "set" "$ROOT/release-42"
run "unset"
run "empty" ""
run "dot-dot" "$ROOT/../../outside"
run "builds root" "$ROOT/"
run "link" "$ROOT/release-link"
run "nested" "$ROOT/release-42/sub"
