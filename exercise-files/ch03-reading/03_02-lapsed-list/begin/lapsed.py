"""Lapsed members for Elmfield Tennis Club.

Lists members whose membership ran out in the last 14 days, so that a
committee member can give them a friendly call.
"""
import argparse
import csv
from datetime import date, datetime
from pathlib import Path

LAPSED_WINDOW_DAYS = 14


def parse_date(text):
    """Parse a date from the export, which uses DD/MM/YYYY."""
    return datetime.strptime(text.strip(), "%d/%m/%Y").date()


def lapsed_members(members, today=date.today()):
    """Members whose membership expired within the last 14 days."""
    found = []
    for m in members:
        if not m["expires"].strip():
            continue  # life members never lapse
        days = (parse_date(m["expires"]) - today).days
        if -LAPSED_WINDOW_DAYS < days < 0:
            found.append(m)
    return found


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("members_csv")
    p.add_argument("--today", help="date to run as, YYYY-MM-DD (default: today)")
    p.add_argument("--out", default="out")
    args = p.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()

    with open(args.members_csv, newline="", encoding="utf-8") as f:
        members = list(csv.DictReader(f))
    found = lapsed_members(members)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    with open(out / "lapsed.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["member_id", "name", "expires"])
        for m in found:
            w.writerow([m["member_id"], m["name"], m["expires"]])

    print(f"Elmfield Tennis Club: lapsed members on {today} (last {LAPSED_WINDOW_DAYS} days)")
    print(f"Members read: {len(members)}   Lapsed: {len(found)}")
    print(f"Written: {(out / 'lapsed.csv').as_posix()}")


if __name__ == "__main__":
    main()
