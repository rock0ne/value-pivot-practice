"""Author tool: generate the fictional Harbour Lane Physiotherapy data for Chapter 12.

Deterministic (fixed seed). Writes into ../project/data:
  clients.csv                every client on file
  bookings.csv               September to December 2026, as exported from the new database
  card-payments-2026-12.csv  what the card machine actually took each day in December
and tools/expected.json, the author's own figures, which tools/check_ch12.py recomputes.

Charging policy (unchanged from Chapter 2, with the November rule):
  completed = full price; no_show = half; late_cancel = half; cancelled = nothing.

Planted facts the chapter depends on:
  * About 6% of bookings are walk-ins with no client record (client_ref empty -> NULL).
  * Clients C-0201 to C-0260 last visited in September (some later cancelled), so they're lapsed.
  * Twice in November, Bethan was double-booked: two live bookings for the same slot,
    created in the same second. Kofi was free both times and saw the second client.
  * 31 December has normal bookings.
All people, prices and records are invented. Email addresses use the reserved example.org domain.
"""

import csv
import json
import random
from datetime import date, datetime, timedelta
from pathlib import Path

SEED = 20261231
HERE = Path(__file__).resolve().parent
DATA = HERE.parent / "project" / "data"
THERAPISTS = ["Amir", "Bethan", "Kofi"]
SERVICES = [("Assessment", 6500), ("Follow-up", 4800), ("Sports massage", 5500)]
FEE = {"completed": 1.0, "no_show": 0.5, "late_cancel": 0.5, "cancelled": 0.0}
HOURS = range(9, 18)
CLOSED = {date(2026, 12, 25)}
FIRST = ["Aisha", "Ben", "Chloe", "Dev", "Ella", "Femi", "Grace", "Hamza", "Isla", "Jack",
         "Kemi", "Liam", "Maya", "Noah", "Orla", "Priya", "Quinn", "Rosa", "Sam", "Tara",
         "Usman", "Vera", "Will", "Yara", "Zac"]
LAST = ["Ahmed", "Bell", "Clarke", "Davies", "Evans", "Fraser", "Green", "Hughes", "Iqbal",
        "Jones", "Khan", "Lewis", "Morgan", "Nowak", "Owusu", "Patel", "Reid", "Shaw",
        "Taylor", "Walsh"]


def charge(price, status):
    return round(price * FEE[status])


def days(start, end):
    d = start
    while d <= end:
        if d.weekday() < 5 and d not in CLOSED:
            yield d
        d += timedelta(days=1)


def main():
    rng = random.Random(SEED)
    DATA.mkdir(parents=True, exist_ok=True)

    clients = []
    for i in range(1, 261):
        first, last = rng.choice(FIRST), rng.choice(LAST)
        if i == 42:
            first, last = "Siobhan", "O'Brien"  # the apostrophe the chapter's "correct part" handles
        ref = f"C-{i:04d}"
        email = f"{first}.{last}".lower().replace("'", "") + f".{i}@example.org"
        clients.append({"client_ref": ref, "name": f"{first} {last}", "email": email})
    active = [c["client_ref"] for c in clients[:200]]
    lapsed = [c["client_ref"] for c in clients[200:]]

    rows = []
    sep_slots = []
    for d in days(date(2026, 9, 1), date(2026, 12, 31)):
        for t in THERAPISTS:
            for h in HOURS:
                if rng.random() > 0.62:
                    continue
                start = datetime(d.year, d.month, d.day, h, 0)
                service, price = rng.choice(SERVICES)
                if rng.random() < 0.06:
                    ref = ""
                elif d.month == 9 and rng.random() < 0.3:
                    ref = rng.choice(lapsed)
                else:
                    ref = rng.choice(active)
                status = rng.choices(["completed", "no_show", "cancelled", "late_cancel"],
                                     [0.80, 0.06, 0.10, 0.04])[0]
                if d < date(2026, 11, 1) and status == "late_cancel":
                    status = "cancelled"  # the late-cancel rule started on 1 November
                created = start - timedelta(days=rng.randint(1, 20), minutes=rng.randint(0, 600),
                                            seconds=rng.randint(0, 59))
                rows.append({"therapist": t, "start": start, "client_ref": ref, "service": service,
                             "price_pence": price, "status": status, "created_at": created})
                if d.month == 9:
                    sep_slots.append(start)

    # Every lapsed client must have at least one September visit.
    seen = {r["client_ref"] for r in rows}
    for ref in lapsed:
        if ref not in seen:
            for r in rows:
                if r["start"].month == 9 and r["client_ref"] in active and r["status"] == "completed":
                    r["client_ref"] = ref
                    seen.add(ref)
                    break
    # Five lapsed clients booked again in October and cancelled: still lapsed under the rule.
    october_cancels = [r for r in rows if r["start"].month == 10 and r["status"] == "cancelled"
                       and r["client_ref"] in active]
    for ref, r in zip(lapsed[:5], october_cancels[:5]):
        r["client_ref"] = ref

    # Two November double-bookings for Bethan, at slots where Kofi was free.
    occupied = {(r["therapist"], r["start"]) for r in rows}
    doubles = []
    for r in rows:
        if (len(doubles) < 2 and r["therapist"] == "Bethan" and r["start"].month == 11
                and r["status"] == "completed" and r["client_ref"]
                and ("Kofi", r["start"]) not in occupied
                and r["start"].day > (doubles[0]["start"].day + 7 if doubles else 0)):
            twin_created = r["created_at"]
            twin = {"therapist": "Bethan", "start": r["start"], "client_ref": rng.choice(active),
                    "service": "Follow-up", "price_pence": 4800, "status": "completed",
                    "created_at": twin_created}
            doubles.append(r)
            rows.append(twin)

    rows.sort(key=lambda r: (r["created_at"], r["therapist"], r["start"]))
    for i, r in enumerate(rows, start=1001):
        r["booking_id"] = i

    fields = ["booking_id", "therapist", "start", "client_ref", "service", "price_pence",
              "status", "created_at"]
    with open(DATA / "bookings.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fields, lineterminator="\n")
        w.writeheader()
        for r in sorted(rows, key=lambda r: r["booking_id"]):
            out = dict(r)
            out["start"] = r["start"].strftime("%Y-%m-%d %H:%M")
            out["created_at"] = r["created_at"].strftime("%Y-%m-%d %H:%M:%S")
            w.writerow(out)
    with open(DATA / "clients.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, ["client_ref", "name", "email"], lineterminator="\n")
        w.writeheader()
        w.writerows(clients)

    daily = {}
    for r in rows:
        if r["start"].month == 12:
            daily[r["start"].date()] = daily.get(r["start"].date(), 0) + charge(r["price_pence"], r["status"])
    with open(DATA / "card-payments-2026-12.csv", "w", newline="", encoding="utf-8") as f:
        f.write("date,amount_taken_gbp\n")
        for d in sorted(daily):
            f.write(f"{d.strftime('%d/%m/%Y')},{daily[d] // 100}.{daily[d] % 100:02d}\n")

    expected = {
        "bookings": len(rows),
        "walk_ins": sum(1 for r in rows if not r["client_ref"]),
        "december_card_pence": sum(daily.values()),
        "dec31_pence": daily.get(date(2026, 12, 31), 0),
        "double_booked_slots": [r["start"].strftime("%Y-%m-%d %H:%M") for r in doubles],
    }
    (HERE / "expected.json").write_text(json.dumps(expected, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(expected, indent=2))


if __name__ == "__main__":
    main()
