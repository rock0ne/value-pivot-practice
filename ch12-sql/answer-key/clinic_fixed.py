"""Harbour Lane Physiotherapy: booking and reporting functions, corrected (answer key).

Each change is tied to a business rule:
  B1  A therapist can have only one live booking per slot. The DATABASE enforces this,
      with a partial unique index (see migrate.py). The friendly check stays for a nice
      message, but it isn't what keeps the rule.
  B2  A cancelled booking frees the slot, so the index ignores cancelled rows.
  L1  A client is lapsed if they have no booking on or after the date, other than a
      cancelled one. Walk-ins have no client record (NULL) and must not hide anyone.
  M1  "From the 1st to the 31st" means every booking on the 31st, up to midnight.

Same functions and command line as clinic.py.
"""

import sqlite3
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "project" / "clinic.db"
PRICES = {"Assessment": 6500, "Follow-up": 4800, "Sports massage": 5500}


def connect(path=DB):
    conn = sqlite3.connect(path, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def is_slot_free(conn, therapist, start):
    """Friendly early check only. The unique index is what actually keeps rule B1."""
    row = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE therapist = ? AND start = ? AND status != 'cancelled'",
        (therapist, start)).fetchone()
    return row[0] == 0


def book_slot(conn, therapist, start, client_ref, service, created_at=None):
    """Book a slot. Returns the new booking_id, or None if the slot is taken."""
    if not is_slot_free(conn, therapist, start):
        return None
    created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        cur = conn.execute(
            "INSERT INTO bookings (therapist, start, client_ref, service, price_pence, status, created_at)"
            " VALUES (?, ?, ?, ?, ?, 'booked', ?)",
            (therapist, start, client_ref, service, PRICES[service], created_at))
        conn.commit()
        return cur.lastrowid
    except sqlite3.IntegrityError:
        # B1: someone else booked it between our check and our insert.
        conn.rollback()
        return None


def lapsed_clients(conn, since):
    """L1: NOT EXISTS asks about each client directly, so a NULL elsewhere can't hide them."""
    return conn.execute(
        """SELECT c.client_ref, c.name, c.email FROM clients AS c
           WHERE NOT EXISTS (
               SELECT 1 FROM bookings AS b
               WHERE b.client_ref = c.client_ref
                 AND b.start >= ? AND b.status != 'cancelled')
           ORDER BY c.client_ref""",
        (since,)).fetchall()


def revenue_between(conn, first_day, last_day):
    """M1: a half-open range, from first_day 00:00 up to (not including) the day after last_day."""
    day_after = (date.fromisoformat(last_day) + timedelta(days=1)).isoformat()
    total, count = conn.execute(
        """SELECT COALESCE(SUM(CASE status
                                   WHEN 'completed'   THEN price_pence
                                   WHEN 'no_show'     THEN price_pence / 2
                                   WHEN 'late_cancel' THEN price_pence / 2
                                   ELSE 0 END), 0),
                  COUNT(*)
           FROM bookings
           WHERE start >= ? AND start < ?""",
        (first_day, day_after)).fetchone()
    return total, count


def pounds(pence):
    return f"£{pence // 100:,}.{pence % 100:02d}"


def main(argv):
    if not argv:
        print(__doc__)
        return 1
    conn = connect()
    if argv[0] == "revenue":
        total, count = revenue_between(conn, argv[1], argv[2])
        print(f"{count} bookings from {argv[1]} to {argv[2]}: revenue {pounds(total)}")
    elif argv[0] == "lapsed":
        rows = lapsed_clients(conn, argv[1])
        for ref, name, email in rows:
            print(f"{ref}  {name:<22} {email}")
        print(f"{len(rows)} clients not seen since {argv[1]}")
    elif argv[0] == "book":
        new_id = book_slot(conn, argv[1], argv[2], argv[3], argv[4])
        print(f"Booked: booking {new_id}" if new_id else "Sorry, that slot is taken.")
    else:
        print(__doc__)
        return 1
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.exit(main(sys.argv[1:]))
