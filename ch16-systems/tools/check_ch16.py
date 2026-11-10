"""Author check for Chapter 16. Run under WSL: python3 -I tools/check_ch16.py
C scenarios: tools/run_c.sh (GCC). Go and Rust scenarios: tools/run_go_rust.sh (Go and Rust toolchains)."""
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
out = subprocess.run(["bash", str(HERE / "run_c.sh")], capture_output=True, text=True).stdout
results = []


def check(name, ok):
    results.append(ok)
    print(("PASS " if ok else "FAIL ") + name)


for opt in ("O0", "O2"):
    check(f"meter -{opt}: overflow check did not fire, total wrapped negative", f"meter -{opt}: new total: -2147483296" in out)
    check(f"meter_fixed -{opt}: overflow refused", f"meter_fixed -{opt}: refused: would overflow" in out)
check("ubsan build reports the signed overflow", "runtime error: signed integer overflow" in out)
check("login -O0: memset present", "login -O0: wipe calls=1 memset_calls=1" in out)
check("login -O2: memset removed", "login -O2: wipe calls=0 memset_calls=0" in out)
check("login_fixed -O2: explicit_bzero kept", "login_fixed -O2: explicit_bzero calls=1" in out)
c_env = f"{out.splitlines()[0]}; {out.splitlines()[1]}"

gr = subprocess.run(["bash", str(HERE / "run_go_rust.sh")], capture_output=True, text=True).stdout
sec = {}
name = "head"
for line in gr.splitlines():
    if line.startswith("--- "):
        name = line[4:]
        sec[name] = []
    else:
        sec.setdefault(name, []).append(line)
s = {k: "\n".join(v) for k, v in sec.items()}
g = s.get("go project (go.mod: go 1.21)", "")
check("go: valid reading reported as an error (typed nil)", "M-1001 5120 Wh: err != nil is true (*main.RejectError)" in g)
check("go: every job polls the last meter under go 1.21", "polled: [M-1003 M-1003 M-1003]" in g)
check("go: the shipped tests pass", "ok  \tlumengrid.example/meterd" in s.get("go project tests", ""))
check("go: go vet reports nothing", "vet: no findings" in s.get("go vet on project", ""))
check("go: same source with go 1.22 polls every meter", "polled: [M-1001 M-1002 M-1003]" in s.get("same project, go.mod changed to go 1.22", ""))
a = s.get("go answer key", "")
check("go answer key: valid reading accepted, negative refused, every meter polled, tests pass",
      "M-1001 5120 Wh: err != nil is false (<nil>)" in a and "M-1003 -3 Wh: err != nil is true" in a
      and "polled: [M-1001 M-1002 M-1003]" in a and "ok  \tlumengrid.example/meterd" in a)
check("rust: the shipped tests pass", "test result: ok. 2 passed" in s.get("rust project tests (debug)", ""))
check("rust debug: panics on the subtraction", "attempt to subtract with overflow" in s.get("rust project, debug build", ""))
r = s.get("rust project, release build", "")
check("rust release: wraps to 4294965426 pence", "amount due: 4294965426 pence" in r)
check("rust release: channel 260 stored in slot 4", "reading from channel 260 stored in slot 4" in r)
check("rust release with overflow-checks: panics instead", "attempt to subtract with overflow" in s.get("rust project, release build with overflow-checks on", ""))
check("clippy: cast_possible_truncation warns", "casting `u32` to `u8` may truncate the value" in s.get("clippy on project (cast lint enabled)", ""))
k = s.get("rust answer key tests and release run", "")
check("rust answer key: tests pass, credit carried, channel refused",
      "test result: ok. 3 passed" in k and "credit carried forward: 1870 pence" in k and "channel 260 is out of range" in k)
gr_env = "; ".join(s.get("head", "").splitlines()[:2])
print(f"{sum(results)}/{len(results)} PASS ({c_env}; {gr_env})")
sys.exit(0 if all(results) else 1)
