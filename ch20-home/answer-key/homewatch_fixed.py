"""HomeWatch, fixed: listens only on this computer, has no default password,
and sends nothing out unless the owner turns it on. Devices are simulated."""
import json
import os
import secrets
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CONFIG = {
    "host": "127.0.0.1",                 # this computer only
    "port": 8088,
    "admin_user": "admin",
    "admin_password": os.environ.get("HOMEWATCH_PASSWORD"),  # must be set by the owner
    "analytics_url": None,               # off unless the owner sets one
}

DEVICES = [
    {"name": "Hall camera", "ip": "192.168.1.40", "status": "online"},
    {"name": "Front door lock", "ip": "192.168.1.41", "status": "locked"},
    {"name": "Kitchen speaker", "ip": "192.168.1.42", "status": "online"},
]


def report_usage(devices):
    if not CONFIG["analytics_url"]:
        return
    body = json.dumps({"device_count": len(devices)}).encode()   # counts only, never names or addresses
    req = urllib.request.Request(CONFIG["analytics_url"], data=body,
                                 headers={"Content-Type": "application/json"})
    urllib.request.urlopen(req, timeout=5)


def check_login(user, password):
    expected = CONFIG["admin_password"]
    if not expected or len(expected) < 12:
        raise RuntimeError("set HOMEWATCH_PASSWORD to a password of 12 or more characters first")
    return secrets.compare_digest(user, CONFIG["admin_user"]) and secrets.compare_digest(password, expected)


class Dashboard(BaseHTTPRequestHandler):
    def do_GET(self):
        body = json.dumps(DEVICES).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(body)


def make_server():
    report_usage(DEVICES)
    return ThreadingHTTPServer((CONFIG["host"], CONFIG["port"]), Dashboard)
