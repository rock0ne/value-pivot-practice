"""Author check for Chapter 13. Run under WSL: python3 -I tools/check_ch13.py
Needs Node 22 at /root/.local/node22/bin/node (or set NODE)."""
import os
import subprocess
import sys
from pathlib import Path

P = Path(__file__).resolve().parents[1] / "project"
NODE = os.environ.get("NODE", "/root/.local/node22/bin/node")
FLAGS = ["--experimental-strip-types", "--no-warnings"]
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def node(*args):
    r = subprocess.run([NODE, *FLAGS, *args], cwd=P, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


ver = subprocess.run([NODE, "--version"], capture_output=True, text=True).stdout.strip()
code, out = node("--test", "tests/profile.test.ts")
check("shipped tests pass (3)", code == 0 and "# pass 3" in out)
code, out = node("demo.ts", "original")
check("original: isAdmin rides along on a profile update", "accepted; isAdmin is now true" in out)
check("original: 9007199254740993 parses as ...992", "parsed id: 9007199254740992" in out)
check("original: the neighbour's record is fetched", "record fetched: Flat 6, Holm Road" in out)
code, out = node("demo.ts", "fixed")
check("fixed: isAdmin rejected", "rejected: field not allowed: isAdmin" in out)
check("fixed: exact id kept and right record fetched", "parsed id: 9007199254740993" in out and "Flat 7, Holm Road" in out)
check("fixed: a request with one bad field changes nothing", "mixed update: rejected: phone must be a short string; stored name is now Jo" in out)
code, out = node("demo.ts", "regression")
check("regression: the Draft 1.8.1 fix changed the name before rejecting", "mixed update: rejected: phone must be a short string; stored name is now Changed" in out)
print(f"{sum(results)}/{len(results)} PASS on Node {ver}")
sys.exit(0 if all(results) else 1)
