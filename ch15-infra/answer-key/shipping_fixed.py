"""The fix: check the configuration's shape when it's loaded, and fail loudly.
Quoting the codes in the YAML ("NO") also works, but only until someone forgets."""
import re
import sys
import yaml

CODE = re.compile(r"[A-Z]{2}")


def allowed_countries(path):
    with open(path, encoding="utf-8") as f:
        raw = yaml.safe_load(f)["ship_to"]
    bad = [v for v in raw if not (isinstance(v, str) and CODE.fullmatch(v))]
    if bad:
        raise ValueError(f"ship_to must be two-letter country codes; got {bad!r} (quote codes like \"NO\")")
    return raw


if __name__ == "__main__":
    try:
        print("loaded:", allowed_countries(sys.argv[1]))
    except ValueError as e:
        print("refused:", e)
