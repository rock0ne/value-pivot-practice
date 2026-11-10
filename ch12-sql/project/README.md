# Harbour Lane Physiotherapy: the booking database project (Chapter 12)

This is the companion project for Chapter 12 of *Value Pivot*. Everything in it is fiction: the clinic, its therapists, its clients and its money. Email addresses use `example.org`, a domain reserved for examples. The code and its faults were written by the author to show mistakes that AI-written code commonly makes. None of it is output from a real AI assistant.

## What you need
- **Python 3.10 or newer,** as in Chapter 2. SQLite comes with Python, so there's nothing else to install.
- **Optional:** a database browser such as "DB Browser for SQLite" lets you look inside `clinic.db`. You don't need one; everything in the chapter works from the terminal.

## Get started
1. Unzip the project and open a terminal in the `project` folder.
2. Build the database:

```
python setup_db.py
```

You should see `clinic.db built with 1433 bookings.` Run it again whenever you want to start fresh: it replaces `clinic.db` from the CSV files.

3. Run the assistant's tests:

```
python -m unittest discover tests
```

On a Mac or Linux, use `python3` wherever this guide says `python`.

## What's in the folder

| File | What it is |
|---|---|
| `schema.sql` | The database design the assistant wrote |
| `setup_db.py` | Builds `clinic.db` from the CSV files |
| `clinic.py` | Booking, the "we miss you" list and the revenue report |
| `tests/test_clinic.py` | The tests the assistant wrote alongside it |
| `race_demo.py` | A teaching tool: two receptionists press "Book" at the same moment |
| `agent/proposed_tidy.sql` | What the clinic's AI agent proposed to run. **Don't run it on anything you care about.** |
| `data/` | The exported clients and bookings, and December's card-machine takings |
| `exercise/loyalty.py` | The chapter's final exercise. Don't open it until the chapter tells you to. |

## Answers
The `answer-key/` folder in this pack holds the fixed code the chapter walks you through, because the chapter asks you to run it. If you want to try the fixes yourself first, don't open it until Section 7.

The answer to the final exercise is kept apart, in a second download, so you can't see it by accident. Read it only after you've tried the exercise yourself.
