"""Answer key: the probe tests from Chapter 3, Section 8.

Copy into project/tests/ to run them against your own reminders.py.
Three fail on the original script; all five pass after the chapter's fixes.
"""
import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import reminders  # noqa: E402

TODAY = date(2026, 12, 1)


def member(expires, opt="", kind="adult"):
    return {"member_id": "T-1", "name": "Test", "email": "t@example.org",
            "type": kind, "expires": expires, "email_opt_out": opt}


class BoundaryTests(unittest.TestCase):
    def test_reminds_member_expiring_today(self):
        self.assertTrue(reminders.due_for_reminder(member("01/12/2026"), TODAY))

    def test_reminds_member_expiring_in_30_days(self):
        self.assertTrue(reminders.due_for_reminder(member("31/12/2026"), TODAY))

    def test_skips_member_expiring_in_31_days(self):
        self.assertFalse(reminders.due_for_reminder(member("01/01/2027"), TODAY))

    def test_never_reminds_life_member(self):
        self.assertFalse(reminders.due_for_reminder(member("", kind="life"), TODAY))

    def test_respects_opt_out_whatever_the_capitals(self):
        for answer in ("yes", "Yes", "YES", "Y", "TRUE"):
            with self.subTest(answer=answer):
                self.assertFalse(reminders.wants_email(member("15/12/2026", answer)))


if __name__ == "__main__":
    unittest.main()
