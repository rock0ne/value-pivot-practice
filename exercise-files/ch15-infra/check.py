"""Check your Chapter 15 exercises.

    python check.py          checks your work in each exercise's begin folder
    python check.py --end    checks the answers in the end folders

It prints the results and writes results.html next to this file. Python 3.10 or newer, with PyYAML
(python -m pip install pyyaml), and Bash.

Exercise 15_01 runs a clean-up script that calls `rm -rf`, so it is only ever run through safe_run.sh,
the way the chapter's own tools/bash_demo.sh runs it: with `env -i` and a PATH that holds nothing but
the stand-in rm in data/fakebin, which prints what it would delete and deletes nothing. On Windows,
safe_run.sh runs as root under WSL Ubuntu, as the chapter's checker does, creates its test folders, and
runs your script as the unprivileged user nobody. On Linux it runs directly, and needs root to create
its test folders, so use a throwaway container or virtual machine.
Before running your script, the checker also refuses to run it if it could reach a real command by
another route: an absolute path such as /bin/rm, a change to PATH, eval, exec, source, command
substitution, or a redirection that writes to a file.
"""
import functools, importlib.util, os, re, shutil, subprocess, sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import report  # noqa: E402

ROOT = "/srv/pennant/builds"
ORIGINAL_YAML = HERE / "data" / "shipping.yaml"
WRITTEN = ["GB", "IE", "FR", "DE", "NO", "SE", "DK"]


def guard(fn):
    """A missing tool or an unsafe script is a failed check with a one-line reason, not a crash."""
    @functools.wraps(fn)
    def check(folder):
        try:
            return fn(folder)
        except RuntimeError as e:
            return str(e)
    return check


def one_file(folder, pattern):
    files = sorted(folder.glob(pattern))
    if len(files) != 1:
        raise RuntimeError(f"expected one {pattern} file in {folder.parent.name}/{folder.name}, found {len(files)}")
    return files[0]


def short(text, n=200):
    return " ".join(text.split())[:n]


# ---------- 15_01: the clean-up script, run only with the stand-in rm ----------

UNSAFE = [
    (r"\bPATH\b", "it mentions PATH"),
    (r"\b(eval|exec|source|hash|command|builtin|enable|coproc|kill|history|fc)\b", "it uses `{0}`"),
    (r"`|\$\(|<\(|>\(", "it uses command or process substitution"),
    (r"(^|[;&|]\s*)\.\s", "it sources another file with `.`"),
    (r"\.\./", "it climbs out of a folder with ../"),
]


def unsafe_reason(text):
    """Returns why the script mustn't be run, or None. Defence in depth: safe_run.sh already
    gives the script a PATH that holds only the stand-in rm."""
    body = "\n".join(line for line in text.splitlines() if not line.lstrip().startswith("#"))
    for pattern, why in UNSAFE:
        m = re.search(pattern, body, re.M)
        if m:
            return why.format(m.group(0).strip())
    for m in re.finditer(r"(?:^|(?<=[\s=\"'(;|&:+<>-]))/[^\s}*]\S*", body, re.M):
        path = m.group(0).strip("\"';)")
        if not (path.startswith(ROOT) or path == "/dev/null"):
            return f"it names the path {path}: the only paths allowed are under {ROOT}"
    for m in re.finditer(r"(?<![0-9&])>>?\s*(?!&[0-9])(\S+)", body):
        if m.group(1).strip("\"'") != "/dev/null":
            return f"it writes to a file with > {m.group(1)}"
    return None


def wsl_path(p):
    s = str(Path(p).resolve()).replace("\\", "/")
    return "/mnt/" + s[0].lower() + s[2:]


@functools.lru_cache(maxsize=None)
def run_cleanup(folder):
    """Runs the folder's .sh script through safe_run.sh for each test case; returns {label: output}."""
    script = one_file(folder, "*.sh")
    raw = script.read_bytes()
    if b"\r\n" in raw:
        raise RuntimeError(f"{script.name} has Windows line endings: save it with LF (Unix) line endings")
    why = unsafe_reason(raw.decode("utf-8", errors="replace"))
    if why:
        raise RuntimeError(f"not run, for safety: {why}")
    driver = HERE / "safe_run.sh"
    if os.name == "nt":
        if not shutil.which("wsl"):
            raise RuntimeError("WSL isn't installed: this check runs the script under WSL Ubuntu (see the README)")
        cmd = ["wsl", "-d", "Ubuntu", "-u", "root", "--exec", "/bin/bash", wsl_path(driver), wsl_path(script)]
    else:
        if not Path("/bin/bash").exists():
            raise RuntimeError("Bash isn't installed at /bin/bash")
        cmd = ["/bin/bash", str(driver), str(script)]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=300)
    except subprocess.TimeoutExpired:
        raise RuntimeError("the script took more than 5 minutes")
    out = r.stdout
    if "SETUP FAILED" in out:
        raise RuntimeError(short(out.split("SETUP FAILED:", 1)[1]))
    blocks = {}
    for chunk in out.split("== ")[1:]:
        label, _, body = chunk.partition("\n")
        blocks[label.strip()] = body
    if "nested" not in blocks:
        raise RuntimeError("safe_run.sh didn't finish: " + short(out + r.stderr))
    return blocks


def exit_code(body):
    m = re.search(r"exit=(\d+)\s*$", body)
    return int(m.group(1)) if m else None


def deletes_inside(folder):
    b = run_cleanup(folder)["set"]
    if f"WOULD DELETE: {ROOT}/release-42/*" in b and "top-level" not in b and exit_code(b) == 0:
        return True
    return "it printed: " + short(b)


def stops_when_missing(case):
    @guard
    def check(folder):
        b = run_cleanup(folder)[case]
        if "WOULD DELETE" in b:
            return "rm was called: " + short(b)
        if exit_code(b) in (0, None):
            return "it called no rm, but finished with exit 0, so the pipeline would report success"
        if "BUILD_DIR" not in b:
            return "it stopped, but its message doesn't say BUILD_DIR is missing: " + short(b)
        return True
    return check


def refuses(case):
    @guard
    def check(folder):
        b = run_cleanup(folder)[case]
        if "WOULD DELETE" in b:
            return "rm was called: " + short(b)
        if exit_code(b) in (0, None):
            return "it called no rm, but finished with exit 0"
        if not b.rsplit("exit=", 1)[0].strip():
            return "it stopped, but printed no message saying why"
        return True
    return check


# ---------- 15_02: the shipping configuration ----------

def loader(folder):
    try:
        import yaml  # noqa: F401
    except ImportError:
        raise RuntimeError("PyYAML isn't installed: run python -m pip install pyyaml")
    src = one_file(folder, "*.py")
    spec = importlib.util.spec_from_file_location(f"{src.stem}_{folder.parent.name}_{folder.name}".replace("-", "_"), src)
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.allowed_countries


@guard
def refuses_original(folder):
    load = loader(folder)
    try:
        got = load(str(ORIGINAL_YAML))
    except Exception as e:
        return True if str(e) else "it refused the file, but with no message"
    return f"it loaded {got!r}: Norway's NO became False, and nothing complained"


@guard
def loads_as_written(folder):
    load = loader(folder)
    try:
        got = load(str(one_file(folder, "*.yaml")))
    except Exception as e:
        return f"your shipping.yaml was refused ({short(str(e), 120)}): quote the code that YAML misreads"
    if got == WRITTEN:
        return True
    return f"it loaded {got!r}" + (": NO can't ship" if "NO" not in got else "")


EXERCISES = [
    dict(id="15_01", title="The clean-up that would have deleted everything",
         book="Scenario 1 (Bash): the clean-up that would have deleted everything", folder="15_01-clean-up-script",
         checks=[(f"with BUILD_DIR set to {ROOT}/release-42, asks to delete only what's inside that folder", guard(deletes_inside)),
                 ("with BUILD_DIR not set, stops before rm, says BUILD_DIR is not set, and exits with an error", stops_when_missing("unset")),
                 ("with BUILD_DIR set but empty, does the same", stops_when_missing("empty")),
                 (f"refuses a path with .. in it ({ROOT}/../../outside) before rm, and exits with an error", refuses("dot-dot")),
                 (f"refuses the builds root itself ({ROOT}/) before rm, and exits with an error", refuses("builds root")),
                 (f"refuses a link ({ROOT}/release-link, which points at /etc) before rm, and exits with an error", refuses("link")),
                 (f"refuses a nested path ({ROOT}/release-42/sub) before rm, and exits with an error", refuses("nested"))]),
    dict(id="15_02", title="The country that became \"false\"",
         book="Scenario 2 (YAML): the country that became \"false\"", folder="15_02-country-became-false",
         checks=[("refuses the file as the AI wrote it, where NO loads as False, with a clear message", refuses_original),
                 ("loads your shipping.yaml as exactly the seven codes written, GB IE FR DE NO SE DK, so Norway can ship", loads_as_written)]),
]

if __name__ == "__main__":
    sys.exit(report.run("Chapter 15. Infrastructure, pipelines and scripts: the code that runs everything else", EXERCISES, HERE))
