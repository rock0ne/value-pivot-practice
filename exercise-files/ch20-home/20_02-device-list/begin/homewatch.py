"""HomeWatch: a dashboard for the smart devices in one home (fictional).

Written as a local AI assistant might write it, to show common failure patterns.
It isn't the output of any particular AI. The devices are simulated: nothing here
talks to a real device.
"""
import json
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

CONFIG = {
    "host": "0.0.0.0",
    "port": 8088,
    "admin_user": "admin",
    "admin_password": "admin",
    "analytics_url": "https://telemetry.homewatch-stats.example/v1/report",
}

DEVICES = [
    {"name": "Hall camera", "ip": "192.168.1.40", "status": "online"},
    {"name": "Front door lock", "ip": "192.168.1.41", "status": "locked"},
    {"name": "Kitchen speaker", "ip": "192.168.1.42", "status": "online"},
]


def report_usage(devices):
    """'Anonymous usage statistics' to help improve HomeWatch."""
    body = json.dumps({"devices": devices}).encode()
    req = urllib.request.Request(CONFIG["analytics_url"], data=body,
                                 headers={"Content-Type": "application/json"})
    try:
        urllib.request.urlopen(req, timeout=5)
    except Exception:
        pass


def check_login(user, password):
    return user == CONFIG["admin_user"] and password == CONFIG["admin_password"]


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


if __name__ == "__main__":
    make_server().serve_forever()
