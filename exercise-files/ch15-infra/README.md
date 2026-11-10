# Chapter 15 exercise files: infrastructure, pipelines and scripts

Two exercises, one for each of the chapter's scenarios. Run `python check.py` in this folder to check your work, or `python check.py --end` to check the answers.

**What you need:** Python 3.10 or newer with PyYAML (`python -m pip install pyyaml`) for 15_02, and Bash for 15_01. On Windows, 15_01 runs under WSL Ubuntu, as the chapter's own checker does.

**How 15_01 is kept safe.** The clean-up script calls `rm -rf`, so the checker never runs it the ordinary way. It runs it only through `safe_run.sh`, which copies the chapter's `tools/bash_demo.sh`:

- The script runs with `env -i` and a PATH that holds nothing but the stand-in `rm` in `data/fakebin`. The stand-in prints what it was asked to delete, and deletes nothing.
- `safe_run.sh` runs as root, because it creates two test items: an empty folder, `/srv/pennant/builds/release-42`, and a link to `/etc`, `/srv/pennant/builds/release-link`. It removes only what it created when it finishes. One addition to the chapter's approach: your script itself runs as the unprivileged user `nobody`.
- Before any of that, `check.py` reads your script and won't run it if it could reach a real command another way: an absolute path such as `/bin/rm`, a change to PATH, `eval`, `exec`, `source`, command substitution, `../`, or a redirection that writes to a file. That's a guard against mistakes, not a sandbox, so don't try to get round it.

On Windows, `check.py` calls `wsl -d Ubuntu -u root`. On Linux it runs `safe_run.sh` directly, which needs root, so use a throwaway container or virtual machine, never your own computer. Never run `clean_build.sh` yourself.
