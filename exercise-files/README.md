# Value Pivot: exercise files

Try each chapter's fixes for yourself. Every exercise has three parts:

- **begin:** the code the AI assistant wrote, with the fault the chapter finds. You work on this.
- **a checker:** it tells you which parts of your fix are right, and which aren't yet.
- **end:** one possible answer. Open it only when you've finished, or you're truly stuck.

Start with `index.html`: open it in your browser.

## In your browser: Chapters 12 and 13

Open `ch12-sql/index.html` (SQL) or `ch13-js-ts/index.html` (JavaScript). The page runs everything: the Chapter 12 booking database runs inside it, using a pinned copy of sql.js in `shared/vendor`. Type, press **Run**, then check your answer. Nothing is sent anywhere.

The SQL exercises are also in `ch12-sql/begin` and `ch12-sql/end` as `.sql` files, if you'd rather use the SQLite shell or a database browser.

## On your computer: Chapters 3, 11, 14, 15, 16 and 20

1. Read the exercise's `README.md`, for example `ch03-reading/03_01-reminders/README.md`.
2. Edit the files in its `begin` folder.
3. From the chapter's folder, run:

   ```bash
   python check.py
   ```

   It prints PASS or FAIL for each check and writes `results.html`, which you can open in your browser.
4. Run it again after each change. To see what passing looks like, run `python check.py --end`, which checks the answers instead.

What each chapter needs installed is in `index.html` and in each chapter's folder.

## Safety

The code has deliberate faults in it. The checkers run it only in safe ways: on made-up data, in temporary folders, with stand-ins for anything that deletes, and with nothing sent over the internet. Run the files the same way, on your own computer, and don't point them at real data or real systems.

## For the author

`tools/verify_all.py` checks that every exercise's begin state fails and its end state passes. `tools/build_ch12.py` rebuilds the SQL page's data and checks its numbers against the book.
