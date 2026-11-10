import sys
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import reminders  # noqa: E402

TODAY = date(2026, 12, 1)


def member(expires, opt=""):
    return {"member_id": "T-1", "name": "Test", "email": "t@example.org",
            "type": "adult", "expires": expires, "email_opt_out": opt}


class ReminderTests(unittest.TestCase):
    def test_reminds_member_expiring_mid_window(self):
        self.assertTrue(reminders.due_for_reminder(member("15/12/2026"), TODAY))

    def test_skips_member_expiring_next_year(self):
        self.assertFalse(reminders.due_for_reminder(member("15/03/2027"), TODAY))

    def test_respects_opt_out(self):
        self.assertFalse(reminders.wants_email(member("15/12/2026", "yes")))


if __name__ == "__main__":
    unittest.main()
