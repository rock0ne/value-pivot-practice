# 14_02: The query that ran four times

**Book:** Chapter 14, Scenario 2 (C#): the query that ran four times.

Harbour Fresh's overdue-invoice job gives the right answers: 5,427 overdue invoices and 5,427 reminders. But its stand-in database reports 4 reads and 150,007 rows read, for 50,000 invoices. Change the code so the query runs once, and keep every answer the same. Done means 1 database read of 50,000 rows, with the same counts and the same total owed.

**Files:** `begin/overdue.cs` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch14-java-csharp` folder, run `python check.py`.

**Hint:** `overdue` isn't a list of invoices, but a recipe for finding them. Count how many times the code asks for its results.
