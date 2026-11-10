"""Check your Chapter 20 exercises.

    python check.py          checks your work in each exercise's begin folder
    python check.py --end    checks the answers in the end folders

It prints the results and writes results.html next to this file. Python 3.10 or newer; nothing else to install.
Nothing touches the network: each check runs the chapter's audit tool (data/audit.py), which replaces the
network with recorders, so no port is opened and nothing is sent. The devices are simulated.
"""
import os, subprocess, sys
from functools import lru_cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "shared"))
import report  # noqa: E402

AUDIT = HERE / "data" / "audit.py"


@lru_cache(maxsize=None)
def audit(folder, owner_password=None):
    """Run the chapter's audit on folder/homewatch.py and return what it printed."""
    target = folder / "homewatch.py"
    if not target.exists():
        raise FileNotFoundError(f"there's no homewatch.py in {folder.parent.name}/{folder.name}")
    env = {k: v for k, v in os.environ.items() if k != "HOMEWATCH_PASSWORD"}
    if owner_password is not None:
        env["HOMEWATCH_PASSWORD"] = owner_password
    r = subprocess.run([sys.executable, "-I", str(AUDIT), str(target)], cwd=HERE, env=env,
                       capture_output=True, text=True, timeout=30)
    return r.stdout + r.stderr


def line(out, start):
    for ln in out.splitlines():
        if ln.startswith(start):
            return ln.strip()
    return "(the audit printed no '" + start.strip(": ") + "' line: " + " ".join(out.split())[-160:] + ")"


# 20_01: listening

def this_computer_only(folder):
    out = audit(folder)
    return True if "listens on: [('127.0.0.1', 8088)]" in out else "the audit says it " + line(out, "listens on:")


def not_any_address(folder):
    out = audit(folder)
    return True if "0.0.0.0" not in line(out, "listens on:") else "it still " + line(out, "listens on:") + ", every network interface"


# 20_02: sending

def sends_nothing(folder):
    out = audit(folder)
    return True if "sends to: []" in out else "the audit says it " + line(out, "sends to:")


def no_device_details(folder):
    out = audit(folder)
    bodies = " ".join(ln for ln in out.splitlines() if ln.strip().startswith("body:"))
    found = [s for s in ("Hall camera", "Front door lock", "Kitchen speaker", "192.168.1.40", "192.168.1.41", "192.168.1.42") if s in bodies]
    return True if not found else "these went out: " + ", ".join(found)


# 20_03: the default password

def default_login(folder):
    out = audit(folder)
    return True if "default login admin/admin: refused" in out or "default login admin/admin accepted: False" in out \
        else "the audit says: " + line(out, "default login")


def needs_owner_password(folder):
    out = audit(folder)
    return True if "default login admin/admin: refused" in out \
        else "with no HOMEWATCH_PASSWORD set, login still runs: " + line(out, "default login")


def short_password_refused(folder):
    out = audit(folder, "admin")
    return True if "default login admin/admin: refused" in out \
        else "with HOMEWATCH_PASSWORD set to admin (under 12 characters): " + line(out, "default login")


EXERCISES = [
    dict(id="20_01", title="It listened to the whole network", folder="20_01-whole-network",
         book="What HomeWatch actually did: 1. It listened to the whole network, not just Nadia's computer",
         checks=[("doesn't listen on 0.0.0.0, the address for every network", not_any_address),
                 ("listens on 127.0.0.1, this computer only, port 8088", this_computer_only)]),
    dict(id="20_02", title="It sent the list of devices to someone else", folder="20_02-device-list",
         book="What HomeWatch actually did: 2. It sent the list of devices to someone else",
         checks=[("sends nothing out when it starts, unless the owner turns it on", sends_nothing),
                 ("never sends device names or local addresses", no_device_details)]),
    dict(id="20_03", title="It had a default password", folder="20_03-default-password",
         book="What HomeWatch actually did: 3. It had a default password",
         checks=[("doesn't accept the login admin/admin", default_login),
                 ("refuses to run the login until the owner sets HOMEWATCH_PASSWORD", needs_owner_password),
                 ("refuses an owner password shorter than 12 characters, such as admin", short_password_refused)]),
]

if __name__ == "__main__":
    sys.exit(report.run("Chapter 20. Local AI doesn't mean local code", EXERCISES, HERE))
