# 15_01: The clean-up that would have deleted everything

**Book:** Chapter 15, Scenario 1 (Bash): the clean-up that would have deleted everything.

Pennant Print Works clears the previous build with a three-line script. If `BUILD_DIR` isn't set, it asks `rm -rf` to delete every top-level folder on the machine, and then prints "clean done". Make it stop with an error when `BUILD_DIR` is missing or empty, and refuse any path that isn't one real build folder directly under `/srv/pennant/builds`: a path with `..` in it, the builds root itself, a link and a nested path. Done means every refusal happens before `rm` is called, with a message and an error exit, while a real build folder is still cleaned.

**Files:** `begin/clean_build.sh` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch15-infra` folder, run `python check.py`. Never run the script yourself: the checker runs it only with a stand-in `rm` that deletes nothing (see `../README.md`).

**Hint:** start with `set -euo pipefail` and `${BUILD_DIR:?...}`. Then take the builds root off the front of the path, and ask what's left.
