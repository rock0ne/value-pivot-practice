"""Build the Chapter 12 SQL exercise page from the chapter's own data. Standard library only.

Usage: python -I tools/build_ch12.py      (from the exercise-files folder)
Writes ch12-sql/data.js, ch12-sql/exercises.js, ch12-sql/begin/*.sql and ch12-sql/end/*.sql.
It also checks every exercise: the begin query must fail the check, the end query must pass,
and the numbers must match the ones the book quotes.
"""
import csv, json, sqlite3, sys
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
BOOK = HERE.parent
PROJ = BOOK / "ch12-sql/project"
OUT = HERE / "ch12-sql"

EX = [
    dict(id="12_01", title="Find the double bookings",
         book="Section 2, Start with evidence, not code",
         task="Ruth says two clients turned up for the same appointment, twice in November. Write a query that lists every "
              "therapist and start time with more than one <em>live</em> booking (a live booking is any booking that isn't "
              "cancelled). Return three columns: <code>therapist</code>, <code>start</code> and the number of live bookings.",
         hint="Group by therapist and start, count the rows, and keep only the groups with a count above 1. Leave out "
              "cancelled bookings before you group.",
         begin="-- The assistant's booking code checks the slot is free before it books.\n"
               "-- Don't trust that. Ask the data what actually happened.\n"
               "SELECT therapist, start, status\nFROM bookings\nORDER BY therapist, start\nLIMIT 20;\n",
         end="SELECT therapist, start, COUNT(*) AS live_bookings\nFROM bookings\nWHERE status != 'cancelled'\n"
             "GROUP BY therapist, start\nHAVING COUNT(*) > 1\nORDER BY start;\n",
         check="rows", book_check=lambda r: len(r) == 2 and {x[1] for x in r} == {"2026-11-02 11:00", "2026-11-10 10:00"}),
    dict(id="12_02", title="December was £648 short",
         book="Section 6, December was £648 short",
         task="The assistant's report totals revenue with <code>start BETWEEN '2026-12-01' AND '2026-12-31'</code>. "
              "Run it, then fix it so the December total matches the card machine. Completed visits count at full price, "
              "no-shows and late cancellations at half price, and cancellations at nothing. Return one row with one "
              "column: the total in pence.",
         hint="<code>start</code> holds a date and a time, as text. Compared as text, <code>'2026-12-31 09:00'</code> "
              "comes after <code>'2026-12-31'</code>. Ask for everything from the first day up to, but not including, "
              "the first day of the next month.",
         begin="SELECT COALESCE(SUM(CASE status\n           WHEN 'completed'   THEN price_pence\n"
               "           WHEN 'no_show'     THEN price_pence / 2\n           WHEN 'late_cancel' THEN price_pence / 2\n"
               "           ELSE 0 END), 0) AS revenue_pence\nFROM bookings\nWHERE start BETWEEN '2026-12-01' AND '2026-12-31';\n",
         end="SELECT COALESCE(SUM(CASE status\n           WHEN 'completed'   THEN price_pence\n"
             "           WHEN 'no_show'     THEN price_pence / 2\n           WHEN 'late_cancel' THEN price_pence / 2\n"
             "           ELSE 0 END), 0) AS revenue_pence\nFROM bookings\nWHERE start >= '2026-12-01' AND start < '2027-01-01';\n",
         check="rows", book_check=lambda r: r == [(1635000,)], begin_value=[(1570200,)]),
    dict(id="12_03", title="The \"we miss you\" list says nobody",
         book="Section 5, The email list that came back empty",
         task="Ruth wants every client with no live booking on or after 1 October 2026. The assistant's query returns "
              "nobody. Run it, find out why, and fix it. Return <code>client_ref</code>, <code>name</code> and "
              "<code>email</code>.",
         hint="Walk-in bookings have no <code>client_ref</code>: it's NULL. <code>NOT IN</code> a list that contains a "
              "NULL is never true. <code>NOT EXISTS</code> asks about each client directly.",
         begin="SELECT client_ref, name, email\nFROM clients\nWHERE client_ref NOT IN (\n"
               "    SELECT client_ref FROM bookings\n    WHERE start >= '2026-10-01' AND status != 'cancelled')\n"
               "ORDER BY client_ref;\n",
         end="SELECT c.client_ref, c.name, c.email\nFROM clients AS c\nWHERE NOT EXISTS (\n    SELECT 1 FROM bookings AS b\n"
             "    WHERE b.client_ref = c.client_ref\n      AND b.start >= '2026-10-01' AND b.status != 'cancelled')\n"
             "ORDER BY c.client_ref;\n",
         check="rows", book_check=lambda r: len(r) == 63, begin_value=[]),
    dict(id="12_04", title="Your turn: the loyalty card",
         book="Section 10, Your turn: the loyalty card",
         task="Reception stamps a loyalty card for every completed visit. This query lists every client with their "
              "completed visits in December 2026, including clients who didn't come. Something about the counts is "
              "wrong. Find it and fix it. Return <code>client_ref</code>, <code>name</code> and <code>visits</code>.",
         hint="Look at a client who didn't come in December. What does <code>COUNT(*)</code> count after a "
              "<code>LEFT JOIN</code> finds no match?",
         begin="SELECT c.client_ref, c.name, COUNT(*) AS visits\nFROM clients AS c\nLEFT JOIN bookings AS b\n"
               "  ON b.client_ref = c.client_ref\n AND b.status = 'completed'\n"
               " AND b.start >= '2026-12-01' AND b.start < '2027-01-01'\nGROUP BY c.client_ref, c.name\nORDER BY c.client_ref;\n",
         end="SELECT c.client_ref, c.name, COUNT(b.booking_id) AS visits\nFROM clients AS c\nLEFT JOIN bookings AS b\n"
             "  ON b.client_ref = c.client_ref\n AND b.status = 'completed'\n"
             " AND b.start >= '2026-12-01' AND b.start < '2027-01-01'\nGROUP BY c.client_ref, c.name\nORDER BY c.client_ref;\n",
         check="rows", book_check=lambda r: any(x[2] == 0 for x in r)),
    dict(id="12_05", title="Make the database refuse a double booking",
         book="Section 4, Put the rule where it can't be skipped",
         task="A check in the code can't stop two receptionists booking the same slot at the same moment. The database "
              "can. Write the statement that makes the database itself refuse a second live booking for the same "
              "therapist and start time. A cancelled booking must free the slot again. <strong>Check my answer</strong> runs "
              "your statement on an empty <code>bookings</code> table, then tries five bookings. If you press <strong>Run</strong> "
              "instead, it runs on the real data, which already holds the double bookings from Exercise 12_01, so the index "
              "can't be built. That's the chapter's point: clear up the existing clashes first, as Section 4 does.",
         hint="A <code>UNIQUE</code> index on <code>(therapist, start)</code> is close, but it also blocks rebooking a "
              "cancelled slot. Add a <code>WHERE</code> clause to the index so it ignores cancelled rows.",
         begin="-- The assistant's suggestion:\nCREATE UNIQUE INDEX one_booking_per_slot\nON bookings (therapist, start);\n",
         end="CREATE UNIQUE INDEX one_live_booking_per_slot\nON bookings (therapist, start)\nWHERE status != 'cancelled';\n",
         check="guard"),
]

GUARD = [  # (description, insert values, should it be accepted?)
    ("a booking for Bethan at 10:00", ("Bethan", "2027-01-12 10:00", "booked"), True),
    ("a second live booking for Bethan at 10:00", ("Bethan", "2027-01-12 10:00", "booked"), False),
    ("a booking for Bethan at 11:00 that has been cancelled", ("Bethan", "2027-01-12 11:00", "cancelled"), True),
    ("a new live booking for Bethan at 11:00, where the only other booking is cancelled", ("Bethan", "2027-01-12 11:00", "booked"), True),
    ("a booking for Kofi at 10:00, the same time but another therapist", ("Kofi", "2027-01-12 10:00", "booked"), True),
]


def load():
    schema = (PROJ / "schema.sql").read_text(encoding="utf-8")
    clients = list(csv.reader((PROJ / "data/clients.csv").open(encoding="utf-8")))[1:]
    bookings = list(csv.reader((PROJ / "data/bookings.csv").open(encoding="utf-8")))[1:]
    for b in bookings:
        b[0] = int(b[0]); b[5] = int(b[5]); b[3] = b[3] or None
    return schema, clients, bookings


def db(schema, clients, bookings):
    c = sqlite3.connect(":memory:")
    c.executescript(schema)
    c.executemany("INSERT INTO clients VALUES (?,?,?)", clients)
    c.executemany("INSERT INTO bookings VALUES (?,?,?,?,?,?,?,?)", bookings)
    return c


def guard(schema, sql):
    c = sqlite3.connect(":memory:")
    c.executescript(schema)
    c.executescript(sql)
    got = []
    for _, (t, s, st), _want in GUARD:
        try:
            c.execute("INSERT INTO bookings (therapist,start,client_ref,service,price_pence,status,created_at) "
                      "VALUES (?,?,NULL,'Follow-up',4800,?,'2027-01-05 09:00:00')", (t, s, st)); got.append(True)
        except sqlite3.IntegrityError:
            got.append(False)
    return got


def main():
    schema, clients, bookings = load()
    ok = True
    for e in EX:
        if e["check"] == "rows":
            exp = db(schema, clients, bookings).execute(e["end"]).fetchall()
            beg = db(schema, clients, bookings).execute(e["begin"]).fetchall()
            e["expected"] = exp
            fails_begin = sorted(map(repr, beg)) != sorted(map(repr, exp))
            book_ok = e["book_check"](exp)
            if "begin_value" in e:
                book_ok = book_ok and beg == e["begin_value"]
            print(f"{e['id']}: expected {len(exp)} rows; begin fails the check: {fails_begin}; matches the book: {book_ok}")
            ok &= fails_begin and book_ok
        else:
            want = [w for *_, w in GUARD]
            b, en = guard(schema, e["begin"]), guard(schema, e["end"])
            print(f"{e['id']}: begin {b} end {en} want {want}")
            ok &= b != want and en == want
    (OUT / "begin").mkdir(parents=True, exist_ok=True); (OUT / "end").mkdir(exist_ok=True)
    for e in EX:
        slug = e["id"] + "-" + "".join(ch if ch.isalnum() else "-" for ch in e["title"].lower()).strip("-").replace("--", "-")
        (OUT / "begin" / f"{slug}.sql").write_text(f"-- Exercise {e['id']}: {e['title']} (begin)\n" + e["begin"], encoding="utf-8", newline="\n")
        (OUT / "end" / f"{slug}.sql").write_text(f"-- Exercise {e['id']}: {e['title']} (one possible answer)\n" + e["end"], encoding="utf-8", newline="\n")
    data = {"schema": schema, "clients": clients, "bookings": bookings}
    (OUT / "data.js").write_text("// Harbour Lane Physiotherapy (fictional), from Chapter 12's project/data.\n"
                                 "window.CLINIC = " + json.dumps(data, separators=(",", ":")) + ";\n", encoding="utf-8", newline="\n")
    pub = [{k: (v if k != "expected" else [list(r) for r in v]) for k, v in e.items() if k not in ("book_check", "begin_value")} for e in EX]
    guard_pub = [{"what": d, "row": list(v), "accept": w} for d, v, w in GUARD]
    (OUT / "exercises.js").write_text("// Generated by tools/build_ch12.py. The answers are in here, so don't read this file\n"
                                      "// until you've tried. Use the page's 'Show one possible answer' button instead.\n"
                                      "window.EXERCISES = " + json.dumps(pub, ensure_ascii=False, indent=1) + ";\n"
                                      "window.GUARD = " + json.dumps(guard_pub, ensure_ascii=False) + ";\n", encoding="utf-8", newline="\n")
    print("ALL EXERCISES CHECK OUT" if ok else "PROBLEM")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
