#!/bin/bash
# The Draft 1.8.1 fix, kept only to show its fault: it checks how the path
# starts, so /srv/pennant/builds/../../outside and the builds folder itself pass.
set -euo pipefail

DIR="${BUILD_DIR:?BUILD_DIR is not set}"
case "$DIR" in
  ""|"/"|"/*") echo "refusing to clean '$DIR'" >&2; exit 1 ;;
esac
case "$DIR" in
  /srv/pennant/builds/*) ;;
  *) echo "refusing to clean outside /srv/pennant/builds: '$DIR'" >&2; exit 1 ;;
esac
echo "cleaning $DIR"
rm -rf -- "${DIR:?}/"*
echo "clean done"
