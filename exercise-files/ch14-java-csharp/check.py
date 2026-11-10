"""Check your Chapter 14 exercises.

    python check.py          checks your work in each exercise's begin folder
    python check.py --end    checks the answers in the end folders

It prints the results and writes results.html next to this file. Python 3.10 or newer.
Exercise 14_01 needs a Java Development Kit (17 or newer; the book used 21), with java and javac.
Exercise 14_02 needs the .NET 10 SDK (dotnet), which runs a single .cs file with `dotnet run file.cs`.
The checker looks for java, javac and dotnet on your PATH first. If it can't find Java there and you're
on Windows, it tries the author's setup: WSL Ubuntu with a JDK at /root/.local/jdk21.
"""
import functools, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import report  # noqa: E402

AUTHOR_JDK = "/root/.local/jdk21/bin"


def one_file(folder, pattern):
    files = sorted(folder.glob(pattern))
    if len(files) != 1:
        raise RuntimeError(f"expected one {pattern} file in {folder.parent.name}/{folder.name}, found {len(files)}")
    return files[0]


def guard(fn):
    """A missing toolchain or a compile error is a failed check with a one-line reason, not a crash."""
    @functools.wraps(fn)
    def check(folder):
        try:
            return fn(folder)
        except RuntimeError as e:
            return str(e)
    return check


def short(text, n=200):
    return " ".join(text.split())[:n]


# ---------- Java ----------

def wsl_path(p):
    s = str(Path(p).resolve()).replace("\\", "/")
    return "/mnt/" + s[0].lower() + s[2:]


@functools.lru_cache(maxsize=None)
def java_tools():
    """Returns (how, prefix) or (None, reason). how is 'local' or 'wsl'."""
    if shutil.which("java") and shutil.which("javac"):
        return "local", ()
    if os.name == "nt" and shutil.which("wsl"):
        prefix = ("wsl", "-d", "Ubuntu", "-u", "root", "--exec")
        try:
            r = subprocess.run([*prefix, f"{AUTHOR_JDK}/javac", "-version"], capture_output=True, text=True, timeout=120)
            if r.returncode == 0:
                return "wsl", prefix
        except (OSError, subprocess.TimeoutExpired):
            pass
    return None, "Java isn't installed (no java and javac on your PATH): install a JDK, 17 or newer, and see the README"


HARNESS = """import java.math.BigDecimal;
import java.util.*;

public class ValuePivotCheck {
    public static void main(String[] args) {
        try {
            var a = List.of(new CLS.Line("HF-1001", "OLIVE-1L", 6, new BigDecimal("2.40")));
            var b = List.of(new CLS.Line("HF-1001", "OLIVE-1L", 6, new BigDecimal("2.40")));
            System.out.println("same scale: lines=" + CLS.merge(a, b).size() + " total=" + CLS.total(CLS.merge(a, b)));
        } catch (Exception e) { System.out.println("same scale: error " + e); }
        try {
            var web = List.of(new CLS.Line("HF-1002", "FLOUR-25KG", 4, new BigDecimal("18.50")));
            var phone = List.of(new CLS.Line("HF-1002", "FLOUR-25KG", 4, new BigDecimal("18.5")));
            System.out.println("mixed scale: lines=" + CLS.merge(web, phone).size() + " total=" + CLS.total(CLS.merge(web, phone)));
        } catch (Exception e) { System.out.println("mixed scale: error " + e); }
        try {
            new CLS.Line("HF-1003", "SALT-1KG", 1, new BigDecimal("0.995"));
            System.out.println("three-decimal price accepted");
        } catch (ArithmeticException e) {
            System.out.println("three-decimal price refused");
        }
    }
}
"""


@functools.lru_cache(maxsize=None)
def run_billing(folder):
    """Compiles the folder's .java file with a small test program and returns what it printed."""
    how, prefix = java_tools()
    if how is None:
        raise RuntimeError(prefix)
    src = one_file(folder, "*.java")
    m = re.search(r"public\s+class\s+(\w+)", src.read_text(encoding="utf-8"))
    if not m:
        raise RuntimeError(f"{src.name} has no public class")
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        shutil.copy(src, t / src.name)
        (t / "ValuePivotCheck.java").write_text(HARNESS.replace("CLS", m.group(1)), encoding="utf-8")
        if how == "local":
            javac, java, base = ["javac"], ["java"], str(t)
        else:
            javac, java, base = [*prefix, f"{AUTHOR_JDK}/javac"], [*prefix, f"{AUTHOR_JDK}/java"], wsl_path(t)
        c = subprocess.run([*javac, "-d", f"{base}/out", f"{base}/{src.name}", f"{base}/ValuePivotCheck.java"],
                           capture_output=True, text=True, timeout=300)
        if c.returncode != 0:
            raise RuntimeError(f"{src.name} doesn't compile with the checker's test: " + short(c.stdout + c.stderr))
        r = subprocess.run([*java, "-cp", f"{base}/out", "ValuePivotCheck"], capture_output=True, text=True, timeout=300)
    return r.stdout + r.stderr


def billing(label, lines, total):
    @guard
    def check(folder):
        out = run_billing(folder)
        m = re.search(rf"{label}: lines=(\d+) total=([\d.]+)", out)
        if not m:
            return "the test program printed: " + short(out)
        return True if m.groups() == (str(lines), total) else f"got {m.group(1)} line(s), total {m.group(2)}"
    return check


@guard
def refuses_three_decimals(folder):
    out = run_billing(folder)
    if "three-decimal price refused" in out:
        return True
    return "a price of 0.995 was accepted" if "accepted" in out else "the test program printed: " + short(out)


# ---------- C# ----------

@functools.lru_cache(maxsize=None)
def dotnet():
    exe = shutil.which("dotnet")
    if not exe and os.name == "nt" and Path(r"C:\Program Files\dotnet\dotnet.exe").exists():
        exe = r"C:\Program Files\dotnet\dotnet.exe"
    if not exe:
        return None
    try:
        v = subprocess.run([exe, "--version"], capture_output=True, text=True, timeout=120).stdout.strip()
    except (OSError, subprocess.TimeoutExpired):
        return None
    return exe if v.split(".")[0].isdigit() and int(v.split(".")[0]) >= 10 else None


@functools.lru_cache(maxsize=None)
def run_overdue(folder):
    exe = dotnet()
    if exe is None:
        raise RuntimeError(".NET 10 SDK isn't installed (no dotnet 10 on your PATH): see the README")
    src = one_file(folder, "*.cs")
    env = dict(os.environ, DOTNET_SYSTEM_GLOBALIZATION_INVARIANT="1", DOTNET_CLI_TELEMETRY_OPTOUT="1", DOTNET_NOLOGO="1")
    r = subprocess.run([exe, "run", src.name], cwd=folder, capture_output=True, text=True, timeout=600, env=env)
    if r.returncode != 0:
        raise RuntimeError(f"`dotnet run {src.name}` failed: " + short(r.stdout + r.stderr))
    return r.stdout


@guard
def reads_once(folder):
    out = run_overdue(folder)
    m = re.search(r"database reads: (\d+), rows read: (\d+)", out)
    if not m:
        return "the program printed: " + short(out)
    return True if m.groups() == ("1", "50000") else f"database reads: {m.group(1)}, rows read: {m.group(2)}"


@guard
def same_answers(folder):
    out = run_overdue(folder)
    missing = [s for s in ("overdue invoices: 5427", "reminders queued: 5427") if s not in out]
    return True if not missing else "missing from the output: " + "; ".join(missing)


@guard
def same_total(folder):
    out = run_overdue(folder)
    return True if re.search(r"total owed: 295442[.,]00\b", out) else "the program printed: " + short(out)


EXERCISES = [
    dict(id="14_01", title="The flour that was billed twice", book="Scenario 1 (Java): the flour that was billed twice",
         folder="14_01-flour-billed-twice",
         checks=[("the shipped test still passes: the same line from both systems leaves one line, for 14.40",
                  billing("same scale", 1, "14.40")),
                 ("four bags of flour, priced 18.50 by the web shop and 18.5 by the phone system, are billed once: one line, 74.00 (not 148.00)",
                  billing("mixed scale", 1, "74.00")),
                 ("refuses a three-decimal price (0.995) instead of rounding it", refuses_three_decimals)]),
    dict(id="14_02", title="The query that ran four times", book="Scenario 2 (C#): the query that ran four times",
         folder="14_02-query-ran-four-times",
         checks=[("asks the database once: 1 read of 50,000 rows (not 4 reads of 150,007)", reads_once),
                 ("still finds 5,427 overdue invoices and queues 5,427 reminders", same_answers),
                 ("still totals 295,442.00 owed", same_total)]),
]

if __name__ == "__main__":
    sys.exit(report.run("Chapter 14. Java and C#: the enterprise, where equal isn't always equal", EXERCISES, HERE))
