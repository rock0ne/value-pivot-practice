"""Tests the assistant wrote alongside clinic.py. They all pass."""

import sqlite3
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import clinic  # noqa: E402

SCHEMA = (Path(__file__).resolve().parent.parent / "schema.sql").read_text(encoding="utf-8")


def fresh():
    conn = sqlite3.connect(":memory:")
    conn.executescript(SCHEMA)
    conn.executemany("INSERT INTO clients VALUES (?, ?, ?)", [
        ("C-0001", "Test One", "one@example.org"),
        ("C-0002", "Test Two", "two@example.org"),
    ])
    return conn


class TestClinic(unittest.TestCase):
    def test_book_free_slot(self):
        conn = fresh()
        self.assertIsNotNone(clinic.book_slot(conn, "Amir", "2026-12-15 10:00", "C-0001", "Assessment"))

    def test_taken_slot_is_refused(self):
        conn = fresh()
        clinic.book_slot(conn, "Amir", "2026-12-15 10:00", "C-0001", "Assessment")
        self.assertIsNone(clinic.book_slot(conn, "Amir", "2026-12-15 10:00", "C-0002", "Follow-up"))

    def test_lapsed_clients(self):
        conn = fresh()
        clinic.book_slot(conn, "Amir", "2026-12-15 10:00", "C-0001", "Assessment")
        self.assertEqual([r[0] for r in clinic.lapsed_clients(conn, "2026-12-01")], ["C-0002"])

    def test_revenue(self):
        conn = fresh()
        clinic.book_slot(conn, "Amir", "2026-12-15 10:00", "C-0001", "Assessment")
        conn.execute("UPDATE bookings SET status = 'completed'")
        self.assertEqual(clinic.revenue_between(conn, "2026-12-01", "2026-12-31"), (6500, 1))


if __name__ == "__main__":
    unittest.main()
