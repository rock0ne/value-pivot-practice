#!/bin/bash
# Clear the previous build before a release (Pennant Print Works, fictional).
# Written as an AI assistant might write it, to show a common failure pattern.
# BUILD_DIR is set by the CI job.

DIR="$BUILD_DIR"
echo "cleaning $DIR"
rm -rf "$DIR/"*
echo "clean done"
