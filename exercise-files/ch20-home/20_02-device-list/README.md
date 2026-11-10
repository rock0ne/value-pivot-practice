# 20_02: It sent the list of devices to someone else

**Book:** Chapter 20, What HomeWatch actually did, 2. It sent the list of devices to someone else.

When it starts, HomeWatch sends "anonymous usage statistics" to a web address, and those statistics are the name, local address and status of every device in the house. Change it so it sends nothing unless the owner turns it on, and never sends names or addresses even then. You're done when the audit says `sends to: []`.

**Files:** `begin/homewatch.py` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck. The answer fixes all three of the chapter's problems at once.

**Check your work:** from the `ch20-home` folder, run `python check.py`. The address in the code is under `.example`, a domain reserved for examples, and the audit blocks the network anyway, so nothing leaves your computer.

**Hint:** search the file for `https://`, then follow where that address is used.
