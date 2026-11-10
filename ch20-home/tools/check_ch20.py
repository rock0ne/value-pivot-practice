"""Author check for Chapter 20. Usage: python -I tools/check_ch20.py
Nothing touches the network: tools/audit.py replaces it with recorders."""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def audit(rel):
    return subprocess.run([sys.executable, "-I", "tools/audit.py", rel], cwd=ROOT, capture_output=True, text=True).stdout


o = audit("project/homewatch.py")
check("original listens on every network interface", "listens on: [('0.0.0.0', 8088)]" in o)
check("original sends the device list (names and addresses) out", "telemetry.homewatch-stats.example" in o and "Front door lock" in o and "192.168.1.41" in o)
check("original accepts admin/admin", "default login admin/admin accepted: True" in o)
f = audit("answer-key/homewatch_fixed.py")
check("fixed listens on this computer only", "listens on: [('127.0.0.1', 8088)]" in f)
check("fixed sends nothing", "sends to: []" in f)
check("fixed refuses to run login without an owner-set password", "default login admin/admin: refused" in f)
print(f"{sum(results)}/{len(results)} PASS on Python {sys.version.split()[0]}")
sys.exit(0 if all(results) else 1)
