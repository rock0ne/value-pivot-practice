# 11_03: The package that doesn't exist

**Book:** Chapter 11, Scenario 3: the package that doesn't exist.

The AI suggested two packages in `requirements-ai.txt`, and one of them, `hollin-feedkit`, didn't exist on the Python Package Index when the chapter was written. Write the control the chapter describes: a small script, `check_requirements.py`, that compares a requirements file with the team's list of checked packages and fails if anything else appears. It should work offline. You're done when it flags `hollin-feedkit`, leaves `requests` alone, and passes a list that holds only approved packages.

**Files:** create `begin/check_requirements.py`. It's run as `python check_requirements.py requirements-ai.txt approved-packages.txt` and should exit with 1 when it finds an unapproved package, and 0 otherwise. The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch11-python` folder, run `python check.py`.

**Hint:** compare names only, so strip version numbers such as `==1.4.0` and comment lines before you compare. Don't look the name up online: a name someone registers next week would pass that check.
