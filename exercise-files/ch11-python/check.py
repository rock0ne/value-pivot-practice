"""Check your Chapter 11 exercises.

    python check.py          checks your work in each exercise's begin folder
    python check.py --end    checks the answers in the end folders

It prints the results and writes results.html next to this file. Python 3.10 or newer; nothing else to install.
Everything stays on this computer: the suppliers are the chapter's stand-in server on 127.0.0.1, and the
archives are built in a temporary folder that is removed afterwards.
"""
import ast, asyncio, importlib.util, subprocess, sys, tarfile, tempfile, warnings
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import report  # noqa: E402

DATA = HERE / "data"


def module(folder, name):
    path = folder / f"{name}.py"
    if not path.exists():
        raise FileNotFoundError(f"there's no {name}.py in {folder.parent.name}/{folder.name}")
    spec = importlib.util.spec_from_file_location(f"{name}_{folder.parent.name}_{folder.name}", path)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def run(folder, *args):
    r = subprocess.run([sys.executable, "-I", *args], cwd=folder, capture_output=True, text=True, timeout=30)
    return r.returncode, r.stdout + r.stderr


# 11_01: the supplier that froze the shop

@lru_cache(maxsize=None)
def slow_run(folder):
    """Run ingest() against the chapter's three stand-in suppliers, slow one first (about 2 seconds)."""
    server_mod = module(DATA, "supplier_server")
    ingest = module(folder, "ingest")
    server, base = server_mod.start()
    try:
        feeds, finished, beats = asyncio.run(ingest.ingest([base + "/slow", base + "/fast-a", base + "/fast-b"]))
    finally:
        server.shutdown()
    return feeds, finished, beats


def shipped_tests(folder):
    code, out = run(folder, "-m", "unittest", "discover", "-s", "tests", "-q")
    return True if code == 0 else "the tests that came with it fail: " + " ".join(out.split())[-200:]


def all_feeds(folder):
    feeds, _, _ = slow_run(folder)
    got = [f.get("supplier") for f in feeds]
    return True if got == ["slow", "fast-a", "fast-b"] else f"collected {got}"


def fast_ones_quick(folder):
    _, fin, _ = slow_run(folder)
    worst = max(fin["fast-a"], fin["fast-b"])
    return True if worst < 0.5 else f"the fast suppliers finished after {worst} seconds, waiting for the slow one"


def heartbeat_ticks(folder):
    _, _, beats = slow_run(folder)
    n = len(beats)
    return True if n >= 10 else f"the heartbeat ticked {n} {'time' if n == 1 else 'times'} in about 2 seconds"


# 11_02: the archive that wrote outside its folder

def names_filter(folder):
    path = folder / "unpack.py"
    calls = [n for n in ast.walk(ast.parse(path.read_text(encoding="utf-8")))
             if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "extractall"]
    if not calls:
        return "unpack.py has no extractall call to check"
    bare = [c.lineno for c in calls if not any(k.arg == "filter" for k in c.keywords)]
    return True if not bare else "extractall on line " + ", ".join(map(str, bare)) + " relies on the default filter"


def unpack_into_sandbox(folder, which):
    archives = module(DATA, "make_archives")
    unpack = module(folder, "unpack")
    with tempfile.TemporaryDirectory() as tmp:
        sandbox = Path(tmp) / "sandbox"
        good, bad = archives.build(sandbox)
        dest = sandbox / "uploads" / "acme"
        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            try:
                listed = unpack.unpack(good if which == "good" else bad, dest)
                outcome = "extracted"
            except (tarfile.TarError, OSError, ValueError) as exc:
                listed, outcome = None, f"refused: {type(exc).__name__}"
        escaped = (sandbox / "escaped.txt").exists() or any(sandbox.rglob("escaped.txt"))
        inside = sorted(p.name for p in dest.iterdir()) if dest.exists() else []
    return listed, outcome, escaped, inside


def normal_archive(folder):
    listed, outcome, _, inside = unpack_into_sandbox(folder, "good")
    return True if outcome == "extracted" and inside == ["prices.csv"] else f"normal price list: {outcome}, folder holds {inside}"


def tampered_archive(folder):
    _, outcome, escaped, _ = unpack_into_sandbox(folder, "tampered")
    v = sys.version.split()[0]
    if escaped:
        return f"on Python {v}, escaped.txt landed outside the supplier's folder"
    return True if outcome.startswith("refused") else f"on Python {v}, it {outcome} the tampered archive without refusing it"


# 11_03: the package that doesn't exist

def control(folder, req="requirements-ai.txt"):
    if not (folder / "check_requirements.py").exists():
        return None, "there's no check_requirements.py in this folder yet: write the control the chapter describes"
    code, out = run(folder, "check_requirements.py", req, "approved-packages.txt")
    return code, out


def flags_invented(folder):
    code, out = control(folder)
    if code is None:
        return out
    return True if code == 1 and "hollin-feedkit" in out else f"exit code {code}, printed: " + " ".join(out.split())[:160]


def leaves_approved(folder):
    code, out = control(folder)
    if code is None:
        return out
    return True if "requests" not in out else "it flagged requests, which is on the approved list"


def passes_clean_list(folder):
    if not (folder / "check_requirements.py").exists():
        return "there's no check_requirements.py in this folder yet"
    with tempfile.TemporaryDirectory() as tmp:
        req = Path(tmp) / "requirements.txt"
        req.write_text("requests==2.32.3\n", encoding="utf-8")
        code, out = control(folder, str(req))
    return True if code == 0 else f"exit code {code} for a list holding only requests: " + " ".join(out.split())[:160]


EXERCISES = [
    dict(id="11_01", title="The supplier that froze the shop", book="Scenario 1: the supplier that froze the shop", folder="11_01-slow-supplier",
         checks=[("the tests that came with it still pass", shipped_tests),
                 ("collects all three feeds, the slow one included", all_feeds),
                 ("with one supplier taking 2 seconds, the fast ones finish in under 0.5 seconds", fast_ones_quick),
                 ("the heartbeat keeps ticking while the slow supplier answers (at least 10 beats)", heartbeat_ticks)]),
    dict(id="11_02", title="The archive that wrote outside its folder", book="Scenario 2: the archive that wrote outside its folder", folder="11_02-tampered-archive",
         checks=[("every extractall names its filter, whatever the Python version", names_filter),
                 ("still unpacks a normal price list (prices.csv)", normal_archive),
                 ("refuses the tampered archive, and nothing lands outside the supplier's folder", tampered_archive)]),
    dict(id="11_03", title="The package that doesn't exist", book="Scenario 3: the package that doesn't exist", folder="11_03-invented-package",
         checks=[("the control flags hollin-feedkit, which nobody has approved, and fails", flags_invented),
                 ("the control doesn't flag requests, which is on the approved list", leaves_approved),
                 ("the control passes a list that holds only approved packages", passes_clean_list)]),
]

if __name__ == "__main__":
    sys.exit(report.run("Chapter 11. Python: the pipeline that passed every test", EXERCISES, HERE))
