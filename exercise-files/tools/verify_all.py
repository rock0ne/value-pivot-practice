"""Author check for the exercise files: every exercise's begin state fails, and its end state passes.

Usage: python -I tools/verify_all.py      (from the exercise-files folder)
Runs tools/build_ch12.py (which checks the SQL exercises against the book's numbers) and every local
chapter's check.py on begin and --end. The browser pages are checked separately, in a browser.
"""
import re, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
ok = True
r = subprocess.run([sys.executable, "-I", str(HERE / "tools/build_ch12.py")], capture_output=True, text=True)
print("ch12-sql (build and check):", r.stdout.strip().splitlines()[-1])
ok &= r.returncode == 0
for check in sorted(HERE.glob("ch*/check.py")):
    ch = check.parent
    res = {}
    for mode in ("begin", "end"):
        p = subprocess.run([sys.executable, "-I", str(check)] + (["--end"] if mode == "end" else []), cwd=ch, capture_output=True, text=True, timeout=900)
        out = p.stdout
        per_ex = re.findall(r"^(\d\d_\d\d) .*: (PASS|NOT YET)$", out, flags=re.M)
        summary = re.search(r"(\d+) of (\d+) checks pass", out)
        res[mode] = (per_ex, summary.groups() if summary else None)
    (ch / "results.html").unlink(missing_ok=True)
    begin_ok = res["begin"][0] and all(v == "NOT YET" for _, v in res["begin"][0])
    end_ok = res["end"][1] and res["end"][1][0] == res["end"][1][1]
    print(f"{ch.name}: begin {res['begin'][1]} every exercise not yet: {bool(begin_ok)}; end {res['end'][1]} all pass: {bool(end_ok)}")
    ok &= bool(begin_ok) and bool(end_ok)
for pc in HERE.rglob("__pycache__"):
    for f in pc.iterdir(): f.unlink()
    pc.rmdir()
print("ALL EXERCISE FILES CHECK OUT" if ok else "PROBLEM")
sys.exit(0 if ok else 1)
