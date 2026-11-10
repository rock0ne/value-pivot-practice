"""Author check for Chapter 11: every claim the chapter makes about the code.

Usage: python -I tools/check_ch11.py <sandbox-dir>
Run on Python 3.12 and on 3.14: the archive result depends on the version.
"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "project"
SB = Path(sys.argv[1]).resolve()
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def run(*args):
    r = subprocess.run([sys.executable, "-I", *args], cwd=P, capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def parse(out):
    import ast
    fin = ast.literal_eval(out.split("finished (seconds after start):", 1)[1].splitlines()[0].strip())
    beats = int(out.split("heartbeats:", 1)[1].split()[0])
    return fin, beats


code, out = run("-m", "unittest", "discover", "-s", "tests", "-q")
check("shipped tests pass", code == 0)

code, out = run("run_demo.py")
fin, beats = parse(out)
check("original: fast suppliers wait for the slow one (>=1.5 s)", min(fin["fast-a"], fin["fast-b"]) >= 1.5)
check("original: heartbeat frozen (<=2 beats in ~2 s)", beats <= 2)

code, out = run("run_demo.py", "ingest_fixed")
fin, beats = parse(out)
check("fixed: fast suppliers finish under 0.5 s", max(fin["fast-a"], fin["fast-b"]) < 0.5)
check("fixed: heartbeat keeps going (>=10 beats)", beats >= 10)

v = sys.version_info[:2]
code, out = run("unpack_demo.py", str(SB / "orig"))
if v >= (3, 14):
    check(f"original on {v}: default filter refuses the escape", "refused" in out and "escaped file exists: False" in out)
else:
    check(f"original on {v}: file escapes the folder", "escaped file exists: True" in out)
code, out = run("unpack_demo.py", str(SB / "fix"), "unpack_fixed")
check("fixed (filter='data'): refused on this version", "refused" in out and "escaped file exists: False" in out)

r = subprocess.run([sys.executable, "-I", str(ROOT / "answer-key" / "check_requirements.py"),
                    "requirements-ai.txt", "approved-packages.txt"], cwd=P, capture_output=True, text=True)
check("control flags the unapproved package", r.returncode == 1 and "hollin-feedkit" in r.stdout and "requests" not in r.stdout)

print(f"{sum(results)}/{len(results)} PASS on Python {sys.version.split()[0]}")
sys.exit(0 if all(results) else 1)
