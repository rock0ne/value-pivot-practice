"""Author check for Chapter 14. Run on Windows with .NET 10 and WSL (JDK 21 at
/root/.local/jdk21): python -I tools/check_ch14.py"""
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WSL_ROOT = "/mnt/" + str(ROOT).replace("\\", "/").replace(":", "", 1).lower()[0] + str(ROOT).replace("\\", "/")[2:]
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


def java(rel):
    cmd = ["wsl", "-d", "Ubuntu", "-u", "root", "--", "/root/.local/jdk21/bin/java", f"{WSL_ROOT}/{rel}"]
    return subprocess.run(cmd, capture_output=True, text=True).stdout


def dotnet(folder, file):
    return subprocess.run(["dotnet", "run", file], cwd=ROOT / folder, capture_output=True, text=True).stdout


out = java("project/java/Billing.java")
check("java test case: one line, 14.40", "test, same scale: lines=1 total=14.40" in out)
check("java production: duplicate kept, bill doubled to 148.00", "production, mixed scale: lines=2 total=148.00" in out)
check("java: 18.50 not equals 18.5, compareTo 0", "equals 18.5? false; compareTo = 0" in out)
out = java("answer-key/BillingFixed.java")
check("java fixed: one line, 74.00", "fixed, mixed scale: lines=1 total=74.00" in out)
check("java fixed: three-decimal price refused", "three-decimal price refused" in out)

out = dotnet("project/csharp", "overdue.cs")
check("c# original: 4 database reads", "database reads: 4," in out)
check("c# original: 5427 reminders", "reminders queued: 5427" in out)
out2 = dotnet("answer-key", "overdue_fixed.cs")
check("c# fixed: 1 database read, 50000 rows", "database reads: 1, rows read: 50000" in out2)
check("c# fixed: same answers", all(s in out2 for s in ["overdue invoices: 5427", "total owed: 295442.00", "reminders queued: 5427"]))
dv = subprocess.run(["dotnet", "--version"], capture_output=True, text=True).stdout.strip()
print(f"{sum(results)}/{len(results)} PASS (dotnet {dv}, JDK 21)")
sys.exit(0 if all(results) else 1)
