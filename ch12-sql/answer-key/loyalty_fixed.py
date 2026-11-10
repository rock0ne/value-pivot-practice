"""Loyalty card report, corrected (answer key).

COUNT(*) counts rows, and a LEFT JOIN gives a client with no visits one row of NULLs,
so every absent client was counted as one visit. COUNT(b.booking_id) counts only real bookings.

Original docstring follows.

Loyalty card report: completed visits per client in a month.

The request to the assistant (fictional): "Our loyalty card gives every fifth visit free.
List every client with how many completed visits they had in a month, including the
ones who didn't come, so reception can stamp the cards."

Written by the author for the chapter's exercise. It isn't output from any real AI assistant.

    python loyalty_fixed.py 2026-12
"""

import sqlite3
import sys
from datetime import date
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "project" / "clinic.db"


def visits_in_month(conn, month):
    year, mon = (int(x) for x in month.split("-"))
    first = date(year, mon, 1).isoformat()
    after = date(year + (mon == 12), mon % 12 + 1, 1).isoformat()
    return conn.execute(
        """SELECT c.client_ref, c.name, COUNT(b.booking_id) AS visits
           FROM clients AS c
           LEFT JOIN bookings AS b
             ON b.client_ref = c.client_ref
            AND b.status = 'completed'
            AND b.start >= ? AND b.start < ?
           GROUP BY c.client_ref, c.name
           ORDER BY c.client_ref""",
        (first, after)).fetchall()


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    rows = visits_in_month(sqlite3.connect(DB), sys.argv[1])
    for ref, name, visits in rows:
        print(f"{ref}  {name:<22} {visits}")
    counts = {}
    for _, _, v in rows:
        counts[v] = counts.get(v, 0) + 1
    print("Clients by number of visits: " + ", ".join(f"{k}: {counts[k]}" for k in sorted(counts)))
