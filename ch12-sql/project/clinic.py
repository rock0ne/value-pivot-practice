"""Harbour Lane Physiotherapy: booking and reporting functions.

The request to the assistant (fictional): "We've moved bookings into a database so the
website and both receptionists can book. Write the functions to book a slot without
double-booking, list clients we haven't seen since a date for our 'we miss you' email,
and total our revenue between two dates."

Written by the author to show mistakes that AI-written code commonly makes. It isn't
output from any real AI assistant.

Usage:
    python clinic.py revenue 2026-12-01 2026-12-31
    python clinic.py lapsed 2026-10-01
    python clinic.py book Bethan "2027-01-12 10:00" C-0042 Follow-up
"""

import sqlite3
import sys
from datetime import datetime
from pathlib import Path

DB = Path(__file__).resolve().parent / "clinic.db"
PRICES = {"Assessment": 6500, "Follow-up": 4800, "Sports massage": 5500}


def connect(path=DB):
    conn = sqlite3.connect(path, timeout=10)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def is_slot_free(conn, therapist, start):
    """True if the therapist has no live (not cancelled) booking at this start time."""
    row = conn.execute(
        "SELECT COUNT(*) FROM bookings WHERE therapist = ? AND start = ? AND status != 'cancelled'",
        (therapist, start)).fetchone()
    return row[0] == 0


def book_slot(conn, therapist, start, client_ref, service, created_at=None):
    """Book a slot if it's free. Returns the new booking_id, or None if the slot is taken."""
    if not is_slot_free(conn, therapist, start):
        return None
    created_at = created_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur = conn.execute(
        "INSERT INTO bookings (therapist, start, client_ref, service, price_pence, status, created_at)"
        " VALUES (?, ?, ?, ?, ?, 'booked', ?)",
        (therapist, start, client_ref, service, PRICES[service], created_at))
    conn.commit()
    return cur.lastrowid


def lapsed_clients(conn, since):
    """Clients with no booking on or after `since` (YYYY-MM-DD). Cancelled bookings don't count."""
    return conn.execute(
        """SELECT client_ref, name, email FROM clients
           WHERE client_ref NOT IN (
               SELECT client_ref FROM bookings WHERE start >= ? AND status != 'cancelled')
           ORDER BY client_ref""",
        (since,)).fetchall()


def revenue_between(conn, first_day, last_day):
    """Revenue in pence for bookings from first_day to last_day inclusive (YYYY-MM-DD).

    Completed = full price; no-show and late cancellation = half price; cancelled = nothing.
    """
    total, count = conn.execute(
        """SELECT COALESCE(SUM(CASE status
                                   WHEN 'completed'   THEN price_pence
                                   WHEN 'no_show'     THEN price_pence / 2
                                   WHEN 'late_cancel' THEN price_pence / 2
                                   ELSE 0 END), 0),
                  COUNT(*)
           FROM bookings
           WHERE start BETWEEN ? AND ?""",
        (first_day, last_day)).fetchone()
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
