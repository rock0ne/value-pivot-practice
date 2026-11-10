"""Author check for Chapter 15. Run on Windows with PyYAML and WSL Ubuntu:
python -I tools/check_ch15.py   (the Bash part runs under WSL with a fake rm only)"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
p = str(ROOT).replace("\\", "/")
WSL_ROOT = "/mnt/" + p[0].lower() + p[2:]
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def py(*a):
    return subprocess.run([sys.executable, "-I", *a], cwd=ROOT, capture_output=True, text=True).stdout


out = py("project/shipping.py", "project/shipping.yaml")
check("yaml: NO loads as False", "'DE', False, 'SE'" in out)
check("yaml: Norway can't ship, Sweden can", "NO can ship: False" in out and "SE can ship: True" in out)
out = py("answer-key/shipping_fixed.py", "project/shipping.yaml")
check("yaml fixed: config refused with a clear message", "refused: ship_to must be two-letter country codes" in out)

out = subprocess.run(["wsl", "-d", "Ubuntu", "-u", "root", "--", "bash", f"{WSL_ROOT}/tools/bash_demo.sh"],
                     capture_output=True, text=True).stdout
b = {}
for chunk in out.split("== ")[1:]:
    label, _, body = chunk.partition("\n")
    b[label.strip()] = body
check("bash original, set: deletes inside the build folder only", "WOULD DELETE: /srv/pennant/builds/release-42/*" in b["original, set"] and "top-level" not in b["original, set"])
check("bash original, empty: asks to delete the whole filesystem, and reports success",
      "top-level paths of the whole filesystem, including /etc=yes /home=yes" in b["original, empty"] and "clean done" in b["original, empty"] and "exit=0" in b["original, empty"])
check("bash fixed, set: same as before", "WOULD DELETE: /srv/pennant/builds/release-42/*" in b["fixed, set"] and "exit=0" in b["fixed, set"])
check("bash fixed, empty: refused before rm, exit 1", "BUILD_DIR is not set" in b["fixed, empty"] and "WOULD DELETE" not in b["fixed, empty"] and "exit=1" in b["fixed, empty"])
for case in ("dot-dot", "builds root", "link", "nested"):
    body = b["fixed, " + case]
    check(f"bash fixed, {case}: refused before rm, exit 1", "refusing to clean" in body and "WOULD DELETE" not in body and "exit=1" in body)
check("regression: the v1.8.1 fix let ../../outside through to rm",
      "WOULD DELETE: /srv/pennant/builds/../../outside/*" in b["v1.8.1 fix, dot-dot"] and "exit=0" in b["v1.8.1 fix, dot-dot"])
check("regression: the v1.8.1 fix let the whole builds folder through to rm",
      "WOULD DELETE: /srv/pennant/builds//release-42" in b["v1.8.1 fix, builds root"] and "exit=0" in b["v1.8.1 fix, builds root"])
import yaml
print(f"{sum(results)}/{len(results)} PASS (Python {sys.version.split()[0]}, PyYAML {yaml.__version__}, WSL bash)")
sys.exit(0 if all(results) else 1)
