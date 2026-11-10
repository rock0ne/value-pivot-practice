"""Audit a HomeWatch version without letting it touch the network.

Replaces urlopen with a recorder and the server class with a stub that records
the address it would listen on, so no socket is opened and nothing is sent.
Usage: python -I tools/audit.py project/homewatch.py
"""
import importlib.util
import json
import sys
import urllib.request
from pathlib import Path

sent = []
listened = []


def fake_urlopen(req, timeout=None):
    url = req.full_url if hasattr(req, "full_url") else req
    data = getattr(req, "data", None)
    sent.append({"url": url, "body": json.loads(data) if data else None})
    raise OSError("blocked by audit")


class FakeServer:
    def __init__(self, address, handler):
        listened.append(address)


urllib.request.urlopen = fake_urlopen
path = Path(sys.argv[1]).resolve()
spec = importlib.util.spec_from_file_location("hw", path)
hw = importlib.util.module_from_spec(spec)
spec.loader.exec_module(hw)
hw.ThreadingHTTPServer = FakeServer
hw.urllib.request.urlopen = fake_urlopen

try:
    hw.make_server()
except OSError:
    pass
print("listens on:", listened)
print("sends to:", [s["url"] for s in sent])
for s in sent:
    print("  body:", s["body"])
try:
    print("default login admin/admin accepted:", hw.check_login("admin", "admin"))
except RuntimeError as e:
    print("default login admin/admin: refused:", e)
