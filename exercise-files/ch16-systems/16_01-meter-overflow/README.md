# 16_01: The overflow check that wasn't there

**Book:** Chapter 16, Scenario 1: the overflow check that wasn't there.

Lumen Grid's gateway adds each meter reading to a running total, and `add_reading` is meant to refuse any reading that would overflow it. Add 1000 to a total of 2147483000, and the program reports a new total of -2147483296 instead, at `-O0` and at `-O2`. Rewrite the check so the compiler must keep it. You're done when both builds print `refused: would overflow`.

**Files:** `begin/meter.c` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch16-systems` folder, run `python check.py`.

**Hint:** the current check does the risky addition first, then looks at the result. Check before you add, or let GCC's `__builtin_add_overflow` do it.
