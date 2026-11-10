# Chapter 3 project: Elmfield Tennis Club

The companion files for *Value Pivot*, Chapter 3, "Reading code you didn't write". The club, its members and their email addresses are fictional, and every address uses `example.org`, a domain reserved for examples.

## What you need

Python 3.10 or newer, and nothing else: the project uses only what comes with Python. To check whether you have it, open a terminal and type `python --version` (on a Mac or Linux, `python3 --version`). If you don't have it, install it from python.org, the official site.

## What's here

| File | What it is |
|---|---|
| `reminders.py` | The AI-written renewal-reminder script the chapter reviews. Finding out what's wrong with it is part of the method. |
| `lapsed.py` | The second script, for the exercise in Section 12. |
| `tests/test_reminders.py` | The three tests that came with `reminders.py`. |
| `data/members-2026-12-01.csv` | The membership export: 412 members. |
| `data/committee-figures.txt` | The membership system's own counts, which you compare with. |
| `probes/probes.csv` | The book's eight probe members. Try writing your own first. |

## Running it

From this folder:

```
python reminders.py data/members-2026-12-01.csv --today 2026-12-01
python -m unittest discover tests
```

The scripts never send email. They write lists into an `out` folder (or the folder you give with `--out`) for a person to check.

The answer key is in a separate folder. Don't open it until you've finished the chapter's exercise.
