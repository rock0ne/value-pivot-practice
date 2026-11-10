#!/bin/bash
# The fix: stop on any unset variable or failed command, and only ever delete
# inside one build folder, named directly under the builds root.
set -euo pipefail

ROOT=/srv/pennant/builds
DIR="${BUILD_DIR:?BUILD_DIR is not set}"
NAME="${DIR#"$ROOT"/}"
if [ "$NAME" = "$DIR" ]; then
  echo "refusing to clean outside $ROOT: '$DIR'" >&2; exit 1
fi
case "$NAME" in
  ""|.|..|*/*|*[!A-Za-z0-9._-]*)
    echo "refusing to clean '$DIR': not one build folder directly under $ROOT" >&2; exit 1 ;;
esac
if [ -L "$DIR" ] || [ ! -d "$DIR" ]; then
  echo "refusing to clean '$DIR': not a real folder" >&2; exit 1
fi
echo "cleaning $DIR"
rm -rf -- "$DIR/"*
echo "clean done"
