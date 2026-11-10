"""Two receptionists book the same slot at the same moment.

This is a teaching tool written by the author. It isn't part of the clinic's system.

In real life, the timing below happens by chance: rarely, under load, and never in a
test that books one slot after another. Here, the tool forces it every time. Each
receptionist's screen checks the slot, then both wait until the other has checked
too, and only then do they press "Book". The code under test runs unchanged.

    python race_demo.py                  # tests clinic.py
    python race_demo.py path/to/other.py # tests another version with the same functions

It works on a temporary copy of clinic.db, so your database isn't changed.
"""

import importlib.util
import shutil
import sqlite3
import sys
import tempfile
import threading
from pathlib import Path

HERE = Path(__file__).resolve().parent
SLOT = ("Bethan", "2027-01-14 15:00")


def load(path):
    spec = importlib.util.spec_from_file_location("code_under_test", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def run(code_path=HERE / "clinic.py", db_path=HERE / "clinic.db"):
    if not Path(db_path).exists():
        raise SystemExit("clinic.db not found. Run: python setup_db.py")
    module = load(code_path)
    tmp = Path(tempfile.mkdtemp())
    copy = tmp / "clinic.db"
    shutil.copyfile(db_path, copy)
    try:
        both_checked = threading.Barrier(2, timeout=5)
        original_check = module.is_slot_free

        def check_then_wait(conn, therapist, start):
            free = original_check(conn, therapist, start)
            try:
                both_checked.wait()
            except threading.BrokenBarrierError:
                pass
            return free

        module.is_slot_free = check_then_wait
        results = {}

        def receptionist(name, client):
            conn = module.connect(copy)
            try:
                results[name] = module.book_slot(conn, SLOT[0], SLOT[1], client, "Follow-up",
                                                 created_at="2027-01-08 10:41:07")
            except Exception as exc:  # report, don't hide
                results[name] = f"error: {exc}"
            finally:
                conn.close()

        threads = [threading.Thread(target=receptionist, args=("Front desk", "C-0011")),
                   threading.Thread(target=receptionist, args=("Website", "C-0012"))]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        conn = sqlite3.connect(copy)
        live = conn.execute(
            "SELECT COUNT(*) FROM bookings WHERE therapist = ? AND start = ? AND status != 'cancelled'",
            SLOT).fetchone()[0]
        conn.close()
        return results, live
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else HERE / "clinic.py"
    results, live = run(target)
    for name, outcome in sorted(results.items()):
        shown = "slot taken" if outcome is None else outcome
        print(f"{name:<11} -> {shown}")
    print(f"Live bookings for {SLOT[0]} at {SLOT[1]}: {live}")
