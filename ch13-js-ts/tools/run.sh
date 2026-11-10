#!/bin/bash
# Run under WSL: bash tools/run.sh
NODE=/root/.local/node22/bin/node
cd "$(dirname "$0")/../project"
$NODE --version
$NODE --experimental-strip-types --no-warnings --test tests/profile.test.ts 2>&1 | grep -E "^# (pass|fail)|not ok|rror"
$NODE --experimental-strip-types --no-warnings demo.ts original
$NODE --experimental-strip-types --no-warnings demo.ts fixed
