"""Decide whether an order can ship (Pennant Print Works, fictional).
Written as an AI assistant might write it, to show a common failure pattern."""
import sys
import yaml


def allowed_countries(path):
    with open(path, encoding="utf-8") as f:
        return yaml.safe_load(f)["ship_to"]


def can_ship(country_code, allowed):
    return country_code in allowed


if __name__ == "__main__":
    allowed = allowed_countries(sys.argv[1])
    print("loaded:", allowed)
    for c in ["GB", "SE", "NO"]:
        print(c, "can ship:", can_ship(c, allowed))
