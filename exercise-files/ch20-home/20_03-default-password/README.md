# 20_03: It had a default password

**Book:** Chapter 20, What HomeWatch actually did, 3. It had a default password.

HomeWatch's admin login is `admin` with the password `admin`, and anyone who can reach the dashboard can use it. Remove the built-in password: read the owner's password from the `HOMEWATCH_PASSWORD` environment variable, and refuse to run the login until the owner has set one of 12 or more characters. You're done when the audit refuses `admin/admin`, both with no password set and with the password set to `admin`.

**Files:** `begin/homewatch.py` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck. The answer fixes all three of the chapter's problems at once.

**Check your work:** from the `ch20-home` folder, run `python check.py`. The checks run with `HOMEWATCH_PASSWORD` unset, and then set to `admin`, whatever your own computer has.

**Hint:** search for `password` and `admin`. Raising an error with a clear message is a fine way to refuse: the chapter's answer says what the owner has to do.
