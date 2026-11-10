"""Check your Chapter 3 exercises.

    python check.py          checks your work in each exercise's begin folder
    python check.py --end    checks the answers in the end folders

It prints the results and writes results.html next to this file. Python 3.10 or newer; nothing else to install.
"""
import importlib.util, subprocess, sys, tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import report  # noqa: E402

DATA = HERE / "data" / "members-2026-12-01.csv"
TODAY = date(2026, 12, 1)


def module(folder, name):
    spec = importlib.util.spec_from_file_location(f"{name}_{folder.parent.name}_{folder.name}", folder / f"{name}.py")
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def member(expires, opt="", kind="adult"):
    return {"member_id": "T-1", "name": "Test", "email": "t@example.org", "type": kind, "expires": expires, "email_opt_out": opt}


def script(folder, name, *args):
    with tempfile.TemporaryDirectory() as tmp:
        r = subprocess.run([sys.executable, "-I", str(folder / f"{name}.py"), *args, "--out", tmp], capture_output=True, text=True)
    return r.stdout + r.stderr


def due(expires, kind="adult", want=True):
    def check(folder):
        got = module(folder, "reminders").due_for_reminder(member(expires, kind=kind), TODAY)
        return True if bool(got) == want else f"due_for_reminder said {got}"
    return check


def opt_out(folder):
    m = module(folder, "reminders")
    wrong = [a for a in ("yes", "Yes", "YES", "Y", "TRUE") if m.wants_email(member("15/12/2026", a))]
    return True if not wrong else "these opt-out answers still get an email: " + ", ".join(wrong)


def reminder_totals(folder):
    out = script(folder, "reminders", str(DATA), "--today", "2026-12-01")
    return True if "Email reminders: 38   Phone list: 6" in out else "the script printed: " + " ".join(out.split())[:200]


def lapsed(expires, want):
    def check(folder):
        n = len(module(folder, "lapsed").lapsed_members([member(expires)], TODAY))
        return True if n == want else f"found {n} lapsed, expected {want}"
    return check


def uses_given_date(folder):
    with tempfile.TemporaryDirectory() as tmp:
        p = Path(tmp) / "one.csv"
        p.write_text("member_id,name,type,expires\nT-1,Test,adult,10/06/2031\n", encoding="utf-8")
        out = script(folder, "lapsed", str(p), "--today", "2031-06-15")
    return True if "Lapsed: 1" in out else "run as 15 June 2031, it found: " + " ".join(out.split())[:160]


def lapsed_total(folder):
    out = script(folder, "lapsed", str(DATA), "--today", "2026-12-01")
    return True if "Lapsed: 11" in out else "the script printed: " + " ".join(out.split())[:200]


EXERCISES = [
    dict(id="03_01", title="The renewal reminders", book="Sections 2 to 8, the method on reminders.py", folder="03_01-reminders",
         checks=[("reminds a member whose membership expires today (rule M1)", due("01/12/2026")),
                 ("reminds a member whose membership expires in exactly 30 days (rule M1)", due("31/12/2026")),
                 ("doesn't remind a member whose membership expires in 31 days", due("01/01/2027", want=False)),
                 ("never reminds a life member (rule M2)", due("", kind="life", want=False)),
                 ("respects every way of saying 'opted out': yes, Yes, YES, Y, TRUE (rule M3)", opt_out),
                 ("with the club's data, 38 email reminders and 6 phone calls: 44, the membership system's figure", reminder_totals)]),
    dict(id="03_02", title="Your turn: the lapsed list", book="Section 12, Your turn: the lapsed list", folder="03_02-lapsed-list",
         checks=[("includes a member who lapsed exactly 14 days ago", lapsed("17/11/2026", 1)),
                 ("includes a member who lapsed yesterday", lapsed("30/11/2026", 1)),
                 ("leaves out a member who lapsed 15 days ago", lapsed("16/11/2026", 0)),
                 ("leaves out a member whose membership expires today", lapsed("01/12/2026", 0)),
                 ("the script uses the date you give it with --today", uses_given_date),
                 ("with the club's data, 11 lapsed members: the membership system's figure", lapsed_total)]),
]

if __name__ == "__main__":
    sys.exit(report.run("Chapter 3. Reading code you didn't write", EXERCISES, HERE))
