"""Add the one-live-booking-per-slot rule to an existing clinic.db (answer key).

    python migrate.py                # dry run: lists anything that breaks the rule, changes nothing
    python migrate.py --apply        # applies Ruth's decision, then creates the index

Step 1 always runs first: find live bookings that already break the rule. The index
can't be created while they exist, and deleting them would destroy real, paid visits.
A person decides what each one was. Ruth's decision, from her diary: Kofi was free and
saw the second client both times, so the later booking in each pair moves to Kofi.
"""

import sqlite3
import sys
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "project" / "clinic.db"

FIND_CLASHES = """
    SELECT therapist, start, GROUP_CONCAT(booking_id, ', ') AS ids, COUNT(*) AS n
    FROM bookings
    WHERE status != 'cancelled'
    GROUP BY therapist, start
    HAVING COUNT(*) > 1
    ORDER BY start
"""

CREATE_INDEX = """
    CREATE UNIQUE INDEX one_live_booking_per_slot
    ON bookings (therapist, start)
    WHERE status != 'cancelled'
"""


def clashes(conn):
    return conn.execute(FIND_CLASHES).fetchall()


def apply_ruths_decision(conn):
    """Move the later booking of each clash to Kofi, only if Kofi was free then."""
    moved = []
    for therapist, start, ids, _ in clashes(conn):
        later = max(int(i) for i in ids.split(", "))
        kofi_busy = conn.execute(
            "SELECT COUNT(*) FROM bookings WHERE therapist = 'Kofi' AND start = ? AND status != 'cancelled'",
            (start,)).fetchone()[0]
        if kofi_busy:
            raise SystemExit(f"Stop: Kofi was busy at {start}. Ask Ruth again about booking {later}.")
        conn.execute("UPDATE bookings SET therapist = 'Kofi' WHERE booking_id = ?", (later,))
        moved.append((later, start))
    return moved


def migrate(db_path=DB, apply=False):
    conn = sqlite3.connect(db_path)
    found = clashes(conn)
    report = {"clashes": found, "moved": [], "index_created": False}
    if apply and found:
        with conn:
            report["moved"] = apply_ruths_decision(conn)
    if not clashes(conn) and apply:
        with conn:
            conn.execute(CREATE_INDEX)
        report["index_created"] = True
    conn.close()
    return report


if __name__ == "__main__":
    r = migrate(apply="--apply" in sys.argv)
    for therapist, start, ids, n in r["clashes"]:
        print(f"Clash: {therapist} at {start} has {n} live bookings ({ids})")
    for booking_id, start in r["moved"]:
        print(f"Moved booking {booking_id} at {start} to Kofi (Ruth's decision)")
    print("Index created." if r["index_created"] else "No change made (dry run, or clashes remain).")
