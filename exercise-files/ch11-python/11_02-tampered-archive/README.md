# 11_02: The archive that wrote outside its folder

**Book:** Chapter 11, Scenario 2: the archive that wrote outside its folder.

`unpack.py` unpacks each supplier's price list into that supplier's own folder. On Python 3.12 a tampered archive with a member named `../../escaped.txt` lands outside the folder, while Python 3.14 refuses it, so the same line is safe on one version and unsafe on another. Make the code safe on every version by naming the extraction filter, rather than relying on the default. You're done when every `extractall` names its filter, a normal price list still unpacks, and the tampered archive is refused.

**Files:** `begin/unpack.py` (edit this). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch11-python` folder, run `python check.py`. It builds the chapter's two test archives with `data/make_archives.py`, in a temporary folder that's removed afterwards. On Python 3.14 the tampered-archive check passes even before your change, because the newer default protects you: the filter check is the one that tells you the code is safe on older versions too.

**Hint:** Python's documentation recommends one filter name for versions with a less secure default. Look up the `filter` argument of `extractall`.
