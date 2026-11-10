# 16_03: meterd: the refused readings and the go line

**Book:** Chapter 16, Scenario 3 (Go): the success reported as a failure, and Scenario 4 (Go): the same code, two meanings.

Lumen Grid's `meterd` service has two faults, and its tests pass with both. `Accept` refuses every reading, good or bad, and `PollJobs` makes every job poll the last meter: `polled: [M-1003 M-1003 M-1003]`. Fix both. You're done when `go run .` accepts M-1001 and M-1002, refuses M-1003's negative reading, and prints `polled: [M-1001 M-1002 M-1003]`.

**Files:** `begin/accept.go` and `begin/go.mod` (edit these). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch16-systems` folder, run `python check.py`.

**Hint:** read `go.mod` before you read the code. In `Accept`, look at what's returned when nothing is wrong. While you're there, add the tests the project is missing: one with a good reading, and one that polls more than one meter.
