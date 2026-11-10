"""A small review gate for SQL in a code base (answer key).

It doesn't prove code is right. It stops two patterns from this chapter reaching
production without a person looking, and it checks that the database still has
the rule that prevents double-booking.

    python sql_review.py ../../project/clinic.py --db ../../project/clinic.db

Exit code 1 means "a person must look", so it can run as a CI step.
"""

import re
import sqlite3
import sys
from pathlib import Path

RULES = [
    (re.compile(r"\bNOT\s+IN\s*\(\s*SELECT\b", re.I),
     "NOT IN (SELECT ...): one NULL in the subquery returns no rows. Use NOT EXISTS, or prove the column is NOT NULL."),
    (re.compile(r"\b(start|created_at|\w+_at|\w+_time)\s+BETWEEN\b", re.I),
     "BETWEEN on a date-time column: the last day stops at 00:00. Use >= first AND < day after."),
]


def review_source(path):
    findings = []
    text = Path(path).read_text(encoding="utf-8")
    for pattern, message in RULES:
        # Search the whole file, because SQL is often split across lines.
        for match in pattern.finditer(text):
            line_no = text.count("\n", 0, match.start()) + 1
            findings.append(f"{path}:{line_no}: {message}")
    return sorted(findings)


def review_schema(db_path):
    conn = sqlite3.connect(db_path)
    row = conn.execute(
        "SELECT sql FROM sqlite_master WHERE type = 'index' AND name = 'one_live_booking_per_slot'").fetchone()
    conn.close()
    if not row or "UNIQUE" not in row[0].upper() or "cancelled" not in row[0]:
        return [f"{db_path}: no partial unique index on bookings(therapist, start). Double-booking is possible."]
    return []


def main(argv):
    findings = []
    db = None
    if "--db" in argv:
        i = argv.index("--db")
        db = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    for path in argv:
        findings += review_source(path)
    if db:
        findings += review_schema(db)
    for f in findings:
        print(f)
    print(f"{len(findings)} finding(s)")
    return 1 if findings else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
