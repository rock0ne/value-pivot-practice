"""The awkward-cases tests (answer key).

These are the tests the assistant didn't write: a walk-in, a booking late on the last
day, two people booking at once, a rebooking after a cancellation, and a name with an
apostrophe. Run them against any version of the code:

    python test_clinic_awkward.py                      # the corrected code
    CODE=../project/clinic.py python test_clinic_awkward.py   # the original (3 fail)

On Windows PowerShell:  $env:CODE="../project/clinic.py"; python test_clinic_awkward.py
"""

import importlib.util
import os
import shutil
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

HERE = Path(__file__).resolve().parent
PROJECT = HERE.parent / "project"
CODE = Path(os.environ.get("CODE", HERE / "clinic_fixed.py")).resolve()
FIXED = CODE.name == "clinic_fixed.py"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


code = load("code_under_test", CODE)
migrate = load("migrate", HERE / "migrate.py")
race_demo = load("race_demo", PROJECT / "race_demo.py")
SCHEMA = (PROJECT / "schema.sql").read_text(encoding="utf-8")


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    if FIXED:
        conn.execute(migrate.CREATE_INDEX)
    conn.executemany("INSERT INTO clients VALUES (?, ?, ?)", [
        ("C-0001", "Test One", "one@example.org"),
        ("C-0002", "Test Two", "two@example.org"),
        ("C-0003", "Siobhan O'Brien", "siobhan@example.org"),
    ])
    return conn


class AwkwardCases(unittest.TestCase):
    def test_walk_in_does_not_hide_lapsed_clients(self):
        conn = fresh()
        code.book_slot(conn, "Amir", "2026-12-15 10:00", "C-0001", "Assessment")
        code.book_slot(conn, "Kofi", "2026-12-15 10:00", None, "Follow-up")  # a walk-in
        lapsed = [r[0] for r in code.lapsed_clients(conn, "2026-12-01")]
        self.assertEqual(lapsed, ["C-0002", "C-0003"])

    def test_last_afternoon_of_the_month_counts(self):
        conn = fresh()
        code.book_slot(conn, "Amir", "2026-12-31 16:00", "C-0001", "Assessment")
        conn.execute("UPDATE bookings SET status = 'completed'")
        self.assertEqual(code.revenue_between(conn, "2026-12-01", "2026-12-31"), (6500, 1))

    def test_two_people_booking_at_once(self):
        tmp = Path(tempfile.mkdtemp())
        try:
            db = tmp / "clinic.db"
            load("setup_db", PROJECT / "setup_db.py").build(db, PROJECT / "data")
            if FIXED:
                migrate.migrate(db, apply=True)
            _, live = race_demo.run(CODE, db)
            self.assertEqual(live, 1)
        finally:
            shutil.rmtree(tmp, ignore_errors=True)

    def test_rebook_after_cancellation(self):
        conn = fresh()
        first = code.book_slot(conn, "Bethan", "2027-01-12 10:00", "C-0001", "Follow-up")
        conn.execute("UPDATE bookings SET status = 'cancelled' WHERE booking_id = ?", (first,))
        conn.commit()
        self.assertIsNotNone(code.book_slot(conn, "Bethan", "2027-01-12 10:00", "C-0002", "Follow-up"))

    def test_apostrophe_in_a_name(self):
        conn = fresh()
        self.assertIsNotNone(code.book_slot(conn, "Amir", "2027-01-12 11:00", "C-0003", "Assessment"))
        self.assertIn("C-0003", [r[0] for r in code.lapsed_clients(conn, "2027-02-01")])


if __name__ == "__main__":
    unittest.main()
