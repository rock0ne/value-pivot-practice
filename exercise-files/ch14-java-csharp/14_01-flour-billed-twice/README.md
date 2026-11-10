# 14_01: The flour that was billed twice

**Book:** Chapter 14, Scenario 1 (Java): the flour that was billed twice.

Harbour Fresh Foods merges order lines from its web shop and its phone system, and removes the duplicates. Four bags of flour ordered once, priced `18.50` by the web shop and `18.5` by the phone system, come out as two lines and a bill of £148.00 instead of £74.00. Fix `Line` so that equal amounts are equal, and so that a three-decimal price such as `0.995` is refused rather than rounded. Done means one line for £74.00, the shipped test still giving one line for £14.40, and `0.995` refused.

**Files:** `begin/Billing.java` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch14-java-csharp` folder, run `python check.py`.

**Hint:** compare `new BigDecimal("18.50")` and `new BigDecimal("18.5")` with `equals`, then with `compareTo`. Then look at what `setScale` does with `RoundingMode.UNNECESSARY`.
