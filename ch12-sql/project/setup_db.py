"""Build clinic.db from the CSV files in data/. Run this once before anything else.

    python setup_db.py

It replaces any existing clinic.db, so you can run it again to start fresh.
"""

import csv
import sqlite3
from pathlib import Path

HERE = Path(__file__).resolve().parent


def build(db_path=HERE / "clinic.db", data=HERE / "data"):
    db_path = Path(db_path)
    if db_path.exists():
        db_path.unlink()
    conn = sqlite3.connect(db_path)
    conn.executescript((HERE / "schema.sql").read_text(encoding="utf-8"))
    with open(Path(data) / "clients.csv", newline="", encoding="utf-8") as f:
        conn.executemany("INSERT INTO clients VALUES (:client_ref, :name, :email)", csv.DictReader(f))
    with open(Path(data) / "bookings.csv", newline="", encoding="utf-8") as f:
        rows = []
        for r in csv.DictReader(f):
            r["client_ref"] = r["client_ref"] or None   # a walk-in has no client record
            rows.append(r)
        conn.executemany(
            "INSERT INTO bookings VALUES (:booking_id, :therapist, :start, :client_ref, :service,"
            " :price_pence, :status, :created_at)", rows)
    conn.commit()
    n = conn.execute("SELECT COUNT(*) FROM bookings").fetchone()[0]
    conn.close()
    return n


if __name__ == "__main__":
    print(f"clinic.db built with {build()} bookings.")
