"""Check your Chapter 16 exercises.

    python check.py          checks your work in each exercise's begin folder
    python check.py --end    checks the answers in the end folders

It prints the results and writes results.html next to this file. Python 3.10 or newer.
The checks build your code with GCC, Go and Rust (cargo, plus Clippy for one check), the way the
chapter's own checker does. On Linux or macOS they run directly. On Windows they run inside WSL,
in the distribution named Ubuntu (set VP_WSL_DISTRO to use another). Every build happens in a
temporary folder that is deleted afterwards: nothing is written into begin/ or end/.
"""
import os, re, shutil, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import report  # noqa: E402

ON_WINDOWS = os.name == "nt"
DISTRO = os.environ.get("VP_WSL_DISTRO", "Ubuntu")

# Shared start of every build script. $1 is the folder being checked.
PRELUDE = r'''
echo VP-START
export PATH="$HOME/.local/go/bin:$HOME/.local/rust/cargo/bin:$HOME/go/bin:$HOME/.cargo/bin:/usr/local/go/bin:$PATH"
if [ -z "${RUSTUP_HOME:-}" ] && [ -d "$HOME/.local/rust/rustup" ]; then export RUSTUP_HOME="$HOME/.local/rust/rustup"; fi
if [ -z "${CARGO_HOME:-}" ] && [ -d "$HOME/.local/rust/cargo" ]; then export CARGO_HOME="$HOME/.local/rust/cargo"; fi
export GOTOOLCHAIN=local GOPROXY=off GOFLAGS=-mod=mod CARGO_NET_OFFLINE=true
SRC="$1"
if [ "$VP_WSL" = 1 ]; then SRC=$(wslpath -a "$1" 2>/dev/null); fi
if [ ! -d "$SRC" ]; then echo "VP-NOFOLDER"; exit 3; fi
need() { command -v "$1" >/dev/null 2>&1 || { echo "VP-MISSING $1"; exit 3; }; }
T=$(mktemp -d)
trap 'rm -rf "$T"' EXIT
'''

TOOL_NAMES = {"gcc": "GCC", "go": "Go", "cargo": "Rust (cargo)", "wslpath": "WSL's wslpath"}
_cache = {}


def sh(script, folder):
    """Runs a bash script on the folder (via WSL on Windows). Returns the output, or raises Problem."""
    key = (script, str(folder))
    if key in _cache:
        return _cache[key]
    body = ("VP_WSL=1\n" if ON_WINDOWS else "VP_WSL=0\n") + PRELUDE + script
    if ON_WINDOWS:
        if not shutil.which("wsl"):
            raise Problem("WSL isn't installed, and on Windows these checks run in WSL: see the chapter README")
        cmd = ["wsl", "-d", DISTRO, "--", "bash", "-s", "--", Path(folder).as_posix()]
    else:
        if not shutil.which("bash"):
            raise Problem("bash isn't available: see the chapter README")
        cmd = ["bash", "-s", "--", str(folder)]
    try:
        r = subprocess.run(cmd, input=body.encode(), capture_output=True, timeout=600)
    except subprocess.TimeoutExpired:
        raise Problem("the build took longer than 10 minutes and was stopped")
    out = r.stdout.decode("utf-8", "replace")
    if "VP-START" not in out:
        why = r.stderr.replace(b"\x00", b"").decode("utf-8", "replace").strip().splitlines()
        raise Problem(f"couldn't start the WSL distribution '{DISTRO}'" + (f": {why[-1][:120]}" if why else "")
                      + ". See the chapter README" if ON_WINDOWS else "couldn't run bash")
    if "VP-NOFOLDER" in out:
        raise Problem(f"couldn't open {folder} from bash" + (" in WSL" if ON_WINDOWS else ""))
    m = re.search(r"VP-MISSING (\S+)", out)
    if m:
        raise Problem(f"{TOOL_NAMES.get(m.group(1), m.group(1))} isn't installed"
                      + (f" in WSL ({DISTRO})" if ON_WINDOWS else "") + ": see the chapter README")
    _cache[key] = out
    return out


class Problem(Exception):
    pass


def guarded(fn):
    """Turns a missing toolchain or failed start into a one-line reason."""
    def check(folder):
        try:
            return fn(folder)
        except Problem as p:
            return str(p)
    return check


def short(text, n=200):
    return " ".join(text.split())[:n]


def section(out, name):
    """The lines after '--- name' up to the next '--- '."""
    m = re.search(r"^--- " + re.escape(name) + r"\n(.*?)(?=^--- |\Z)", out, re.S | re.M)
    return m.group(1) if m else ""


# ---- 16_01: the overflow check (Scenario 1). Same build and run as tools/run_c.sh.
METER = r'''
need gcc
for opt in O0 O2; do
  if gcc -$opt -o "$T/meter_$opt" "$SRC/meter.c" > "$T/err" 2>&1; then
    echo "meter -$opt: $("$T/meter_$opt" 2147483000 1000)"
  else
    echo "meter -$opt: did not compile: $(head -3 "$T/err" | tr '\n' ' ')"
  fi
done
'''


def meter_refuses(opt):
    @guarded
    def check(folder):
        out = sh(METER, folder)
        line = next((l for l in out.splitlines() if l.startswith(f"meter -{opt}:")), "no output")
        return True if line == f"meter -{opt}: refused: would overflow" else "the program printed: " + short(line, 160)
    return check


# ---- 16_02: the password wipe (Scenario 2). Assembly counted the way tools/run_c.sh counts it.
LOGIN = r'''
need gcc
for opt in O0 O2; do
  if gcc -$opt -S -o "$T/login_$opt.s" "$SRC/login.c" > "$T/err" 2>&1; then
    echo "login -$opt: memset_calls=$(grep -c 'memset' "$T/login_$opt.s" | head -1) safe_wipe_calls=$(grep -cE 'explicit_bzero|memset_explicit' "$T/login_$opt.s" | head -1)"
  else
    echo "login -$opt: did not compile: $(head -3 "$T/err" | tr '\n' ' ')"
  fi
done
'''


@guarded
def wipe_kept_at_o2(folder):
    out = sh(LOGIN, folder)
    line = next((l for l in out.splitlines() if l.startswith("login -O2:")), "no output")
    m = re.search(r"safe_wipe_calls=(\d+)", line)
    if m and int(m.group(1)) >= 1:
        return True
    if m:
        return "the -O2 assembly has no call to explicit_bzero or memset_explicit (" + line.split(": ", 1)[1] + ")"
    return short(line, 160)


def no_plain_memset(folder):
    src = (folder / "login.c").read_text(encoding="utf-8")
    code = re.sub(r"/\*.*?\*/|//[^\n]*", "", src, flags=re.S)
    return True if not re.search(r"\bmemset\s*\(", code) else "login.c still clears the password with memset"


# ---- 16_03: meterd in Go (Scenarios 3 and 4). Same runs as tools/run_go_rust.sh.
GO = r'''
need go
cp -r "$SRC" "$T/meterd"
cd "$T/meterd"
echo "--- run"
go run . 2>&1
echo "--- test"
go test ./... 2>&1
'''


def go_output(expect, what):
    @guarded
    def check(folder):
        run = section(sh(GO, folder), "run")
        if expect in run:
            return True
        line = next((l for l in run.splitlines() if l.startswith(what)), None)
        return "the program printed: " + short(line or run, 160)
    return check


@guarded
def go_tests_pass(folder):
    t = section(sh(GO, folder), "test")
    return True if "ok  \tlumengrid.example/meterd" in t else "go test printed: " + short(t)


# ---- 16_04: Rust billing (Rust: the language to watch). Same runs as tools/run_go_rust.sh.
RUST = r'''
need cargo
cp -r "$SRC" "$T/billing"
cd "$T/billing"
echo "--- test"
cargo test -q --target-dir "$T/target" 2>&1
echo "--- release"
cargo run -q --release --target-dir "$T/target" 2>&1
echo "exit=$?"
echo "--- clippy"
if cargo clippy --version >/dev/null 2>&1; then
  cargo clippy -q --target-dir "$T/target" -- -W clippy::cast_possible_truncation 2>&1 | grep -E '^(warning|error)' | sort -u
  echo "clippy done"
else
  echo "VP-NO-CLIPPY"
fi
'''


@guarded
def rust_tests_pass(folder):
    t = section(sh(RUST, folder), "test")
    ok = "test result: ok." in t and "FAILED" not in t and "error" not in t
    return True if ok else "cargo test printed: " + short(t)


def release_problem(rel):
    if "exit=0" not in rel:
        why = next((l for l in rel.splitlines() if "attempt to" in l or "error" in l), "")
        return "the release build stopped instead of finishing" + (f": {why.strip()[:120]}" if why else "")
    return None


@guarded
def no_huge_bill(folder):
    rel = section(sh(RUST, folder), "release")
    if "4294965426" in rel:
        return "the release build still bills 4294965426 pence (£42,949,654.26)"
    p = release_problem(rel)
    if p:
        return p
    return True if "1870" in rel else "the release run doesn't show the 1870 pence credit: " + short(rel, 160)


@guarded
def channel_not_truncated(folder):
    rel = section(sh(RUST, folder), "release")
    if "stored in slot 4" in rel:
        return "the release build still says: reading from channel 260 stored in slot 4"
    return release_problem(rel) or True


def overflow_checks_on(folder):
    toml = (folder / "Cargo.toml").read_text(encoding="utf-8")
    m = re.search(r"^\[profile\.release\]\s*$(.*?)(?=^\[|\Z)", toml, re.S | re.M)
    if not m:
        return "Cargo.toml has no [profile.release] section"
    return True if re.search(r"^\s*overflow-checks\s*=\s*true\s*$", m.group(1), re.M) else \
        "[profile.release] doesn't set overflow-checks = true"


@guarded
def clippy_quiet(folder):
    c = section(sh(RUST, folder), "clippy")
    if "VP-NO-CLIPPY" in c:
        return "Clippy isn't installed (rustup component add clippy): see the chapter README"
    hits = [l for l in c.splitlines() if l.startswith(("warning", "error"))]
    return True if not hits else "Clippy says: " + short(hits[0], 160)


EXERCISES = [
    dict(id="16_01", title="The overflow check that wasn't there", book="Scenario 1: the overflow check that wasn't there",
         folder="16_01-meter-overflow",
         checks=[("built at -O0, adding 1000 to a total of 2147483000 is refused", meter_refuses("O0")),
                 ("built at -O2, the release level, the same reading is still refused", meter_refuses("O2"))]),
    dict(id="16_02", title="The password that stayed in memory", book="Scenario 2: the password that stayed in memory",
         folder="16_02-password-wipe",
         checks=[("built at -O2, the machine code still wipes the password (explicit_bzero or memset_explicit)", wipe_kept_at_o2),
                 ("the password isn't cleared with plain memset (the chapter's banned-pattern rule)", no_plain_memset)]),
    dict(id="16_03", title="meterd: the refused readings and the go line",
         book="Scenario 3 (Go): the success reported as a failure, and Scenario 4 (Go): the same code, two meanings",
         folder="16_03-go-meterd",
         checks=[("accepts the good reading from M-1001: err != nil is false", go_output("M-1001 5120 Wh: err != nil is false (<nil>)", "M-1001")),
                 ("accepts the good reading from M-1002 too", go_output("M-1002 4870 Wh: err != nil is false (<nil>)", "M-1002")),
                 ("still refuses the negative reading from M-1003", go_output("M-1003 -3 Wh: err != nil is true", "M-1003")),
                 ("polls every meter: polled: [M-1001 M-1002 M-1003]", go_output("polled: [M-1001 M-1002 M-1003]", "polled")),
                 ("the project's tests pass (go test)", go_tests_pass)]),
    dict(id="16_04", title="Rust billing: overflow and casts", book="Rust: the language to watch", folder="16_04-rust-billing",
         checks=[("the project's tests pass (cargo test)", rust_tests_pass),
                 ("in a release build, a £60.20 credit on £41.50 of charges isn't billed as £42,949,654.26, and 1870 pence is carried forward", no_huge_bill),
                 ("in a release build, the reading from channel 260 isn't stored in slot 4", channel_not_truncated),
                 ("Cargo.toml keeps overflow checks on in release builds", overflow_checks_on),
                 ("Clippy's cast_possible_truncation lint finds nothing", clippy_quiet)]),
]

if __name__ == "__main__":
    sys.exit(report.run("Chapter 16. Systems: C, C++ and Go, where the compiler has the last word", EXERCISES, HERE))
