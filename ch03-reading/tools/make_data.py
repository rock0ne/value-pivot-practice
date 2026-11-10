"""Author tool: build the Elmfield Tennis Club data for Chapter 3.

Deterministic (fixed seed), so every reader gets identical files.
Usage: python -I tools/make_data.py   (run from the ch03-reading folder)
"""
import csv
import random
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TODAY = date(2026, 12, 1)
rng = random.Random(3)

FIRST = ["Aisha", "Ben", "Chloe", "Dev", "Ewa", "Femi", "Gareth", "Hana", "Imran", "Jo", "Kwame", "Lena",
         "Marek", "Nia", "Owen", "Priya", "Quinn", "Rosa", "Sam", "Tariq", "Una", "Victor", "Wen", "Yusuf",
         "Zoë", "Alun", "Bea", "Ciaran", "Dina", "Emeka"]
LAST = ["Adeyemi", "Brook", "Chen", "Davies", "Evans", "Fitzgerald", "Gill", "Hughes", "Ibrahim", "Jones",
        "Kowalski", "Lewis", "Mensah", "Nowak", "O'Neill", "Patel", "Quayle", "Rahman", "Singh", "Thomas",
        "Usman", "Vaughan", "Walsh", "Xu", "Young", "Zielinski"]
TYPES = ["adult", "adult", "adult", "family", "senior"]
OTHER_OPT = ["", "", "", "No", "no", "N", "yes", "Yes"]


def person(i):
    f, l = rng.choice(FIRST), rng.choice(LAST)
    email = f"{f}.{l}".lower().replace("'", "").replace("ë", "e") + f"{i}@example.org"
    return f"{f} {l}", email


def d(x):
    return x.strftime("%d/%m/%Y")


rows = []


def add(kind, expires, opt=""):
    i = len(rows) + 1
    name, email = person(i)
    rows.append([f"ETC-{i:04d}", name, email, kind, expires, opt])


# 9 life members: no expiry date.
for _ in range(9):
    add("life", "", "")

# 44 memberships expiring in December 2026 (the reminder window on 1 December).
dec = [TODAY] * 3 + [TODAY + timedelta(days=30)] * 2
dec += [TODAY + timedelta(days=rng.randint(1, 29)) for _ in range(39)]
opt_outs = ["yes", "Yes", "Yes", "Y", "TRUE", "YES"]
middle = [k for k, x in enumerate(dec) if 0 < (x - TODAY).days < 30]
opt_at = set(rng.sample(middle, 6))
oi = iter(opt_outs)
for k, x in enumerate(dec):
    add(rng.choice(TYPES), d(x), next(oi) if k in opt_at else rng.choice(["", "", "No", "no", "N"]))

# 11 lapsed between 17 and 30 November (1 to 14 days ago), including both ends.
lap = [TODAY - timedelta(days=14), TODAY - timedelta(days=1)]
lap += [TODAY - timedelta(days=rng.randint(2, 13)) for _ in range(9)]
for x in lap:
    add(rng.choice(TYPES), d(x), rng.choice(OTHER_OPT))

# 20 lapsed earlier in 2026.
for _ in range(20):
    add(rng.choice(TYPES), d(date(2026, 1, 1) + timedelta(days=rng.randint(0, 314))), rng.choice(OTHER_OPT))

# The rest expire after the window: two on 1 January 2027 (31 days), then 2027.
for _ in range(2):
    add(rng.choice(TYPES), d(TODAY + timedelta(days=31)), rng.choice(OTHER_OPT))
while len(rows) < 412:
    add(rng.choice(TYPES), d(date(2027, 1, 2) + timedelta(days=rng.randint(0, 330))), rng.choice(OTHER_OPT))

rng.shuffle(rows)
out = ROOT / "project/data/members-2026-12-01.csv"
out.parent.mkdir(parents=True, exist_ok=True)
with open(out, "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f, lineterminator="\n")
    w.writerow(["member_id", "name", "email", "type", "expires", "email_opt_out"])
    w.writerows(rows)

(ROOT / "project/data/committee-figures.txt").write_bytes((
    "Elmfield Tennis Club: figures from the membership system, 1 December 2026\n"
    "\n"
    "Memberships expiring in December 2026: 44\n"
    "  of which opted out of email: 6\n"
    "Memberships that lapsed between 17 and 30 November 2026: 11\n"
    "Life members (no expiry date): 9\n"
    "Total members on the system: 412\n").encode())
print("wrote", out, len(rows), "rows")
