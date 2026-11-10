# Chapter 3 answer key

Don't open this until you've finished Section 12, or you're truly stuck.

| File | What it is |
|---|---|
| `reminders_fixed.py` | `reminders.py` with the chapter's three fixes (rules M1, M2 and M3). |
| `reminders_strict.py` | The stricter version from the "What a programmer would check here" boxes. A blank expiry date for anyone who isn't a life member stops the run, and so does an opt-out answer it doesn't recognise. |
| `test_reminders_boundaries.py` | The probe tests from Section 8. Three of the five fail on the original script, and all five pass after the fixes. |
| `lapsed_fixed.py` | The exercise answer: `lapsed.py` with both of its faults fixed. |
| `test_lapsed.py` | Tests for the exercise, including one that proves the script uses the date it's given. |

## The exercise, explained

The chapter's script, `reminders.py`, has three faults, and the exercise script, `lapsed.py`, has two. (The reader pack doesn't say how many, because finding out is step 2 of the method.)

1. **It ignores `--today`.** `main()` reads the date you give it, prints it in the heading, and then calls `lapsed_members(members)` without it. The function falls back to its default, `today=date.today()`, and Python works that default out once, when the script starts. So the heading says 1 December 2026, but the list is for whatever day you happen to run it. The fix is to pass `today` in, and to remove the default so it can't happen again. This kind of fault is called an early-evaluated default argument: Python evaluates `today=date.today()` once, when the file is loaded, not each time the function is called. That's the term to search for if you want to read more.
2. **It leaves out the 14th day.** `-14 < days < 0` excludes a membership that lapsed exactly 14 days ago, on 17 November. Rule L1 includes both ends, so the test is `-14 <= days <= -1`.

With both fixes, `python lapsed.py data/members-2026-12-01.csv --today 2026-12-01` reports **11** lapsed members, which matches the committee's figure.

Your note for Grace might read: *"The lapsed list was built for the day the script ran, not for 1 December, and it missed anyone who lapsed exactly two weeks ago. Both are fixed, and it now matches the membership system's 11. I haven't checked who rings them, or what happens to a member who renews after the list is made."*
