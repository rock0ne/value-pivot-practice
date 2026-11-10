"""Answer key: tests for the Section 12 exercise (lapsed.py).

Copy into project/tests/ to run them against your own lapsed.py.
"""
import subprocess
import sys
import tempfile
import unittest
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import lapsed  # noqa: E402

TODAY = date(2026, 12, 1)


def member(expires):
    return {"member_id": "T-1", "name": "Test", "type": "adult", "expires": expires}


class LapsedTests(unittest.TestCase):
    def test_includes_member_lapsed_14_days_ago(self):
        self.assertEqual(len(lapsed.lapsed_members([member("17/11/2026")], TODAY)), 1)

    def test_includes_member_lapsed_yesterday(self):
        self.assertEqual(len(lapsed.lapsed_members([member("30/11/2026")], TODAY)), 1)

    def test_skips_member_lapsed_15_days_ago(self):
        self.assertEqual(len(lapsed.lapsed_members([member("16/11/2026")], TODAY)), 0)

    def test_skips_member_expiring_today(self):
        self.assertEqual(len(lapsed.lapsed_members([member("01/12/2026")], TODAY)), 0)

    def test_script_uses_the_date_it_is_given(self):
        # Run the whole script "as" a date years away. A script that quietly
        # uses the real date instead would find nobody.
        with tempfile.TemporaryDirectory() as tmp:
            csv_path = Path(tmp) / "one.csv"
            csv_path.write_text("member_id,name,type,expires\nT-1,Test,adult,10/06/2031\n", encoding="utf-8")
            result = subprocess.run(
                [sys.executable, lapsed.__file__, str(csv_path), "--today", "2031-06-15", "--out", tmp],
                capture_output=True, text=True, check=True)
        self.assertIn("Lapsed: 1", result.stdout)


if __name__ == "__main__":
    unittest.main()
