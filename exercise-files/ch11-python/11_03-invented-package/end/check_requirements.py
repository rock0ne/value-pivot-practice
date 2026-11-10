"""A control, not a fix: refuse any dependency the team hasn't approved.

Run it in CI before installing. It works offline, so it can't be fooled by a
name that someone has registered since the AI invented it.
Usage: python -I check_requirements.py requirements.txt approved-packages.txt
"""
import re
import sys


def names(path):
    out = []
    for line in open(path, encoding="utf-8"):
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(re.split(r"[<>=!~;\[ ]", line, 1)[0].lower().replace("_", "-"))
    return out


def unapproved(req, approved):
    ok = set(names(approved))
    return [n for n in names(req) if n not in ok]


if __name__ == "__main__":
    bad = unapproved(sys.argv[1], sys.argv[2])
    for n in bad:
        print(f"NOT APPROVED: {n} (check it exists, who publishes it, and why we need it)")
    sys.exit(1 if bad else 0)
