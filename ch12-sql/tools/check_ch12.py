"""Author tool: prove every number Chapter 12 quotes. Run from anywhere:

    python -I tools/check_ch12.py

Works on temporary copies, recomputes the money and the lapsed list in plain Python
straight from the CSV files (independent of any SQL), and writes tools/chapter-numbers.json.
"""

import csv
import importlib.util
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
PROJECT = ROOT / "project"
KEY = ROOT / "answer-key"
DATA = PROJECT / "data"
FEE = {"completed": 1.0, "no_show": 0.5, "late_cancel": 0.5, "cancelled": 0.0}

results = []
numbers = {}


def check(name, ok, detail=""):
    results.append((name, bool(ok)))
    print(f"{'PASS' if ok else 'FAIL'}  {name}  {detail}")


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def gbp(p):
    return f"{p // 100:,}.{p % 100:02d}"


def run_py(args, env=None, cwd=None):
    e = dict(os.environ)
    e.update(env or {})
    return subprocess.run([sys.executable, "-I", *args], capture_output=True, text=True,
                          cwd=cwd, env=e, encoding="utf-8")


def main():
    setup = load("setup_db", PROJECT / "setup_db.py")
    ai = load("clinic", PROJECT / "clinic.py")
    fixed = load("clinic_fixed", KEY / "clinic_fixed.py")
    migrate = load("migrate", KEY / "migrate.py")
    race = load("race_demo", PROJECT / "race_demo.py")
    guard = load("agent_guard", KEY / "governance" / "agent_guard.py")
    review = load("sql_review", KEY / "governance" / "sql_review.py")
    expected = json.loads((HERE / "expected.json").read_text(encoding="utf-8"))

    bookings = list(csv.DictReader(open(DATA / "bookings.csv", newline="", encoding="utf-8")))
    clients = list(csv.DictReader(open(DATA / "clients.csv", newline="", encoding="utf-8")))
    card = {}
    for r in csv.DictReader(open(DATA / "card-payments-2026-12.csv", newline="", encoding="utf-8")):
        pounds, pence = r["amount_taken_gbp"].split(".")
        card[r["date"]] = int(pounds) * 100 + int(pence)

    tmp = Path(tempfile.mkdtemp())
    try:
        db = tmp / "clinic.db"

        # 1. The assistant's tests pass.
        p = run_py(["-m", "unittest", "discover", "tests"], cwd=PROJECT)
        check("AI's 4 tests pass", p.returncode == 0 and "Ran 4 tests" in p.stderr)

        # 2. The database builds.
        n = setup.build(db, DATA)
        walk_ins = sum(1 for b in bookings if not b["client_ref"])
        numbers.update(bookings=n, walk_ins=walk_ins, clients=len(clients))
        check("database builds", n == expected["bookings"] == len(bookings), f"{n} bookings, {walk_ins} walk-ins")

        # 3. Card machine equals an independent recomputation.
        card_total = sum(card.values())
        dec = [b for b in bookings if b["start"].startswith("2026-12-")]
        recomputed = sum(round(int(b["price_pence"]) * FEE[b["status"]]) for b in dec)
        dec31 = [b for b in dec if b["start"].startswith("2026-12-31")]
        dec31_pence = sum(round(int(b["price_pence"]) * FEE[b["status"]]) for b in dec31)
        numbers.update(card_total=gbp(card_total), december_bookings=len(dec),
                       dec31_bookings=len(dec31), dec31_value=gbp(dec31_pence),
                       card_days=len(card))
        check("card machine = recomputed December charges", card_total == recomputed == expected["december_card_pence"],
              f"£{gbp(card_total)}")

        # 4. The AI's December revenue misses 31 December exactly.
        conn = ai.connect(db)
        ai_total, ai_count = ai.revenue_between(conn, "2026-12-01", "2026-12-31")
        numbers.update(ai_revenue=gbp(ai_total), ai_count=ai_count, revenue_gap=gbp(card_total - ai_total))
        check("AI revenue short by exactly 31 Dec", card_total - ai_total == dec31_pence and ai_count == len(dec) - len(dec31),
              f"£{gbp(ai_total)} from {ai_count}, gap £{gbp(card_total - ai_total)}")
        bt = conn.execute("SELECT '2026-12-31 09:00' BETWEEN '2026-12-01' AND '2026-12-31'").fetchone()[0]
        check("'2026-12-31 09:00' is not BETWEEN ... '2026-12-31'", bt == 0)

        # 5. Lapsed clients: AI says none; plain Python finds the real list.
        ai_lapsed = ai.lapsed_clients(conn, "2026-10-01")
        seen_since = {b["client_ref"] for b in bookings
                      if b["start"] >= "2026-10-01" and b["status"] != "cancelled" and b["client_ref"]}
        truth = sorted(c["client_ref"] for c in clients if c["client_ref"] not in seen_since)
        nulls = conn.execute("SELECT COUNT(*) FROM bookings WHERE start >= '2026-10-01' AND status != 'cancelled'"
                             " AND client_ref IS NULL").fetchone()[0]
        cancelled_only = sum(1 for ref in truth if any(b["client_ref"] == ref and b["start"] >= "2026-10-01"
                                                        for b in bookings))
        numbers.update(ai_lapsed=len(ai_lapsed), lapsed=len(truth), walk_ins_since_oct=nulls,
                       lapsed_with_only_cancelled_since=cancelled_only)
        check("AI lapsed list is empty because of NULL walk-ins", len(ai_lapsed) == 0 and nulls > 0,
              f"{nulls} walk-ins since 1 Oct")
        fixed_lapsed = [r[0] for r in fixed.lapsed_clients(conn, "2026-10-01")]
        check("NOT EXISTS finds the true lapsed list", fixed_lapsed == truth, f"{len(truth)} clients")
        obrien = conn.execute("SELECT name FROM clients WHERE client_ref = 'C-0042'").fetchone()[0]
        check("apostrophe name stored intact (parameters)", obrien == "Siobhan O'Brien")
        conn.close()

        # 6. The double-booking race.
        _, live_ai = race.run(PROJECT / "clinic.py", db)
        check("race: AI code makes 2 live bookings", live_ai == 2)
        raw = sqlite3.connect(db)
        clashes = migrate.clashes(raw)
        same_second = []
        for _, start, ids, _ in clashes:
            created = {r[0] for r in raw.execute(
                f"SELECT created_at FROM bookings WHERE booking_id IN ({ids})")}
            same_second.append(len(created) == 1)
        numbers.update(clashes=[(c[1], c[2]) for c in clashes])
        check("2 historic clashes, each pair created in the same second",
              len(clashes) == 2 and all(same_second) and [c[1] for c in clashes] == expected["double_booked_slots"])
        try:
            raw.execute(migrate.CREATE_INDEX)
            made = True
        except sqlite3.IntegrityError:
            made = False
        check("unique index can't be created over existing clashes", not made)
        raw.close()

        # 7. The agent's tidy-up: unguarded it destroys paid visits; guarded it's refused.
        tidy = (PROJECT / "agent" / "proposed_tidy.sql").read_text(encoding="utf-8")
        loose = tmp / "loose.db"
        shutil.copyfile(db, loose)
        c = sqlite3.connect(loose)
        before = c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        doomed = c.execute("""SELECT COUNT(*), SUM(price_pence) FROM bookings WHERE status = 'completed'
                              AND (therapist, start) IN (SELECT therapist, start FROM bookings
                              WHERE status != 'cancelled' GROUP BY therapist, start HAVING COUNT(*) > 1)""").fetchone()
        c.executescript(tidy)
        after = c.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        c.close()
        numbers.update(agent_deleted=before - after, agent_deleted_paid_value=gbp(doomed[1]))
        check("agent tidy deletes all 4 rows of both clashes, all paid", before - after == 4 == doomed[0],
              f"£{gbp(doomed[1])} of completed visits")
        outcome = guard.try_sql(tidy, db)
        still = sqlite3.connect(db).execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
        check("guarded agent connection refuses it", outcome.startswith("refused") and still == before, outcome)

        # 8. Migration with Ruth's decision, then the race again.
        rep = migrate.migrate(db, apply=True)
        check("migration moves 2 bookings to Kofi and creates the index", len(rep["moved"]) == 2 and rep["index_created"])
        results_fixed, live_fixed = race.run(KEY / "clinic_fixed.py", db)
        check("race: fixed code makes 1 live booking, other told 'taken'",
              live_fixed == 1 and sorted(map(str, results_fixed.values())).count("None") == 1)
        conn = fixed.connect(db)
        f_total, f_count = fixed.revenue_between(conn, "2026-12-01", "2026-12-31")
        numbers.update(fixed_revenue=gbp(f_total), fixed_count=f_count)
        check("fixed revenue = card machine", f_total == card_total and f_count == len(dec), f"£{gbp(f_total)} from {f_count}")
        conn.close()

        # 9. The tempting fix (full unique index) blocks rebooking after a cancellation.
        naive = sqlite3.connect(":memory:")
        naive.executescript((PROJECT / "schema.sql").read_text(encoding="utf-8"))
        naive.execute("CREATE UNIQUE INDEX naive ON bookings (therapist, start)")
        naive.execute("INSERT INTO clients VALUES ('C-1', 'A', 'a@example.org'), ('C-2', 'B', 'b@example.org')")
        first = fixed.book_slot(naive, "Bethan", "2027-01-12 10:00", "C-1", "Follow-up")
        naive.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?", (first,))
        naive.commit()
        second = fixed.book_slot(naive, "Bethan", "2027-01-12 10:00", "C-2", "Follow-up")
        check("full UNIQUE index refuses a rebooking after cancellation", first and second is None)

        # 10. Awkward tests and the review gate.
        p_fixed = run_py([str(KEY / "test_clinic_awkward.py")], cwd=KEY)
        p_ai = run_py([str(KEY / "test_clinic_awkward.py")], env={"CODE": str(PROJECT / "clinic.py")}, cwd=KEY)
        fails = sorted(l.split()[1] for l in p_ai.stderr.splitlines() if l.startswith("FAIL:"))
        check("awkward tests: fixed 5/5, AI fails exactly 3",
              p_fixed.returncode == 0 and "Ran 5 tests" in p_fixed.stderr and fails == [
                  "test_last_afternoon_of_the_month_counts", "test_two_people_booking_at_once",
                  "test_walk_in_does_not_hide_lapsed_clients"], ", ".join(fails))
        ai_findings = review.review_source(PROJECT / "clinic.py")
        fixed_findings = review.review_source(KEY / "clinic_fixed.py") + review.review_schema(db)
        check("review gate: 2 findings on AI code, 0 on fixed code + migrated db",
              len(ai_findings) == 2 and not fixed_findings)
        # 11. The exercise: LEFT JOIN with COUNT(*) gives absent clients one visit.
        loy = load("loyalty", PROJECT / "exercise" / "loyalty.py")
        loy_fixed = load("loyalty_fixed", KEY / "loyalty_fixed.py")
        conn = sqlite3.connect(db)
        ai_rows = loy.visits_in_month(conn, "2026-12")
        fx_rows = loy_fixed.visits_in_month(conn, "2026-12")
        conn.close()
        truth_v = {c["client_ref"]: 0 for c in clients}
        for b in dec:
            if b["status"] == "completed" and b["client_ref"]:
                truth_v[b["client_ref"]] += 1
        zero = sum(1 for v in truth_v.values() if v == 0)
        one = sum(1 for v in truth_v.values() if v == 1)
        ai_one = sum(1 for r in ai_rows if r[2] == 1)
        ai_zero = sum(1 for r in ai_rows if r[2] == 0)
        numbers.update(loyalty_ai_one=ai_one, loyalty_ai_zero=ai_zero, loyalty_true_zero=zero, loyalty_true_one=one)
        check("exercise: AI shows no zeros; absent clients counted as one visit",
              ai_zero == 0 and ai_one == zero + one, f"AI 1-visit {ai_one}; truth 0:{zero} 1:{one}")
        check("exercise: fixed counts match plain Python", {r[0]: r[2] for r in fx_rows} == truth_v)
        check("exercise: the review gate does NOT catch it", review.review_source(PROJECT / "exercise" / "loyalty.py") == [])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    (HERE / "chapter-numbers.json").write_text(json.dumps(numbers, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(numbers, indent=2))
    failed = [n for n, ok in results if not ok]
    print(f"{len(results) - len(failed)}/{len(results)} checks passed")
    print("ALL CHECKS PASSED" if not failed else "FAILED: " + "; ".join(failed))
    return 1 if failed else 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main())
