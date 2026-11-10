# 20_01: It listened to the whole network

**Book:** Chapter 20, What HomeWatch actually did, 1. It listened to the whole network, not just Nadia's computer.

Nadia's HomeWatch dashboard listens on `0.0.0.0`, which means it accepts connections from any device that can reach it, not only from her own computer. Change it so it listens on this computer only, and keep it on port 8088. You're done when the audit says `listens on: [('127.0.0.1', 8088)]`.

**Files:** `begin/homewatch.py` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck. The answer fixes all three of the chapter's problems at once, so you'll see the other two exercises' answers there as well.

**Check your work:** from the `ch20-home` folder, run `python check.py`. It runs the chapter's audit tool, `data/audit.py`, which replaces the network with recorders, so no port is opened and nothing is sent.

**Hint:** search the file for `0.0.0.0`, as Step 2 of the chapter's method suggests.
