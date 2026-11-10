# 15_02: The country that became "false"

**Book:** Chapter 15, Scenario 2 (YAML): the country that became "false".

Pennant added Norway, Sweden and Denmark to its shipping countries, and no orders came from Norway. Load `shipping.yaml` and you'll see why: `NO` loads as `False`. Make two changes, as the chapter does. Change `allowed_countries` in `shipping.py` so it refuses, with a clear message, any entry that isn't a two-letter code, and quote Norway's code in `shipping.yaml`. Done means the file as the AI wrote it is refused, and your corrected file loads as the seven codes that were written.

**Files:** `begin/shipping.py` and `begin/shipping.yaml` (edit these). The answer is in `end/`: open it only when you've finished, or you're truly stuck.

**Check your work:** from the `ch15-infra` folder, run `python check.py`.

**Hint:** print what the loader returns before you trust it. Each entry should be a string of two capital letters.
