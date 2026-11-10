"""Author tool: prove every number Chapter 3 quotes.

Runs the original reminders.py, each fix in the chapter's order, the probes,
the AI's tests and the boundary tests, the strict version, the lapsed.py
exercise and its answer, and the SQL NULL example. Prints PASS or FAIL for
each check and writes tools/chapter-numbers.json.
Usage: python -I tools/check_ch03.py   (run from the ch03-reading folder)
"""
import csv
import importlib.util
import json
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PROJECT = ROOT / "project"
KEY = ROOT / "answer-key"
DATA = PROJECT / "data/members-2026-12-01.csv"
PROBES = PROJECT / "probes/probes.csv"
TODAY = date(2026, 12, 1)
results, numbers = [], {}


def check(name, ok, detail=""):
    results.append(ok)
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def load_source(src, name):
    tmp = Path(tempfile.mkdtemp()) / f"{name}.py"
    tmp.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location(name, tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def lists(mod, path):
    e, p = mod.build_lists(rows(path), TODAY)
    return [m["member_id"] for m in e], [m["member_id"] for m in p]


def rep(t, a, b):
    assert t.count(a) == 1, a
    return t.replace(a, b)


orig = (PROJECT / "reminders.py").read_text(encoding="utf-8")
FIX1 = ("    return 0 < days < REMINDER_WINDOW_DAYS", "    return 0 <= days <= REMINDER_WINDOW_DAYS")
FIX2 = ('''    if member["expires"].strip():
        expires = parse_date(member["expires"])
    else:
        expires = today  # no expiry date recorded
    return (expires - today).days''', '''    text = member["expires"].strip()
    if not text:
        return None  # life members have no expiry date
    return (parse_date(text) - today).days''')
FIX2b = ("    return 0 <= days <= REMINDER_WINDOW_DAYS", "    return days is not None and 0 <= days <= REMINDER_WINDOW_DAYS")
FIX3 = ('    return member["email_opt_out"].strip() != "yes"',
        '    return member["email_opt_out"].strip().lower() not in {"yes", "y", "true"}')

s0 = orig
s1 = rep(s0, *FIX1)
s2 = rep(rep(s1, *FIX2), *FIX2b)
s3 = rep(s2, *FIX3)
stages = {"original": s0, "fix1_boundary": s1, "fix2_life": s2, "fix3_optout": s3}

committee = (PROJECT / "data/committee-figures.txt").read_text(encoding="utf-8")
check("committee figures: 44 expiring, 6 opted out, 11 lapsed, 9 life, 412 total",
      all(x in committee for x in (": 44", ": 6", ": 11", ": 9", ": 412")))
members = rows(DATA)
check("data has 412 members", len(members) == 412, str(len(members)))

for name, src in stages.items():
    mod = load_source(src, f"rem_{name}")
    e, p = lists(mod, DATA)
    pe, pp = lists(mod, PROBES)
    numbers[name] = {"email": len(e), "phone": len(p), "probe_email": pe, "probe_phone": pp}
    print(f"      {name}: data email {len(e)} phone {len(p)}; probes email {pe} phone {pp}")

n = numbers
check("original: 38 email, 1 phone", (n["original"]["email"], n["original"]["phone"]) == (38, 1))
check("original probes: email P6 P8, phone P7", (n["original"]["probe_email"], n["original"]["probe_phone"]) == (["P6", "P8"], ["P7"]))
check("after fix 1: 52 email, 1 phone", (n["fix1_boundary"]["email"], n["fix1_boundary"]["phone"]) == (52, 1))
check("after fix 1 probes: life member P5 now reminded",
      n["fix1_boundary"]["probe_email"] == ["P1", "P2", "P5", "P6", "P8"] and n["fix1_boundary"]["probe_phone"] == ["P7"])
check("after fix 2: 43 email, 1 phone", (n["fix2_life"]["email"], n["fix2_life"]["phone"]) == (43, 1))
check("after fix 2 probes", n["fix2_life"]["probe_email"] == ["P1", "P2", "P6", "P8"])
check("after fix 3: 38 email, 6 phone = 44, matches committee", (n["fix3_optout"]["email"], n["fix3_optout"]["phone"]) == (38, 6))
check("after fix 3 probes: email P1 P2 P8, phone P6 P7",
      (n["fix3_optout"]["probe_email"], n["fix3_optout"]["probe_phone"]) == (["P1", "P2", "P8"], ["P6", "P7"]))

# The answer key's fixed and strict versions agree with fix 3.
for fname in ("reminders_fixed.py", "reminders_strict.py"):
    mod = load_source((KEY / fname).read_text(encoding="utf-8"), fname[:-3])
    e, p = lists(mod, DATA)
    check(f"{fname}: 38 email, 6 phone", (len(e), len(p)) == (38, 6))
strict = load_source((KEY / "reminders_strict.py").read_text(encoding="utf-8"), "strict2")
for bad, why in (({"member_id": "X", "type": "adult", "expires": "", "email_opt_out": ""}, "blank expiry, not life"),
                 ({"member_id": "X", "type": "adult", "expires": "15/12/2026", "email_opt_out": "maybe"}, "unknown opt-out")):
    try:
        strict.build_lists([bad], TODAY)
        check(f"strict stops on {why}", False)
    except ValueError:
        check(f"strict stops on {why}", True)

# Counts behind the chapter's prose.
dec = [m for m in members if m["expires"] and date(2026, 12, 1) <= date(*reversed([int(x) for x in m["expires"].split("/")])) <= date(2026, 12, 31)]
on_first = sum(m["expires"] == "01/12/2026" for m in members)
on_last = sum(m["expires"] == "31/12/2026" for m in members)
check("3 expire on 1 Dec, 2 on 31 Dec", (on_first, on_last) == (3, 2))
opt_values = sorted(m["email_opt_out"] for m in dec if m["email_opt_out"].strip().lower() in {"yes", "y", "true"})
check("December opt-out spellings", opt_values == sorted(["yes", "Yes", "Yes", "Y", "TRUE", "YES"]), str(opt_values))
numbers["dec_opt_values"] = opt_values


def run_tests(test_file, module_src, module_name):
    with tempfile.TemporaryDirectory() as tmp:
        t = Path(tmp)
        (t / f"{module_name}.py").write_text(module_src, encoding="utf-8")
        (t / "tests").mkdir()
        shutil.copy(test_file, t / "tests" / Path(test_file).name)
        r = subprocess.run([sys.executable, "-m", "unittest", "discover", "tests"], cwd=t, capture_output=True, text=True)
        return r.returncode, r.stderr


rc, out = run_tests(PROJECT / "tests/test_reminders.py", s0, "reminders")
check("AI's 3 tests pass on the original", rc == 0 and "Ran 3 tests" in out)
rc, out = run_tests(KEY / "test_reminders_boundaries.py", s0, "reminders")
failed = sorted({ln.split()[1] for ln in out.splitlines() if ln.startswith("FAIL: ")})
check("boundary tests: exactly 3 of 5 fail on the original (today, 30 days, opt-out)",
      rc != 0 and "Ran 5 tests" in out and failed == ["test_reminds_member_expiring_in_30_days", "test_reminds_member_expiring_today", "test_respects_opt_out_whatever_the_capitals"], str(failed))
numbers["boundary_tests_on_original"] = out.strip().splitlines()[-1]
rc, out = run_tests(KEY / "test_reminders_boundaries.py", s3, "reminders")
check("boundary tests pass after the three fixes", rc == 0)
rc, out = run_tests(PROJECT / "tests/test_reminders.py", s3, "reminders")
check("AI's tests still pass after the fixes", rc == 0)

# The single-fix test from Section 8: undo fix 1 and the today test fails.
rc, out = run_tests(KEY / "test_reminders_boundaries.py", rep(s3, "0 <= days <= REMINDER_WINDOW_DAYS", "0 < days < REMINDER_WINDOW_DAYS"), "reminders")
check("undoing fix 1 makes the boundary tests fail again", rc != 0 and "test_reminds_member_expiring_today" in out)

# Exercise: lapsed.py.
lap_src = (PROJECT / "lapsed.py").read_text(encoding="utf-8")
lap = load_source(lap_src, "lapsed_orig")
check("lapsed.py: function given the date, still misses day 14 (10)", len(lap.lapsed_members(members, TODAY)) == 10)
with tempfile.TemporaryDirectory() as tmp:
    r = subprocess.run([sys.executable, str(PROJECT / "lapsed.py"), str(DATA), "--today", "2026-12-01", "--out", tmp],
                       capture_output=True, text=True)
    real = len(lap.lapsed_members(members, date.today()))
    check("lapsed.py run as 1 Dec actually uses the real date", f"Lapsed: {real}" in r.stdout and "on 2026-12-01" in r.stdout,
          f"real date {date.today()} gives {real}")
lapf = load_source((KEY / "lapsed_fixed.py").read_text(encoding="utf-8"), "lapsed_fixed")
check("lapsed_fixed: 11, matches committee", len(lapf.lapsed_members(members, TODAY)) == 11)
with tempfile.TemporaryDirectory() as tmp:
    r = subprocess.run([sys.executable, str(KEY / "lapsed_fixed.py"), str(DATA), "--today", "2026-12-01", "--out", tmp],
                       capture_output=True, text=True)
    check("lapsed_fixed script prints Lapsed: 11", "Lapsed: 11" in r.stdout)
rc, out = run_tests(KEY / "test_lapsed.py", lap_src, "lapsed")
check("exercise tests fail on lapsed.py", rc != 0, out.strip().splitlines()[-1])
rc, out = run_tests(KEY / "test_lapsed.py", (KEY / "lapsed_fixed.py").read_text(encoding="utf-8"), "lapsed")
check("exercise tests pass on lapsed_fixed.py", rc == 0)

# Section 10: the SQL version of the opt-out rule, and NULL.
db = sqlite3.connect(":memory:")
db.execute("CREATE TABLE members (id TEXT, email_opt_out TEXT)")
db.executemany("INSERT INTO members VALUES (?, ?)", [("A", "yes"), ("B", "Yes"), ("C", "no"), ("D", None)])
got = [r[0] for r in db.execute("SELECT id FROM members WHERE email_opt_out <> 'yes' ORDER BY id")]
check("SQL: <> 'yes' emails B (opted out) and drops D (NULL)", got == ["B", "C"], str(got))
got2 = [r[0] for r in db.execute("SELECT id FROM members WHERE COALESCE(LOWER(TRIM(email_opt_out)), '') NOT IN ('yes', 'y', 'true') ORDER BY id")]
check("SQL fixed: C and D", got2 == ["C", "D"], str(got2))
numbers["sql_flawed"], numbers["sql_fixed"] = got, got2

(ROOT / "tools/chapter-numbers.json").write_bytes((json.dumps(numbers, indent=1) + "\n").encode())
print(f"\n{sum(results)} of {len(results)} checks passed")
sys.exit(0 if all(results) else 1)
