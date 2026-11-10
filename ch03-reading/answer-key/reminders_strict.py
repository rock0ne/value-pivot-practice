"""Membership renewal reminders for Elmfield Tennis Club (answer key: the stricter version).

Reads the membership export and writes two files for the secretary to check
before anything is sent: members to remind by email, and members to phone
because they have opted out of email.
"""
import argparse
import csv
from datetime import date, datetime
from pathlib import Path

REMINDER_WINDOW_DAYS = 30


def parse_date(text):
    """Parse a date from the export, which uses DD/MM/YYYY."""
    return datetime.strptime(text.strip(), "%d/%m/%Y").date()


def load_members(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def days_until_expiry(member, today):
    """Days from today until the membership expires, or None for a life member."""
    text = member["expires"].strip()
    if not text:
        if member["type"].strip().lower() == "life":
            return None  # rule M2: life members never expire
        raise ValueError(f"{member['member_id']}: no expiry date, but not a life member")
    return (parse_date(text) - today).days


def due_for_reminder(member, today):
    """True if the membership expires within the next 30 days."""
    days = days_until_expiry(member, today)
    return days is not None and 0 <= days <= REMINDER_WINDOW_DAYS  # rule M1: both ends included


OPT_OUT_ANSWERS = {"yes", "y", "true"}
OPT_IN_ANSWERS = {"", "no", "n", "false"}


def wants_email(member):
    """True unless the member has opted out of email (rule M3).

    Any answer we don't recognise stops the run, so a new spelling on the
    sign-up form can never quietly send email to someone who said no.
    """
    answer = member["email_opt_out"].strip().lower()
    if answer in OPT_OUT_ANSWERS:
        return False
    if answer in OPT_IN_ANSWERS:
        return True
    raise ValueError(f"{member['member_id']}: unrecognised email_opt_out value {member['email_opt_out']!r}")


def build_lists(members, today):
    email, phone = [], []
    for m in members:
        if due_for_reminder(m, today):
            (email if wants_email(m) else phone).append(m)
    return email, phone


def write_list(path, members):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["member_id", "name", "email", "expires"])
        for m in members:
            w.writerow([m["member_id"], m["name"], m["email"], m["expires"]])


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("members_csv")
    p.add_argument("--today", help="date to run as, YYYY-MM-DD (default: today)")
    p.add_argument("--out", default="out")
    args = p.parse_args()
    today = date.fromisoformat(args.today) if args.today else date.today()

    members = load_members(args.members_csv)
    email, phone = build_lists(members, today)
    out = Path(args.out)
    write_list(out / "reminders-email.csv", email)
    write_list(out / "reminders-phone.csv", phone)

    print(f"Elmfield Tennis Club: renewal reminders on {today} (window {REMINDER_WINDOW_DAYS} days)")
    print(f"Members read: {len(members)}")
    print(f"Email reminders: {len(email)}   Phone list: {len(phone)}")
    print(f"Written: {(out / 'reminders-email.csv').as_posix()}, {(out / 'reminders-phone.csv').as_posix()}")


if __name__ == "__main__":
    main()
